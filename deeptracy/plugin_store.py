# Copyright 2017 BBVA
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import logging
from typing import List, Union
from pluginbase import PluginBase
import deeptracy.config as config
from deeptracy_core.dal.plugin.manager import deactivate_all_plugins, add_or_activate_plugin
from deeptracy_core.dal.database import db

log = logging.getLogger(__name__)

class deeptracy_plugin(object):
    def __init__(self, lang: Union[str, List[str]]):
        if not hasattr(lang, "append"):
            self.lang = [lang]
        else:
            self.lang = lang

    def __call__(self, f):
        f.deeptracy_plugin_enable = True
        f.deeptracy_plugin_lang = self.lang

        return f


class DeeptracyPluginStore:

    _plugins = {}
    _manager = None

    def get_all_plugin_paths(self):
        default_path = config.PLUGINS_LOCATION  # os.path.join(os.path.dirname(__file__), '..', 'plugins')
        return [os.path.join(default_path, o) for o in os.listdir(default_path)
                if os.path.isdir(os.path.join(default_path, o))]

    def load_plugins(self):
        session = db.Session()
        deactivate_all_plugins(session)
        session.commit()

        default_paths = self.get_all_plugin_paths()

        # Load plugins from directories
        plugin_base = PluginBase(package="deeptracy.plugins")
        plugin_manager = plugin_base.make_plugin_source(searchpath=default_paths)

        # Locate plugins
        plugins_found = {}

        for module in plugin_manager.list_plugins():

            if module == 'store':
                continue

            module_objects = plugin_manager.load_plugin(module)

            for plugin_name, plugin_obj in vars(module_objects).items():
                if plugin_name.startswith("_") or type(plugin_obj).__name__ != "function":
                    continue

                if hasattr(plugin_obj, "deeptracy_plugin_enable") and hasattr(plugin_obj, "deeptracy_plugin_lang"):
                    for lang in plugin_obj.deeptracy_plugin_lang:
                        plugin = add_or_activate_plugin(plugin_name, lang, session)
                        session.commit()
                        plugins_found[plugin.id] = {
                            'module': module,
                            'func_name': plugin_name
                        }

                    session.commit()

        session.close()

        log.info('[Plugins]')
        log.info(plugins_found)

        self._plugins = plugins_found
        self._manager = plugin_manager

    def get_plugin(self, plugin_id: str):
        plugin = self._plugins[plugin_id]
        plugin_executor = None

        if plugin is not None:
            plugin_executor = vars(self._manager.load_plugin(plugin.get('module')))[plugin.get('func_name')]

        return plugin_executor


plugin_store = DeeptracyPluginStore()
