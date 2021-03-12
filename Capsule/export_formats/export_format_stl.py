
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

class CAP_FormatData_STL(PropertyGroup):

    instance_id: IntProperty(default=-1)

    global_scale: FloatProperty(
        name = "Global Scale",
        description = "Scale multiplayer for the objects to be exported.",
        default = 1.0,
        soft_min = 0.1,
        soft_max = 100,
        step = 0.1,
        min = 0.01,
        max = 1000,
    )

    use_scene_unit: BoolProperty(
        name = "Use Scene Units",
        description = "Applies the current scene's unit (as defined by unit scale) to exported data.",
        default = False,
    )

    save_as_ascii: BoolProperty(
        name = "Save as ASCII",
        description = "Save the file in an ASCII file format.",
        default = False,
    )
    
    axis_up: EnumProperty(
		name="Axis Up",
		description="What the Up Axis will be defined as when the model is exported.",
		items=(
			('X', 'X', ''),
			('Y', 'Y', ''),
			('Z', 'Z', ''),
			('-X', '-X', ''),
			('-Y', '-Y', ''),
			('-Z', '-Z', '')),
		default='Y',
	)

    axis_forward: EnumProperty(
        name="Axis Forward",
        description="What the Forward Axis will be defined as when the model is exported.",
        items=(
            ('X', 'X', ''),
            ('Y', 'Y', ''),
            ('Z', 'Z', ''),
            ('-X', '-X', ''),
            ('-Y', '-Y', ''),
            ('-Z', '-Z', '')),
        default='Z'
        )
    
    def export(self, context, export_preset, filePath):
        """
        Calls the Alembic export operator module to export the currently selected objects.
        """

        bpy.ops.export_mesh.stl(

            # core
            filepath = filePath + ".stl",
            check_existing = False,
            use_selection = True,

            use_mesh_modifiers = export_preset.apply_modifiers,

            # all
            global_scale = self.global_scale,
            use_scene_unit = self.use_scene_unit,
            use_ascii = self.save_as_ascii,
            axis_forward = self.axis_forward,
            axis_up = self.axis_up
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

        export_options.separator()
        export_options.prop(exportData, "save_as_ascii")
        export_options.prop(exportData, "use_scene_unit")
        export_options.separator()

        export_options.prop(exportData, "axis_up")
        export_options.prop(exportData, "axis_forward")
        export_options.separator()
        export_options.prop(exportData, "global_scale")
        export_options.separator()

        # right padding
        export_area.separator()

