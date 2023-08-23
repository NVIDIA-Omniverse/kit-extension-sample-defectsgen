# Changelog

All notable changes to this project will be documented in this file.

and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.1] - 2023-08-23

### Changed

- Changed annotations to use Tight Bounding Box instead of Loose
- Updated ReadMe

## [1.1.0] - 2023-08-15

### Removed

- Ogn nodes, these nodes are now apart of the replicator pipeline
- proxy.usd, Replicator has built in functionality in their nodes that creates the proxy
- Functions in `utils.py` that are not longer being used
- Region selection

### Added

- Options to either use bounding boxes or segmentation
- Functionality to remove new prims created by Replicator
- Notificataion popup for when the prim vars are applied to the mesh

### Changed

- Textures are now represented as a D, N, and R
    - D is Diffuse
    - N is Normal
    - R is Roughness
- Default values for dimensions start at 0.1
- Output Directory UI defaults to replicator default output directory
- Textures folder UI defaults to folder inside of extension with sample scratches
- Updated README talking about the new images being used

## [1.0.1] - 2023-04-18

### Changed

- CustomDirectory now takes file_types if the user wants to specify the files they can filter by
- Material that is applied to the prim

### Fixed

- Nodes not connecting properly with Code 2022.3.3
- In utils.py if rotation is not found use (0,0,0) as default
- lookat in utils.py could not subtract Vec3f by Vec3d