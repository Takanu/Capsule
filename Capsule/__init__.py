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
    "author": "Takanu Kyriako",
    "version": (1, 2, 0),
    "blender": (2, 80, 0),
    "location": "3D View > Object Mode > Tools > Capsule",
    "wiki_url": "https://github.com/Takanu/Capsule",
    "description": "An export manager that helps you export 3D objects into multiple files and formats.",
    "tracker_url": "",
    "category": "Import-Export"
}

# Start importing all the addon files
# #FIXME: I dont have to import everything here.
import bpy
from .export_formats import *
from .tk_utils import *
from .properties import *
from .user_interface import *
from .export_operators import *
from .export_presets import *
from .export_properties import *
from .export_utils import *
from .export_menu import *
from .ui_operators import *
from .update import *
from .update_collections import *

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

from bpy.app.handlers import persistent

from .export_properties import (
    CAPSULE_ExportTag, 
    CAPSULE_ExportPassTag, 
    CAPSULE_ExportPass, 
    CAPSULE_ExportPreset, 
    CAPSULE_LocationDefault, 
    CAPSULE_ExportPresets,
    )


# This sequence checks the files currently loaded? (CHECKME)
# I actually don't know what this quite does anymore, commenting out for now.

# print("Checking modules...")

# if "bpy" in locals():
#     import imp
#     print("------------------Reloading Capsule------------------")
#     if "tk_utils" in locals():
#         imp.reload(tk_utils)
#     if "properties" in locals():
#         imp.reload(properties)
#     if "user_interface" in locals():
#         imp.reload(user_interface)
#     if "export_operators" in locals():
#         imp.reload(export_operators)
#     if "export_presets" in locals():
#         imp.reload(export_presets)
#     if "export_properties" in locals():
#         imp.reload(export_properties)
#     if "export_utils" in locals():
#         imp.reload(export_utils)
#     if "export_menu" in locals():
#         imp.reload(export_menu)
#     if "ui_operators" in locals():
#         imp.reload(ui_operators)
#     if "update" in locals():
#         imp.reload(update)
#     if "update_collections" in locals():
#         imp.reload(update_collections)

# print("Importing modules...")


def GetGlobalPresets(scene, context):

    items = [
        ("0", "None",  "", 0),
        ]

    preferences = context.preferences
    addon_prefs = preferences.addons[__package__].preferences
    exp = addon_prefs.saved_presets

    u = 1

    for i,x in enumerate(exp):
        items.append((str(i+1), x.name, x.description, i+1))

    return items

def UpdateObjectSelectMode(self, context):

    if self.object_multi_edit is True:
        context.scene.CAPScn.object_list_index = -1

def UpdateCollectionSelectMode(self, context):

    if self.collection_multi_edit is True:
        context.scene.CAPScn.collection_list_index = -1


class CAP_AddonPreferences(AddonPreferences):
    bl_idname = __name__

    # The name for the empty object that exists to store .blend file level Capsule data.
    default_datablock: StringProperty(
        name="Dummy Datablock Name",
        description="The dummy block being used to store Export Default and Location Default data, in order to enable the data to be used between scenes.",
        default=">Capsule Blend File Data<"
    )

    # Storage for the Global Presets, and it's enum UI list.
    sort_presets: CollectionProperty(type=CAPSULE_ExportPreset)
    saved_presets: CollectionProperty(type=CAPSULE_ExportPreset)
    saved_presets_index: IntProperty()

    saved_presets_dropdown: BoolProperty(default=False)
    presets_dropdown: BoolProperty(default = False)
    tags_dropdown: BoolProperty(default = False)
    passes_dropdown: BoolProperty(default = False)
    options_dropdown: BoolProperty(default = False)

    # not currently accessible through any menu, this is now an internally-managed state.
    # used to turn off multi-selection editing when an object is selected from the export list,
    # or potentially for other operations.
    object_multi_edit: BoolProperty(
        name="Collection Multi-Edit Mode",
        description="Allows you to edit export settings for all objects that the currently selected.  \n\nTurning this option off will let you edit the currently selected object on the list.",
        default=True,
        update=UpdateObjectSelectMode
        )
    
    # not currently accessible through any menu, this is now an internally-managed state.
    # used to turn off multi-selection editing when an object is selected from the export list,
    # or potentially for other operations.
    collection_multi_edit: BoolProperty(
        name="Collection Multi-Edit Mode",
        description="Allows you to edit export settings for all collections that the currently selected objects belong to.  \n\nWARNING - One object can belong to multiple collections, please be careful when using this mode.",
        default=False,
        update=UpdateCollectionSelectMode
        )

    object_list_autorefresh: BoolProperty(
        name="Object List Auto-Refresh",
        description="Determines whether or not an object on the object export list will automatically be removed when Enable Export is unticked.  If this option is disabled, a manual refresh button will appear next to the list."
        )

    list_feature: EnumProperty(
        name="Additional List Features",
        description="Allows for the customisation of a secondary button next to each Object and Collection Export list entry.",
        items=(
            ('none', 'None', 'No extra option will be added to the list'),
            ('sel', 'Select', 'Adds an option next to a list entry that allows you to select that Object or Collection in the 3D View.'),
            ('focus', 'Focus', 'Adds an option next to a list entry that allows you to select and focus the 3D view on that Object or Collection.')),
        default='focus'
        )

    substitute_directories: BoolProperty(
        name="Substitute Invalid Folder Characters",
        description="If any of your export directories contain invalid characters for the operating system you currently use, ticking this on will substitute them with an underscore.  \n\nIf unticked, the plugin will prompt you with an error if your directories contain invalid characters.",
        default=True
        )

    data_missing: BoolProperty(default=False)
    plugin_is_ready: BoolProperty(default=False)
    prev_selected_object: StringProperty(default='')
    prev_selected_count: IntProperty(default=0)

    def draw(self, context):
        layout = self.layout

        preferences = context.preferences
        addon_prefs = preferences.addons[__name__].preferences
        exp = None

        # UI Prompt for when the .blend Capsule data can no longer be found.
        try:
            exp = bpy.data.objects[addon_prefs.default_datablock].CAPExp
        except KeyError:
            layout = self.layout
            col_export = layout.column(align=True)
            col_export.label(text="No Capsule for this .blend file has been found,")
            col_export.label(text="Please press the button below to generate new data.")
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
            col_export_title.label(text="Export Presets")


        else:
            col_export_title.prop(addon_prefs, "presets_dropdown", text="", icon='TRIA_DOWN', emboss=False)
            #col_export_title.operator("cap_tutorial.tags", text="", icon='INFO')
            col_export_title.label(text="Export Presets")

            if addon_prefs.saved_presets_dropdown is False:
                savedpresets_box = export_box.box()
                col_saved_title = savedpresets_box.row(align=True)
                col_saved_title.prop(addon_prefs, "saved_presets_dropdown", text="", icon='TRIA_RIGHT', emboss=False)
                col_saved_title.label(text="Saved Presets")

            else:
                savedpresets_box = export_box.box()
                col_saved_title = savedpresets_box.row(align=True)
                col_saved_title.prop(addon_prefs, "saved_presets_dropdown", text="", icon='TRIA_DOWN', emboss=False)
                col_saved_title.label(text="Saved Presets")

                col_savedpresets = savedpresets_box.row(align=True)
                col_savedpresets_list = col_savedpresets.column(align=True)
                col_savedpresets_list.template_list("CAPSULE_UL_Saved_Default", "default", addon_prefs, "saved_presets", addon_prefs, "saved_presets_index", rows=3, maxrows=6)
                col_savedpresets_list.operator("cap.create_current_preset", text="Add to File Presets", icon="FORWARD")

                col_savedpresets_options = col_savedpresets.column(align=True)
                col_savedpresets_options.operator("cap.delete_global_preset", text="", icon="REMOVE")


            filepresets_box = export_box.box()
            filepresets_box.label(text="Current File Presets")

            row_defaults = filepresets_box.row(align=True)
            col_defaultslist = row_defaults.column(align=True)
            col_defaultslist.template_list("CAPSULE_UL_Export_Default", "default", exp, "file_presets", exp, "file_presets_listindex", rows=3, maxrows=6)
            col_defaultslist.operator("cap.add_global_preset", text="Add to Saved Presets", icon="FORWARD")

            col_defaultslist_options = row_defaults.column(align=True)
            col_defaultslist_options.operator("scene.cap_addexport", text="", icon="ADD")
            col_defaultslist_options.operator("scene.cap_deleteexport", text="", icon="REMOVE")


            if len(exp.file_presets) > 0 and (exp.file_presets_listindex) < len(exp.file_presets):

                currentExp = exp.file_presets[exp.file_presets_listindex]

                filepresets_box.label(text="Basic Settings")
                filepresets_options = filepresets_box.row(align=True)

                filepresets_options_2_col = filepresets_options.row(align=True)
                filepresets_options_2_col.alignment = 'LEFT'

                filepresets_options_2_label = filepresets_options_2_col.column(align=True)
                filepresets_options_2_label.alignment = 'LEFT'
                filepresets_options_2_label.label(text="Format Type:")

                filepresets_options_2_dropdowns = filepresets_options_2_col.column(align=True)
                filepresets_options_2_dropdowns.alignment = 'EXPAND'
                filepresets_options_2_dropdowns.prop(currentExp, "format_type", text="")
                filepresets_options_2_dropdowns.separator()

                filepresets_options.separator()
                filepresets_options.separator()
                filepresets_options.separator()

                filepresets_options_1 = filepresets_options.column(align=True)
                filepresets_options_1.alignment = 'EXPAND'
                filepresets_options_1.prop(currentExp, "use_blend_directory")
                filepresets_options_1.prop(currentExp, "use_sub_directory")
                filepresets_options_1.prop(currentExp, "filter_render")

                # this was removed from 1.01 onwards due to implementation issues.
                # filepresets_options_1.prop(currentExp, "reset_rotation")

                filepresets_options_1.prop(currentExp, "preserve_armature_constraints")

                filepresets_options.separator()


                filepresets_box.label(text="Format Type Settings")
                #filepresets_box.separator()

                if currentExp.format_type == 'FBX':
                    currentExp.data_fbx.draw_addon_preferences(filepresets_box, currentExp.data_fbx, exp)

                elif currentExp.format_type == 'OBJ':
                    currentExp.data_obj.draw_addon_preferences(filepresets_box, currentExp.data_obj, exp)

                elif currentExp.format_type == 'GLTF':
                    currentExp.data_gltf.draw_addon_preferences(filepresets_box, currentExp.data_gltf, exp)
                
                elif currentExp.format_type == 'Alembic':
                    currentExp.data_abc.draw_addon_preferences(filepresets_box, currentExp.data_abc, exp)
                
                elif currentExp.format_type == 'Collada':
                    currentExp.data_dae.draw_addon_preferences(filepresets_box, currentExp.data_dae, exp)
                
                elif currentExp.format_type == 'STL':
                    currentExp.data_stl.draw_addon_preferences(filepresets_box, currentExp.data_stl, exp)

            else:
                preset_unselected = filepresets_box.column(align=True)
                preset_unselected.label(text="Select a preset in order to view preset settings.")
                preset_unselected.separator()
                return


        #---------------------------------------------------------
        # Tags UI
        #---------------------------------------------------------
        tag_box = layout.box()
        tag_title = tag_box.row(align=True)

        if addon_prefs.tags_dropdown is False:
            tag_title.prop(addon_prefs, "tags_dropdown", text="", icon='TRIA_RIGHT', emboss=False)
            tag_title.label(text="Tags")

        else:
            tag_title.prop(addon_prefs, "tags_dropdown", text="", icon='TRIA_DOWN', emboss=False)
            tag_title.label(text="Tags")

            if len(exp.file_presets) > 0 and (exp.file_presets_listindex) < len(exp.file_presets):

                currentExp = exp.file_presets[exp.file_presets_listindex]

                tagUI_row = tag_box.row(align=True)
                tagUI_row.template_list("CAPSULE_UL_Tag_Default", "default", currentExp, "tags", currentExp, "tags_index", rows=3, maxrows=6)

                tagUI_col = tagUI_row.column(align=True)
                tagUI_col.operator("scene.cap_addtag", text="", icon="ADD")
                tagUI_col.operator("scene.cap_deletetag", text="", icon="REMOVE")
                tagUI_col.separator()

                tag_settings = tag_box.column(align=True)
                tag_settings.separator()

                if len(currentExp.tags) == 0:
                    tag_settings.label(text="Create a new tag in order to view and edit tag settings.")
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
                unselected.label(text="Select a preset in order to view tag settings.")
                unselected.separator()

        #---------------------------------------------------------
        # Pass UI
        #---------------------------------------------------------
        pass_box = layout.box()
        passUI = pass_box.row(align=True)

        if addon_prefs.passes_dropdown is False:
            passUI.prop(addon_prefs, "passes_dropdown", text="", icon='TRIA_RIGHT', emboss=False)
            passUI.label(text="Passes")

        else:
            passUI.prop(addon_prefs, "passes_dropdown", text="", icon='TRIA_DOWN', emboss=False)
            passUI.label(text="Passes")


            if len(exp.file_presets) > 0 and (exp.file_presets_listindex) < len(exp.file_presets):

                currentExp = exp.file_presets[exp.file_presets_listindex]

                row_passes = pass_box.row(align=True)
                row_passes.template_list("CAPSULE_UL_Pass_Default", "default", currentExp, "passes", currentExp, "passes_index", rows=3, maxrows=6)

                row_passes.separator()

                col_passes = row_passes.column(align=True)
                col_passes.operator("scene.cap_addpass", text="", icon="ADD")
                col_passes.operator("scene.cap_deletepass", text="", icon="REMOVE")
                col_passes.separator()


                pass_settings = pass_box.column(align=True)
                pass_settings.separator()

                if len(currentExp.passes) == 0:
                    pass_settings.label(text="Create a new pass in order to view and edit pass settings.")
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
                unselected.label(text="Select a preset in order to view tag settings.")
                unselected.separator()

        #---------------------------------------------------------
        # Options
        #---------------------------------------------------------
        options_box = layout.box()
        optionsUI = options_box.row(align=True)

        if addon_prefs.options_dropdown is False:
            optionsUI.prop(addon_prefs, "options_dropdown", text="", icon='TRIA_RIGHT', emboss=False)
            optionsUI.label(text="Extra Settings")

        else:
            optionsUI.prop(addon_prefs, "options_dropdown", text="", icon='TRIA_DOWN', emboss=False)
            optionsUI.label(text="Extra Settings")
            options_main = options_box.row(align=True)
            options_main.separator()

            options_1 = options_main.column(align=False)
            #options_1.alignment = 'CENTER'
            options_1.label(text="Additional List Options")
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
            options_2.label(text="Reset")
            options_2.separator()
            options_2.operator("scene.cap_resetsceneprops", text="Reset Scene")
            options_2.separator()

            options_main.separator()

@persistent
def CreateDefaultData(scene):
    """
    Attempts to create a Default Data object (a plain axis with a very specific name) to store export preference information in.  If one already exists, it will exit early.
    """

    preferences = bpy.context.preferences
    addon_prefs = preferences.addons[__name__].preferences

    # Figure out if an object already exists, if yes do nothing
    for object in bpy.data.objects:
        print(object)
        if object.name == addon_prefs.default_datablock:
            return

    # Otherwise create the object using the addon preference data
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.empty_add(type='PLAIN_AXES')

    # set it's properties
    defaultDatablock = bpy.context.view_layer.objects.active
    defaultDatablock.name = addon_prefs.default_datablock
    defaultDatablock.CAPExp.is_storage_object = True

    # hide it!
    defaultDatablock.hide_set(true)
    defaultDatablock.select_set(true)
    defaultDatablock.hide_render = True
    

@persistent
def CheckSelectedObject(scene):
    """
    A scene handler used to configure the status of previously selected objects and multi-edit opportunities behind the scenes.
    """

    preferences = bpy.context.preferences
    addon_prefs = preferences.addons[__name__].preferences
    #print("SCENE UPDATE")

    if bpy.context.active_object is not None:
        if bpy.context.active_object.name != addon_prefs.prev_selected_object:
            addon_prefs.object_multi_edit = True
            addon_prefs.collection_multi_edit = True
            addon_prefs.prev_selected_object = bpy.context.active_object.name

    if len(bpy.context.selected_objects) != addon_prefs.prev_selected_count:
        addon_prefs.object_multi_edit = True
        addon_prefs.collection_multi_edit = True
        addon_prefs.prev_selected_count = len(bpy.context.selected_objects)


addon_keymaps = []

classes = (
    # export_formats
    CAP_FormatData_FBX,
    CAP_FormatData_OBJ,
    CAP_FormatData_GLTF,
    CAP_FormatData_Alembic,
    CAP_FormatData_Collada,
    CAP_FormatData_STL,

    # properties
    ObjectListItem, 
    CollectionListItem, 
    ActionListItem, 
    CAPSULE_Scene_Preferences, 
    CAPSULE_Object_Preferences, 
    CAPSULE_Collection_Preferences, 
    CAPSULE_Object_StateMachine, 
    # CAPSULE_Action_Preferences,

    # export_operators
    CAPSULE_OT_ExportAssets,

    # export_properties
    CAPSULE_ExportTag, 
    CAPSULE_ExportPassTag, 
    CAPSULE_ExportPass, 
    CAPSULE_ExportPreset, 
    CAPSULE_LocationDefault, 
    CAPSULE_ExportPresets,

    # ui_operators
    CAPSULE_OT_Add_Path,
    CAPSULE_OT_Delete_Path,
    CAPSULE_OT_Add_Export,
    CAPSULE_OT_Delete_Export,
    CAPSULE_OT_Add_Tag,
    CAPSULE_OT_Delete_Tag,
    CAPSULE_OT_Add_Pass,
    CAPSULE_OT_Delete_Pass,
    CAPSULE_OT_Shift_Path_Up,
    CAPSULE_OT_Shift_Path_Down,
    CAPSULE_OT_Set_Root_Object,
    CAPSULE_OT_Clear_Root_Object,
    CAPSULE_OT_Clear_List,
    CAPSULE_OT_Refresh_List,
    CAPSULE_OT_Reset_Scene,
    CAPSULE_OT_Reset_Defaults,
    CAPSULE_OT_UI_Group_Separate,
    CAPSULE_OT_UI_Group_Options,
    CAPSULE_OT_Refresh_Actions,
    CAPSULE_OT_Tutorial_Tags,
    CAPSULE_OT_Create_ExportData,
    CAPSULE_OT_Add_Stored_Presets,
    CAPSULE_OT_Delete_Presets,
    CAPSULE_OT_Store_Presets,

    # user_inferface
    CAPSULE_UL_Name,
    CAPSULE_UL_TagFilter,
    CAPSULE_UL_Object,
    CAPSULE_UL_Collection,
    CAPSULE_UL_Path_Default,
    CAPSULE_UL_Saved_Default,
    CAPSULE_UL_Export_Default,
    CAPSULE_UL_Tag_Default,
    CAPSULE_UL_Pass_Default,
    # CAPSULE_UL_Action,
    CAPSULE_PT_Header,
    CAPSULE_PT_Selection,
    CAPSULE_PT_List,
    CAPSULE_PT_Location,

    # init
    CAP_AddonPreferences,
)

def register():
    """
    Registers itself and any extra pointer properties, handlers and keymaps to Blender.
    """

    # Register classes
    for cls in classes:
        print("Registering ", cls)
        bpy.utils.register_class(cls)

    # Assign datablocks now all classes have been registered.
    bpy.types.Scene.CAPScn = PointerProperty(name='Capsule Scene Properties', type=CAPSULE_Scene_Preferences)
    bpy.types.Object.CAPObj = PointerProperty(name='Capsule Object Properties', type=CAPSULE_Object_Preferences)
    bpy.types.Collection.CAPCol = PointerProperty(name='Capsule Collection Properties', type=CAPSULE_Collection_Preferences)
    # bpy.types.Action.CAPAcn = PointerProperty(type=CAPSULE_Action_Preferences)
    bpy.types.Object.CAPStm = PointerProperty(name='Capsule State Tracker', type=CAPSULE_Object_StateMachine)
    bpy.types.Object.CAPExp = PointerProperty(name='Capsule Export Presets', type=CAPSULE_ExportPresets)


    # Setup data and handlers
    # export_presets.CreatePresets()
    bpy.app.handlers.load_pre.append(CreateDefaultData)
    bpy.app.handlers.depsgraph_update_post.append(CheckSelectedObject)


    # Register keymaps
    wm = bpy.context.window_manager
    if wm.keyconfigs.addon:
        # Object Mode
        km = wm.keyconfigs.addon.keymaps.new(name='Object Mode')
        kmi = km.keymap_items.new('wm.call_menu_pie', 'E', 'PRESS')
        kmi.properties.name = "pie.capsule_main"
#        kmi.active = True
        addon_keymaps.append(kmi)


def unregister():
    """
    Unregisters itself and any extra pointer properties, handlers and keymaps from Blender.
    """

    # Remove keymaps
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps['Object Mode']
        for kmi in km.keymap_items:
            if kmi.idname == 'wm.call_menu_pie':
                if kmi.properties.name == "pie.capsule_main":
                    km.keymap_items.remove(kmi)
    
    # export_presets.DeletePresets()
    bpy.app.handlers.load_pre.remove(CreateDefaultData)
    bpy.app.handlers.depsgraph_update_post.remove(CheckSelectedObject)


    # Delete custom datablocks
    del bpy.types.Scene.CAPScn
    del bpy.types.Object.CAPObj
    del bpy.types.Collection.CAPCol
    # del bpy.types.Action.CAPAcn
    del bpy.types.Object.CAPStm
    del bpy.types.Object.CAPExp


    # Unregister classes
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)



