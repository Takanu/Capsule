
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
		name = 'GLTF Type',
		description = 'Defines the type of GLTF file to export.  Each one have differences in how the file is written and how assets are exported or bundled',
		items = (
			('GLB', 'Binary (.glb) (Default)', 'Exports a single file, with all object data and assets packed in binary form. The most efficient and portable type of GLTF file, but more difficult to edit later'),
			('GLTF_SEPARATE', 'Separate Assets (.gltf + .bin + textures)', "Exports multiple files, with separate JSON, binary and texture data. Easiest to edit later but slower and takes up more space"),
			('GLTF_EMBEDDED', 'Embedded Assets (.gltf)', 'Exports a single file, with all data packed into JSON data. Less efficient than binary, but easier to edit later and all non-model assets are bundled in the same file'),
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

	export_import_convert_lighting_mode: EnumProperty(
		name = "Lighting Mode",
		description = "This options provides backwards compatibility for non-standard render engines. Applies to lights",
		items = (
			('SPEC', 'Standard (Default)', 'Physically-based glTF lighting units (cd, lx, nt)'),
			('COMPAT', 'Unitless', 'Non-physical, unitless lighting. Useful when exposure controls are not available'),
			),
		default = 'SPEC',
	)

	export_cameras: BoolProperty(
		name = 'Cameras',
		description = 'Export cameras',
		default = False
	)

	export_lights: BoolProperty(
		name = 'Punctual Lights',
		description = 'Export directional, point, and spot lights',
		default = False,
	)

	# TODO: This doesn't work in Blender 4.1, consider adding this in 4.2 depending on the feature-set

	# export_hierarchy_full_collections: BoolProperty(
	# 	name = 'Include Collections (Collections Only)',
	# 	description = 'Exports the full scene hierarchy, including any intermediate collections.  WARNING - This will only work with Collection Export as it requires an Active Collection'
	# )
 
	export_hierarchy_flatten_objs: BoolProperty(
		name = 'Flatten Object Hierarchies',
		description = 'Will flatten any parent/child relationships between objects on export, apart from skinned meshes.  Useful when working with non-decomposable transformation matrices',
		default = False,
	)

	export_gn_mesh: BoolProperty(
		name = 'Geometry Node Instances (Experimental)',
		description = 'Export Geometry Node instance meshes',
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
		default = False
	)

	export_attributes: BoolProperty(
		name = 'Export Marked Attributes',
		description = 'Exports attributes (including Color Attributes?).  Their name MUST start with an underscore to be exported',
		default = False
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

	export_shared_accessors: BoolProperty(
		name = 'Use Shared Accessors',
		description = "This is a hyper-specific GLTF feature I dont understand and isn't adequately explained by the exporter.  This tooltip will be updated when I know more!",
		default = False
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
		description = "Decides how images associated with the 3D object are exported.",
		items = (
			('AUTO', 'Automatic (Default)', 'Ensures that PNG, JPEG and WebP image files will retain their file formats when exported.  If any other image file format is used it will be converted to PNG'),
			('JPEG', 'JPEG', 'Encodes and saves target images as JPEG files unless the image has alpha, which are instead saved as a PNG.  Can result in a loss of quality'),
			('WEBP', 'WebP', "Encodes and saves target images as WebP files (no fallback is used, all images will be WebP.  WARNING: Most target apps will not accept WebP files"),
			('NONE', 'None', "Don't export images"),
			),
		default = 'AUTO',
	)

	export_texture_dir: StringProperty(
		name = 'Export Image Directory',
		description = "(Only available with the 'GLTF Separate' Export Format) The location to place the textures in, relative to the exported GLTF file",
		default = "",
	)

	export_image_quality: IntProperty(
		name = "Compression",
		description = "Sets the compression quality of exported JPEG and WebP files (when used for texture exports)",
		default = 75,
		subtype = 'PERCENTAGE',
		min = 0,
		max = 100,
	)

	# the property for 'export_keep_originals'
	export_keep_originals: BoolProperty(
		name = 'Keep Original Images',
		description = "(Only available with the 'GLTF Separate' Export Format) Keep original textures files if possible. WARNING: if you use more than one texture, where pbr standard requires only one, only one texture will be used. This can lead to unexpected results",
		default = False,
	)

	export_image_webp_fallback: BoolProperty(
		name = 'Create PNG Fallback for WebP',
		description = "For all WebP images, a PNG image will be created and included as a fallback.  WARNING: Even with a fallback, target apps can still fail to import a GLTF file with WebP images",
		default = True,
	)


	# /////////////////////////////////
	# ANIMATION
 
	export_animation_mode: EnumProperty(
		name = 'Animation Mode',
		description = 'Decides how animations are exported',
		items = (
			('ACTIONS', 'All Actions (Default)', 'Export all actions (active actions and on NLA tracks) as separate animations'),
			('ACTIVE_ACTIONS', 'Merged Active Actions', 'Merge all currently assigned actions into one GLTF animation'),
			('NLA_TRACKS', 'NLA Tracks', "Export individual NLA Tracks as separate animations"),
			('SCENE', 'Scene Data', "Export the 'baked' scene animation data as a single GLTF animation"),
			),
	)

	export_nla_strips_merged_animation_name: StringProperty(
		name = "Merged Animation Name",
		description = "When 'Export Animations by NLA Track' is disabled, this defines the name that the combined GLTF animation will receive",
		default = "Merged Animation",
	)

	export_bake_animation: BoolProperty(
		name = 'Force Export Object Actions',
		description = '*groaning noises*',
		default = False,
	)

	



	export_current_frame: BoolProperty(
		name = 'Use Current Frame',
		description = 'Exports the scene in the current given animation frame',
		default = False
	)

	export_anim_single_armature: BoolProperty(
		name = 'Export All Armature Actions',
		description = 'Export all actions, bound to a single armature. WARNING: Does not support exports including multiple armatures, assign armatures as separate exports before using this option',
		default = False,
	)

	export_frame_range: BoolProperty(
		name = 'Limit to Playback Range',
		description = 'Limits the range of animation exported to the selected playback range',
		default = True,
	)

	export_reset_pose_bones: BoolProperty(
		name = "Always Reset Pose Bones",
		description = "Always reset Pose Bones between each action exported. This is needed when some Bones are not keyed on specific animations",
		default = True,
	)

	export_morph_reset_sk_data: BoolProperty(
		name = "Always Reset Shape Keys",
		description = "Always reset Shape Keys between each action exported. This is needed when some Shape Key channels are not keyed on specific animations",
		default = True,
	)

	export_anim_slide_to_zero: BoolProperty(
		name = "Set Animation Start to 0",
		description = "Ensures all exportable animations will start at 0.0 seconds.  Important for looping animations",
		default = False,
	)

	export_negative_frame: EnumProperty(
		name = "Negative Frame Handling",
		description = "Decide what to do for any exportable animation frames that start before 0",
		items = (
			('SLIDE', 'Slide (Default)', 'Slide the animation to start at frame 0'),
			('CROP', 'Crop', 'Remove any animation frames that start before 0'),
			),
		default = 'SLIDE',
	)


	export_optimize_animation_size: BoolProperty(
		name = 'Optimize Animation Size',
		description = 'Reduces exported filesize by removing duplicate keyframes.  WARNING - Can cause problems with stepped animation',
		default = True
	)
	
	# TODO: Find a better explanation for this
	export_optimize_animation_keep_anim_armature: BoolProperty(
		name = 'Force Keep Channels for Bones',
		description = 'If all keyframes are identical in a rig, force keeping the minimal animation',
		default = True
	)

	export_optimize_animation_keep_anim_object : BoolProperty(
		name = 'Force Keep Channels for Objects',
		description = 'If all keyframes are identical for object transformations, force keeping the minimal animation',
		default = False
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

	



	
	


	# /////////////////////////////////
	# RIGGING
	
	export_rest_position_armature: BoolProperty(
		name = "Use Armature Rest Position",
		description = "If enabled, armatures will be exported in the pose of their rest position",
		default = True,
	)

	export_def_bones: BoolProperty(
		name = 'Export Deformation Bones Only',
		description = 'When on, only the deformation bones will be exported (and needed bones in the hierarchy)',
		default = False
	)

	export_armature_object_remove: BoolProperty(
		name = "Remove Armature Objects",
		description = " Remove Armature objects from export if possible. If an Armature has multiple root bones, it will not be removed",
		default = False,
	)

	export_hierarchy_flatten_bones: BoolProperty(
		name = "Flatten Bone Hierarchy",
		description = "Useful in case of a 'non decomposable transformation matrix'",
		default = False,
	)



	export_morph: BoolProperty(
		name = 'Export Shape Keys',
		description = 'Export shape keys (Also known as morph targets)',
		default = True
	)

	export_morph_normal: BoolProperty(
		name = 'Include Shape Key Normals',
		description = 'Export vertex normals with shape keys',
		default = True
	)

	export_morph_tangent: BoolProperty(
		name = 'Include Shape Key Tangents',
		description = 'Export vertex tangents with shape keys',
		default = True
	)

	export_try_sparse_sk: BoolProperty(
		name = 'Use Sparse Accessors',
		description = "This is a hyper-specific GLTF feature I dont understand and isn't adequately explained by the exporter.  This tooltip will be updated when I know more!",
		default = False
	)

	export_try_omit_sparse_sk: BoolProperty(
		name = 'Omit Empty Sparce Accessors',
		description = "This is a hyper-specific GLTF feature I dont understand and isn't adequately explained by the exporter.  This tooltip will be updated when I know more!",
		default = False
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

	export_influence_nb: IntProperty(
		name = "Bone Influence Count",
		description = "How many joint verex influences will be exported. Models may appear incorrectly in many viewers with value different to 4 or 8",
		default = 4,
		min = 1,
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

			# used to identify that the exporter is being called in code.
			gltf_export_id = "Capsule 1.42", 

			# While this is active, Shape Keys cannot be exported.
			export_apply = export_preset.apply_modifiers,
			
			# FILE
			export_format = self.export_format,
			export_copyright = self.export_copyright,
			export_extras = self.export_custom_properties,


			# SCENE
			export_yup = self.export_y_up,
			export_import_convert_lighting_mode = self.export_import_convert_lighting_mode,
			export_cameras = self.export_cameras,
			export_lights = self.export_lights,
			export_gn_mesh = self.export_gn_mesh,
			# export_hierarchy_full_collections = self.export_hierarchy_full_collections,
   			export_hierarchy_flatten_objs = self.export_hierarchy_flatten_objs,
			

			# MESH
			export_texcoords = self.export_texcoords,
			export_normals = self.export_normals,
			export_tangents = self.export_tangents,
			export_attributes = self.export_attributes,
			use_mesh_edges = self.use_mesh_edges,
			use_mesh_vertices = self.use_mesh_vertices,
			export_shared_accessors = self.export_shared_accessors,

			export_materials = self.export_materials,
			export_image_format = self.export_image_format,
			export_jpeg_quality = self.export_image_quality,
			export_image_quality = self.export_image_quality,
			export_texture_dir = self.export_texture_dir,
			export_keep_originals = self.export_keep_originals,
			export_image_webp_fallback = self.export_image_webp_fallback,


			# ANIMATION`
   			export_animations = export_preset.export_animation,
			export_animation_mode = self.export_animation_mode,
			export_bake_animation = self.export_bake_animation,
			# export_nla_strips = self.export_nla_strips,
			export_nla_strips_merged_animation_name = self.export_nla_strips_merged_animation_name,

			export_current_frame = self.export_current_frame,
			export_frame_range = self.export_frame_range,
			export_anim_slide_to_zero = self.export_anim_slide_to_zero,
			export_negative_frame = self.export_negative_frame,
			
			export_anim_single_armature = self.export_anim_single_armature,
			export_optimize_animation_size = self.export_optimize_animation_size,

			export_force_sampling = self.export_force_sampling,
			export_frame_step = self.export_frame_step,

			export_reset_pose_bones = self.export_reset_pose_bones,
			export_morph_reset_sk_data = self.export_morph_reset_sk_data,

			# RIGGING
			export_rest_position_armature = self.export_rest_position_armature,
			export_def_bones = self.export_def_bones,
			export_armature_object_remove = self.export_armature_object_remove,
			export_hierarchy_flatten_bones = self.export_hierarchy_flatten_bones,

			export_morph = self.export_morph,
			export_morph_normal = self.export_morph_normal,
			export_morph_tangent = self.export_morph_tangent,
			export_try_sparse_sk = self.export_try_sparse_sk,
			export_try_omit_sparse_sk = self.export_try_omit_sparse_sk,

			export_skins = self.export_skins,
			export_all_influences = self.export_all_influences,
			export_influence_nb = self.export_influence_nb,

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

		export_options = export_options_area.column(align = True)
		export_options.use_property_split = True
		export_options.use_property_decorate = False
		export_options.separator()

		if cap_file.gltf_menu_options == 'File':

			export_options.prop(exportData, "export_format")
			export_options.separator()
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
			export_options.prop(exportData, "export_cameras")
			export_options.prop(exportData, "export_lights")
			export_options.separator()
			export_options.prop(exportData, "export_hierarchy_flatten_objs")
			# export_options.prop(exportData, "export_hierarchy_full_collections")
			export_options.separator()	
			export_options.separator()	
			export_options.prop(exportData, "export_import_convert_lighting_mode")
			export_options.separator()
			export_options.separator()


		elif cap_file.gltf_menu_options == 'Object':

			mesh_options = export_options.column(align = True, heading = "Mesh Data")
			mesh_options.prop(exportData, "export_texcoords")
			mesh_options.prop(exportData, "export_normals")
			mesh_options.prop(exportData, "export_tangents")
			mesh_options.prop(exportData, "export_attributes")
			# mesh_options.prop(exportData, "export_displacement")
			mesh_options.separator()
			mesh_options.prop(exportData, "use_mesh_edges")
			mesh_options.prop(exportData, "use_mesh_vertices")
			mesh_options.separator()
			mesh_options.prop(exportData, "export_shared_accessors")

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
			
			compression_options = mat_options.column()
			if exportData.export_image_format == 'AUTO' or exportData.export_image_format == 'NONE':
				compression_options.active = False
			compression_options.prop(exportData, "export_image_quality")
			compression_options.separator()

			compression_options = mat_options.column()
			if exportData.export_image_format == 'NONE' or exportData.export_image_format == 'JPEG':
				compression_options.active = False
			compression_options.prop(exportData, "export_image_webp_fallback")
			compression_options.separator()

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

			type_sub = animation_options.column(align = True)
			type_sub.prop(exportData, "export_animation_mode")
			type_sub.separator()

			anim_mode = exportData.export_animation_mode

			merged_sub = type_sub.column(align = True)
			merged_sub.active = False
			if anim_mode == 'ACTIVE_ACTIONS':
				merged_sub.active = True
			merged_sub.prop(exportData, "export_nla_strips_merged_animation_name")
			merged_sub.separator()

			action_sub = type_sub.column(align = True)
			action_sub.active = False
			if anim_mode == 'ACTIONS' or anim_mode == 'ACTIVE_ACTIONS':
				action_sub.active = True
			action_sub.prop(exportData, "export_bake_animation")

			animation_options.separator()
			animation_options.separator()
			
			generic_sub = animation_options.column(align = True, heading = "Animation Options")
			generic_sub.prop(exportData, "export_current_frame")
			generic_sub.prop(exportData, "export_anim_single_armature")
			generic_sub.prop(exportData, "export_frame_range")
			generic_sub.separator()

			generic_sub.prop(exportData, "export_reset_pose_bones")
			generic_sub.prop(exportData, "export_morph_reset_sk_data")
			generic_sub.separator()
			generic_sub.prop(exportData, "export_anim_slide_to_zero")
			generic_sub.separator()
			generic_sub.separator()
			generic_sub.prop(exportData, "export_negative_frame")
			animation_options.separator()
			animation_options.separator()

			optimization_options = animation_options.column(align = True, heading = "Optimization")
			optimization_options.prop(exportData, "export_optimize_animation_size")
			optimization_options.prop(exportData, "export_optimize_animation_keep_anim_armature")
			optimization_options.prop(exportData, "export_optimize_animation_keep_anim_object")
			optimization_options.separator()
			optimization_options.separator()

			sample_row = animation_options.column(align = True, heading = "Force Sampling")
			sample_row.prop(exportData, "export_force_sampling", text = "Enable")
			sample_row.separator()

			sample_sub = sample_row.column(align = True)
			sample_sub.active = exportData.export_force_sampling 
			sample_sub.prop(exportData, "export_frame_step")
			
			animation_options.separator()
			animation_options.separator()

			
		
		elif cap_file.gltf_menu_options == 'Rigging':

			rigging_options = export_options.column(align = True)

			armature_options = rigging_options.column(align = True, heading = "Armature Options")
			armature_options.prop(exportData, "export_rest_position_armature")
			armature_options.prop(exportData, "export_def_bones")
			armature_options.prop(exportData, "export_armature_object_remove")
			armature_options.prop(exportData, "export_hierarchy_flatten_bones")
			armature_options.separator()
			armature_options.separator()

			shapekey_options = rigging_options.column(align = True, heading = "Shape Key Options")
			shapekey_options.active = False

			if preset.apply_modifiers == False:
				shapekey_options.active = True

			shapekey_options.prop(exportData, "export_morph")
			shapekey_sub = shapekey_options.column(align = True)
			shapekey_sub.active = exportData.export_morph
			
			shapekey_sub.prop(exportData, "export_morph_normal")
			shapekey_sub.prop(exportData, "export_morph_tangent")
			shapekey_sub.separator()

			shapekey_accessors = shapekey_sub.column(align = True)
			shapekey_accessors.prop(exportData, 'export_try_sparse_sk')

			shapekey_accessors_sub = shapekey_accessors.column(align = True)
			if exportData.export_try_sparse_sk == False:
				shapekey_accessors_sub.active = False
			shapekey_accessors_sub.prop(exportData, 'export_try_omit_sparse_sk')

			shapekey_options.separator()
			shapekey_options.separator()

			skinning_options = rigging_options.column(align = True, heading = "Skinning Options")
			skinning_options.prop(exportData, "export_skins")
			skinning_sub = skinning_options.column(align = True)
			skinning_sub.active = exportData.export_skins
			skinning_sub.prop(exportData, "export_all_influences")
			skinning_sub.separator()

			influence_sub = skinning_options.column(align = True)
			if exportData.export_all_influences == True:
				influence_sub.active = False
			influence_sub.prop(exportData, "export_influence_nb")

			rigging_options.separator()
			rigging_options.separator()
		
		elif cap_file.gltf_menu_options == 'Draco':

			# Draco Warning
			if exportData.export_draco_mesh_compression_enable == True:
				export_options_warning = export_options.box()
				export_options_warning_l = export_options_warning.row(align= True)
				export_options_warning_l.label(text= "Draco is an extension and may not be supported by your target application")
				export_options.separator()
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
			export_options.separator()
		
		# right padding
		export_area.separator()
