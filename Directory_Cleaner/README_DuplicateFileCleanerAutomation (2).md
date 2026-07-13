# Duplicate File Cleaner & Log Automation

## Description

A Python automation script that periodically scans a directory for duplicate
files, deletes the duplicates, generates a log file recording what was kept
and what was deleted, and emails that log file for audit purposes.

## Features

- Recursively scans a directory and all its subfolders
- Detects duplicate files using MD5 checksums
- Automatically deletes duplicate copies, keeping one original
- Generates a timestamped log file in a dedicated `CleanerLogs` folder
- Log file includes a summary table of kept vs deleted files
- Sends the log file as an email attachment after every run
- Runs on a repeating schedule (chosen interval, in minutes)
- Continues running even if the email could not be sent

## Requirements

### Standard library (included with Python, no installation needed)

- `os`
- `sys`
- `time`
- `hashlib`
- `smtplib`
- `email.message`

### Third-party (must be installed)

- `schedule`

Install the third-party library with:

```
pip install schedule
```

## Usage

```
python DuplicateFileCleanerAutomation.py <directory> <interval> <emailpassword> <senderemail> <receiveremail>
```

| Argument | Description |
|---|---|
| `directory` | Absolute path to the folder to scan and clean |
| `interval` | How often to run, in minutes |
| `emailpassword` | Gmail App Password of the sender account |
| `senderemail` | Gmail address used to send the log |
| `receiveremail` | Email address that receives the log |

### Help and usage flags

```
python DuplicateFileCleanerAutomation.py --h
python DuplicateFileCleanerAutomation.py --u
```

## Function Reference

### `calculatechecksum(path, blocksize=1024)`
Reads a file in chunks and returns its MD5 checksum. Two files with the same
checksum are considered identical.

### `findduplicate(directoryname=".")`
Walks through the given directory and all subfolders, calculates a checksum
for every file, and groups file paths by checksum. Returns a dictionary
where each key is a checksum and each value is a list of file paths with
that checksum.

### `deleteduplicate(path=".")`
Calls `findduplicate` to find groups of identical files. For each group with
more than one file, keeps the first file and deletes the rest. Returns two
lists: `deletedfiles` (paths that were removed) and `keptfiles` (paths that
were kept as originals).

### `generatelog(deletedfiles, keptfiles, directoryname)`
Creates a `CleanerLogs` folder inside the target directory if it does not
already exist. Writes a timestamped `.log` file containing the kept files,
deleted files, total deleted count, and a summary table with `Status` and
`File path` columns. Returns the path to the log file.

### `sendmail(fpath, emailpassword, senderemail, receiveremail)`
Reads the given log file and sends it as an email attachment from
`senderemail` to `receiveremail`, using Gmail's SMTP server with the supplied
app password. Subject line is `"log of deleted files"`.

### `task(directoryname, emailpassword, senderemail, receiveremail)`
Runs the full cycle for one scheduled execution: deletes duplicates, generates
the log file, and sends it by email. If the email fails, prints the error and
continues without stopping the script.

### `main()`
Reads command line arguments, validates them, and either prints help/usage
information or schedules `task` to run repeatedly at the chosen interval.

## Notes and Limitations

- **Security**: The email password is passed as a plain command line argument.
  It will be visible in your terminal history and to anyone who can see your
  screen or process list. Do not use this on a shared computer, and use a
  Gmail App Password rather than your real account password.
- The directory scan re-checks the entire folder on every run; previously
  deleted duplicates are not remembered between runs.
- If `os.remove()` fails (for example, a file is open in another program),
  the script will stop with an unhandled error.
- Stop the script with `Ctrl+C`. This will print a `KeyboardInterrupt`
  message, which is expected.
