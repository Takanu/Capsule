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
    "version": (1, 3, 1),
    "blender": (3, 1, 0),
    "location": "3D View > Object Mode > Tools > Capsule",
    "wiki_url": "https://github.com/Takanu/Capsule",
    "description": "An export manager that makes the process of repeat and bulk exports simple.",
    "tracker_url": "",
    "category": "Import-Export"
}

# Start importing all the addon files
# #FIXME: I dont have to import everything here.
import bpy
from .export_formats import *
from .tk_utils import *
from .update import *
from .properties import *

from .user_interface import *
from .export_operators import *
from .export_presets import *
from .export_utils import *
from .export_menu import *
from .ui_operators import *

import rna_keymap_ui

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

from .properties.export_properties import (
    CAPSULE_ExportPreset, 
    CAPSULE_LocationPreset, 
    CAPSULE_ExportData,
    )


# This sequence checks the files currently loaded? (CHECKME)
# I actually don't know what this quite does anymore, commenting out for now.

# #print("Checking modules...")

# if "bpy" in locals():
#     import imp
#     #print("------------------Reloading Capsule------------------")
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
#         imp.reload(update_objects)
#     if "update_collections" in locals():
#         imp.reload(update_collections)

# #print("Importing modules...")


def GetGlobalPresets(scene, context):

    items = [
        ("0", "None",  "", 0),
        ]

    preferences = context.preferences
    addon_prefs = preferences.addons[__package__].preferences
    exp = addon_prefs.saved_export_presets

    u = 1

    for i,x in enumerate(exp):
        items.append((str(i+1), x.name, x.description, i+1))

    return items


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
    saved_export_presets: CollectionProperty(type=CAPSULE_ExportPreset)
    saved_export_presets_index: IntProperty()

    # Addon Preferences Dropdowns
    saved_export_presets_dropdown: BoolProperty(default=False)
    file_export_presets_dropdown: BoolProperty(default=False)
    presets_dropdown: BoolProperty(default = False)
    keymap_dropdown: BoolProperty(default = False)
    options_dropdown: BoolProperty(default = False)

    # Selection Dropdowns
    edit_enable_dropdown: BoolProperty(default=False)

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
        name="Substitute Invalid Directory Characters",
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
        # Saved Presets
        #---------------------------------------------------------

        if addon_prefs.saved_export_presets_dropdown is False:
            savedpresets_box = layout.box()
            savedpresets_title = savedpresets_box.row(align=True)
            savedpresets_title.prop(addon_prefs, "saved_export_presets_dropdown", text="", icon='TRIA_RIGHT', emboss=False)
            savedpresets_title.label(text="Saved Presets")

        else:
            savedpresets_box = layout.box()

            savedpresets_title = savedpresets_box.row(align=True)
            savedpresets_title.prop(addon_prefs, "saved_export_presets_dropdown", text="", icon='TRIA_DOWN', emboss=False)
            savedpresets_title.label(text="Saved Presets")

            savedpresets_items = savedpresets_box.row(align=True)
            savedpresets_list = savedpresets_items.column(align=True)
            savedpresets_list.template_list("CAPSULE_UL_Saved_Default", "default", addon_prefs, "saved_export_presets", addon_prefs, "saved_export_presets_index", rows=3, maxrows=6)
            savedpresets_list.operator("cap.create_current_preset", text="Add to Active Export Presets", icon="FORWARD")

            savedpresets_listedit = savedpresets_items.column(align=True)
            savedpresets_listedit.operator("cap.delete_global_preset", text="", icon="REMOVE")

            

        #---------------------------------------------------------
        # Active Export Presets
        #---------------------------------------------------------

        if addon_prefs.file_export_presets_dropdown is False:
            file_presets_box = layout.box()
            col_saved_title = file_presets_box.row(align=True)
            col_saved_title.prop(addon_prefs, "file_export_presets_dropdown", text="", icon='TRIA_RIGHT', emboss=False)
            col_saved_title.label(text="Active Export Presets")

        else:
            file_presets_box = layout.box()
            col_saved_title = file_presets_box.row(align=True)
            col_saved_title.prop(addon_prefs, "file_export_presets_dropdown", text="", icon='TRIA_DOWN', emboss=False)
            col_saved_title.label(text="Active Export Presets")

            row_defaults = file_presets_box.row(align=True)
            col_defaultslist = row_defaults.column(align=True)
            col_defaultslist.template_list("CAPSULE_UL_Export_Default", "default", exp, "export_presets", exp, "export_presets_listindex", rows=3, maxrows=6)
            col_defaultslist.operator("cap.add_global_preset", text="Add to Saved Presets", icon="FORWARD")

            col_defaultslist_options = row_defaults.column(align=True)
            col_defaultslist_options.operator("scene.cap_addexport", text="", icon="ADD")
            col_defaultslist_options.operator("scene.cap_deleteexport", text="", icon="REMOVE")


            if len(exp.export_presets) > 0 and (exp.export_presets_listindex) < len(exp.export_presets):

                currentExp = exp.export_presets[exp.export_presets_listindex]

                general_options_box = file_presets_box.box()
                general_options_content = general_options_box.column(align=True)
                general_options_content.separator()

                general_options_heading = general_options_content.row(align=True)
                general_options_heading.label(text="General Export Options", icon="OBJECT_DATA")
                general_options_heading.separator()
                general_options_content.separator()


                general_options = general_options_content.column(align=True)
                
                
                general_options_anim = general_options_content.column(align=True)
                general_options_anim.use_property_split = True
                general_options_anim.use_property_decorate = False  # removes animation options
                if currentExp.format_type == 'STL':
                    general_options_anim.active = False
                general_options_anim.prop(currentExp, "export_animation")
                
                general_options_other = general_options_content.column(align=True)
                general_options_other.use_property_split = True
                general_options_other.use_property_decorate = False  # removes animation options
                general_options_other.prop(currentExp, "apply_modifiers")
                general_options_other.separator()
                general_options_other.prop(currentExp, "filter_by_rendering")
                general_options_other.prop(currentExp, "preserve_armature_constraints")
                general_options_other.separator()

                ## Format Options

                format_type_box = file_presets_box.box()
                format_type = format_type_box.column(align=True)
                format_type.separator()

                # Used a split here to recreate the use_property_split with a custom design.
                format_type_selector = format_type.row(align=True)
                format_type_selector_split = format_type_selector.split(factor=0.4, align=True)
                format_type_selector_split.label(text="Export File Type", icon="FILE")
                format_type_selector_split.prop(currentExp, "format_type", text="")
                format_type_selector.separator()

                format_type.separator()

                # TODO: Provide full preset data and reorganize arguments.
                # TODO: exp is an ambiguous name, rename it!
                # TODO: Add "default" markers for any complex dropdowns like Axis Up/Forward (smart thinking OBJ exporter)
                # TODO: Standardize Axis Labelling
                # TODO: Allow exporters to report issues and warnings based on configurations to be populated higher
                # in the UI hierarchy.
                # TODO: When a tab is changed in one format type, try to have it changed in all other types using an updater.
                if currentExp.format_type == 'FBX':
                    currentExp.data_fbx.draw_addon_preferences(format_type_box, currentExp.data_fbx, exp, currentExp)

                elif currentExp.format_type == 'OBJ':
                    currentExp.data_obj.draw_addon_preferences(format_type_box, currentExp.data_obj, exp, currentExp)

                elif currentExp.format_type == 'GLTF':
                    currentExp.data_gltf.draw_addon_preferences(format_type_box, currentExp.data_gltf, exp, currentExp)
                
                elif currentExp.format_type == 'Alembic':
                    currentExp.data_abc.draw_addon_preferences(format_type_box, currentExp.data_abc, exp, currentExp)
                
                elif currentExp.format_type == 'Collada':
                    currentExp.data_dae.draw_addon_preferences(format_type_box, currentExp.data_dae, exp, currentExp)
                
                elif currentExp.format_type == 'STL':
                    currentExp.data_stl.draw_addon_preferences(format_type_box, currentExp.data_stl, exp)
                
                elif currentExp.format_type == 'USD':
                    currentExp.data_usd.draw_addon_preferences(format_type_box, currentExp.data_usd, exp)

            else:
                preset_unselected = file_presets_box.column(align=True)
                preset_unselected.label(text="Select a preset in order to view preset settings.")
                preset_unselected.separator()

        #---------------------------------------------------------
        # Shortcut Keys
        #---------------------------------------------------------
        keymap_box = layout.box()
        keymap_menu = keymap_box.row(align=True)

        if addon_prefs.keymap_dropdown is False:
            keymap_menu.prop(addon_prefs, "keymap_dropdown", text="", icon='TRIA_RIGHT', emboss=False)
            keymap_menu.label(text="Key Shortcuts")

        else:
            keymap_menu.prop(addon_prefs, "keymap_dropdown", text="", icon='TRIA_DOWN', emboss=False)
            keymap_menu.label(text="Key Shortcuts")

            # Added L/R padding
            keymap_area = keymap_box.row(align=True)
            keymap_area.separator()
            
            keymap_options = keymap_area.column(align=True) 

            # Brings up the kinda-native keymap interface for plugin keymaps.
            wm = bpy.context.window_manager
            kc = wm.keyconfigs.user
            old_km_name = ""
            get_kmi_l = []
            for km_add, kmi_add in addon_keymaps:
                for km_con in kc.keymaps:
                    if km_add.name == km_con.name:
                        km = km_con
                        break

                for kmi_con in km.keymap_items:
                    if kmi_add.idname == kmi_con.idname:
                        if kmi_add.name == kmi_con.name:
                            get_kmi_l.append((km,kmi_con))

            get_kmi_l = sorted(set(get_kmi_l), key=get_kmi_l.index)

            for km, kmi in get_kmi_l:
                if not km.name == old_km_name:
                    keymap_options.label(text=str(km.name),icon="DOT")
                    keymap_options.context_pointer_set("keymap", km)
                    rna_keymap_ui.draw_kmi([], kc, km, kmi, keymap_options, 0)
                    keymap_options.separator()
                    old_km_name = km.name
            
            # right padding
            keymap_area.separator()

        #---------------------------------------------------------
        # Options
        #---------------------------------------------------------
        options_box = layout.box()
        extras_dropdown = options_box.row(align=True)

        if addon_prefs.options_dropdown is False:
            extras_dropdown.prop(addon_prefs, "options_dropdown", text="", icon='TRIA_RIGHT', emboss=False)
            extras_dropdown.label(text="Extra Settings")

        else:
            extras_dropdown.prop(addon_prefs, "options_dropdown", text="", icon='TRIA_DOWN', emboss=False)
            extras_dropdown.label(text="Extra Settings")
            options_box.separator()

            # Added L/R padding
            extras_area = options_box.row(align=True)
            extras_area.separator()

            extras_content = extras_area.column(align=True)
            extras_content.use_property_split = True
            extras_content.use_property_decorate = False  # removes 

            extras_content.prop(addon_prefs, "list_feature")
            extras_content.separator()
            extras_content.prop(addon_prefs, "substitute_directories")
            extras_content.separator()
            extras_content.separator()
            extras_content.separator()

            erase_options = extras_content.column(align=True)
            erase_options.operator("scene.cap_resetsceneprops", text="Reset Capsule Scene Data")
            erase_options.separator()
            # TODO: Work this out for later!
            # erase_options_split = erase_options.split(factor=0.4, align=False)
            # erase_options_split.label(text="Reset Options")
            # erase_options_split.operator("scene.cap_resetsceneprops", text="Reset Capsule Scene Data")

            # right padding
            extras_area.separator()

@persistent
def CreateDefaultData(scene):
    """
    Attempts to create a Default Data object (a plain axis with a very specific name) to store export preference information in.  If one already exists, it will exit early.
    """

    preferences = bpy.context.preferences
    addon_prefs = preferences.addons[__name__].preferences

    # Figure out if an object already exists, if yes do nothing
    for object in bpy.data.objects:
        #print(object)
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
    defaultDatablock.hide_set(True)
    defaultDatablock.select_set(True)
    defaultDatablock.hide_render = True

@persistent
def CheckSelectedObject(scene):
    """
    A scene handler used to configure the status of previously selected objects and multi-edit opportunities behind the scenes.
    """

    preferences = bpy.context.preferences
    addon_prefs = preferences.addons[__name__].preferences
    proxy = bpy.context.scene.CAPProxy
    #print("SCENE UPDATE")

    # If the active selected object changes or anything else about the selection, we need to update the edit toggles
    if bpy.context.active_object is not None:
        if bpy.context.active_object.name != addon_prefs.prev_selected_object or len(bpy.context.selected_objects) != addon_prefs.prev_selected_count:
            addon_prefs.prev_selected_object = bpy.context.active_object.name
            addon_prefs.prev_selected_count = len(bpy.context.selected_objects)

            for item in bpy.context.selected_objects:
                item.CAPObj.enable_edit = True

                for collection in item.users_collection:
                    collection.CAPCol.enable_edit = True
            
            # update the proxy objects with the current selection
            obj = bpy.context.active_object.CAPObj
            grp = bpy.context.active_object.users_collection[0].CAPCol

            proxy.disable_updates = True
            proxy.obj_enable_export = obj.enable_export
            proxy.obj_origin_point = obj.origin_point
            proxy.obj_location_preset = obj.location_preset
            proxy.obj_export_preset = obj.export_preset
            
            proxy.col_enable_export = grp.enable_export
            proxy.col_origin_point = grp.origin_point
            proxy.col_root_object = grp.root_object
            proxy.col_location_preset = grp.location_preset
            proxy.col_export_preset = grp.export_preset
            proxy.disable_updates = False

            return
    
    elif len(bpy.context.selected_objects) != addon_prefs.prev_selected_count:
        addon_prefs.prev_selected_count = len(bpy.context.selected_objects)
        return

#---------------------------------------------------------
# Keymaps
#---------------------------------------------------------

addon_keymaps = []

def add_hotkeys():
    wm = bpy.context.window_manager
    if wm.keyconfigs.addon:

        # Object Mode
        km = wm.keyconfigs.addon.keymaps.new(name='Object Mode')
        kmi = km.keymap_items.new('wm.call_menu_pie', 'E', 'PRESS')
        kmi.properties.name = "pie.capsule_main"
        # kmi.active = True
        addon_keymaps.append((km, kmi))


# TODO: This needs to actually work for multiple keymaps if I introduce more later
def remove_hotkeys():
    ''' clears all addon level keymap hotkeys stored in addon_keymaps '''
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    km = kc.keymaps['Object Mode']
    
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    
    wm.keyconfigs.addon.keymaps.remove(km)

    addon_keymaps.clear()


classes = (
    # export_formats
    CAP_FormatData_FBX,
    CAP_FormatData_OBJ,
    CAP_FormatData_GLTF,
    CAP_FormatData_Alembic,
    CAP_FormatData_Collada,
    CAP_FormatData_STL,
    CAP_FormatData_USD,

    # properties
    ObjectListItem, 
    CollectionListItem, 
    ActionListItem, 
    CAPSULE_Scene_Preferences, 
    CAPSULE_Object_Preferences, 
    CAPSULE_Collection_Preferences, 
    CAPSULE_Object_StateMachine, 
    # CAPSULE_Action_Preferences,
    CAPSULE_Proxy_Properties,

    # export_operators
    CAPSULE_OT_ExportAll,
    CAPSULE_OT_ExportSelected,

    # export_properties
    CAPSULE_ExportPreset, 
    CAPSULE_LocationPreset, 
    CAPSULE_ExportData,
    
    # export menu
    CAPSULE_OT_PieWarning,
    CAPSULE_OT_ToggleExport,
    CAPSULE_OT_LocationSelectObject,
    CAPSULE_OT_LocationSelectCollection,
    CAPSULE_MT_PieLocationObject,
    CAPSULE_MT_PieLocationCollection,
    CAPSULE_OT_ExportSelectObject,
    CAPSULE_OT_ExportSelectCollection,
    CAPSULE_MT_PieExportObject,
    CAPSULE_MT_PieExportCollection,
    CAPSULE_OT_PieObjectMenu,
    CAPSULE_OT_PieCollectionMenu,
    CAPSULE_OT_PieExport,
    CAPSULE_OT_PieMainMenu,

    # ui_operators
    CAPSULE_OT_Add_Path,
    CAPSULE_OT_Delete_Path,
    CAPSULE_OT_Add_Location_Path_Tag,
    CAPSULE_OT_Add_ExportPreset_Path_Tag,
    CAPSULE_OT_Add_Export,
    CAPSULE_OT_Delete_Export,
    CAPSULE_OT_Shift_Path_Up,
    CAPSULE_OT_Shift_Path_Down,
    CAPSULE_OT_Clear_List,
    CAPSULE_OT_Refresh_List,
    CAPSULE_OT_Reset_Scene,
    CAPSULE_OT_Reset_Defaults,
    CAPSULE_OT_UI_Group_Separate,
    CAPSULE_OT_UI_Group_Options,
    CAPSULE_OT_Refresh_Actions,
    CAPSULE_OT_Create_ExportData,
    CAPSULE_OT_Add_Stored_Presets,
    CAPSULE_OT_Delete_Presets,
    CAPSULE_OT_Store_Presets,

    # user_inferface
    CAPSULE_UL_Name,
    CAPSULE_UL_Object,
    CAPSULE_UL_Collection,
    CAPSULE_UL_Path_Default,
    CAPSULE_UL_Saved_Default,
    CAPSULE_UL_Export_Default,
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
        #print("Registering ", cls)
        bpy.utils.register_class(cls)

    # Assign datablocks now all classes have been registered.
    bpy.types.Scene.CAPScn = PointerProperty(name='Capsule Scene Properties', type=CAPSULE_Scene_Preferences)
    bpy.types.Object.CAPObj = PointerProperty(name='Capsule Object Properties', type=CAPSULE_Object_Preferences)
    bpy.types.Collection.CAPCol = PointerProperty(name='Capsule Collection Properties', type=CAPSULE_Collection_Preferences)
    # bpy.types.Action.CAPAcn = PointerProperty(type=CAPSULE_Action_Preferences)
    bpy.types.Object.CAPStm = PointerProperty(name='Capsule State Tracker', type=CAPSULE_Object_StateMachine)
    bpy.types.Object.CAPExp = PointerProperty(name='Capsule Export Presets', type=CAPSULE_ExportData)
    bpy.types.Scene.CAPProxy = PointerProperty(name='Capsule Scene Property Proxy', type=CAPSULE_Proxy_Properties)


    # Setup data and handlers
    export_presets.CreatePresets()
    bpy.app.handlers.load_pre.append(CreateDefaultData)
    bpy.app.handlers.depsgraph_update_post.append(CheckSelectedObject)

    add_hotkeys()

def unregister():
    """
    Unregisters itself and any extra pointer properties, handlers and keymaps from Blender.
    """

    remove_hotkeys()
    
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
    del bpy.types.Scene.CAPProxy


    # Unregister classes
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)



