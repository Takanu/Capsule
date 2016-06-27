# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 3
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
# ##### END GPL LICENSE BLOCK #####

#This states the metadata for the plugin
bl_info = {
    "name": "Capsule",
    "author": "Crocadillian (BA) / Takanu (GitHub), special thanks to Acidhawk and Asahd <3",
    "version": (1, 0, 1),
    "blender": (2, 7, 7),
    "location": "3D View > Object Mode > Tools > Capsule",
    "wiki_url": "https://github.com/Takanu/Capsule",
    "description": "Provides tools for batch exporting objects from Blender using FBX.",
    "tracker_url": "",
    "category": "Import-Export"
}

# Start importing all the addon files
# The init file just gets things started, no code needs to be placed here.
import bpy
from . import definitions
from . import properties
from . import user_interface
from . import export_operators
from . import ui_operators
from . import update
from bpy.props import IntProperty, FloatProperty, BoolProperty, StringProperty, PointerProperty, CollectionProperty, EnumProperty
from bpy.types import AddonPreferences, PropertyGroup
from bpy.app.handlers import persistent

print("Checking modules...")

if "bpy" in locals():
    import imp
    print("------------------Reloading Plugin------------------")
    if "definitions" in locals():
        imp.reload(definitions)
    if "properties" in locals():
        imp.reload(properties)
    if "user_interface" in locals():
        imp.reload(user_interface)
    if "export_operators" in locals():
        imp.reload(export_operators)
    if "ui_operators" in locals():
        imp.reload(ui_operators)
    if "update" in locals():
        imp.reload(update)

print("Importing modules...")


def Update_TagName(self, context):

    user_preferences = context.user_preferences
    addon_prefs = user_preferences.addons[__package__].preferences

    if addon_prefs.plugin_is_ready is True:
        exp = bpy.data.objects[addon_prefs.default_datablock].CAPExp
        currentTag = exp.tags[exp.tags_index]
        tag_name = currentTag.name

        # Get tags in all current passes, and edit them
        for expPass in export.passes:
            passTag = expPass.tags[export.tags_index]
            passTag.name = tag_name

    return None

def GetGlobalPresets(scene, context):

    items = [
        ("0", "None",  "", 0),
        ]

    user_preferences = context.user_preferences
    addon_prefs = user_preferences.addons[__package__].preferences
    exp = addon_prefs.saved_presets

    u = 1

    for i,x in enumerate(exp):
        items.append((str(i+1), x.name, x.description, i+1))

    return items

def UpdateObjectSelectMode(self, context):

    if self.object_multi_edit is True:
        context.scene.CAPScn.object_list_index = -1

def UpdateGroupSelectMode(self, context):

    if self.group_multi_edit is True:
        context.scene.CAPScn.group_list_index = -1

def DrawAnimationWarning(self, context):
        layout = self.layout
        layout.label("Hey!  The animation feature is currently experimental, and may result in")
        layout.label("objects being repositioned after exporting, and in the FBX file.")
        layout.separator()
        layout.label("The animation features should work fine if you're exporting armature animations,")
        layout.label("any other kinds of object animations are unlikely to export correctly, and if")
        layout.label("attempted, you may find your scene translated slightly.  If this happens though,")
        layout.label("simply use the undo tool.")
        layout.separator()
        layout.label("Hopefully i'll have this fully functional in the next version :)")

def Update_AnimationWarning(self, context):
    if self.export_animation_prev is False and self.export_animation is True:
        bpy.context.window_manager.popup_menu(DrawAnimationWarning, title="Animation Warning", icon='INFO')
    self.export_animation_prev = self.export_animation

class CAP_ExportTag(PropertyGroup):
    # The main Export Tag collection property, used for storing the actual tags used in an Export Preset

    name = StringProperty(
        name="Tag Name",
        description="The name of the tag.",
        update=Update_TagName
        )

    name_filter = StringProperty(
        name="Tag",
        description="The text you wish to use as a filter, when sorting through object names."
        )

    name_filter_type = EnumProperty(
        name="Tag Type",
        description="Where the name filter is being looked for.",
        items=(
        ('1', 'Suffix', ''),
        ('2', 'Prefix', ''),),
        )

    object_type = EnumProperty(
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
            ('11', 'Lamp', 'Applies to lamp object types only.'),
            ('12', 'Speaker', 'Applies to speaker object types only.')
            ),
        default='1'
        )

    # Special preferences for special export presets.
    x_user_deletable = BoolProperty(default=True)
    x_user_editable_type = BoolProperty(default=True)

    # Special preference to rename objects during export, to make UE4/Unity export more seamless.
    x_ue4_collision_naming = BoolProperty(default=False)

class CAP_ExportPassTag(PropertyGroup):
    # The Export Tag reference, used inside Export Passes to list the available tags.
    # Also specified for that pass, whether or not it is to be used.

    name = StringProperty(
        name="Tag Name",
        description="The name of the tag.",
        default=""
        )
    prev_name = StringProperty(
        name="Previous Tag Name",
        description="A backup tag name designed to prevent editing of tag names when viewing them. (Internal Only)",
        default=""
        )
    index = IntProperty(
        name="Tag Index",
        description="Where the tag is located in the Export Preset, so it can be looked up later (Internal Only)",
        default=0
        )
    use_tag = BoolProperty(
        name="",
        description="Determines whether or not the tag gets used in the pass.",
        default=False
        )

class CAP_ExportPass(PropertyGroup):

    name = StringProperty(
        name="Pass Name",
        description="The name of the selected pass."
        )
    file_suffix = StringProperty(
        name="File Suffix",
        description="An optional string that if used, will be appended to all the names of files produced through this pass."
        )
    sub_directory = StringProperty(
        name="Sub-Directory",
        description="If enabled, a folder will be created inside the currently defined file path (and any other defined folders for the File Preset), where all exports from this pass will be placed into."
        )

    tags = CollectionProperty(type=CAP_ExportPassTag)
    tags_index = IntProperty(default=0)

    export_individual = BoolProperty(
        name="Export Individual",
        description="If enabled, the pass will export every individual object available in the pass into individual files, rather than a single file.",
        default=False
        )

    export_animation = BoolProperty(
        name="Export Animation",
        description="(EXPERIMENTAL) If ticked, animations found in objects or groups in this pass, will be exported.",
        default=False,
        update=Update_AnimationWarning
        )
    export_animation_prev = BoolProperty(default=False)

    apply_modifiers = BoolProperty(
        name="Apply Modifiers",
        description="If enabled, all modifiers on every object in the pass will be applied.",
        default=False
        )

    triangulate = BoolProperty(
        name="Triangulate Export",
        description="If enabled, all objects in the pass will be triangulated automatically using optimal triangulation settings, unless a Triangulation modifier is already present.",
        default=False
        )

    use_tags_on_objects = BoolProperty(
        name="Use Tags for Objects",
        description="If enabled, active tag filters will also apply to any single-object exports in this pass, as well as those in the scene that share the same name - which will also be exported with it.",
        default=False
        )

class CAP_ExportPreset(PropertyGroup):
    name = StringProperty(
        name = "Preset Name",
        description="The name of the export preset.",
        default=""
        )

    description = StringProperty(
        name = "Description",
        description="(Internal Use Only) TBA",
        default=""
        )

    use_blend_directory = BoolProperty(
        name="Add Blend File Directory",
        description="If enabled, a folder will be created inside the currently defined file path, where all exports from this blend file will be placed into.  Useful for exporting multiple .blend file contents to the same destination.",
        default=False
        )

    use_sub_directory = BoolProperty(
        name="Add Object Directory",
        description="If enabled, a folder will be created inside the currently defined file path (and inside the Blend Folder if enabled), for every object or group created, where it's export results will be placed into.  Useful for complex object or group exports, with multiple passes.",
        default=False
        )

    bundle_textures = BoolProperty(
        name="Bundle Textures",
        description="If enabled, allows any textures that are packed in the .blend file and applied to an object or group that's tagged for export, to be bundled with it inside the FBX file.",
        default=False
        )

    filter_render = BoolProperty(
        name="Filter by Rendering",
        description="Will use the Hide Render option on objects (viewable in the Outliner) to filter whether or not an object can be exported.  If the object is hidden from the render, it will not export regardless of any other settings in this plugin."
        )

    export_types = EnumProperty(
        name="Object Types",
        options={'ENUM_FLAG'},
        items=(('MESH', "Mesh", ""),
            ('ARMATURE', "Armature", ""),
            ('CAMERA', "Camera", ""),
            ('LAMP', "Lamp", ""),
            ('EMPTY', "Empty", ""),
            ('OTHER', "Other", "Includes other mesh types like Curves and Metaballs, which are converted to meshes on export"),),
        description="Defines what kinds of objects will be exported by the FBX exporter, regardless of any other options in Capsule.",
        default={'EMPTY', 'CAMERA', 'LAMP', 'ARMATURE', 'MESH', 'OTHER'},
        )


    passes = CollectionProperty(type=CAP_ExportPass)
    passes_index = IntProperty(default=0)
    tags = CollectionProperty(type=CAP_ExportTag)
    tags_index = IntProperty(default=0)

    global_scale = FloatProperty(
        name="Global Scale",
        description="The exported scale of the objects.",
        default=1.0
        )

    bake_space_transform = BoolProperty(
        name="Bake Space Transform (Experimental)",
        description="Bakes the space transform of meshes from Blender into the FBX file, when the target world space does not align with the one Blender has. (WARNING - Known broken on armatures/animations, use at your own peril!)",
        default=False
        )

    reset_rotation = BoolProperty(
        name="Reset Rotation",
        description="If enabled, the plugin will reset the rotation of objects and groups when exported.  For groups, they will be reset depending on the rotation of the root object, so make sure that aligns with how you wish the rotation of a group to be reset.  Currently this doesn't work with rotation-influencing constraints, and will be disabled on Objects and Groups that use them.",
        default=False
        )


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

    apply_unit_scale = BoolProperty(
        name="Apply Unit Scale",
        description="Scales the Blender Units system to match the FBX unit measurement (centimetres).",
        default=False
        )

    loose_edges = BoolProperty(
        name="Loose Edges",
        description="Makes any separate edges a two-verted polygon.",
        default=False
        )

    tangent_space = BoolProperty(
        name="Tangent Space",
        description="Exports the mesh tangent vectors,  This option will only work on objects with no n-gons (faces with more than 4 vertices), so please check beforehand!",
        default=False
        )

    use_armature_deform_only = BoolProperty(
        name="Only Include Deform Bones",
        description="Makes any separate edges a two-verted polygon.",
        default=False
        )

    add_leaf_bones = BoolProperty(
        name="Add Leaf Bones",
        description="Appends an extra bone to the end of each bone chain.",
        default=False
        )

    preserve_armature_constraints = BoolProperty(
        name="Preserve Armature Constraints",
        description="(Experimental Feature) If enabled, Capsule will not mute specific bone constraints during the export process.  Turn this on if you rely on bone constraints for animation, but if you also need to change the origin point of these armatures, then the plugin may not succeed in doing this.",
        default=True
        )


    primary_bone_axis = EnumProperty(
        name="Primary Bone Axis",
        description="Defines the primary bone axis for the export.",
        items=(
            ('X', 'X', ''),
            ('Y', 'Y', ''),
            ('Z', 'Z', ''),
            ('-X', '-X', ''),
            ('-Y', '-Y', ''),
            ('-Z', '-Z', '')),
            default='Y'
            )

    secondary_bone_axis = EnumProperty(
        name="Secondary Bone Axis",
        description="Defines the secondary bone axis for the export.",
        items=(
            ('X', 'X', ''),
            ('Y', 'Y', ''),
            ('Z', 'Z', ''),
            ('-X', '-X', ''),
            ('-Y', '-Y', ''),
            ('-Z', '-Z', '')),
        default='X'
        )

    armature_nodetype = EnumProperty(
        name="FBX Armature NodeType",
        description="Defines the type of FBX object Armatures will be exported as.  Change this from Null if you're experiencing import problems in other apps, but picking anything other than null will not guarantee a successful re-import into Blender.",
        items=(
            ('Null', 'Null', ''),
            ('Root', 'Root', ''),
            ('LimbNode', 'LimbNode', ''))
            )


    bake_anim_use_all_bones = BoolProperty(
        name="Key All Bones",
        description="If enabled, this forces the export of one key animation for all bones (required for target apps like UE4).",
        default=False)

    bake_anim_use_nla_strips = BoolProperty(
        name="Use NLA Strips",
        description="If enabled, NLA strips will be exported as animation data.",
        default=False
        )

    bake_anim_use_all_actions = BoolProperty(
        name="Use All Actions",
        description="If enabled, all animation actions in the group or object will be exported.",
        default=False
        )

    bake_anim_force_startend_keying = BoolProperty(
        name="Start/End Keying",
        description="If enabled, this option fully keys the start and end positions of an animation.  Use this if the exported animations playback with incorrect starting positions.",
        default=False
        )

    use_default_take = BoolProperty(
        name="Use Default Take",
        description="If enabled, uses the currently viewed pose/translation of the object as a starting pose for exported animations (excluding certain keyframes).",
        default=False
        )

    optimise_keyframes = BoolProperty(
        name="Optimise Keyframes",
        description="If enabled, removes double keyframes from exported animations.",
        default=False
        )

    bake_anim_step = FloatProperty(
        name="Sampling Rate",
        description="Defines how often, in frames, the export process should evaluate keyframes.",
        default=1,
        min=0,
        max=100,
        soft_min=0.1,
        soft_max=10
        )

    bake_anim_simplify_factor = FloatProperty(
        name="Simplify Factor",
        description="A measure for how much when exported, animations should be simplified.  Setting this value to 0 will disable simplification.  The higher the value, the greater the simplification.",
        default=1,
        min=0,
        max=100,
        soft_min=0,
        soft_max=10
        )

    # A special system variable that defines whether it can be deleted from the Global Presets list.
    x_global_user_deletable = BoolProperty(default=True)
    # A secret fix embedded in the Unity 5 export option, to fix rotated objects.
    x_unity_rotation_fix = BoolProperty(default=False)

class CAP_LocationDefault(PropertyGroup):
    name = StringProperty(
        name="",
        description="The name of the file path default."
        )

    path = StringProperty(name="",
        description="The file path to export the object to.",
        default="",
        subtype="FILE_PATH"
        )

class CAP_ExportPresets(PropertyGroup):
    file_presets = CollectionProperty(type=CAP_ExportPreset)
    file_presets_index = IntProperty(default=0)
    is_storage_object = BoolProperty(default=False)

    location_presets = CollectionProperty(type=CAP_LocationDefault)
    location_presets_index = IntProperty(default=0)

class CAP_AddonPreferences(AddonPreferences):
    bl_idname = __name__

    # The name for the empty object that exists to store .blend file level Capsule data.
    default_datablock = StringProperty(
        name="Dummy Datablock Name",
        description="The dummy block being used to store Export Default and Location Default data, in order to enable the data to be used between scenes.",
        default=">Capsule Blend File Data<"
    )

    # Storage for the Global Presets, and it's enum UI list.
    sort_presets = CollectionProperty(type=CAP_ExportPreset)
    saved_presets = CollectionProperty(type=CAP_ExportPreset)
    saved_presets_index = IntProperty()

    saved_presets_dropdown = BoolProperty(default=False)
    presets_dropdown = BoolProperty(default = False)
    tags_dropdown = BoolProperty(default = False)
    passes_dropdown = BoolProperty(default = False)
    options_dropdown = BoolProperty(default = False)

    export_preset_options = EnumProperty(
        name="Export Options",
        description="",
        items=(
        ('Export', 'Export', 'A tab containing additional export paramaters exclusive to Capsule.'),
        ('Transform', 'Transform', 'A tab containing options to how objects are scaled and orientated in the export.'),
        ('Geometry', 'Geometry', 'A tab containing options for how object geometry is interpreted in the export.'),
        ('Armature', 'Armature', 'A tab containing options for how armature objects are interpreted in the export.'),
        ('Animation', 'Animation', 'A tab containing options for how animations are interpreted and used in the export.')
        ),)

    object_multi_edit = BoolProperty(
        name="Group Multi-Edit Mode",
        description="Allows you to edit export settings for all objects that the currently selected.  Turning this option off will let you edit the currently selected object on the list.",
        default=True,
        update=UpdateObjectSelectMode
        )

    group_multi_edit = BoolProperty(
        name="Group Multi-Edit Mode",
        description="Allows you to edit export settings for all groups that the currently selected objects belong to.  WARNING - One object can belong to multiple groups, please be careful when using this mode.",
        default=False,
        update=UpdateGroupSelectMode
        )

    object_list_autorefresh = BoolProperty(
        name="Object List Auto-Refresh",
        description="Determines whether or not an object on the object export list will automatically be removed when Enable Export is unticked.  If this option is disabled, a manual refresh button will appear next to the list."
        )

    list_feature = EnumProperty(
        name="Additional List Features",
        description="Allows for the customisation of a secondary button next to each Object and Group Export list entry.",
        items=(
            ('none', 'None', 'No extra option will be added to the list'),
            ('sel', 'Select', 'Adds an option next to a list entry that allows you to select that Object or Group in the 3D View.'),
            ('focus', 'Focus', 'Adds an option next to a list entry that allows you to select and focus the 3D view on that Object or Group.')),
        default='focus'
        )

    substitute_directories = BoolProperty(
        name="Substitute Invalid Folder Characters",
        description="If any of your export directories contain invalid characters for the operating system you currently use, ticking this on will substitute them with an underscore.  If unticked, the plugin will prompt you with an error if your directories contain invalid characters.",
        default=True
        )

    data_missing = BoolProperty(default=False)
    plugin_is_ready = BoolProperty(default=False)
    prev_selected_object = StringProperty()
    prev_selected_count = IntProperty()

    def draw(self, context):
        layout = self.layout

        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__name__].preferences
        exp = None

        # UI Prompt for when the .blend Capsule data can no longer be found.
        try:
            exp = bpy.data.objects[addon_prefs.default_datablock].CAPExp
        except KeyError:
            layout = self.layout
            col_export = layout.column(align=True)
            col_export.label("No Capsule for this .blend file has been found,")
            col_export.label("Please press the button below to generate new data.")
            col_export.separator()
            col_export.separator()
            col_export.operator("cap.exportdata_create")
            col_export.separator()
            return

        scn = context.scene.CAPScn
        ob = context.object

        #---------------------------------------------------------
        # Export UI
        #---------------------------------------------------------
        export_box = layout.box()
        col_export_title = export_box.row(align=True)

        if addon_prefs.presets_dropdown is False:
            col_export_title.prop(addon_prefs, "presets_dropdown", text="", icon='TRIA_RIGHT', emboss=False)
            #col_export_title.operator("cap_tutorial.tags", text="", icon='INFO')
            col_export_title.label("Export Presets")


        else:
            col_export_title.prop(addon_prefs, "presets_dropdown", text="", icon='TRIA_DOWN', emboss=False)
            #col_export_title.operator("cap_tutorial.tags", text="", icon='INFO')
            col_export_title.label("Export Presets")

            if addon_prefs.saved_presets_dropdown is False:
                savedpresets_box = export_box.box()
                col_saved_title = savedpresets_box.row(align=True)
                col_saved_title.prop(addon_prefs, "saved_presets_dropdown", text="", icon='TRIA_RIGHT', emboss=False)
                col_saved_title.label("Saved Presets")

            else:
                savedpresets_box = export_box.box()
                col_saved_title = savedpresets_box.row(align=True)
                col_saved_title.prop(addon_prefs, "saved_presets_dropdown", text="", icon='TRIA_DOWN', emboss=False)
                col_saved_title.label("Saved Presets")

                col_savedpresets = savedpresets_box.row(align=True)
                col_savedpresets_list = col_savedpresets.column(align=True)
                col_savedpresets_list.template_list("Saved_Default_UIList", "default", addon_prefs, "saved_presets", addon_prefs, "saved_presets_index", rows=3, maxrows=6)
                col_savedpresets_list.operator("cap.create_current_preset", text="Add to File Presets", icon="FORWARD")

                col_savedpresets_options = col_savedpresets.column(align=True)
                col_savedpresets_options.operator("cap.delete_global_preset", text="", icon="ZOOMOUT")


            filepresets_box = export_box.box()
            filepresets_box.label("File Presets")

            row_defaults = filepresets_box.row(align=True)
            col_defaultslist = row_defaults.column(align=True)
            col_defaultslist.template_list("Export_Default_UIList", "default", exp, "file_presets", exp, "file_presets_index", rows=3, maxrows=6)
            col_defaultslist.operator("cap.add_global_preset", text="Add to Saved Presets", icon="FORWARD")

            col_defaultslist_options = row_defaults.column(align=True)
            col_defaultslist_options.operator("scene.cap_addexport", text="", icon="ZOOMIN")
            col_defaultslist_options.operator("scene.cap_deleteexport", text="", icon="ZOOMOUT")


            if len(exp.file_presets) > 0 and (exp.file_presets_index) < len(exp.file_presets):

                currentExp = exp.file_presets[exp.file_presets_index]

                export_settings = filepresets_box.column(align=True)
                export_settings.separator()
                export_tabs = export_settings.row(align=True)
                export_tabs.prop(addon_prefs, "export_preset_options", expand=True)

                export_separator = filepresets_box.column(align=True)
                #export_separator.separator()


                if addon_prefs.export_preset_options == 'Export':
                    export_main = filepresets_box.row(align=True)
                    export_main.separator()

                    export_1 = export_main.column(align=True)
                    export_1.label("Additional Options")
                    export_1.separator()
                    export_1.prop(currentExp, "use_blend_directory")
                    export_1.prop(currentExp, "use_sub_directory")
                    export_1.prop(currentExp, "filter_render")
                    export_1.prop(currentExp, "bundle_textures")

                    export_main.separator()
                    export_main.separator()
                    export_main.separator()

                    export_2 = export_main.column(align=True)
                    export_2.label("Exportable Object Types")
                    export_2.separator()
                    #export_types = export_1.row(align=True)
                    export_2.prop(currentExp, "export_types")
                    export_2.separator()

                    export_main.separator()

                if addon_prefs.export_preset_options == 'Transform':
                    export_main = filepresets_box.row(align=True)
                    export_main.separator()

                    export_1 = export_main.column(align=True)
                    export_scale = export_1.row(align=True)
                    export_scale.prop(currentExp, "global_scale")
                    export_scale.prop(currentExp, "apply_unit_scale", text="", icon='NDOF_TRANS')
                    export_1.separator()

                    export_1.prop(currentExp, "bake_space_transform")
                    #export_1.prop(currentExp, "reset_rotation")

                    export_1.separator()


                    export_main.separator()
                    export_main.separator()
                    export_main.separator()

                    export_2 = export_main.column(align=True)
                    export_2_row = export_2.row(align=True)
                    export_2_row.alignment = 'RIGHT'

                    export_2_label = export_2_row.column(align=True)
                    export_2_label.alignment = 'RIGHT'
                    export_2_label.label("Axis Up:")
                    export_2_label.label("Axis Forward:")

                    export_2_dropdowns = export_2_row.column(align=True)
                    export_2_dropdowns.alignment = 'EXPAND'
                    export_2_dropdowns.prop(currentExp, "axis_up", text="")
                    export_2_dropdowns.prop(currentExp, "axis_forward", text="")
                    export_2_dropdowns.separator()

                    export_main.separator()

                elif addon_prefs.export_preset_options == 'Geometry':
                    export_main = filepresets_box.row(align=True)
                    export_main.separator()
                    export_1 = export_main.column(align=True)
                    export_1.prop(currentExp, "loose_edges")
                    export_1.prop(currentExp, "tangent_space")
                    export_1.separator()

                elif addon_prefs.export_preset_options == 'Armature':
                    export_main = filepresets_box.row(align=True)
                    export_main.separator()
                    export_1 = export_main.column(align=True)
                    export_1.prop(currentExp, "use_armature_deform_only")
                    export_1.prop(currentExp, "add_leaf_bones")
                    export_1.prop(currentExp, "preserve_armature_constraints")

                    export_main.separator()
                    export_main.separator()
                    export_main.separator()

                    export_2 = export_main.row(align=True)
                    export_2.alignment = 'RIGHT'
                    export_2_label = export_2.column(align=True)
                    export_2_label.alignment = 'RIGHT'
                    export_2_label.label("Primary Bone Axis:")
                    export_2_label.label("Secondary Bone Axis:")
                    export_2_label.label("Armature Node Type:")

                    export_2_dropdowns = export_2.column(align=True)
                    export_2_dropdowns.alignment = 'EXPAND'
                    export_2_dropdowns.prop(currentExp, "primary_bone_axis", text="")
                    export_2_dropdowns.prop(currentExp, "secondary_bone_axis", text="")
                    export_2_dropdowns.prop(currentExp, "armature_nodetype", text="")
                    export_2_dropdowns.separator()

                    export_main.separator()

                elif addon_prefs.export_preset_options == 'Animation':
                    export_main = filepresets_box.row(align=True)
                    export_main.separator()

                    export_1 = export_main.column(align=True)
                    export_1.prop(currentExp, "bake_anim_use_all_bones")
                    export_1.prop(currentExp, "bake_anim_use_nla_strips")
                    export_1.prop(currentExp, "bake_anim_use_all_actions")
                    export_1.prop(currentExp, "bake_anim_force_startend_keying")
                    export_1.prop(currentExp, "optimise_keyframes")
                    export_1.prop(currentExp, "use_default_take")
                    export_1.separator()

                    export_main.separator()
                    export_main.separator()
                    export_main.separator()

                    export_2 = export_main.column(align=True)
                    export_2.prop(currentExp, "bake_anim_step")
                    export_2.prop(currentExp, "bake_anim_simplify_factor")
                    export_2.separator()

                    export_main.separator()

            else:
                preset_unselected = filepresets_box.column(align=True)
                preset_unselected.label("Select a preset in order to view preset settings.")
                preset_unselected.separator()


        #---------------------------------------------------------
        # Tags UI
        #---------------------------------------------------------
        tag_box = layout.box()
        tag_title = tag_box.row(align=True)

        if addon_prefs.tags_dropdown is False:
            tag_title.prop(addon_prefs, "tags_dropdown", text="", icon='TRIA_RIGHT', emboss=False)
            tag_title.label("Tags")

        else:
            tag_title.prop(addon_prefs, "tags_dropdown", text="", icon='TRIA_DOWN', emboss=False)
            tag_title.label("Tags")

            if len(exp.file_presets) > 0 and (exp.file_presets_index) < len(exp.file_presets):

                currentExp = exp.file_presets[exp.file_presets_index]

                tagUI_row = tag_box.row(align=True)
                tagUI_row.template_list("Tag_Default_UIList", "default", currentExp, "tags", currentExp, "tags_index", rows=3, maxrows=6)

                tagUI_col = tagUI_row.column(align=True)
                tagUI_col.operator("scene.cap_addtag", text="", icon="ZOOMIN")
                tagUI_col.operator("scene.cap_deletetag", text="", icon="ZOOMOUT")
                tagUI_col.separator()

                tag_settings = tag_box.column(align=True)
                tag_settings.separator()

                if len(currentExp.tags) == 0:
                    tag_settings.label("Create a new tag in order to view and edit tag settings.")
                    tag_settings.separator()

                else:
                    currentTag = currentExp.tags[currentExp.tags_index]
                    tag_settings.prop(currentTag, "name_filter")
                    tag_settings.prop(currentTag, "name_filter_type")

                    toggle_settings = tag_settings.column(align=True)
                    toggle_settings.prop(currentTag, "object_type")

                    if currentTag.x_user_editable_type is False:
                        toggle_settings.enabled = False

            else:
                unselected = tag_box.column(align=True)
                unselected.label("Select a preset in order to view tag settings.")
                unselected.separator()

        #---------------------------------------------------------
        # Pass UI
        #---------------------------------------------------------
        pass_box = layout.box()
        passUI = pass_box.row(align=True)

        if addon_prefs.passes_dropdown is False:
            passUI.prop(addon_prefs, "passes_dropdown", text="", icon='TRIA_RIGHT', emboss=False)
            passUI.label("Passes")

        else:
            passUI.prop(addon_prefs, "passes_dropdown", text="", icon='TRIA_DOWN', emboss=False)
            passUI.label("Passes")


            if len(exp.file_presets) > 0 and (exp.file_presets_index) < len(exp.file_presets):

                currentExp = exp.file_presets[exp.file_presets_index]

                row_passes = pass_box.row(align=True)
                row_passes.template_list("Pass_Default_UIList", "default", currentExp, "passes", currentExp, "passes_index", rows=3, maxrows=6)

                row_passes.separator()

                col_passes = row_passes.column(align=True)
                col_passes.operator("scene.cap_addpass", text="", icon="ZOOMIN")
                col_passes.operator("scene.cap_deletepass", text="", icon="ZOOMOUT")
                col_passes.separator()


                pass_settings = pass_box.column(align=True)
                pass_settings.separator()

                if len(currentExp.passes) == 0:
                    pass_settings.label("Create a new pass in order to view and edit pass settings.")
                    pass_settings.separator()

                else:

                    # Pass Options UI
                    currentPass = currentExp.passes[currentExp.passes_index]

                    pass_settings.prop(currentPass, "file_suffix")
                    pass_settings.prop(currentPass, "sub_directory")
                    pass_settings.separator()
                    pass_settings.separator()

                    pass_options = pass_settings.row(align=True)
                    pass_options.separator()

                    # Additional Export Options
                    options_ui = pass_options.column(align=True)
                    options_ui.label(text="Export Options")

                    options_ui.separator()
                    options_ui.prop(currentPass, "export_animation")
                    options_ui.prop(currentPass, "apply_modifiers")
                    options_ui.prop(currentPass, "triangulate")
                    options_ui.prop(currentPass, "export_individual")
                    options_ui.separator()

                    pass_options.separator()
                    pass_options.separator()
                    pass_options.separator()

                    # Tag Filters
                    tag_filter = pass_options.column(align=True)
                    tag_filter.label(text="Filter by Tag")
                    tag_filter.separator()

                    for passTag in currentPass.tags:
                        tag_column = tag_filter.column(align=True)
                        tag_column.prop(passTag, "use_tag", text="Filter " + passTag.name)

                    tag_filter.separator()

                    # Tag Options
                    tag_options = pass_options.column(align=True)
                    tag_options.label(text="Tag Options")
                    tag_options.separator()

                    tag_options.prop(currentPass, "use_tags_on_objects")
                    tag_options.separator()

            else:
                unselected = pass_box.column(align=True)
                unselected.label("Select a preset in order to view tag settings.")
                unselected.separator()

        #---------------------------------------------------------
        # Options
        #---------------------------------------------------------
        options_box = layout.box()
        optionsUI = options_box.row(align=True)

        if addon_prefs.options_dropdown is False:
            optionsUI.prop(addon_prefs, "options_dropdown", text="", icon='TRIA_RIGHT', emboss=False)
            optionsUI.label("Extra Settings")

        else:
            optionsUI.prop(addon_prefs, "options_dropdown", text="", icon='TRIA_DOWN', emboss=False)
            optionsUI.label("Extra Settings")
            options_main = options_box.row(align=True)
            options_main.separator()

            options_1 = options_main.column(align=False)
            #options_1.alignment = 'CENTER'
            options_1.label("Additional List Options")
            options_1.separator()
            options_1.prop(addon_prefs, "list_feature", text="", expand=False)
            options_1.separator()
            options_1.prop(addon_prefs, "substitute_directories", expand=False)

            options_main.separator()
            options_main.separator()
            options_main.separator()
            options_main.separator()
            options_main.separator()

            options_2 = options_main.column(align=False)
            options_2.label("Reset")
            options_2.separator()
            options_2.operator("scene.cap_resetsceneprops", text="Reset Scene")
            options_2.separator()

            options_main.separator()

@persistent
def CreateDefaultData(scene):

    user_preferences = bpy.context.user_preferences
    addon_prefs = user_preferences.addons[__name__].preferences

    # Figure out if an object already exists, if yes do nothing
    for object in bpy.data.objects:
        print(object)
        if object.name == addon_prefs.default_datablock:
            return

    # Otherwise create the object using the addon preference data
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.empty_add(type='PLAIN_AXES')

    defaultDatablock = bpy.context.scene.objects.active
    defaultDatablock.name = addon_prefs.default_datablock
    defaultDatablock.hide = True
    defaultDatablock.hide_render = True
    defaultDatablock.hide_select = True
    defaultDatablock.CAPExp.is_storage_object = True

@persistent
def CheckSelectedObject(scene):

    user_preferences = bpy.context.user_preferences
    addon_prefs = user_preferences.addons[__name__].preferences
    #print("SCENE UPDATE")

    if bpy.context.active_object is not None:
        if bpy.context.active_object.name != addon_prefs.prev_selected_object:
            addon_prefs.object_multi_edit = True
            addon_prefs.group_multi_edit = True
            addon_prefs.prev_selected_object = bpy.context.active_object.name

    if len(bpy.context.selected_objects) != addon_prefs.prev_selected_count:
        addon_prefs.object_multi_edit = True
        addon_prefs.group_multi_edit = True
        addon_prefs.prev_selected_count = len(bpy.context.selected_objects)


def register():
    print("Registering Stuff")
    bpy.utils.register_module(__name__)

    bpy.types.Scene.CAPScn = PointerProperty(type=properties.CAP_Scene_Preferences)
    bpy.types.Object.CAPObj = PointerProperty(type=properties.CAP_Object_Preferences)
    bpy.types.Group.CAPGrp = PointerProperty(type=properties.CAP_Group_Preferences)
    bpy.types.Action.CAPAcn = PointerProperty(type=properties.CAP_Action_Preferences)
    bpy.types.Object.CAPStm = PointerProperty(type=properties.CAP_Object_StateMachine)
    bpy.types.Object.CAPExp = PointerProperty(type=CAP_ExportPresets)

    ui_operators.CreatePresets()

    bpy.app.handlers.load_pre.append(CreateDefaultData)
    bpy.app.handlers.scene_update_post.append(CheckSelectedObject)

def unregister():
    print("Unregistering Stuff")
    ui_operators.DeletePresets()

    bpy.app.handlers.load_pre.remove(CreateDefaultData)
    bpy.app.handlers.scene_update_post.remove(CheckSelectedObject)

    del bpy.types.Object.CAPExp
    del bpy.types.Scene.CAPScn
    del bpy.types.Object.CAPObj
    del bpy.types.Group.CAPGrp
    del bpy.types.Action.CAPAcn
    del bpy.types.Object.CAPStm

    bpy.utils.unregister_module(__name__)


# Only if i ever wanted to run the script in the text editor, which I don't
if __name__ == "__main__":
    register()
