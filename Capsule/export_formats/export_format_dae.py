
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

class CAP_FormatData_Collada(PropertyGroup):

	instance_id: IntProperty(default=-1)

	# excluded due to unsure purpose + not included in Blender UI.
	# export_mesh_type : IntProperty(
	# 	name = "Resolution",
	# 	description = "Modifier resolution for export",
	# 	default = 0,
	# )

	# export_object_transformation_type : IntProperty(
	# 	name="Object Transform",
	# 	description="Object Transformation type for translation, scale and rotation",
	# 	default=1,
	# )

	# export_animation_transformation_type : IntProperty(
	# 	name="Animation Transform",
	# 	description="Animation Transformation type for translation, scale and rotation",
	# 	default=1,
	# )


	# # TODO : These must always match?  idk why
	# export_object_transformation_type_selection : EnumProperty(
	# 	name="Object Transform",
	# 	items=(
	# 		('matrix', "Matrix", "Use <matrix> representation for exported transformations"),
	# 		('decomposed', "Decomposed", "Use <rotate>, <translate> and <scale> representation for exported transformations"),
	# 		),
	# 	description="Object Transformation type for translation, scale and rotation",
	# )

	# # TODO : These must always match?  idk why
	# export_animation_transformation_type_selection : EnumProperty(
	# 	name="Animation Transform",
	# 	items=(
	# 		('matrix', "Matrix", "Use <matrix> representation for exported transformations"),
	# 		('decomposed', "Decomposed", "Use <rotate>, <translate> and <scale> representation for exported transformations"),
	# 		),
	# 	description="Defines the type of animation key exported",
	# )


	export_mesh_type_selection : EnumProperty(
		name="Modifier Resolution Export",
		items=(
			('view', "View", "The viewport modifier settings will be exported (IF you have Apply Modifiers enabled)."),
			('render', "Render", "The render modifier settings will be exported"),
			),
		description="Defines what modifier settings are used for the export.",
	)

	export_global_forward_selection : EnumProperty(
		name="Forward Axis",
		description="What the Forward Axis will be defined as when the model is exported.",
		items=(
			('X', 'X', ''),
			('Y', 'Y', ''),
			('Z', 'Z', ''),
			('-X', '-X', ''),
			('-Y', '-Y', ''),
			('-Z', '-Z', '')),
		default='Y',
	)

	export_global_up_selection : EnumProperty(
		name="Up Axis",
		description="What the Up Axis will be defined as when the model is exported.",
		items=(
			('X', 'X', ''),
			('Y', 'Y', ''),
			('Z', 'Z', ''),
			('-X', '-X', ''),
			('-Y', '-Y', ''),
			('-Z', '-Z', '')),
		default='Z'
	)

	apply_global_orientation : BoolProperty(
		name="Apply Global Orientation",
		description="Rotate all root objects to match the global orientation settings otherwise set the global orientation per Collada asset.",
		default=False
	)

	## TODO: Test this, the wording is really weird.
	include_armatures : BoolProperty(
		name="Include Related Armatures",
		description="Export related armatures (even if not enabled).",
		default=False
	)

	include_shapekeys : BoolProperty(
		name="Include Shape Keys",
		description="Export all shape keys from mesh objects.",
		default=False
	)

	deform_bones_only : BoolProperty(
		name="Only Include Deform Bones",
		description="If selected, only deforming bones in armatures will be exported.",
		default=False
	)

	include_animations : BoolProperty(
		name="Include Animations",
		description="Export animations if available (exporting animations will enforce the decomposition of node transforms into <translation> <rotation> and <scale> components).",
		default=False
	)

	include_all_actions : BoolProperty(
		name="Include All Actions",
		description="Include all Actions, Export also unassigned actions (this allows you to export entire animation libraries for your character(s)).",
		default=True
	)

	export_animation_type_selection : EnumProperty(
		name="Key Type",
		items=(
			('sample', "Samples", "Export sampled points guided by the Sampling Rate."),
			('keys', "Curves", "Export curves, guided by the curve keys"),
			),
		description="Defines the type of animation key exported",
	)
	
	sampling_rate : IntProperty(
		name="Sampling Rate",
		description="The distance between 2 keyframes (1 to key every frame)",
		default=1,
	)
	
	keep_smooth_curves : BoolProperty(
		name="Keep Smooth Curves",
		description="Include the curve handles (if available) in the export.  This only works when the inverse parent matrix is the unity matrix, otherwise you may end up with odd results",
		default=False
	)

	keep_keyframes : BoolProperty(
		name="Keep Keyframes",
		description="Use existing keyframes as additional sample points (this helps when you want to keep manual tweaks)",
		default=False
	)

	keep_flat_curves : BoolProperty(
		name="Include All Keyed Curves",
		description="Export also curves which have only one key or are totally flat",
		default=False
	)

	active_uv_only : BoolProperty(
		name="Only Export Active UV Map",
		description="Export only the active UV Map",
		default=False
	)

	use_texture_copies : BoolProperty(
		name="Export Textures",
		description="Export textures to same folder where the .dae file is exported",
		default=False
	)

	triangulate : BoolProperty(
		name="Triangulate Mesh",
		description="Export polygons (quads and n-gons) as triangles",
		default=True
	)

	use_object_instantiation : BoolProperty(
		name="Use Object Instances",
		description="Instantiate multiple Objects from same Data",
		default=True
	)

	use_blender_profile : BoolProperty(
		name="Use Blender Profile",
		description="Export additional Blender specific information (for material, shaders, bones, etc.)",
		default=True
	)

	sort_by_name : BoolProperty(
		name="Sort by Object Name",
		description="Sort exported data by Object name.",
		default=False
	)
	
	

	open_sim : BoolProperty(
		name="Export to SL/OpenSim",
		description="Export in compatibility mode for Second Life, OpenSim and other compatible online worlds",
		default=False
	)

	limit_precision : BoolProperty(
		name="Limit Precision",
		description="Reduce the precision of the exported data to 6 digits",
		default=False
	)

	keep_bind_info : BoolProperty(
		name="Keep Bind Info",
		description="Store Bindpose information in custom bone properties for later use during Collada export",
		default=False
	)

	# used instead of export_object_transformation_type_selection 
	# and export_animation_transformation_type 
	export_transform_type : EnumProperty(
		name="Export Transform",
		items=(
			('0', "Matrix", "Use <matrix> representation for exported transformations"),
			('1', "Decomposed", "Use <rotate>, <translate> and <scale> representation for exported transformations"),
			),
		description="Defines the type of transformation data exported for both objects and animations.",
	)


	def export(self, export_preset, filePath):
		"""
		Calls the Collada Export API to export the currently selected objects with the given settings.
		"""

		# if self.export_transform_type == '0':
		# 	anim_transform_type = 'matrix'
		# else:
		# 	anim_transform_type = 'decomposed'


		bpy.ops.wm.collada_export(

			# core
			filepath = filePath + '.dae',
			check_existing = False,
			apply_modifiers = export_preset.apply_modifiers,
			selected = True,
			include_animations = export_preset.export_animation,

			export_mesh_type_selection = self.export_mesh_type_selection,
			export_global_forward_selection = self.export_global_forward_selection,
			export_global_up_selection = self.export_global_up_selection,
			apply_global_orientation = self.apply_global_orientation,
			include_armatures = self.include_armatures,
			include_shapekeys = self.include_shapekeys,
			deform_bones_only = self.deform_bones_only,
			include_all_actions = self.include_all_actions,
			export_animation_type_selection = self.export_animation_type_selection,
			sampling_rate = self.sampling_rate,
			keep_smooth_curves = self.keep_smooth_curves,
			keep_keyframes = self.keep_keyframes,
			keep_flat_curves = self.keep_flat_curves,

			active_uv_only = self.active_uv_only,
			use_texture_copies = self.use_texture_copies,
			triangulate = self.triangulate,

			use_object_instantiation = self.use_object_instantiation,
			use_blender_profile = self.use_blender_profile,
			sort_by_name = self.sort_by_name,
			open_sim = self.open_sim,
			limit_precision = self.limit_precision,
			keep_bind_info = self.keep_bind_info,

			## TODO: Confirm this worked the way I expect it to.
			export_object_transformation_type = int(self.export_transform_type),
			export_animation_transformation_type = int(self.export_transform_type),

			
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

		# internal column for tabs and contents
		export_tab_area = export_area.column(align=True)
		export_tab_row = export_tab_area.row(align=True)
		export_tab_row.prop(exp, "collada_menu_options", expand=True)
		export_tab_area.separator()
		export_tab_area.separator()
		
		# area for revealed export options
		export_options_area = export_tab_area.column(align=True)

		if exp.collada_menu_options == 'File':
			export_options = export_options_area.column(align=True)
			export_options.use_property_split = True
			export_options.use_property_decorate = False  # removes animation options
			export_options.separator()

			export_options.prop(exportData, "use_object_instantiation")
			export_options.prop(exportData, "sort_by_name")
			export_options.prop(exportData, "use_blender_profile")
			export_options.prop(exportData, "limit_precision")
			export_options.prop(exportData, "use_texture_copies")

			export_options.separator()
		
		elif exp.collada_menu_options == 'Scene':
			export_options = export_options_area.column(align=True)
			export_options.use_property_split = True
			export_options.use_property_decorate = False  # removes animation options
			export_options.separator()

			export_options.prop(exportData, "apply_global_orientation")
			export_options.separator()
			export_options.prop(exportData, "export_global_forward_selection")
			export_options.prop(exportData, "export_global_up_selection")
			export_options.separator()
			export_options.prop(exportData, "export_transform_type")
			export_options.separator()

		elif exp.collada_menu_options == 'Mesh':
			export_options = export_options_area.column(align=True)
			export_options.use_property_split = True
			export_options.use_property_decorate = False  # removes animation options
			export_options.separator()

			export_options.prop(exportData, "triangulate")
			export_options.prop(exportData, "active_uv_only")
			export_options.separator()
			export_options.prop(exportData, "export_mesh_type_selection")
			

			export_options.separator()


		elif exp.collada_menu_options == 'Animation':
			export_options = export_options_area.column(align=True)
			export_options.use_property_split = True
			export_options.use_property_decorate = False  # removes animation options
			export_options.separator()


			export_options.prop(exportData, "keep_flat_curves")
			export_options.prop(exportData, "include_all_actions")
			export_options.prop(exportData, "include_shapekeys")
			export_options.separator()
			export_options.separator()

			export_options.prop(exportData, "export_animation_type_selection")
			export_options.separator()
			curves_optional = export_options.column(align=True)

			smooth_curves_active = False
			if exportData.export_animation_type_selection == 'keys':
				smooth_curves_active = True

			curves_optional.active = smooth_curves_active
			curves_optional.prop(exportData, "keep_smooth_curves")
			curves_optional.separator()
			curves_optional.separator()

			
			samples_optional = export_options.column(align=True)
			samples_active = False
			if exportData.export_animation_type_selection == 'sample':
				samples_active = True
			
			samples_optional.active = samples_active
			samples_optional.prop(exportData, "sampling_rate")
			samples_optional.prop(exportData, "keep_keyframes")
			samples_optional.separator()


		elif exp.collada_menu_options == 'Armature':
			export_options = export_options_area.column(align=True)
			export_options.use_property_split = True
			export_options.use_property_decorate = False  # removes animation options
			export_options.separator()

			export_options.prop(exportData, "include_armatures")
			export_options.prop(exportData, "deform_bones_only")
			export_options.prop(exportData, "open_sim")
			export_options.prop(exportData, "keep_bind_info")

			export_options.separator()

		
		# right padding
		export_area.separator()


	
