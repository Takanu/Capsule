
#This states the metadata for the plugin
bl_info = {
    "name": "GEX",
    "author": "Crocadillian/Takanu @ Polarised Games",
    "version": (0,85),
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
    print("Reloading Plugin"*20)
    if "definitions" in locals():
        imp.reload(definitions)
    if "properties" in locals():
        imp.reload(properties)
    if "user_interface" in locals():
        imp.reload(user_interface)
    if "export_operators" in locals():
        imp.reload(export_operators)
    if "ui_operators" in locals():
        imp.reload(ui_operators)
    if "update" in locals():
        imp.reload(update)


print("Beginning Import"*20)

import bpy
from . import definitions
from . import properties
from . import user_interface
from . import export_operators
from . import ui_operators
from . import update
from bpy.props import IntProperty, BoolProperty, StringProperty, PointerProperty, CollectionProperty
from bpy.types import AddonPreferences, PropertyGroup

print("End of import")

class ExportPass(PropertyGroup):

    name = StringProperty(
        name="Pass Name",
        description="The name of the selected pass."
    )

    file_suffix = StringProperty(
        name="File Suffix",
        description="The suffix added on the exported file created from this pass."
    )

    sub_directory = StringProperty(
        name="Sub-Directory",
        description="Export the pass to a new folder inside the chosen location default."
    )

    # Sub-directory?

    export_lp = BoolProperty(
        name="Export Low_Poly",
        description="Selects all low-poly objects available for export.",
        default=False
    )

    export_hp = BoolProperty(
        name="Export High_Poly",
        description="Selects all high-poly objects available for export.",
        default=False
    )

    export_cg = BoolProperty(
        name="Export Cage",
        description="Selects all cage objects available for export.",
        default=False
    )

    export_cx = BoolProperty(
        name="Export Collision",
        description="Selects all collision objects available for export.",
        default=False
    )

    export_ar = BoolProperty(
        name="Export Armature",
        description="Selects all armature objects available for export.",
        default=False
    )

    export_am = BoolProperty(
        name="Export Animation",
        description="Selects all animation objects available for export.",
        default=False
    )

    export_individual = BoolProperty(
        name="Export Individual",
        description="Exports every object in the pass as an individual object.",
        default=False
    )

    apply_modifiers = BoolProperty(
        name="Apply Modifiers",
        description="Applies all modifiers on every object in the pass",
        default=False
    )

    triangulate = BoolProperty(
        name="Triangulate Export",
        description="Triangulate objects in the pass on export using optimal triangulation settings.",
        default=False
    )


class ExportDefault(PropertyGroup):
    name = StringProperty(
        name = "Default Name",
        description="The name of the export default, whoda thunk :OO",
        default=""
    )

    passes = CollectionProperty(type=ExportPass)
    passes_index = IntProperty(default=0)

class GEXAddonPreferences(AddonPreferences):
    bl_idname = __name__

    export_defaults = CollectionProperty(type=ExportDefault)
    export_defaults_index = IntProperty(default=0)

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
    bpy.utils.register_class(ExportPass)
    bpy.utils.register_class(ExportDefault)
    bpy.utils.register_module(__name__)


def unregister():
    bpy.utils.unregister_class(GEXAddonPreferences)
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()
