
import bpy

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

class CAP_FormatData_GLTF(PropertyGroup):

	instance_id: IntProperty(default=-1)

	# export

	export_copyright: StringProperty(
		name='Copyright Info',
		description='(Optional) Defines the legal rights and conditions for the model.',
		default=''
		)

	export_format: EnumProperty(
		name='Export File Format',
		description='Decides how the assets associated with the model being exported are included with the ',
		items=(
			('GLTF_EMBEDDED', 'GLTF Embedded (.gltf)', '(Recommended) Exports a single file, with all data packed in JSON. Less efficient than binary, but easier to edit later.'),
			('GLB', 'GLTF Binary (.glb)', 'Exports a single file, with all data packed in binary form. Most efficient and portable, but more difficult to edit later.'),
			('GLTF_SEPARATE', 'GLTF Separate (.gltf + .bin + textures)', 'Exports multiple files, with separate JSON, binary and texture data. Easiest to edit later.')
			),
	)

	export_image_format: EnumProperty(
		name='Export Image Format',
		description='(Optional) Decides how images associated with the 3D object are exported.',
		items=(
			('AUTO', 'Automatic', 'Decides the format to be exported from the image name associated with it in Blender.  PNGs will remain PNGs and JPEGs will remain JPEGs'),
			('JPEG', 'JPEG', 'Encodes and saves all images as JPEG files unless the image has alpha, which are instead saved as a PNG.  Can result in a loss of quality.')
			),
	)

	export_texture_dir: StringProperty(
		name='Export Texture Directory',
		description="What location to place the textures in (relative to the exported GLTF file).",
		default="",
	)

	export_cameras: BoolProperty(
		name='Export Cameras',
		description='',
		default=False
	)

	export_lights: BoolProperty(
		name='Export Lights',
		description='',
		default=False,
	)

	export_custom_properties: BoolProperty(
		name='Export Custom Properties',
		description='Export any custom properties as GLTF extras',
		default=False
	)

	export_draco_mesh_compression_enable: BoolProperty(
		name="Use Draco Mesh Compression",
		description="Try it, who knows! ¯\_(ツ)_/¯",
		#TODO: Come back when you know what this is, smh.
		default=False
	)

	export_draco_mesh_compression_level: IntProperty(
		name="Draco Mesh Compression Level",
		description=" Quantization bits for position values (0 = no quantization)",
		default=3,
		min=0,
		max=6,
	)

	export_draco_position_quantization: IntProperty(
		name="Draco Mesh Position Quantization",
		description="Quantization bits for vertex position values (0 = no quantization)",
		default=14,
		min=0,
		max=30,
	)

	export_draco_normal_quantization: IntProperty(
		name="Draco Mesh Position Quantization",
		description="Quantization bits for normal values (0 = no quantization)",
		default=10,
		min=0,
		max=30,
	)

	export_draco_texcoord_quantization: IntProperty(
		name="Draco UV Quantization",
		description="Quantization bits for UV values (0 = no quantization)",
		default=12,
		min=0,
		max=30,
	)

	export_draco_color_quantization: IntProperty(
		name="Draco Color Quantization",
		description="Quantization bits for color values (0 = no quantization)",
		default=10,
		min=0,
		max=30,
	)

	export_draco_generic_quantization: IntProperty(
		name="Draco Generic Quantization",
		description="Quantization bits for generic coordinate values like weights or joints (0 = no quantization)",
		default=12,
		min=0,
		max=30,
	)

	# transform

	export_y_up: BoolProperty(
		name='Axis Up as +Y',
		description='',
		default=True
	)

	# attributes

	export_texcoords: BoolProperty(
		name='Export UVs',
		description='Exports any UV coordinate sets associated with meshes.',
		default=True
	)

	export_normals: BoolProperty(
		name='Export Normals',
		description='Exports vertex normals with meshes.',
		default=True
	)

	export_tangents: BoolProperty(
		name='Export Tangents',
		description='',
		default=True
	)

	export_materials: EnumProperty(
		name='Export Materials',
		description='Decides how materials are exported.',
		items=(
			('EXPORT', 'Export', 'Export all materials.'),
			('PLACEHOLDER', 'Placeholder', 'Do not export materials, but write multiple primitive groups per mesh, keeping material slot information.'),
			('NONE', 'None', "Do not export materials and combine mesh primitive groups.  This will result in the loss of all material slot information.")
			),
	)

	export_colors: BoolProperty(
		name='Export Colors',
		description='',
		default=True
	)

	export_displacement: BoolProperty(
		name='Export Displacement (Experimental)',
		description='Export displacement textures. Uses an incomplete “KHR_materials_displacement” glTF extension, use at your own peril!',
		default=False
	)

	# animation

	export_frame_range: BoolProperty(
		name='Limit Export to Playback Range',
		description='Limits the range of animation exported to the selected playback range.',
		default=True
	)

	export_force_sampling: BoolProperty(
		name='Force Sample Animations',
		description='Apply sampling to all animations.',
		default=False
	)

	export_current_frame: BoolProperty(
		name='Export Current Frame',
		description='Exports the scene in the current given animation frame.',
		default=True
	)

	export_nla_strips: BoolProperty(
		name='Group by NLA Track',
		description='When on, multiple actions become part of the same glTF animation if they’re pushed onto NLA tracks with the same name. When off, all the currently assigned actions become one glTF animation',
		default=False
	)

	export_def_bones: BoolProperty(
		name='Export Deformation Bones Only',
		description='When on, only the deformation bones will be exported (and needed bones in the hierarchy)',
		default=False
	)

	export_all_influences: BoolProperty(
		name='Include All Bone Influences',
		description='Allows >4 joint vertex influences. Models may appear incorrectly in many viewers',
		default=False
	)

	export_frame_step: IntProperty(
		name='Sampling Rate',
		description='Determines how often animated frames should be evaluated for export.',
		default=1,
		min=1,
		max=120,
	)

	

	export_skins: BoolProperty(
		name='Export Skinning',
		description='',
		default=False
	)
	# FIXME : Removed from 2.8?  Hmm...
	# export_bake_skins: BoolProperty(
	# 	name='Bake Skinning Constraints',
	# 	description='',
	# 	default=False
	# )

	export_morph: BoolProperty(
		name='Export Morphing',
		description='',
		default=True
	)

	export_morph_normal: BoolProperty(
		name='Export Morphing Normals',
		description='',
		default=True
	)

	export_morph_tangent: BoolProperty(
		name='Export Morphing Tangents',
		description='',
		default=True
		)

		
	def export(self, context, export_preset, filePath, fileName):
		"""
		Calls the GLTF Export module to make the export happen.
		"""

		final_filename = ""
		if self.export_format == 'GLTF_EMBEDDED' or 'GLTF_SEPARATE':
			final_filename = filePath + fileName + '.gltf'
		else:
			final_filename = filePath + fileName + '.glb'

		bpy.ops.export_scene.gltf(

			# core settings
			filepath=final_filename,
			check_existing=False,

			# export settings
			export_format=self.export_format,
			export_copyright=self.export_copyright,
			export_image_format=self.export_image_format,
			export_texture_dir =self.export_texture_dir ,

			# object filtering
			export_selected=True,
			export_cameras=self.export_cameras,
			export_lights=self.export_lights,
			export_extras=self.export_custom_properties,

			# compression
			export_draco_mesh_compression_enable=self.export_draco_mesh_compression_enable,
			export_draco_mesh_compression_level=self.export_draco_mesh_compression_level,
			export_draco_position_quantization=self.export_draco_position_quantization,
			export_draco_normal_quantization=self.export_draco_normal_quantization,
			export_draco_texcoord_quantization=self.export_draco_texcoord_quantization,
			export_draco_color_quantization=self.export_draco_color_quantization,
			export_draco_generic_quantization=self.export_draco_generic_quantization,

			# mesh data
			export_yup=self.export_y_up,
			export_apply=export_preset.apply_modifiers,

			export_texcoords=self.export_texcoords,
			export_normals=self.export_normals,
			export_tangents=self.export_tangents,
			export_materials=self.export_materials,
			export_colors=self.export_colors,
			export_displacement=self.export_displacement,

			# animation data
			export_animations=export_preset.export_animation,
			export_frame_range=self.export_frame_range,
			export_frame_step=self.export_frame_step,
			export_force_sampling=self.export_force_sampling,
			export_nla_strips=self.export_nla_strips,
			export_def_bones=self.export_def_bones,
			export_current_frame=self.export_current_frame,
			export_all_influences=self.export_all_influences,

			export_skins=self.export_skins,
			# export_bake_skins=self.export_bake_skins,
			export_morph=self.export_morph,
			export_morph_normal=self.export_morph_normal,
			export_morph_tangent=self.export_morph_tangent,

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
			export_1.alignment = 'RIGHT'
			export_1.prop(exportData, "export_cameras")
			export_1.prop(exportData, "export_lights")
			export_1.prop(exportData, "export_custom_properties")
			export_1.separator()
			
			export_1_row = export_1.row(align=True)
			export_1_row.alignment = 'LEFT'

			export_1_label = export_1_row.column(align=True)
			export_1_label.alignment = 'LEFT'
			export_1_label.label(text="Export Format:")
			export_1_label.label(text="Export Copyright:")
			export_1_label.separator()
			export_1_label.label(text="Texture Format:")
			export_1_label.label(text="Texture Directory:")

			export_1_dropdowns = export_1_row.column(align=True)
			export_1_dropdowns.alignment = 'EXPAND'
			export_1_dropdowns.prop(exportData, "export_format", text="")
			export_1_dropdowns.prop(exportData, "export_copyright", text="")
			export_1_dropdowns.separator()
			export_1_dropdowns.prop(exportData, "export_image_format", text="")
			export_1_dropdowns.prop(exportData, "export_texture_dir", text="")

			export_main.separator()

		if exp.gltf_menu_options == 'Transform':
			export_main = filepresets_box.row(align=True)
			export_main.separator()

			export_1 = export_main.column(align=True)
			export_1.prop(exportData, "export_y_up")
			export_1.separator()

			# export_main.separator()
			# export_main.separator()
			# export_main.separator()

			# export_2 = export_main.column(align=True)
			# export_1.prop(exportData, "export_y_up")
			# export_2.separator()

			export_main.separator()

		elif exp.gltf_menu_options == 'Object':
			export_main = filepresets_box.row(align=True)
			export_main.separator()

			export_1 = export_main.column(align=True)
			export_1_row = export_1.row(align=True)
			export_1_row.alignment = 'LEFT'

			export_1_label = export_1_row.column(align=True)
			export_1.prop(exportData, "export_draco_mesh_compression_enable")
			export_1.separator()
			export_1.prop(exportData, "export_draco_mesh_compression_level")
			export_1.prop(exportData, "export_draco_position_quantization")
			export_1.prop(exportData, "export_draco_normal_quantization")
			export_1.prop(exportData, "export_draco_texcoord_quantization")
			export_1.prop(exportData, "export_draco_color_quantization")
			export_1.prop(exportData, "export_draco_generic_quantization")

			export_main.separator()
			export_main.separator()
			export_main.separator()

			export_2 = export_main.column(align=True)
			export_2.prop(exportData, "export_texcoords")
			export_2.prop(exportData, "export_normals")
			export_2.prop(exportData, "export_tangents")
			export_2.prop(exportData, "export_materials")
			export_2.prop(exportData, "export_colors")
			export_2.prop(exportData, "export_displacement")
			export_2.separator()

			export_main.separator()

		elif exp.gltf_menu_options == 'Animation':
			export_main = filepresets_box.row(align=True)
			export_main.separator()

			export_1 = export_main.column(align=True)
			export_1.prop(exportData, "export_frame_range")
			export_1.prop(exportData, "export_force_sampling")
			export_1.prop(exportData, "export_current_frame")
			export_1.prop(exportData, "export_nla_strips")
			export_1.prop(exportData, "export_def_bones ")
			export_1.prop(exportData, "export_all_influences")
			export_1.separator()
			export_1.prop(exportData, "export_frame_step")
			export_1.separator()

			export_main.separator()
			export_main.separator()
			export_main.separator()

			export_2 = export_main.column(align=True)
			export_2.prop(exportData, "export_skins")
			# export_2.prop(exportData, "export_bake_skins")
			export_2.prop(exportData, "export_morph")
			export_2.prop(exportData, "export_morph_normal")
			export_2.prop(exportData, "export_morph_tangent")
			export_2.separator()

			export_main.separator()
