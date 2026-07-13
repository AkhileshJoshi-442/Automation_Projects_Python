# System Process Logger with Scheduling

## Description

A Python automation script that periodically scans all running processes on
the system and logs their PID, name, user, and memory usage to a timestamped
log file. The log file is then emailed for record-keeping.

## Features

- Scans all currently running processes
- Records PID, process name, username, and memory usage (in MB)
- Generates a new timestamped log file on every run
- Log file is written as an aligned table for easy reading
- Sends the log file as an email attachment after every run
- Runs on a repeating schedule (chosen interval, in minutes)
- Continues running even if the email could not be sent

## Requirements

### Standard library (included with Python, no installation needed)

- `os`
- `sys`
- `time`
- `smtplib`
- `email.message`

### Third-party (must be installed)

- `psutil`
- `schedule`

Install the third-party libraries with:

```
pip install psutil schedule
```

## Usage

```
python ProcessLogger.py <folder> <interval> <emailpassword> <senderemail> <receiveremail>
```

| Argument | Description |
|---|---|
| `folder` | Path to the folder where log files will be created |
| `interval` | How often to run, in minutes |
| `emailpassword` | Gmail App Password of the sender account |
| `senderemail` | Gmail address used to send the log |
| `receiveremail` | Email address that receives the log |

If `folder` does not exist, it will be created automatically.

### Help and usage flags

```
python ProcessLogger.py --h
python ProcessLogger.py --u
```

## Function Reference

### `ProcessScan()`
Iterates over every running process on the system and collects its PID,
name, username, and memory usage (converted from bytes to megabytes).
Processes that cannot be accessed (closed, restricted, or zombie processes)
are skipped. Returns a list of dictionaries, one per process.

### `CreateLog(FolderName)`
Calls `ProcessScan` to get the current list of processes and writes them to a
new timestamped `.log` file inside `FolderName`. The file contains a header,
an aligned table with `PID`, `Name`, `User`, and `Memory(MB)` columns, and a
total process count. Returns the path to the created log file.

### `sendmail(fpath, emailpassword, senderemail, receiveremail)`
Reads the given log file and sends it as an email attachment from
`senderemail` to `receiveremail`, using Gmail's SMTP server with the supplied
app password. Subject line is `"log of running processes"`.

### `task(foldername, emailpassword, senderemail, receiveremail)`
Runs the full cycle for one scheduled execution: creates the process log file
and sends it by email. If the email fails, prints the error and continues
without stopping the script.

### `main()`
Reads command line arguments, validates the target folder, and either prints
help/usage information or schedules `task` to run repeatedly at the chosen
interval.

## Notes and Limitations

- **Security**: The email password is passed as a plain command line argument.
  It will be visible in your terminal history and to anyone who can see your
  screen or process list. Do not use this on a shared computer, and use a
  Gmail App Password rather than your real account password.
- A typical system has 100+ running processes, so each log file can be long.
  Short intervals (e.g. 1 minute) will generate and email files frequently —
  use a longer interval for normal use.
- Some processes may be skipped if they require elevated permissions to
  inspect (depends on whether the script is run as Administrator/root).
- Stop the script with `Ctrl+C`. This will print a `KeyboardInterrupt`
  message, which is expected.
