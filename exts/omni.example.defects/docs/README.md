# Defects Sample Extension (omni.sample.defects)
![Defects Preview](../data/preview.png)


## Overview

The Defects Sample Extension allows users to choose a texture, that represents a defect, to apply to a [Prim](https://docs.omniverse.nvidia.com/prod_usd/prod_usd/quick-start/prims.html) and generate synthetic data of the position, rotation, and dimensions of that texture.

This Sample Extension utilizes Omniverse's [Replicator](https://developer.nvidia.com/omniverse/replicator) functionality for randomizing and generating synthetic data.

## UI Overview

### Object Parameters

![Object Params](../data/objparam.png)

1. Target Prim
    - This defines what prim to apply the material to. To get the prim path, **select** a prim in the scene then hit the **Copy button**
2. Apply
    - Once you have a Target Prim selected and Copied its path, hitting Apply will bring in the proxy decal material and create the primvar's on the Target Prim.

### Defect Parameters

![Defect Params](../data/defectparam.png)

Randomizations are based on Replicator's [Distributions](https://docs.omniverse.nvidia.com/prod_extensions/prod_extensions/ext_replicator/distribution_examples.html)

1. Defect Semantic
    - The semantic label that will be used to represent the defect in the output file produced by Replicator.
    - Default Value: `defect`
2. Defect Texture
    - A folder location that holds all the texture(s) to choose from. Textures should be in PNG format.
    - Default Value: `None`
    - Defect textures are a normal map representation of the defect. Example shown below:
    - ![texture_sample](../omni/example/defects/data/scratch_0.png)
3. Defect Dimensions (Width and Length)
    - Replicator will choose random values between the Min and Max defined (cms) for the Width and Length.
    - Default Value Min: `0`
    - Default Value Max: `1`
4. Define Defect Region
    - This will create a Plane Prim, this is used as a reference to define a region in which the defect can be in.
    - Default Value: `None`
5. Defect Rotation
    - Replicator will choose random values between the Min and Max defined (cms) and will set that rotation.
    - Default Value Min: `0`
    - Default Value Max: `1`

A recommended set of values using the CarDefectPanel scene is the following:
 - Defect Semantics: Scratch
 - Defect Texture: [Path to Scratchs in nucleus]
 - Defect Dimensions Width: Min 0.01 Max 0.02
 - Defect Dimensions Length: Min 0.015 Max 0.02
 - Define Defect Region: *None*
 - Defect Rotation: Min 0 Max 360

### Replicator Parameters

![Rep Params](../data/repparam.png)

1. Output Directory
    - Defines the location in which Replicator will use to output data. By default it will be `DRIVE/Users/USER/omni.replicator_out`
2. [Render Subframe](https://docs.omniverse.nvidia.com/prod_extensions/prod_extensions/ext_replicator/subframes_examples.html) Count
    - If rendering in RTX Realtime mode, specifies the number of subframes to render in order to reduce artifacts caused by large changes in the scene.
3. Create Replicator Layer
    - Generates the [OmniGraph](https://docs.omniverse.nvidia.com/prod_extensions/prod_extensions/ext_omnigraph.html) or Omni.Replicator graph architecture, if changes are made the user can click this button to reflect changes. This does not run the actual execution or logic.
4. Preview / Run for X frames
    - **Preview** performs a single iteration of randomizations and prevents data from being written to disk.
    - **Run for**  will run the generation for a specified amount of frames. Each frame will be one data file so 100 frames will produce 100 images/json/npy files.

![scratch](../data/scratch.gif)
