# Changelog

All notable changes to this project will be documented in this file.

and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.1] - 2023-04-18

### Changed

- CustomDirectory now takes file_types if the user wants to specify the files they can filter by
- Material that is applied to the prim

### Fixed

- Nodes not connecting properly with Code 2022.3.3
- In utils.py if rotation is not found use (0,0,0) as default
- lookat in utils.py could not subtract Vec3f by Vec3d
