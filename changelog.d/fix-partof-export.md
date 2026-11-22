### Fixed

- `intblocks.partof` holds parent ids when the source YAML uses the object form
  `partof: {id: BIS, name: ...}`. Before, the build exported the object's keys, so 53
  intblocks (for example `FSB`, `AFRICACDC`, `ITLOS`, `OPCW`, `LVFO`) had
  `partof = ['id', 'name']`; `FSB` now has `['BIS']`. A list of `{id, name}` objects
  exports each `id` instead of the object's string form. No source YAML changes.
