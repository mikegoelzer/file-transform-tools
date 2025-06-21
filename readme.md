# `replace_block`

Deletes, replaces or inserts a block of lines into a file overwriting one of various multi-line regex patterns.  The is a library of patterns is in [`re_pattern_library.py`](re_pattern_library.py).

## Requirements

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

## Usage

### Available regex patterns

The patterns are defined in [`re_pattern_library.py`](re_pattern_library.py).  For a list and short descriptions, use the `-l` flag:

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

### Replacing or appending/prepending

If the block is not found, by default nothing will be done.  Use `--append/-A` or `--prepend/-P` if you want the replacement text to be added anyway.

Example (append to `~/.bashrc` if block is not found):

```sh
# replace the block in ~/.bashrc with a string from the command line, 
# or append the string to ~/.bashrc if the block is not found
# (--dry-run just displays the diff, doesn't modify ~/.bashrc)
./replace_block -r "export PATH=/usr/local/bin:$PATH" -p bash_rc_export_path --append --dry-run ~/.bashrc
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

## Running the unit tests

```sh
# run tests
./tests/test_replaceblock.py
```