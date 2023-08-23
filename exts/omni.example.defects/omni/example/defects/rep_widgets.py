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

import omni.ui as ui
from .widgets import MinMaxWidget, CustomDirectory, PathWidget
from .utils import *
from pxr import Sdf
from pathlib import Path
import omni.kit.notification_manager as nm

TEXTURE_DIR = Path(__file__).parent / "data"
SCRATCHES_DIR = TEXTURE_DIR / "scratches" 

# Parameter Objects

class DefectParameters:
    def __init__(self) -> None:
        self.semantic_label = ui.SimpleStringModel("defect")
        self.count = ui.SimpleIntModel(1)
        self._build_semantic_label()
        self.defect_text = CustomDirectory("Defect Texture Folder",
                                           default_dir=str(SCRATCHES_DIR.as_posix()), 
                                           tooltip="A folder location containing a single or set of textures (.png)",
                                           file_types=[("*.png", "PNG"), ("*", "All Files")])
            
        self.dim_w = MinMaxWidget("Defect Dimensions Width",
                                  min_value=0.1,
                                  tooltip="Defining the Minimum and Maximum Width of the Defect")
        self.dim_h = MinMaxWidget("Defect Dimensions Length",
                                  min_value=0.1,
                                  tooltip="Defining the Minimum and Maximum Length of the Defect")

        self.rot = MinMaxWidget("Defect Rotation", 
                                tooltip="Defining the Minimum and Maximum Rotation of the Defect")
    
    def _build_semantic_label(self):
        with ui.HStack(height=0, tooltip="The label that will be associated with the defect"):
            ui.Label("Defect Semantic")
            ui.StringField(model=self.semantic_label)
    
    def destroy(self):
        self.semantic_label = None
        self.defect_text.destroy()
        self.defect_text = None
        self.dim_w.destroy()
        self.dim_w = None
        self.dim_h.destroy()
        self.dim_h = None
        self.rot.destroy()
        self.rot = None

class ObjectParameters():
    def __init__(self) -> None:
        self.target_prim = PathWidget("Target Prim")

        def apply_primvars(prim):
            # Apply prim vars
            prim.CreateAttribute('primvars:d1_forward_vector', Sdf.ValueTypeNames.Float3, custom=True).Set((0,0,0))
            prim.CreateAttribute('primvars:d1_right_vector', Sdf.ValueTypeNames.Float3, custom=True).Set((0,0,0))
            prim.CreateAttribute('primvars:d1_up_vector', Sdf.ValueTypeNames.Float3, custom=True).Set((0,0,0))
            prim.CreateAttribute('primvars:d1_position', Sdf.ValueTypeNames.Float3, custom=True).Set((0,0,0))
            prim.CreateAttribute('primvars:v3_scale', Sdf.ValueTypeNames.Float3, custom=True).Set((0,0,0))
            nm.post_notification(f"Applied Primvars to: {prim.GetPath()}", hide_after_timeout=True, duration=5, status=nm.NotificationStatus.INFO)

        def apply():
            # Check Paths
            if not check_path(self.target_prim.path_value):
                return 
            
            # Check if prim is valid
            prim = is_valid_prim(self.target_prim.path_value)
            if prim is None:
                return
    
            apply_primvars(prim)
        
        ui.Button("Apply",  
            style={"padding": 5}, 
            clicked_fn=lambda: apply(), 
            tooltip="Apply Primvars and Material to selected Prim."
        )

    def destroy(self):
        self.target_prim.destroy()
        self.target_prim = None

class MaterialParameters():
    def __init__(self) -> None:
        pass