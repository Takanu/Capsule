
#This states the metadata for the plugin
bl_info = {
    "name": "Capsule",
    "author": "Crocadillian/Takanu @ Polarised Games",
    "version": (1,0),
    "blender": (2, 7, 5),
    "api": 39347,
    "location": "3D View > Object Mode > Tools > GEX",
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


print("Beginning Import"*20)

import bpy
from . import definitions
from . import properties
from . import user_interface
from . import export_operators
from . import ui_operators
from . import update
from bpy.props import IntProperty, FloatProperty, BoolProperty, StringProperty, PointerProperty, CollectionProperty, EnumProperty
from bpy.types import AddonPreferences, PropertyGroup

print("End of import")

def Update_TagName(self, context):

    user_preferences = context.user_preferences
    addon_prefs = user_preferences.addons[__package__].preferences

    export = addon_prefs.export_defaults[addon_prefs.export_defaults_index]
    currentTag = export.tags[export.tags_index]

    # Get the name of the tag
    tag_name = currentTag.name

    # Get tags in all current passes, and edit them
    for expPass in export.passes:
        passTag = expPass.tags[export.tags_index]
        passTag.name = tag_name

    return None

class ExportTag(PropertyGroup):

    name = StringProperty(
        name="Tag Name",
        description="The name of the tag.",
        update = Update_TagName
    )

    name_filter = StringProperty(
        name="Tag",
        description="The string you wish to use as a tag when sorting through object names."
    )

    name_filter_type = EnumProperty(
        name = "Tag Type",
        description = "Where the tag is being placed in the object name.",
        items=(
        ('1', 'Suffix', ''),
        ('2', 'Prefix', ''),
        ),)

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

    # Special preferences for special export presets
    x_user_deletable = BoolProperty(default=True)
    x_user_editable_type = BoolProperty(default=True)

    # Special preference to rename objects during export, to make UE4/Unity export more seamless
    x_ue4_collision_naming = BoolProperty(default=False)

class ExportPassTag(PropertyGroup):
    name = StringProperty(
        name = "Tag Name",
        description = "The name of the tag...",
        default = "")

    prev_name = StringProperty(
        name = "Previous Tag Name",
        description = "A backup tag name designed to prevent editing of tag names when viewing them",
        default = "")

    index = IntProperty(
        name = "Tag Index",
        description = "Where the tag is located in the Export Preset, so it can be looked up later (Internal Only)",
        default = 0)

    use_tag = BoolProperty(
        name = "Use Tag",
        description = "Determines whether or not the tag gets used in the pass.",
        default = False)

class ExportPass(PropertyGroup):

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

    tags = CollectionProperty(type=ExportPassTag)
    tags_index = IntProperty(default=0)

    export_individual = BoolProperty(
        name="Export Individual",
        description="Exports every object in the pass as an individual object, regardless of whether it's in a group.",
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


class ExportPreset(PropertyGroup):
    name = StringProperty(
        name = "Default Name",
        description="The name of the export preset, whoda thunk :OO",
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

    filter_render = BoolProperty(
        name="Filter by Rendering",
        description="Will use the Hide Render option on objects (viewable in the Outliner) to filter whether or not an object can be exported.  If the object is hidden from the render, it will not export regardless of any other settings in this plugin."
    )

    export_types = EnumProperty(
            name="Object Types",
            options={'ENUM_FLAG'},
            items=(('EMPTY', "Empty", ""),
                   ('CAMERA', "Camera", ""),
                   ('LAMP', "Lamp", ""),
                   ('ARMATURE', "Armature", ""),
                   ('MESH', "Mesh", ""),
                   ('OTHER', "Other", "Includes other mesh types like Curves and Metaballs, which are converted to meshes on export"),
                   ),
            description="Defines what kinds of objects will be exported by the FBX exporter, regardless of any other defined options in Capsule.",
            default={'EMPTY', 'CAMERA', 'LAMP', 'ARMATURE', 'MESH', 'OTHER'},
            )


    passes = CollectionProperty(type=ExportPass)
    passes_index = IntProperty(default=0)
    tags = CollectionProperty(type=ExportTag)
    tags_index = IntProperty(default=0)

    global_scale = FloatProperty(
        name="Global Scale",
        description="The exported scale of the objects.",
        default=1.0)

    bake_space_transform = BoolProperty(
        name="Bake Space Transform",
        description="Erm...",
        default=False)

    axis_up = EnumProperty(
        name="Axis Up",
        description="What the Up Axis will be defined as when the model is exported.",
        items=(
            ('X', 'X', ''),
            ('Y', 'Y', ''),
            ('Z', 'Z', ''),
            ('-X', '-X', ''),
            ('-Y', '-Y', ''),
            ('-Z', '-Z', '')))


    axis_forward = EnumProperty(
        name="Axis Forward",
        description="What the Forward Axis will be defined as when the model is exported.",
        items=(
            ('X', 'X', ''),
            ('Y', 'Y', ''),
            ('Z', 'Z', ''),
            ('-X', '-X', ''),
            ('-Y', '-Y', ''),
            ('-Z', '-Z', '')))

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
            default='Y')

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
        default='X')

    armature_nodetype = EnumProperty(
        name="FBX Armature NodeType",
        description="What the Forward Axis will be defined as when the model is exported.",
        items=(
            ('Null', 'Null', ''),
            ('Root', 'Root', ''),
            ('LimbNode', 'LimbNode', '')))


    bake_anim_use_all_bones = BoolProperty(
        name="Use All Bones",
        description="Makes any separate edges a two-verted polygon.",
        default=False
    )

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
        default = 1,
        min = 0,
        max = 100,
        soft_min = 0.1,
        soft_max = 10

    )

    bake_anim_simplify_factor = FloatProperty(
        name="Simplify Factor",
        description="Blah",
        default = 1,
        min = 0,
        max = 100,
        soft_min = 0,
        soft_max = 10
    )

class GEXAddonPreferences(AddonPreferences):
    bl_idname = __name__

    export_defaults = CollectionProperty(type=ExportPreset)
    export_defaults_index = IntProperty(default=0)

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

    def draw(self, context):
        layout = self.layout

        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__name__].preferences
        scn = context.scene.GXScn
        ob = context.object
        ui = context.scene.GXUI

        #---------------------------------------------------------
        # Export UI
        #---------------------------------------------------------
        export_box = layout.box()
        col_export_title = export_box.row(align=True)

        if ui.presets_dropdown is False:
            col_export_title.prop(ui, "presets_dropdown", text="", icon='TRIA_RIGHT', emboss=False)
            col_export_title.label("Export Defaults")
            col_export_title.operator_menu_enum("gx.custom_presets", "presets")

        else:
            col_export_title.prop(ui, "presets_dropdown", text="", icon='TRIA_DOWN', emboss=False)
            col_export_title.label("Export Defaults")
            col_export_title.operator_menu_enum("gx.custom_presets", "presets")

            #custom_presets = export_box.column(align=True)
            #custom_presets.operator_menu_enum("gx.custom_presets", "presets")

            col_export = export_box.row(align=True)
            col_export.template_list("Export_Default_UIList", "default", addon_prefs, "export_defaults", addon_prefs, "export_defaults_index", rows=3, maxrows=6)

            col_export.separator()
            row_export = col_export.column(align=True)
            row_export.operator("scene.gx_addexport", text="", icon="ZOOMIN")
            row_export.operator("scene.gx_deleteexport", text="", icon="ZOOMOUT")

            if len(addon_prefs.export_defaults) > 0 and (addon_prefs.export_defaults_index) < len(addon_prefs.export_defaults):

                currentExp = addon_prefs.export_defaults[addon_prefs.export_defaults_index]

                export_settings = export_box.column(align=True)
                export_settings.separator()
                export_tabs = export_settings.row(align=True)
                export_tabs.prop(ui, "export_preset_options", expand=True)

                export_separator = export_box.column(align=True)
                #export_separator.separator()

                if ui.export_preset_options == 'Export':
                    export_main = export_box.row(align=True)
                    export_1 = export_main.column(align=True)

                    export_1.label("Exportable Object Types")
                    export_1.separator()
                    export_types = export_1.row(align=True)
                    export_types.prop(currentExp, "export_types")
                    export_1.separator()
                    export_1.separator()

                    export_1.prop(currentExp, "use_blend_directory")
                    export_1.prop(currentExp, "use_sub_directory")
                    export_1.prop(currentExp, "filter_render")

                if ui.export_preset_options == 'Transform':
                    export_main = export_box.row(align=True)
                    export_1 = export_main.column(align=True)
                    export_1.prop(currentExp, "bake_space_transform")
                    export_1.separator()

                    export_scale = export_1.row(align=True)
                    export_scale.prop(currentExp, "global_scale")
                    export_scale.prop(currentExp, "apply_unit_scale", text="", icon='NDOF_TRANS')

                    export_main_separator = export_main.column(align=True)
                    export_main_separator.separator()
                    export_main_separator.separator()

                    export_2 = export_main.column(align=True)
                    export_2.prop(currentExp, "axis_up")
                    export_2.prop(currentExp, "axis_forward")
                    export_2.separator()

                elif ui.export_preset_options == 'Geometry':
                    export_main = export_box.row(align=True)
                    export_1 = export_main.column(align=True)
                    export_1.prop(currentExp, "loose_edges")
                    export_1.prop(currentExp, "tangent_space")
                    export_1.separator()

                elif ui.export_preset_options == 'Armature':
                    export_main = export_box.row(align=True)
                    export_1 = export_main.column(align=True)
                    export_1.prop(currentExp, "use_armature_deform_only")
                    export_1.prop(currentExp, "add_leaf_bones")

                    export_2 = export_main.column(align=True)
                    export_2.prop(currentExp, "primary_bone_axis")
                    export_2.prop(currentExp, "secondary_bone_axis")
                    export_2.prop(currentExp, "armature_nodetype")
                    export_2.separator()

                elif ui.export_preset_options == 'Animation':
                    export_main = export_box.row(align=True)
                    export_1 = export_main.column(align=True)
                    export_1.prop(currentExp, "bake_anim_use_all_bones")
                    export_1.prop(currentExp, "bake_anim_use_nla_strips")
                    export_1.prop(currentExp, "bake_anim_use_all_actions")
                    export_1.prop(currentExp, "bake_anim_force_startend_keying")
                    export_1.prop(currentExp, "optimise_keyframes")
                    export_1.prop(currentExp, "use_default_take")

                    export_2 = export_main.column(align=True)
                    export_2.prop(currentExp, "bake_anim_step")
                    export_2.prop(currentExp, "bake_anim_simplify_factor")
                    export_2.separator()

            else:
                preset_unselected = export_box.column(align=True)
                preset_unselected.label("Select a preset in order to view preset settings.")
                preset_unselected.separator()


        #---------------------------------------------------------
        # Tags UI
        #---------------------------------------------------------
        tag_box = layout.box()
        tag_title = tag_box.row(align=True)

        if ui.tags_dropdown is False:
            tag_title.prop(ui, "tags_dropdown", text="", icon='TRIA_RIGHT', emboss=False)
            tag_title.label("Tags")

        else:
            tag_title.prop(ui, "tags_dropdown", text="", icon='TRIA_DOWN', emboss=False)
            tag_title.label("Tags")

            if len(addon_prefs.export_defaults) > 0 and (addon_prefs.export_defaults_index) < len(addon_prefs.export_defaults):

                currentExp = addon_prefs.export_defaults[addon_prefs.export_defaults_index]

                tagUI_row = tag_box.row(align=True)
                tagUI_row.template_list("Tag_Default_UIList", "default", currentExp, "tags", currentExp, "tags_index", rows=3, maxrows=6)

                tagUI_col = tagUI_row.column(align=True)
                tagUI_col.operator("scene.gx_addtag", text="", icon="ZOOMIN")
                tagUI_col.operator("scene.gx_deletetag", text="", icon="ZOOMOUT")
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

        if ui.passes_dropdown is False:
            passUI.prop(ui, "passes_dropdown", text="", icon='TRIA_RIGHT', emboss=False)
            passUI.label("Passes")

        else:
            passUI.prop(ui, "passes_dropdown", text="", icon='TRIA_DOWN', emboss=False)
            passUI.label("Passes")


            if len(addon_prefs.export_defaults) > 0 and (addon_prefs.export_defaults_index) < len(addon_prefs.export_defaults):

                currentExp = addon_prefs.export_defaults[addon_prefs.export_defaults_index]

                row_passes = pass_box.row(align=True)
                row_passes.template_list("Pass_Default_UIList", "default", currentExp, "passes", currentExp, "passes_index", rows=3, maxrows=6)

                row_passes.separator()

                col_passes = row_passes.column(align=True)
                col_passes.operator("scene.gx_addpass", text="", icon="ZOOMIN")
                col_passes.operator("scene.gx_deletepass", text="", icon="ZOOMOUT")
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

                    # Additional Export Options
                    options_ui = pass_options.column(align=True)
                    options_ui.label(text="Export Options")

                    options_ui.separator()
                    options_ui.prop(currentPass, "export_individual")
                    options_ui.prop(currentPass, "export_animation")
                    options_ui.prop(currentPass, "apply_modifiers")
                    options_ui.prop(currentPass, "triangulate")

                    # Tag Filters
                    tag_filter = pass_options.column(align=True)
                    tag_filter.label(text="Tag Filters")
                    tag_filter.separator()

                    for passTag in currentPass.tags:
                        tag = tag_filter.column(align=True)
                        tag.prop(passTag, "use_tag", text="Filter " + passTag.name)

                    #tag_filter.prop(ui, "component_dropdown", text="Filter By Tags")
                    #tag_filter.template_list("GEX_TagFilter_UIList", "default", currentPass, "tags", currentPass, "tags_index", rows=3, maxrows=6)
                    #tag_filter.separator()

                    pass_settings.separator()

            else:
                unselected = pass_box.column(align=True)
                unselected.label("Select a preset in order to view tag settings.")
                unselected.separator()

        #---------------------------------------------------------
        # Options
        #---------------------------------------------------------
        options_box = layout.box()
        optionsUI = options_box.row(align=True)

        if ui.options_dropdown is False:
            optionsUI.prop(ui, "options_dropdown", text="", icon='TRIA_RIGHT', emboss=False)
            optionsUI.label("Plugin Options")

        else:
            optionsUI.prop(ui, "options_dropdown", text="", icon='TRIA_DOWN', emboss=False)
            optionsUI.label("Plugin Options")
            options_main = options_box.row(align=True)

            options_1 = options_main.column(align=True)
            options_1.label("Additional List Option")
            options_1.separator()
            options_1.prop(addon_prefs, "list_feature", text="")
            options_1.separator()
            options_1.separator()
            options_1.prop(addon_prefs, "object_list_autorefresh")

            options_2 = options_main.column(align=True)
            options_2.label(" ")
            options_2.separator()



def register():
    bpy.utils.register_class(ExportTag)
    bpy.utils.register_class(ExportPassTag)
    bpy.utils.register_class(ExportPass)
    bpy.utils.register_class(ExportPreset)
    bpy.utils.register_module(__name__)


def unregister():
    bpy.utils.unregister_class(ExportTag)
    bpy.utils.unregister_class(ExportPassTag)
    bpy.utils.unregister_class(ExportPass)
    bpy.utils.unregister_class(ExportPreset)
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()
