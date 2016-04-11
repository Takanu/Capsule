import bpy, bmesh
from bpy.types import Operator
from bpy.props import IntProperty, BoolProperty, FloatProperty, EnumProperty, PointerProperty, StringProperty, CollectionProperty
from .definitions import SelectObject, FocusObject, ActivateObject, DuplicateObject, DuplicateObjects, DeleteObject, MoveObject, MoveObjects, CheckSuffix, CheckForTags
from mathutils import Vector

#///////////////// - LOCATION DEFAULTS - ///////////////////////////////////////////

class CAP_Add_Path(Operator):
    """Creates a new Location, that lets you define a file path for exports to go to."""

    bl_idname = "scene.cap_addpath"
    bl_label = "Add"

    def execute(self, context):
        print(self)

        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__package__].preferences
        exp = bpy.data.objects[addon_prefs.default_datablock].CAPExp

        newPath = exp.location_defaults.add()
        newPath.name = "Location " + str(len(exp.location_defaults))
        newPath.path = ""

        # Position the index to the current location of the
        #count = 0
        #for i, item in enumerate(scn.path_defaults, 1):
            #count += 1

        #oldIndex = scn.path_list_index

        #scn.path_defaults.move(count - 1, scn.path_list_index)
        #scn.path_list_index = oldIndex

        return {'FINISHED'}

class CAP_Delete_Path(Operator):
    """Deletes the selected Location from the list."""

    bl_idname = "scene.cap_deletepath"
    bl_label = "Remove"

    def execute(self, context):
        print(self)

        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__package__].preferences
        exp = bpy.data.objects[addon_prefs.default_datablock].CAPExp

        exp.location_defaults.remove(exp.location_defaults_index)

        return {'FINISHED'}



#///////////////// - EXPORT DEFAULTS - ///////////////////////////////////////////

class CAP_Add_Export(Operator):
    """Creates a new Export Preset."""

    bl_idname = "scene.cap_addexport"
    bl_label = "Add"

    def execute(self, context):
        print(self)

        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__package__].preferences
        exp = bpy.data.objects[addon_prefs.default_datablock].CAPExp

        newDefault = exp.export_defaults.add()
        newDefault.name = "Export " + str(len(exp.export_defaults))
        newDefault.path = ""

        # Ensure the tag index keeps within a window
        exp.export_defaults_index = len(exp.export_defaults) - 1

        return {'FINISHED'}

class CAP_Delete_Export(Operator):
    """Deletes the selected Export Preset from the list."""

    bl_idname = "scene.cap_deleteexport"
    bl_label = "Delete Export Preset"

    #StringProperty(default="Are you sure you wish to delete the selected preset?")

    def execute(self, context):
        print(self)

        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__package__].preferences
        exp = bpy.data.objects[addon_prefs.default_datablock].CAPExp

        exp.export_defaults.remove(exp.export_defaults_index)

        if exp.export_defaults_index > 0:
            exp.export_defaults_index -= 1

        return {'FINISHED'}


class CAP_Add_Tag(Operator):
    """Creates a new Tag."""

    bl_idname = "scene.cap_addtag"
    bl_label = "Add"


    def execute(self, context):
        print(self)

        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__package__].preferences
        exp = bpy.data.objects[addon_prefs.default_datablock].CAPExp

        # Add the tag into the main list
        export = exp.export_defaults[exp.export_defaults_index]
        newTag = export.tags.add()
        newTag.name = "Tag " + str(len(export.tags))

        # Now add it for all other passes in the export
        for expPass in export.passes:
            newPassTag = expPass.tags.add()
            newPassTag.name = newTag.name
            newPassTag.index = len(export.tags) - 1

        # Ensure the tag index keeps within a window
        export.tags_index = len(export.tags) - 1

        return {'FINISHED'}

class CAP_Delete_Tag(Operator):
    """Deletes the selected Tag from the list."""

    bl_idname = "scene.cap_deletetag"
    bl_label = "Remove"

    @classmethod
    def poll(cls, context):
        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__package__].preferences
        exp = bpy.data.objects[addon_prefs.default_datablock].CAPExp

        export = exp.export_defaults[exp.export_defaults_index]
        currentTag = export.tags[export.tags_index]

        if currentTag.x_user_deletable is True:
            return True

        else:
            return False

    def execute(self, context):
        print(self)

        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__package__].preferences
        exp = bpy.data.objects[addon_prefs.default_datablock].CAPExp

        export = exp.export_defaults[exp.export_defaults_index]
        export.tags.remove(export.tags_index)

        for expPass in export.passes:
            expPass.tags_index -= 1
            expPass.tags.remove(export.tags_index)

        if export.tags_index > 0:
            export.tags_index -= 1

        return {'FINISHED'}


class CAP_Add_Pass(Operator):
    """Creates a new Pass."""

    bl_idname = "scene.cap_addpass"
    bl_label = "Add"

    def execute(self, context):
        print(self)

        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__package__].preferences
        exp = bpy.data.objects[addon_prefs.default_datablock].CAPExp

        export = exp.export_defaults[exp.export_defaults_index]
        newPass = export.passes.add()
        newPass.name = "Pass " + str(len(export.passes))
        newPass.path = ""

        # Ensure the new pass has all the current tags
        for tag in export.tags:
            newPassTag = newPass.tags.add()
            newPassTag.name = tag.name
            newPassTag.index = len(export.tags) - 1

        # Ensure the tag index keeps within a window
        export.passes_index = len(export.passes) - 1

        return {'FINISHED'}

class CAP_Delete_Pass(Operator):
    """Deletes the selected Pass from the list."""

    bl_idname = "scene.cap_deletepass"
    bl_label = "Remove"

    def execute(self, context):
        print(self)

        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__package__].preferences
        exp = bpy.data.objects[addon_prefs.default_datablock].CAPExp

        export = exp.export_defaults[exp.export_defaults_index]
        export.passes.remove(export.passes_index)

        if export.passes_index > 0:
            export.passes_index -= 1

        return {'FINISHED'}

class CAP_Shift_Path_Up(Operator):
    """Moves the current entry in the list up by one"""

    bl_idname = "scene.cap_shiftup"
    bl_label = "Add"

    def execute(self, context):
        print(self)

        scn = context.scene.CAPScn
        obj = context.active_object.CAPObj

        scn.path_defaults.move(scn.path_list_index, scn.path_list_index - 1)
        scn.path_list_index -= 1

        return {'FINISHED'}

class CAP_Shift_Path_Down(Operator):
    """Moves the current entry in the list down by one"""

    bl_idname = "scene.cap_shiftdown"
    bl_label = "Remove"

    def execute(self, context):
        print(self)

        scn = context.scene.CAPScn
        obj = context.active_object.CAPObj

        scn.path_defaults.move(scn.path_list_index, scn.path_list_index + 1)
        scn.path_list_index += 1

        return {'FINISHED'}

#///////////////// - OBJECTS - //////////////////////////////////////////////////////
class CAP_Refresh_Objects(Operator):
    """Refreshes the list of objects that are marked for export."""

    bl_idname = "scene.cap_refobjects"
    bl_label = "Refresh"

    def execute(self, context):
        print(self)

        scn = context.scene.CAPScn

        scn.object_list.clear()

        for object in context.scene.objects:
            if object.CAPObj.enable_export is True:
                entry = scn.object_list.add()
                entry.name = object.name
                entry.prev_name = object.name
                entry.enable_export = object.CAPObj.enable_export


        return {'FINISHED'}


#///////////////// - GROUPS - //////////////////////////////////////////////////////


class CAP_Refresh_Groups(Operator):
    """Refreshes the list of available groups in the scene, that can be marked for export."""

    bl_idname = "scene.cap_refgroups"
    bl_label = "Refresh"

    def execute(self, context):
        print(self)

        scn = context.scene.CAPScn
        scn.group_list.clear()

        for group in bpy.data.groups:
            groupEntry = scn.group_list.add()
            groupEntry.name = group.name
            groupEntry.prev_name = group.name


        return {'FINISHED'}

class CAP_Set_Root_Object(Operator):
    """Allows you to set the Origin Object through an interactive tool.  Right-Click: Select the object you wish to be the origin point for the scene.  Esc - Quit the tool."""

    bl_idname = "scene.cap_setroot"
    bl_label = "Remove"

    def finish(self):
        # This def helps us tidy the shit we started
        # Restore the active area's header to its initial state.
        bpy.context.area.header_text_set()


    def execute(self, context):
        print("invoke!")
        print("Is this new?")

        scn = context.scene.CAPScn

        user_preferences = context.user_preferences
        self.addon_prefs = user_preferences.addons[__package__].preferences

        self.object = context.scene.objects.active
        context.window_manager.modal_handler_add(self)
        self._timer = context.window_manager.event_timer_add(0.05, context.window)

        bpy.ops.object.select_all(action='DESELECT')

        # Set the header text with USEFUL INSTRUCTIONS :O
        context.area.header_text_set(
            "Select the object you want to use as a root object.  " +
            "RMB: Select Collision Object, Esc: Exit"
        )

        return {'RUNNING_MODAL'}

    def modal(self,context,event):
        # If escape is pressed, exit
        if event.type in {'ESC'}:
            self.finish()

            # This return statement has to be within the same definition (cant defer to finish())
            return{'FINISHED'}

        # When an object is selected, set it as a child to the object, and finish.
        elif event.type == 'RIGHTMOUSE':

            # ALSO, check its not a dummy or origin object
            if context.selected_objects != None and len(context.selected_objects) == 1:

                entry = context.scene.CAPScn.group_list[context.scene.CAPScn.group_list_index]

                # Find the group we're getting a root object for
                for group in bpy.data.groups:
                    if group.name == entry.name:
                        print("Found Group: ", group.name)

                        # Make sure the root object being selected matches the groip
                        #for item in group.objects:
                            #if item.name == context.selected_objects[0].name:

                        group.CAPGrp.root_object = context.selected_objects[0].name
                        if self.object != None:
                            FocusObject(self.object)
                        self.finish()
                        return{'FINISHED'}

                        #self.report({'WARNING'}, 'The object selected is not in the same group, TRY AGAIN O_O')

                        #FocusObject(self.object)
                        #self.finish()
                        #return{'FINISHED'}

        return {'PASS_THROUGH'}

    def cancel(self, context):
        context.window_manager.event_timer_remove(self._timer)
        return {'FINISHED'}


class CAP_Clear_Root_Object(Operator):
    """Clears the currently chosen origin object for the group."""

    bl_idname = "scene.cap_clearroot"
    bl_label = "Remove"

    def execute(self, context):
        print(self)

        scn = context.scene.CAPScn
        obj = context.active_object.CAPObj

        entry = context.scene.CAPScn.group_list[context.scene.CAPScn.group_list_index]
        for group in bpy.data.groups:
            if group.name == entry.name:
                group.CAPGrp.root_object = ""
                return{'FINISHED'}

        return {'FINISHED'}


class CAP_Reset_Scene(Operator):
    """Resets all object and group variables in the scene.  Use at your own peril!"""

    bl_idname = "scene.cap_resetsceneprops"
    bl_label = "Reset Scene"

    def execute(self, context):
        print(self)

        exportedObjects = 0

        # Keep a record of the selected and active objects to restore later
        active = None
        selected = []

        for sel in context.selected_objects:
            if sel.name != context.active_object.name:
                selected.append(sel)

        active = context.active_object

        for group in bpy.scene.groups:
            obj.enable_export = False
            obj.root_object = False
            obj.location_default = '0'
            obj.export_default = '0'
            obj.normals = '1'

        for object in bpy.scene.objects:
            obj = object.CAPObj

            obj.enable_export = False
            obj.use_scene_origin = False
            obj.location_default = '0'
            obj.export_default = '0'
            obj.normals = '1'

        # Re-select the objects previously selected
        FocusObject(active)

        for sel in selected:
            SelectObject(sel)

        return {'FINISHED'}

class CAP_Reset_Scene(Operator):
    """Resets all location and export defaults in the file"""

    bl_idname = "scene.cap_resetprefs"
    bl_label = "Reset Scene"

    def execute(self, context):
        print(self)

        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__package__].preferences

        if addon_prefs == None:
            print("ADDON COULD NOT START, CONTACT DEVELOPER FOR ASSISTANCE")
            return

        # Figure out if an object already exists, if yes, DELETE IT
        for object in bpy.data.objects:
            print(object)
            if object.name == addon_prefs.default_datablock:
                DeleteObject(object)

        # Otherwise create the object using the addon preference data
        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.object.empty_add(type='PLAIN_AXES')

        defaultDatablock = bpy.context.scene.objects.active
        defaultDatablock.name = addon_prefs.default_datablock
        defaultDatablock.hide = True
        defaultDatablock.hide_render = True
        defaultDatablock.hide_select = True


        return {'FINISHED'}

class CAP_UI_Group_Separate(Operator):
    """Toggles the drop-down menu for separate group export options"""

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

class CAP_UI_Group_Options(Operator):
    """Toggles the drop-down menu for separate group export options"""

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


class CAP_Refresh_Actions(Operator):
    """Generates a list of groups to browse"""

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

class CAP_Tutorial_Tags(Operator):
    """Deletes the selected Export Preset from the list."""

    bl_idname = "cap_tutorial.tags"
    bl_label = "Tags let you automatically split objects in your passes by defining an object suffix/prefix and/or object type, that objects in the pass it's used in need to match in order to be included for export, enabiling you to create multiple different versions of an object or group export, without having to manually define them."

    StringProperty(default="Are you sure you wish to delete the selected preset?")

    def execute(self, context):
        print(self)

        #main(self, context)

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

        return {'FINISHED'}

class CAP_Create_ExportData(Operator):
    """Creates a new empty object from which Export Preset and Location data for the blend file is stored."""

    bl_idname = "cap.exportdata_create"
    bl_label = "Create Capsule Data"

    def execute(self, context):
        print(self)

        user_preferences = bpy.context.user_preferences
        addon_prefs = user_preferences.addons[__package__].preferences

        # Figure out if an object already exists, if yes do nothing
        for object in bpy.data.objects:
            print(object)
            if object.name == addon_prefs.default_datablock:
                self.report({'WARNING'}, "Capsule data for the blend file has been found, a new one will not be created.")
                return {'CANCELLED'}

        # Otherwise create the object using the addon preference data
        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.object.empty_add(type='PLAIN_AXES')

        defaultDatablock = bpy.context.scene.objects.active
        defaultDatablock.name = addon_prefs.default_datablock
        defaultDatablock.hide = True
        defaultDatablock.hide_render = True
        defaultDatablock.hide_select = True
        defaultDatablock.CAPExp.is_storage_object = True
        addon_prefs.data_missing = False

        self.report({'INFO'}, "Capsule data created.")
        return {'FINISHED'}

def ExchangePresetData(context, new_preset, old_preset):
    #First transfer the basic information
    pass

class CAP_Add_Stored_Presets(Operator):
    """Adds a stored preset into the usable Export Presets for this .blend file."""
    bl_idname = "cap.create_current_preset"
    bl_label = "Default Presets"

    def execute(self, context):

        # Get the current export data
        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__package__].preferences
        exp = bpy.data.objects[addon_prefs.default_datablock].CAPExp

        # Obtain the selected preset
        new_preset = exp.export_defaults.add()
        preset_len = int(addon_prefs.global_presets_enum) - 1
        CopyPreset(addon_prefs.global_presets[preset_len], new_preset)

        return {'FINISHED'}

class CAP_Delete_Presets(Operator):
    """Deletes the currently selected Global Preset."""
    bl_idname = "cap.delete_global_preset"
    bl_label = "Store Preset"

    @classmethod
    def poll(cls, context):
        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__package__].preferences

        if len(addon_prefs.global_presets) > 0:
            if addon_prefs.global_presets_enum != "0":
                export = addon_prefs.global_presets[int(addon_prefs.global_presets_enum) - 1]
                if export.x_global_user_deletable is True:
                    return True

        return False

    def execute(self, context):

        # Get the current export data
        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__package__].preferences
        exp = bpy.data.objects[addon_prefs.default_datablock].CAPExp

        # Obtain the selected preset
        addon_prefs.global_presets.remove(int(addon_prefs.global_presets_enum) - 1)
        addon_prefs.global_presets_enum = str(0)

        return {'FINISHED'}

class CAP_Store_Presets(Operator):
    """Stores the currently selected Export Preset as Plugin data, to enable it's use in other .blend files."""
    bl_idname = "cap.add_global_preset"
    bl_label = "Store Preset"

    @classmethod
    def poll(cls, context):
        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__package__].preferences
        exp = bpy.data.objects[addon_prefs.default_datablock].CAPExp

        if len(exp.export_defaults) > 0:
            return True

        else:
            return False


    def execute(self, context):

        # Get the current export data
        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__package__].preferences
        exp = bpy.data.objects[addon_prefs.default_datablock].CAPExp

        # Obtain the selected preset
        new_preset = addon_prefs.global_presets.add()
        CopyPreset(exp.export_defaults[exp.export_defaults_index], new_preset)

        return {'FINISHED'}

def CreatePresets():
    # -------------------------------------------------------------------------
    # Basic Export All
    # -------------------------------------------------------------------------
    user_preferences = bpy.context.user_preferences
    addon_prefs = user_preferences.addons[__package__].preferences
    exp = addon_prefs.global_presets

    export = exp.add()
    export.name = "Basic Export All (Preset)"
    export.description = "Creates a basic Export Preset with ideal settings for most purposes."
    export.axis_forward = "-Z"
    export.axis_up = "Y"
    export.global_scale = 1.0
    export.x_global_user_deletable = False

    passOne = export.passes.add()
    passOne.name = "Combined Pass"
    passOne.export_animation = True
    passOne.apply_modifiers = True
    passOne.triangulate = True

    export = None

    # -------------------------------------------------------------------------
    # UE4 Standard Template
    # -------------------------------------------------------------------------
    export = exp.add()
    export.name = "UE4 Standard (Preset)"
    export.description = "Creates an Export Preset for exporting FBX files for Unreal Engine 4, with optimised settings.  Enables the bundling of Collision objects in a format readable by UE4."
    export.axis_forward = "-Z"
    export.axis_up = "Y"
    export.global_scale = 1.0
    export.x_global_user_deletable = False

    tagHP = export.tags.add()
    tagHP.name = "High-Poly"
    tagHP.name_filter = "_HP"
    tagHP.name_filter_type = '1'
    tagHP.object_type = '2'
    tagHP.x_user_deletable = False
    tagHP.x_user_editable_type = True


    tagLP = export.tags.add()
    tagLP.name = "Low-Poly"
    tagLP.name_filter = "_LP"
    tagLP.name_filter_type = '1'
    tagLP.object_type = '2'
    tagLP.x_user_deletable = False
    tagLP.x_user_editable_type = True

    tagCG = export.tags.add()
    tagCG.name = "Cage"
    tagCG.name_filter = "_CG"
    tagCG.name_filter_type = '1'
    tagCG.object_type = '2'
    tagCG.x_user_deletable = False
    tagCG.x_user_editable_type = True

    tagCG.x_name_ext = "UCX_"
    tagCG.x_name_ext_type = '2'

    tagCX = export.tags.add()
    tagCX.name = "Collision"
    tagCX.name_filter = "_CX"
    tagCX.name_filter_type = '1'
    tagCX.object_type = '2'
    tagCX.x_user_deletable = False
    tagCX.x_user_editable_type = True
    tagCX.x_ue4_collision_naming = True

    tagAR = export.tags.add()
    tagAR.name = "Armature"
    tagAR.name_filter = "_AR"
    tagAR.name_filter_type = '1'
    tagAR.object_type = '7'
    tagAR.x_user_deletable = False
    tagAR.x_user_editable_type = False



    passOne = export.passes.add()
    passOne.name = "Combined Pass"
    passOne.export_animation = True
    passOne.apply_modifiers = True
    passOne.triangulate = True

    # Ensure the new pass has all the current tags
    for tag in export.tags:
        newPassTag = passOne.tags.add()
        newPassTag.name = tag.name
        newPassTag.index = len(export.tags) - 1
        newPassTag.use_tag = True

    passTwo = export.passes.add()
    passTwo.name = "Game-Ready Pass"
    passTwo.export_animation = True
    passTwo.apply_modifiers = True
    passTwo.triangulate = True

    i = 0

    # Ensure the new pass has all the current tags
    for tag in export.tags:
        newPassTag = passTwo.tags.add()
        newPassTag.name = tag.name
        newPassTag.index = len(export.tags) - 1

        if i != 0:
            newPassTag.use_tag = True

        i += 1

    export = None

    # -------------------------------------------------------------------------
    # Unity 5 Standard Template
    # -------------------------------------------------------------------------
    export = exp.add()
    export.name = "Unity 5 Standard (Preset)"
    export.description = "Creates an Export Preset for exporting FBX files for Unity 5, with optimised settings."
    export.axis_forward = "-Z"
    export.axis_up = "Y"
    export.global_scale = 1.0
    export.bake_space_transform = True
    export.x_global_user_deletable = False

    tagLP = export.tags.add()
    tagLP.name = "Low-Poly"
    tagLP.name_filter = "_LP"
    tagLP.name_filter_type = '1'
    tagLP.x_user_deletable = False

    tagHP = export.tags.add()
    tagHP.name = "High-Poly"
    tagHP.name_filter = "_HP"
    tagHP.name_filter_type = '1'
    tagHP.x_user_deletable = False

    tagCG = export.tags.add()
    tagCG.name = "Cage"
    tagCG.name_filter = "_CG"
    tagCG.name_filter_type = '1'
    tagCG.x_user_deletable = False

    tagCX = export.tags.add()
    tagCX.name = "Collision"
    tagCX.name_filter = "_CX"
    tagCX.name_filter_type = '1'
    tagCX.x_user_deletable = False

    tagAR = export.tags.add()
    tagAR.name = "Armature"
    tagAR.name_filter = "_AR"
    tagAR.name_filter_type = '1'
    tagAR.object_type = '7'
    tagAR.x_user_deletable = False

    passOne = export.passes.add()
    passOne.name = "Combined Pass"
    passOne.export_animation = True
    passOne.apply_modifiers = True
    passOne.triangulate = True

    # Ensure the new pass has all the current tags
    for tag in export.tags:
        newPassTag = passOne.tags.add()
        newPassTag.name = tag.name
        newPassTag.index = len(export.tags) - 1
        newPassTag.use_tag = True

    export = None

def CopyPreset(old_preset, new_preset):

    new_preset.name = old_preset.name
    new_preset.use_blend_directory = old_preset.use_blend_directory
    new_preset.use_sub_directory = old_preset.use_sub_directory
    new_preset.bundle_textures = old_preset.bundle_textures
    new_preset.filter_render = old_preset.filter_render
    new_preset.export_types = old_preset.export_types

    # OLD PASS COPYING
    for old_pass in old_preset.passes:
        new_pass = new_preset.passes.add()

        new_pass.name = old_pass.name
        new_pass.file_suffix = old_pass.file_suffix
        new_pass.sub_directory = old_pass.sub_directory

        # OLD TAG COPYING
        for old_passtag in old_pass.tags:
            new_passtag = new_pass.tags.add()

            new_passtag.name = old_passtag.name
            new_passtag.prev_name = old_passtag.prev_name
            new_passtag.index = old_passtag.index
            new_passtag.use_tag = old_passtag.use_tag

        new_pass.export_individual = old_pass.export_individual
        new_pass.export_animation = old_pass.export_animation
        new_pass.apply_modifiers = old_pass.apply_modifiers
        new_pass.triangulate = old_pass.triangulate
        new_pass.object_use_tags = old_pass.object_use_tags

    new_preset.passes_index = old_preset.passes_index

    for old_tag in old_preset.tags:
        new_tag = new_preset.tags.add()

        new_tag.name = old_tag.name
        new_tag.name_filter = old_tag.name_filter
        new_tag.name_filter_type = old_tag.name_filter_type
        new_tag.object_type = old_tag.object_type
        new_tag.x_user_deletable = old_tag.x_user_deletable
        new_tag.x_user_editable_type = old_tag.x_user_editable_type
        new_tag.x_ue4_collision_naming = old_tag.x_ue4_collision_naming

    new_preset.tags_index = old_preset.tags_index

    new_preset.global_scale = old_preset.global_scale
    new_preset.bake_space_transform = old_preset.bake_space_transform
    new_preset.axis_up = old_preset.axis_up
    new_preset.axis_forward = old_preset.axis_forward
    new_preset.apply_unit_scale = old_preset.apply_unit_scale

    new_preset.loose_edges = old_preset.loose_edges
    new_preset.tangent_space = old_preset.tangent_space

    new_preset.use_armature_deform_only = old_preset.use_armature_deform_only
    new_preset.add_leaf_bones = old_preset.add_leaf_bones
    new_preset.primary_bone_axis = old_preset.primary_bone_axis
    new_preset.secondary_bone_axis = old_preset.secondary_bone_axis
    new_preset.armature_nodetype = old_preset.armature_nodetype

    new_preset.bake_anim_use_all_bones = old_preset.bake_anim_use_all_bones
    new_preset.bake_anim_use_nla_strips = old_preset.bake_anim_use_nla_strips
    new_preset.bake_anim_use_all_actions = old_preset.bake_anim_use_all_actions
    new_preset.bake_anim_force_startend_keying = old_preset.bake_anim_force_startend_keying
    new_preset.use_default_take = old_preset.use_default_take
    new_preset.optimise_keyframes = old_preset.optimise_keyframes
    new_preset.bake_anim_step = old_preset.bake_anim_step
    new_preset.bake_anim_simplify_factor = old_preset.bake_anim_simplify_factor
    new_preset.x_global_user_deletable = old_preset.x_global_user_deletable
