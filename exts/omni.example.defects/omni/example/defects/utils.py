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
import omni.kit.commands
import os

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

def get_textures(dir_path, png_type=".png"):
    textures = []
    dir_path += "/"
    for file in os.listdir(dir_path):
        if file.endswith(png_type):
            textures.append(dir_path + file)
    return textures

def get_prim(prim_path: str):
    stage = get_current_stage()
    prim = stage.GetPrimAtPath(prim_path)
    return prim

