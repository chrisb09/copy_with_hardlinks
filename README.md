Well, this script is kinda pointless because `cp -rl` or `cp -al` exists on linux systems...well, technically it *should* be os-agnostic...but yeah.


# Copy with Hardlinks

A simple Python utility to clone directory structures while creating hardlinks for files instead of copying their data. This is useful for creating efficient backups or snapshots on the same filesystem.

## Features

- **Efficient Cloning:** Uses hardlinks to save space and time.
- **Ownership Preservation:** Option to preserve original file ownership.
- **Custom Ownership:** Option to set a specific user/group for all cloned files.
- **Self-Installation:** Built-in command to install itself as a system-wide utility.
- **Single File Support:** Handles both directories and individual files.

## Usage

### Direct execution

```bash
python3 copy_with_hardlinks.py [source] [destination] [options]
```

### Parameters

- `source`: The file or directory to clone.
- `destination`: The destination directory.
- `-p`, `--preserve-ownership`: Preserve the UID/GID of the original files.
- `-u USER:GROUP`, `--user-group USER:GROUP`: Set a specific user and group for the cloned files.

## Installation

The script can install a wrapper for itself into `/usr/local/bin`:

```bash
python3 copy_with_hardlinks.py install
```

During installation, it will interactively ask if you want to enable certain flags by default (like `--preserve-ownership`). If `/usr/local/bin` is not writable, it will attempt to use `sudo`.

Once installed, you can use the command directly:

```bash
copy-with-hardlinks [source] [destination]
```

## Requirements

- Python 3.x
- Unix-like operating system (for hardlinks and ownership management)
