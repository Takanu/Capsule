
import bpy
from bpy.props import IntProperty, BoolProperty, FloatProperty, EnumProperty, PointerProperty
from bpy.types import Menu, Panel, AddonPreferences, PropertyGroup, UIList
from rna_prop_ui import PropertyPanel

from .tk_utils import select
from .tk_utils import groups as group_utils

class GEX_Name_UIList(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):

            layout.prop(item, "name", text="", emboss=False)

class GEX_TagFilter_UIList(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):

            layout.prop(item, "name", text="", emboss=False)
            layout.prop(item, "use_tag", text="")

class Object_UIList(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):

        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__package__].preferences
        scn = context.scene.CAPScn

        layout.prop(item, "name", text="", emboss=False)
        layout.prop(item, "enable_export", text="")

        # A switch to change the extra tool on the Object list entries.
        if addon_prefs.list_feature != 'none':
            layout.prop(item, addon_prefs.list_feature, text="", emboss=False, icon='FULLSCREEN_EXIT')

        layout.prop(item, "remove", text="", icon="X", emboss=False)


    def draw_filter(self, context, layout):
        # Nothing much to say here, it's usual UI code...
        row = layout.row()

class Group_UIList(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):

        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__package__].preferences
        scn = context.scene.CAPScn

        layout.prop(item, "name", text="", emboss=False)
        layout.prop(item, "enable_export", text="")

        # A switch to change the extra tool on the Group list entries.
        if addon_prefs.list_feature != 'none':
            layout.prop(item, addon_prefs.list_feature, text="", emboss=False, icon='FULLSCREEN_EXIT')

        layout.prop(item, "remove", text="", icon="X", emboss=False)

    def draw_filter(self, context, layout):
        # Nothing much to say here, it's usual UI code...
        row = layout.row()

class Path_Default_UIList(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):

        scn = context.scene.CAPScn
        layout.prop(item, "name", text="", emboss=False)

class Saved_Default_UIList(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):

        scn = context.scene.CAPScn
        layout.prop(item, "name", text="", emboss=False)

class Export_Default_UIList(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):

        scn = context.scene.CAPScn
        layout.prop(item, "name", text="", emboss=False)

class Tag_Default_UIList(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):

        scn = context.scene.CAPScn
        layout.prop(item, "name", text="", emboss=False)

class Pass_Default_UIList(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):

        scn = context.scene.CAPScn
        layout.prop(item, "enable", text="")
        layout.prop(item, "name", text="", emboss=False)

class Action_UIList(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):

        scn = context.scene.CAPScn
        active = context.active_object

        icon = "OBJECT_DATA"

        if item.anim_type == '2':
            icon = "OBJECT_DATA"
        elif item.anim_type == '4':
            icon = "OUTLINER_OB_ARMATURE"

        layout.prop(item, "name", text="", icon=icon, emboss=False)
        layout.separator()

#//////////////////////// - USER INTERFACE - ////////////////////////

class CAP_Selection(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_label = "Selection"
    bl_category = "Capsule"

    def draw(self, context):

        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__package__].preferences

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
        selectTab = int(str(scn.selection_switch))

        layout = self.layout
        col_selection_title_tab = layout.row(align=True)
        col_selection_title_tab.prop(scn, "selection_switch", expand=True)

        if selectTab == 1:
            # Get the currently active object, whatever that might be.
            obj = None
            ob = None

            # If multi-edit is off, find it from the currently selected list entry.
            if addon_prefs.object_multi_edit is False:
                if len(scn.object_list) is not 0:
                    if len(scn.object_list) > scn.object_list_index:
                        entry = scn.object_list[scn.object_list_index]

                        for item in context.scene.objects:
                            if item.name == entry.name:
                                obj = item.CAPObj
                                ob = item

            # If multi-edit is on, find it from the scene.
            elif context.active_object is not None:
                obj = context.active_object.CAPObj
                ob = context.active_object

            elif len(context.selected_objects) > 0:
                obj = context.selected_objects[0].CAPObj
                ob = context.selected_objects[0]

            # Now we can build the UI
            if ob != None:
                if addon_prefs.object_multi_edit is False or len(context.selected_objects) == 1 or (context.active_object is not None and len(context.selected_objects) == 0):
                    col_selection_item_box = layout.box()
                    col_export = col_selection_item_box.column(align=True)
                    col_export.alignment = 'EXPAND'
                    col_export.label(text=ob.name, icon="OBJECT_DATA")
                    #col_export.separator()

                elif len(context.selected_objects) > 1:
                    objectCount = 0
                    objectLabel = ""
                    selected = []
                    for sel in context.selected_objects:
                        if sel.type == 'MESH':
                            objectCount += 1
                            selected.append(sel)

                    if objectCount == 1:
                        if type is 1:
                            col_selection_item_box = layout.box()
                            col_export = layout.column(align=True)
                            col_export.label(text=selected[0].name, icon="OBJECT_DATA")
                            #col_export.separator()

                    else:
                        col_selection_item_box = layout.box()
                        col_export = col_selection_item_box.column(align=True)
                        objectLabel = str(objectCount) + " objects selected"
                        col_export.label(text=objectLabel, icon="OBJECT_DATA")
                        #col_export.separator()

            if ob != None:
                obj_settings = layout.column(align=True)
                obj_settings.separator()
                obj_settings.prop(obj, "enable_export")
                obj_settings.prop(obj, "use_scene_origin")
                obj_settings.separator()
                obj_settings.separator()
                obj_settings.label(text="Location:")
                obj_settings.separator()
                obj_settings.prop(obj, "location_default", icon="FILESEL", text="")
                obj_settings.separator()
                obj_settings.label(text="Export Preset:")
                obj_settings.separator()
                obj_settings.prop(obj, "export_default", text="")
                obj_settings.separator()
                #obj_settings.label(text="Mesh Normals:")
                #obj_settings.separator()
                #obj_settings.prop(obj, "normals", text="")
                #obj_settings.separator()

            # If no object was eventually found, bring up warning labels.
            else:
                object_info = layout.column(align=True)
                object_info.separator()
                object_info.label(text="No objects selected.")

            layout.separator()


        #/////////////////////////////////////////////////////////////////
        #////////////////////////// GROUP UI /////////////////////////////
        #/////////////////////////////////////////////////////////////////
        elif selectTab is 2:

            # Get the first group pointer we need
            grp = None
            gr = None

            # If the multi-edit isnt on, just grab the list group
            if addon_prefs.group_multi_edit is False:
                if len(scn.group_list) > 0:
                    entry = scn.group_list[scn.group_list_index]

                    for group in group_utils.GetSceneGroups(context.scene, True):
                        if group.name == entry.name:
                            grp = group.CAPGrp
                            gr = group

                if gr is not None:
                    col_selection_item_box = layout.box()
                    group_label = col_selection_item_box.column(align=True)
                    group_label.alignment = 'EXPAND'
                    group_label.label(text=gr.name, icon="MOD_ARRAY")


            # Otherwise, just find it in a selection
            elif context.active_object is not None or len(context.selected_objects) > 0:
                groups_found = []
                groupLabel = ""
                for item in context.selected_objects:
                    for group in item.users_group:
                        groupAdded = False

                        for found_group in groups_found:
                            if found_group.name == group.name:
                                groupAdded = True

                        if groupAdded == False:
                            groups_found.append(group)

                if len(groups_found) == 1:
                    groupLabel = groups_found[0].name + " group selected."

                elif len(groups_found) > 1:
                    groupLabel = str(len(groups_found)) + " groups found."

                if context.active_object is not None:
                    if len(context.active_object.users_group) > 0:
                        for group in context.active_object.users_group:
                            gr = group
                            grp = group.CAPGrp
                            break

                if gr is not None and len(groups_found) == 0:
                    groupLabel = gr.name + " group selected."

                if groupLabel != "":
                    col_selection_item_box = layout.box()
                    group_label = col_selection_item_box.column(align=True)
                    group_label.alignment = 'EXPAND'
                    group_label.label(text=groupLabel, icon="MOD_ARRAY")



            #Get the group so we can obtain preference data from it
            #With Multi-Edit, we have to find a flexible approach to obtaining group data
            if grp != None:
                rawr = layout.column(align=True)
                rawr.separator()
                rawr.prop(grp, "enable_export", text="Enable Export")
                rawr.separator()
                rawr.separator()
                rawr.label(text="Origin Object:")

                rawr_row = layout.row(align=True)
                rawr_row.prop(grp, "root_object", icon="OBJECT_DATA", text="")
                rawr_row.operator("scene.cap_setroot", text="", icon="EYEDROPPER")
                rawr_row.operator("scene.cap_clearroot", text="", icon="X")

                rawr_other = layout.column(align=True)
                rawr_other.label(text="Location:")
                rawr_other.separator()
                rawr_other.prop(grp, "location_default", icon="FILESEL", text="")
                rawr_other.separator()
                rawr_other.label(text="Export Preset:")
                rawr_other.separator()
                rawr_other.prop(grp, "export_default", text="")
                #rawr_other.separator()
                #rawr_other.label(text="Mesh Normal Export:")
                #rawr_other.separator()
                #rawr_other.prop(grp, "normals", text="")

            # If no group was eventually found, bring up warning labels.
            else:
                group_info = layout.column(align=True)
                group_info.separator()
                group_info.label(text="No groups selected.")

            layout.separator()







        #////////////////////////// ANIMATION UI /////////////////////////
        #/////////////////////////////////////////////////////////////////
        # Currently broken, un-comment at your own peril!

        #col_location = layout.row(align=True)
        #col_location.template_list("Action_UIList", "rawr", ui, "action_list", ui, "action_list_index", rows=3, maxrows=10)

        #col_location.separator()

        #row_location = col_location.column(align=True)
        #row_location.operator("scene.cap_refactions", text="", icon="FILE_REFRESH")

        #layout.separator()

class CAP_List(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_label = "Export List"
    bl_category = "Capsule"

    @classmethod
    def poll(cls, context):
        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__package__].preferences
        try:
            exp = bpy.data.objects[addon_prefs.default_datablock].CAPExp
        except KeyError:
            return False
        return True

    def draw(self, context):
        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__package__].preferences
        scn = context.scene.CAPScn

        layout = self.layout
        listTab = int(str(scn.list_switch))

        list_switch = layout.row(align=True)
        list_switch.prop(scn, "list_switch", expand=True)

        col_location = layout.column(align=True)

        if listTab == 1:
            col_location.template_list("Object_UIList", "rawr", scn, "object_list", scn, "object_list_index", rows=3, maxrows=10)
        elif listTab == 2:
            col_location.template_list("Group_UIList", "rawr", scn, "group_list", scn, "group_list_index", rows=3, maxrows=10)

        col_location_options = layout.row(align=True)
        col_location_options.operator("scene.cap_clearlist", icon="X")
        col_location_options.operator("scene.cap_refreshlist", icon="FILE_REFRESH")

        col_export = layout.column(align=True)
        col_export.operator("scene.cap_export")
        layout.separator()


class CAP_Location(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_label = "Locations"
    bl_category = "Capsule"

    @classmethod
    def poll(cls, context):
        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__package__].preferences

        try:
            exp = bpy.data.objects[addon_prefs.default_datablock].CAPExp
        except KeyError:
            return False
        return True

    def draw(self, context):
        layout = self.layout

        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__package__].preferences
        exp = bpy.data.objects[addon_prefs.default_datablock].CAPExp
        scn = context.scene.CAPScn
        ob = context.object

        col_location = layout.row(align=True)
        col_location.template_list("Path_Default_UIList", "default", exp, "location_presets", exp, "location_presets_listindex", rows=3, maxrows=6)

        col_location.separator()

        row_location = col_location.column(align=True)
        row_location.operator("scene.cap_addpath", text="", icon="ZOOMIN")
        row_location.operator("scene.cap_deletepath", text="", icon="ZOOMOUT")
        #row_location.operator("scene.cap_shiftup", text="", icon="TRIA_UP")
        #row_location.operator("scene.cap_shiftdown", text="", icon="TRIA_DOWN")

        file = layout.column(align=True)
        file.alignment = 'EXPAND'

        count = 0
        for i, item in enumerate(exp.location_presets, 1):
            count += 1

        if exp.location_presets_listindex > -1 and exp.location_presets_listindex < count:
            file.label("File Path:")
            file.separator()
            file.prop(exp.location_presets[exp.location_presets_listindex], "path", text="")
