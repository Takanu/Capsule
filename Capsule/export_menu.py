import bpy
from bpy.props import IntProperty, BoolProperty, FloatProperty, EnumProperty, PointerProperty, StringProperty, CollectionProperty
from bpy.types import Menu, Operator

class CAP_PieWarning(Operator):
    bl_idname = "capsule.pie_warning"
    bl_label = ""

    label = StringProperty(defaut="")

    def execute(self, context):
        self.report({'WARNING'}, self.label)
        return {"FINISHED"}

class CAP_ToggleObjectExport(Operator):
    bl_idname = "capsule.toggle_export"
    bl_label = "Toggle Export"

    args = StringProperty(default="")

    def execute(self, context):
        scn = context.scene.CAPScn
        sel = context.selected_objects
        args = self.args.split(".")
        scn.enable_sel_active = True

        if args[0] == "OBJECT":
            if args[1] == "True":
                context.active_object.CAPObj.enable_export = True
            else:
                context.active_object.CAPObj.enable_export = False
        else:
            enable = False
            if args[1] == "True":
                enable = True

            groups_found = []
            for item in context.selected_objects:
                for group in item.users_group:
                    groupAdded = False

                    for found_group in groups_found:
                        if found_group.name == group.name:
                            groupAdded = True

                    if groupAdded == False:
                        print("")
                        groups_found.append(group)


            for group in groups_found:
                group.CAPGrp.enable_export = enable

        scn.enable_sel_active = False
        return {'FINISHED'}

class CAP_LocationSelectObject(Operator):
    bl_idname = "capsule.location_select_object"
    bl_label = "Toggle Export"

    loc = IntProperty(default=-1)

    def execute(self, context):
        if self.loc != -1:
            context.active_object.CAPObj.location_default = str(self.loc + 1)
        return {'FINISHED'}

class CAP_LocationSelectGroup(Operator):
    bl_idname = "capsule.location_select_group"
    bl_label = "Toggle Export"

    loc = IntProperty(default=-1)

    def execute(self, context):
        if self.loc != -1:
            groups_found = []
            for item in context.selected_objects:
                for group in item.users_group:
                    groupAdded = False

                    for found_group in groups_found:
                        if found_group.name == group.name:
                            groupAdded = True

                    if groupAdded == False:
                        print("")
                        groups_found.append(group)

            for group in groups_found:
                group.CAPGrp.location_default = str(self.loc + 1)

        return {'FINISHED'}

class CAP_PieLocationObject(Menu):
    bl_idname = "pie.location_object"
    bl_label = "Select Location"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        obj = context.object.CAPObj
        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__package__].preferences
        exp = bpy.data.objects[addon_prefs.default_datablock].CAPExp

        i = 0
        for loc in exp.location_presets:
            pie.operator("capsule.location_select_object", text=exp.location_presets[i].name, icon="FILE_FOLDER").loc = i
            i += 1

class CAP_PieLocationGroup(Menu):
    bl_idname = "pie.location_group"
    bl_label = "Select Location"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        obj = context.object.CAPObj
        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__package__].preferences
        exp = bpy.data.objects[addon_prefs.default_datablock].CAPExp

        i = 0
        for loc in exp.location_presets:
            pie.operator("capsule.location_select_group", text=exp.location_presets[i].name, icon="FILE_FOLDER").loc = i
            i += 1

class CAP_ExportSelectObject(Operator):
    bl_idname = "capsule.export_select_object"
    bl_label = "Toggle Export"

    loc = IntProperty(default=-1)

    def execute(self, context):
        if self.loc != -1:
            context.active_object.CAPObj.export_default = str(self.loc + 1)
        return {'FINISHED'}

class CAP_ExportSelectGroup(Operator):
    bl_idname = "capsule.export_select_group"
    bl_label = "Toggle Export"

    loc = IntProperty(default=-1)

    def execute(self, context):
        if self.loc != -1:
            groups_found = []
            for item in context.selected_objects:
                for group in item.users_group:
                    groupAdded = False

                    for found_group in groups_found:
                        if found_group.name == group.name:
                            groupAdded = True

                    if groupAdded == False:
                        print("")
                        groups_found.append(group)

            for group in groups_found:
                group.CAPGrp.export_default = str(self.loc + 1)

        return {'FINISHED'}

class CAP_PieExportObject(Menu):
    bl_idname = "pie.export_object"
    bl_label = "Select Location"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        obj = context.object.CAPObj
        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__package__].preferences
        exp = bpy.data.objects[addon_prefs.default_datablock].CAPExp

        i = 0
        for loc in exp.file_presets:
            pie.operator("capsule.export_select_object", text=exp.file_presets[i].name, icon="SCRIPTWIN").loc = i
            i += 1

class CAP_PieExportGroup(Menu):
    bl_idname = "pie.export_group"
    bl_label = "Select Location"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        obj = context.object.CAPObj
        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__package__].preferences
        exp = bpy.data.objects[addon_prefs.default_datablock].CAPExp

        i = 0
        for loc in exp.file_presets:
            pie.operator("capsule.export_select_group", text=exp.file_presets[i].name, icon="SCRIPTWIN").loc = i
            i += 1

class CAP_PieObjectMenu(Menu):
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
        pie.operator("capsule.toggle_export", text="Enable Export", icon="ZOOMIN").args = "OBJECT.True"
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

class CAP_PieGroupMenu(Menu):
    bl_idname = "pie.capsule_group"
    bl_label = "Capsule Group Settings"

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
        pie.operator("capsule.toggle_export", text="Enable Export", icon="ZOOMIN").args = "GROUP.True"
        # 6 - RIGHT
        pie.operator("capsule.toggle_export", text="Disable Export", icon="X").args = "GROUP.False"
        # 2 - BOTTOM
        pie.operator("wm.call_menu_pie", text="Set Location", icon="FILE_FOLDER").name = "pie.location_group"
        # 8 - TOP
        pie.operator("wm.call_menu_pie", text="Set Export Preset", icon="SCRIPTWIN").name = "pie.export_group"
        # 7 - TOP - LEFT
        # 1 - BOTTOM - LEFT
        # 9 - TOP - RIGHT
        # 3 - BOTTOM - RIGHT

class CAP_PieMainMenu(Menu):
    bl_idname = "pie.capsule_main"
    bl_label = "Capsule Export"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        has_sel = False
        if len(context.selected_objects) > 0:
            pie.operator("wm.call_menu_pie", text="Object Settings", icon="OBJECT_DATA").name = "pie.capsule_object"
            # 6 - RIGHT
            pie.operator("wm.call_menu_pie", text="Group Settings", icon="GROUP").name = "pie.capsule_group"
            # 2 - BOTTOM
            pie.operator("scene.cap_export", text="Export with Capsule", icon="EXPORT")
        else:
            pie.operator("scene.cap_export", text="Export with Capsule", icon="EXPORT")
