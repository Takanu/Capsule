
import bpy
from bpy.props import IntProperty, FloatProperty, BoolProperty, StringProperty, PointerProperty, CollectionProperty, EnumProperty
from bpy.types import AddonPreferences, PropertyGroup
from bpy.types import UILayout

from .export_format import CAP_ExportFormat

class CAP_FormatData_OBJ(PropertyGroup):

	instance_id = IntProperty(default=-1)

	# export

	use_blen_objects: BoolProperty(
		name="OBJ Objects",
		description="Exports an object as an OBJ object.  This along with Export Objects as OBJ Groups doesn't really matter to Blender, but may matter to the program you're exporting to.",
		default=True,
		)

	group_by_object: BoolProperty(
		name="OBJ Groups",
		description="Exports an object as an OBJ group.  This along with Export Objects as OBJ Objects doesn't really matter to Blender, but may matter to the program you're exporting to.",
		default=False,
		)

	group_by_material: BoolProperty(
		name="Material Groups",
		description="Exports objects into OBJ groups by the material assigned to them.",
		default=False,
		)

	use_vertex_groups: BoolProperty(
		name="Map Vertex Groups to Polygroups",
		description="The exporter will attempt to map your defined vertex groups into OBJ Polygroups, which is designed to group faces.  If you have any single vertices defined in a vertex group, you will still lose them when using this feature.",
		default=False,
		)


	# transform

	global_scale: FloatProperty(
		name="Global Scale",
		description="The exported scale of the objects.",
		default=1.0,
		min=0.01,
		soft_min=0.1,
		soft_max=100.0,
		max=1000,
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


	

	# mesh

	use_edges: BoolProperty(
		name="Include Edges",
		description="Include edges in the export.",
		default=True,
		)
		#TODO: Check whether or not this should be on by default, not included in Blender's own UI.

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
		name="Convert NURBS",
		description="Write NURBS curves as OBJ nurbs rather than converting them to geometry.",
		default=False,
		)
	
	keep_vertex_order: BoolProperty(
		name="Preserve Vertex Order",
		description="Preserves the vertex order of your models when exporting.",
		default=False,
		)

	# the property for 'use_triangles'
	triangulate_faces: BoolProperty(
		name="Triangulate Faces",
		description="Converts all faces to triangles.",
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
			# TODO: Add a warning to recommend people not use OBJ for animated objects.
			use_animation=export_preset.export_animation, 
			use_mesh_modifiers=export_preset.apply_modifiers, 

			use_edges=self.use_edges, 
			use_smooth_groups=self.use_smooth_groups, 
			use_smooth_groups_bitflags=self.use_smooth_groups_bitflags, 
			use_normals=self.use_normals, 
			use_uvs=self.use_uvs, 
			use_materials=self.use_materials, 
			use_triangles=self.triangulate_faces, 
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

		export_area = filepresets_box.row(align=True)

		# left padding
		export_area.separator()

		# internal column for tabs and contents
		export_tab_area = export_area.column(align=True)
		export_tab_row = export_tab_area.row(align=True)
		export_tab_row.prop(exp, "obj_menu_options", expand=True)
		export_tab_area.separator()
		export_tab_area.separator()

		# area for revealed export options
		export_options_area = export_tab_area.column(align=True)

		if exp.obj_menu_options == 'File':
			export_options = export_options_area.column(align=True)
			export_options.use_property_split = True
			export_options.use_property_decorate = False  # removes animation options
			export_options.separator()

			object_options = export_options.column(align=True, heading="Objects as")
			object_options.prop(exportData, "use_blen_objects")
			object_options.prop(exportData, "group_by_object")
			object_options.prop(exportData, "group_by_material")
			object_options.separator()

		if exp.obj_menu_options == 'Scene':
			export_options = export_options_area.column(align=True)
			export_options.use_property_split = True
			export_options.use_property_decorate = False  # removes animation options
			export_options.separator()

			export_options.prop(exportData, "global_scale")
			export_options.separator()

			export_options.prop(exportData, "axis_up")
			export_options.prop(exportData, "axis_forward")
			export_options.separator()

		elif exp.obj_menu_options == 'Mesh':
			export_options = export_options_area.column(align=True)
			export_options.use_property_split = True
			export_options.use_property_decorate = False  # removes animation options
			export_options.separator()

			mesh_options = export_options.column(align=True, heading="Mesh Data")
			mesh_options.prop(exportData, "use_normals")
			mesh_options.prop(exportData, "use_materials")
			mesh_options.prop(exportData, "use_uvs")
			mesh_options.prop(exportData, "use_nurbs")
			mesh_options.separator()

			export_options.prop(exportData, "use_edges")
			export_options.prop(exportData, "use_smooth_groups")
			export_options.prop(exportData, "use_smooth_groups_bitflags")
			export_options.prop(exportData, "use_vertex_groups")
			export_options.separator()
			export_options.separator()

			export_options.prop(exportData, "triangulate_faces")
			export_options.prop(exportData, "keep_vertex_order")
			export_options.separator()

			export_options.separator()
		

			
		
		# right padding
		export_area.separator()
	