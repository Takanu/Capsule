
import bpy
from bpy.props import IntProperty, FloatProperty, BoolProperty, StringProperty, PointerProperty, CollectionProperty, EnumProperty
from bpy.types import AddonPreferences, PropertyGroup
from bpy.types import UILayout

from .export_format import CAP_ExportFormat

class CAP_FormatData_GLTF(PropertyGroup):

	instance_id = IntProperty(default=-1)

	# export

	asset_version = EnumProperty(
		name="Export Version",
		description="Change the version of gltf that will be exported.",
		items=(
			('1.0', '1.0', ''),
    	('2.0', '2.0', ''),
			)
		)

	gltf_export_binary = BoolProperty(
		name='Export as binary',
		description='Export to the binary glTF file format (.glb)',
		default=False
		)

	pretty_print = BoolProperty(
		name='Pretty-print / indent JSON',
		description='Export JSON with indentation and a newline',
		default=True
		)

	blocks_prune_unused = BoolProperty(
		name='Prune Unused Resources',
		description='Do not export any data-blocks that have no users or references',
		default=True
		)

	enable_cameras = BoolProperty(
		name='Cameras',
		description='Enable the export of cameras',
		default=True
	  )

	enable_lamps = BoolProperty(
		name='Lamps',
		description='Enable the export of lamps',
		default=True
		)

	enable_materials = BoolProperty(
		name='Materials',
		description='Enable the export of materials',
		default=True
		)

	enable_meshes = BoolProperty(
		name='Meshes',
		description='Enable the export of meshes',
		default=True
		)

	enable_textures = BoolProperty(
		name='Textures',
		description='Enable the export of textures',
		default=True
		)

	# transform

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

	# object

	mesh_interleave_vertex_data = BoolProperty(
		name="Interleave Vertex Data",
		description="Store data for each vertex contiguously instead of each vertex property (e.g. position) contiguously.",
		default=False
		)

	materials_disable = BoolProperty(
		name='Disab;e Material Export',
		description='Exports minimum default materials instead of full materials. Useful when using material extensions',
		default=False
		)

	images_data_storage = EnumProperty(
		name='Storage',
		items=(
			('EMBED', 'Embed', 'Embed image data into the glTF file'),
			('REFERENCE', 'Reference', 'Use the same filepath that Blender uses for images'),
			('COPY', 'Copy', 'Copy images to output directory and use a relative reference')
			),
		default='COPY'
		)

	# extensions

	# eh, not yet



class CAP_ExportFormat_GLTF(CAP_ExportFormat):
	"""
	Defines how the FBX format inside Capsule.
	"""

	def __init__(self):
		self.type = 'GLTF'

	def draw_addon_preferences(layout, exportData, exp):
		"""
		Draws the panel that represents all the options that the export format has.
		"""
		filepresets_box = layout.column(align=True)
		filepresets_box.separator()

		export_tabs = filepresets_box.row(align=True)

		# tab bar and tab bar padding
		export_tabs.separator()
		export_tabs.prop(exp, "gltf_menu_options", expand=True)
		export_tabs.separator()

		# separation space between tab bar and contents
		export_separator = filepresets_box.column(align=True)
		export_separator.separator()
		export_separator.separator()

		if exp.gltf_menu_options == 'Export':
			export_main = filepresets_box.row(align=True)
			export_main.separator()

			export_1 = export_main.column(align=True)
			export_1.label("Group Options")
			export_1.separator()
			export_1.prop(exportData, "gltf_export_binary")
			export_1.prop(exportData, "pretty_print")
			export_1.prop(exportData, "blocks_prune_unused")
			export_1.separator()

			export_main.separator()
			export_main.separator()
			export_main.separator()

			export_2 = export_main.column(align=True)
			export_2.label("Exportable Object Types")
			export_2.separator()
			export_2.prop(exportData, "enable_cameras", toggle=True)
			export_2.prop(exportData, "enable_lamps", toggle=True)
			export_2.prop(exportData, "enable_materials", toggle=True)
			export_2.prop(exportData, "enable_meshes", toggle=True)
			export_2.prop(exportData, "enable_textures", toggle=True)
			export_2.separator()

			export_main.separator()

		if exp.gltf_menu_options == 'Transform':
			export_main = filepresets_box.row(align=True)
			export_main.separator()

			export_1 = export_main.column(align=True)
			export_1_row = export_1.row(align=True)
			export_1_row.alignment = 'CENTER'

			export_1_label = export_1_row.column(align=True)
			export_1_label.alignment = 'CENTER'
			export_1_label.label("Axis Up:")
			export_1_label.label("Axis Forward:")

			export_1_dropdowns = export_1_row.column(align=True)
			export_1_dropdowns.alignment = 'EXPAND'
			export_1_dropdowns.prop(exportData, "axis_up", text="")
			export_1_dropdowns.prop(exportData, "axis_forward", text="")
			export_1_dropdowns.separator()

			export_main.separator()

		elif exp.gltf_menu_options == 'Object':
			export_main = filepresets_box.row(align=True)
			export_main.separator()
			export_1 = export_main.column(align=True)
			export_1.prop(exportData, "mesh_interleave_vertex_data")
			export_1.prop(exportData, "materials_disable")

			export_main.separator()
			export_main.separator()
			export_main.separator()

			export_2 = export_main.column(align=True)
			export_2_row = export_2.row(align=True)

			export_2_label = export_2_row.column(align=True)
			export_2_label.alignment = 'RIGHT'
			export_2_label.label("Image Storage:")

			export_2_dropdowns = export_2_row.column(align=True)
			export_2_dropdowns.alignment = 'EXPAND'
			export_2_dropdowns.prop(exportData, "images_data_storage", text="")
			export_2_dropdowns.separator()
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