# Changelog

All notable changes to this project are documented here.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project uses [Semantic Versioning](https://semver.org/).

## [1.0.2] - 2026-10-02

### Added
- Optional `holidays` list in the settings file. These dates are left out of the workday count.
- README, LICENSE (MIT), and this changelog.

### Changed
- Renamed `RetirementCountdown.py` to `RetirementCountdown.pyw` so it runs without a console window on Windows.
- The bottom message is now picked once per day instead of changing every 30 seconds.
- The settings file now goes in the real Documents folder, including when it's redirected to OneDrive. Settings from the old `%USERPROFILE%\Documents` location are read automatically and moved on the next save.
- Cancelling the date dialog now keeps the current date instead of showing a "using default" message.

### Fixed
- The source file used non-breaking spaces for indentation, which stopped Python from running it.
- An unreadable date entered through "Update Retirement Date" was saved anyway, which caused an error popup on every launch. Invalid dates are now rejected, and you're asked again.
- The default window height didn't match between Reset Position (110 px) and restoring a saved position (130 px).

## [1.0.1]

### Added
- The retirement date and window position are saved in a settings file in the Documents folder.

## [1.0.0]

### Added
- Initial release: a translucent, borderless countdown window with the target date, time remaining, workdays remaining, and a rotating message.
