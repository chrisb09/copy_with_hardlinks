import os
import shutil
import argparse
import pwd
import grp
import sys
import subprocess

def clone_structure(source_path, dest_dir, preserve_ownership, user_group):
    errors = []
    source_path = os.path.abspath(source_path)
    
    try:
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
            if preserve_ownership:
                st = os.stat(source_path)
                os.chown(dest_dir, st.st_uid, st.st_gid)
            elif user_group:
                uid, gid = get_uid_gid(user_group)
                os.chown(dest_dir, uid, gid)
    except PermissionError as e:
        print(f"Permission denied creating directory {dest_dir}: {e}")
        return [f"Dir Permission Denied: {dest_dir}"]
    except Exception as e:
        print(f"Error creating directory {dest_dir}: {e}")
        return [f"Dir Error: {dest_dir} ({e})"]

    if os.path.isdir(source_path) and not os.path.islink(source_path):
        try:
            source_items = os.listdir(source_path)
            source_dir = source_path
        except PermissionError:
            print(f"Permission denied listing {source_path}")
            return [f"List Permission Denied: {source_path}"]
    else:
        # Single file or symlink to dir/file
        source_items = [os.path.basename(source_path)]
        source_dir = os.path.dirname(source_path)

    for item in source_items:
        source_item = os.path.join(source_dir, item)
        dest_item = os.path.join(dest_dir, item)

        try:
            if os.path.islink(source_item):
                link_target = os.readlink(source_item)
                if os.path.exists(dest_item):
                    os.unlink(dest_item)
                os.symlink(link_target, dest_item)
            elif os.path.isdir(source_item):
                errors.extend(clone_structure(source_item, dest_item, preserve_ownership, user_group))
            else:
                if os.path.exists(dest_item):
                    os.unlink(dest_item)
                os.link(source_item, dest_item)
                if preserve_ownership:
                    shutil.copystat(source_item, dest_item)
                elif user_group:
                    uid, gid = get_uid_gid(user_group)
                    os.chown(dest_item, uid, gid)
        except FileNotFoundError:
            print(f"Warning: File not found (skipped): {source_item}")
            errors.append(f"Not Found: {source_item}")
        except PermissionError as e:
            print(f"Warning: Permission denied (skipped): {source_item}")
            errors.append(f"Permission Denied: {source_item}")
        except Exception as e:
            print(f"Warning: Failed to process {source_item}: {e}")
            errors.append(f"Error: {source_item} ({e})")
            
    return errors

def get_uid_gid(user_group):
    if ':' in user_group:
        user, group = user_group.split(':')
        uid = int(user) if user.isdigit() else pwd.getpwnam(user).pw_uid
        gid = int(group) if group.isdigit() else grp.getgrnam(group).gr_gid  
    else:
        uid = gid = int(user_group) if user_group.isdigit() else pwd.getpwnam(user_group).pw_uid
    return uid, gid

def install():
    if not sys.stdin.isatty():
        print("Installation must be run from an interactive terminal.")
        sys.exit(1)

    print("--- Installation Configuration ---")
    default_p = input("Use --preserve-ownership by default? (y/N): ").lower() == 'y'
    default_u = ""
    if input("Use --user-group by default? (y/N): ").lower() == 'y':
        default_u = input("Enter user:group to use by default: ")

    script_path = os.path.abspath(__file__)
    python_exe = sys.executable

    flags = []
    if default_p:
        flags.append("-p")
    if default_u:
        flags.append(f"-u {default_u}")
    
    flag_str = " ".join(flags)
    wrapper_content = f"""#!/bin/sh
{python_exe} {script_path} {flag_str} "$@"
"""

    install_dir = "/usr/local/bin"
    if not os.access(install_dir, os.W_OK):
        print(f"No write access to {install_dir}. Will try to use sudo.")
        use_sudo = True
    else:
        use_sudo = False

    dest_path = os.path.join(install_dir, "copy-with-hardlinks")
    
    try:
        if use_sudo:
            # Use a temporary file and then move it with sudo
            tmp_wrapper = "/tmp/copy-with-hardlinks-wrapper"
            with open(tmp_wrapper, "w") as f:
                f.write(wrapper_content)
            
            subprocess.run(["sudo", "mv", tmp_wrapper, dest_path], check=True)
            subprocess.run(["sudo", "chmod", "+x", dest_path], check=True)
        else:
            with open(dest_path, "w") as f:
                f.write(wrapper_content)
            os.chmod(dest_path, 0o755)
        
        print(f"Successfully installed to {dest_path}")
    except Exception as e:
        print(f"Error during installation: {e}")
        sys.exit(1)

def main():
    if len(sys.argv) > 1 and sys.argv[1] == 'install':
        install()
        return

    parser = argparse.ArgumentParser(description='Clone directory structure with hardlinked files.')
    parser.add_argument('source', help='Path to the source folder')
    parser.add_argument('destination', help='Path to the destination folder')
    parser.add_argument('-p', '--preserve-ownership', action='store_true', help='Preserve ownership of files')
    parser.add_argument('-u', '--user-group', help='Set user and group of files (format: user:group)')
    
    args = parser.parse_args()

    errors = clone_structure(args.source, args.destination, args.preserve_ownership, args.user_group)
    if errors:
        print(f"\nCompleted with {len(errors)} issues.")
    else:
        print("\nCompleted successfully.")

if __name__ == '__main__':
    main()
