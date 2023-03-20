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
This is the implementation of the OGN node defined in OgnSetSemanticBoxTransform.ogn
"""

# Array or tuple values are accessed as numpy arrays so you probably need this import
import numpy
import omni.usd
import carb
from pxr import Gf


class OgnSetSemanticBoxTransform:

    """
    Attribute Value Properties:
    Inputs:
        inputs.execIn
        inputs.position
        inputs.proxy_path
        inputs.prim_path
    Outputs:
        outputs.execOut
    """

    """
         Takes in a position, rotation, and scale values to effect a semantic cube in the
     scene
    """
    @staticmethod
    def compute(db) -> bool:
        """Compute the outputs from the current input"""

        try:
            stage = omni.usd.get_context().get_stage()
            prim = stage.GetPrimAtPath(db.inputs.prim_path)
            proxy_prim = stage.GetPrimAtPath(db.inputs.proxy_path)
            pos = Gf.Vec3d(db.inputs.position.tolist())
            prim.GetAttribute("xformOp:translate").Set(pos)
            prim.GetAttribute("xformOp:rotateXYZ").Set(proxy_prim.GetAttribute('xformOp:rotateXYZ').Get())
            prim.GetAttribute("xformOp:scale").Set(proxy_prim.GetAttribute('xformOp:scale').Get())
            # With the compute in a try block you can fail the compute by raising an exception
        except Exception as error:
            # If anything causes your compute to fail report the error and return False
            db.log_error(str(error))
            return False

        # Even if inputs were edge cases like empty arrays, correct outputs mean success
        return True
