
import bpy
from bpy.props import IntProperty, BoolProperty, FloatProperty, EnumProperty, PointerProperty
from bpy.types import Menu, Panel, AddonPreferences, PropertyGroup, UIList
from rna_prop_ui import PropertyPanel

from .tk_utils import select
from .tk_utils import search as collection_utils

class CAPSULE_UL_Name(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):

            layout.prop(item, "name", text= "", emboss= False)

class CAPSULE_UL_Object(UIList):
    """Populates an export list based on properties that are representations of an object 
        rather than the actual object itself"""

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):

        preferences = context.preferences
        addon_prefs = preferences.addons[__package__].preferences
        scn = context.scene.CAPScn

        #layout.alignment = 'LEFT'

        # ////////////////
        # DELETED OBJECT LIST ITEM
        no_object = (item.object == None)
        if item.object != None:
            no_object = (bpy.context.scene.objects.get(item.object.name) == None)

        if no_object:
            # spaces are here to cheat on the layout spacing
            layout.label(text = "  Deleted Object")
            # layout.prop(item, "deleted_name", text = "", emboss = False)
            layout.prop(item, "remove", text = "", icon = "X", emboss= False)
            layout.active = False
            return


        # ////////////////
        # NORMAL OBJECT LIST ITEM
        cap_obj = item.object.CAPObj
        missing_data = (cap_obj.export_preset == '0' or cap_obj.location_preset == '0')

        layout.prop(item.object, "name", text = "", emboss = False)
        
        if missing_data:
            layout.prop(item, "missing_data", text = "", icon = "ERROR", emboss = False)
            layout.separator()
            
        layout.prop(item, "enable_export", text = "")

        # A switch to change the extra tool on the Object list entries.
        if addon_prefs.list_feature != 'none':
            layout.prop(item, addon_prefs.list_feature, text= "", emboss= False, icon= 'FULLSCREEN_EXIT')

        layout.prop(item, "remove", text= "", icon = "X", emboss= False)
        


    def draw_filter(self, context, layout):
        # Nothing much to say here, it's usual UI code...
        row = layout.row()


class CAPSULE_UL_Collection(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):

        preferences = context.preferences
        addon_prefs = preferences.addons[__package__].preferences
        scn = context.scene.CAPScn
        
        # ////////////////
        # DELETED COLLECTION LIST ITEM
        if item.collection == None:
            # spaces are here to cheat on the layout spacing
            layout.label(text = "  Deleted Collection")
            # layout.prop(item, "deleted_name", text = "", emboss = False)
            layout.prop(item, "remove", text = "", icon = "X", emboss= False)
            layout.active = False
            return


        # ////////////////
        # NORMAL COLLECTION LIST ITEM
        cap_col = item.collection.CAPCol
        missing_data = (cap_col.export_preset == '0' or cap_col.location_preset == '0')

        layout.prop(item.collection, "name", text= "", emboss= False)

        if missing_data:
            layout.prop(item, "missing_data", text = "", icon = "ERROR", emboss = False)
            layout.separator()

        layout.prop(item, "enable_export", text= "")

        # A switch to change the extra tool on the Collection list entries.
        if addon_prefs.list_feature != 'none':
            layout.prop(item, addon_prefs.list_feature, text= "", emboss= False, icon= 'FULLSCREEN_EXIT')

        layout.prop(item, "remove", text= "", icon = "X", emboss= False)

    def draw_filter(self, context, layout):
        # Nothing much to say here, it's usual UI code...
        row = layout.row()

class CAPSULE_UL_Path_Default(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):

        scn = context.scene.CAPScn
        layout.prop(item, "name", text= "", emboss= False)

class CAPSULE_UL_Saved_Default(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):

        scn = context.scene.CAPScn
        layout.prop(item, "name", text= "", emboss= False)

class CAPSULE_UL_Export_Default(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):

        scn = context.scene.CAPScn
        layout.prop(item, "name", text= "", emboss= False)

class CAPSULE_UL_Action(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):

        scn = context.scene.CAPScn
        active = context.active_object

        icon = "OBJECT_DATA"

        if item.anim_type == '2':
            icon = "OBJECT_DATA"
        elif item.anim_type == '4':
            icon = "OUTLINER_OB_ARMATURE"

        layout.prop(item, "name", text= "", icon=icon, emboss= False)
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
    bl_category = "Capsule"
    bl_context = "objectmode"
    bl_label = "Export Options"
    

    # bl_space_type = "PROPERTIES"
    # bl_region_type = "WINDOW"
    # bl_context = "render"
    # bl_label = "Selection"
    # bl_parent_id = "CAPSULE_PT_Header"

    def draw(self, context):

        preferences = context.preferences
        addon_prefs = preferences.addons[__package__].preferences
        scn = context.scene.CAPScn
        proxy = context.scene.CAPProxy
        selectTab = int(str(scn.selection_switch))

        layout = self.layout
        
        # UI Prompt for when the .blend Capsule data can no longer be found.
        try:
            cap_file = bpy.data.objects[addon_prefs.default_datablock].CAPFile
        except KeyError:
            Draw_CreateCapsuleData(layout)
            return

        col_selection_title_tab = layout.row(align= True)
        col_selection_title_tab.prop(scn, "selection_switch", expand= True)

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
                    object_count = 0
                    selected = []

                    for sel in context.selected_objects:
                        object_count += 1
                        selected.append(sel)

                    edit_enable_list = True
                    selection_label = str(object_count) + " objects selected"
                
                # No dropdown, indicate objects to be edited
                if addon_prefs.edit_enable_dropdown is False:
                    col_selection_item_box = layout.box()
                    col_edit_indicator = col_selection_item_box.row(align= True)

                    col_edit_indicator.prop(addon_prefs, "edit_enable_dropdown", text= "", icon= 'TRIA_RIGHT', emboss= False)
                    col_edit_indicator.alignment = 'EXPAND'
                    col_edit_indicator.label(text=selection_label, icon = "OBJECT_DATA")

                # Dropdown active, multiple objects selected.
                elif edit_enable_list is True:
                    col_selection_item_box = layout.box()
                    col_edit_indicator = col_selection_item_box.row(align= True)

                    col_edit_indicator.prop(addon_prefs, "edit_enable_dropdown", text= "", icon= 'TRIA_DOWN', emboss= False)
                    col_edit_indicator.alignment = 'EXPAND'
                    col_edit_indicator.label(text=selection_label, icon = "OBJECT_DATA")
                    col_edit_list = col_selection_item_box.column(align= True)

                    for item in context.selected_objects:
                        item_label = "Edit " + item.name
                        col_edit_list.prop(item.CAPObj, 'enable_edit', text=item_label)

                # Only one object selected, no need to show the list.
                else:
                    col_selection_item_box = layout.box()
                    col_edit_indicator = col_selection_item_box.row(align= True)

                    col_edit_indicator.prop(addon_prefs, "edit_enable_dropdown", text= "", icon= 'TRIA_DOWN', emboss= False)
                    col_edit_indicator.alignment = 'EXPAND'
                    col_edit_indicator.label(text=selection_label, icon = "OBJECT_DATA")
                    

            if ob != None:

                # now build the UI with that proxy
                obj_settings = layout.column(align= False)
                obj_settings.use_property_split = True
                obj_settings.use_property_decorate = False
                obj_settings.separator()

                obj_settings.prop(proxy, "obj_enable_export")
                obj_settings.separator()
                obj_settings.prop(proxy, "obj_origin_point")
                obj_settings.separator()
                obj_settings.prop(proxy, "obj_location_preset")
                obj_settings.separator()
                obj_settings.prop(proxy, "obj_export_preset")
                obj_settings.separator()
                obj_settings.separator()

                obj_settings.operator("scene.cap_export_all")
                obj_settings.operator("scene.cap_export_selected")

                # TODO 2.0 : Add this back in with other object/collection switches.
                #obj_settings.label(text= "Mesh Normals:")
                #obj_settings.separator()
                #obj_settings.prop(obj, "normals", text= "")
                #obj_settings.separator()

            # If no object was eventually found, bring up warning labels.
            else:
                object_info = layout.column(align= True)
                object_info.separator()
                object_info.label(text= "No objects selected.")

            layout.separator()


        #/////////////////////////////////////////////////////////////////
        #////////////////////////// COLLECTION UI /////////////////////////////
        #/////////////////////////////////////////////////////////////////
        elif selectTab == 2:
            
            # TODO : Rename these awful variable names
            # Get the first collection pointer we need
            grp = None


            collections = collection_utils.GetSelectedCollections()
            if len(collections) != 0:
                grp = collections[0]

            if len(collections) > 0:
                selection_label = ""
                edit_enable_list = False

                # LABEL - If we only have one collection
                if len(collections) == 1:
                    selection_label = collections[0].name

                elif len(collections) > 1:
                    edit_enable_list = True
                    selection_label = str(len(collections)) + " collections selected"

                if context.active_object is not None:
                    if len(context.active_object.users_collection) > 0:
                        for collection in context.active_object.users_collection:
                            gr = collection
                            grp = collection.CAPCol
                            break
                
                # Failsafe if we didn't find a collection label by now.
                if gr is not None and len(collections) == 0:
                    selection_label = gr.name + " collection selected."

                # If we have one, we can continue onwards!
                if selection_label != "":
                    
                    # No dropdown, indicate objects to be edited
                    if addon_prefs.edit_enable_dropdown is False:
                        col_selection_item_box = layout.box()
                        col_edit_indicator = col_selection_item_box.row(align= True)

                        col_edit_indicator.prop(addon_prefs, "edit_enable_dropdown", text= "", icon= 'TRIA_RIGHT', emboss= False)
                        col_edit_indicator.alignment = 'EXPAND'
                        col_edit_indicator.label(text=selection_label, icon = "MOD_ARRAY")
                    
                    # Dropdown active, multiple objects selected.
                    elif edit_enable_list is True:
                        col_selection_item_box = layout.box()
                        col_edit_indicator = col_selection_item_box.row(align= True)

                        col_edit_indicator.prop(addon_prefs, "edit_enable_dropdown", text= "", icon= 'TRIA_DOWN', emboss= False)
                        col_edit_indicator.alignment = 'EXPAND'
                        col_edit_indicator.label(text=selection_label, icon = "MOD_ARRAY")
                        col_edit_list = col_selection_item_box.column(align= True)

                        for item in collections:
                            item_label = "Edit " + item.name
                            col_edit_list.prop(item.CAPCol, 'enable_edit', text=item_label)

                    # Only one object selected, no need to show the list.
                    else:
                        col_selection_item_box = layout.box()
                        col_edit_indicator = col_selection_item_box.row(align= True)

                        col_edit_indicator.prop(addon_prefs, "edit_enable_dropdown", text= "", icon= 'TRIA_DOWN', emboss= False)
                        col_edit_indicator.alignment = 'EXPAND'
                        col_edit_indicator.label(text=selection_label, icon = "MOD_ARRAY")



            #Get the collection so we can obtain preference data from it
            #With Multi-Edit, we have to find a flexible approach to obtaining collection data
            if grp != None:

                # now build the UI with that proxy
                group_layout = layout.column(align= False)
                group_layout.use_property_split = True
                group_layout.use_property_decorate = False
                group_layout.separator()

                group_layout.prop(proxy, "col_enable_export")
                group_layout.separator()

                root_object_ui = group_layout.column(align= True)
                root_object_ui.prop(proxy, "col_origin_point")

                if proxy.col_origin_point == 'Object':
                    root_object_ui.prop(proxy, "col_root_object", text= " ")
                
                root_object_ui.separator()

                group_layout.prop(proxy, "col_child_export_option")
                group_layout.separator()
                group_layout.prop(proxy, "col_location_preset") 
                group_layout.separator()
                group_layout.prop(proxy, "col_export_preset")
                group_layout.separator()
                group_layout.separator()

                group_layout.operator("scene.cap_export_all")
                group_layout.operator("scene.cap_export_selected")

            # If no collection was eventually found, bring up warning labels.
            else:
                collection_info = layout.column(align= True)
                collection_info.separator()
                collection_info.label(text= "No groups selected.")

            layout.separator()





        #////////////////////////// ANIMATION UI /////////////////////////
        #/////////////////////////////////////////////////////////////////
        # Currently broken, un-comment at your own peril!

        #col_location = layout.row(align= True)
        #col_location.template_list("CAPSULE_UL_Action", "rawr", ui, "action_list", ui, "action_list_index", rows=3, maxrows=10)

        #col_location.separator()

        #row_location = col_location.column(align= True)
        #row_location.operator("scene.cap_refactions", text= "", icon = "FILE_REFRESH")

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
    #         cap_file = bpy.data.objects[addon_prefs.default_datablock].CAPFile
    #     except KeyError:
    #         return False
    #     return True

    def draw(self, context):
        preferences = context.preferences
        addon_prefs = preferences.addons[__package__].preferences
        scn = context.scene.CAPScn

        layout = self.layout

        try:
            cap_file = bpy.data.objects[addon_prefs.default_datablock].CAPFile
        except KeyError:
            Draw_CreateCapsuleData(layout)
            return

        listTab = int(str(scn.list_switch))

        list_switch = layout.row(align= True)
        list_switch.prop(scn, "list_switch", expand= True)

        col_location = layout.column(align= True)

        if listTab == 1:
            col_location.template_list("CAPSULE_UL_Object", "rawr", scn, "object_list", scn, "object_list_index", rows=3, maxrows=10)
        elif listTab == 2:
            col_location.template_list("CAPSULE_UL_Collection", "rawr", scn, "collection_list", scn, "collection_list_index", rows=3, maxrows=10)

        col_location_options = layout.row(align= True)
        col_location_options.operator("scene.cap_clearlist", icon = "X")
        col_location_options.operator("scene.cap_refreshlist", icon = "FILE_REFRESH")
        export_options = layout.column(align = True)
        export_options.operator("scene.cap_export_all", text = "Export All Active")
        export_options.separator()

        # TODO REALLY IMPORTANT: List selections can no longer rely on the object being available.

        if listTab == 1:
            obj = None
            ob = None

            if len(scn.object_list) != 0:
                if len(scn.object_list) > scn.object_list_index:
                    entry = scn.object_list[scn.object_list_index]
                    ob = entry.object
            
            if ob != None:
                obj = entry.object.CAPObj
                object_options_list = layout.column(align= False)
                object_options_list.use_property_split = True
                object_options_list.use_property_decorate = False
                object_options_list.separator()

                object_options_list.prop(obj, "origin_point")
                object_options_list.separator()
                object_options_list.prop(obj, "location_preset")
                object_options_list.separator()
                object_options_list.prop(obj, "export_preset")
        
        # Group selection
        elif listTab == 2:
            grp = None 
            gr = None

            if len(scn.collection_list) > 0:
                entry = scn.collection_list[scn.collection_list_index]
                grp = entry.collection.CAPCol
                gr = entry.collection
                        
            
            if gr is not None:
                group_options_list = layout.column(align= False)
                group_options_list.use_property_split = True
                group_options_list.use_property_decorate = False
                group_options_list.separator()
                
                root_object_ui = group_options_list.column(align= True)
                root_object_ui.prop(grp, "origin_point")

                if grp.origin_point == 'Object':
                    root_object_ui.prop(grp, "root_object", text= " ")
                
                root_object_ui.separator()

                group_options_list.prop(grp, "child_export_option")
                group_options_list.separator()
                group_options_list.prop(grp, "location_preset")
                group_options_list.separator()
                group_options_list.prop(grp, "export_preset")

        layout.separator()


class CAPSULE_PT_Location(Panel):
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_label = "File Locations"
    bl_parent_id = "CAPSULE_PT_Header"

    # @classmethod
    # def poll(cls, context):
    #     preferences = context.preferences
    #     addon_prefs = preferences.addons[__package__].preferences

    #     try:
    #         cap_file = bpy.data.objects[addon_prefs.default_datablock].CAPFile
    #     except KeyError:
    #         return False
    #     return True

    def draw(self, context):

        preferences = context.preferences
        addon_prefs = preferences.addons[__package__].preferences
        layout = self.layout

        # UI Prompt for when the .blend Capsule data can no longer be found.
        try:
            cap_file = bpy.data.objects[addon_prefs.default_datablock].CAPFile
        except KeyError:
            Draw_CreateCapsuleData(layout)
            return

        
        cap_file = bpy.data.objects[addon_prefs.default_datablock].CAPFile
        scn = context.scene.CAPScn
        ob = context.object

        col_location = layout.row(align= True)
        col_location.template_list("CAPSULE_UL_Path_Default", "default", cap_file, "location_presets", cap_file, "location_presets_listindex", rows=3, maxrows=6)

        col_location.separator()

        row_location = col_location.column(align= True)
        row_location.operator("scene.cap_addpath", text= "", icon = "ADD")
        row_location.operator("scene.cap_deletepath", text= "", icon = "REMOVE")
        #row_location.operator("scene.cap_shiftup", text= "", icon = "TRIA_UP")
        #row_location.operator("scene.cap_shiftdown", text= "", icon = "TRIA_DOWN")

        location_options = layout.column(align= False)
        location_options.use_property_split = True
        location_options.use_property_decorate = False
        location_options.separator()

        count = 0
        for i, item in enumerate(cap_file.location_presets, 1):
            count += 1

        if cap_file.location_presets_listindex > -1 and cap_file.location_presets_listindex < count:
            location_options.prop(cap_file.location_presets[cap_file.location_presets_listindex], "path")
            location_options.operator_menu_enum("scene.cap_add_location_path_tag", "path_tags")



def Draw_CreateCapsuleData(layout):

    # UI Prompt for when the .blend Capsule data can no longer be found.
    col_export = layout.column(align= True)
    col_export.label(text= "No Capsule for this .blend file has been found,")
    col_export.label(text= "Please press the button below to generate new data.")
    col_export.separator()
    col_export.separator()
    col_export.operator("cap.exportdata_create")
    col_export.separator()
    return
