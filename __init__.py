
#This states the metadata for the plugin
bl_info = {
    "name": "GEX",
    "author": "Crocadillian/Takanu @ Polarised Games",
    "version": (0,72),
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
from bpy.props import IntProperty, BoolProperty, StringProperty
from bpy.types import AddonPreferences

class GEXAddonPreferences(AddonPreferences):
    bl_idname = __name__

    test_prop = IntProperty(
    name = "TESTPROP",
    default = 6
    )

    lp_tag = StringProperty(
    name = "Low-Poly Tag",
    description = "Defines the object name suffix name for low-poly objects when using Auto-Assign mode. ",
    default = "_LP"
    )

    hp_tag = StringProperty(
    name = "High-Poly Tag",
    description = "Defines the object name suffix name for high-poly objects when using Auto-Assign mode. ",
    default = "_HP"
    )

    cg_tag = StringProperty(
    name = "Cage Tag",
    description = "Defines the object name suffix name for cage objects when using Auto-Assign mode. ",
    default = "_CG"
    )

    cx_tag = StringProperty(
    name = "Collision Tag",
    description = "Defines the object name suffix name for collision objects when using Auto-Assign mode. ",
    default = "_CX"
    )

    def draw(self, context):
        layout = self.layout

        row = layout.row(align=True)
        row.prop(self, "lp_tag")
        row.separator()
        row.prop(self, "hp_tag")

        row = layout.row(align=True)
        row.prop(self, "cg_tag")
        row.separator()
        row.prop(self, "cx_tag")



def register():
    bpy.utils.register_class(GEXAddonPreferences)
    bpy.utils.register_module(__name__)


def unregister():
    bpy.utils.unregister_class(GEXAddonPreferences)
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()
