
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
        description = "When enabled, hair will be exported as USD curves",
        default = False,
    )

    export_uvmaps: BoolProperty(
        name = "Export UVs",
        description = "When enabled, all UV maps of exported meshes are included in the export",
        default = False,
    )

    export_normals: BoolProperty(
        name = "Export Normals",
        description = "When checked, normals of exported meshes are included in the export",
        default = False,
    )

    export_materials: BoolProperty(
        name = "Export Materials",
        description = "When enabled, the viewport settings of materials are exported as USD preview materials, and material assignments are exported as geometry subsets",
        default = False,
    )

    use_instancing: BoolProperty(
        name = "Use Instancing (Experimental)",
        description = "When checked, instanced objects are exported as references in USD. When unchecked, instanced objects are exported as real objects",
        default = False,
    )

    evaluation_mode : EnumProperty(
		name="Evaluation Mode",
		items=(
			('RENDER', "Render", "Use Render settings for object visibility, modifier settings, etc."),
			('VIEWPORT', "Viewport", "Use Viewport settings for object visibility, modifier settings, etc"),
			),
		description="Determines what visibility layer affects the visibility of exported objects, modifier settings and other areas where settings differ between Viewport and Render mode.  (Be careful if you're using Filter by Rendering in General Export Options as it will also modify the objects eligible for export)",
	)

    def export(self, context, export_preset, filePath):
        """
        Calls the USD export operator module to export the currently selected objects.
        """
        #TODO: Turn Filter by Rendering off for USD export, and ask people to use Evaluation Mode instead.
        bpy.ops.wm.usd_export(

            # core
            filepath = filePath,
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

        export_area = filepresets_box.row(align=True)

        # left padding
        export_area.separator()

        # area for revealed export options
        export_options = export_area.column(align=True)
        export_options.use_property_split = True
        export_options.use_property_decorate = False  # removes animation options

        # options.label(text="Export Filters")
        export_options.prop(exportData, "export_hair")
        export_options.prop(exportData, "export_uvmaps")
        export_options.prop(exportData, "export_normals")
        export_options.prop(exportData, "export_materials")
        export_options.separator()
        export_options.separator()

        export_options.prop(exportData, "use_instancing")
        export_options.separator()
        export_options.separator()

        export_options.prop(exportData, "evaluation_mode")
        export_options.separator()

        # left padding
        export_area.separator()

