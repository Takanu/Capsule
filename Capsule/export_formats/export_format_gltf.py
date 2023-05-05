
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


	# ////////////////////////////////
	# FILE

	export_copyright: StringProperty(
		name = 'Copyright Info',
		description = 'Defines the legal rights, conditions and artist attributions for the model',
		default = ''
		)

	export_format: EnumProperty(
		name = 'Export File Format',
		description = 'Decides how the assets associated with the model being exported are included with the ',
		items = (
			('GLB', 'GLTF Binary (.glb)', 'Exports a single file, with all data packed in binary form. The most efficient and portable type of GLTF file, but more difficult to edit later'),
			('GLTF_SEPARATE', 'GLTF Separate (.gltf + .bin + textures)', "Exports multiple files, with separate JSON, binary and texture data. Easiest to edit later but slower and takes up more space"),
			('GLTF_EMBEDDED', 'GLTF Embedded (.gltf)', '(Recommended) Exports a single file, with all data packed in JSON. Less efficient than binary, but easier to edit later and all non-model assets are bundled in the same file'),
			),
		default = 'GLB',
	)
	

	# the property for 'export_extras'
	export_custom_properties: BoolProperty(
		name = 'Export Custom Properties',
		description = 'Export any custom properties as GLTF extras',
		default = False
	)


	# /////////////////////////////////
	# SCENE

	export_y_up: BoolProperty(
		name = 'Axis Up as +Y',
		description = '',
		default = True
	)

	export_cameras: BoolProperty(
		name = 'Export Cameras',
		description = '',
		default = False
	)

	export_lights: BoolProperty(
		name = 'Export Punctual Lights',
		description = '',
		default = False,
	)


	# /////////////////////////////////
	# MESH DATA

	export_texcoords: BoolProperty(
		name = 'Export UVs',
		description = 'Exports any UV coordinate sets associated with meshes',
		default = True
	)

	export_normals: BoolProperty(
		name = 'Export Normals',
		description = 'Exports vertex normals with meshes',
		default = True
	)

	export_tangents: BoolProperty(
		name = 'Export Tangents',
		description = 'Export vertex tangents with meshes',
		default = True
	)

	
	use_mesh_edges: BoolProperty(
		name = 'Include Loose Edges',
		description = 'Export loose edges as lines, using the material from the first material slot',
		default = False
	)

	use_mesh_vertices: BoolProperty(
		name = 'Include Loose Points',
		description = 'Export loose points as glTF points, using the material from the first material slot',
		default = False
	)

	export_colors: BoolProperty(
		name = 'Export Vertex Colors',
		description = 'Export vertex colors with meshes',
		default = True
	)

	export_materials: EnumProperty(
		name = 'Export Materials',
		description = 'Decides how materials are exported',
		items = (
			('EXPORT', 'Export (Default)', 'Export all materials used by exported objects'),
			('PLACEHOLDER', 'Placeholder', 'DO NOT export materials, but write multiple primitive groups per mesh to retain material slot information'),
			('NONE', 'None', "Do not export materials and combine mesh primitive groups.  This will result in the loss of all material slot information")
			),
	)

	export_image_format: EnumProperty(
		name = 'Export Image Format',
		description = 'Decides how images associated with the 3D object are exported',
		items = (
			('AUTO', 'Automatic (Default)', 'Ensures that PNG and JPEG image files will retain their file formats.  If any other image file format is used it will be converted to PNG'),
			('JPEG', 'JPEG', 'Encodes and saves all images as JPEG files unless the image has alpha, which are instead saved as a PNG.  Can result in a loss of quality'),
			('NONE', 'None', "Don't export images")
			),
	)

	export_texture_dir: StringProperty(
		name = 'Export Image Directory',
		description = "(Only available with the 'GLTF Separate' Export Format) The location to place the textures in, relative to the exported GLTF file",
		default = "",
	)

	export_jpeg_quality: IntProperty(
		name = "JPEG Quality",
		description = "Sets the quality of the exported JPEG (when used for texture exports)",
		default = 75,
		min = 0,
		max = 100,
	)

	# the property for 'export_keep_originals'
	export_keep_originals: BoolProperty(
		name = 'Keep Original Images',
		description = "(Only available with the 'GLTF Separate' Export Format) Keep original textures files if possible. WARNING: if you use more than one texture, where pbr standard requires only one, only one texture will be used. This can lead to unexpected results",
		default = False,
	)

	# export_displacement: BoolProperty(
	# 	name = 'Export Displacement (Experimental)',
	# 	description = 'Export displacement textures. Uses an incomplete “KHR_materials_displacement” glTF extension, use at your own peril!',
	# 	default = False
	# )


	# /////////////////////////////////
	# ANIMATION

	export_current_frame: BoolProperty(
		name = 'Use Current Frame',
		description = 'Exports the scene in the current given animation frame',
		default = False
	)


	export_frame_range: BoolProperty(
		name = 'Limit to Playback Range',
		description = 'Limits the range of animation exported to the selected playback range',
		default = True
	)

	
	export_nla_strips: BoolProperty(
		name = 'Group by NLA Track',
		description = 'When on, multiple actions become part of the same glTF animation if they’re pushed onto NLA tracks with the same name. When off, all the currently assigned actions become one glTF animation',
		default = True
	)

	export_nla_strips_merged_animation_name: StringProperty(
		name = "Grouped Animation Name",
		description = "Name of the glTF animation to be exported",
		default = "",
	)

	export_anim_single_armature: BoolProperty(
		name = 'Export All Armature Actions',
		description = 'Export all actions, bound to a single armature. WARNING: Does not support exports including multiple armatures, assign armatures as separate exports before using this option',
		default = False,
	)

	export_optimize_animation_size: BoolProperty(
		name = 'Optimize Animation Size',
		description = 'Reduces exported filesize by removing duplicate keyframes.  WARNING - Can cause problems with stepped animation',
		default = True
	)

	# ////////
	
	export_force_sampling: BoolProperty(
		name = 'Always Sample Animations',
		description = 'Apply sampling to all animations',
		default = True
	)

	export_frame_step: IntProperty(
		name = 'Sampling Rate',
		description = 'Determines how often animated frames should be evaluated for export',
		default = 1,
		min = 1,
		max = 120,
	)

	# ////////

	export_morph: BoolProperty(
		name = 'Export Shape Keys',
		description = 'Export shape keys (Also known as morph targets)',
		default = True
	)

	export_morph_normal: BoolProperty(
		name = 'Export Shape Key Normals',
		description = 'Export vertex normals with shape keys',
		default = True
	)

	export_morph_tangent: BoolProperty(
		name = 'Export Shape Key Tangents',
		description = 'Export vertex tangents with shape keys',
		default = True
	)

	# ////////

	export_skins: BoolProperty(
		name = 'Export Skinning',
		description = '',
		default = False
	)

	export_all_influences: BoolProperty(
		name = 'Include All Bone Influences',
		description = 'Allows >4 joint vertex influences. Models may appear incorrectly in many viewers',
		default = False
	)

	export_def_bones: BoolProperty(
		name = 'Export Deformation Bones Only',
		description = 'When on, only the deformation bones will be exported (and needed bones in the hierarchy)',
		default = False
	)
	

	# TODO: Missing some new animation properties


	# /////////////////////////////////
	# DRACO

	export_draco_mesh_compression_enable: BoolProperty(
		name = "Use Draco Mesh Compression",
		description = "A compression library for GLTF to reduce file sizes and improve file streaming over the web.  Recommended for web content.  WARNING - Not all applications that read GLTF files can read files using Draco compression",
		#TODO: Come back when you know what this is, smh.
		default = False
	)

	export_draco_mesh_compression_level: IntProperty(
		name = "Compression Quality",
		description = "The level of compression applied to the export (0 = fastest, 6 = most compressed)",
		default = 3,
		min = 0,
		max = 6,
	)

	export_draco_position_quantization: IntProperty(
		name = "Draco Mesh Position Quantization",
		description = "Quantization bits for vertex position values (0 = no quantization)",
		default = 14,
		min = 0,
		max = 30,
	)

	export_draco_normal_quantization: IntProperty(
		name = "Draco Mesh Position Quantization",
		description = "Quantization bits for normal values (0 = no quantization)",
		default = 10,
		min = 0,
		max = 30,
	)

	export_draco_texcoord_quantization: IntProperty(
		name = "Draco UV Quantization",
		description = "Quantization bits for UV values (0 = no quantization)",
		default = 12,
		min = 0,
		max = 30,
	)

	export_draco_color_quantization: IntProperty(
		name = "Draco Color Quantization",
		description = "Quantization bits for color values (0 = no quantization)",
		default = 10,
		min = 0,
		max = 30,
	)

	export_draco_generic_quantization: IntProperty(
		name = "Draco Generic Quantization",
		description = "Quantization bits for generic coordinate values like weights or joints (0 = no quantization)",
		default = 12,
		min = 0,
		max = 30,
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

			# CAPSULE
			filepath=final_filename,
			check_existing = False,
			use_selection  = True,

			use_visible = False,
			use_renderable = False,
			use_active_collection = False,
			use_active_scene = True,
			gltf_export_id = "Capsule", # used to identify that the exporter is being called in code.

			# While this is active, Shape Keys cannot be exported.
			export_apply = export_preset.apply_modifiers,
			

			# FILE
			export_format = self.export_format,
			export_copyright = self.export_copyright,
			export_extras = self.export_custom_properties,


			# SCENE
			export_yup = self.export_y_up,
			export_cameras = self.export_cameras,
			export_lights = self.export_lights,
			

			# MESH
			export_texcoords = self.export_texcoords,
			export_normals = self.export_normals,
			export_tangents = self.export_tangents,
			export_colors = self.export_colors,
			use_mesh_edges = self.use_mesh_edges,
			use_mesh_vertices = self.use_mesh_vertices,

			export_materials = self.export_materials,
			export_image_format = self.export_image_format,
			export_jpeg_quality = self.export_jpeg_quality,
			export_texture_dir = self.export_texture_dir,
			export_keep_originals = self.export_keep_originals,

			# TODO: Double-check if this has been removed before the release of 3.3.
			# export_displacement = self.export_displacement,


			# ANIMATION
			
			export_nla_strips = self.export_nla_strips,
			export_nla_strips_merged_animation_name = self.export_nla_strips_merged_animation_name,

			export_animations = export_preset.export_animation,
			export_current_frame = self.export_current_frame,
			export_frame_range = self.export_frame_range,
			export_anim_single_armature = self.export_anim_single_armature,
			export_optimize_animation_size = self.export_optimize_animation_size,

			export_force_sampling = self.export_force_sampling,
			export_frame_step = self.export_frame_step,

			export_morph = self.export_morph,
			export_morph_normal = self.export_morph_normal,
			export_morph_tangent = self.export_morph_tangent,

			export_skins = self.export_skins,
			export_all_influences = self.export_all_influences,
			export_def_bones = self.export_def_bones,


			# DRACO
			export_draco_mesh_compression_enable = self.export_draco_mesh_compression_enable,
			export_draco_mesh_compression_level = self.export_draco_mesh_compression_level,
			export_draco_position_quantization = self.export_draco_position_quantization,
			export_draco_normal_quantization = self.export_draco_normal_quantization,
			export_draco_texcoord_quantization = self.export_draco_texcoord_quantization,
			export_draco_color_quantization = self.export_draco_color_quantization,
			export_draco_generic_quantization = self.export_draco_generic_quantization,

		)

		
	def draw_addon_preferences(self, layout, exportData, cap_file, preset):
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
		export_tab_row.prop(cap_file, "gltf_menu_options", expand = True)
		export_tab_area.separator()
		export_tab_area.separator()

		# area for revealed export options
		export_options_area = export_tab_area.column(align = True)

		if cap_file.gltf_menu_options == 'File':
			export_options = export_options_area.column(align = True)
			export_options.use_property_split = True
			export_options.use_property_decorate = False  # removes animation options
			export_options.separator()
			
			export_options.prop(exportData, "export_format")
			export_options.prop(exportData, "export_copyright")
			export_options.separator()
			export_options.prop(exportData, "export_custom_properties")
			export_options.separator()
			export_options.separator()


		if cap_file.gltf_menu_options == 'Scene':
			export_options = export_options_area.column(align = True)
			export_options.use_property_split = True
			export_options.use_property_decorate = False  # removes animation options
			export_options.separator()

			export_options.prop(exportData, "export_y_up")
			export_options.separator()
			export_options.separator()

			export_options.prop(exportData, "export_cameras")
			export_options.prop(exportData, "export_lights")
			export_options.separator()


		elif cap_file.gltf_menu_options == 'Object':
			export_options = export_options_area.column(align = True)
			export_options.use_property_split = True
			export_options.use_property_decorate = False  # removes animation options
			export_options.separator()

			mesh_options = export_options.column(align = True, heading = "Mesh Data")
			mesh_options.prop(exportData, "export_texcoords")
			mesh_options.prop(exportData, "export_normals")
			mesh_options.prop(exportData, "export_tangents")
			mesh_options.prop(exportData, "export_colors")
			# mesh_options.prop(exportData, "export_displacement")
			mesh_options.separator()
			mesh_options.prop(exportData, "use_mesh_edges")
			mesh_options.prop(exportData, "use_mesh_vertices")

			mesh_options.separator()
			mesh_options.separator()

			export_options.prop(exportData, "export_materials")
			export_options.separator()
			export_options.separator()

			mat_options = export_options.column()
			mat_options.active = True
			if exportData.export_materials == 'NONE':
				mat_options.active = False

			mat_options.prop(exportData, "export_image_format")
			mat_options.separator()

			jpeg_options = mat_options.column()
			jpeg_options.active = True
			if exportData.export_image_format != 'JPEG':
				jpeg_options.active = False
			jpeg_options.prop(exportData, "export_jpeg_quality")
			jpeg_options.separator()

			export_tex_options = mat_options.column()
			if exportData.export_format == 'GLTF_SEPARATE':
				export_tex_options.active = True
			else:
				export_tex_options.active = False
			export_tex_options.prop(exportData, "export_texture_dir")
			export_options.separator()
			export_tex_options.prop(exportData, "export_keep_originals")
			export_options.separator()


		elif cap_file.gltf_menu_options == 'Animation':
			export_options = export_options_area.column(align = True)
			export_options.use_property_split = True
			export_options.use_property_decorate = False  # removes animation options
			export_options.separator()
			
			# Shapekey warning
			if preset.apply_modifiers == True:
				export_options_warning = export_options.box()
				export_options_warning_l = export_options_warning.row(align= True)
				export_options_warning_l.label(text= "While Apply Modifiers is active, objects with Modifiers will NOT export Shape Keys")
				export_options.separator()
				export_options.separator()
			
			# Disabled Animations Warning
			if preset.export_animation == False:
				export_options_warning = export_options.box()
				export_options_warning_l = export_options_warning.row(align= True)
				export_options_warning_l.label(text= "Export Animation is currently disabled in the General Export Options")
				export_options.separator()
				export_options.separator()


			animation_options = export_options.column(align = True)
			animation_options.active = preset.export_animation

			group_sub = animation_options.column(align = True, heading = "NLA Strip Options")
			group_sub.prop(exportData, "export_nla_strips")
			group_sub.separator()

			merged_sub = group_sub.column(align = True)
			merged_sub.active = True
			if exportData.export_nla_strips == True:
				merged_sub.active = False

			merged_sub.prop(exportData, "export_nla_strips_merged_animation_name")
			group_sub.separator()
			group_sub.separator()
			
			generic_sub = animation_options.column(align = True, heading = "Animation Options")
			generic_sub.prop(exportData, "export_current_frame")
			generic_sub.prop(exportData, "export_anim_single_armature")
			generic_sub.prop(exportData, "export_frame_range")
			generic_sub.prop(exportData, "export_optimize_animation_size")
			
			
			animation_options.separator()
			animation_options.separator()

			sample_row = animation_options.row(align = True, heading = "Force Sampling")
			sample_row.separator()
			sample_sub = sample_row.row(align = True)
			sample_sub.prop(exportData, "export_force_sampling", text = "")

			samplerate_sub = sample_sub.row(align = True)
			samplerate_sub.active = exportData.export_force_sampling
			samplerate_sub.prop(exportData, "export_frame_step", text = "")
			sample_row.separator()

			animation_options.separator()
			animation_options.separator()

			shapekey_options = animation_options.column(align = True, heading = "Shape Key Options")
			shapekey_options.active = False
			if preset.apply_modifiers == False:
				shapekey_options.active = True

			shapekey_options.prop(exportData, "export_morph")
			shapekey_sub = shapekey_options.column(align = True)
			shapekey_sub.active = exportData.export_morph
			
			shapekey_sub.prop(exportData, "export_morph_normal")
			shapekey_sub.prop(exportData, "export_morph_tangent")
			shapekey_options.separator()
			shapekey_options.separator()

			skinning_options = animation_options.column(align = True, heading = "Skinning Options")
			skinning_options.prop(exportData, "export_skins")
			skinning_sub = skinning_options.column(align = True)
			skinning_sub.active = exportData.export_skins
			skinning_sub.prop(exportData, "export_all_influences")
			skinning_sub.prop(exportData, "export_def_bones")

			export_options.separator()
		
		elif cap_file.gltf_menu_options == 'Draco':
			export_options = export_options_area.column(align = True)
			export_options.use_property_split = True
			export_options.use_property_decorate = False  # removes animation options
			export_options.separator()

			export_options.prop(exportData, "export_draco_mesh_compression_enable")
			export_options.separator()

			draco_options = export_options.column(align = True)
			draco_options.active = exportData.export_draco_mesh_compression_enable
			draco_options.prop(exportData, "export_draco_mesh_compression_level", text = "Mesh Compression")
			draco_options.separator()
			draco_options.prop(exportData, "export_draco_position_quantization", text = "Position Quantization")
			draco_options.prop(exportData, "export_draco_normal_quantization", text = "Normal Quantization")
			draco_options.prop(exportData, "export_draco_texcoord_quantization", text = "UV Quantization")
			draco_options.prop(exportData, "export_draco_color_quantization", text = "Color Quantization")
			draco_options.prop(exportData, "export_draco_generic_quantization", text = "Other Quantization")

			export_options.separator()
		
		# right padding
		export_area.separator()
