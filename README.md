# sfdlpy

A CLI Tool to handle [SFDL Files](https://sfdl.net/). It can create them and read them to download the provided files.

# Requirements

* Python 3.8.0
* click 7.0
* ftputil 3.4
* pycryptodome 3.9.4

# Installation

```
❯ pip install sfdlpy
```

# Usage

```
❯ sfdlpy --help                                                                                                                                        ~/c/sfdlpy master
Usage: sfdlpy [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  create-from  Create SFDL File from an FTP Link.
  create-with  Create SFDL with passed data
  load         Download a SFDL File.

```

# Commands

## create-from

### Usage

```
❯ sfdlpy create-from --help
Usage: sfdlpy create-from [OPTIONS] LINK

  Create SFDL File from an FTP Link.

Options:
  --help  Show this message and exit.
```


## create-with

### Usage

```
❯ sfdlpy create-with --help                                                                                                                            ~/c/sfdlpy master
Usage: sfdlpy create-with [OPTIONS]

  Create SFDL with passed data

Options:
  --host TEXT      The FTP Server to connect to.
  --user TEXT      The user to use for FTP Login
  --password TEXT  The password to use for FTP Login
  --port INTEGER   The Port to connect to.
  --path TEXT      Which file/dir to download
  --help           Show this message and exit.
```

## load

### Usage
```
❯ sfdlpy load --help                                                                                                                                   ~/c/sfdlpy master
Usage: sfdlpy load [OPTIONS] FILE

  Download a SFDL File.

Options:
  -o, --output DIRECTORY  The output directory.
  -p, --password TEXT     Password for decryption.
  --help                  Show this message and exit.
```
