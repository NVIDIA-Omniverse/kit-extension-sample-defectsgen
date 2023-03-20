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

"""
This is the implementation of the OGN node defined in OgnWritePrimVars.ogn
"""

# Array or tuple values are accessed as numpy arrays so you probably need this import
import numpy
import omni.kit
import omni.usd
from pxr import Gf, Sdf
import omni.graph.core as og

class OgnWritePrimVars:
    """
        Write Primvars to target mesh based on the decal proxy

        Attribute Value Properties:
        Inputs:
            inputs.proxy_path
            inputs.target_path
    """
    @staticmethod
    def compute(db) -> bool:
        """Compute the outputs from the current input"""

        try:
            context = omni.usd.get_context()
            stage = context.get_stage()
            proxy_prim = stage.GetPrimAtPath(Sdf.Path(db.inputs.proxy_path))
            # Get Prim Direction Vectors
            proxy_world_trans = omni.usd.get_world_transform_matrix(proxy_prim)
            
            x_vector = Gf.Vec3d(proxy_world_trans[0][0], proxy_world_trans[0][1], proxy_world_trans[0][2])
            right_vector = x_vector.GetNormalized()
            y_vector = Gf.Vec3d(proxy_world_trans[1][0], proxy_world_trans[1][1], proxy_world_trans[1][2])
            up_vector = y_vector.GetNormalized()
            z_vector = Gf.Vec3d(proxy_world_trans[2][0], proxy_world_trans[2][1], proxy_world_trans[2][2])
            forward_vector = z_vector.GetNormalized()

            # Get Prim Position and Scale
            position = proxy_prim.GetAttribute('xformOp:translate').Get()
            scale = proxy_prim.GetAttribute('xformOp:scale').Get()
            scale = (scale[0], scale[1], scale[2])
            # # Set Attributes to Target Prim
            target_prim = stage.GetPrimAtPath(db.inputs.target_path)
            target_prim.GetAttribute('primvars:d1_forward_vector').Set(forward_vector)
            target_prim.GetAttribute('primvars:d1_right_vector').Set(right_vector)
            target_prim.GetAttribute('primvars:d1_up_vector').Set(up_vector)
            target_prim.GetAttribute('primvars:d1_position').Set(position)
            target_prim.GetAttribute('primvars:v3_scale').Set(scale) 
            db.outputs.execOut = og.ExecutionAttributeState.ENABLED
            # With the compute in a try block you can fail the compute by raising an exception
        
        except Exception as error:
            # If anything causes your compute to fail report the error and return False
            db.log_error(str(error))
            return False

        # Even if inputs were edge cases like empty arrays, correct outputs mean success
        return True
