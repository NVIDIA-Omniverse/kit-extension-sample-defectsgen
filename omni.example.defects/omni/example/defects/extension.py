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

import omni.ext
from .window import DefectsWindow

class DefectsGenerator(omni.ext.IExt):
    WINDOW_NAME = "Defects Sample Extension"
    MENU_PATH = f"Window/{WINDOW_NAME}"

    def __init__(self) -> None:
        super().__init__()
        self._window = None

    def on_startup(self, ext_id):
        self._menu = omni.kit.ui.get_editor_menu().add_item(
            DefectsGenerator.MENU_PATH, self.show_window, toggle=True, value=True
        )
        self.show_window(None, True)
    
    def on_shutdown(self):
        if self._menu:
            omni.kit.ui.get_editor_menu().remove_item(DefectsGenerator.MENU_PATH)
            self._menu
        if self._window:
            self._window.destroy()
            self._window = None

    def _set_menu(self, value):
        omni.kit.ui.get_editor_menu().set_value(DefectsGenerator.MENU_PATH, value)

    def _visibility_changed_fn(self, visible):
        self._set_menu(visible)
        if not visible:
            self._window = None

    def show_window(self, menu, value):
        self._set_menu(value)
        if value:
            self._set_menu(True)
            self._window = DefectsWindow(DefectsGenerator.WINDOW_NAME, width=450, height=700)
            self._window.set_visibility_changed_fn(self._visibility_changed_fn)
        elif self._window:
            self._window.visible = False

