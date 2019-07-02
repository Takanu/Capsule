
import bpy, bmesh, random

from mathutils import Vector
from bpy.types import Operator
from bpy.props import IntProperty, BoolProperty, FloatProperty, EnumProperty, PointerProperty, StringProperty, CollectionProperty

from .tk_utils import collections as collection_utils
from .tk_utils import select as select_utils
from .export_formats import CAP_ExportFormat
from . import export_presets

#///////////////// - LOCATION DEFAULTS - ///////////////////////////////////////////

class CAPSULE_OT_Add_Path(Operator):
    """Create a new location."""

    bl_idname = "scene.cap_addpath"
    bl_label = "Add"

    def execute(self, context):
        print(self)

        preferences = context.preferences
        addon_prefs = preferences.addons[__package__].preferences
        exp = bpy.data.objects[addon_prefs.default_datablock].CAPExp

        newPath = exp.location_presets.add()
        newPath.name = "Location " + str(len(exp.location_presets))
        newPath.path = ""

        # Position the index to the current location of the
        #count = 0
        #for i, item in enumerate(scn.path_defaults, 1):
            #count += 1

        #oldIndex = scn.path_list_index

        #scn.path_defaults.move(count - 1, scn.path_list_index)
        #scn.path_list_index = oldIndex

        return {'FINISHED'}

class CAPSULE_OT_Delete_Path(Operator):
    """Delete the selected location from the list."""

    bl_idname = "scene.cap_deletepath"
    bl_label = "Remove"

    def execute(self, context):
        print(self)

        preferences = context.preferences
        addon_prefs = preferences.addons[__package__].preferences
        exp = bpy.data.objects[addon_prefs.default_datablock].CAPExp

        exp.location_presets.remove(exp.location_presets_listindex)

        return {'FINISHED'}

class CAPSULE_OT_Add_Path_Tag(Operator):
    """Adds a new path tag to the currently selected path."""

    bl_idname = "scene.cap_add_path_tag"
    bl_label = "Add Path Tag"

    path_tags: EnumProperty(
        name="Add Path Tag",
        description="",
        items=(
        ('export_name', 'Export Name', 'Adds a folder with the name of the Object or Collection being exported.'),
        # ('object_type', 'Object Type', 'Adds a folder with the object type.'),
        # ('collection', 'Collection Name', 'Adds a folder with the collection name.'),
        ('blend_file_name', 'Blend File Name', 'Adds a folder with the blend file name.'),
        ('export_preset_name', 'Export Preset Name', 'Adds a folder with the Export Preset name used.'),
        ('export_date_ymd', 'Export Date (Year-Month-Day)', 'Adds a folder with the date of the export.'),
        ('export_date_dmy', 'Export Date (Day-Month-Year)', 'Adds a folder with the date of the export.'),
        ('export_date_mdy', 'Export Date (Month-Year-Day)', 'Adds a folder with the date of the export.'),
        ('export_time_hm', 'Export Time (Hour-Minute)', 'Adds a folder with the time of the export.'),
        ('export_time_hms', 'Export Time (Hour-Minute-Second)', 'Adds a folder with the time of the export.'),
        ),
    )

    def execute(self, context):
        print(self)

        preferences = context.preferences
        addon_prefs = preferences.addons[__package__].preferences
        exp = bpy.data.objects[addon_prefs.default_datablock].CAPExp
        
        # get the selected path
        path_index = exp.location_presets_listindex
        new_path = exp.location_presets[path_index].path

        # directory failsafe
        if new_path.endswith("/") == False:
            new_path += "/"

        # insert the selected option into the currently selected path
        new_path += "^"
        new_path += self.path_tags
        new_path += "^/"
        
        exp.location_presets[path_index].path = new_path

        return {'FINISHED'}

class CAPSULE_OT_Add_Export(Operator):
    """Create a new file preset."""

    bl_idname = "scene.cap_addexport"
    bl_label = "Add"

    def get_unique_id(self, context, exp):
        newID = random.randrange(0, 1000000)

        for preset in exp.export_presets:
            if preset.instance_id == newID:
                newID = self.get_unique_id(context, exp)

        return newID

    def execute(self, context):
        print(self)

        preferences = context.preferences
        addon_prefs = preferences.addons[__package__].preferences
        exp = bpy.data.objects[addon_prefs.default_datablock].CAPExp


        # make the new file preset
        newDefault = exp.export_presets.add()
        newDefault.name = "Export " + str(len(exp.export_presets))
        newDefault.path = ""

        # Ensure the tag index keeps within a window
        exp.export_presets_listindex = len(exp.export_presets) - 1

        return {'FINISHED'}



class CAPSULE_OT_Delete_Export(Operator):
    """Delete the selected file preset from the list."""

    bl_idname = "scene.cap_deleteexport"
    bl_label = "Delete Export Preset"

    #StringProperty(default="Are you sure you wish to delete the selected preset?")

    @classmethod
    def poll(cls, context):
        preferences = context.preferences
        addon_prefs = preferences.addons[__package__].preferences
        exp = bpy.data.objects[addon_prefs.default_datablock].CAPExp

        if len(exp.export_presets) > 0:
            return True

        return False

    def execute(self, context):
        print(self)

        preferences = context.preferences
        addon_prefs = preferences.addons[__package__].preferences
        exp = bpy.data.objects[addon_prefs.default_datablock].CAPExp

        # remove the data from both lists
        exp.export_presets.remove(exp.export_presets_listindex)

        # ensure the selected list index is within the list bounds
        if exp.export_presets_listindex > 0:
            exp.export_presets_listindex -= 1

        return {'FINISHED'}


class CAPSULE_OT_Shift_Path_Up(Operator):
    """Move the current entry in the list up by one"""

    bl_idname = "scene.cap_shiftup"
    bl_label = "Add"

    def execute(self, context):
        print(self)

        scn = context.scene.CAPScn
        obj = context.active_object.CAPObj

        scn.path_defaults.move(scn.path_list_index, scn.path_list_index - 1)
        scn.path_list_index -= 1

        return {'FINISHED'}

class CAPSULE_OT_Shift_Path_Down(Operator):
    """Move the current entry in the list down by one"""

    bl_idname = "scene.cap_shiftdown"
    bl_label = "Remove"

    def execute(self, context):
        print(self)

        scn = context.scene.CAPScn
        obj = context.active_object.CAPObj

        scn.path_defaults.move(scn.path_list_index, scn.path_list_index + 1)
        scn.path_list_index += 1

        return {'FINISHED'}

class CAPSULE_OT_Set_Root_Object(Operator):
    """Allows you to set the Origin Object through an interactive tool.  Right-Click: Select the object you wish to be the origin point for the scene.  Esc - Quit the tool."""

    bl_idname = "scene.cap_setroot"
    bl_label = "Remove"

    def finish(self):
        # This def helps us tidy the shit we started
        # Restore the active area's header to its initial state.
        bpy.context.area.header_text_set(None)


    def execute(self, context):
        scn = context.scene.CAPScn

        preferences = context.preferences
        self.addon_prefs = preferences.addons[__package__].preferences

        # Get collections and selections
        self.collections = collection_utils.GetEditableCollections(context)
        self.select_record = select_utils.SaveSelections()

        # Get key configs for click select
        wm = context.window_manager
        keyconfig = wm.keyconfigs.active
        self.select = getattr(keyconfig.preferences, "select_mouse", "LEFT")

        context.window_manager.modal_handler_add(self)
        self._timer = context.window_manager.event_timer_add(0.05, window=context.window)
        bpy.ops.object.select_all(action='DESELECT')

        # Set the header text with USEFUL INSTRUCTIONS :O
        # TODO 2.0 : Learn how to really format Python text, c'mon.
        if self.select == 'LEFT':
            context.area.header_text_set(
                "Select the object you want to use as a root object.  " +
                "Left Mouse: Select Collision Object, Esc: Exit"
            )
            self.event = 'LEFTMOUSE'
        else:
            context.area.header_text_set(
                "Select the object you want to use as a root object.  " +
                "Right Mouse: Select Collision Object, Esc: Exit"
            )
            self.event = 'RIGHTMOUSE'

        return {'RUNNING_MODAL'}

    def modal(self,context,event):
        # If escape is pressed, exit
        if event.type in {'ESC'}:
            select_utils.RestoreSelections(self.select_record)
            self.finish()
            return{'FINISHED'}

        # When an object is selected, set it as a child to the object, and finish.
        elif event.type == self.event:

            # Check only one object was selected
            if context.active_object != None and len(context.selected_objects) == 1:

                new_root_object = context.active_object.name
                for collection in self.collections:
                    collection.CAPCol.root_object = new_root_object

                bpy.ops.object.select_all(action='DESELECT')
                select_utils.RestoreSelections(self.select_record)

                self.finish()

                return{'FINISHED'}

        return {'PASS_THROUGH'}

    def cancel(self, context):
        context.window_manager.event_timer_remove(self._timer)
        return {'FINISHED'}


class CAPSULE_OT_Clear_Root_Object(Operator):
    """Clear the currently chosen origin object for the collection."""

    bl_idname = "scene.cap_clearroot"
    bl_label = "Remove"

    def execute(self, context):
        print(self)

        context.scene.CAPProxy.col_root_object = ""

        return {'FINISHED'}


class CAPSULE_OT_Clear_List(Operator):
    """Delete all objects from the export list, and un-mark them for export"""

    bl_idname = "scene.cap_clearlist"
    bl_label = "Delete All"

    def execute(self, context):
        print(self)

        scn = context.scene.CAPScn
        objectTab = int(str(scn.list_switch))

        if objectTab == 1:
            for object in context.scene.objects:
                obj = object.CAPObj
                obj.enable_export = False
                obj.in_export_list = False
            scn.object_list.clear()

        elif objectTab == 2:
            for collection in collection_utils.GetSceneCollections(context.scene, True):
                col = collection.CAPCol
                col.enable_export = False
                col.in_export_list = False
            scn.collection_list.clear()

        return {'FINISHED'}

class CAPSULE_OT_Refresh_List(Operator):
    """Rebuild the list based on available objects or collections in the scene."""

    bl_idname = "scene.cap_refreshlist"
    bl_label = "Refresh"

    def execute(self, context):
        print(self)

        scn = context.scene.CAPScn
        objectTab = int(str(scn.list_switch))

        if objectTab == 1:
            scn.object_list.clear()
            for obj in context.scene.objects:
                if obj.CAPObj.in_export_list is True:
                    entry = scn.object_list.add()
                    entry.name = obj.name
                    entry.prev_name = obj.name
                    entry.enable_export = obj.CAPObj.enable_export


        elif objectTab == 2:
            scn.collection_list.clear()
            for collection in collection_utils.GetSceneCollections(context.scene, True):
                if collection.CAPCol.in_export_list is True:
                        entry = scn.collection_list.add()
                        entry.name = collection.name
                        entry.prev_name = collection.name
                        entry.enable_export = collection.CAPCol.enable_export

        return {'FINISHED'}


class CAPSULE_OT_Reset_Scene(Operator):
    """Reset all object and collection variables in the scene.  Use at your own peril!"""

    bl_idname = "scene.cap_resetsceneprops"
    bl_label = "Reset Scene"

    def execute(self, context):
        print(self)

        self.export_stats['object_export_count'] = 0

        # Keep a record of the selected and active objects to restore later
        active = None
        selected = []

        for sel in context.selected_objects:
            if sel.name != context.active_object.name:
                selected.append(sel)

        active = context.active_object

        for collection in collection_utils.GetSceneCollections(context.scene, False):
            col = collection.CAPCol
            col.enable_export = False
            col.root_object = ""
            col.location_preset = '0'
            col.export_preset = '0'
            col.normals = '1'

        for object in context.scene.objects:
            obj = object.CAPObj
            obj.enable_export = False
            obj.origin_export = "Object"
            obj.location_preset = '0'
            obj.export_preset = '0'
            obj.normals = '1'

        bpy.ops.scene.cap_refobjects()
        bpy.ops.scene.cap_refgroups()

        # Re-select the objects previously selected
        select_utils.FocusObject(active)

        for sel in selected:
            SelectObject(sel)

        return {'FINISHED'}

class CAPSULE_OT_Reset_Defaults(Operator):
    """Reset all location and export defaults in the file"""

    bl_idname = "scene.cap_resetprefs"
    bl_label = "Reset Scene"

    def execute(self, context):
        print(self)

        preferences = context.preferences
        addon_prefs = preferences.addons[__package__].preferences

        if addon_prefs == None:
            print("ADDON COULD NOT START, CONTACT DEVELOPER FOR ASSISTANCE")
            return

        # Figure out if an object already exists, if yes, DELETE IT
        for object in bpy.data.objects:
            if object.name == addon_prefs.default_datablock:
                DeleteObject(object)

        # Otherwise create the object using the addon preference data
        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.object.empty_add(type='PLAIN_AXES')

        defaultDatablock = bpy.context.view_layer.objects.active
        defaultDatablock.name = addon_prefs.default_datablock
        defaultDatablock.hide_viewport = True
        defaultDatablock.hide_render = True
        defaultDatablock.hide_select = True


        return {'FINISHED'}

class CAPSULE_OT_UI_Group_Separate(Operator):
    """Toggle the drop-down menu for separate collection export options"""

    bl_idname = "scene.cap_grpseparate"
    bl_label = ""

    def execute(self, context):
        print(self)

        scn = context.scene.CAPScn
        ui = context.scene.CAPUI

        if ui.group_separate_dropdown is True:
            ui.group_separate_dropdown = False
        else:
            ui.group_separate_dropdown = True

        return {'FINISHED'}

class CAPSULE_OT_UI_Group_Options(Operator):
    """Toggle the drop-down menu for separate collection export options"""

    bl_idname = "scene.cap_grpoptions"
    bl_label = ""

    def execute(self, context):
        print(self)

        scn = context.scene.CAPScn
        ui = context.scene.CAPUI

        if ui.group_options_dropdown is True:
            ui.group_options_dropdown = False
        else:
            ui.group_options_dropdown = True

        return {'FINISHED'}

# TODO : Make relevant in 2.0
class CAPSULE_OT_Refresh_Actions(Operator):
    """Generate a list of collections to browse"""

    bl_idname = "scene.cap_refactions"
    bl_label = "Refresh"

    def execute(self, context):
        print(self)

        ui = context.scene.CAPUI
        active = context.active_object
        armature = None

        ui.action_list.clear()

        if active.animation_data is not None:
            actions = active.animation_data.nla_tracks
            activeAction = active.animation_data.action

            if activeAction is not None:
                entry = ui.action_list.add()
                entry.name = activeAction.name
                entry.prev_name = activeAction.name
                entry.anim_type = '1'

            for action in actions:
                entry = ui.action_list.add()
                entry.name = action.name
                entry.prev_name = action.name
                entry.anim_type = '2'


        modType = {'ARMATURE'}

        for modifier in active.modifiers:
            if modifier.type in modType:
                armature = modifier.object

        if armature is not None:
            if armature.animation_data is not None:
                actions = armature.animation_data.nla_tracks
                activeAction = armature.animation_data.action

                if activeAction is not None:
                    entry = ui.action_list.add()
                    entry.name = activeAction.name
                    entry.prev_name = activeAction.name
                    entry.anim_type = '3'

                for action in actions:
                    entry = ui.action_list.add()
                    entry.name = action.name
                    entry.prev_name = action.name
                    entry.anim_type = '4'


        return {'FINISHED'}


class CAPSULE_OT_Create_ExportData(Operator):
    """Create a new empty object for which Capsule data is stored, and where both file presets and other scene data is stored."""

    bl_idname = "cap.exportdata_create"
    bl_label = "Create Capsule Data"

    def execute(self, context):
        print(self)

        preferences = bpy.context.preferences
        addon_prefs = preferences.addons[__package__].preferences

        # Figure out if an object already exists, if yes do nothing
        for object in bpy.data.objects:
            print(object)
            if object.name == addon_prefs.default_datablock:
                self.report({'WARNING'}, "Capsule data for the blend file has been found, a new one will not be created.")
                return {'CANCELLED'}

        # Otherwise create the object using the addon preference data
        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.object.empty_add(type='PLAIN_AXES')

        defaultDatablock = bpy.context.view_layer.objects.active
        defaultDatablock.name = addon_prefs.default_datablock
        defaultDatablock.hide_viewport = True
        defaultDatablock.hide_render = True
        defaultDatablock.hide_select = True
        defaultDatablock.CAPExp.is_storage_object = True
        addon_prefs.data_missing = False

        self.report({'INFO'}, "Capsule data created.")
        return {'FINISHED'}


class CAPSULE_OT_Add_Stored_Presets(Operator):
    """Add the currently selected saved preset into the file presets list, enabling it's use for exports in this .blend file."""
    bl_idname = "cap.create_current_preset"
    bl_label = "Default Presets"

    @classmethod
    def poll(cls, context):
        preferences = context.preferences
        addon_prefs = preferences.addons[__package__].preferences
        exp = bpy.data.objects[addon_prefs.default_datablock].CAPExp

        if len(addon_prefs.saved_export_presets) > 0:
            return True

        else:
            return False

    def execute(self, context):

        # Get the current export data
        preferences = context.preferences
        addon_prefs = preferences.addons[__package__].preferences
        exp = bpy.data.objects[addon_prefs.default_datablock].CAPExp

        # Obtain the selected preset
        new_preset = exp.export_presets.add()
        export_presets.CopyPreset(addon_prefs.saved_export_presets[addon_prefs.saved_export_presets_index], new_preset)

        return {'FINISHED'}

class CAPSULE_OT_Delete_Presets(Operator):
    """Delete the currently selected saved preset."""
    bl_idname = "cap.delete_global_preset"
    bl_label = "Store Preset"

    @classmethod
    def poll(cls, context):
        preferences = context.preferences
        addon_prefs = preferences.addons[__package__].preferences

        if len(addon_prefs.saved_export_presets) > 0:
            export = addon_prefs.saved_export_presets[addon_prefs.saved_export_presets_index]
            
            if export.x_global_user_deletable is True:
                return True

        return False

    def execute(self, context):

        # Get the current export data
        preferences = context.preferences
        addon_prefs = preferences.addons[__package__].preferences
        exp = bpy.data.objects[addon_prefs.default_datablock].CAPExp

        # Obtain the selected preset
        addon_prefs.saved_export_presets.remove(addon_prefs.saved_export_presets_index)

        # Decrement the list selection
        if addon_prefs.saved_export_presets_index > 0:
            addon_prefs.saved_export_presets_index -= 1

        return {'FINISHED'}

class CAPSULE_OT_Store_Presets(Operator):
    """Store the currently selected export preset as a saved preset, to enable it's use in across .blend files."""
    bl_idname = "cap.add_global_preset"
    bl_label = "Store Preset"

    @classmethod
    def poll(cls, context):
        preferences = context.preferences
        addon_prefs = preferences.addons[__package__].preferences
        exp = bpy.data.objects[addon_prefs.default_datablock].CAPExp

        if len(exp.export_presets) > 0:
            return True

        else:
            return False


    def execute(self, context):

        # Get the current export data
        preferences = context.preferences
        addon_prefs = preferences.addons[__package__].preferences
        exp = bpy.data.objects[addon_prefs.default_datablock].CAPExp

        # Obtain the selected preset
        new_preset = addon_prefs.saved_export_presets.add()
        export_presets.CopyPreset(exp.export_presets[exp.export_presets_listindex], new_preset)

        return {'FINISHED'}


# ////////////////////// - CLASS REGISTRATION - ////////////////////////
# decided to do it all in __init__ instead, skipping for now.

# classes = (
#     CAPSULE_OT_Add_Path,
#     CAPSULE_OT_Delete_Path,
#     CAPSULE_OT_Add_Export,
#     CAPSULE_OT_Delete_Export,
#     CAPSULE_OT_Add_Tag,
#     CAPSULE_OT_Delete_Tag,
#     CAPSULE_OT_Add_Pass,
#     CAPSULE_OT_Delete_Pass,
#     CAPSULE_OT_Shift_Path_Up,
#     CAPSULE_OT_Shift_Path_Down,
#     CAPSULE_OT_Set_Root_Object,
#     CAPSULE_OT_Clear_Root_Object,
#     CAPSULE_OT_Clear_List,
#     CAPSULE_OT_Refresh_List,
#     CAPSULE_OT_Reset_Scene,
#     CAPSULE_OT_Reset_Defaults,
#     CAPSULE_OT_UI_Group_Separate,
#     CAPSULE_OT_UI_Group_Options,
#     CAPSULE_OT_Refresh_Actions,
#     CAPSULE_OT_Tutorial_Tags,
#     CAPSULE_OT_Create_ExportData,
#     CAPSULE_OT_Add_Stored_Presets,
#     CAPSULE_OT_Delete_Presets,
#     CAPSULE_OT_Store_Presets,
# )

# def register():
#     for cls in classes:
#         bpy.utils.register_class(cls)

# def unregister():
#     for cls in reversed(classes):
#         bpy.utils.unregister_class(cls)


