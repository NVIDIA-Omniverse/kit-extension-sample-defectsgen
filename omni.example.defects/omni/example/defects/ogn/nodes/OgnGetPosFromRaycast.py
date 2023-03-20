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
This is the implementation of the OGN node defined in .ogn.ogn
"""

# Array or tuple values are accessed as numpy arrays so you probably need this import
import numpy
import omni.usd
import omni.physx
from omni.physx import get_physx_scene_query_interface
from pxr import Gf
import omni.graph.core as og
"""
Attribute Value Properties:
    Inputs:
        inputs.distance
        inputs.execIn
        inputs.prim_path
    Outputs:
        outputs.execOut
        outputs.hit_position
"""

class OgnGetPosFromRaycast:
    """
         Get the position of an object based on the raycast 
    """
    @staticmethod
    def compute(db) -> bool:
        """Compute the outputs from the current input"""

        try:
            # With the compute in a try block you can fail the compute by raising an exception
            context = omni.usd.get_context()
            stage = context.get_stage()
            proxy_prim = stage.GetPrimAtPath(db.inputs.prim_path)
            # Projects a raycast from 'origin', in the direction of 'rayDir', for a length of 'distance' cm
            # Parameters can be replaced with real-time position and orientation data  (e.g. of a camera)

            proxy_world_trans = omni.usd.get_world_transform_matrix(proxy_prim)
            x_vector = Gf.Vec3d(proxy_world_trans[0][0], proxy_world_trans[0][1], proxy_world_trans[0][2])
            direction = x_vector.GetNormalized()

            proxy_origin = Gf.Vec3d(proxy_world_trans[3][0], proxy_world_trans[3][1], proxy_world_trans[3][2])
            position = proxy_origin + (direction * -100) 
            distance = db.inputs.distance
            # physX query to detect closest hit
            hit = get_physx_scene_query_interface().raycast_closest(position, direction, distance)
            if(hit["hit"]):
                db.outputs.hit_position = (hit['position'][0], hit['position'][1], hit['position'][2])
            else:
                db.outputs.hit_position = (0,0,0)
            db.outputs.execOut = og.ExecutionAttributeState.ENABLED

        except Exception as error:
            # If anything causes your compute to fail report the error and return False
            db.log_error(str(error))
            return False

        # Even if inputs were edge cases like empty arrays, correct outputs mean success
        return True
