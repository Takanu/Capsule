import bpy
from bpy.props import IntProperty, BoolProperty, FloatProperty, EnumProperty, PointerProperty
from bpy.types import Menu, Panel, AddonPreferences, PropertyGroup, UIList
from rna_prop_ui import PropertyPanel


class Path_Default_List(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
            
        layout.prop(item, "name", text="", emboss=False)
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
        
        layout.label(text="Target")
        
        col_export = layout.column(align=True)
        col_export.alignment = 'EXPAND'
        col_export.prop(scn, "engine_select", text="", icon = "LOGIC")
        col_export.separator()
        
        if scn.engine_select is '1':
            col_export.prop(scn, "scale_100x")
            
        #elif scn.engine_select is '2':
            #col_export.prop(scn, "correct_rotation")
        
        col_export.separator()
        col_export.separator()
        col_export.operator("scene.gx_export")
        
        
class GX_Selection(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_label = "Selection"
    bl_category = "GEX"

    def draw(self, context):
        
        layout = self.layout
        
        # Check we have an active object
        if context.active_object is None:
            col_export = layout.column(align=True)
            col_export.alignment = 'EXPAND'
            col_export.label(text="Select an object to change settings")
            
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
            scn = context.scene.GXScn
            obj = context.object.GXObj
            ob = context.object
        
            col_export = layout.column(align=True)
            col_export.alignment = 'EXPAND'
            
            # Work out what kind of object label should be used
            if len(context.selected_objects) is 1:
                col_export.label(text=context.object.name, icon="OBJECT_DATA")
                
            else:
                objectCount = 0
                objectLabel = ""
                selected = []
                for sel in context.selected_objects:
                    if sel.type == 'MESH':
                        objectCount += 1
                        selected.append(sel)
                
                if objectCount == 1:
                    col_export.label(text=selected[0].name, icon="OBJECT_DATA")
                
                else:
                    objectLabel = str(objectCount) + " valid objects selected"
                    col_export.label(text=objectLabel, icon="OBJECT_DATA")
                
            col_export.separator()
            col_export.prop(obj, "enable_export")
            col_export.prop(obj, "apply_modifiers")
        
            col_export.separator()
            col_export.separator()
       
            col_export.label(text="Asset Type")
            col_export.separator()
            col_export.prop(obj, "asset_type", text="")

            if scn.engine_select is '1':
                col_export.separator()
                col_export.separator()
                col_export.label(text="Collision")
                col_export.prop(obj, "use_collision")
                col_export.prop(obj, "export_collision")
                #col_export.prop(obj, "generate_convex")
                col_export.prop(obj, "separate_collision")
        
                if obj.separate_collision is True:
                    col_export.separator()
                    col_collision = col_export.row(align=True)
                    col_collision.prop(obj, "collision_object", icon="OBJECT_DATA")
                    col_collision.operator("scene.gx_setcollision", text="", icon="FORWARD")
                    col_collision.operator("scene.gx_clearcollision", text="", icon="X")
                
            elif scn.engine_select is '2':
                col_export.separator()
                col_export.separator()
                col_export.label(text="Collision (exported as file)")
                col_export.prop(obj, "use_collision")
                #col_export.prop(obj, "generate_convex")
                col_export.prop(obj, "separate_collision")
        
                if obj.separate_collision is True:
                    col_export.separator()
                    col_collision = col_export.row(align=True)
                    col_collision.prop(obj, "collision_object", icon="OBJECT_DATA")
                    col_collision.operator("scene.gx_setcollision", text="", icon="FORWARD")
                    col_collision.operator("scene.gx_clearcollision", text="", icon="X")
        
            col_export.separator()
            col_export.separator()
            col_export.label(text="Location")
            col_export.separator()
            col_export.prop(obj, "location_default", text="")
        
        
        
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
     
        

        