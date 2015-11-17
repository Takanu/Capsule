import bpy
from bpy.props import IntProperty, BoolProperty, FloatProperty, EnumProperty, PointerProperty
from bpy.types import Menu, Panel, AddonPreferences, PropertyGroup, UIList
from rna_prop_ui import PropertyPanel

class Object_UIList(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):

        scn = context.scene.GXScn

        layout.prop(item, "name", text="", emboss=False)
        layout.prop(item, "enable_export", text="")
        layout.separator()


class Group_UIList(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):

        scn = context.scene.GXScn
        groupData = None

        for group in bpy.data.groups:
            if group.name == item.name:
                groupData = group

        layout.prop(item, "name", text="", emboss=False)
        layout.prop(groupData.GXGrp, "export_group", text="")
        layout.separator()


class Path_Default_UIList(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):

        scn = context.scene.GXScn
        layout.prop(item, "name", text="", emboss=False)
        layout.separator()

class Export_Default_UIList(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):

        scn = context.scene.GXScn
        layout.prop(item, "name", text="", emboss=False)
        layout.separator()

class Pass_Default_UIList(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):

        scn = context.scene.GXScn
        layout.prop(item, "name", text="", emboss=False)
        layout.separator()

class Action_UIList(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):

        scn = context.scene.GXScn
        active = context.active_object

        icon = "OBJECT_DATA"

        if item.anim_type == '2':
            icon = "OBJECT_DATA"

        elif item.anim_type == '4':
            icon = "OUTLINER_OB_ARMATURE"

        layout.prop(item, "name", text="", icon=icon, emboss=False)

        layout.separator()

#//////////////////////// - USER INTERFACE - ////////////////////////

#Generates the UI panel inside the 3D view
class GX_Export(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_label = "Export"
    bl_category = "GEX"

    def draw(self, context):
        layout = self.layout

        scn = context.scene.GXScn
        ob = context.object

        col_export = layout.column(align=True)
        col_export.operator("scene.gx_export")
        col_export.separator()

        #layout.label(text="Target")

        col_export = layout.column(align=True)
        col_export.alignment = 'EXPAND'
        col_export.prop(scn, "engine_select", text="", icon = "LOGIC")
        col_export.separator()

        if scn.engine_select is '1':
            col_export.prop(scn, "scale_100x")

        elif scn.engine_select is '2':
            col_export.prop(scn, "merge_export")



class GX_SelectionObject(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_label = "Selection"
    bl_category = "GEX"

    @classmethod
    def poll(cls, context):
        return True

    def draw(self, context):

        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__package__].preferences
        scn = context.scene.GXScn
        ui = context.scene.GXUI

        layout = self.layout
        obType = int(scn.object_switch)
        layout.row().prop(scn, "object_switch", expand=True)


        #/////////////// OBJECT SELECTION UI /////////////////////////////
        #/////////////////////////////////////////////////////////////////
        if obType == 1:

            col_location = layout.row(align=True)
            col_location.template_list("Object_UIList", "rawr", scn, "object_list", scn, "object_list_index", rows=3, maxrows=10)

            col_location.separator()

            row_location = col_location.column(align=True)
            row_location.operator("scene.gx_refobjects", text="", icon="FILE_REFRESH")

            layout.separator()

            # Check we have an active object
            if context.active_object is None or len(context.selected_objects) is 0:
                col_export = layout.column(align=True)
                col_export.alignment = 'EXPAND'
                col_export.label(text="Select an object to change settings")
                return

            # Ensure the active object isnt an incorrect type
            elif context.active_object.type != 'MESH':
                if len(context.selected_objects) == 1:
                    col_export = layout.column(align=True)
                    col_export.alignment = 'EXPAND'
                    col_export.label(text="Select a mesh object to change settings")
                else:
                    col_export = layout.column(align=True)
                    col_export.alignment = 'EXPAND'
                    col_export.label(text="Deselect the active non-mesh object")
                    col_export.label(text="to change settings")

            #elif context.active_object.name.find(addon_prefs.lp_tag) == -1:
                #col_export = layout.column(align=True)
                #col_export.alignment = 'EXPAND'
                #col_export.label(text="Select a low-poly object.")

            # Now the UI can load
            else:
                obj = context.object.GXObj
                ob = context.object

                # Need to figure out if only one object is selected and whather any selected objects have an armature
                singleObject = False
                skeletalFound = False
                staticFound = False
                type = 1

                if len(context.selected_objects) is 1:
                    singleObject = True

                for sel in context.selected_objects:
                    if sel.type == 'MESH':
                        foundLocal = False

                        for modifier in sel.modifiers:
                            if modifier.type == 'ARMATURE':
                                skeletalFound = True
                                foundLocal = True
                                type = 2

                        if foundLocal is False:
                            staticFound = True


                if skeletalFound is not True:
                    type = 1

                col_export = layout.column(align=True)
                col_export.alignment = 'EXPAND'

                # Work out what kind of object label should be used
                if len(context.selected_objects) is 1:
                    if type is 1:
                        col_export.label(text=context.object.name, icon="OBJECT_DATA")
                    else:
                        col_export.label(text=context.object.name, icon="OUTLINER_OB_ARMATURE")

                else:
                    objectCount = 0
                    objectLabel = ""
                    selected = []
                    for sel in context.selected_objects:
                        if sel.type == 'MESH':
                            objectCount += 1
                            selected.append(sel)

                    if objectCount == 1:
                        if type is 1:
                            col_export.label(text=selected[0].name, icon="OBJECT_DATA")

                    else:
                        objectLabel = str(objectCount) + " valid objects selected"
                        col_export.label(text=objectLabel, icon="OBJECT_DATA")

                col_export.separator()
                col_export.prop(obj, "enable_export")
                #col_export.prop(obj, "auto_assign")
                col_export.separator()
                col_export.separator()
                col_export.label(text="Location")
                col_export.separator()
                col_export.prop(obj, "location_default", icon="FILESEL", text="")
                col_export.separator()
                col_export.label(text="Export Settings:")
                col_export.separator()
                col_export.prop(obj, "export_default", text="")
                col_export.separator()


        #////////////////////////// GROUP UI /////////////////////////////
        #/////////////////////////////////////////////////////////////////

        else:
            col_location = layout.row(align=True)
            col_location.template_list("Group_UIList", "rawr", scn, "group_list", scn, "group_list_index", rows=3, maxrows=10)

            col_location.separator()

            row_location = col_location.column(align=True)
            row_location.operator("scene.gx_refgroups", text="", icon="FILE_REFRESH")

            layout.separator()

            #Get the group so we can obtain preference data from it
            if len(scn.group_list) > 0:
                entry = scn.group_list[scn.group_list_index]

                for group in bpy.data.groups:
                    if group.name == entry.name:
                        grp = group.GXGrp

                        rawr = layout.column(align=True)
                        rawr.prop(grp, "export_group")
                        rawr.separator()
                        rawr.label(text="Root Object:")

                        rawr_row = layout.row(align=True)
                        rawr_row.prop(grp, "root_object", icon="OBJECT_DATA", text="")
                        rawr_row.operator("scene.gx_setroot", text="", icon="EYEDROPPER")
                        rawr_row.operator("scene.gx_clearroot", text="", icon="X")

                        rawr_other = layout.column(align=True)
                        rawr_other.label(text="Location:")
                        rawr_other.separator()
                        rawr_other.prop(grp, "location_default", icon="FILESEL", text="")
                        rawr_other.separator()
                        rawr_other.label(text="Export Settings:")
                        rawr_other.separator()
                        rawr_other.prop(grp, "export_default", text="")
            else:
                groupPrefs = layout.column(align=True)
                groupPrefs.label(text="No groups found, press refresh to find new groups.")

            layout.separator()


        #////////////////////////// ANIMATION UI /////////////////////////
        #/////////////////////////////////////////////////////////////////

        #col_location = layout.row(align=True)
        #col_location.template_list("Action_UIList", "rawr", ui, "action_list", ui, "action_list_index", rows=3, maxrows=10)

        #col_location.separator()

        #row_location = col_location.column(align=True)
        #row_location.operator("scene.gx_refactions", text="", icon="FILE_REFRESH")

        #layout.separator()




class GX_Location(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_label = "Location Defaults"
    bl_category = "GEX"

    def draw(self, context):
        layout = self.layout

        scn = context.scene.GXScn
        ob = context.object

        col_location = layout.row(align=True)
        col_location.template_list("Path_Default_UIList", "default", scn, "location_defaults", scn, "location_defaults_index", rows=3, maxrows=6)

        col_location.separator()

        row_location = col_location.column(align=True)
        row_location.operator("scene.gx_addpath", text="", icon="ZOOMIN")
        row_location.operator("scene.gx_deletepath", text="", icon="ZOOMOUT")
        #row_location.operator("scene.gx_shiftup", text="", icon="TRIA_UP")
        #row_location.operator("scene.gx_shiftdown", text="", icon="TRIA_DOWN")

        file = layout.row(align=True)
        file.alignment = 'EXPAND'

        count = 0
        for i, item in enumerate(scn.location_defaults, 1):
            count += 1

        if scn.location_defaults_index > -1 and scn.location_defaults_index < count:
            file.prop(scn.location_defaults[scn.location_defaults_index], "path", text="Location")





class GX_ExportDefaults(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_label = "Export Defaults"
    bl_category = "GEX"

    def draw(self, context):
        layout = self.layout

        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__package__].preferences
        scn = context.scene.GXScn
        ob = context.object
        ui = context.scene.GXUI

        # Export UI
        col_export = layout.row(align=True)
        col_export.template_list("Export_Default_UIList", "default", addon_prefs, "export_defaults", addon_prefs, "export_defaults_index", rows=3, maxrows=6)

        col_export.separator()
        row_export = col_export.column(align=True)
        row_export.operator("scene.gx_addexport", text="", icon="ZOOMIN")
        row_export.operator("scene.gx_deleteexport", text="", icon="ZOOMOUT")

        if len(addon_prefs.export_defaults) > 0:

            currentExp = addon_prefs.export_defaults[addon_prefs.export_defaults_index]

            # Pass UI
            passUI = layout.column(align=True)
            passUI.separator()
            passUI.label(text="Passes")
            row_passes = passUI.row(align=True)
            row_passes.template_list("Pass_Default_UIList", "default", currentExp, "passes", currentExp, "passes_index", rows=3, maxrows=6)

            row_passes.separator()

            col_passes = row_passes.column(align=True)
            col_passes.operator("scene.gx_addpass", text="", icon="ZOOMIN")
            col_passes.operator("scene.gx_deletepass", text="", icon="ZOOMOUT")
            col_passes.separator()

            if len(currentExp.passes) > 0:

                # Pass Options UI
                currentPass = currentExp.passes[currentExp.passes_index]

                pass_settings = layout.column(align=True)
                pass_settings.separator()
                pass_settings.prop(currentPass, "file_suffix")
                pass_settings.prop(currentPass, "sub_directory")
                pass_settings.separator()
                pass_settings.separator()

                if ui.component_dropdown is False:
                    component_ui = pass_settings.row(align=True)
                    component_ui.prop(ui, "component_dropdown", icon="TRIA_RIGHT")
                    component_ui.label(text="Export Components")

                else:
                    component_ui = pass_settings.row(align=True)
                    component_ui.prop(ui, "component_dropdown", icon="TRIA_DOWN")
                    component_ui.label(text="Export Components")

                    component_list = pass_settings.column(align=True)
                    component_list.separator()
                    component_list.prop(currentPass, "export_lp")
                    component_list.prop(currentPass, "export_hp")
                    component_list.prop(currentPass, "export_cg")
                    component_list.prop(currentPass, "export_cx")
                    component_list.prop(currentPass, "export_ar")
                    component_list.prop(currentPass, "export_am")
                    component_list.separator()

                pass_settings.separator()

                if ui.options_dropdown is False:
                    options_ui = pass_settings.row(align=True)
                    options_ui.prop(ui, "options_dropdown", icon="TRIA_RIGHT")
                    options_ui.label(text="Export Options")

                else:
                    options_ui = pass_settings.row(align=True)
                    options_ui.prop(ui, "options_dropdown", icon="TRIA_DOWN")
                    options_ui.label(text="Export Options")

                    options_list = pass_settings.column(align=True)
                    options_list.separator()
                    options_list.prop(currentPass, "export_individual")
                    options_list.prop(currentPass, "apply_modifiers")
                    options_list.prop(currentPass, "triangulate")

        layout.separator()




class GX_Settings(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_label = "Settings"
    bl_category = "GEX"

    def draw(self, context):
        layout = self.layout

        scn = context.scene.GXScn
        ob = context.object

        col_settings = layout.column(align=True)
        col_settings.operator("scene.gx_resetsceneprops", text="Reset Scene")
        col_settings.operator("scene.gx_resetprefs", text="Reset Defaults")
