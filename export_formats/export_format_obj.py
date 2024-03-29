
import bpy
from bpy.props import IntProperty, FloatProperty, BoolProperty, StringProperty, PointerProperty, CollectionProperty, EnumProperty
from bpy.types import AddonPreferences, PropertyGroup
from bpy.types import UILayout

from .export_format import CAP_ExportFormat

class CAP_FormatData_OBJ(PropertyGroup):

	instance_id = IntProperty(default=-1)


	# file / grouping

	export_object_groups: BoolProperty(
		name = "Export Object Groups",
		description = "Append mesh name to object name, separated by a ‘_’",
		default = False,
	)

	export_material_groups: BoolProperty(
		name = "Export Material Groups",
		description = " Append mesh name and material name to object name, separated by a ‘_’",
		default = False,
	)

	export_vertex_groups: BoolProperty(
		name = "Export Vertex Groups",
		description = "Export the name of the vertex group of a face. It is approximated by choosing the vertex group with the most members among the vertices of a face",
		default = False,
	)

	export_smooth_groups: BoolProperty(
		name = "Export Smoothing Groups",
		description = "Every smooth-shaded face is assigned group “1” and every flat-shaded face “off”",
		default = False,
	)

	smooth_group_bitflags: BoolProperty(
		name = "Generate Bitflags for Smooth Groups",
		description = "???",
		default = False,
	)

	evaluation_mode : EnumProperty(
		name = "Evaluation Mode",
		items = (
			('DAG_EVAL_VIEWPORT', "Viewport (Default)", "Export objects as they appear in the Viewport"),
			('DAG_EVAL_RENDER', "Render", "Export objects as they appear in the Render"),
			),
		description = "Determines properties like object visibility, modifiers etc., where they differ for Render and Viewport",
		default = 'DAG_EVAL_VIEWPORT'
    )


	# transform

	global_scale: FloatProperty(
		name = "Global Scale",
		description = "The scale of the exported objects",
		default = 1.0,
		min = 0.001,
		soft_min = 0.1,
		soft_max = 100.0,
		max = 10000,
		)
	
	forward_axis: EnumProperty(
		name = "Forward Axis",
		description = "What the Forward Axis will be defined as when the model is exported.",
		items = (
			('X', 'X', ''),
			('Y', 'Y', ''),
			('Z', 'Z', ''),
			('NEGATIVE_X', '-X', ''),
			('NEGATIVE_Y', '-Y', ''),
			('NEGATIVE_Z', '-Z (Default)', '')),
		default = 'NEGATIVE_Z'
	)

	up_axis: EnumProperty(
		name = "Up Axis",
		description = "What the Up Axis will be defined as when the model is exported.",
		items = (
			('X', 'X', ''),
			('Y', 'Y (Default)', ''),
			('Z', 'Z', ''),
			('NEGATIVE_X', '-X', ''),
			('NEGATIVE_Y', '-Y', ''),
			('NEGATIVE_Z', '-Z', '')),
		default = 'Y',
	)
	

	# mesh

	export_uv: BoolProperty(
		name = "Export UVs",
		description = "Export UVs",
		default = True,
	)
	
	export_normals: BoolProperty(
		name = "Export Normals",
		description = "Export per-face normals if the face is flat-shaded, per-face-per-loop normals if smooth-shaded",
		default = True,
	)

	export_colors: BoolProperty(
		name = "Export Colors",
		description = "Export per-vertex colors",
		default = False,
	)

	export_curves_as_nurbs: BoolProperty(
		name = "Export Curves as NURBs",
		description = "Export curves in parametric form instead of exporting as mesh",
		default = False,
	)
	
	export_triangulated_mesh: BoolProperty(
		name = "Triangulate Faces",
		description = "All ngons with four or more vertices will be triangulated. Meshes in the scene will not be affected. Behaves like Triangulate Modifier with ngon-method: “Beauty”, quad-method: “Shortest Diagonal”, min vertices: 4",
		default = False,
	)


	export_materials: BoolProperty(
		name = "Export Materials",
		description = "Export a corresponding MTL library with the OBJ file. There must be a Principled-BSDF node for image textures to be exported to the MTL file",
		default = True,
	)

	export_pbr_extensions: BoolProperty(
		name = "Use PBR Extension",
		description = "Export Materials with PBR Extensions, Export MTL library using PBR extensions (roughness, metallic, sheen, clearcoat, anisotropy, transmission)",
		default = False,
	)


	# animation

	start_frame: IntProperty(
		name = "First Frame",
		description = "The first frame to be exported (if Export Animations is enabled)",
		default = 1,
	)

	end_frame: IntProperty(
		name = "Last Frame",
		description = "The last frame to be exported (if Export Animations is enabled)",
		default = 250,
	)


	def export(self, export_preset, filePath):
		"""
		Calls the OBJ Export API to export the currently selected objects with the given settings.
		"""

		# TODO: Ensure export_eval_mode is used appropriately.
		# TODO: Ensure export_selected_objects is used appropriately.
		# TODO: Ensure export_animation is handled appropriately.

		bpy.ops.wm.obj_export(
			# Capsule-handled arguments
			filepath = filePath + ".obj",
			check_existing = False,
			export_animation = export_preset.export_animation,
			export_selected_objects = True,
			apply_modifiers = export_preset.apply_modifiers,

			# File
			export_object_groups = self.export_object_groups,
			export_material_groups = self.export_material_groups,
			export_vertex_groups  = self.export_vertex_groups,
			export_smooth_groups = self.export_smooth_groups,
			smooth_group_bitflags = self.smooth_group_bitflags,
			export_eval_mode = self.evaluation_mode,

			# Scene
			global_scale = self.global_scale,
			forward_axis = self.forward_axis,
			up_axis = self.up_axis,

			# Mesh
			export_uv = self.export_uv,
			export_normals = self.export_normals,
			export_colors = self.export_colors,
			export_curves_as_nurbs = self.export_curves_as_nurbs,
			export_triangulated_mesh = self.export_triangulated_mesh,

			export_materials = self.export_materials,
			export_pbr_extensions = self.export_pbr_extensions,

			# Animation
			start_frame = self.start_frame,
			end_frame = self.end_frame,
		)



	def draw_addon_preferences(self, layout, exportData, cap_file, preset):
		"""
		Draws the panel that represents all the options that the export format has.
		"""
		filepresets_box = layout.column(align = True)
		filepresets_box.separator()

		export_area = filepresets_box.row(align = True)

		# left padding
		export_area.separator()

		# internal column for tabs and contents
		export_tab_area = export_area.column(align = True)
		export_tab_row = export_tab_area.row(align = True)
		export_tab_row.prop(cap_file, "obj_menu_options", expand = True)
		export_tab_area.separator()
		export_tab_area.separator()

		# area for revealed export options
		export_options_area = export_tab_area.column(align = True)

		if cap_file.obj_menu_options == 'File':
			export_options = export_options_area.column(align = True)
			export_options.use_property_split = True
			export_options.use_property_decorate = False  
			export_options.separator()

			object_options = export_options.column(align = True, heading = "Preserve Groups")
			object_options.prop(exportData, "export_object_groups")
			object_options.prop(exportData, "export_material_groups")
			object_options.prop(exportData, "export_vertex_groups")
			object_options.prop(exportData, "export_smooth_groups")

			smooth_bitflags_option = export_options.column(align = True)
			smooth_bitflags_option.active = exportData.export_smooth_groups
			smooth_bitflags_option.prop(exportData, "smooth_group_bitflags")
			smooth_bitflags_option.separator()
			smooth_bitflags_option.separator()
			
			eval_mode_option = export_options.column(align = True)
			eval_mode_option.prop(exportData, "evaluation_mode")
			eval_mode_option.separator()


		if cap_file.obj_menu_options == 'Scene':
			export_options = export_options_area.column(align = True)
			export_options.use_property_split = True
			export_options.use_property_decorate = False
			export_options.separator()

			export_options.prop(exportData, "global_scale")
			export_options.separator()
			export_options.separator()

			export_options.prop(exportData, "forward_axis")
			export_options.prop(exportData, "up_axis")
			export_options.separator()


		elif cap_file.obj_menu_options == 'Object':
			export_options = export_options_area.column(align = True)
			export_options.use_property_split = True
			export_options.use_property_decorate = False
			export_options.separator()

			mesh_options = export_options.column(align = True, heading = "Export")
			mesh_options.prop(exportData, "export_uv")
			mesh_options.prop(exportData, "export_normals")
			mesh_options.prop(exportData, "export_colors")
			mesh_options.prop(exportData, "export_curves_as_nurbs")
			mesh_options.separator()
			mesh_options.prop(exportData, "export_triangulated_mesh")
			mesh_options.separator()

			mat_options = export_options.column(align = True, heading = "Materials")
			mat_options.prop(exportData, "export_materials")

			mat_extension_options = export_options.column(align = True)
			mat_extension_options.active = self.export_materials
			mat_extension_options.prop(exportData, "export_pbr_extensions")
		

		elif cap_file.obj_menu_options == 'Animation':
			export_options = export_options_area.column(align = True)
			export_options.use_property_split = True
			export_options.use_property_decorate = False
			export_options.separator()

			# Disabled Animations Warning
			if preset.export_animation == False:
				export_options_warning = export_options.box()
				export_options_warning_l = export_options_warning.row(align= True)
				export_options_warning_l.label(text= "Export Animation is currently disabled in the General Export Options")
				export_options.separator()
				export_options.separator()

			
			anim_options = export_options.column(align = True, heading = "")
			anim_options.active = preset.export_animation
			
			anim_options.prop(exportData, "start_frame")
			anim_options.prop(exportData, "end_frame")
			anim_options.separator()
			
		
		# right padding
		export_area.separator()
	