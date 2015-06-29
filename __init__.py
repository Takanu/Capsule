
#This states the metadata for the plugin
bl_info = {
    "name": "GEX",
    "author": "Crocadillian/Takanu @ Polarised Games",
    "version": (0,41),
    "blender": (2, 7, 5),
    "api": 39347,
    "location": "3D View > Object Mode > Tools > GEX",
    "description": "Provides tools for batch exporting assets from Blender to game engines.",
    "warning": "Beta",
    "tracker_url": "",
    "category": "Import-Export"
}

# Start importing all the addon files
# The init file just gets things started, no code needs to be placed here.

if "bpy" in locals():
    import imp
    if "definitions" in locals():
        imp.reload(definitions)
    if "properties" in locals():
        imp.reload(properties)
    if "user_interface" in locals():
        imp.reload(user_interface)
    if "operators" in locals():
        imp.reload(operators)
    if "update" in locals():
        imp.reload(update)

import bpy
from . import definitions
from . import properties
from . import user_interface
from . import operators
from . import update


def register():
    bpy.utils.register_module(__name__)


def unregister():
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()
