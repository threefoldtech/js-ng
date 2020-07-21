# Release

The document specifies the necessary steps to release js-ng.

## Versioning

The following need to have the same version as the release version:

- jsng config version (Found in config module)
- jsng poetry version (Found in pyprojects.toml)
- The release tag

This is needed in order to make the self-update feature of the sdk binary possible.

## SDK binary

A statically compiled sdk binary needs to be part of the release.
