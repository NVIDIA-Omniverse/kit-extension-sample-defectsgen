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

import omni.usd
import carb
from pxr import UsdGeom
import omni.kit.commands
import os
import omni.timeline
from pxr import Gf

def start_timeline():
    timeline_interface = omni.timeline.get_timeline_interface()
    timeline_interface.play()

def get_current_stage():
    context = omni.usd.get_context()
    stage = context.get_stage()
    return stage

def check_path(path: str) -> bool:
    if not path:
        carb.log_error("No path was given")
        return False
    return True

def is_valid_prim(path: str):
    prim = get_prim(path)
    if not prim.IsValid():
        carb.log_warn(f"No valid prim at path given: {path}")
        return None
    return prim

def delete_prim(path: str):
    omni.kit.commands.execute('DeletePrims',
        paths=[path],
        destructive=False)

def get_prim_attr(prim_path: str, attr_name: str):
    prim = get_prim(prim_path)
    return prim.GetAttribute(attr_name).Get()

def set_prim_attr(prim_path: str, attr_name: str, new_value):
    prim = get_prim(prim_path)
    prim.GetAttribute(attr_name).Set(new_value)

def get_textures(dir_path):
    textures = []
    for file in os.listdir(dir_path):
        if file.endswith(".png"):
            textures.append(dir_path + file)
    return textures

def get_up_axis() -> str:
    stage = get_current_stage()
    up_axis = UsdGeom.GetStageUpAxis(stage)
    return up_axis

def get_prim(prim_path: str):
    stage = get_current_stage()
    prim = stage.GetPrimAtPath(prim_path)
    return prim

def realign_prim_to_target(target_path, prim_path):
    position = get_prim_attr(target_path, 'xformOp:translate')
    rotation = get_prim_attr(target_path, 'xformOp:rotateXYZ') or Gf.Vec3d(0,0,0)
    set_prim_attr(prim_path, 'xformOp:translate', position)
    set_prim_attr(prim_path, 'xformOp:rotateXYZ', rotation)
    proxy_world_trans = omni.usd.get_world_transform_matrix(get_current_stage().GetPrimAtPath(prim_path))
    proxy_rotation = proxy_world_trans.ExtractRotationQuat().GetNormalized()
    y_axis = (0,1,0)
    up_vector = (proxy_rotation * Gf.Quatd(0, y_axis) * proxy_rotation.GetInverse()).GetImaginary()
    trans = (up_vector * 250) + get_prim_attr(prim_path, 'xformOp:translate')
    set_prim_attr(prim_path, 'xformOp:translate', trans)

def look_at(target_path, prim_path):
    forward = Gf.Vec3d(1.0,0.0,0.0)
    target = get_prim_attr(target_path, 'xformOp:translate')
    start = get_prim_attr(prim_path, 'xformOp:translate')
    direction = Gf.Vec3d(target) - start
    rotation = Gf.Rotation(forward, direction)
    decomposed = rotation.Decompose(Gf.Vec3d.ZAxis(), Gf.Vec3d.YAxis(), Gf.Vec3d.XAxis())
    rotateXYZ = (decomposed[2], decomposed[1], decomposed[0])
    set_prim_attr(prim_path, 'xformOp:rotateXYZ', rotateXYZ)