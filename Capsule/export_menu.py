import bpy
from bpy.props import IntProperty, BoolProperty, FloatProperty, EnumProperty, PointerProperty, StringProperty, CollectionProperty
from bpy.types import Menu, Operator

from .update import CAP_Update_ObjectExport, UpdateObjectList
from .update_collections import CAP_Update_CollectionExport, UpdateCollectionList
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
        sel = context.selected_objects
        args = self.args.split(".")

        if args[0] == "OBJECT":

            for item in sel:
                if args[1] == "True":
                    item.CAPObj.enable_export = True
                    UpdateObjectList(context.scene, item, True)
                else:
                    item.CAPObj.enable_export = False
                    UpdateObjectList(context.scene, item, False)
        else:
            isEnabled = False
            if args[1] == "True":
                isEnabled = True

            for collection in collection_utils.GetSelectedObjectCollections():
                collection.CAPCol.enable_export = isEnabled
                UpdateCollectionList(context.scene, collection, isEnabled)

        scn.enable_sel_active = False
        return {'FINISHED'}

class CAPSULE_OT_LocationSelectObject(Operator):
    bl_idname = "capsule.location_select_object"
    bl_label = "Toggle Export"

    loc = IntProperty(default=-1)

    def execute(self, context):
        if self.loc != -1:
            context.active_object.CAPObj.location_default = str(self.loc + 1)
        return {'FINISHED'}

class CAPSULE_OT_LocationSelectCollection(Operator):
    bl_idname = "capsule.location_select_collection"
    bl_label = "Toggle Export"

    loc = IntProperty(default=-1)

    def execute(self, context):
        if self.loc != -1:

            for collection in collection_utils.GetSelectedObjectCollections():
                collection.CAPCol.location_default = str(self.loc + 1)

        return {'FINISHED'}

class CAPSULE_MT_PieLocationObject(Menu):
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
    A pie-specific operator for toggling the export status of the currently selected collections.
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
            context.active_object.CAPObj.export_default = str(self.loc + 1)
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

            for collection in collection_utils.GetSelectedObjectCollections():
                collection.CAPCol.export_default = str(self.loc + 1)

        return {'FINISHED'}

class CAPSULE_MT_PieExportObject(Menu):
    """
    Displays the export default options for objects.
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
        for loc in exp.file_presets:
            pie.operator("capsule.export_select_object", text=exp.file_presets[i].name, icon="SCRIPTWIN").loc = i
            i += 1

class CAPSULE_MT_PieExportCollection(Menu):
    """
    Displays the export default options for collections.
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
        for loc in exp.file_presets:
            pie.operator("capsule.export_select_collection", text=exp.file_presets[i].name, icon="SCRIPTWIN").loc = i
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
        pie.operator("wm.call_menu_pie", text="Set Export Preset", icon="SCRIPTWIN").name = "pie.export_object"
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
        pie.operator("wm.call_menu_pie", text="Set Export Preset", icon="SCRIPTWIN").name = "pie.export_collection"
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
            pie.operator("scene.cap_export", text="Export with Capsule", icon="EXPORT")
        else:
            pie.operator("scene.cap_export", text="Export with Capsule", icon="EXPORT")
