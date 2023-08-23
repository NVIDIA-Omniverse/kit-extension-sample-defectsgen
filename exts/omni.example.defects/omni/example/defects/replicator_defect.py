# SPDX-FileCopyrightText: Copyright (c) 2023 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import omni.replicator.core as rep
import carb
from .rep_widgets import DefectParameters, ObjectParameters
from .utils import *


camera_path = "/World/Camera"

def rep_preview():
    rep.orchestrator.preview()

def rep_run():
    rep.orchestrator.run()

def does_defect_layer_exist() -> bool:
    stage = get_current_stage()
    for layer in stage.GetLayerStack():
        if layer.GetDisplayName() == "Defect":
            return True
    return False

def get_defect_layer():
    stage = get_current_stage()
    pos = 0
    for layer in stage.GetLayerStack():
        if layer.GetDisplayName() == "Defect":
            return layer, pos
        pos = pos + 1
    return None

def create_randomizers(defect_params: DefectParameters, object_params: ObjectParameters):
    diffuse_textures = get_textures(defect_params.defect_text.directory, "_D.png")
    normal_textures = get_textures(defect_params.defect_text.directory, "_N.png")
    roughness_textures = get_textures(defect_params.defect_text.directory, "_R.png")
    def move_defect():
        defects = rep.get.prims(semantics=[('class', defect_params.semantic_label.as_string + '_mesh')])
        plane = rep.get.prim_at_path(object_params.target_prim.path_value)
        with defects:
            rep.randomizer.scatter_2d(plane)
            rep.modify.pose(
                rotation=rep.distribution.uniform(
                    (defect_params.rot.min_value, 0, 90), 
                    (defect_params.rot.max_value, 0, 90)
                ),
                scale=rep.distribution.uniform(
                    (1, defect_params.dim_h.min_value,defect_params.dim_w.min_value),
                    (1, defect_params.dim_h.max_value, defect_params.dim_w.max_value)
                )
            )

        return defects.node
    
    def change_defect_image():
        projections = rep.get.prims(semantics=[('class', defect_params.semantic_label.as_string + '_projectmat')])
        with projections:
            rep.modify.projection_material(
                diffuse=rep.distribution.sequence(diffuse_textures),
                normal=rep.distribution.sequence(normal_textures),
                roughness=rep.distribution.sequence(roughness_textures))
        return projections.node

    rep.randomizer.register(move_defect)
    rep.randomizer.register(change_defect_image)

def create_camera(target_path):
    if is_valid_prim(camera_path) is None:
        camera = rep.create.camera(position=1000, look_at=rep.get.prim_at_path(target_path))
        carb.log_info(f"Creating Camera: {camera}")
    else:
        camera = rep.get.prim_at_path(camera_path)
    return camera

def create_defects(defect_params: DefectParameters, object_params: ObjectParameters):
    target_prim = rep.get.prims(path_pattern=object_params.target_prim.path_value)
    count = 1
    if defect_params.count.as_int > 1:
        count = defect_params.count.as_int
    for i in range(count):
        cube = rep.create.cube(visible=False, semantics=[('class', defect_params.semantic_label.as_string + '_mesh')], position=0, scale=1, rotation=(0, 0, 90))
        with target_prim:
            rep.create.projection_material(cube, [('class', defect_params.semantic_label.as_string + '_projectmat')])

def create_defect_layer(defect_params: DefectParameters, object_params: ObjectParameters, frames: int = 1, output_dir: str = "_defects", rt_subframes: int = 0, use_seg: bool = False, use_bb: bool = True):
    if len(defect_params.defect_text.directory) <= 0:
        carb.log_error("No directory selected")
        return
    
    with rep.new_layer("Defect"):
        create_defects(defect_params, object_params)
        create_randomizers(defect_params=defect_params, object_params=object_params)        
        
        # Create / Get camera
        camera = create_camera(object_params.target_prim.path_value)
        
        # Add Default Light
        distance_light = rep.create.light(rotation=(315,0,0), intensity=3000, light_type="distant")

        render_product  = rep.create.render_product(camera, (1024, 1024))

        # Initialize and attach writer
        writer = rep.WriterRegistry.get("BasicWriter")
        writer.initialize(output_dir=output_dir, rgb=True, semantic_segmentation=use_seg, bounding_box_2d_tight=use_bb)
        # Attach render_product to the writer
        writer.attach([render_product])

        # Setup randomization
        with rep.trigger.on_frame(num_frames=frames, rt_subframes=rt_subframes):
            rep.randomizer.move_defect()
            rep.randomizer.change_defect_image()
