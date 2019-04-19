
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

class CAP_FormatData_FBX(PropertyGroup):

	instance_id: IntProperty(default=-1)

	bundle_textures: BoolProperty(
			name="Bundle Textures",
			description="If enabled, allows any textures that are packed in the .blend file and applied to an object or group that's tagged for export, to be bundled with it inside the FBX file.",
			default=False
		)

	export_types: EnumProperty(
		name="Object Types",
		options={'ENUM_FLAG'},
		items=(('MESH', "Mesh", ""),
			('ARMATURE', "Armature", ""),
			('CAMERA', "Camera", ""),
			('LIGHT', "Light", ""),
			('EMPTY', "Empty", ""),
			('OTHER', "Other", "Includes other mesh types like Curves and Metaballs, which are converted to meshes on export"),),
		description="Defines what kinds of objects will be exported by the FBX exporter, regardless of any other options in Capsule.",
		default={'EMPTY', 'CAMERA', 'LIGHT', 'ARMATURE', 'MESH', 'OTHER'},
	)

	global_scale: FloatProperty(
		name="Global Scale",
		description="The exported scale of the objects.",
		default=1.0
	)
	
	apply_unit_scale: BoolProperty(
		name="Apply Unit Scale",
		description="Apply Unit, Take into account current Blender units settings (if unset, raw Blender Units values are used as-is)",
		default=False
	)

	apply_scale_options: EnumProperty(
		name="Apply Scale Options",
		items=(
			('FBX_SCALE_NONE', "All Local", "Apply custom scaling and units scaling to each object transformation, FBX scale remains at 1.0."),
			('FBX_SCALE_UNITS', "FBX Units Scale", "Apply custom scaling to each object transformation, and units scaling to FBX scale."),
			('FBX_SCALE_CUSTOM', "FBX Custom Scale", "Apply custom scaling to FBX scale, and units scaling to each object transformation."),
			('FBX_SCALE_ALL', "FBX All", "Apply custom scaling and units scaling to FBX scale."),
			),
		description="Defines what kinds of objects will be exported by the FBX exporter, regardless of any other options in Capsule.",
	)

	bake_space_transform: BoolProperty(
		name="Bake Space Transform (Experimental)",
		description="Bakes the space transform of meshes from Blender into the FBX file, when the target world space does not align with the one Blender has. (WARNING - Known broken on armatures/animations, use at your own peril!)",
		default=False
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
		default='-Z'
	)

	loose_edges: BoolProperty(
		name="Loose Edges",
		description="Makes any separate edges a two-verted polygon.",
		default=False
	)

	normals: EnumProperty(
		name="Normal Export Type",
		description="Defines how mesh normals are exported.",
		items=(
			('EDGE', 'Edge', 'Writes edge smoothing data for the mesh in the FBX file.'),
			('FACE', 'Face', 'Writes face smoothing data for the mesh in the FBX file.'),
			('OFF', 'Normals Only', 'Exports the current custom normals of the model.')
			),
	)

	tangent_space: BoolProperty(
		name="Tangent Space",
		description="Exports the mesh tangent vectors,  This option will only work on objects with no n-gons (faces with more than 4 vertices), so please check beforehand!",
		default=False
	)

	use_armature_deform_only: BoolProperty(
		name="Only Include Deform Bones",
		description="Makes any separate edges a two-verted polygon.",
		default=False
	)

	add_leaf_bones: BoolProperty(
		name="Add Leaf Bones",
		description="Appends an extra bone to the end of each bone chain.",
		default=False
	)


	primary_bone_axis: EnumProperty(
		name="Primary Bone Axis",
		description="Defines the primary bone axis for the export.",
		items=(
			('X', 'X', ''),
			('Y', 'Y', ''),
			('Z', 'Z', ''),
			('-X', '-X', ''),
			('-Y', '-Y', ''),
			('-Z', '-Z', '')
			),
		default='Y'
	)

	secondary_bone_axis: EnumProperty(
		name="Secondary Bone Axis",
		description="Defines the secondary bone axis for the export.",
		items=(
			('X', 'X', ''),
			('Y', 'Y', ''),
			('Z', 'Z', ''),
			('-X', '-X', ''),
			('-Y', '-Y', ''),
			('-Z', '-Z', '')
			),
		default='X'
	)

	armature_nodetype: EnumProperty(
		name="FBX Armature NodeType",
		description="Defines the type of FBX object Armatures will be exported as.  Change this from Null if you're experiencing import problems in other apps, but picking anything other than null will not guarantee a successful re-import into Blender.",
		items=(
			('NULL', 'Null', "‘Null’ FBX node, similar to Blender’s Empty (default)."),
			('ROOT', 'Root', "‘Root’ FBX node, supposed to be the root of chains of bones."),
			('LIMBNODE', 'LimbNode', "‘LimbNode’ FBX node, a regular joint between two bones.")
			)
		)


	bake_anim_use_all_bones: BoolProperty(
		name="Key All Bones",
		description="If enabled, this forces the export of one key animation for all bones (required for target apps like UE4).",
		default=False
	)

	bake_anim_use_nla_strips: BoolProperty(
		name="Use NLA Strips",
		description="If enabled, NLA strips will be exported as animation data.",
		default=False
	)

	bake_anim_use_all_actions: BoolProperty(
		name="Use All Actions",
		description="If enabled, all animation actions in the group or object will be exported.",
		default=False
	)

	bake_anim_force_startend_keying: BoolProperty(
		name="Start/End Keying",
		description="If enabled, this option fully keys the start and end positions of an animation.  Use this if the exported animations playback with incorrect starting positions.",
		default=False
		)

	optimise_keyframes: BoolProperty(
		name="Optimise Keyframes",
		description="If enabled, removes double keyframes from exported animations.",
		default=False
	)

	bake_anim_step: FloatProperty(
		name="Sampling Rate",
		description="Defines how often, in frames, the export process should evaluate keyframes.",
		default=1,
		min=0,
		max=100,
		soft_min=0.1,
		soft_max=10
	)

	bake_anim_simplify_factor: FloatProperty(
		name="Simplify Factor",
		description="A measure for how much when exported, animations should be simplified.  Setting this value to 0 will disable simplification.  The higher the value, the greater the simplification.",
		default=1,
		min=0,
		max=100,
		soft_min=0,
		soft_max=10
	)

	# A secret fix embedded in the Unity 5 export option, to fix rotated objects.
	x_unity_rotation_fix: BoolProperty(default=False)


	def export(self, exportPreset, exportPass, filePath):
		"""
		Calls the FBX Export API to export the currently selected objects with the given settings.
		"""

		#print("APPLY UNIT SCALE, IS IT FUCKING ON?", self.apply_unit_scale)

		print("Exporting", "*"*70)
		bpy.ops.export_scene.fbx(
			check_existing=False,
			filepath=filePath+ ".fbx",
			filter_glob="*.fbx",
			use_selection=True,
			use_active_collection=False,
			global_scale=self.global_scale,
			apply_unit_scale=self.apply_unit_scale,
			apply_scale_options=self.apply_scale_options,
			axis_forward=self.axis_forward,
			axis_up=self.axis_up,
			bake_space_transform=self.bake_space_transform,
			object_types=self.export_types,
			use_mesh_modifiers=exportPass.apply_modifiers,
			mesh_smooth_type=self.normals,
			use_mesh_edges=self.loose_edges,
			use_tspace=self.tangent_space,
			use_custom_props=False,
			
			# Animation
			add_leaf_bones=self.add_leaf_bones,
			primary_bone_axis=self.primary_bone_axis,
			secondary_bone_axis=self.secondary_bone_axis,
			use_armature_deform_only=self.use_armature_deform_only,
			armature_nodetype=self.armature_nodetype,

			bake_anim=exportPass.export_animation,
			bake_anim_use_all_bones=self.bake_anim_use_all_bones,
			bake_anim_use_nla_strips=self.bake_anim_use_nla_strips,
			bake_anim_use_all_actions=self.bake_anim_use_all_actions,
			bake_anim_force_startend_keying=self.bake_anim_force_startend_keying,
			bake_anim_step=self.bake_anim_step,
			bake_anim_simplify_factor=self.bake_anim_simplify_factor,

			# Export Details
			path_mode='ABSOLUTE',
			embed_textures=self.bundle_textures,
			batch_mode='OFF',
			use_batch_own_dir=False,
			use_metadata=False
		
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
		export_tabs.prop(exp, "fbx_menu_options", expand=True)
		export_tabs.separator()

		# separation space between tab bar and contents
		export_separator = filepresets_box.column(align=True)
		export_separator.separator()
		export_separator.separator()

		if exp.fbx_menu_options == 'Export':
			export_main = filepresets_box.row(align=True)
			export_main.separator()

			export_1 = export_main.column(align=True)
			export_1.label(text="Additional Options")
			export_1.separator()
			export_1.prop(exportData, "bundle_textures")

			export_main.separator()
			export_main.separator()
			export_main.separator()

			export_2 = export_main.column(align=True)
			export_2.label(text="Exportable Object Types")
			export_2.separator()
			#export_types = export_1.row(align=True)
			export_2.prop(exportData, "export_types")
			export_2.separator()

			export_main.separator()

		if exp.fbx_menu_options == 'Transform':
			export_main = filepresets_box.row(align=True)
			export_main.separator()

			export_1 = export_main.column(align=True)
			export_scale = export_1.row(align=True)
			export_scale.prop(exportData, "global_scale")
			export_scale.prop(exportData, "apply_unit_scale", text="", icon='NDOF_TRANS')
			export_1.separator()

			export_1.prop(exportData, "bake_space_transform")
			

			export_1.separator()


			export_main.separator()
			export_main.separator()
			export_main.separator()

			export_2 = export_main.column(align=True)
			export_2_row = export_2.row(align=True)
			export_2_row.alignment = 'RIGHT'

			export_2_label = export_2_row.column(align=True)
			export_2_label.alignment = 'RIGHT'
			export_2_label.label(text="Axis Up:")
			export_2_label.label(text="Axis Forward:")
			export_2_label.label(text="Apply Scale Options:")

			export_2_dropdowns = export_2_row.column(align=True)
			export_2_dropdowns.alignment = 'EXPAND'
			export_2_dropdowns.prop(exportData, "axis_up", text="")
			export_2_dropdowns.prop(exportData, "axis_forward", text="")
			export_2_dropdowns.prop(exportData, "apply_scale_options", text="")
			export_2_dropdowns.separator()

			export_main.separator()

		elif exp.fbx_menu_options == 'Geometry':
			export_main = filepresets_box.row(align=True)
			export_main.separator()
			export_1 = export_main.column(align=True)
			export_1.prop(exportData, "loose_edges")
			export_1.prop(exportData, "tangent_space")
			export_1.separator()

			export_2 = export_main.row(align=True)
			export_2.alignment = 'RIGHT'
			export_2_label = export_2.column(align=True)
			export_2_label.alignment = 'RIGHT'
			export_2_label.label(text="Normals:")

			export_2_dropdowns = export_2.column(align=True)
			export_2_dropdowns.alignment = 'EXPAND'
			export_2_dropdowns.prop(exportData, "normals", text="")
			export_2_dropdowns.separator()

			export_main.separator()

		elif exp.fbx_menu_options == 'Armature':
			export_main = filepresets_box.row(align=True)
			export_main.separator()
			export_1 = export_main.column(align=True)
			export_1.prop(exportData, "use_armature_deform_only")
			export_1.prop(exportData, "add_leaf_bones")

			export_main.separator()
			export_main.separator()
			export_main.separator()

			export_2 = export_main.row(align=True)
			export_2.alignment = 'RIGHT'
			export_2_label = export_2.column(align=True)
			export_2_label.alignment = 'RIGHT'
			export_2_label.label(text="Primary Bone Axis:")
			export_2_label.label(text="Secondary Bone Axis:")
			export_2_label.label(text="Armature Node Type:")

			export_2_dropdowns = export_2.column(align=True)
			export_2_dropdowns.alignment = 'EXPAND'
			export_2_dropdowns.prop(exportData, "primary_bone_axis", text="")
			export_2_dropdowns.prop(exportData, "secondary_bone_axis", text="")
			export_2_dropdowns.prop(exportData, "armature_nodetype", text="")
			export_2_dropdowns.separator()

			export_main.separator()

		elif exp.fbx_menu_options == 'Animation':
			export_main = filepresets_box.row(align=True)
			export_main.separator()

			export_1 = export_main.column(align=True)
			export_1.prop(exportData, "bake_anim_use_all_bones")
			export_1.prop(exportData, "bake_anim_use_nla_strips")
			export_1.prop(exportData, "bake_anim_use_all_actions")
			export_1.prop(exportData, "bake_anim_force_startend_keying")
			export_1.prop(exportData, "optimise_keyframes")
			export_1.separator()

			export_main.separator()
			export_main.separator()
			export_main.separator()

			export_2 = export_main.column(align=True)
			export_2.prop(exportData, "bake_anim_step")
			export_2.prop(exportData, "bake_anim_simplify_factor")
			export_2.separator()

			export_main.separator()


