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
import omni.physx
import omni.replicator.core as rep
import carb
import omni.graph.core as og
from .rep_widgets import DefectParameters, ObjectParameters
import omni.usd
from .utils import *
from pxr import Sdf

keys = og.Controller.Keys

decal_texture_primvar = "/World/proxy/Looks/PsuedoDecal/texture_2d_const_02"
proxy = "/World/proxy/DecalProxy"
transparent_mat_path = '/World/proxy/Looks/Transparent'
camera_path = "/World/Camera"

def create_transparent_mat(cube_path):
    # Check if Material exists
    if is_valid_prim(transparent_mat_path) is not None:
        delete_prim(transparent_mat_path)
    # Create OmniPBR material
    omni.kit.commands.execute('CreateMdlMaterialPrim',
        mtl_url='OmniPBR.mdl',
        mtl_name='OmniPBR',
        mtl_path=transparent_mat_path)
    mat = get_prim(transparent_mat_path + '/Shader')
    # Create and Set Attributes
    mat.CreateAttribute('inputs:enable_opacity', Sdf.ValueTypeNames.Bool)
    mat.CreateAttribute('inputs:opacity_constant', Sdf.ValueTypeNames.Float)
    set_prim_attr(transparent_mat_path + '/Shader', 'inputs:enable_opacity', True)
    set_prim_attr(transparent_mat_path + '/Shader', 'inputs:opacity_constant', 0)

    omni.kit.commands.execute('BindMaterial',
        material_path=transparent_mat_path,
        prim_path=[cube_path],
        strength=['weakerThanDescendants'])

def create_semantic_cube(semantic_label: str = ""):
    cube = rep.create.cube(semantics=[('class', semantic_label)], 
        position=get_prim_attr(proxy, 'xformOp:translate'), 
        scale=get_prim_attr(proxy, 'xformOp:scale'), 
        rotation=get_prim_attr(proxy, 'xformOp:rotateXYZ'),
    )
    return cube.node.get_attribute('inputs:prims').get().get_prim_path()

def hide_proxy(to_hide: bool):
    if to_hide:
        set_prim_attr(proxy, 'visibility', 'invisible')
    else:
        set_prim_attr(proxy, 'visibility', 'inherited')

def startup():
    hide_proxy(True)
    start_timeline()

def rep_preview():
    startup()
    rep.orchestrator.preview()

def rep_run():
    startup()
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

# HACK: Functionality will be removed once rep.utils.sequential() gets a new update
def stitch_nodes(decal_trans_node, prim_vars_node, raycast_node, semanticbox_node, trigger_node):
    trigger_execOut = trigger_node.get_attribute('outputs:execOut')
    # 
    scatter_node = decal_trans_node.get_attribute('outputs:execOut').get_downstream_connections()[0].get_node()
    get_target_prim_node = scatter_node.get_attribute('inputs:surfacePrim').get_upstream_connections()[0].get_node()
    get_prim_proxy_node = scatter_node.get_attribute('inputs:execIn').get_upstream_connections()[0].get_node()
    og.Controller.disconnect(trigger_execOut, get_target_prim_node.get_attribute('inputs:execIn'), True)
    og.Controller.disconnect(get_prim_proxy_node.get_attribute('outputs:execOut'), scatter_node.get_attribute('inputs:execIn'), True)
    
    write_node = get_prim_proxy_node.get_attribute('outputs:execOut').get_downstream_connections()[0].get_node()
    og.Controller.disconnect(get_prim_proxy_node.get_attribute('outputs:execOut'), write_node.get_attribute('inputs:exec'),True)
    og.Controller.connect(get_prim_proxy_node.get_attribute('outputs:execOut'), get_target_prim_node.get_attribute('inputs:execIn'), True)
    og.Controller.connect(get_target_prim_node.get_attribute('outputs:execOut'), scatter_node.get_attribute('inputs:execIn'), True)
    og.Controller.connect(scatter_node.get_attribute('outputs:execOut'), write_node.get_attribute('inputs:exec'), True)

    # Get to the end execution of translating the proxy
    current_node = write_node.get_attribute('outputs:exec').get_downstream_connections()[0].get_node()
    while len(current_node.get_attribute('outputs:execOut').get_downstream_connections()) > 0:
        current_node = current_node.get_attribute('outputs:execOut').get_downstream_connections()[0].get_node()
    
    # Grab execution attributes
    prim_execIn = prim_vars_node.get_attribute('inputs:execIn')
    raycast_execIn = raycast_node.get_attribute('inputs:execIn')
    semanticbox_execIn = semanticbox_node.get_attribute('inputs:execIn')

    # Unhook the execution for the other nodes
    og.Controller.disconnect(trigger_execOut, prim_execIn, True)
    og.Controller.disconnect(trigger_execOut, raycast_execIn, True)
    og.Controller.disconnect(trigger_execOut, semanticbox_execIn, True)

    # Reconnect execution to the end of decal translation
    og.Controller.connect(current_node.get_attribute('outputs:execOut'), prim_execIn, True)
    og.Controller.connect(prim_vars_node.get_attribute('outputs:execOut'), raycast_execIn, True)
    og.Controller.connect(raycast_node.get_attribute('outputs:execOut'), semanticbox_execIn, True)

    # Connect raycast node
    og.Controller.connect(raycast_node.get_attribute('outputs:hit_position'), semanticbox_node.get_attribute('inputs:position'))

def create_randomizers(defect_params: DefectParameters, object_params: ObjectParameters):
    textures=get_textures(defect_params.defect_text.directory)
    def change_decal():
        material = rep.get.prims(path_pattern = decal_texture_primvar)
        with material:
            rep.modify.attribute("inputs:tex", rep.distribution.choice(textures))
        return material.node

    def translate_decal():
        prox = rep.get.prims(path_pattern = proxy)
        surface_path = object_params.target_prim.path_value
        if is_valid_prim(defect_params.define_region.path_value):
            surface_path = defect_params.define_region.path_value
            region = get_prim(surface_path)
            region.GetAttribute('visibility').Set('invisible')
        surface = rep.get.prims(path_pattern=surface_path)
        proxy_rotation = get_prim_attr(proxy, 'xformOp:rotateXYZ')
        with prox:
            rep.randomizer.scatter_2d(surface)
            rep.modify.pose(
                rotation=rep.distribution.uniform(
                    (defect_params.rot.min_value, proxy_rotation[1], proxy_rotation[2]), 
                    (defect_params.rot.max_value, proxy_rotation[1], proxy_rotation[2])),
                scale=rep.distribution.uniform(
                    (1, defect_params.dim_h.min_value,defect_params.dim_w.min_value),
                    (1, defect_params.dim_h.max_value, defect_params.dim_w.max_value)
                )
            )

        return prox.node

    rep.randomizer.register(change_decal)
    rep.randomizer.register(translate_decal)

def create_custom_nodes():
    def write_prim_vars(proxy_path: str = "", target_path: str = ""):
        node = rep.utils.create_node("omni.example.defects.WritePrimVars", proxy_path=proxy_path, target_path=target_path)
        return node

    rep.modify.register(write_prim_vars)

    def raycast_from_proxy(distance: float = 0, prim_path: str = ""):
        node = rep.utils.create_node("omni.example.defects.GetPosFromRaycast", distance=distance, prim_path=prim_path)
        return node
    
    rep.modify.register(raycast_from_proxy)

    def write_to_semanticbox(position=(0,0,0), proxy_path: str = "", prim_path: str = ""):
        node = rep.utils.create_node("omni.example.defects.SetSemanticBoxTransform", position=position, proxy_path=proxy_path, prim_path=prim_path)
        return node
    
    rep.modify.register(write_to_semanticbox)

def create_camera(target_path):
    if not is_valid_prim(camera_path):
        camera = rep.create.camera(position=1000, look_at=rep.get.prim_at_path(target_path))
    else:
        camera = rep.get.prim_at_path(camera_path)
    return camera

def create_defect_layer(defect_params: DefectParameters, object_params: ObjectParameters, frames: int = 1, output_dir: str = "_defects", rt_subframes: int = 0):
    if len(defect_params.defect_text.directory) <= 0:
        carb.log_error("No directory selected")
        return
    
    if is_valid_prim(defect_params.define_region.path_value):
        realign_prim_to_target(target_path=defect_params.define_region.path_value, prim_path=proxy)
        look_at(target_path=defect_params.define_region.path_value, prim_path=proxy)
    with rep.new_layer("Defect"):
        trigger = rep.trigger.on_frame(num_frames=frames, rt_subframes=rt_subframes)

        create_custom_nodes()
        create_randomizers(defect_params=defect_params, object_params=object_params)        
        
        camera = create_camera(object_params.target_prim.path_value)
        render_product = rep.create.render_product(camera, (512,512))
        basic_writer = rep.WriterRegistry.get("BasicWriter")
        basic_writer.initialize(output_dir=output_dir, rgb=True, bounding_box_2d_loose=True)
        # Attach render_product to the writer
        basic_writer.attach([render_product])

        cube_path = create_semantic_cube(defect_params.semantic_label.get_value_as_string())
        create_transparent_mat(cube_path)

        # Setup randomization
        with trigger:
            rep.randomizer.change_decal()
            decal_trans = rep.randomizer.translate_decal()
            prim_vars = rep.modify.write_prim_vars(proxy_path=proxy, target_path=object_params.target_prim.path_value)
            raycast = rep.modify.raycast_from_proxy(distance=1000, prim_path=proxy)
            semantic_box = rep.modify.write_to_semanticbox(proxy_path=proxy, prim_path=cube_path)

        stitch_nodes(decal_trans.node, prim_vars.node, raycast.node, semantic_box.node, trigger.node)