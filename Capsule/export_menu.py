import bpy
from bpy.props import IntProperty, BoolProperty, FloatProperty, EnumProperty, PointerProperty, StringProperty, CollectionProperty
from bpy.types import Menu, Operator

from .update.update_objects import CAP_Update_ProxyObjectExport, UpdateObjectList
from .update.update_collections import CAP_Update_ProxyCollectionExport, UpdateCollectionList
from .tk_utils import collections as collection_utils

from . import tk_utils

class CAPSULE_OT_PieWarning(Operator):
    bl_idname = "capsule.pie_warning"
    bl_label = ""

    label = StringProperty(default="")

    def execute(self, context):
        self.report({'WARNING'}, self.label)
        return {"FINISHED"}

class CAPSULE_OT_ToggleExport(Operator):
    bl_idname = "capsule.toggle_export"
    bl_label = "Toggle Export"

    args = StringProperty(default="")

    def execute(self, context):

        print("*" * 40)
        scn = context.scene.CAPScn
        proxy = context.scene.CAPProxy
        sel = context.selected_objects
        args = self.args.split(".")

        if args[0] == "OBJECT":

            for item in sel:
                if args[1] == "True":
                    proxy.obj_enable_export = True
                else:
                    proxy.obj_enable_export = False
        else:
            isEnabled = False
            if args[1] == "True":
                isEnabled = True

            proxy.col_enable_export = isEnabled


        return {'FINISHED'}

class CAPSULE_OT_LocationSelectObject(Operator):
    bl_idname = "capsule.location_select_object"
    bl_label = "Toggle Export"

    loc = IntProperty(default=-1)

    def execute(self, context):
        if self.loc != -1:
            proxy = context.scene.CAPProxy
            proxy.obj_location_preset = str(self.loc + 1)
        return {'FINISHED'}

class CAPSULE_OT_LocationSelectCollection(Operator):
    bl_idname = "capsule.location_select_collection"
    bl_label = "Toggle Export"

    loc = IntProperty(default=-1)

    def execute(self, context):
        if self.loc != -1:
            proxy = context.scene.CAPProxy
            proxy.col_location_preset = str(self.loc + 1)

        return {'FINISHED'}

class CAPSULE_MT_PieLocationObject(Menu):
    """
    Shows the currently available locations that can be assigned to an object export.
    """
    bl_idname = "pie.location_object"
    bl_label = "Select Location"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        obj = context.object.CAPObj
        preferences = context.preferences
        addon_prefs = preferences.addons[__package__].preferences
        exp = bpy.data.objects[addon_prefs.default_datablock].CAPExp

        i = 0
        for loc in exp.location_presets:
            pie.operator("capsule.location_select_object", text=exp.location_presets[i].name, icon="FILE_FOLDER").loc = i
            i += 1

class CAPSULE_MT_PieLocationCollection(Menu):
    """
    Shows the currently available locations that can be assigned to an collection export.
    """
    bl_idname = "pie.location_collection"
    bl_label = "Select Location"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        obj = context.object.CAPObj
        preferences = context.preferences
        addon_prefs = preferences.addons[__package__].preferences
        exp = bpy.data.objects[addon_prefs.default_datablock].CAPExp

        i = 0
        for loc in exp.location_presets:
            pie.operator("capsule.location_select_collection", text=exp.location_presets[i].name, icon="FILE_FOLDER").loc = i
            i += 1

class CAPSULE_OT_ExportSelectObject(Operator):
    """
    A pie-specific operator for toggling the export status of the currently selected objects.
    """
    bl_idname = "capsule.export_select_object"
    bl_label = "Toggle Export"

    loc = IntProperty(default=-1)

    def execute(self, context):
        if self.loc != -1:
            proxy = context.scene.CAPProxy
            proxy.obj_export_preset = str(self.loc + 1)
        return {'FINISHED'}

class CAPSULE_OT_ExportSelectCollection(Operator):
    """
    A pie-specific operator for toggling the export status of the currently selected collections.
    """
    bl_idname = "capsule.export_select_collection"
    bl_label = "Toggle Export"

    loc = IntProperty(default=-1)

    def execute(self, context):
        if self.loc != -1:
            proxy = context.scene.CAPProxy
            proxy.col_export_preset = str(self.loc + 1)

        return {'FINISHED'}

class CAPSULE_MT_PieExportObject(Menu):
    """
    Shows the currently available export presets that can be assigned to an object export.
    """
    bl_idname = "pie.export_object"
    bl_label = "Select Location"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        obj = context.object.CAPObj
        preferences = context.preferences
        addon_prefs = preferences.addons[__package__].preferences
        exp = bpy.data.objects[addon_prefs.default_datablock].CAPExp

        i = 0
        for loc in exp.export_presets:
            pie.operator("capsule.export_select_object", text=exp.export_presets[i].name, icon="PREFERENCES").loc = i
            i += 1

class CAPSULE_MT_PieExportCollection(Menu):
    """
    Shows the currently available export presets that can be assigned to a collection export.
    """
    bl_idname = "pie.export_collection"
    bl_label = "Select Location"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        obj = context.object.CAPObj
        preferences = context.preferences
        addon_prefs = preferences.addons[__package__].preferences
        exp = bpy.data.objects[addon_prefs.default_datablock].CAPExp

        i = 0
        for loc in exp.export_presets:
            pie.operator("capsule.export_select_collection", text=exp.export_presets[i].name, icon="PREFERENCES").loc = i
            i += 1

class CAPSULE_OT_PieObjectMenu(Menu):
    """
    Pie menus to display object-specific Capsule options and settings.
    """
    bl_idname = "pie.capsule_object"
    bl_label = "Capsule Object Settings"

    @classmethod
    def poll(cls, context):
        has_sel = False
        if len(context.selected_objects) > 0:
            has_sel = True

        return has_sel

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        # 4 - LEFT
        pie.operator("capsule.toggle_export", text="Enable Export", icon="ADD").args = "OBJECT.True"
        # 6 - RIGHT
        pie.operator("capsule.toggle_export", text="Disable Export", icon="X").args = "OBJECT.False"
        # 2 - BOTTOM
        pie.operator("wm.call_menu_pie", text="Set Location", icon="FILE_FOLDER").name = "pie.location_object"
        # 8 - TOP
        pie.operator("wm.call_menu_pie", text="Set Export Preset", icon="PREFERENCES").name = "pie.export_object"
        # 7 - TOP - LEFT
        # 1 - BOTTOM - LEFT
        # 9 - TOP - RIGHT
        # 3 - BOTTOM - RIGHT

class CAPSULE_OT_PieCollectionMenu(Menu):
    """
    Pie menus to display collection-specific Capsule options and settings.
    """
    bl_idname = "pie.capsule_collection"
    bl_label = "Capsule Collection Settings"

    @classmethod
    def poll(cls, context):
        has_sel = False
        if len(context.selected_objects) > 0:
            has_sel = True

        return has_sel

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        # 4 - LEFT
        pie.operator("capsule.toggle_export", text="Enable Export", icon="ADD").args = "GROUP.True"
        # 6 - RIGHT
        pie.operator("capsule.toggle_export", text="Disable Export", icon="X").args = "GROUP.False"
        # 2 - BOTTOM
        pie.operator("wm.call_menu_pie", text="Set Location", icon="FILE_FOLDER").name = "pie.location_collection"
        # 8 - TOP
        pie.operator("wm.call_menu_pie", text="Set Export Preset", icon="PREFERENCES").name = "pie.export_collection"
        # 7 - TOP - LEFT
        # 1 - BOTTOM - LEFT
        # 9 - TOP - RIGHT
        # 3 - BOTTOM - RIGHT

class CAPSULE_OT_PieExport(Menu):
    """
    Pie menus for the base menu that appears when E is used.
    """

    bl_idname = "pie.capsule_export"
    bl_label = "Export..."

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        # 4 - LEFT
        pie.operator("scene.cap_export_all", text="Export All", icon="EXPORT")
        # 6 - RIGHT
        pie.operator("scene.cap_export_selected", text="Export Selected", icon="EXPORT")
        # 2 - BOTTOM
        # 8 - TOP
        # 7 - TOP - LEFT
        # 1 - BOTTOM - LEFT
        # 9 - TOP - RIGHT
        # 3 - BOTTOM - RIGHT

class CAPSULE_OT_PieMainMenu(Menu):
    """
    Pie menus for the base menu that appears when E is used.
    """

    bl_idname = "pie.capsule_main"
    bl_label = "Capsule Export"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        has_sel = False
        if len(context.selected_objects) > 0:
            pie.operator("wm.call_menu_pie", text="Object Settings", icon="OBJECT_DATA").name = "pie.capsule_object"
            # 6 - RIGHT
            pie.operator("wm.call_menu_pie", text="Collection Settings", icon="GROUP").name = "pie.capsule_collection"
            # 2 - BOTTOM
            pie.operator("wm.call_menu_pie", text="Export with Capsule", icon="EXPORT").name = "pie.capsule_export"
        else:
            pie.operator("wm.call_menu_pie", text="Export with Capsule", icon="EXPORT").name = "pie.capsule_export"
