
import bpy
import mathutils
import os
import json

from bpy.types import UILayout

from bpy.props import (
	IntProperty, 
	FloatProperty, 
	BoolProperty, 
	StringProperty, 
	PointerProperty, 
	CollectionProperty, 
	EnumProperty
)
from bpy.types import (
	AddonPreferences, 
	PropertyGroup,
)
from bpy_extras.io_utils import (
	ExportHelper,
	orientation_helper_factory,
	axis_conversion,
)

from ..io_scene_gltf2 import gltf2_export

class CAP_FormatData_GLTF(PropertyGroup):

	instance_id = IntProperty(default=-1)

	# export

	export_copyright = StringProperty(
		name='Copyright Info',
		description='',
		default=''
		)

	export_embed_buffers = BoolProperty(
		name='Embed Buffers',
		description='',
		default=False
		)

	export_embed_images = BoolProperty(
		name='Embed Images',
		description='',
		default=False
		)

	export_strip = BoolProperty(
		name='Strip Delimiters',
		description='',
		default=False
		)

	# transform

	export_y_up = BoolProperty(
		name='Convert Z Up to Y Up',
		description='',
		default=True
		)

	# attributes

	export_indices = EnumProperty(
		name='Maximum Indices',
		items=(('UNSIGNED_BYTE', 'Unsigned Byte', ''),
			('UNSIGNED_SHORT', 'Unsigned Short', ''),
			('UNSIGNED_INT', 'Unsigned Integer', '')),
		default='UNSIGNED_INT'
		)

	export_force_indices = BoolProperty(
		name='Force Maximum Indices',
		description='',
		default=False
		)

	export_texcoords = BoolProperty(
		name='Export Texture Coordinates',
		description='',
		default=True
		)

	export_normals = BoolProperty(
		name='Export Normals',
		description='',
		default=True
		)

	export_tangents = BoolProperty(
		name='Export Tangents',
		description='',
		default=True
		)

	export_materials = BoolProperty(
		name='Export Materials',
		description='',
		default=True
		)

	export_colors = BoolProperty(
		name='Export Colors',
		description='',
		default=True
		)

	export_cameras = BoolProperty(
		name='Export Cameras',
		description='',
		default=False
		)

	export_camera_infinite = BoolProperty(
		name='Infinite Perspective Camera',
		description='',
		default=False
		)

	# animation

	export_frame_range = BoolProperty(
		name='Export Within Playback Range',
		description='',
		default=True
		)

	export_move_keyframes = BoolProperty(
		name='Move Start Keyframes To 0',
		description='',
		default=True
		)

	export_force_sampling = BoolProperty(
		name='Force Sample Animations',
		description='',
		default=False
		)

	export_current_frame = BoolProperty(
		name='Export Current Frame',
		description='',
		default=True
		)

	export_skins = BoolProperty(
		name='Export Skinning',
		description='',
		default=False
		)

	export_bake_skins = BoolProperty(
		name='Bake Skinning Constraints',
		description='',
		default=False
		)

	export_morph = BoolProperty(
		name='Export Morphing',
		description='',
		default=True
		)

	export_morph_normal = BoolProperty(
		name='Export Morphing Normals',
		description='',
		default=True
		)

	export_morph_tangent = BoolProperty(
		name='Export Morphing Tangents',
		description='',
		default=True
		)

	# experimental features

	export_lights_pbr = BoolProperty(
		name='Export "KHR_lights_pbr"',
		description='',
		default=False
		)

	export_lights_cmn = BoolProperty(
		name='Export "KHR_lights_cmn"',
		description='',
		default=False
		)

	export_common = BoolProperty(
		name='Export "KHR_materials_cmnBlinnPhong"',
		description='',
		default=False
		)

	export_displacement = BoolProperty(
		name='Export "KHR_materials_displacement"',
		description='',
		default=False
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
			export_1.prop(exportData, "export_embed_buffers")
			export_1.prop(exportData, "export_embed_images")
			export_1.prop(exportData, "export_strip")
			export_1.separator()

			export_1.prop(exportData, "export_copyright")
			export_1.separator()

			export_main.separator()
			export_main.separator()
			export_main.separator()

			export_2 = export_main.column(align=True)
			export_2.label("Exportable Object Types")
			export_2.separator()

			export_main.separator()

		if exp.gltf_menu_options == 'Transform':
			export_main = filepresets_box.row(align=True)
			export_main.separator()

			export_1 = export_main.column(align=True)
			export_1.prop(exportData, "export_y_up")
			export_1.separator()

			export_main.separator()
			export_main.separator()
			export_main.separator()

			export_2 = export_main.column(align=True)
			export_2.separator()

			export_main.separator()

		elif exp.gltf_menu_options == 'Attributes':
			export_main = filepresets_box.row(align=True)
			export_main.separator()

			export_1 = export_main.column(align=True)
			export_1_row = export_1.row(align=True)
			export_1_row.alignment = 'LEFT'

			export_1_label = export_1_row.column(align=True)
			export_1_label.alignment = 'LEFT'
			export_1_label.label("Export Indices:")

			export_1_dropdowns = export_1_row.column(align=True)
			export_1_dropdowns.alignment = 'EXPAND'
			export_1_dropdowns.prop(exportData, "export_indices", text="")
			export_1_dropdowns.separator()

			export_1.separator()
			export_1.prop(exportData, "export_force_indices")

			export_2 = export_main.column(align=True)
			export_2.prop(exportData, "export_texcoords")
			export_2.prop(exportData, "export_normals")
			export_2.prop(exportData, "export_tangents")
			export_2.prop(exportData, "export_materials")
			export_2.prop(exportData, "export_colors")
			export_2.separator()

			export_main.separator()

		elif exp.gltf_menu_options == 'Animation':
			export_main = filepresets_box.row(align=True)
			export_main.separator()

			export_1 = export_main.column(align=True)
			export_1.prop(exportData, "export_frame_range")
			export_1.prop(exportData, "export_move_keyframes")
			export_1.prop(exportData, "export_force_sampling")
			export_1.prop(exportData, "export_current_frame")
			export_1.prop(exportData, "export_skins")
			export_1.prop(exportData, "export_bake_skins")
			export_1.separator()

			export_main.separator()
			export_main.separator()
			export_main.separator()

			export_2 = export_main.column(align=True)
			export_2.prop(exportData, "export_morph")
			export_2.prop(exportData, "export_morph_normal")
			export_2.prop(exportData, "export_morph_tangent")
			export_2.separator()

			export_main.separator()

		elif exp.gltf_menu_options == 'Experimental':
			export_main = filepresets_box.row(align=True)
			export_main.separator()

			export_1 = export_main.column(align=True)
			export_1.prop(exportData, "export_lights_pbr")
			export_1.prop(exportData, "export_lights_cmn")
			export_1.prop(exportData, "export_common")
			export_1.prop(exportData, "export_displacement")
			export_1.separator()

			export_main.separator()
			export_main.separator()
			export_main.separator()

			export_2 = export_main.column(align=True)
			export_2.separator()

			export_main.separator()
		
	def export(self, context, exportPreset, exportPass, filePath, fileName):

		"""
		Calls the GLTF Export module to make the export happen.
		"""

		export_settings = {}

		export_settings['gltf_filepath'] = filePath + fileName + ".gltf"
		export_settings['gltf_filedirectory'] = os.path.dirname(export_settings['gltf_filepath']) + '/'

		export_settings['gltf_format'] = 'ASCII'
		export_settings['gltf_copyright'] = self.export_copyright
		export_settings['gltf_embed_buffers'] = self.export_embed_buffers
		export_settings['gltf_embed_images'] = self.export_embed_images
		export_settings['gltf_strip'] = self.export_strip
		export_settings['gltf_indices'] = self.export_indices
		export_settings['gltf_force_indices'] = self.export_force_indices
		export_settings['gltf_texcoords'] = self.export_texcoords
		export_settings['gltf_normals'] = self.export_normals
		export_settings['gltf_tangents'] = self.export_tangents and self.export_normals
		export_settings['gltf_materials'] = self.export_materials
		export_settings['gltf_colors'] = self.export_colors

		# FIXME : Re-introduce once the exporter-agnostic filtering tools are added
		export_settings['gltf_cameras'] = False

		if self.export_cameras:
			export_settings['gltf_camera_infinite'] = self.export_camera_infinite
		else:
			export_settings['gltf_camera_infinite'] = False

			export_settings['gltf_selected'] = True

		# FIXME: Need to work out if layers refers to "export all objects regardless of layer", or "store layer metadata".
		export_settings['gltf_layers'] = True
		export_settings['gltf_extras'] = True
		export_settings['gltf_yup'] = self.export_y_up
		export_settings['gltf_apply'] = exportPass.apply_modifiers
		export_settings['gltf_animations'] = exportPass.export_animation


		if exportPass.export_animation:
			export_settings['gltf_current_frame'] = False
			export_settings['gltf_frame_range'] = self.export_frame_range
			export_settings['gltf_move_keyframes'] = self.export_move_keyframes
			export_settings['gltf_force_sampling'] = self.export_force_sampling
		else:
			export_settings['gltf_current_frame'] = self.export_current_frame
			export_settings['gltf_frame_range'] = False
			export_settings['gltf_move_keyframes'] = False
			export_settings['gltf_force_sampling'] = False

		export_settings['gltf_skins'] = self.export_skins


		if self.export_skins:
			export_settings['gltf_bake_skins'] = self.export_bake_skins
		else:
			export_settings['gltf_bake_skins'] = False
			export_settings['gltf_morph'] = self.export_morph

		if self.export_morph:
			export_settings['gltf_morph_normal'] = self.export_morph_normal
		else:
			export_settings['gltf_morph_normal'] = False

		if self.export_morph and self.export_morph_normal:
			export_settings['gltf_morph_tangent'] = self.export_morph_tangent
		else:
			export_settings['gltf_morph_tangent'] = False


		export_settings['gltf_lights_pbr'] = self.export_lights_pbr
		export_settings['gltf_lights_cmn'] = self.export_lights_cmn
		export_settings['gltf_common'] = self.export_common
		export_settings['gltf_displacement'] = self.export_displacement


		export_settings['gltf_uri'] = []
		export_settings['gltf_binary'] = bytearray()
		export_settings['gltf_binaryfilename'] = os.path.splitext(os.path.basename(filePath + fileName))[0] + '.bin'

		gltf2_export.save(self, context, export_settings)
