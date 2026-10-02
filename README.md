# Retirement Countdown

A small, semi-transparent desktop widget that counts down to your retirement date.

It shows:

- the target retirement date
- the time remaining in days, hours, and minutes
- the number of workdays left (weekdays, minus any holidays you list)
- a message of the day

The window has no title bar, stays on top of other windows by default, and remembers its position between runs.

## Requirements

- Windows, macOS, or Linux
- Python 3.8 or newer with tkinter (included with the standard Windows and macOS installers from python.org)

It uses only the Python standard library, so there is nothing to install.

## Running

On Windows, double-click `RetirementCountdown.pyw`. The `.pyw` extension runs it without a console window. You can also start it from a command prompt:

```
pythonw RetirementCountdown.pyw
```

To see error output while troubleshooting, run it with a console:

```
python RetirementCountdown.pyw
```

On the first run, you'll be asked for your retirement date. Use a format like `June 1 2027 17:00:00` or `June 1 2027`.

To launch it at sign-in on Windows, put a shortcut to `RetirementCountdown.pyw` in your Startup folder. Press Win+R and run `shell:startup` to open that folder.

## Using it

| Action | Result |
| --- | --- |
| Left-drag (or middle-drag) | Move the window |
| Right-click | Open the menu |

Menu options:

- **Stay on Top**: keep the window above other windows
- **Reset Position**: move the window back to the bottom-right corner
- **Update Retirement Date**: change the target date (Cancel keeps the current one)
- **About**: version information
- **Close App**: save the window position and exit

## Settings

Settings are stored in `retirement_settings.json` in your Documents folder. If Windows redirects Documents to OneDrive, the file goes in the OneDrive folder.

```json
{
  "retirement_date": "June 1 2027 17:00:00",
  "window_position": {"x": 1715, "y": 920, "width": 200, "height": 110},
  "holidays": ["2026-11-26", "2026-12-25", "2027-01-01"]
}
```

`holidays` is optional and is only edited by hand. List dates in `YYYY-MM-DD` format, and they'll be left out of the workday count. Entries it can't read are ignored.

### How workdays are counted

Today is not counted. Every weekday from tomorrow through the retirement date is counted, including the retirement day itself, except any listed holidays.

## License

MIT. See [LICENSE](LICENSE).
