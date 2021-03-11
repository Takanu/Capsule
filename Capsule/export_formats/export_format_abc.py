
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

class CAP_FormatData_Alembic(PropertyGroup):

	instance_id: IntProperty(default=-1)

	# scene
	start_frame: IntProperty(
		name = "Start Frame",
		description = "The start frame of the export.  Leave at the default value (1) to take the start frame of the current scene.",
		default = 1,
	)

	end_frame: IntProperty(
		name = "End Frame",
		description = "The end frame of the export.  Leave at the default value (250) to take the start frame of the current scene.",
		default = 250,
	)

	transform_samples: IntProperty(
		name = "Transform Samples",
		description = "The number of times per-frame transformations are sampled.",
		default = 1,
		min = 1, 
		max = 128,
	)

	geometry_samples: IntProperty(
		name = "Geometry Samples",
		description = "The number of times per-frame object data is sampled.",
		default = 1,
		min = 1, 
		max = 128,
	)

	shutter_open: FloatProperty(
		name = "Shutter Open",
		description = "The time at which the shutter is open.",
		default = 0.0,
		step = 0.1,
		min = -1,
		max = 1,
	)

	shutter_close: FloatProperty(
		name = "Shutter Close",
		description = "The time at which the shutter is closed.",
		default = 1.0,
		step = 0.1,
		min = -1,
		max = 1,
	)

	flatten_hierarchy: BoolProperty(
		name = "Flatten Hierarchy",
		description = "Do not preserve object parent/child relationships on export.",
		default = False
	)

	export_custom_properties: BoolProperty(
		name = "Export Custom Properties",
		description = "Export custom properties to Alembic .userProperties.",
		default = False
	)

	global_scale: FloatProperty(
		name = "Global Scale",
		description = "The value to which all objects will be scaled with respect to the world's origin point.",
		default = 1.0,
		soft_min = 0.1,
		soft_max = 10,
		step = 0.1,
		min = 0.0001,
		max = 1000,
	)

	# object
	export_uvs: BoolProperty(
		name = "Export UVs",
		description = "Include mesh UVs with the export.",
		default = True
	)

	pack_uvs: BoolProperty(
		name = "Pack UV Islands",
		description = "Export UVs with packed islands.",
		default = True
	)

	export_normals: BoolProperty(
		name = "Export Normals",
		description = "Include mesh normals with the export.",
		default = True
	)

	export_colors: BoolProperty(
		name = "Export Vertex Colors",
		description = "Include vertex colors with the export.",
		default = False
	)

	export_face_sets: BoolProperty(
		name = "Export Face Sets",
		description = "Export per-face shading group assignments.",
		default = False
	)

	# object > triangulate
	triangulate : BoolProperty(
		name = "Triangulate",
		description = "Export polygons (quads and n-gons) as triangles.",
		default = False
	)

	quad_method : EnumProperty(
		name='Quad Method',
		description='The method used for splitting quads into triangles.',
		items=(
			('BEAUTY', 'Beauty', 'Splits quads in nice triangles, a slower method.'),
			('FIXED', 'Fixed', 'Splits every quad on the first and third vertices.'),
			('FIXED_ALTERNATE', 'Fixed Alternate', 'Splits every quads on the 2nd and 4th vertices.'),
			('SHORTEST_DIAGONAL', 'Shortest Diagonal', 'Split the quads based on the distance between the vertices.'),
			),
	)

	ngon_method : EnumProperty(
		name='N-Gon Method',
		description='The method used for splitting n-gons into triangles.',
		items=(
			('BEAUTY', 'Beauty', 'Arranges the new triangles evenly, a slower method.'),
			('CLIP', 'Clip', 'Splits the polygons with an ear clipping algorithm.'),
			),
	)



	use_subdiv_schema: BoolProperty(
		name = "Use Subdivision Schema",
		description = "Export meshes using Alembic’s subdivision schema.",
		default = False
	)

	apply_subdiv: BoolProperty(
		name = "Apply Subsurface Divisions",
		description = "Export subdivision surfaces as meshes.",
		default = False
	)

	export_curves_as_mesh: BoolProperty(
		name = "Export Curves as Meshes",
		description = "Export curves and NURBS surfaces as meshes.",
		default = False
	)

	use_instancing: BoolProperty(
		name = "Use Instancing",
		description = "Export data of duplicated objects as Alembic instances; speeds up the export and can be disabled for compatibility with other software.",
		default = False
	)

	compression_type: EnumProperty(
		name='Compression Type',
		description='???',
		items=(
			('OGAWA', 'OGAWA', '???'),
			('HDF5', 'HDF5', '???'),
			),
	)
	



	# particles
	export_hair: BoolProperty(
		name = "Export Hair",
		description = "Exports hair particle systems as animated curves.",
		default = False
	)

	export_particles: BoolProperty(
		name = "Export Particles",
		description = "Exports non-hair particle systems.",
		default = False
	)

	def export(self, context, export_preset, filePath):
		"""
		Calls the Alembic export operator module to export the currently selected objects.
		"""

		bpy.ops.wm.alembic_export(

			# core
			filepath = filePath + ".abc",
			check_existing = False,
			as_background_job = False,

			selected = True,
			renderable_only = False,
			visible_layers_only = False,

			# scene
			start = self.start_frame,
			end = self.end_frame,
			xsamples = self.transform_samples,
			gsamples = self.geometry_samples,
			sh_open = self.shutter_open,
			sh_close = self.shutter_close,
			flatten = self.flatten_hierarchy,
			global_scale = self.global_scale,

			# object
			uvs = self.export_uvs,
			packuv = self.pack_uvs,
			normals = self.export_normals,
			vcolors = self.export_colors,
			face_sets = self.export_face_sets,
			triangulate = self.triangulate,
			quad_method = self.quad_method,
			ngon_method = self.ngon_method,

			subdiv_schema = self.use_subdiv_schema,
			apply_subdiv = self.apply_subdiv,
			curves_as_mesh = self.export_curves_as_mesh,
			compression_type = self.compression_type,
			use_instancing = self.use_instancing,
			# trianglulate = False,  # part of the API, but Capsule does this elsewhere.
			# quad_method = ???      # see above, although I should provide options like this API does.
			# ngon_method = ???      # ^
			
			# particles
			export_hair = self.export_hair,
			export_particles = self.export_particles,

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
		export_tabs.prop(exp, "alembic_menu_options", expand=True)
		export_tabs.separator()

		# separation space between tab bar and contents
		export_separator = filepresets_box.column(align=True)
		export_separator.separator()
		export_separator.separator()

		if exp.alembic_menu_options == 'Scene':
			export_main = filepresets_box.row(align=True)
			export_main.separator()

			export_1 = export_main.column(align=True)
			export_1.separator()
			export_1.prop(exportData, "start_frame")
			export_1.prop(exportData, "end_frame")
			export_1.prop(exportData, "shutter_open")
			export_1.prop(exportData, "shutter_close")

			export_main.separator()
			export_main.separator()
			export_main.separator()

			export_2 = export_main.column(align=True)
			export_2.separator()
			export_2.prop(exportData, "flatten_hierarchy")
			export_2.prop(exportData, "export_custom_properties")
			export_2.separator()
			export_2.prop(exportData, "transform_samples")
			export_2.prop(exportData, "geometry_samples")
			export_2.prop(exportData, "global_scale")
			export_2.separator()

			export_main.separator()

		if exp.alembic_menu_options == 'Object':
			export_main = filepresets_box.row(align=True)
			export_main.separator()

			export_1 = export_main.column(align=True)
			export_1.separator()
			export_1.prop(exportData, "use_subdiv_schema")
			export_1.prop(exportData, "apply_subdiv")
			export_1.prop(exportData, "export_curves_as_mesh")
			export_1.prop(exportData, "use_instancing")
			export_1.separator()
			export_1.prop(exportData, "compression_type")
			export_1.separator()

			export_main.separator()
			export_main.separator()
			export_main.separator()

			export_2 = export_main.column(align=True)
			export_2.separator()
			export_2.prop(exportData, "export_uvs")
			export_2.prop(exportData, "pack_uvs")
			export_2.prop(exportData, "export_normals")
			export_2.prop(exportData, "export_colors")
			export_2.prop(exportData, "export_face_sets")
			export_2.prop(exportData, "triangulate")
			export_2.prop(exportData, "quad_method")
			export_2.prop(exportData, "ngon_method")
			export_2.separator()

			export_main.separator()

		elif exp.alembic_menu_options == 'Particles':
			export_main = filepresets_box.row(align=True)
			export_main.separator()

			export_1 = export_main.column(align=True)
			export_1.prop(exportData, "export_hair")
			export_1.prop(exportData, "export_particles")
			export_1.separator()

			export_main.separator()
			export_main.separator()
			export_main.separator()

			export_2 = export_main.row(align=True)
			export_2.separator()

			export_main.separator()
