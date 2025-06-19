# `delblock`

Deletes a block of lines from a file based on a complicated multi-line regex. WIP.

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
delblock --help
```

```sh
# just prints the diff of what it would od
delblock --dry-run ~/.bashrc
```

```sh
# don't overwrite ~/.bashrc; instead write to new_bashrc
delblock -o new_bashrc ~/.bashrc
```

```sh
# overwrite ~/.bashrc with the block deleted
delblock ~/.bashrc
```

## Running the tests

```sh
# run tests
./tests/test_delblock.py
```