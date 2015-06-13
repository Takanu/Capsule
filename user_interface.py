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
        obj = context.object.GXObj
        ob = context.object
        
        layout.label(text="Target")
        
        col_export = layout.column(align=True)
        col_export.alignment = 'EXPAND'
        col_export.prop(scn, "engine_select", text="", icon = "LOGIC")
        col_export.separator()
        
        if scn.engine_select is '1':
            col_export.prop(scn, "scale_100x")
        
        col_export.separator()
        col_export.separator()
        col_export.operator("scene.gx_export")
        
class GX_Location(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_label = "Location Defaults"
    bl_category = "GEX"

    def draw(self, context):
        layout = self.layout
        
        scn = context.scene.GXScn
        obj = context.object.GXObj
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
     
        
class GX_Selection(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_label = "Selection"
    bl_category = "GEX"

    def draw(self, context):
        layout = self.layout
        
        scn = context.scene.GXScn
        obj = context.object.GXObj
        ob = context.object
        
        col_export = layout.column(align=True)
        col_export.alignment = 'EXPAND'
        col_export.prop(obj, "enable_export")
        
        col_export.separator()
        col_export.separator()
       
        #col_export.label(text="Asset Type")
        #col_export.separator()
        #col_export.prop(obj, "asset_type", text="")

        #col_export.separator()
        #col_export.separator()
        #col_export.label(text="Collision")
        col_export.prop(obj, "export_collision")
        #col_export.prop(obj, "generate_convex")
        #col_export.prop(obj, "collision_separate")
        
        if obj.collision_separate is True:
            col_export.separator()
            col_export.prop(obj, "collision_object", icon="OBJECT_DATA")
            
        #col_export.separator()
        #col_export.separator()
        col_export.prop(obj, "apply_modifiers")
        
        col_export.separator()
        col_export.separator()
        col_export.label(text="Location")
        col_export.separator()
        col_export.prop(obj, "location_default", text="")
        