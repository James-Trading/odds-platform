Version 0.1
------------
- Event creation
- Market creation
- Selection creation

Version 0.2
------------
- Save/load
- Search
- Audit log

Version 0.3
------------
- Templates
- Delete functions

## v0.1 (In Progress)

### Added
- Pending price workflow
- Save pending changes
- Event publication
- Client publishing
- Event export
- Scheduler foundation
- Start time and suspend mode for events

### Changed
- Price changes now use pending prices before being committed.
- Published markets now update automatically after saved changes.

### Fixed
- Scheduler now ignores invalid dates instead of crashing.
- Added migrations for new data fields.