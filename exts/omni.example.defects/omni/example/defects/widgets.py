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
from omni.kit.window.file_importer import get_file_importer
from typing import List
import carb
import omni.usd

class CustomDirectory:
    def __init__(self, label: str, tooltip: str = "", default_dir: str = "", file_types: List[str] = None) -> None:
        self._label_text = label
        self._tooltip = tooltip
        self._file_types = file_types
        self._dir = ui.SimpleStringModel(default_dir)
        self._build_directory()

    @property
    def directory(self) -> str:
        """
        Selected Directory name from file importer

        :type: str
        """
        return self._dir.get_value_as_string()

    def _build_directory(self):
        with ui.HStack(height=0, tooltip=self._tooltip):
            ui.Label(self._label_text)
            ui.StringField(model=self._dir)
            ui.Button("Open", width=0, style={"padding": 5}, clicked_fn=self._pick_directory)

    def _pick_directory(self):
        file_importer = get_file_importer()
        if not file_importer:
            carb.log_warning("Unable to get file importer")
        file_importer.show_window(title="Select Folder", 
                                  import_button_label="Import Directory", 
                                  import_handler=self.import_handler, 
                                  file_extension_types=self._file_types
                                  )


    def import_handler(self, filename: str, dirname: str, selections: List[str] = []):
        self._dir.set_value(dirname)

    def destroy(self):
        self._dir = None

class MinMaxWidget:
    def __init__(self, label: str, min_value: float = 0, max_value: float = 1, tooltip: str = "") -> None:
        self._min_model = ui.SimpleFloatModel(min_value)
        self._max_model = ui.SimpleFloatModel(max_value)
        self._label_text = label
        self._tooltip = tooltip
        self._build_min_max()

    @property
    def min_value(self) -> float:
        """
        Min Value of the UI

        :type: int
        """
        return self._min_model.get_value_as_float()
    
    @property 
    def max_value(self) -> float:
        """
        Max Value of the UI

        :type: int
        """
        return self._max_model.get_value_as_float()

    def _build_min_max(self):
        with ui.HStack(height=0, tooltip=self._tooltip):
            ui.Label(self._label_text)
            with ui.HStack():
                ui.Label("Min", width=0)
                ui.FloatDrag(model=self._min_model)
                ui.Label("Max", width=0)
                ui.FloatDrag(model=self._max_model)

    def destroy(self):
        self._max_model = None
        self._min_model = None

class PathWidget:
    def __init__(self, label: str, button_label: str = "Copy", read_only: bool = False, tooltip: str = "") -> None:
        self._label_text = label
        self._tooltip = tooltip
        self._button_label = button_label
        self._read_only = read_only
        self._path_model = ui.SimpleStringModel()
        self._top_stack = ui.HStack(height=0, tooltip=self._tooltip)
        self._button = None
        self._build()
    
    @property
    def path_value(self) -> str:
        """
        Path of the Prim in the scene

        :type: str
        """
        return self._path_model.get_value_as_string()
    
    @path_value.setter
    def path_value(self, value) -> None:
        """
        Sets the path value

        :type: str
        """
        self._path_model.set_value(value)

    def _build(self):
        def copy():
            ctx = omni.usd.get_context()
            selection = ctx.get_selection().get_selected_prim_paths()
            if len(selection) > 0:
                self._path_model.set_value(str(selection[0]))

        with self._top_stack:
            ui.Label(self._label_text)
            ui.StringField(model=self._path_model, read_only=self._read_only)
            self._button = ui.Button(self._button_label, width=0, style={"padding": 5}, clicked_fn=lambda: copy(), tooltip="Copies the Current Selected Path in the Stage")

    def destroy(self):
        self._path_model = None


