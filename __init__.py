
#This states the metadata for the plugin
bl_info = {
    "name": "Capsule",
    "author": "Takanu Kyriako",
    "version": (1,0),
    "blender": (2, 7, 5),
    "location": "3D View > Object Mode > Tools > GEX",
    "wiki_url": "http://blenderartists.org/forum/showthread.php?373523-GEX-0-85-(15-11-2015)-One-Click-Batch-FBX-Exports",
    "description": "Provides tools for batch exporting objects from Blender using FBX.",
    "tracker_url": "",
    "category": "Import-Export"
}

# Start importing all the addon files
# The init file just gets things started, no code needs to be placed here.

if "bpy" in locals():
    import imp
    print("Reloading Plugin"*20)
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

def Update_TagName(self, context):

    user_preferences = context.user_preferences
    addon_prefs = user_preferences.addons[__package__].preferences
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
    exp = addon_prefs.global_presets

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


class CAP_ExportTag(PropertyGroup):
    # The main Export Tag collection property, used for storing the actual tags used in an Export Preset

    name = StringProperty(
        name="Tag Name",
        description="The name of the tag.",
        update=Update_TagName
        )

    name_filter = StringProperty(
        name="Tag",
        description="The string you wish to use as a tag when sorting through object names."
        )

    name_filter_type = EnumProperty(
        name="Tag Type",
        description="Where the tag is being placed in the object name.",
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
        description="The name of the tag...",
        default=""
        )
    prev_name = StringProperty(
        name="Previous Tag Name",
        description="A backup tag name designed to prevent editing of tag names when viewing them",
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
        description="The suffix added on the exported file created from this pass."
        )
    sub_directory = StringProperty(
        name="Sub-Directory",
        description="Export the pass to a new folder inside the chosen location default."
        )

    tags = CollectionProperty(type=CAP_ExportPassTag)
    tags_index = IntProperty(default=0)

    export_individual = BoolProperty(
        name="Export Individual",
        description="Exports every object in the pass into individual files, rather than a single file, as well as ensuring their .",
        default=False
        )

    export_animation = BoolProperty(
        name="Export Animation",
        description="Enables animations for this pass to be exported.",
        default=False
        )

    apply_modifiers = BoolProperty(
        name="Apply Modifiers",
        description="Applies all modifiers on every object in the pass",
        default=False
        )

    triangulate = BoolProperty(
        name="Triangulate Export",
        description="Triangulate objects in the pass on export using optimal triangulation settings.",
        default=False
        )

    object_use_tags = BoolProperty(
        name="(Object Only) Use All Tags",
        description="If enabling individual export, this option allows the inclusion of all tagged objects associated with a single object.",
        default=False
        )

class CAP_ExportPreset(PropertyGroup):
    name = StringProperty(
        name = "Default Name",
        description="The name of the export preset, whoda thunk :OO",
        default=""
        )

    description = StringProperty(
        name = "Description",
        description="(Internal Use Only)",
        default=""
        )

    use_blend_directory = BoolProperty(
        name="Add Blend Directory",
        description="Exports all objects from a .blend file, into a folder named after that .blend file.  Useful if you're exporting objects from multiple .blend files into one export folder, for additional, automated organisation.",
        default=False
        )

    use_sub_directory = BoolProperty(
        name="Add Object Directories",
        description="If ticked, every individual or group export will be placed in it's own folder inside the target location.  Any pass sub-directories will be contained inside these folders.",
        default=False
        )

    bundle_textures = BoolProperty(
        name="Bundle Textures",
        description="Allows any textures that are packed in the .blend file and applied to an object or group you're exporting, to be bundled with it inside the FBX file.",
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
                   ('OTHER', "Other", "Includes other mesh types like Curves and Metaballs, which are converted to meshes on export"),
                   ),
            description="Defines what kinds of objects will be exported by the FBX exporter, regardless of any other defined options in Capsule.",
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
        name="Bake Space Transform",
        description="Erm...",
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
        description="blablablabla",
        default=False
        )

    use_armature_deform_only = BoolProperty(
        name="Only Include Deform Bones",
        description="Makes any separate edges a two-verted polygon.",
        default=False
        )

    add_leaf_bones = BoolProperty(
        name="Add Leaf Bones",
        description="Append a bone to the end of each chain...",
        default=False
        )

    primary_bone_axis = EnumProperty(
        name="Primary Bone Axis",
        description="What the Forward Axis will be defined as when the model is exported.",
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
        description="What the Forward Axis will be defined as when the model is exported.",
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
        description="What the Forward Axis will be defined as when the model is exported.",
        items=(
            ('Null', 'Null', ''),
            ('Root', 'Root', ''),
            ('LimbNode', 'LimbNode', ''))
            )


    bake_anim_use_all_bones = BoolProperty(
        name="Use All Bones",
        description="Makes any separate edges a two-verted polygon.",
        default=False)

    bake_anim_use_nla_strips = BoolProperty(
        name="Use NLA Strips",
        description="Makes any separate edges a two-verted polygon.",
        default=False
        )

    bake_anim_use_all_actions = BoolProperty(
        name="Use All Actions",
        description="Makes any separate edges a two-verted polygon.",
        default=False
        )

    bake_anim_force_startend_keying = BoolProperty(
        name="Start/End Keying",
        description="Makes any separate edges a two-verted polygon.",
        default=False
        )

    use_default_take = BoolProperty(
        name="Use Default Take",
        description="Rawr?",
        default=False
        )

    optimise_keyframes = BoolProperty(
        name="Optimise Keyframes",
        description="Removes double keyframes.",
        default=False
        )

    bake_anim_step = FloatProperty(
        name="Sampling Rate",
        description="Blah",
        default=1,
        min=0,
        max=100,
        soft_min=0.1,
        soft_max=10
        )

    bake_anim_simplify_factor = FloatProperty(
        name="Simplify Factor",
        description="Blah",
        default=1,
        min=0,
        max=100,
        soft_min=0,
        soft_max=10
        )

    # A special system variable that defines whether it can be deleted from the Global Presets list.
    x_global_user_deletable = BoolProperty(default=True)

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
    export_defaults = CollectionProperty(type=CAP_ExportPreset)
    export_defaults_index = IntProperty(default=0)
    is_storage_object = BoolProperty(default=False)

    location_defaults = CollectionProperty(type=CAP_LocationDefault)
    location_defaults_index = IntProperty(default=0)

class CAP_AddonPreferences(AddonPreferences):
    bl_idname = __name__

    # The name for the empty object that exists to store .blend file level Capsule data.
    default_datablock = StringProperty(
        name="Dummy Datablock Name",
        description="The dummy block being used to store Export Default and Location Default data, in order to enable the data to be used between scenes.",
        default=">Capsule Blend File Data<"
    )

    # Storage for the Global Presets, and it's enum UI list.
    global_presets = CollectionProperty(type=CAP_ExportPreset)
    global_presets_enum = EnumProperty(
        name="Stored Export Presets",
        description="The export presets saved as plugin data, which can be accessed between .blend files.",
        items=GetGlobalPresets)

    presets_dropdown = BoolProperty(default = False)
    tags_dropdown = BoolProperty(default = False)
    passes_dropdown = BoolProperty(default = False)
    options_dropdown = BoolProperty(default = False)

    #global_presets_dropdown = EnumProperty(
        #name = "Export Options",
        #description = "",
        #items=GetGlobalPresets)

    export_preset_options = EnumProperty(
        name="Export Options",
        description="",
        items=(
        ('Export', 'Export', 'A tab containing additional export paramaters exclusive to Capsule.'),
        ('Transform', 'Transform', 'A tab containing options to how objects are scaled and orientated in the export.'),
        ('Geometry', 'Geometry', 'A tab containing options for how object geometry is interpreted in the export.'),
        ('Armature', 'Armature', 'A tab containing options for how armature objects are interpreted in the export.')
        #('Animation', 'Animation', 'A tab containing options for how animations are interpreted and used in the export.')
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
            ('sel', 'Select', 'Adds an option next to a list entry that allows you to select that Object or Group in the 3D View.'),
            ('focus', 'Focus', 'Adds an option next to a list entry that allows you to select and focus the 3D view on that Object or Group.')),
        default='focus'
        )

    data_missing = BoolProperty(default=False)
    prev_selected_object = StringProperty()

    def draw(self, context):
        layout = self.layout

        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__name__].preferences
        exp = None

        for item in bpy.data.objects:
            if item.name == addon_prefs.default_datablock:
                exp = bpy.data.objects[addon_prefs.default_datablock].CAPExp

        if exp is None:
            layout = self.layout
            col_export = layout.column(align=True)
            col_export.label("No Capsule for this .blend file has been found,")
            col_export.label("Please press the button below to generate new data.")
            col_export.separator()
            col_export.separator()
            col_export.operator("cap.exportdata_create")
            col_export.separator()
            addon_prefs.data_missing = True
            return


        scn = context.scene.CAPScn
        ob = context.object
        ui = context.scene.CAPUI

        #---------------------------------------------------------
        # Export UI
        #---------------------------------------------------------
        export_box = layout.box()
        col_export_title = export_box.row(align=True)

        if addon_prefs.presets_dropdown is False:
            col_export_title.prop(addon_prefs, "presets_dropdown", text="", icon='TRIA_RIGHT', emboss=False)
            #col_export_title.operator("cap_tutorial.tags", text="", icon='INFO')
            col_export_title.label("Export Defaults")
            col_export_title.operator("cap.create_current_preset", text="", icon="ZOOMIN")
            col_export_title.operator("cap.delete_global_preset", text="", icon="ZOOMOUT")
            col_export_title.prop(addon_prefs, "global_presets_enum", text="")


        else:
            col_export_title.prop(addon_prefs, "presets_dropdown", text="", icon='TRIA_DOWN', emboss=False)
            #col_export_title.operator("cap_tutorial.tags", text="", icon='INFO')
            col_export_title.label("Export Defaults")
            col_export_title.operator("cap.create_current_preset", text="", icon="ZOOMIN")
            col_export_title.operator("cap.delete_global_preset", text="", icon="ZOOMOUT")
            col_export_title.prop(addon_prefs, "global_presets_enum", text="")

            col_export = export_box.row(align=True)
            col_export.template_list("Export_Default_UIList", "default", exp, "export_defaults", exp, "export_defaults_index", rows=3, maxrows=6)

            col_export.separator()
            row_export = col_export.column(align=True)
            row_export.operator("scene.cap_addexport", text="", icon="ZOOMIN")
            row_export.operator("scene.cap_deleteexport", text="", icon="ZOOMOUT")
            row_export.separator()
            row_export.operator("cap.add_global_preset", text="", icon="FORWARD")

            if len(exp.export_defaults) > 0 and (exp.export_defaults_index) < len(exp.export_defaults):

                currentExp = exp.export_defaults[exp.export_defaults_index]

                export_settings = export_box.column(align=True)
                export_settings.separator()
                export_tabs = export_settings.row(align=True)
                export_tabs.prop(addon_prefs, "export_preset_options", expand=True)

                export_separator = export_box.column(align=True)
                #export_separator.separator()


                if addon_prefs.export_preset_options == 'Export':
                    export_main = export_box.row(align=True)
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
                    export_main = export_box.row(align=True)
                    export_main.separator()

                    export_1 = export_main.column(align=True)
                    export_1.prop(currentExp, "bake_space_transform")
                    export_1.separator()

                    export_scale = export_1.row(align=True)
                    export_scale.prop(currentExp, "global_scale")
                    export_scale.prop(currentExp, "apply_unit_scale", text="", icon='NDOF_TRANS')
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
                    export_main = export_box.row(align=True)
                    export_main.separator()
                    export_1 = export_main.column(align=True)
                    export_1.prop(currentExp, "loose_edges")
                    export_1.prop(currentExp, "tangent_space")
                    export_1.separator()

                elif addon_prefs.export_preset_options == 'Armature':
                    export_main = export_box.row(align=True)
                    export_main.separator()
                    export_1 = export_main.column(align=True)
                    export_1.prop(currentExp, "use_armature_deform_only")
                    export_1.prop(currentExp, "add_leaf_bones")

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

                #elif addon_prefs.export_preset_options == 'Animation':
                    #export_main = export_box.row(align=True)
                    #export_main.separator()

                    #export_1 = export_main.column(align=True)
                    #export_1.prop(currentExp, "bake_anim_use_all_bones")
                    #export_1.prop(currentExp, "bake_anim_use_nla_strips")
                    #export_1.prop(currentExp, "bake_anim_use_all_actions")
                    #export_1.prop(currentExp, "bake_anim_force_startend_keying")
                    #export_1.prop(currentExp, "optimise_keyframes")
                    #export_1.prop(currentExp, "use_default_take")
                    #export_1.separator()

                    #export_main.separator()
                    #export_main.separator()
                    #export_main.separator()

                    #export_2 = export_main.column(align=True)
                    #export_2.prop(currentExp, "bake_anim_step")
                    #export_2.prop(currentExp, "bake_anim_simplify_factor")
                    #export_2.separator()

                    #export_main.separator()

            else:
                preset_unselected = export_box.column(align=True)
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

            if len(exp.export_defaults) > 0 and (exp.export_defaults_index) < len(exp.export_defaults):

                currentExp = exp.export_defaults[exp.export_defaults_index]

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


            if len(exp.export_defaults) > 0 and (exp.export_defaults_index) < len(exp.export_defaults):

                currentExp = exp.export_defaults[exp.export_defaults_index]

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
                    #options_ui.prop(currentPass, "export_animation")
                    options_ui.prop(currentPass, "apply_modifiers")
                    options_ui.prop(currentPass, "triangulate")
                    options_ui.prop(currentPass, "export_individual")
                    options_object_tags = options_ui.column(align=True)
                    options_object_tags.prop(currentPass, "object_use_tags")
                    if currentPass.export_individual is False:
                        options_object_tags.enabled = False
                    options_ui.separator()

                    pass_options.separator()
                    pass_options.separator()
                    pass_options.separator()

                    # Tag Filters
                    tag_filter = pass_options.column(align=True)
                    tag_filter.label(text="Tag Filters")
                    tag_filter.separator()

                    for passTag in currentPass.tags:
                        tag_column = tag_filter.column(align=True)
                        tag_column.prop(passTag, "use_tag", text="Filter " + passTag.name)

                    tag_filter.separator()

                    #pass_options.separator()

                    #tag_filter.prop(addon_prefs, "component_dropdown", text="Filter By Tags")
                    #tag_filter.template_list("GEX_TagFilter_UIList", "default", currentPass, "tags", currentPass, "tags_index", rows=3, maxrows=6)
                    #tag_filter.separator()

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
            optionsUI.label("Plugin Options")

        else:
            optionsUI.prop(addon_prefs, "options_dropdown", text="", icon='TRIA_DOWN', emboss=False)
            optionsUI.label("Plugin Options")
            options_main = options_box.row(align=True)
            options_main.separator()

            options_1 = options_main.column(align=False)
            #options_1.alignment = 'CENTER'
            options_1.label("Additional List Options")
            options_1.separator()
            options_1.prop(addon_prefs, "list_feature", text="", expand=False)
            options_1.separator()
            options_1.separator()
            options_1.prop(addon_prefs, "object_list_autorefresh", expand=False)

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

    if bpy.context.active_object.name != addon_prefs.prev_selected_object:
        if addon_prefs.object_multi_edit is False:
            addon_prefs.object_multi_edit = True
        if addon_prefs.group_multi_edit is False:
            addon_prefs.group_multi_edit = True

        addon_prefs.prev_selected_object = bpy.context.active_object.name



def register():

    print("Registering Stuff")
    bpy.utils.register_module(__name__)

    bpy.types.Scene.CAPScn = PointerProperty(type=properties.CAP_Scene_Preferences)
    bpy.types.Object.CAPObj = PointerProperty(type=properties.CAP_Object_Preferences)
    bpy.types.Group.CAPGrp = PointerProperty(type=properties.CAP_Group_Preferences)
    bpy.types.Action.CAPAcn = PointerProperty(type=properties.CAP_Action_Preferences)
    bpy.types.Scene.CAPUI = PointerProperty(type=properties.CAP_UI_Preferences)
    bpy.types.Object.CAPStm = PointerProperty(type=properties.CAP_Object_StateMachine)
    bpy.types.Object.CAPExp = PointerProperty(type=CAP_ExportPresets)
    ui_operators.CreatePresets()

    bpy.app.handlers.load_post.append(CreateDefaultData)
    bpy.app.handlers.scene_update_post.append(CheckSelectedObject)

def unregister():

    bpy.app.handlers.load_post.remove(CreateDefaultData)
    bpy.app.handlers.scene_update_post.remove(CheckSelectedObject)

    print("Unregistering Stuff")
    del bpy.types.Object.CAPExp
    del bpy.types.Scene.CAPScn
    del bpy.types.Object.CAPObj
    del bpy.types.Group.CAPGrp
    del bpy.types.Action.CAPAcn
    del bpy.types.Scene.CAPUI
    del bpy.types.Object.CAPStm

    bpy.utils.unregister_module(__name__)


# Only if i ever wanted to run the script in the text editor, which I don't
if __name__ == "__main__":
    register()
