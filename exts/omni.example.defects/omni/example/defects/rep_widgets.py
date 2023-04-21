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

import omni.kit.commands
import omni.ui as ui
from .widgets import MinMaxWidget, CustomDirectory, PathWidget
from .utils import *
from pathlib import Path
from pxr import Sdf, Gf
# Parameter Objects

class DefectParameters:
    def __init__(self) -> None:
        self.semantic_label = ui.SimpleStringModel("defect")
        self._build_semantic_label()
        self.defect_text = CustomDirectory("Defect Texture", 
                                           tooltip="A folder location containing a single or set of textures (.png)",
                                           file_types=[("*.png", "PNG"), ("*", "All Files")])
        self.dim_w = MinMaxWidget("Defect Dimensions Width",
                                  tooltip="Defining the Minimum and Maximum Width of the Defect")
        self.dim_h = MinMaxWidget("Defect Dimensions Length",
                                  tooltip="Defining the Minimum and Maximum Length of the Defect")
        self.define_region = PathWidget("Define Defect Region", button_label="New", read_only=True,
                                        tooltip="Define a region in which the defect will appear")
        def create_region():
            region_path = "/World/Region_Plane"
            if is_valid_prim(region_path):
                delete_prim(region_path)
            omni.kit.commands.execute('CreateMeshPrimWithDefaultXform',
                prim_type='Plane',
                prim_path=region_path,
            )
            self.define_region.path_value = region_path
        self.define_region._button.set_clicked_fn(lambda: create_region())

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
        self.define_region.destroy()
        self.define_region = None

class ObjectParameters():
    def __init__(self) -> None:
        self.target_prim = PathWidget("Target Prim")
        self.default_payload_path = "/World/proxy"
        self.material_prim = self.default_payload_path + "/Looks/PsuedoDecal"

        def apply_primvars(prim):
            # Apply prim vars
            prim.CreateAttribute('primvars:d1_forward_vector', Sdf.ValueTypeNames.Float3, custom=True).Set((0,0,0))
            prim.CreateAttribute('primvars:d1_right_vector', Sdf.ValueTypeNames.Float3, custom=True).Set((0,0,0))
            prim.CreateAttribute('primvars:d1_up_vector', Sdf.ValueTypeNames.Float3, custom=True).Set((0,0,0))
            prim.CreateAttribute('primvars:d1_position', Sdf.ValueTypeNames.Float3, custom=True).Set((0,0,0))
            prim.CreateAttribute('primvars:v3_scale', Sdf.ValueTypeNames.Float3, custom=True).Set((0,0,0))
        def import_proxy(prim_path):
            # Import proxy usd into the stage
            proxy_usd = str(Path(__file__).parent / "data" / "proxy.usd")
            omni.kit.commands.execute("CreatePayload",
                usd_context=omni.usd.get_context(),
                path_to=self.default_payload_path, 
                asset_path=proxy_usd,
                instanceable=False
            )
            realign_prim_to_target(prim_path, '/World/proxy/DecalProxy')
            look_at(target_path=prim_path, prim_path='/World/proxy/DecalProxy')

        def apply_material():
            # Apply Sample Material
            omni.kit.commands.execute('BindMaterial',
                material_path=self.material_prim,
                prim_path=[self.target_prim.path_value],
                strength=['weakerThanDescendants'])
            
        def apply_rigidbody():
            omni.kit.commands.execute('SetRigidBody',
                path=Sdf.Path(self.target_prim.path_value),
                approximationShape='convexDecomposition',
                kinematic=False)
            omni.kit.commands.execute('ChangeProperty',
                prop_path=Sdf.Path(self.target_prim.path_value + '.physxRigidBody:disableGravity'),
                value=True,
                prev=None)

        def apply():
            # Check Paths
            if not check_path(self.target_prim.path_value):
                return 
            
            # Check if prim is valid
            prim = is_valid_prim(self.target_prim.path_value)
            if prim is None:
                return
            
            # Delete proxy if it already exists
            if is_valid_prim(self.default_payload_path):
                delete_prim(self.default_payload_path)

            import_proxy(self.target_prim.path_value)
            apply_primvars(prim)
            apply_rigidbody()
            
            # Check if Material is valid
            if is_valid_prim(self.material_prim) is None:
                return
            
            apply_material()

        ui.Button("Apply",  
            style={"padding": 5}, 
            clicked_fn=lambda: apply(), 
            tooltip="Apply Primvars and Material to selected Prim."
        )

    def destroy(self):
        self.target_prim.destroy()
        self.target_prim = None