
import bpy
from bpy.props import IntProperty, FloatProperty, BoolProperty, StringProperty, PointerProperty, CollectionProperty, EnumProperty
from bpy.types import AddonPreferences, PropertyGroup
from bpy.types import UILayout

from .export_format import CAP_ExportFormat

class CAP_FormatData_FBX(PropertyGroup):

	instance_id = IntProperty(default=-1)

	bundle_textures = BoolProperty(
			name="Bundle Textures",
			description="If enabled, allows any textures that are packed in the .blend file and applied to an object or group that's tagged for export, to be bundled with it inside the FBX file.",
			default=False
			)

	filter_render = BoolProperty(
		name="Filter by Rendering",
		description="Will use the Hide Render option on objects (viewable in the Outliner) to filter whether or not an object can be exported.  If the object is hidden from the render, it will not export regardless of any other settings in this plugin."
		)

	export_types = EnumProperty(
		name="Object Types",
		options={'ENUM_FLAG'},
		items=(('MESH', "Mesh", ""),
			('ARMATURE', "Armature", ""),
			('CAMERA', "Camera", ""),
			('LAMP', "Lamp", ""),
			('EMPTY', "Empty", ""),
			('OTHER', "Other", "Includes other mesh types like Curves and Metaballs, which are converted to meshes on export"),),
		description="Defines what kinds of objects will be exported by the FBX exporter, regardless of any other options in Capsule.",
		default={'EMPTY', 'CAMERA', 'LAMP', 'ARMATURE', 'MESH', 'OTHER'},
		)

	global_scale = FloatProperty(
		name="Global Scale",
		description="The exported scale of the objects.",
		default=1.0
		)

	bake_space_transform = BoolProperty(
		name="Bake Space Transform (Experimental)",
		description="Bakes the space transform of meshes from Blender into the FBX file, when the target world space does not align with the one Blender has. (WARNING - Known broken on armatures/animations, use at your own peril!)",
		default=False
		)

	reset_rotation = BoolProperty(
		name="Reset Rotation",
		description="If enabled, the plugin will reset the rotation of objects and groups when exported.  For groups, they will be reset depending on the rotation of the root object, so make sure that aligns with how you wish the rotation of a group to be reset.  Currently this doesn't work with rotation-influencing constraints, and will be disabled on Objects and Groups that use them.",
		default=False
		)


	axis_up = EnumProperty(
		name="Axis Up",
		description="What the Up Axis will be defined as when the model is exported.",
		items=(
			('X', 'X', ''),
			('Y', 'Y', ''),
			('Z', 'Z', ''),
			('-X', '-X', ''),
			('-Y', '-Y', ''),
			('-Z', '-Z', ''))
			)


	axis_forward = EnumProperty(
		name="Axis Forward",
		description="What the Forward Axis will be defined as when the model is exported.",
		items=(
			('X', 'X', ''),
			('Y', 'Y', ''),
			('Z', 'Z', ''),
			('-X', '-X', ''),
			('-Y', '-Y', ''),
			('-Z', '-Z', ''))
			)

	apply_unit_scale = BoolProperty(
		name="Apply Unit Scale",
		description="Scales the Blender Units system to match the FBX unit measurement (centimetres).",
		default=False
		)

	loose_edges = BoolProperty(
		name="Loose Edges",
		description="Makes any separate edges a two-verted polygon.",
		default=False
		)

	tangent_space = BoolProperty(
		name="Tangent Space",
		description="Exports the mesh tangent vectors,  This option will only work on objects with no n-gons (faces with more than 4 vertices), so please check beforehand!",
		default=False
		)

	use_armature_deform_only = BoolProperty(
		name="Only Include Deform Bones",
		description="Makes any separate edges a two-verted polygon.",
		default=False
		)

	add_leaf_bones = BoolProperty(
		name="Add Leaf Bones",
		description="Appends an extra bone to the end of each bone chain.",
		default=False
		)

	preserve_armature_constraints = BoolProperty(
		name="Preserve Armature Constraints",
		description="(Experimental Feature) If enabled, Capsule will not mute specific bone constraints during the export process.  Turn this on if you rely on bone constraints for animation, but if you also need to change the origin point of these armatures, then the plugin may not succeed in doing this.",
		default=True
		)


	primary_bone_axis = EnumProperty(
		name="Primary Bone Axis",
		description="Defines the primary bone axis for the export.",
		items=(
			('X', 'X', ''),
			('Y', 'Y', ''),
			('Z', 'Z', ''),
			('-X', '-X', ''),
			('-Y', '-Y', ''),
			('-Z', '-Z', '')),
			default='Y'
			)

	secondary_bone_axis = EnumProperty(
		name="Secondary Bone Axis",
		description="Defines the secondary bone axis for the export.",
		items=(
			('X', 'X', ''),
			('Y', 'Y', ''),
			('Z', 'Z', ''),
			('-X', '-X', ''),
			('-Y', '-Y', ''),
			('-Z', '-Z', '')),
		default='X'
		)

	armature_nodetype = EnumProperty(
		name="FBX Armature NodeType",
		description="Defines the type of FBX object Armatures will be exported as.  Change this from Null if you're experiencing import problems in other apps, but picking anything other than null will not guarantee a successful re-import into Blender.",
		items=(
			('Null', 'Null', ''),
			('Root', 'Root', ''),
			('LimbNode', 'LimbNode', ''))
			)


	bake_anim_use_all_bones = BoolProperty(
		name="Key All Bones",
		description="If enabled, this forces the export of one key animation for all bones (required for target apps like UE4).",
		default=False)

	bake_anim_use_nla_strips = BoolProperty(
		name="Use NLA Strips",
		description="If enabled, NLA strips will be exported as animation data.",
		default=False
		)

	bake_anim_use_all_actions = BoolProperty(
		name="Use All Actions",
		description="If enabled, all animation actions in the group or object will be exported.",
		default=False
		)

	bake_anim_force_startend_keying = BoolProperty(
		name="Start/End Keying",
		description="If enabled, this option fully keys the start and end positions of an animation.  Use this if the exported animations playback with incorrect starting positions.",
		default=False
		)

	use_default_take = BoolProperty(
		name="Use Default Take",
		description="If enabled, uses the currently viewed pose/translation of the object as a starting pose for exported animations (excluding certain keyframes).",
		default=False
		)

	optimise_keyframes = BoolProperty(
		name="Optimise Keyframes",
		description="If enabled, removes double keyframes from exported animations.",
		default=False
		)

	bake_anim_step = FloatProperty(
		name="Sampling Rate",
		description="Defines how often, in frames, the export process should evaluate keyframes.",
		default=1,
		min=0,
		max=100,
		soft_min=0.1,
		soft_max=10
		)

	bake_anim_simplify_factor = FloatProperty(
		name="Simplify Factor",
		description="A measure for how much when exported, animations should be simplified.  Setting this value to 0 will disable simplification.  The higher the value, the greater the simplification.",
		default=1,
		min=0,
		max=100,
		soft_min=0,
		soft_max=10
		)

	# A special system variable that defines whether it can be deleted from the Global Presets list.
	x_global_user_deletable = BoolProperty(default=True)
	# A secret fix embedded in the Unity 5 export option, to fix rotated objects.
	x_unity_rotation_fix = BoolProperty(default=False)

class CAP_ExportFormat_FBX(CAP_ExportFormat):
	"""
	Defines how the FBX format inside Capsule.
	"""

	def __init__(self):
		self.type = 'FBX'

	def draw_addon_preferences(layout, exportData, exp):
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
			export_1.label("Additional Options")
			export_1.separator()
			export_1.prop(exportData, "filter_render")
			export_1.prop(exportData, "bundle_textures")

			export_main.separator()
			export_main.separator()
			export_main.separator()

			export_2 = export_main.column(align=True)
			export_2.label("Exportable Object Types")
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
			#export_1.prop(exportData, "reset_rotation")

			export_1.separator()


			export_main.separator()
			export_main.separator()
			export_main.separator()

			export_2 = export_main.column(align=True)
			export_2_row = export_2.row(align=True)
			export_2_row.alignment = 'RIGHT'

			export_2_label = export_2_row.column(align=True)
			export_2_label.alignment = 'RIGHT'
			export_2_label.label("Axis Up:")
			export_2_label.label("Axis Forward:")

			export_2_dropdowns = export_2_row.column(align=True)
			export_2_dropdowns.alignment = 'EXPAND'
			export_2_dropdowns.prop(exportData, "axis_up", text="")
			export_2_dropdowns.prop(exportData, "axis_forward", text="")
			export_2_dropdowns.separator()

			export_main.separator()

		elif exp.fbx_menu_options == 'Geometry':
			export_main = filepresets_box.row(align=True)
			export_main.separator()
			export_1 = export_main.column(align=True)
			export_1.prop(exportData, "loose_edges")
			export_1.prop(exportData, "tangent_space")
			export_1.separator()

		elif exp.fbx_menu_options == 'Armature':
			export_main = filepresets_box.row(align=True)
			export_main.separator()
			export_1 = export_main.column(align=True)
			export_1.prop(exportData, "use_armature_deform_only")
			export_1.prop(exportData, "add_leaf_bones")
			export_1.prop(exportData, "preserve_armature_constraints")

			export_main.separator()
			export_main.separator()
			export_main.separator()

			export_2 = export_main.row(align=True)
			export_2.alignment = 'RIGHT'
			export_2_label = export_2.column(align=True)
			export_2_label.alignment = 'RIGHT'
			export_2_label.label("Primary Bone Axis:")
			export_2_label.label("Secondary Bone Axis:")
			export_2_label.label("Armature Node Type:")

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
			export_1.prop(exportData, "use_default_take")
			export_1.separator()

			export_main.separator()
			export_main.separator()
			export_main.separator()

			export_2 = export_main.column(align=True)
			export_2.prop(exportData, "bake_anim_step")
			export_2.prop(exportData, "bake_anim_simplify_factor")
			export_2.separator()

			export_main.separator()



	def draw_selection_preferences(self, layout):
		"""
		Draws the panel that represents all the options that the export format 
location_presets_listindex		has for specific selections of objects and groups.
		"""

		column = layout.column(align=True)
		column.label("This export type is undefined, someone let a base class here! D:")
		return
