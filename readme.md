# `replace_block`

Replaces a block of lines from a file based on a complicated multi-line regex.

## Prerequisites

Install `delta` (for showing diffs):

For macOS:

```sh
brew install git-delta
```

or for Ubuntu and other Debian-based systems:

```sh
DELTA_VERSION=$(curl -s https://api.github.com/repos/dandavison/delta/releases/latest | grep '"tag_name":' | cut -d'"' -f4)
wget https://github.com/dandavison/delta/releases/download/${DELTA_VERSION}/git-delta_${DELTA_VERSION#v}_amd64.deb
sudo dpkg -i git-delta_${DELTA_VERSION#v}_amd64.deb
```

## Usage

### Available regex patterns

The patterns are defined in `re_pattern_library.py`.  For a list and short description, use the `-l` flag:

```sh
./replace_block -l
```

### Deleting a block (no replacement)

```sh
# show help
replace_block --help
```

```sh
# delete the block, but just prints the diff of what it would do
replace_block --dry-run ~/.bashrc
```

```sh
# delete the block, but write to new file instead of overwriting ~/.bashrc
replace_block -o new_bashrc ~/.bashrc
```

```sh
# overwrite ~/.bashrc with the block deleted
replace_block ~/.bashrc
```

### Replacing a block

```sh
# replace the block with the contents of 'readme.md'
./replace_block -r- -p bash_rc_export_path -d tests/replace_block_debug_input.txt < readme.md
```

```sh
# replace the block with a string from the command line
./replace_block -r "export PATH=/usr/local/bin:$PATH" -p bash_rc_export_path -d ~/.bashrc
```

## Running the tests

```sh
# run tests
./tests/test_replaceblock.py
```