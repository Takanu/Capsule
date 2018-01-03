
import bpy
import mathutils

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



	def draw_addon_preferences(self, layout, exportData, exp):
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
		
	def export(self, gltfModule, exportPreset, exportPass, filePath):
		"""
		Calls the GLTF Export API to make the export happen
		"""

		# filter data according to settings
		data = {
			# 'actions': list(bpy.data.actions) if self.enable_actions else [],
			# 'cameras': list(bpy.data.cameras) if self.enable_cameras else [],
			# 'lamps': list(bpy.data.lamps) if self.enable_lamps else [],
			# 'images': list(bpy.data.images) if self.enable_textures else [],
			'materials': list(bpy.data.materials), # if self.enable_materials else [],
			'meshes': list(bpy.data.meshes), # if self.enable_meshes else [],
			'objects': list(bpy.context.selected_objects),
			'scenes': list(bpy.data.scenes),
			'textures': list(bpy.data.textures) # if self.enable_textures else [],
		}

		# # Remove objects that point to disabled data
		# if not self.enable_cameras:
		#     data['objects'] = [
		#         obj for obj in data['objects']
		#         if not isinstance(obj.data, bpy.types.Camera)
		#     ]
		# if not self.enable_lamps:
		#     data['objects'] = [
		#         obj for obj in data['objects']
		#         if not isinstance(obj.data, bpy.types.Lamp)
		#     ]
		# if not self.enable_meshes:
		#     data['objects'] = [
		#         obj for obj in data['objects']
		#         if not isinstance(obj.data, bpy.types.Mesh)
		#     ]

		# if not settings['nodes_export_hidden']:
		#     data = visible_only(data)

		# if settings['nodes_selected_only']:
		#     data = selected_only(data)

		# if settings['blocks_prune_unused']:
		#     data = used_only(data)

		# for ext_exporter in self.ext_exporters:
		#     ext_exporter.settings = getattr(
		#         self,
		#         'settings_' + ext_exporter.ext_meta['name'],
		#         None
		#     )

		# def is_builtin_mat_ext(prop_name):
		#     if Version(self.asset_version) < Version('2.0'):
		#         return prop_name == 'KHR_technique_webgl'
		#     return False

		# settings['extension_exporters'] = [
		#     self.ext_prop_to_exporter_map[prop.name]
		#     for prop in self.extension_props
		#     if prop.enable and not (self.materials_disable and is_builtin_mat_ext(prop.name))
		# ]

		SETTINGS = {
			'gltf_output_dir': filePath + ".gltf",
			'gltf_name': 'gltf',
			'gltf_export_binary': False,
			'buffers_embed_data': True,
			'buffers_combine_data': False,
			'nodes_export_hidden': False,
			'nodes_global_matrix': mathutils.Matrix.Identity(4),
			'nodes_selected_only': False,
			'blocks_prune_unused': True,
			'meshes_apply_modifiers': True,
			'meshes_interleave_vertex_data': True,
			'images_data_storage': 'COPY',
			'asset_version': '2.0',
			'asset_profile': 'WEB',
			'images_allow_srgb': False,
			'extension_exporters': [],
			'animations_object_export': 'ACTIVE',
			'animations_armature_export': 'ELIGIBLE',
		}

		gltfModule.export_gltf(data, SETTINGS)

