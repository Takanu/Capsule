
import bpy
from bpy.types import AddonPreferences, PropertyGroup
from bpy.props import (
    IntProperty, 
    FloatProperty, 
    BoolProperty, 
    StringProperty, 
    PointerProperty, 
    CollectionProperty, 
    EnumProperty,
)

from ..export_formats import (
    CAP_ExportFormat, 
    CAP_FormatData_FBX, 
    CAP_FormatData_OBJ, 
    CAP_FormatData_GLTF, 
    CAP_FormatData_Alembic, 
    CAP_FormatData_Collada,
    CAP_FormatData_STL,
    CAP_FormatData_USD,
)

# Disabled as it's outdated.
# TODO: hmm...
# def DrawAnimationWarning(self, context):
#         layout = self.layout
#         layout.label(text="Hey!  The animation feature may result in objects being incorrectly positioned")
#         layout.label(text="if you define the Origin as anything other than Scene for exports with complex")
#         layout.label(text="dependencies and animations (armature animations will be unaffected).")
#         layout.separator()
#         layout.label(text="If you find objects have moved after the export operation simply use the undo tool.")
#         layout.separator()
# def CAP_Update_AnimationWarning(self, context):
#     if self.export_animation_prev is False and self.export_animation is True:
#         bpy.context.window_manager.popup_menu(DrawAnimationWarning, title="Animation Warning", icon='INFO')
#     self.export_animation_prev = self.export_animation


class CAPSULE_ExportPreset(PropertyGroup):
    # Used to define properties for a single export preset.
    # Export presets include Capsule-specific features as well as .FBX exporter features
    # and any defined Passes and Tags.

    name: StringProperty(
        name = "Preset Name",
        description="The name of the export preset.",
        default=""
        )

    instance_id: IntProperty(
        name = "Instance ID",
        description="INTERNAL ONLY - Unique ID used to pair with format data, that holds the full export settings for the chosen file type."
        )

    description: StringProperty(
        name = "Description",
        description="(Internal Use Only) TBA",
        default=""
        )

    sub_directory: StringProperty(
        name="Sub-directory",
        description="Allows you to extend the file path of the export from the Location Preset assigned to it",
        default="/"
        )

    filter_by_rendering: BoolProperty(
        name="Filter by Render Visibility",
        description="Will use the Hide Render option on objects (viewable in the Outliner) to filter whether or not an object can be exported.  If the object is hidden from the render, it will not export regardless of any other settings in this plugin"
        )
    
    # FIXME 1.2 : Move as exporter-specific data?
    export_animation: BoolProperty(
        name="Export Animation",
        description="If ticked, animation data will be exported depending on the File Format.  STL does not support animation data",
        default=False,
        )

    export_animation_prev: BoolProperty(default=False)

    apply_modifiers: BoolProperty(
        name="Apply Modifiers",
        description="If enabled, all modifiers will be applied to the export",
        default=False
        )

    # Currently disabled until further notice due to reliability issues.
    # reset_rotation: BoolProperty(
    #     name="Reset Rotation",
    #     description="If enabled, the plugin will reset the rotation of objects and collections when exported.  For collections, they will be reset depending on the rotation of the root object, so make sure that aligns with how you wish the rotation of a collection to be reset.  \n\nCurrently this doesn't work with rotation-influencing constraints, and will be disabled on objects and collection that use them.",
    #     default=False
    #     )

    preserve_armature_constraints: BoolProperty(
        name="Preserve Armature Constraints",
        description="(Experimental Feature) If enabled, Capsule will not mute specific bone constraints during the export process.  \n\nTurn this on if you rely on bone constraints for animation, but if you also need to change the origin point of these armatures, then the plugin may not succeed in doing this",
        default=True
        )


    # TODO : This is where the Filter and Export Commands will sit

    format_type: EnumProperty(
        name="Format Type",
        items=
            (
            ('Alembic', "Alembic (.abc)", "Export assets in the Alembic file format.  A lossy file format designed to bake complex assets for caching and production purposes"),
            ('Collada', "Collada (.dae)", "Export assets in the Collada file format.  An older file format used for import with various modelling programs and some online games"),
            ('FBX', "FBX (.fbx)", "Export assets in the FBX file format.  A proprietary Autodesk format suitable for exchanging data with Autodesk apps and a popular format for game engines."),
            ('GLTF', "GLTF (.gltf, .glb)", "Export assets in the GLTF file format.  An efficient, lossy 3D format designed for web apps and games."),
            ('OBJ', "OBJ (.obj)", "Export assets in the OBJ file format.  An ancient file format with limited options suitable for simple static objects"),
            ('STL', "STL (.stl)", "Export assets as STL files.  An older file format used specifically for CAD and 3D printing applications"),
            ('USD', "USD (.usda)", "Export assets as USD files.  A modern, highly detailed file format but Blender's implementation is new and offers limited capabilities"),
            ),
        description="Defines what file type objects with this preset will export to and the export options available for this preset",
        )

    # the data stored for FBX presets.
    data_fbx: PointerProperty(type=CAP_FormatData_FBX)

    # the data stored for OBJ presets.
    data_obj: PointerProperty(type=CAP_FormatData_OBJ)

    # the data stored for GLTF presets.
    data_gltf: PointerProperty(type=CAP_FormatData_GLTF)

    # the data stored for Alembic presets.
    data_abc: PointerProperty(type=CAP_FormatData_Alembic)

    # the data stored for Collada presets.
    data_dae: PointerProperty(type=CAP_FormatData_Collada)

    # the data stored for STL presets.
    data_stl: PointerProperty(type=CAP_FormatData_STL)

    # the data stored for USD presets.
    data_usd: PointerProperty(type=CAP_FormatData_USD)


    # A special system variable that defines whether it can be deleted from the Global Presets list.
    x_global_user_deletable: BoolProperty(default=True)


class CAPSULE_LocationPreset(PropertyGroup):
    # Defines a single location default, assigned to specific objects to define where they should be exported to.

    name: StringProperty(
        name="",
        description="The name of the file path default."
        )

    path: StringProperty(name="",
        description="The file path to export the object to.",
        default="",
        subtype="FILE_PATH"
        )


class CAPSULE_ExportData(PropertyGroup):
    """
    A property group passed onto the "default datablock", the empty object created in a blend file to store all the available export presets.
    """

    # the version of Capsule this datablock was created with
    version_number: FloatProperty(default=1.10)

    # the available file presets
    export_presets: CollectionProperty(type=CAPSULE_ExportPreset)

    # the preset selected on the list panel, when viewed from the AddonPreferences window.
    export_presets_listindex: IntProperty(default=0)

    # if true, this object is the empty created for the purposes of storing preset data.
    is_storage_object: BoolProperty(default=False)

    # the available location presets created by the user
    location_presets: CollectionProperty(type=CAPSULE_LocationPreset)

    # the location selected on the Locations panel, inside the 3D view
    location_presets_listindex: IntProperty(default=0)

    alembic_menu_options: EnumProperty(
        name="Export Options",
        description="",
        items=(
        ('File', 'File', 'A tab containing file format-specific data sets like custom properties.'),
        ('Scene', 'Scene', 'A tab containing options for scene units, transform data and object type export filters.'),
        ('Mesh', 'Mesh', 'A tab containing options for how object geometry and mesh-related assets are exported.'),
        ('Animation', 'Animation', 'A tab containing options for animation-related data is handled and exported.'),
        ('Particles', 'Particles', 'A tab containing options for how particles are exported.'),
        ),
    )

    collada_menu_options: EnumProperty(
        name="Export Options",
        description="",
        items=(
        ('File', 'File', 'A tab containing file format-specific data sets like custom properties.'),
        ('Scene', 'Scene', 'A tab containing options for scene units, transform data and object type export filters.'),
        ('Mesh', 'Mesh', 'A tab containing options for how object geometry and mesh-related assets are exported.'),
        ('Animation', 'Animation', 'A tab containing options for animation-related data is exported.'),
        ('Armature', 'Armature', 'A tab containing options for how armature and armature-related data are exported.'),
        ),
    )

    fbx_menu_options: EnumProperty(
        name="Export Options",
        description="",
        items=(
        ('File', 'File', 'A tab containing file format-specific data sets like custom properties.'),
        ('Scene', 'Scene', 'A tab containing options for scene units, transform data and object type export filters.'),
        ('Mesh', 'Mesh', 'A tab containing options for how object geometry and mesh-related assets are exported.'),
        ('Animation', 'Animation', 'A tab containing options for animation-related data is exported.'),
        ('Armature', 'Armature', 'A tab containing options for how armature and armature-related data are exported.'),
        ),
    )

    gltf_menu_options: EnumProperty(
        name="Export Options",
        description="",
        items=(
        ('File', 'File', 'A tab containing file format-specific data sets like custom properties.'),
        ('Scene', 'Scene', 'A tab containing options for scene units, transform data and object type export filters.'),
        ('Mesh', 'Mesh', 'A tab containing options for how object geometry and mesh-related assets are exported.'),
        ('Animation', 'Animation', 'A tab containing options for animation-related data is exported.'),
        ('Draco', 'Draco','A tab containing Draco compression options.'),
        ),
    )

    obj_menu_options: EnumProperty(
        name="Export Options",
        description="",
        items=(
        ('File', 'File', 'A tab containing file format-specific data sets like custom properties.'),
        ('Scene', 'Scene', 'A tab containing options for scene units, transform data and object type export filters.'),
        ('Mesh', 'Mesh', 'A tab containing options for how object geometry and mesh-related assets are exported.'),
        ),
    )

    



# ////////////////////// - CLASS REGISTRATION - ////////////////////////
# decided to do it all in __init__ instead, skipping for now.

# classes = (
#     CAPSULE_ExportTag, 
#     CAPSULE_ExportPassTag, 
#     CAPSULE_ExportPass, 
#     CAPSULE_ExportPreset, 
#     CAPSULE_LocationPreset, 
#     CAPSULE_ExportData,
# )

# def register():
#     export_formats.register()
#     for cls in classes:
#         bpy.utils.register_class(cls)


# def unregister():
#     for cls in reversed(classes):
#         bpy.utils.unregister_class(cls)

#     export_formats.unregister()
