
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

	# unsure what they do, not revealed in Blender's Export UI
	# subsurf_resolution_modifier: IntProperty(
	# 	name = "Subsurface Resolution",
	# 	description = "???",
	# 	default = 1,
	# ) 

	# subsurf_resolution_type: EnumProperty(
	# 	name="Subsurface Resolution Type",
	# 	description="???",
	# 	items=(
	# 		('view', "View", ""),
	# 		('render', "Render", ""),
	# 	),
	# )

	# export
	include_armatures: BoolProperty(
		name = "Include Armatures",
		description = "Exports related armatures even if unselected.",
		default = False,
	)

	include_shapekeys: BoolProperty(
		name = "Include Shape Keys",
		description = "Exports all shape keys from Mesh objects.",
		default = False,
	)

	export_blender_profile: BoolProperty(
		name = "Export Blender Profile",
		description = "If true, Blender-specific information will be exported (for materials, shaders, bones and other components).",
		default = False,
	)

	sort_by_name: BoolProperty(
		name = "Sort By Name",
		description = "Sort exported data by Object name.",
		default = False,
	)

	export_sim: BoolProperty(
		name = "Export to SL/OpenSim",
		description = "Ensures export compatibility with SL, OpenSim and other compatible online worlds.",
		default = False,
	)

	limit_precision: BoolProperty(
		name = "Limit Precision",
		description = "Reduces the precision of the exported data to 6 digits.",
		default = False,
	)
	

	# object
	export_active_uv_only: BoolProperty(
		name = "Export Active UV Only",
		description = "If true, only the currently active UV map will be exported.",
		default = False,
	)

	export_texture_copy: BoolProperty(
		name = "Export Texture Copy",
		description = "If true, textures associated with the object will be copied to the same destination.",
		default = False,
	)

	use_object_instantiation: BoolProperty(
		name = "Use Object Instances",
		description = "Instantiate multiple Objects from same Data (needs clearer description).",
		default = False,
	)


	# animation
	include_shapekeys: BoolProperty(
		name = "Include Shape Keys",
		description = "Exports all shape keys from Mesh objects.",
		default = False,
	)

	include_all_actions: BoolProperty(
		name = "Include All Actions",
		description = "Exports all animation actions even if currently unassigned (for exporting animation libraries).",
		default = False,
	)

	export_animation_type: EnumProperty(
		name = "Animation Key Type",
		description = "Defines how animation information is exported.",
		items = (
			('sample', "Samples", "Apply custom scaling and units scaling to each object transformation, FBX scale remains at 1.0."),
			('keys', "Curves", "Apply custom scaling to each object transformation, and units scaling to FBX scale."),
			),
	)

	export_transformation_type_selection: EnumProperty(
		name = "Transformation Type",
		description = "Transformation type for translation, scale and rotation.",
		items = (
			('matrix', "Matrix", "Use <matrix> to specify transformations."),
			('transrotloc', 'TransRotLoc', " Use <translate>, <rotate>, <scale> to specify transformations."),
			),
	)

	sampling_rate: IntProperty(
		name = "Sampling Rate",
		description = "The distance between 2 keyframes (1 to key every frame).",
		default = 1,
		min = 1,
	)

	keep_smooth_curves: BoolProperty(
		name = "Keep Smooth Curves",
		description = "Export also the curve handles (if available) (this does only work when the inverse parent matrix is the unity matrix, otherwise you may end up with odd results).",
		default = False,
	)

	keep_keyframes: BoolProperty(
		name = "Keep Keyframes",
		description = "Use existing keyframes as additional sample points (this helps when you want to keep manual tweaks).",
		default = False,
	)

	keep_flat_curves: BoolProperty(
		name = "Keep Flat Curves",
		description = "Export also curves which have only one key or are totally flat.",
		default = False,
	)

	deform_bones_only: BoolProperty(
		name = "Deform Bones Only",
		description = "Only export deforming bones with armatures.",
		default = False,
	)

	keep_bind_info: BoolProperty(
		name = "Keep Bind Info",
		description = "Store Bindpose information in custom bone properties for later use during Collada export.",
		default = False,
	)

	def export(self, exportPreset, exportPass, filePath):
		"""
		Calls the Collada Export API to export the currently selected objects with the given settings.
		"""

		bpy.ops.wm.collada_export(

			# core
			filepath = filePath + '.dae',
			check_existing = False,
			apply_modifiers = exportPass.apply_modifiers,
			selected = True,

			# export
			include_armatures = self.include_armatures,
			include_shapekeys = self.include_shapekeys,
			use_blender_profile = self.export_blender_profile,
			sort_by_name = self.sort_by_name,
			open_sim = self.export_sim,
			limit_precision = self.limit_precision,

			# object
			active_uv_only = self.export_active_uv_only,
			use_texture_copies = self.export_texture_copy,
			use_object_instantiation = self.use_object_instantiation,

			# animation
			include_animations = exportPass.export_animation,
			include_all_actions = self.include_all_actions,
			export_animation_type_selection = self.export_animation_type,
			export_transformation_type_selection = self.export_transformation_type_selection,
			sampling_rate = self.sampling_rate,
			keep_smooth_curves = self.keep_smooth_curves,
			keep_keyframes = self.keep_keyframes,

			deform_bones_only = self.deform_bones_only,
			keep_flat_curves = self.keep_flat_curves,
		)
	
	def draw_addon_preferences(self, layout, exportData, exp):
		"""
		Draws the panel that represents all the options that the export format has.
		"""

		filepresets_box = layout.column(align=True)
		filepresets_box.separator()

		export_tabs = filepresets_box.row(align=True)

		# tab bar and tab bar padding
		export_tabs.separator()
		export_tabs.prop(exp, "collada_menu_options", expand=True)
		export_tabs.separator()

		# separation space between tab bar and contents
		export_separator = filepresets_box.column(align=True)
		export_separator.separator()
		export_separator.separator()

		if exp.collada_menu_options == 'Main':
			export_main = filepresets_box.row(align=True)
			export_main.separator()

			export_1 = export_main.column(align=True)
			export_1.prop(exportData, "include_armatures")
			export_1.prop(exportData, "include_shapekeys")
			export_1.prop(exportData, "sort_by_name")
			export_1.prop(exportData, "limit_precision")
			export_1.prop(exportData, "export_blender_profile")
			export_1.prop(exportData, "export_sim")
			export_1.separator()

			export_main.separator()

		if exp.collada_menu_options == 'Object':
			export_main = filepresets_box.row(align=True)
			export_main.separator()

			export_1 = export_main.column(align=True)
			export_1.prop(exportData, "export_active_uv_only")
			export_1.prop(exportData, "export_texture_copy")
			export_1.prop(exportData, "use_object_instantiation")
			export_1.separator()

			export_main.separator()

		elif exp.collada_menu_options == 'Animation':
			export_main = filepresets_box.row(align=True)
			export_main.separator()

			export_1 = export_main.column(align=True)
			export_1.prop(exportData, "include_all_actions")
			export_1.prop(exportData, "keep_smooth_curves")
			export_1.prop(exportData, "keep_keyframes")
			export_1.prop(exportData, "keep_flat_curves")
			export_1.prop(exportData, "deform_bones_only")
			export_1.separator()
			export_1.prop(exportData, "export_animation_type")
			export_1.prop(exportData, "export_transformation_type_selection")
			export_1.separator()
			export_1.prop(exportData, "sampling_rate")
			export_1.separator()

			export_main.separator()

	
