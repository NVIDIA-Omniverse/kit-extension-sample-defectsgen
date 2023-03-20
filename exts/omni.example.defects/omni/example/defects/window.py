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

import carb
import omni.ui as ui
from functools import partial
from omni.ui import DockPreference
from .style import *
from .widgets import CustomDirectory
from .replicator_defect import create_defect_layer, rep_preview, does_defect_layer_exist, rep_run, get_defect_layer
from .rep_widgets import DefectParameters, ObjectParameters
from .utils import *

class DefectsWindow(ui.Window):
    def __init__(self, title: str, dockPreference: DockPreference = DockPreference.DISABLED, **kwargs) -> None:
        super().__init__(title, dockPreference, **kwargs)
        # Models
        self.frames = ui.SimpleIntModel(1, min=1)
        self.rt_subframes = ui.SimpleIntModel(1, min=1)
        # Widgets
        self.defect_params = None
        self.object_params = None
        self.output_dir = None

        self.frame.set_build_fn(self._build_frame)

    def _build_collapse_base(self, label: str, collapsed: bool = False):
        v_stack = None
        with ui.CollapsableFrame(label, height=0, collapsed=collapsed):
            with ui.ZStack():
                ui.Rectangle()
                v_stack = ui.VStack()
        return v_stack

    def _build_frame(self):
        with self.frame:
            with ui.ScrollingFrame(style=default_defect_main):
                with ui.VStack(style={"margin": 3}):
                    self._build_object_param()               
                    self._build_defect_param()
                    self._build_replicator_param()

    def _build_object_param(self):
        with self._build_collapse_base("Object Parameters"):
            self.object_params = ObjectParameters()

    def _build_defect_param(self):    
        with self._build_collapse_base("Defect Parameters"):
            self.defect_params = DefectParameters()
    
    def _build_replicator_param(self):
        def preview_data():
            if does_defect_layer_exist():
                rep_preview()
            else:
                create_defect_layer(self.defect_params, self.object_params)
                self.rep_layer_button.text = "Recreate Replicator Graph"
        
        def run_replicator():
            total_frames = self.frames.get_value_as_int()
            if total_frames > 0:
                create_defect_layer(self.defect_params, self.object_params, total_frames, self.output_dir.directory)
                self.rep_layer_button.text = "Recreate Replicator Graph"
                rep_run()
            else:
                carb.log_error(f"Number of frames is {total_frames}. Input value needs to be greater than 0.")
        
        def create_replicator_graph():
            if get_defect_layer() is not None:
                layer, pos = get_defect_layer()
                omni.kit.commands.execute('RemoveSublayer',
                    layer_identifier=layer.identifier,
                    sublayer_position=pos)
            if is_valid_prim('/Replicator'):
                delete_prim('/Replicator')
            create_defect_layer(self.defect_params, self.object_params)
            self.rep_layer_button.text = "Recreate Replicator Graph"

        def set_text(label, model):
            label.text = model.as_string

        with self._build_collapse_base("Replicator Parameters"):
            self.output_dir = CustomDirectory("Output Directory", tooltip="Directory to specify where the output files will be stored. Default is [DRIVE/Users/USER/omni.replicator_out]")
            with ui.HStack(height=0):
                ui.Label("Render Subframe Count: ", width=0,
                         tooltip="Defines how many subframes of rendering occur before going to the next frame")
                ui.Spacer(width=ui.Fraction(0.25))
                ui.IntField(model=self.rt_subframes)
            self.rep_layer_button = ui.Button("Create Replicator Layer", 
                                              clicked_fn=lambda: create_replicator_graph(), 
                                              tooltip="Creates/Recreates the Replicator Graph, based on the current Defect Parameters")
            with ui.HStack(height=0):
                ui.Button("Preview", width=0, clicked_fn=lambda: preview_data(),
                          tooltip="Preview a Replicator Scene")
                ui.Label("or", width=0)
                ui.Button("Run for", width=0, clicked_fn=lambda: run_replicator(),
                          tooltip="Run replicator for so many frames")
            
                with ui.ZStack(width=0):
                    l = ui.Label("", style={"color": ui.color.transparent, "margin_width": 10})
                    self.frame_change = ui.StringField(model=self.frames)
                    self.frame_change_cb = self.frame_change.model.add_value_changed_fn(lambda m, l=l: set_text(l, m))
                ui.Label("frame(s)")

    def destroy(self) -> None:
        self.frames = None
        self.defect_semantic = None
        if self.frame_change is not None:
            self.frame_change.model.remove_value_changed_fn(self.frame_change_cb)
        if self.defect_params is not None:
            self.defect_params.destroy()
            self.defect_params = None
        if self.object_params is not None:
            self.object_params.destroy()
            self.object_params = None
        return super().destroy()
