
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

from . import export_formats
from .export_formats import (
    CAP_ExportFormat, 
    CAP_FormatData_FBX, 
    CAP_FormatData_OBJ, 
    CAP_FormatData_GLTF, 
    CAP_FormatData_Alembic, 
    CAP_FormatData_Collada,
    CAP_FormatData_STL,
)

def CAP_Update_TagName(self, context):

    preferences = context.preferences
    addon_prefs = preferences.addons[__package__].preferences

    if addon_prefs.plugin_is_ready is True:
        exp = bpy.data.objects[addon_prefs.default_datablock].CAPExp
        currentTag = exp.tags[exp.tags_index]
        tag_name = currentTag.name

        # Get tags in all current passes, and edit them
        for expPass in export.passes:
            passTag = expPass.tags[export.tags_index]
            passTag.name = tag_name

    return None


def DrawAnimationWarning(self, context):
        layout = self.layout
        layout.label(text="Hey!  The animation feature is currently experimental, and may result in")
        layout.label(text="objects being repositioned after exporting in the scene and in the FBX file.")
        layout.separator()
        layout.label(text="The animation features should work fine if you're exporting armature animations,")
        layout.label(text="any other kinds of object animations are unlikely to export correctly, and if")
        layout.label(text="attempted you may find your scene translated slightly.  If this happens though")
        layout.label(text="simply use the undo tool.")
        layout.separator()


def CAP_Update_AnimationWarning(self, context):
    if self.export_animation_prev is False and self.export_animation is True:
        bpy.context.window_manager.popup_menu(DrawAnimationWarning, title="Animation Warning", icon='INFO')
    self.export_animation_prev = self.export_animation

class CAPSULE_ExportTag(PropertyGroup):
    # The main Export Tag collection property, used for storing the actual tags used in an Export Preset

    name: StringProperty(
        name="Tag Name",
        description="The name of the tag.",
        update=CAP_Update_TagName
        )

    name_filter: StringProperty(
        name="Tag",
        description="The text you wish to use as a filter, when sorting through object names."
        )

    name_filter_type: EnumProperty(
        name="Tag Type",
        description="Where the name filter is being looked for.",
        items=(
        ('1', 'Suffix', ''),
        ('2', 'Prefix', ''),),
        )

    object_type: EnumProperty(
        name="Object Type",
        items=(
            ('1', 'All', 'Applies to all object types.'),
            ('2', 'Mesh', 'Applies to mesh object types only.'),
            ('3', 'Curve', 'Applies to curve object types only.'),
            ('4', 'Surface', 'Applies to surface object types only.'),
            ('5', 'Metaball', 'Applies to metaball object types only.'),
            ('6', 'Font', 'Applies to font object types only.'),
            ('7', 'Armature', 'Applies to armature object types only.'),
            ('8', 'Lattice', 'Applies to lattice object types only.'),
            ('9', 'Empty', 'Applies to empty object types only.'),
            ('10', 'Camera', 'Applies to camera object types only.'),
            ('11', 'light', 'Applies to light object types only.'),
            ('12', 'Speaker', 'Applies to speaker object types only.')
            ),
        default='1'
        )

    # Special preferences for special export presets.
    x_user_deletable: BoolProperty(default=True)
    x_user_editable_type: BoolProperty(default=True)


class CAPSULE_ExportPassTag(PropertyGroup):
    # The Export Tag reference, used inside Export Passes to list the available tags.
    # Also specified for that pass, whether or not it is to be used.

    name: StringProperty(
        name="Tag Name",
        description="The name of the tag.",
        default=""
        )
    prev_name: StringProperty(
        name="Previous Tag Name",
        description="A backup tag name designed to prevent editing of tag names when viewing them. (Internal Only)",
        default=""
        )
    index: IntProperty(
        name="Tag Index",
        description="Where the tag is located in the Export Preset, so it can be looked up later (Internal Only)",
        default=0
        )
    use_tag: BoolProperty(
        name="",
        description="Determines whether or not the tag gets used in the pass.",
        default=False
        )

class CAPSULE_ExportPass(PropertyGroup):
    # Used to define properties for a single export pass.

    name: StringProperty(
        name="Pass Name",
        description="The name of the selected pass."
        )

    enable: BoolProperty(
        name="Enable Pass",
        description="Lets you enable or disable the pass for use when exporting objects.",
        default=True
    )

    file_suffix: StringProperty(
        name="File Suffix",
        description="An optional string that if used, will be appended to all the names of files produced through this pass."
        )
    sub_directory: StringProperty(
        name="Sub-Directory",
        description="If enabled, a folder will be created inside the currently defined file path (and any other defined folders for the File Preset), where all exports from this pass will be placed into."
        )

    tags: CollectionProperty(type=CAPSULE_ExportPassTag)
    tags_index: IntProperty(default=0)

    export_individual: BoolProperty(
        name="Export Individual",
        description="If enabled, the pass will export every individual object available in the pass into individual files, rather than a single file.",
        default=False
        )

    export_animation: BoolProperty(
        name="Export Animation",
        description="(EXPERIMENTAL) If ticked, animations found in objects or collections in this pass, will be exported.",
        default=False,
        update=CAP_Update_AnimationWarning
        )
    export_animation_prev: BoolProperty(default=False)

    apply_modifiers: BoolProperty(
        name="Apply Modifiers",
        description="If enabled, all modifiers on every object in the pass will be applied.",
        default=False
        )

    triangulate: BoolProperty(
        name="Triangulate Export",
        description="If enabled, all objects in the pass will be triangulated automatically using optimal triangulation settings, unless a Triangulation modifier is already present.",
        default=False
        )

    use_tags_on_objects: BoolProperty(
        name="Use Tags for Objects",
        description="If enabled, active tag filters will also apply to any single-object exports in this pass.\n\nAny other objects with matching names and valid, enabled tags will then be included in the export for this pass.",
        default=False
        )

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

    use_blend_directory: BoolProperty(
        name="Add Blend File Directory",
        description="If enabled, a folder will be created inside the currently defined file path, where all exports from this blend file will be placed into.  \n\nUseful for exporting multiple .blend file contents to the same location.",
        default=False
        )

    use_sub_directory: BoolProperty(
        name="Add Object Directory",
        description="If enabled, a folder will be created inside the currently defined file path (and inside the Blend Folder if enabled), for every object or collection created, where it's export results will be placed into.  \n\nUseful for organising complex object or collection exports, with multiple passes.",
        default=False
        )

    filter_render: BoolProperty(
        name="Filter by Rendering",
        description="Will use the Hide Render option on objects (viewable in the Outliner) to filter whether or not an object can be exported.  If the object is hidden from the render, it will not export regardless of any other settings in this plugin."
        )

    # Currently disabled until further notice due to reliability issues.
    reset_rotation: BoolProperty(
        name="Reset Rotation",
        description="If enabled, the plugin will reset the rotation of objects and collections when exported.  For collections, they will be reset depending on the rotation of the root object, so make sure that aligns with how you wish the rotation of a collection to be reset.  \n\nCurrently this doesn't work with rotation-influencing constraints, and will be disabled on objects and collection that use them.",
        default=False
        )

    preserve_armature_constraints: BoolProperty(
        name="Preserve Armature Constraints",
        description="(Experimental Feature) If enabled, Capsule will not mute specific bone constraints during the export process.  \n\nTurn this on if you rely on bone constraints for animation, but if you also need to change the origin point of these armatures, then the plugin may not succeed in doing this.",
        default=True
        )


    passes: CollectionProperty(type=CAPSULE_ExportPass)
    passes_index: IntProperty(default=0)
    tags: CollectionProperty(type=CAPSULE_ExportTag)
    tags_index: IntProperty(default=0)

    format_type: EnumProperty(
        name="Format Type",
        items=
            (
            ('FBX', "FBX", "Export assets in the FBX file format.  Ideal for 3D game engines."),
            ('OBJ', "OBJ", "Export assets in the OBJ file format.  Ideal for simple objects and older software compatibility."),
            ('GLTF', "GLTF", "Export assets in the GLTF file format."),
            ('Alembic', "Alembic", "Export assets in the Alembic file format.  Ideal for moving assets between 3D modelling programs."),
            ('Collada', "Collada", "Export assets in the Collada file format.  Ideal for moving assets between 3D modelling programs."),
            ('STL', "STL", "Export assets as STL files.  Ideal for 3D printing applications."),
            ),
        description="Defines what file type objects with this preset will export to and the export options available for this preset.",
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

    # A special system variable that defines whether it can be deleted from the Global Presets list.
    x_global_user_deletable: BoolProperty(default=True)


class CAPSULE_LocationDefault(PropertyGroup):
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


class CAPSULE_ExportPresets(PropertyGroup):
    """
    A property group passed onto the "default datablock", the empty object created in a blend file to store all the available export presets.
    """

    # the version of Capsule this datablock was created with
    version_number: FloatProperty(default=1.10)

    # the available file presets
    file_presets: CollectionProperty(type=CAPSULE_ExportPreset)

    # the preset selected on the list panel, when viewed from the AddonPreferences window.
    file_presets_listindex: IntProperty(default=0)

    # if true, this object is the empty created for the purposes of storing preset data.
    is_storage_object: BoolProperty(default=False)

    # the available location presets created by the user
    location_presets: CollectionProperty(type=CAPSULE_LocationDefault)

    # the location selected on the Locations panel, inside the 3D view
    location_presets_listindex: IntProperty(default=0)

    fbx_menu_options: EnumProperty(
        name="Export Options",
        description="",
        items=(
        ('Export', 'Export', 'A tab containing additional export paramaters exclusive to Capsule.'),
        ('Transform', 'Transform', 'A tab containing options to how objects are scaled and orientated in the export.'),
        ('Geometry', 'Geometry', 'A tab containing options for how object geometry is interpreted in the export.'),
        ('Armature', 'Armature', 'A tab containing options for how armature objects are interpreted in the export.'),
        ('Animation', 'Animation', 'A tab containing options for how animations are interpreted and used in the export.')
        ),
    )

    obj_menu_options: EnumProperty(
        name="Export Options",
        description="",
        items=(
        ('Export', 'Export', 'A tab containing general export paramaters.'),
        ('Transform', 'Transform', 'A tab containing options to how objects are scaled and orientated in the export.'),
        ('Object', 'Geometry', 'A tab containing options for how object geometry, materials and other associated assets are exported.'),
        ),
    )

    gltf_menu_options: EnumProperty(
        name="Export Options",
        description="",
        items=(
        ('Export', 'Export', 'A tab containing general export paramaters.'),
        ('Transform', 'Transform', 'A tab containing options to how objects are scaled and orientated in the export.'),
        ('Object', 'Attributes', 'A tab containing options for how object geometry and mesh-related assets are exported.'),
        ('Animation', 'Animation', 'A tab containing options for how object geometry and mesh-related assets are exported.'),
        ),
    )

    alembic_menu_options: EnumProperty(
        name="Export Options",
        description="",
        items=(
        ('Scene', 'Scene', 'A tab containing general scene paramaters.'),
        ('Object', 'Object', 'A tab containing options for how object geometry and mesh-related assets are exported.'),
        ('Particles', 'Particles', 'A tab containing options for how particles are exported.'),
        ),
    )

    collada_menu_options: EnumProperty(
        name="Export Options",
        description="",
        items=(
        ('Main', 'Main', 'A tab containing general export paramaters.'),
        ('Object', 'Object', 'A tab containing options for how object geometry and mesh-related assets are exported.'),
        ('Animation', 'Animation', 'A tab containing options for how animations and armatures are exported.'),
        ),
    )

# ////////////////////// - CLASS REGISTRATION - ////////////////////////
# decided to do it all in __init__ instead, skipping for now.

# classes = (
#     CAPSULE_ExportTag, 
#     CAPSULE_ExportPassTag, 
#     CAPSULE_ExportPass, 
#     CAPSULE_ExportPreset, 
#     CAPSULE_LocationDefault, 
#     CAPSULE_ExportPresets,
# )

# def register():
#     export_formats.register()
#     for cls in classes:
#         bpy.utils.register_class(cls)


# def unregister():
#     for cls in reversed(classes):
#         bpy.utils.unregister_class(cls)

#     export_formats.unregister()
