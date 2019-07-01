
import bpy
from bpy.props import IntProperty, BoolProperty, FloatProperty, EnumProperty, PointerProperty
from bpy.types import Menu, Panel, AddonPreferences, PropertyGroup, UIList
from rna_prop_ui import PropertyPanel

from .tk_utils import select
from .tk_utils import collections as collection_utils

class CAPSULE_UL_Name(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):

            layout.prop(item, "name", text="", emboss=False)

class CAPSULE_UL_Object(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):

        preferences = context.preferences
        addon_prefs = preferences.addons[__package__].preferences
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

class CAPSULE_UL_Collection(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):

        preferences = context.preferences
        addon_prefs = preferences.addons[__package__].preferences
        scn = context.scene.CAPScn

        layout.prop(item, "name", text="", emboss=False)
        layout.prop(item, "enable_export", text="")

        # A switch to change the extra tool on the Collection list entries.
        if addon_prefs.list_feature != 'none':
            layout.prop(item, addon_prefs.list_feature, text="", emboss=False, icon='FULLSCREEN_EXIT')

        layout.prop(item, "remove", text="", icon="X", emboss=False)

    def draw_filter(self, context, layout):
        # Nothing much to say here, it's usual UI code...
        row = layout.row()

class CAPSULE_UL_Path_Default(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):

        scn = context.scene.CAPScn
        layout.prop(item, "name", text="", emboss=False)

class CAPSULE_UL_Saved_Default(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):

        scn = context.scene.CAPScn
        layout.prop(item, "name", text="", emboss=False)

class CAPSULE_UL_Export_Default(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):

        scn = context.scene.CAPScn
        layout.prop(item, "name", text="", emboss=False)

class CAPSULE_UL_Action(UIList):
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

class CAPSULE_PT_Header(Panel):
    bl_space_type = "PROPERTIES"
    bl_region_type = 'WINDOW'
    bl_context = "scene"
    bl_label = "Capsule"

    def draw(self, context):
        pass


class CAPSULE_PT_Selection(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "View"
    bl_context = "objectmode"
    bl_label = "Capsule"
    

    # bl_space_type = "PROPERTIES"
    # bl_region_type = "WINDOW"
    # bl_context = "render"
    # bl_label = "Selection"
    # bl_parent_id = "CAPSULE_PT_Header"

    def draw(self, context):

        preferences = context.preferences
        addon_prefs = preferences.addons[__package__].preferences

        # UI Prompt for when the .blend Capsule data can no longer be found.
        try:
            exp = bpy.data.objects[addon_prefs.default_datablock].CAPExp
        except KeyError:
            Draw_CreateCapsuleData(layout)


        scn = context.scene.CAPScn
        proxy = context.scene.CAPProxy
        selectTab = int(str(scn.selection_switch))

        layout = self.layout
        col_selection_title_tab = layout.row(align=True)
        col_selection_title_tab.prop(scn, "selection_switch", expand=True)

        if selectTab == 1:
            # Get the currently active object, whatever that might be.
            obj = None
            ob = None

            if context.active_object is not None:
                obj = context.active_object.CAPObj
                ob = context.active_object

            elif len(context.selected_objects) > 0:
                obj = context.selected_objects[0].CAPObj
                ob = context.selected_objects[0]

            # Now we can build the UI
            if ob != None:
                
                selection_label = ""
                edit_enable_list = False

                # LABEL - If we only have one object
                if len(context.selected_objects) == 1 or (context.active_object is not None and len(context.selected_objects) == 0):
                    selection_label = ob.name

                # LABEL - If we have MORE THAN ONE OBJECT
                elif len(context.selected_objects) > 1:
                    objectCount = 0
                    selected = []

                    for sel in context.selected_objects:
                        objectCount += 1
                        selected.append(sel)

                    edit_enable_list = True
                    selection_label = str(objectCount) + " objects selected"
                
                # No dropdown, indicate objects to be edited
                if addon_prefs.edit_enable_dropdown is False:
                    col_selection_item_box = layout.box()
                    col_edit_indicator = col_selection_item_box.row(align=True)

                    col_edit_indicator.prop(addon_prefs, "edit_enable_dropdown", text="", icon='TRIA_RIGHT', emboss=False)
                    col_edit_indicator.alignment = 'EXPAND'
                    col_edit_indicator.label(text=selection_label, icon="OBJECT_DATA")

                # Dropdown active, multiple objects selected.
                elif edit_enable_list is True:
                    col_selection_item_box = layout.box()
                    col_edit_indicator = col_selection_item_box.row(align=True)

                    col_edit_indicator.prop(addon_prefs, "edit_enable_dropdown", text="", icon='TRIA_DOWN', emboss=False)
                    col_edit_indicator.alignment = 'EXPAND'
                    col_edit_indicator.label(text=selection_label, icon="OBJECT_DATA")
                    col_edit_list = col_selection_item_box.column(align=True)

                    for item in context.selected_objects:
                        item_label = "Edit " + item.name
                        col_edit_list.prop(item.CAPObj, 'enable_edit', text=item_label)

                # Only one object selected, no need to show the list.
                else:
                    col_selection_item_box = layout.box()
                    col_edit_indicator = col_selection_item_box.row(align=True)

                    col_edit_indicator.prop(addon_prefs, "edit_enable_dropdown", text="", icon='TRIA_DOWN', emboss=False)
                    col_edit_indicator.alignment = 'EXPAND'
                    col_edit_indicator.label(text=selection_label, icon="OBJECT_DATA")
                    

            if ob != None:

                # now build the UI with that proxy
                obj_settings = layout.column(align=True)
                obj_settings.separator()
                obj_settings.prop(proxy, "obj_enable_export")
                obj_settings.separator()
                obj_settings.separator()
                obj_settings.label(text="Origin Point:")
                obj_settings.separator()
                obj_settings.prop(proxy, "obj_origin_point", text="")
                obj_settings.separator()
                obj_settings.label(text="Folder Location:")
                obj_settings.separator()
                obj_settings.prop(proxy, "obj_location_preset", icon="FILE_FOLDER", text="")
                obj_settings.separator()
                obj_settings.label(text="Export Preset:")
                obj_settings.separator()
                obj_settings.prop(proxy, "obj_export_preset", text="")
                obj_settings.separator()
                obj_settings.separator()
                obj_settings.separator()
                obj_settings.operator("scene.cap_export_all")
                obj_settings.operator("scene.cap_export_selected")

                # TODO 2.0 : Add this back in with other object/collection switches.
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
        #////////////////////////// COLLECTION UI /////////////////////////////
        #/////////////////////////////////////////////////////////////////
        elif selectTab is 2:

            # Get the first collection pointer we need
            grp = None
            gr = None

            if len(context.selected_objects) > 0:
                collections_found = collection_utils.GetSelectedObjectCollections()
                selection_label = ""
                edit_enable_list = False

                # LABEL - If we only have one collection
                if len(collections_found) == 1:
                    selection_label = collections_found[0].name

                elif len(collections_found) > 1:
                    edit_enable_list = True
                    selection_label = str(len(collections_found)) + " collections selected"

                if context.active_object is not None:
                    if len(context.active_object.users_collection) > 0:
                        for collection in context.active_object.users_collection:
                            gr = collection
                            grp = collection.CAPCol
                            break
                
                # Failsafe if we didn't find a collection label by now.
                if gr is not None and len(collections_found) == 0:
                    selection_label = gr.name + " collection selected."

                # If we have one, we can continue onwards!
                if selection_label != "":
                    
                    # No dropdown, indicate objects to be edited
                    if addon_prefs.edit_enable_dropdown is False:
                        col_selection_item_box = layout.box()
                        col_edit_indicator = col_selection_item_box.row(align=True)

                        col_edit_indicator.prop(addon_prefs, "edit_enable_dropdown", text="", icon='TRIA_RIGHT', emboss=False)
                        col_edit_indicator.alignment = 'EXPAND'
                        col_edit_indicator.label(text=selection_label, icon="MOD_ARRAY")
                    
                    # Dropdown active, multiple objects selected.
                    elif edit_enable_list is True:
                        col_selection_item_box = layout.box()
                        col_edit_indicator = col_selection_item_box.row(align=True)

                        col_edit_indicator.prop(addon_prefs, "edit_enable_dropdown", text="", icon='TRIA_DOWN', emboss=False)
                        col_edit_indicator.alignment = 'EXPAND'
                        col_edit_indicator.label(text=selection_label, icon="MOD_ARRAY")
                        col_edit_list = col_selection_item_box.column(align=True)

                        for item in collections_found:
                            item_label = "Edit " + item.name
                            col_edit_list.prop(item.CAPCol, 'enable_edit', text=item_label)

                    # Only one object selected, no need to show the list.
                    else:
                        col_selection_item_box = layout.box()
                        col_edit_indicator = col_selection_item_box.row(align=True)

                        col_edit_indicator.prop(addon_prefs, "edit_enable_dropdown", text="", icon='TRIA_DOWN', emboss=False)
                        col_edit_indicator.alignment = 'EXPAND'
                        col_edit_indicator.label(text=selection_label, icon="MOD_ARRAY")



            #Get the collection so we can obtain preference data from it
            #With Multi-Edit, we have to find a flexible approach to obtaining collection data
            if grp != None:

                # now build the UI with that proxy
                rawr = layout.column(align=True)
                rawr.separator()
                rawr.prop(proxy, "col_enable_export", text="Enable Export")
                rawr.separator()
                rawr.separator()
                rawr.label(text="Origin Point:")
                rawr.separator()
                rawr.prop(proxy, "col_origin_point", text="")
                
                if proxy.col_origin_point == 'Object':
                    rawr_row = rawr.row(align=True)
                    rawr_row.prop(proxy, "col_root_object", icon="OBJECT_DATA", text="")
                    rawr_row.operator("scene.cap_setroot", text="", icon="EYEDROPPER")
                    rawr_row.operator("scene.cap_clearroot", text="", icon="X")

                rawr_other = layout.column(align=True)
                rawr_other.label(text="Child Export Options:")
                rawr_other.separator()
                rawr_other.prop(proxy, "col_child_export_option", text="")
                rawr_other.separator()
                rawr_other.label(text="Export Location:")
                rawr_other.separator()
                rawr_other.prop(proxy, "col_location_preset", icon="FILE_FOLDER", text="")
                rawr_other.separator()
                rawr_other.label(text="Export Preset:")
                rawr_other.separator()
                rawr_other.prop(proxy, "col_export_preset", text="")
                rawr_other.separator()
                rawr_other.separator()
                rawr_other.operator("scene.cap_export_all")
                rawr_other.operator("scene.cap_export_selected")

            # If no collection was eventually found, bring up warning labels.
            else:
                collection_info = layout.column(align=True)
                collection_info.separator()
                collection_info.label(text="No groups selected.")

            layout.separator()





        #////////////////////////// ANIMATION UI /////////////////////////
        #/////////////////////////////////////////////////////////////////
        # Currently broken, un-comment at your own peril!

        #col_location = layout.row(align=True)
        #col_location.template_list("CAPSULE_UL_Action", "rawr", ui, "action_list", ui, "action_list_index", rows=3, maxrows=10)

        #col_location.separator()

        #row_location = col_location.column(align=True)
        #row_location.operator("scene.cap_refactions", text="", icon="FILE_REFRESH")

        #layout.separator()

class CAPSULE_PT_List(Panel):
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_label = "Export List"
    bl_parent_id = "CAPSULE_PT_Header"

    # @classmethod
    # def poll(cls, context):
    #     preferences = context.preferences
    #     addon_prefs = preferences.addons[__package__].preferences
    #     try:
    #         exp = bpy.data.objects[addon_prefs.default_datablock].CAPExp
    #     except KeyError:
    #         return False
    #     return True

    def draw(self, context):
        preferences = context.preferences
        addon_prefs = preferences.addons[__package__].preferences
        scn = context.scene.CAPScn

        layout = self.layout

        try:
            exp = bpy.data.objects[addon_prefs.default_datablock].CAPExp
        except KeyError:
            Draw_CreateCapsuleData(layout)
            return

        listTab = int(str(scn.list_switch))

        list_switch = layout.row(align=True)
        list_switch.prop(scn, "list_switch", expand=True)

        col_location = layout.column(align=True)

        if listTab == 1:
            col_location.template_list("CAPSULE_UL_Object", "rawr", scn, "object_list", scn, "object_list_index", rows=3, maxrows=10)
        elif listTab == 2:
            col_location.template_list("CAPSULE_UL_Collection", "rawr", scn, "collection_list", scn, "collection_list_index", rows=3, maxrows=10)

        col_location_options = layout.row(align=True)
        col_location_options.operator("scene.cap_clearlist", icon="X")
        col_location_options.operator("scene.cap_refreshlist", icon="FILE_REFRESH")

        if listTab == 1:
            obj = None
            ob = None

            if len(scn.object_list) is not 0:
                if len(scn.object_list) > scn.object_list_index:
                    entry = scn.object_list[scn.object_list_index]

                    for item in context.scene.objects:
                        if item.name == entry.name:
                            obj = item.CAPObj
                            ob = item
            
            if obj is not None:
                col_export_options = layout.column(align=True)
                col_export_options.separator()
                col_export_options.label(text="Origin Point:")
                col_export_options.separator()
                col_export_options.prop(obj, "origin_point", text="")
                col_export_options.separator()
                col_export_options.label(text="Folder Location:")
                col_export_options.separator()
                col_export_options.prop(obj, "location_preset", icon="FILE_FOLDER", text="")
                col_export_options.separator()
                col_export_options.label(text="Export Preset:")
                col_export_options.separator()
                col_export_options.prop(obj, "export_preset", text="")
        
        # Group selection
        elif listTab == 2:
            grp = None 
            gr = None

            if len(scn.collection_list) > 0:
                entry = scn.collection_list[scn.collection_list_index]

                for collection in collection_utils.GetSceneCollections(context.scene, True):
                    if collection.name == entry.name:
                        grp = collection.CAPCol
                        gr = collection
            
            if grp is not None:
                col_origin_point = layout.column(align=True)
                col_origin_point.separator()
                col_origin_point.label(text="Origin Point:")
                col_origin_point.separator()
                col_origin_point.prop(grp, "origin_point", text="")
                
                if grp.origin_point == 'Object':
                    col_origin_point.prop(grp, "root_object", icon="OBJECT_DATA", text="")

                col_export_options = layout.column(align=True)
                col_export_options.label(text="Child Export Options:")
                col_export_options.separator()
                col_export_options.prop(grp, "child_export_option", text="")
                col_export_options.separator()
                col_export_options.label(text="Export Location:")
                col_export_options.separator()
                col_export_options.prop(grp, "location_preset", icon="FILE_FOLDER", text="")
                col_export_options.separator()
                col_export_options.label(text="Export Preset:")
                col_export_options.separator()
                col_export_options.prop(grp, "export_preset", text="")

        layout.separator()


class CAPSULE_PT_Location(Panel):
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_label = "Locations"
    bl_parent_id = "CAPSULE_PT_Header"

    # @classmethod
    # def poll(cls, context):
    #     preferences = context.preferences
    #     addon_prefs = preferences.addons[__package__].preferences

    #     try:
    #         exp = bpy.data.objects[addon_prefs.default_datablock].CAPExp
    #     except KeyError:
    #         return False
    #     return True

    def draw(self, context):

        preferences = context.preferences
        addon_prefs = preferences.addons[__package__].preferences
        layout = self.layout

        # UI Prompt for when the .blend Capsule data can no longer be found.
        try:
            exp = bpy.data.objects[addon_prefs.default_datablock].CAPExp
        except KeyError:
            Draw_CreateCapsuleData(layout)
            return

        
        exp = bpy.data.objects[addon_prefs.default_datablock].CAPExp
        scn = context.scene.CAPScn
        ob = context.object

        col_location = layout.row(align=True)
        col_location.template_list("CAPSULE_UL_Path_Default", "default", exp, "location_presets", exp, "location_presets_listindex", rows=3, maxrows=6)

        col_location.separator()

        row_location = col_location.column(align=True)
        row_location.operator("scene.cap_addpath", text="", icon="ADD")
        row_location.operator("scene.cap_deletepath", text="", icon="REMOVE")
        #row_location.operator("scene.cap_shiftup", text="", icon="TRIA_UP")
        #row_location.operator("scene.cap_shiftdown", text="", icon="TRIA_DOWN")

        file = layout.column(align=True)
        file.alignment = 'EXPAND'

        count = 0
        for i, item in enumerate(exp.location_presets, 1):
            count += 1

        if exp.location_presets_listindex > -1 and exp.location_presets_listindex < count:
            file.label(text="File Path:")
            file.separator()
            file.prop(exp.location_presets[exp.location_presets_listindex], "path", text="")
            file.operator_menu_enum("scene.cap_add_path_tag", "path_tags")

class CAPSULE_PT_Export(Panel):
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_label = "Export Overview"
    bl_parent_id = "CAPSULE_PT_Header"

    def draw(self, context):

        preferences = context.preferences
        addon_prefs = preferences.addons[__package__].preferences
        layout = self.layout

        # UI Prompt for when the .blend Capsule data can no longer be found.
        try:
            exp = bpy.data.objects[addon_prefs.default_datablock].CAPExp
        except KeyError:
            Draw_CreateCapsuleData(layout)
            return

        exp = bpy.data.objects[addon_prefs.default_datablock].CAPExp

        export_buttons = layout.row(align=True)
        export_buttons.operator("scene.cap_export_all")




def Draw_CreateCapsuleData(layout):

    # UI Prompt for when the .blend Capsule data can no longer be found.
    col_export = layout.column(align=True)
    col_export.label(text="No Capsule for this .blend file has been found,")
    col_export.label(text="Please press the button below to generate new data.")
    col_export.separator()
    col_export.separator()
    col_export.operator("cap.exportdata_create")
    col_export.separator()
    return
