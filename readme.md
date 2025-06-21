# `replace_block`

Deletes, replaces or inserts a block of lines into a file overwriting one of various multi-line regex patterns.  The is a library of patterns is in [`re_pattern_library.py`](re_pattern_library.py).

## Table of Contents

- [Installation](#installation)
  - [Requirements](#requirements)
  - [Install the package](#install-the-package)
- [Usage](#usage)
  - [Available regex patterns](#available-regex-patterns)
  - [Deleting a block (no replacement)](#deleting-a-block-no-replacement)
  - [Replacing a block](#replacing-a-block)
  - [Replacing or appending/prepending](#replacing-or-appendingprepending)
    - [Controlling replace vs append/prepend behavior](#controlling-replace-vs-appendprepend-behavior)
    - [Newline control](#newline-control)
  - [Inserting a block](#inserting-a-block)
  - [Processing multiple files](#processing-multiple-files)
  - [Backup files](#backup-files)
  - [Running the unit tests](#running-the-unit-tests)

## Installation

### Requirements

Install `delta` (for showing diffs) and make sure it's in your `PATH`:

- For macOS:

    ```sh
    brew install git-delta
    ```

- For Ubuntu and other Debian-based systems:

    ```sh
    DELTA_VERSION=$(curl -s https://api.github.com/repos/dandavison/delta/releases/latest | grep '"tag_name":' | cut -d'"' -f4)
    wget https://github.com/dandavison/delta/releases/download/${DELTA_VERSION}/git-delta_${DELTA_VERSION#v}_amd64.deb
    sudo dpkg -i git-delta_${DELTA_VERSION#v}_amd64.deb
    ```

### Install the package

```sh
git clone https://github.com/mikegoelzer/file_transform_tools.git
cd file_transform_tools
pip install --prefix ~/.local -e .
```

## Usage

### Available regex patterns

The patterns are defined in [`re_pattern_library.py`](re_pattern_library.py).  For a list and short descriptions, see `--help`. 

```sh
./replace_block --help
```

### Deleting a block (no replacement)

```sh
# delete the block, but with --dry-run just prints the diff of what it would do
replace_block --dry-run -pat bash_rc_export_path ~/.bashrc
```

```sh
# delete the block, but write to new file instead of overwriting ~/.bashrc
replace_block -o new_bashrc -p bash_rc_export_path ~/.bashrc
```

```sh
# overwrite ~/.bashrc with the block deleted
replace_block -pat bash_rc_export_path~/.bashrc
```

### Replacing a block

Replacement string can come from the command line with `-r "<string>"`:

```sh
# replace the block in ~/.bashrc with a string from the command line
./replace_block -r "export PATH=/usr/local/bin:$PATH" -pat bash_rc_export_path ~/.bashrc
```

Replacement string can come from stdin with `-r -`:

```sh
# replace the block with the contents of 'replacement.txt'
# (--dry-run just displays the diff, doesn't modify the file)
./replace_block -r- -pat bash_rc_export_path --dry-run tests/test_vectors/replace_block_debug_input.txt < replacement.txt
```

Replacement string can come from a file with `-r @<filename>`:

```sh
# replace the block with the contents of 'replacement.txt'
# (--dry-run just displays the diff, doesn't modify the file)
./replace_block -r @replacement.txt -pat bash_rc_export_path --dry-run tests/test_vectors/replace_block_debug_input.txt
```

### Replacing or appending/prepending

If the block is not found, by default nothing will be done.  Use `--append/-A` or `--prepend/-P` if you want the replacement text to be added anyway.

Example (append to `~/.bashrc` if block is not found):

```sh
# replace the block in ~/.bashrc with a string from the command line, 
# or append the string to ~/.bashrc if the block is not found
# (--dry-run just displays the diff, doesn't modify ~/.bashrc)
./replace_block -r "export PATH=/usr/local/bin:$PATH" -p bash_rc_export_path --append --dry-run ~/.bashrc
```

#### Controlling replace vs append/prepend behavior

You may want slightly different replacement text inserted when you are replacing an existing block vs appending/prepending the block for the first time.  Both `-A` and `-P` take an optional argument string that is inserted along with your replacement text only when no replacement is being performed.

For `-A`, the argument is inserted **before** the replacement text.  For `-P`, the argument is inserted **after** the replacement text.

Example:

```sh
echo -ne $BASHRC_UPDATE_STR | replace-block -y -b -r - -pat bash_rc_export_path -A $'\n' ~/.bashrc
```

If the block is already in `.bashrc`, it is simply replaced with $BASHRC_UPDATE_STR.  But if it's not already there, then `.bashrc` will be appended with a newline followed by $BASHRC_UPDATE_STR.

(Note that `-A $'\n'` is a shell convention that inserts an actual newline instead of a literal n.)

With `-P`, the insertion order is the opposite:

```sh
echo -ne $BASHRC_UPDATE_STR | replace-block -y -b -r - -pat bash_rc_export_path -P $'\n' ~/.bashrc
```

Assuming the block was not already present in `.bashrc`, then `.bashrc` will be prepended with $BASHRC_UPDATE_STR followed by a newline.

#### Newline control

You can control the final number of newlines both before and after your replacement or insertion with the `-w <num_before> <num_after>` option.  The default is to do nothing, but if you want to ensure that there is is exactly one newline before your replacement or insertion, and two newlines after, you can use `-w 1 2`:

Example:

```sh
echo -ne $BASHRC_UPDATE_STR | replace-block -y -b -r - -pat bash_rc_export_path -A -w 1 2 ~/.bashrc
```

### Inserting a block

You can omit `-pat` to entirely to just append or prepend the pattern into the file.  In this case, the "replacement" string is really an "insertion" string.

```sh
# insert the string at the end of ~/.bashrc
./replace_block -r "export PATH=/usr/local/bin:$PATH" --append ~/.bashrc
```

which is equivalent to:

```sh
echo "export PATH=/usr/local/bin:$PATH" >> ~/.bashrc
```

### Processing multiple files

You can pass multiple files to `replace_block` to replace the same block of text in each file with the same replacement string.  However, the `--outfile` option is not supported with multiple files, so you must either allow overwrite or use `--dry-run` if you want to test.

```sh
./replace_block -r "export PATH=/usr/local/bin:$PATH" -pat bash_rc_export_path ~/.bashrc ~/.zshrc
```

### Backup files

If you're worried about clobbering your input file, you can use the `-b` option to create a backup of the file before overwriting it.

The back up file is saved to `/tmp` with a name like `/tmp/[filename]-[timestamp].bak`.

Example:

```sh
./replace_block -b -r "replacement text" -pat bash_rc_export_path ~/.bashrc
# creates something like /tmp/home-user-.bashrc-20250621_120100.000000.bak
```

If you create these files, you must delete them manually later (if you wish to clean them up).




## Running the unit tests

```sh
# run tests
./tests/test_replaceblock.py
```