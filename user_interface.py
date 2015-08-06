import bpy
from bpy.props import IntProperty, BoolProperty, FloatProperty, EnumProperty, PointerProperty
from bpy.types import Menu, Panel, AddonPreferences, PropertyGroup, UIList
from rna_prop_ui import PropertyPanel


class Path_Default_List(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):

        groupData = None

        for group in bpy.data.groups:
            if group.name == item.name:
                groupData = group

        layout.prop(item, "name", text="", emboss=False)
        layout.prop(groupData.GXGrp, "export_group", text="")
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

        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons["GEX"].preferences

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

        #elif scn.engine_select is '2':
            #col_export.prop(scn, "correct_rotation")





class GX_SelectionObject(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_label = "Options"
    bl_category = "GEX"

    @classmethod
    def poll(cls, context):
        return True

    def draw(self, context):

        scn = context.scene.GXScn
        ui = context.scene.GXUI

        layout = self.layout
        obType = int(scn.object_switch)
        layout.row().prop(scn, "object_switch", expand=True)


        #/////////////// OBJECT SELECTION UI /////////////////////////////
        #/////////////////////////////////////////////////////////////////
        if obType == 1:

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
                col_export.prop(obj, "apply_modifiers")

                if obj.apply_modifiers is True:
                    col_export.prop(obj, "triangulate")

                col_export.separator()
                col_export.separator()



                if singleObject is False and skeletalFound is True and staticFound is True:
                    col_export.row().prop(scn, "type_switch", expand=True)
                    col_export.separator()
                    col_export.separator()
                    type = int(scn.type_switch)


                if type == 1:
                    if scn.engine_select is '1':
                        col_export.label(text="Collision")
                        col_export.prop(obj, "use_collision")
                        col_export.prop(obj, "export_collision")
                        #col_export.prop(obj, "generate_convex")
                        col_export.prop(obj, "separate_collision")

                        if obj.separate_collision is True:
                            col_export.separator()
                            col_collision = col_export.row(align=True)
                            col_collision.prop(obj, "collision_object", icon="OBJECT_DATA")
                            col_collision.operator("scene.gx_setcollision", text="", icon="EYEDROPPER")
                            col_collision.operator("scene.gx_clearcollision", text="", icon="X")

                    elif scn.engine_select is '2':
                        col_export.label(text="Collision (exported as file)")
                        col_export.prop(obj, "use_collision")
                        #col_export.prop(obj, "generate_convex")
                        col_export.prop(obj, "separate_collision")

                        if obj.separate_collision is True:
                            col_export.separator()
                            col_collision = col_export.row(align=True)
                            col_collision.prop(obj, "collision_object", icon="OBJECT_DATA")
                            col_collision.operator("scene.gx_setcollision", text="", icon="EYEDROPPER")
                            col_collision.operator("scene.gx_clearcollision", text="", icon="X")


                else:
                    col_export.label(text="Animation")
                    col_export.prop(obj, "export_anim")
                    col_export.prop(obj, "export_anim_file")
                    #col_export.prop(obj, "export_anim_actions")

                col_export.separator()
                col_export.separator()
                col_export.label(text="Location")
                col_export.separator()
                col_export.prop(obj, "location_default", text="")



        #////////////////////////// GROUP UI /////////////////////////////
        #/////////////////////////////////////////////////////////////////

        else:
            col_location = layout.row(align=True)
            col_location.template_list("Path_Default_List", "rawr", scn, "group_list", scn, "group_list_index", rows=3, maxrows=10)

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

                        setTable = layout.column_flow(columns=2, align=True)

                        rowRoot = setTable.row(align=True)
                        #rowRoot.alignment = 'LEFT'
                        rowRoot.label(text="Root Object:")
                        #rowRootSplit = rowRoot.split(percentage=2, align=True)

                        rowLoc = setTable.row(align=True)
                        rowLoc.label(text="Location:")

                        rowRootButtons = setTable.row(align=True)
                        rowRootButtons.prop(grp, "root_object", icon="OBJECT_DATA", text="")
                        rowRootButtons.operator("scene.gx_setroot", text="", icon="EYEDROPPER")
                        rowRootButtons.operator("scene.gx_clearroot", text="", icon="X")

                        rowRootButtons = setTable.row(align=True)
                        rowRootButtons.prop(grp, "location_default", icon="FILESEL", text="")
                        layout.separator()


                        exportOptions = layout.row(align=True)


                        if ui.group_options_dropdown is False:
                            exportOptions.operator("scene.gx_grpoptions", text="", icon="TRIA_RIGHT")
                            exportOptions.label(text="Export Options")


                        else:
                            exportOptions.operator("scene.gx_grpoptions", text="", icon="TRIA_DOWN")
                            exportOptions.label(text="Export Options")

                            exportOptionsPanel = layout.column(align=True)
                            exportOptionsPanel.prop(grp, "export_group")
                            exportOptionsPanel.prop(grp, "auto_assign")
                            exportOptionsPanel.prop(grp, "apply_modifiers")

                            exportOptionsModifier = exportOptionsPanel.column(align=True)

                            if grp.apply_modifiers is True:
                                exportOptionsModifier.enabled = True
                            else:
                                exportOptionsModifier.enabled = False

                            exportOptionsModifier.prop(grp, "triangulate")

                            exportOptionsPanel.separator()
                            exportOptionsPanel.separator()


                        exportSeparate = layout.row(align=True)

                        if grp.auto_assign is True:
                            exportSeparate.enabled = True
                        else:
                            exportSeparate.enabled = False




                        if ui.group_separate_dropdown is False or grp.auto_assign is False:
                            exportSeparate.operator("scene.gx_grpseparate", text="", icon="TRIA_RIGHT")
                            exportSeparate.label(text="Separate Export Slots")

                        else:
                            exportSeparate.operator("scene.gx_grpseparate", text="", icon="TRIA_DOWN")
                            exportSeparate.label(text="Separate Export Slots")

                            exportSeparatePanel = layout.column(align=True)
                            exportSeparatePanel.prop(grp, "export_lp", text="Separate Low-Poly")
                            exportSeparatePanel.prop(grp, "export_hp", text="Separate High-Poly")
                            exportSeparatePanel.prop(grp, "export_cg", text="Separate Cage")
                            exportSeparatePanel.prop(grp, "export_cx", text="Separate Collision")





            else:
                groupPrefs = layout.column(align=True)
                groupPrefs.label(text="No groups found, press refresh to find new groups.")

            layout.separator()



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
        col_location.template_list("Path_Default_List", "default", scn, "path_defaults", scn, "path_list_index", rows=3, maxrows=6)

        row_location = col_location.column(align=True)
        row_location.operator("scene.gx_addpath", text="", icon="ZOOMIN")
        row_location.operator("scene.gx_deletepath", text="", icon="ZOOMOUT")
        #row_location.operator("scene.gx_shiftup", text="", icon="TRIA_UP")
        #row_location.operator("scene.gx_shiftdown", text="", icon="TRIA_DOWN")

        col_list = layout.column(align=True)

        count = 0
        for i, item in enumerate(scn.path_defaults, 1):
            count += 1

        if scn.path_list_index > -1 and scn.path_list_index < count:
            col_list.label(text="Location")
            col_list.separator()
            col_list.prop(scn.path_defaults[scn.path_list_index], "path")


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
        col_settings.operator("scene.gx_resetscene", text="Reset Scene")
