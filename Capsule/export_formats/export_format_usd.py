
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

    # ////////////////////////////////
    # FILE

    use_instancing: BoolProperty(
        name = "Use Instancing (Experimental)",
        description = "When checked, instanced objects are exported as references in USD. When unchecked, instanced objects are exported as real objects",
        default = False,
    )

    evaluation_mode : EnumProperty(
		name = "Evaluation Mode",
		items =  (
			('RENDER', "Render (Default)", "Use Render settings for object visibility, modifier settings, etc."),
			('VIEWPORT', "Viewport", "Use Viewport settings for object visibility, modifier settings, etc"),
			),
		description = "Determines what visibility layer affects the visibility of exported objects, modifier settings and other areas where settings differ between Viewport and Render mode.  (Be careful if you're using Filter by Rendering in General Export Options, as objects that are hidden from the Render will not export",
    )


    # ////////////////////////////////
    # SCENE
    
    export_hair: BoolProperty(
        name = "Export Hair",
        description = "When enabled, hair will be exported as USD curves",
        default = False,
    )


    # ////////////////////////////////
    # MESH

    export_uvmaps: BoolProperty(
        name = "Export UVs",
        description = "When enabled, all UV maps of exported meshes are included in the export",
        default = True,
    )

    export_normals: BoolProperty(
        name = "Export Normals",
        description = "When checked, normals of exported meshes are included in the export",
        default = True,
    )

    # ////////

    export_materials: BoolProperty(
        name = "Export Materials",
        description = "When enabled, the viewport settings of materials are exported as USD preview materials, and material assignments are exported as geometry subsets",
        default = True,
    )

    generate_preview_surface: BoolProperty(
        name = "Generate USD Preview Surface",
        description = "When enabled, an approximate USD Preview Surface shader representation of a Principled BSDF node network will be generated",
        default = True,
    )

    export_textures: BoolProperty(
        name = "Export Textures",
        description = "If exporting materials, export textures referenced by material nodes to a ‘textures’ directory in the same directory as the USD file",
        default = True,
    )

    relative_texture_paths: BoolProperty(
        name = "Use Relative Texture Paths",
        description = "Make texture asset paths relative to the USD file",
        default = True,
    )

    

    def export(self, context, export_preset, filePath):
        """
        Calls the USD export operator module to export the currently selected objects.
        """

        bpy.ops.wm.usd_export(

            # CAPSULE
            filepath = filePath + ".usdc",
            check_existing = False,
            selected_objects_only  = True,
            visible_objects_only = False,
            export_animation = export_preset.export_animation,

            # FILE
            use_instancing = self.use_instancing,
            evaluation_mode = self.evaluation_mode,
            

            # SCENE
            export_hair = self.export_hair,


            # MESH
            export_uvmaps = self.export_uvmaps,
            export_normals = self.export_normals,
            
            export_materials = self.export_materials,
            generate_preview_surface = self.generate_preview_surface,
            export_textures = self.export_textures,
            overwrite_textures = True,  # Capsule assumes this behaviour everywhere, assume it here too.
            relative_texture_paths = self.relative_texture_paths,
            

        )
    
    def draw_addon_preferences(self, layout, exportData, cap_file):
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

        # options.label(text= "Export Filters")
        data_options = export_options.column(align = True, heading = "Scene Data")
        data_options.prop(exportData, "export_hair")
        data_options.prop(exportData, "export_uvmaps")
        data_options.prop(exportData, "export_normals")
        data_options.separator()
        data_options.separator()

        material_options = export_options.column(align = True, heading = "Materials")
        material_options.prop(exportData, "export_materials")

        material_sub = export_options.column(align = True)
        material_sub.active = exportData.export_materials
        material_sub.prop(exportData, "generate_preview_surface")
        material_sub.prop(exportData, "export_textures")
        material_sub.prop(exportData, "relative_texture_paths")
        material_sub.separator()
        material_sub.separator()

        eval_options = export_options.column(align = True)
        eval_options.prop(exportData, "evaluation_mode", text= "Use Settings For")
        eval_options.separator()
        eval_options.separator()

        file_options = export_options.column(align = True)
        file_options.prop(exportData, "use_instancing")
        file_options.separator()

        # left padding
        export_area.separator()

