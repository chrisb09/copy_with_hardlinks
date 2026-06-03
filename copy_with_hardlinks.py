import os
import shutil
import argparse
import pwd
import grp

def clone_structure(source_path, dest_dir, preserve_ownership, user_group):
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
        if preserve_ownership:
            st = os.stat(source_path)
            os.chown(dest_dir, st.st_uid, st.st_gid)
        elif user_group:
            uid, gid = get_uid_gid(user_group)
            os.chown(dest_dir, uid, gid)

    source_items = []
    source_dir = source_path
    if os.path.isdir(source_path):
        source_items = os.listdir(source_path)
    else:
        source_items.append(source_dir)
        source_dir = os.path.dirname(source_path)

    for item in source_items:
        source_item = os.path.join(source_dir, item)
        dest_item = os.path.join(dest_dir, item)

        if os.path.isdir(source_item):
            clone_structure(source_item, dest_item, preserve_ownership, user_group)
        else:
            if os.path.exists(dest_item):
                os.unlink(dest_item)
            os.link(source_item, dest_item)
            if preserve_ownership:
                shutil.copystat(source_item, dest_item)
            elif user_group:
                uid, gid = get_uid_gid(user_group)
                os.chown(dest_item, uid, gid)

def get_uid_gid(user_group):
    if ':' in user_group:
        user, group = user_group.split(':')
        uid = int(user) if user.isdigit() else pwd.getpwnam(user).pw_uid
        gid = int(group) if group.isdigit() else grp.getgrnam(group).gr_gid  
    else:
        uid = gid = int(user_group) if user_group.isdigit() else pwd.getpwnam(user_group).pw_uid
    return uid, gid

def main():
    parser = argparse.ArgumentParser(description='Clone directory structure with hardlinked files.')
    parser.add_argument('source', help='Path to the source folder')
    parser.add_argument('destination', help='Path to the destination folder')
    parser.add_argument('-p', '--preserve-ownership', action='store_true', help='Preserve ownership of files')
    parser.add_argument('-u', '--user-group', help='Set user and group of files (format: user:group)')
    args = parser.parse_args()

    clone_structure(args.source, args.destination, args.preserve_ownership, args.user_group)

if __name__ == '__main__':
    main()
