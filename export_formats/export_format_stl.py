
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

    # the property for 'use_ascii'
    save_as_ascii: BoolProperty(
        name = "Save as ASCII",
        description = "Save the file in an ASCII file format.",
        default = False,
    )

    use_batch: BoolProperty(
        name = "Batch Individually",
        description = "Exports each object to a separate file.",
        default = False,
    )


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

    # the property for 'axis_forward'
    forward_axis: EnumProperty(
        name = "Forward Axis",
        description = "What the Forward Axis will be defined as when the model is exported.",
        items = (
            ('X', 'X', ''),
            ('Y', 'Y (Default)', ''),
            ('Z', 'Z', ''),
            ('-X', '-X', ''),
            ('-Y', '-Y', ''),
            ('-Z', '-Z', '')),
        default = 'Y',
    )
    
    # the property for 'axis_up'
    up_axis: EnumProperty(
		name = "Up Axis",
		description = "What the Up Axis will be defined as when the model is exported.",
		items = (
			('X', 'X', ''),
			('Y', 'Y', ''),
			('Z', 'Z (Default)', ''),
			('-X', '-X', ''),
			('-Y', '-Y', ''),
			('-Z', '-Z', '')),
		default = 'Z',
	)

    
    
    def export(self, context, export_preset, filePath):
        """
        Calls the Alembic export operator module to export the currently selected objects.
        """

        bpy.ops.wm.stl_export(

            # core
            filepath = filePath + ".stl",
            check_existing = False,
            export_selected_objects  = True,
            

            apply_modifiers = export_preset.apply_modifiers,

            # all
            ascii_format  = self.save_as_ascii,
            use_batch = self.use_batch,
            global_scale = self.global_scale,
            use_scene_unit = self.use_scene_unit,
            forward_axis = self.forward_axis,
            up_axis = self.up_axis
        )

    
    def draw_addon_preferences(self, layout, exportData, cap_file, preset):
        """
        Draws the panel that represents all the options that the export format has.
        """

        filepresets_box = layout.column(align= True)
        filepresets_box.separator()

        export_area = filepresets_box.row(align= True)

        # left padding
        export_area.separator()

        # area for revealed export options
        export_options = export_area.column(align= True)
        export_options.use_property_split = True
        export_options.use_property_decorate = False  # removes animation options

        if preset.export_animation == True:
            export_options_warning = export_options.box()
            export_options_warning_l = export_options_warning.row(align= True)
            export_options_warning_l.label(text= "STL doesn't support animations, 'Export Animation' will be ignored.")
            export_options.separator()
            export_options.separator()

        export_options.separator()
        export_options.prop(exportData, "save_as_ascii")
        export_options.prop(exportData, "use_batch")
        export_options.separator()
        export_options.prop(exportData, "use_scene_unit")
        export_options.separator()

        export_options.prop(exportData, "global_scale")
        export_options.separator()
        export_options.separator()
        export_options.prop(exportData, "forward_axis")
        export_options.prop(exportData, "up_axis")
        export_options.separator()

        # right padding
        export_area.separator()

