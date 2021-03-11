
import bpy
from bpy.types import AddonPreferences, PropertyGroup
from bpy.types import UILayout
from bpy.props import (
	IntProperty, 
	FloatProperty, 
	BoolProperty, 
	StringProperty, 
	PointerProperty, 
	CollectionProperty, 
	EnumProperty,
)

from .export_format import CAP_ExportFormat

class CAP_FormatData_USD(PropertyGroup):

    instance_id: IntProperty(default=-1)

    export_hair: BoolProperty(
        name = "Export Hair",
        description = "When enabled, hair will be exported as USD curves.",
        default = False,
    )

    export_uvmaps: BoolProperty(
        name = "Export UVs",
        description = "When enabled, all UV maps of exported meshes are included in the export.",
        default = False,
    )

    export_normals: BoolProperty(
        name = "Export Normals",
        description = "When checked, normals of exported meshes are included in the export.",
        default = False,
    )

    export_materials: BoolProperty(
        name = "Export Materials",
        description = "When enabled, the viewport settings of materials are exported as USD preview materials, and material assignments are exported as geometry subsets.",
        default = False,
    )

    use_instancing: BoolProperty(
        name = "Use Instancing",
        description = "When checked, instanced objects are exported as references in USD. When unchecked, instanced objects are exported as real objects.",
        default = False,
    )

    def export(self, context, export_preset, filePath):
        """
        Calls the USD export operator module to export the currently selected objects.
        """
        #TODO: THIS DOESNT SUPPORT MODIFIER APPLICATION!  AAAA!

        bpy.ops.wm.usd_export(

            # core
            filepath = filePath + ".usd",
            check_existing = False,
            selected_objects_only  = True,
            visible_objects_only = False,
            export_animation = export_preset.export_animation,
            
            # all
            export_hair = self.export_hair,
            export_uvmaps = self.export_uvmaps,
            export_normals = self.export_normals,
            export_materials = self.export_materials,
            use_instancing = self.use_instancing,
        )
    
    def draw_addon_preferences(self, layout, exportData, exp):
        """
        Draws the panel that represents all the options that the export format has.
        """

        filepresets_box = layout.column(align=True)
        filepresets_box.separator()

        export_tabs = filepresets_box.row(align=True)

        export_separator = filepresets_box.column(align=True)

        export_main = filepresets_box.row(align=True)
        export_main.separator()

        export_1 = export_main.column(align=True)
        export_1.separator()
        export_1.prop(exportData, "export_hair")
        export_1.prop(exportData, "export_uvmaps")
        export_1.prop(exportData, "export_normals")
        export_1.prop(exportData, "export_materials")
        export_1.separator()
        export_1.prop(exportData, "use_instancing")

        export_main.separator()

