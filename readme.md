# `delblock

Deletes a block of lines from a file based on a complicated multi-line regex

## Prereqs

Install `delta`:

```sh
# for macOS and brew-based systems
brew install git-delta
```

or

```sh
# for Ubuntu and other Debian-based systems

# Get latest version number
DELTA_VERSION=$(curl -s https://api.github.com/repos/dandavison/delta/releases/latest | grep '"tag_name":' | cut -d'"' -f4)

# Download and install
wget https://github.com/dandavison/delta/releases/download/${DELTA_VERSION}/git-delta_${DELTA_VERSION#v}_amd64.deb

sudo dpkg -i git-delta_${DELTA_VERSION#v}_amd64.deb
```

## Usage

```sh
# show help
delblock.py --help
```

```sh
# just prints the diff of what it would od
delblock.py --dry-run ~/.bashrc
```

```sh
# don't overwrite ~/.bashrc; instead write to new_bashrc
delblock.py -o new_bashrc ~/.bashrc
```

```sh
# overwrite ~/.bashrc with the block deleted
delblock.py ~/.bashrc
```

## Tests

```sh
# run tests
./test_delblock.py
```