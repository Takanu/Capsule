import bpy
from bpy.props import IntProperty, BoolProperty, FloatProperty, EnumProperty, PointerProperty
from bpy.types import Menu, Panel, AddonPreferences, PropertyGroup, UIList
from rna_prop_ui import PropertyPanel

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

        if addon_prefs.list_feature == 'focus':
            layout.prop(item, "focus", text="", emboss=False, icon='FULLSCREEN_EXIT')
        elif addon_prefs.list_feature == 'sel':
            layout.prop(item, "sel", text="", emboss=False, icon='RESTRICT_SELECT_OFF')

        layout.separator()


class Group_UIList(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):

        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__package__].preferences
        scn = context.scene.CAPScn
        groupData = None

        for group in bpy.data.groups:
            if group.name == item.name:
                groupData = group

        if groupData is not None:
            layout.prop(item, "name", text="", emboss=False)
            layout.prop(groupData.CAPGrp, "export_group", text="")

            if addon_prefs.list_feature == 'focus':
                layout.prop(item, "focus", text="", emboss=False, icon='FULLSCREEN_EXIT')
            elif addon_prefs.list_feature == 'sel':
                layout.prop(item, "sel", text="", emboss=False, icon='RESTRICT_SELECT_OFF')

            layout.separator()


class Path_Default_UIList(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):

        scn = context.scene.CAPScn
        layout.prop(item, "name", text="", emboss=False)
        layout.separator()

class Export_Default_UIList(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):

        scn = context.scene.CAPScn
        layout.prop(item, "name", text="", emboss=False)
        layout.separator()

class Tag_Default_UIList(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):

        scn = context.scene.CAPScn
        layout.prop(item, "name", text="", emboss=False)
        layout.separator()

class Pass_Default_UIList(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):

        scn = context.scene.CAPScn
        layout.prop(item, "name", text="", emboss=False)
        layout.separator()

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

class CAP_SelectionObject(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_label = "Export"
    bl_category = "Capsule"

    @classmethod
    def poll(cls, context):
        return True

    def draw(self, context):

        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__package__].preferences

        if addon_prefs.data_missing is True:
            layout = self.layout
            col_export = layout.column(align=True)
            col_export.label("No Capsule for this .blend file has been found,")
            col_export.label("Please press the button below to generate new data.")
            col_export.separator()
            col_export.separator()
            col_export.operator("cap.exportdata_create")
            col_export.separator()
            return

        exp = bpy.data.objects[addon_prefs.default_datablock].CAPExp
        scn = context.scene.CAPScn
        ui = context.scene.CAPUI

        layout = self.layout
        obType = int(str(scn.object_switch))
        col_export = layout.column(align=True)
        col_export.operator("scene.cap_export")
        col_export.separator()
        object_switch = layout.row(align=True)
        object_switch.prop(scn, "object_switch", expand=True)


        #/////////////// OBJECT SELECTION UI /////////////////////////////
        #/////////////////////////////////////////////////////////////////
        if obType == 1:

            col_location = layout.row(align=True)
            col_location.template_list("Object_UIList", "rawr", scn, "object_list", scn, "object_list_index", rows=3, maxrows=10)
            col_location.separator()
            row_location = col_location.column(align=True)
            row_location.prop(addon_prefs, "object_multi_edit", text="", icon='RESTRICT_SELECT_OFF')

            if addon_prefs.object_list_autorefresh is False:
                row_location.operator("scene.cap_refobjects", text="", icon="FILE_REFRESH")

            layout.separator()

            # Get the currently active object, whatever that is
            obj = None
            ob = None

            # If we're taking objects from a
            if addon_prefs.object_multi_edit is False:
                if len(scn.object_list) is not 0:
                    if len(scn.object_list) > scn.object_list_index:
                        entry = scn.object_list[scn.object_list_index]

                        for item in context.scene.objects:
                            if item.name == entry.name:
                                obj = item.CAPObj
                                ob = item

            elif context.active_object is not None:
                obj = context.active_object.CAPObj
                ob = context.active_object

            elif len(context.selected_objects) > 0:
                obj = context.selected_objects[0].CAPObj
                ob = context.selected_objects[0]

            # Now we can build the UI
            if ob != None:
                if addon_prefs.object_multi_edit is False or len(context.selected_objects) == 1 or (context.active_object is not None and len(context.selected_objects) == 0):
                    col_export = layout.column(align=True)
                    col_export.alignment = 'EXPAND'
                    col_export.label(text=ob.name, icon="OBJECT_DATA")
                    col_export.separator()

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
                            col_export = layout.column(align=True)
                            col_export.label(text=selected[0].name, icon="OBJECT_DATA")
                            col_export.separator()

                    else:
                        col_export = layout.column(align=True)
                        objectLabel = str(objectCount) + " objects selected"
                        col_export.label(text=objectLabel, icon="OBJECT_DATA")
                        col_export.separator()

            if ob != None:

                obj_settings = layout.column(align=True)
                obj_settings.prop(obj, "enable_export")
                obj_settings.prop(obj, "use_scene_origin")
                obj_settings.separator()
                obj_settings.separator()
                obj_settings.label(text="Location")
                obj_settings.separator()
                obj_settings.prop(obj, "location_default", icon="FILESEL", text="")
                obj_settings.separator()
                obj_settings.label(text="Export Settings:")
                obj_settings.separator()
                obj_settings.prop(obj, "export_default", text="")
                obj_settings.separator()
                obj_settings.label(text="Mesh Normal Export:")
                obj_settings.separator()
                obj_settings.prop(obj, "normals", text="")
                obj_settings.separator()

            else:
                object_info = layout.column(align=True)
                if addon_prefs.object_multi_edit is False:
                    if len(scn.object_list) < (scn.object_list_index + 1) and len(scn.object_list) != 0:
                        object_info.label(text="Please select an object from the list to view")
                        object_info.label(text="it's settings.")
                    else:
                        object_info.label(text="No objects found, press refresh to find new objects,")
                        object_info.label(text="or change selection mode.")
                else:
                    object_info.label(text="No objects selected.  Please objects a group to edit it,")
                    object_info.label(text="or change selection mode.")



            layout.separator()



        #////////////////////////// GROUP UI /////////////////////////////
        #/////////////////////////////////////////////////////////////////

        else:
            col_location = layout.row(align=True)
            col_location.template_list("Group_UIList", "rawr", scn, "group_list", scn, "group_list_index", rows=3, maxrows=10)
            col_location.separator()
            row_location = col_location.column(align=True)
            row_location.prop(addon_prefs, "group_multi_edit", text="", icon='RESTRICT_SELECT_OFF')
            row_location.operator("scene.cap_refgroups", text="", icon="FILE_REFRESH")

            layout.separator()

            # Get the first group pointer we need
            grp = None
            gr = None

            # If the multi-edit isnt on, just grab the list group
            if addon_prefs.group_multi_edit is False:
                if len(scn.group_list) > 0:
                    entry = scn.group_list[scn.group_list_index]

                    for group in bpy.data.groups:
                        if group.name == entry.name:
                            grp = group.CAPGrp
                            gr = group

                if gr is not None:
                    group_label = layout.column(align=True)
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
                    group_label = layout.column(align=True)
                    group_label.alignment = 'EXPAND'
                    group_label.label(text=groupLabel, icon="MOD_ARRAY")



            #Get the group so we can obtain preference data from it
            #With Multi-Edit, we have to find a flexible approach to obtaining group data
            if grp != None:

                rawr = layout.column(align=True)
                rawr.prop(grp, "export_group", text="Enable Export")
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
                rawr_other.label(text="Export Settings:")
                rawr_other.separator()
                rawr_other.prop(grp, "export_default", text="")
                rawr_other.separator()
                rawr_other.label(text="Mesh Normal Export:")
                rawr_other.separator()
                rawr_other.prop(grp, "normals", text="")

            else:
                group_info = layout.column(align=True)
                if addon_prefs.group_multi_edit is False:
                    group_info.label(text="No groups found, press refresh to find new groups,")
                    group_info.label(text="or change selection mode.")
                else:
                    group_info.label(text="No groups selected.  Please select a group to edit it,")
                    group_info.label(text="or change selection mode.")

            layout.separator()


        #////////////////////////// ANIMATION UI /////////////////////////
        #/////////////////////////////////////////////////////////////////

        #col_location = layout.row(align=True)
        #col_location.template_list("Action_UIList", "rawr", ui, "action_list", ui, "action_list_index", rows=3, maxrows=10)

        #col_location.separator()

        #row_location = col_location.column(align=True)
        #row_location.operator("scene.cap_refactions", text="", icon="FILE_REFRESH")

        #layout.separator()




class CAP_Location(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_label = "Locations"
    bl_category = "Capsule"

    def draw(self, context):
        layout = self.layout

        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__package__].preferences
        exp = bpy.data.objects[addon_prefs.default_datablock].CAPExp
        scn = context.scene.CAPScn
        ob = context.object

        col_location = layout.row(align=True)
        col_location.template_list("Path_Default_UIList", "default", exp, "location_defaults", exp, "location_defaults_index", rows=3, maxrows=6)

        col_location.separator()

        row_location = col_location.column(align=True)
        row_location.operator("scene.cap_addpath", text="", icon="ZOOMIN")
        row_location.operator("scene.cap_deletepath", text="", icon="ZOOMOUT")
        #row_location.operator("scene.cap_shiftup", text="", icon="TRIA_UP")
        #row_location.operator("scene.cap_shiftdown", text="", icon="TRIA_DOWN")

        file = layout.row(align=True)
        file.alignment = 'EXPAND'

        count = 0
        for i, item in enumerate(exp.location_defaults, 1):
            count += 1

        if exp.location_defaults_index > -1 and exp.location_defaults_index < count:
            file.prop(exp.location_defaults[exp.location_defaults_index], "path", text="Location")
