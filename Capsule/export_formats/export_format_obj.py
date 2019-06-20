
import bpy
from bpy.props import IntProperty, FloatProperty, BoolProperty, StringProperty, PointerProperty, CollectionProperty, EnumProperty
from bpy.types import AddonPreferences, PropertyGroup
from bpy.types import UILayout

from .export_format import CAP_ExportFormat

class CAP_FormatData_OBJ(PropertyGroup):

	instance_id = IntProperty(default=-1)

	# export

	use_blen_objects: BoolProperty(
		name="Export Objects as OBJ Objects",
		description="Exports an object as an OBJ object.  This along with Export Objects as OBJ Groups doesn't really matter to Blender, but may matter to the program you're exporting to.",
		default=False,
		)

	group_by_object: BoolProperty(
		name="Export Objects as OBJ Groups",
		description="Exports an object as an OBJ group.  This along with Export Objects as OBJ Objects doesn't really matter to Blender, but may matter to the program you're exporting to.",
		default=False,
		)

	group_by_material: BoolProperty(
		name="Create OBJ Object by Material",
		description="Exports objects into OBJ groups by the material assigned to them.",
		default=False,
		)

	use_vertex_groups: BoolProperty(
		name="Map Vertex Groups to Polygroups",
		description="The exporter will attempt to map your defined vertex groups into OBJ Polygroups, which is designed to group faces.  If you have any single vertices defined in a vertex group, you will still lose them when using this feature.",
		default=False,
		)
	
	export_per_frame: BoolProperty(
		name="Export OBJ File Per-Frame",
		description="An OBJ file will be written for each frame of animation.  Not recommended for most people, if you want to export assets with animation, use FBX or GLTF instead.",
		default=False
	)

	# transform

	global_scale: FloatProperty(
		name="Global Scale",
		description="The exported scale of the objects.",
		default=1.0,
		soft_min=0.1,
		soft_max=1000.0,
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

	# mesh

	use_smooth_groups: BoolProperty(
		name="Use Smoothing Groups",
		description="Writes sharp edges as basic smoothing groups.",
		default=False,
		)

	use_smooth_groups_bitflags: BoolProperty(
		name="Use Bitflag Smoothing",
		description="Writes smoothing groups IDs as bit flags (this produces at most 32 different smooth groups, usually much less).",
		default=False,
		)

	use_normals: BoolProperty(
		name="Export Normals",
		description="Export one normal per vertex and per face, to represent flat faces and sharp edges",
		default=True,
		)

	use_materials: BoolProperty(
		name="Export Materials",
		description="Export material information as a separate .MTL file.",
		default=True,
		)

	use_uvs: BoolProperty(
		name="Export UVs",
		description="Same as ‘Smooth Groups’, but generate smooth groups IDs as bitflags (produces at most 32 different smooth groups, usually much less).",
		default=True,
		)

	use_nurbs: BoolProperty(
		name="Preserve NURBS",
		description="Write nurbs curves as OBJ nurbs rather than converting them to geometry.",
		default=False,
		)

	keep_vertex_order: BoolProperty(
		name="Preserve Vertex Order",
		description="Preserves the vertex order of your models when exporting.",
		default=False,
		)


	def export(self, export_preset, filePath):
		"""
		Calls the FBX Export API to export the currently selected objects with the given settings.
		"""

		bpy.ops.export_scene.obj(
			filepath=filePath + ".obj", 
			check_existing=False, 
			use_selection=True, 
			use_animation=self.export_per_frame, 
			use_mesh_modifiers=True, 

			use_edges=True, 
			use_smooth_groups=self.use_smooth_groups, 
			use_smooth_groups_bitflags=self.use_smooth_groups_bitflags, 
			use_normals=self.use_normals, 
			use_uvs=self.use_uvs, 
			use_materials=self.use_materials, 
			use_triangles=False, 
			use_nurbs=self.use_nurbs, 
			use_vertex_groups=self.use_vertex_groups, 
			
			use_blen_objects=self.use_blen_objects, 
			group_by_object=self.group_by_object, 
			group_by_material=self.group_by_material, 
			keep_vertex_order=self.keep_vertex_order, 

			global_scale=self.global_scale, 
			path_mode='ABSOLUTE',

			axis_forward=self.axis_forward, 
			axis_up=self.axis_up, 
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
		export_tabs.prop(exp, "obj_menu_options", expand=True)
		export_tabs.separator()

		# separation space between tab bar and contents
		export_separator = filepresets_box.column(align=True)
		export_separator.separator()
		export_separator.separator()

		if exp.obj_menu_options == 'Export':
			export_main = filepresets_box.row(align=True)
			export_main.separator()

			export_1 = export_main.column(align=True)
			export_1.label(text="Group Options")
			export_1.separator()
			export_1.prop(exportData, "use_blen_objects")
			export_1.prop(exportData, "group_by_object")
			export_1.prop(exportData, "group_by_material")
			export_1.prop(exportData, "export_per_frame")
			export_1.separator()

			export_main.separator()
			export_main.separator()
			export_main.separator()

			export_2 = export_main.column(align=True)
			#export_2.label(text="Exportable Object Types")
			export_2.separator()
			#export_types = export_1.row(align=True)
			#export_2.prop(exportData, "export_types")
			export_2.separator()

			export_main.separator()

		if exp.obj_menu_options == 'Transform':
			export_main = filepresets_box.row(align=True)
			export_main.separator()

			export_1 = export_main.column(align=True)
			export_scale = export_1.row(align=True)
			export_scale.prop(exportData, "global_scale")
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

			export_2_dropdowns = export_2_row.column(align=True)
			export_2_dropdowns.alignment = 'EXPAND'
			export_2_dropdowns.prop(exportData, "axis_up", text="")
			export_2_dropdowns.prop(exportData, "axis_forward", text="")
			export_2_dropdowns.separator()

			export_main.separator()

		elif exp.obj_menu_options == 'Object':
			export_main = filepresets_box.row(align=True)
			export_main.separator()
			export_1 = export_main.column(align=True)
			export_1.prop(exportData, "use_smooth_groups")
			export_1.prop(exportData, "use_smooth_groups_bitflags")
			export_1.prop(exportData, "use_vertex_groups")

			export_main.separator()
			export_main.separator()
			export_main.separator()

			export_2 = export_main.column(align=True)
			export_2.prop(exportData, "use_normals")
			export_2.prop(exportData, "use_materials")
			export_2.prop(exportData, "use_uvs")
			export_2.prop(exportData, "use_nurbs")
			export_2.prop(exportData, "keep_vertex_order")
			export_2.separator()

			export_main.separator()
	