
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

	# ////////////////////////////////
	# FILE

	export_hair: BoolProperty(
		name = "Export Hair",
		description = "Exports hair particle systems as animated curves.",
		default = True
	)

	export_particles: BoolProperty(
		name = "Export Particles",
		description = "Exports non-hair particle systems.",
		default = True
	)

	# the property for 'flatten'.
	flatten_hierarchy: BoolProperty(
		name = "Flatten Hierarchy",
		description = "Do not preserve object parent/child relationships on export.",
		default = False
	)

	use_instancing: BoolProperty(
		name = "Use Instancing",
		description = "Export data of duplicated objects as Alembic instances; speeds up the export and can be disabled for compatibility with other software.",
		default = True
	)

	# the property for 'curves_as_mesh'
	export_curves_as_mesh: BoolProperty(
		name = "Export Curves as Meshes",
		description = "Export curves and NURBS surfaces as meshes.",
		default = False
	)

	export_custom_properties: BoolProperty(
		name = "Export Custom Properties",
		description = "Export custom properties to Alembic .userProperties.",
		default = True
	)

	evaluation_mode : EnumProperty(
		name = "Evaluation Mode",
		items = (
			('RENDER', "Render (Default)", "Use Render settings for object visibility, modifier settings, etc."),
			('VIEWPORT', "Viewport", "Use Viewport settings for object visibility, modifier settings, etc"),
			),
		description = "Determines what visibility layer affects the visibility of exported objects, modifier settings and other areas where settings differ between Viewport and Render mode.  (Be careful if you're using Filter by Rendering in General Export Options, as objects that are hidden from the Render will not export",
		default = 'RENDER'
    )
	


	# ////////////////////////////////
	# SCENE

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


	# ////////////////////////////////
	# MESH

	# the property for 'uvs'
	export_uvs: BoolProperty(
		name = "Export UVs",
		description = "Include mesh UVs with the export.",
		default = True
	)

	# the property for 'packuv'
	pack_uvs: BoolProperty(
		name = "Pack UV Islands",
		description = "Export UVs with packed islands.",
		default = True
	)

	# the property for 'normals'
	export_normals: BoolProperty(
		name = "Export Normals",
		description = "Include mesh normals with the export.",
		default = True
	)

	# the property for 'vcolors'
	export_colors: BoolProperty(
		name = "Export Vertex Colors",
		description = "Include vertex colors with the export.",
		default = False
	)

	# the property for 'orcos'
	export_generated_coordinates: BoolProperty(
		name = "Export Generated Coordinates",
		description = "Export undeformed mesh vertex coordinates",
		default = False
	)

	# the property for 'face_sets'
	export_face_sets: BoolProperty(
		name = "Export Face Sets",
		description = "Export per-face shading group assignments.",
		default = False
	)

	triangulate : BoolProperty(
		name = "Enable Triangulation",
		description = "Export polygons (quads and n-gons) as triangles.",
		default = False
	)

	quad_method : EnumProperty(
		name = 'Quad Method',
		description = 'The method used for splitting quads into triangles.',
		items = (
			('BEAUTY', 'Beauty', 'Splits quads in nice triangles, a slower method.'),
			('FIXED', 'Fixed', 'Splits every quad on the first and third vertices.'),
			('FIXED_ALTERNATE', 'Fixed Alternate', 'Splits every quads on the 2nd and 4th vertices.'),
			('SHORTEST_DIAGONAL', 'Shortest Diagonal', 'Split the quads based on the distance between the vertices.'),
			('LONGEST_DIAGONAL', 'Longest Diagonal', 'Split the quads along their longest diagonal.'),
			),
		default = 'SHORTEST_DIAGONAL',
	)

	ngon_method : EnumProperty(
		name = 'N-Gon Method',
		description = 'The method used for splitting n-gons into triangles.',
		items = (
			('BEAUTY', 'Beauty', 'Arranges the new triangles evenly, a slower method.'),
			('CLIP', 'Clip', 'Splits the polygons with an ear clipping algorithm.'),
			),
		default = 'BEAUTY',
	)


	# the property for 'subdiv_schema'
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


	# ////////////////////////////////
	# ANIMATION

	# the property for 'start'.
	start_frame: IntProperty(
		name = "Start Frame",
		description = "The start frame of the export.  Leave at the default value (1) to take the start frame of the current scene.",
		default = 1,
	)

	# the property for 'end'.
	end_frame: IntProperty(
		name = "End Frame",
		description = "The end frame of the export.  Leave at the default value (250) to take the start frame of the current scene.",
		default = 250,
	)

	# the property for 'xsamples'.
	transform_samples: IntProperty(
		name = "Transform Samples",
		description = "The number of times per-frame transformations are sampled.",
		default = 1,
		min = 1, 
		max = 128,
	)

	# the property for 'gsamples'.
	geometry_samples: IntProperty(
		name = "Geometry Samples",
		description = "The number of times per-frame object data is sampled.",
		default = 1,
		min = 1, 
		max = 128,
	)

	# the property for 'sh_open'.
	shutter_open: FloatProperty(
		name = "Shutter Open",
		description = "The time at which the shutter is open.",
		default = 0.0,
		step = 0.1,
		min = -1,
		max = 1,
	)

	# the property for 'sh_close'.
	shutter_close: FloatProperty(
		name = "Shutter Close",
		description = "The time at which the shutter is closed.",
		default = 1.0,
		step = 0.1,
		min = -1,
		max = 1,
	)


	


	def export(self, context, export_preset, filePath):
		"""
		Calls the Alembic export operator module to export the currently selected objects.
		"""

		bpy.ops.wm.alembic_export(

			# CAPSULE
			filepath = filePath + ".abc",
			check_existing = False,
			as_background_job = False,

			selected = True,
			renderable_only = False,
			visible_objects_only = False,

			# FILE
			export_hair = self.export_hair,
			export_particles = self.export_particles,

			flatten = self.flatten_hierarchy,
			use_instancing = self.use_instancing,
			curves_as_mesh = self.export_curves_as_mesh,
			export_custom_properties = self.export_custom_properties,

			evaluation_mode = self.evaluation_mode,

			# SCENE
			global_scale = self.global_scale,


			# MESH
			uvs = self.export_uvs,
			packuv = self.pack_uvs,
			normals = self.export_normals,
			vcolors = self.export_colors,
			orcos = self.export_generated_coordinates,
			face_sets = self.export_face_sets,
			triangulate = self.triangulate,
			quad_method = self.quad_method,
			ngon_method = self.ngon_method,

			subdiv_schema = self.use_subdiv_schema,
			apply_subdiv = self.apply_subdiv,

			# ANIMATION
			start = self.start_frame,
			end = self.end_frame,
			xsamples = self.transform_samples,
			gsamples = self.geometry_samples,
			sh_open = self.shutter_open,
			sh_close = self.shutter_close,
			

			

		)
	
	def draw_addon_preferences(self, layout, exportData, exp, preset):
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
		export_tab_row.prop(exp, "alembic_menu_options", expand = True)
		export_tab_area.separator()
		export_tab_area.separator()
		
		# area for revealed export options
		export_options_area = export_tab_area.column(align = True)

		if exp.alembic_menu_options == 'File':
			export_options = export_options_area.column(align = True)
			export_options.use_property_split = True
			export_options.use_property_decorate = False
			export_options.separator()
			
			particle_options = export_options.column(align = True, heading = "Particles")
			particle_options.prop(exportData, "export_particles")
			particle_options.prop(exportData, "export_hair")
			particle_options.separator()
			particle_options.separator()

			extra_options = export_options.column(align = True, heading = "Extras")
			extra_options.prop(exportData, "flatten_hierarchy")
			extra_options.prop(exportData, "use_instancing")
			extra_options.prop(exportData, "export_curves_as_mesh")		
			extra_options.prop(exportData, "export_custom_properties")
			extra_options.separator()
			extra_options.separator()

			export_options.prop(exportData, "evaluation_mode")
			export_options.separator()


		if exp.alembic_menu_options == 'Scene':
			export_options = export_options_area.column(align = True)
			export_options.use_property_split = True
			export_options.use_property_decorate = False
			export_options.prop(exportData, "global_scale")
			export_options.separator()

			
		elif exp.alembic_menu_options == 'Mesh':
			export_options = export_options_area.column(align = True)
			export_options.use_property_split = True
			export_options.use_property_decorate = False
			export_options.separator()
			
			mesh_options = export_options.column(align = True, heading = "Mesh Data")
			mesh_options.prop(exportData, "export_normals")
			mesh_options.prop(exportData, "export_colors")
			mesh_options.prop(exportData, "export_face_sets")
			mesh_options.prop(exportData, 'export_generated_coordinates')
			mesh_options.prop(exportData, "export_uvs")
			mesh_options.prop(exportData, "pack_uvs")
			mesh_options.separator()
			mesh_options.separator()

			subdiv_options = export_options.column(align = True, heading = "Subdivision Data")
			subdiv_options.prop(exportData, "use_subdiv_schema")
			subdiv_options.prop(exportData, "apply_subdiv")
			subdiv_options.separator()
			subdiv_options.separator()

			triangulate_options = export_options.column(align = True, heading = 'Triangulation')
			triangulate_options.prop(exportData, "triangulate", text = "")
			triangulate_options.separator()

			triangulate_sub = export_options.column(align = True)
			triangulate_sub.active = exportData.triangulate
			triangulate_sub.prop(exportData, "quad_method")
			triangulate_sub.prop(exportData, "ngon_method")
			triangulate_sub.separator()
		

		elif exp.alembic_menu_options == 'Animation':
			export_options = export_options_area.column(align = True)
			export_options.use_property_split = True
			export_options.use_property_decorate = False
			export_options.separator()

			# Disabled Animations Warning
			if preset.export_animation == False:
				export_options_warning = export_options.box()
				export_options_warning_l = export_options_warning.row(align=True)
				export_options_warning_l.label(text="Export Animation is currently disabled in the General Export Options")
				export_options.separator()
				export_options.separator()
			
			animation_options = export_options.column(align = True)
			animation_options.active = preset.export_animation

			animation_options.prop(exportData, "start_frame")
			animation_options.prop(exportData, "end_frame")
			animation_options.separator()
			
			animation_options.prop(exportData, "transform_samples")
			animation_options.prop(exportData, "geometry_samples")
			animation_options.separator()

			animation_options.prop(exportData, "shutter_open", slider = True)
			animation_options.prop(exportData, "shutter_close", slider = True)
			animation_options.separator()


		
		# right padding
		export_area.separator()
