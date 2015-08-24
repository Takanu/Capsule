import bpy, bmesh
from bpy.types import Operator
from .definitions import SelectObject, FocusObject, ActivateObject, DuplicateObject, DuplicateObjects, DeleteObject, MoveObject, MoveObjects, GetPluginDefaults
from mathutils import Vector

class GT_Add_Path(Operator):
    """Creates a path from the menu"""

    bl_idname = "scene.gx_addpath"
    bl_label = "Add"

    def execute(self, context):
        print(self)

        defaults = GetPluginDefaults()
        newPath = defaults.location_defaults.add()
        newPath.name = "Location " + str(len(defaults.location_defaults))
        newPath.path = ""

        # Position the index to the current location of the
        #count = 0
        #for i, item in enumerate(scn.path_defaults, 1):
            #count += 1

        #oldIndex = scn.path_list_index

        #scn.path_defaults.move(count - 1, scn.path_list_index)
        #scn.path_list_index = oldIndex

        return {'FINISHED'}

class GT_Delete_Path(Operator):
    """Deletes the selected path from the menu"""

    bl_idname = "scene.gx_deletepath"
    bl_label = "Remove"

    def execute(self, context):
        print(self)

        defaults = GetPluginDefaults()
        defaults.location_defaults.remove(defaults.location_defaults_index)

        return {'FINISHED'}

class GT_Add_Export(Operator):
    """Creates a path from the menu"""

    bl_idname = "scene.gx_addexport"
    bl_label = "Add"

    def execute(self, context):
        print(self)

        defaults = GetPluginDefaults()
        newDefault = defaults.export_defaults.add()
        newDefault.name = "Export " + str(len(defaults.export_defaults))
        newDefault.path = ""

        return {'FINISHED'}

class GT_Delete_Export(Operator):
    """Deletes the selected path from the menu"""

    bl_idname = "scene.gx_deleteexport"
    bl_label = "Remove"

    def execute(self, context):
        print(self)

        defaults = GetPluginDefaults()
        defaults.export_defaults.remove(defaults.export_defaults_index)

        return {'FINISHED'}

class GT_Add_Pass(Operator):
    """Creates a path from the menu"""

    bl_idname = "scene.gx_addpass"
    bl_label = "Add"

    def execute(self, context):
        print(self)

        defaults = GetPluginDefaults()
        export = defaults.export_defaults[defaults.export_defaults_index]
        newPass = export.passes.add()
        newPass.name = "Pass " + str(len(export.passes))
        newPass.path = ""

        return {'FINISHED'}

class GT_Delete_Pass(Operator):
    """Deletes the selected path from the menu"""

    bl_idname = "scene.gx_deletepass"
    bl_label = "Remove"

    def execute(self, context):
        print(self)

        defaults = GetPluginDefaults()
        export = defaults.export_defaults[defaults.export_defaults_index]
        export.passes.remove(export.passes_index)

        export.passes_index -= 1

        return {'FINISHED'}

class GT_Shift_Path_Up(Operator):
    """Moves the current entry in the list up by one"""

    bl_idname = "scene.gx_shiftup"
    bl_label = "Add"

    def execute(self, context):
        print(self)

        scn = context.scene.GXScn
        obj = context.active_object.GXObj

        scn.path_defaults.move(scn.path_list_index, scn.path_list_index - 1)
        scn.path_list_index -= 1

        return {'FINISHED'}

class GT_Shift_Path_Down(Operator):
    """Moves the current entry in the list down by one"""

    bl_idname = "scene.gx_shiftdown"
    bl_label = "Remove"

    def execute(self, context):
        print(self)

        scn = context.scene.GXScn
        obj = context.active_object.GXObj

        scn.path_defaults.move(scn.path_list_index, scn.path_list_index + 1)
        scn.path_list_index += 1

        return {'FINISHED'}

class GT_Set_Collision_Object(Operator):
    """Lets you click on another object to set it as the collision object."""

    bl_idname = "scene.gx_setcollision"
    bl_label = "Remove"

    def finish(self):
        # This def helps us tidy the shit we started
        # Restore the active area's header to its initial state.
        bpy.context.area.header_text_set()


    def execute(self, context):
        print("invoke!")
        print("Is this new?")

        scn = context.scene.GXScn
        obj = context.active_object.GXObj

        # Deselect all objects, then go into the modal loop
        self.object = context.scene.objects.active

        # Add the modal handler and LETS GO!
        context.window_manager.modal_handler_add(self)

        # Add a timer to enable a search for a selected object
        self._timer = context.window_manager.event_timer_add(0.05, context.window)

        bpy.ops.object.select_all(action='DESELECT')

        # Set the header text with USEFUL INSTRUCTIONS :O
        context.area.header_text_set(
            "Select the object you want to use as a collision object.  " +
            "RMB: Select Collision Object, Esc: Exit"
        )

        return {'RUNNING_MODAL'}

    def modal(self,context,event):
        # If escape is pressed, exit
        if event.type in {'ESC'}:
            self.finish()

            # This return statement has to be within the same definition (cant defer to finish())
            return{'FINISHED'}

        # When an object is selected, set it as a child to the object, and finish.
        elif event.type == 'RIGHTMOUSE':
            print('TIMER')

            # ALSO, check its not a dummy or origin object
            if context.selected_objects != None and len(context.selected_objects) == 1:
                if context.active_object != self.object:
                    self.object.GXObj.collision_object = context.selected_objects[0].name
                    FocusObject(self.object)

                else:
                    self.report({'WARNING'}, 'The collision object selected is the same object, pick a different object.')

                    FocusObject(self.object)
                    self.finish()
                    return{'FINISHED'}

                self.finish()
                return{'FINISHED'}

        return {'PASS_THROUGH'}

    def cancel(self, context):
        context.window_manager.event_timer_remove(self._timer)
        return {'FINISHED'}


class GT_Clear_Collision_Object(Operator):
    """Clears the currently chosen collision object."""

    bl_idname = "scene.gx_clearcollision"
    bl_label = "Remove"

    def execute(self, context):
        print(self)

        scn = context.scene.GXScn
        obj = context.active_object.GXObj

        obj.collision_object = ""

        MoveObject(context.active_object, context, (0.0, 0.0, 0.0))

        return {'FINISHED'}


class GT_Refresh_Groups(Operator):
    """Generates a list of groups to browse"""

    bl_idname = "scene.gx_refgroups"
    bl_label = "Refresh"

    def execute(self, context):
        print(self)

        scn = context.scene.GXScn

        scn.group_list.clear()

        for group in bpy.data.groups:
            groupEntry = scn.group_list.add()
            groupEntry.name = group.name
            groupEntry.prev_name = group.name


        return {'FINISHED'}

class GT_Set_Root_Object(Operator):
    """Lets you click on another object to set it as the root object for the group."""

    bl_idname = "scene.gx_setroot"
    bl_label = "Remove"

    def finish(self):
        # This def helps us tidy the shit we started
        # Restore the active area's header to its initial state.
        bpy.context.area.header_text_set()


    def execute(self, context):
        print("invoke!")
        print("Is this new?")

        scn = context.scene.GXScn
        obj = context.active_object.GXObj

        user_preferences = context.user_preferences
        self.addon_prefs = user_preferences.addons["GEX"].preferences

        self.object = context.scene.objects.active
        context.window_manager.modal_handler_add(self)
        self._timer = context.window_manager.event_timer_add(0.05, context.window)

        bpy.ops.object.select_all(action='DESELECT')

        # Set the header text with USEFUL INSTRUCTIONS :O
        context.area.header_text_set(
            "Select the object you want to use as a root object.  " +
            "RMB: Select Collision Object, Esc: Exit"
        )

        return {'RUNNING_MODAL'}

    def CheckForChild(self, group, target):

        # Figure out if it is a child of any object in the group.
        print("Searching through children...")
        for altObject in group.objects:
            for child in altObject.children:
                print("Checking child ", child.name)
                if child.name == target.name:
                    self.report({'WARNING'}, 'The object selected is a child of another object in the group, and cant be used as a root object.')

                    FocusObject(self.object)
                    self.finish()
                    return{'FINISHED'}

    def modal(self,context,event):
        # If escape is pressed, exit
        if event.type in {'ESC'}:
            self.finish()

            # This return statement has to be within the same definition (cant defer to finish())
            return{'FINISHED'}

        # When an object is selected, set it as a child to the object, and finish.
        elif event.type == 'RIGHTMOUSE':

            # ALSO, check its not a dummy or origin object
            if context.selected_objects != None and len(context.selected_objects) == 1:

                entry = context.scene.GXScn.group_list[context.scene.GXScn.group_list_index]
                for group in bpy.data.groups:
                    if group.name == entry.name:

                        print("Found Group: ", group.name)
                        for object in group.objects:
                            if object.name == context.selected_objects[0].name:
                                if object.name.find(self.addon_prefs.lp_tag) != -1:
                                    print("Object Passed Main Check", object.name)

                                    self.CheckForChild(group, object)

                                    group.GXGrp.root_object = context.selected_objects[0].name
                                    FocusObject(self.object)
                                    self.finish()
                                    return{'FINISHED'}

                                elif group.GXGrp.auto_assign is False:

                                    self.CheckForChild(group, object)

                                    group.GXGrp.root_object = context.selected_objects[0].name
                                    FocusObject(self.object)
                                    self.finish()
                                    return{'FINISHED'}

                                else:
                                    self.report({'WARNING'}, 'The object selected is not a low-poly object, PAY ATTENTION OmO')

                                    FocusObject(self.object)
                                    self.finish()
                                    return{'FINISHED'}



                        self.report({'WARNING'}, 'The object selected is not in the same group, TRY AGAIN O_O')

                        FocusObject(self.object)
                        self.finish()
                        return{'FINISHED'}

        return {'PASS_THROUGH'}

    def cancel(self, context):
        context.window_manager.event_timer_remove(self._timer)
        return {'FINISHED'}


class GT_Clear_Root_Object(Operator):
    """Clears the currently chosen root object."""

    bl_idname = "scene.gx_clearroot"
    bl_label = "Remove"

    def execute(self, context):
        print(self)

        scn = context.scene.GXScn
        obj = context.active_object.GXObj

        entry = context.scene.GXScn.group_list[context.scene.GXScn.group_list_index]
        for group in bpy.data.groups:
            if group.name == entry.name:
                group.GXGrp.root_object = ""
                return{'FINISHED'}

        return {'FINISHED'}


class GT_Reset_Scene(Operator):
    """Resets all object and group variables in the file."""

    bl_idname = "scene.gx_resetscene"
    bl_label = "Reset Scene"

    def execute(self, context):
        print(self)

        exportedObjects = 0

        # Keep a record of the selected and active objects to restore later
        active = None
        selected = []

        for sel in context.selected_objects:
            if sel.name != context.active_object.name:
                selected.append(sel)

        active = context.active_object

        for group in bpy.data.groups:
            group.GXGrp.export_group = False
            group.GXGrp.auto_assign = False
            group.GXGrp.location_default = '0'

        for object in bpy.data.objects:
            obj = object.GXObj
            FocusObject(object)

            obj.enable_export = False
            obj.apply_modifiers = False
            obj.triangulate = False
            obj.use_collision = False
            obj.generate_convex = False
            obj.separate_collision = False
            obj.collision_object = ""
            obj.export_collision = False
            obj.location_default = '0'
            obj.export_anim = False
            obj.export_anim_file = False
            obj.export_anim_actions = False

        # Re-select the objects previously selected
        FocusObject(active)

        for sel in selected:
            SelectObject(sel)

        return {'FINISHED'}

class GT_Reset_Scene(Operator):
    """Resets all location and export defaults in the file"""

    bl_idname = "scene.gx_resetprefs"
    bl_label = "Reset Scene"

    def execute(self, context):
        print(self)

        user_preferences = bpy.context.user_preferences
        addon_prefs = user_preferences.addons["GEX"].preferences

        if addon_prefs == None:
            print("ADDON COULD NOT START, CONTACT DEVELOPER FOR ASSISTANCE")
            return

        # Figure out if an object already exists, if yes, DELETE IT
        for object in bpy.data.objects:
            print(object)
            if object.name == addon_prefs.default_datablock:
                DeleteObject(object)

        # Otherwise create the object using the addon preference data
        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.object.empty_add(type='PLAIN_AXES')

        defaultDatablock = bpy.context.scene.objects.active
        defaultDatablock.name = addon_prefs.default_datablock
        defaultDatablock.hide = True
        defaultDatablock.hide_render = True
        defaultDatablock.hide_select = True


        return {'FINISHED'}

class GT_Export_Assets(Operator):
    """Updates the origin point based on the option selected, for all selected objects"""

    bl_idname = "scene.gx_export"
    bl_label = "Export"

    def ExportFBX(self, filePath, globalScale, axisForward, axisUp, bakeSpaceTransform, applyModifiers, meshSmooth, objectTypes, useAnim, useAnimAction, useAnimOptimise):

        print("animExport=")
        print(useAnim)

        #useAnimAction = False

        print("Exporting")
        bpy.ops.export_scene.fbx(check_existing=False,
        filepath=filePath,
        filter_glob="*.fbx",
        version='BIN7400',
        use_selection=True,
        global_scale=globalScale,
        axis_forward=axisForward,
        axis_up=axisUp,
        bake_space_transform=bakeSpaceTransform,
        object_types=objectTypes,
        use_mesh_modifiers=applyModifiers,
        mesh_smooth_type=meshSmooth,
        use_mesh_edges=False,
        use_tspace=False,
        use_armature_deform_only=True,
        add_leaf_bones=False,
        bake_anim=useAnim,
        bake_anim_use_all_bones=useAnim,
        bake_anim_use_nla_strips=False,
        bake_anim_use_all_actions=useAnimAction,
        use_anim=useAnim,
        use_anim_action_all=useAnimAction,
        use_default_take=False,
        use_anim_optimize=useAnimOptimise,
        anim_optimize_precision=6.0,
        path_mode='AUTO',
        embed_textures=False,
        batch_mode='OFF',
        use_batch_own_dir=False,
        use_metadata=False)

    def AddTriangulate(self, object):

        modType = {'TRIANGULATE'}

        for modifier in object.modifiers:
            print("Looking for modifier...")
            if modifier.type in modType:
                print("Already found triangulation.")
                return True

        FocusObject(object)
        bpy.ops.object.modifier_add(type='TRIANGULATE')

        for modifier in object.modifiers:
            if modifier.type in modType:
                print("Triangulation Found")
                modifier.quad_method = 'FIXED_ALTERNATE'
                modifier.ngon_method = 'CLIP'
                return False

        print("No modifier found, triangulation failed.")

    def RemoveTriangulate(self, object):

        modType = {'TRIANGULATE'}
        FocusObject(object)

        for modifier in object.modifiers:
            if modifier.type in modType:
                bpy.ops.object.modifier_remove(modifier=modifier.name)


    def GetfilePath(self, locationEnum, fileName):
        # Get the file extension.  If the index is incorrect (as in, the user didnt set the fucking path)
        defaults = GetPluginDefaults()
        enumIndex = int(locationEnum)
        filePath = ""

        if enumIndex == 0:
            return {'1'}

        print("Are we still going for some reason?")
        enumIndex -= 1
        defaultFilePath = defaults.location_defaults[enumIndex].path

        if defaultFilePath == "":
            return {'2'}

        if defaultFilePath.find('//') != -1:
            return {'3'}

        filePath = defaultFilePath
        filePath += fileName

        return filePath



    def execute(self, context):
        print("Self = ")
        print(self)

        scn = context.scene.GXScn
        obj = context.active_object.GXObj
        defaults = GetPluginDefaults()
        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons["GEX"].preferences

        exportedObjects = 0
        exportedGroups = 0
        exportedPasses = 0

        # Keep a record of the selected and active objects to restore later
        active = None
        selected = []
        for sel in context.selected_objects:
            if sel.name != context.active_object.name:
                selected.append(sel)
        active = context.active_object


        # Generate export details based on the export type selected
        axisForward = "-Z"
        axisUp = "Y"
        globalScale = 1.0
        bakeSpaceTransform = False


        # //////////// - ENGINE PROPERTIES - ////////////////////////////////////////////////////////
        # Assign custom properties based on the export target
        if int(scn.engine_select) is 1:
            print("UE4 selected")
            axisForward = "-Z"
            axisUp = "Y"

            if scn.scale_100x is True:
                globalScale = 100.0

            else:
                globalScale = 1.0

        elif int(scn.engine_select) is 2:
            print("Unity selected")
            axisForward = "-Z"
            axisUp = "Y"
            globalScale = 1
            bakeSpaceTransform = True



        # OBJECT CYCLE
        ###############################################################
        ###############################################################
        # Cycle through the available objects
        for object in context.scene.objects:
            if object.type == 'MESH':
                print("Object", object.name, "found.")
                print("Enable export for", object.name, "is false.")

                if object.GXObj.enable_export is True:

                    print("-"*59)
                    print("NEW JOB", "-"*50)
                    print("-"*59)

                    #Get the export default for the object
                    expKey = int(object.GXObj.export_default) - 1
                    exportDefault = defaults.export_defaults[expKey]

                    # Figure out whether the object needs automatic assigning
                    auto_assign = False
                    rootType = 0
                    rootObject = object

                    if object.name.find(addon_prefs.lp_tag) != -1:
                        auto_assign = True
                        rootType = 1
                    elif object.name.find(addon_prefs.hp_tag) != -1:
                        auto_assign = True
                        rootType = 2
                    elif object.name.find(addon_prefs.cg_tag) != -1:
                        auto_assign = True
                        rootType = 3
                    elif object.name.find(addon_prefs.cx_tag) != -1:
                        auto_assign = True
                        rootType = 4

                    print("Auto Assign is", auto_assign)


                    for objPass in exportDefault.passes:

                        print("-"*59)
                        print("NEW PASS", "-"*50)
                        print("-"*59)
                        print("Export pass", objPass.name, "being used on object", object.name)



                        rootObjectLocation = Vector((0.0, 0.0, 0.0))
                        rootObjectLocation[0] = object.location[0]
                        rootObjectLocation[1] = object.location[1]
                        rootObjectLocation[2] = object.location[2]

                        lowPoly = None
                        highPoly = None
                        cage = None
                        collision = None
                        animation = None
                        armature = None

                        # Obtain some object-specific preferences
                        applyModifiers = objPass.apply_modifiers
                        useTriangulate = objPass.triangulate
                        exportIndividual = objPass.export_individual
                        hasTriangulation = False
                        meshSmooth = 'FACE'
                        exportTypes = {'MESH', 'ARMATURE'}

                        # Obtain Object Component Information
                        expLP = objPass.export_lp
                        expHP = objPass.export_hp
                        expCG = objPass.export_cg
                        expCX = objPass.export_cx
                        expAR = objPass.export_ar
                        expAM = objPass.export_am
                        expRoot = False

                        export_anim = False
                        export_anim_actions = False
                        export_anim_optimise = False

                        # Also set file path name
                        path = ""
                        filePath = ""
                        objectFilePath = ""
                        suffix = objPass.file_suffix
                        objectName = ""

                        # Lets see if the root object can be exported...
                        if expLP is True and rootType == 1:
                            expRoot = True
                        if expHP is True and rootType == 2:
                            expRoot = True
                        if expCG is True and rootType == 3:
                            expRoot = True
                        if expCX is True and rootType == 4:
                            expRoot = True

                        #/////////////////// - FILE NAME - /////////////////////////////////////////////////
                        print("Obtaining File...")
                        print("File Enumerator = ", rootObject.GXObj.location_default)
                        filePath = ""
                        filePath = self.GetfilePath(rootObject.GXObj.location_default, rootObject.name)


                        if filePath == "":
                            self.report({'WARNING'}, "Welp, something went wrong.  Contact the developer.")
                            return {'CANCELLED'}

                        if filePath == {'1'}:
                            self.report({'WARNING'}, 'One of the objects has no set file path default.  Set it plzplzplz.')
                            return {'CANCELLED'}

                        if filePath == {'2'}:
                            self.report({'WARNING'}, 'One of the objects file path default has no file path.  A file path is required to export.')
                            return {'CANCELLED'}

                        if filePath == {'3'}:
                            self.report({'WARNING'}, 'One of the objects file path default is using a relative file path name, please tick off the Relative Path option when choosing the file path.')
                            return {'CANCELLED'}

                        path = filePath.replace(rootObject.name, "")
                        objectName = rootObject.name.replace(addon_prefs.lp_tag, "")

                        #/////////////////// - FIND OBJECTS - /////////////////////////////////////////////////
                        # First we have to find all objects in the group that are of type MESHHH
                        # If auto-assignment is on, use the names to filter into lists, otherwise forget it.

                        print(">>>> Collecting Objects <<<<")

                        if bpy.data.objects.find(objectName + addon_prefs.lp_tag) != -1 and expLP is True:
                            item = bpy.data.objects[objectName + addon_prefs.lp_tag]

                            if item.type == 'MESH':
                                if item != rootObject or rootType != 1:
                                    lowPoly = item
                                    print("LP Found...", item.name)

                        if bpy.data.objects.find(objectName + addon_prefs.hp_tag) != -1 and expHP is True:
                            item = bpy.data.objects[objectName + addon_prefs.hp_tag]

                            if item.type == 'MESH':
                                if item != rootObject or rootType != 2:
                                    highPoly = item
                                    print("HP Found...", item.name)

                        if bpy.data.objects.find(objectName + addon_prefs.cg_tag) != -1 and expCG is True:
                            item = bpy.data.objects[objectName + addon_prefs.cg_tag]

                            if item.type == 'MESH':
                                if item != rootObject or rootType != 3:
                                    cage = item
                                    print("CG Found...", item.name)

                        if bpy.data.objects.find(objectName + addon_prefs.cx_tag) != -1 and expCX is True:
                            item = bpy.data.objects[objectName + addon_prefs.cx_tag]

                            if item.type == 'MESH':
                                if item != rootObject or rootType != 4:
                                    collision = item
                                    print("CX Found...", item.name)


                        # We have to collect the armature from the modifier stack
                        modType = {'ARMATURE'}
                        FocusObject(object)

                        if expAR is True:
                            for modifier in object.modifiers:
                                if modifier.type in modType:
                                    armature = modifier.object

                        print("Checking found objects...")
                        print("LP...", rootObject)
                        print("HP...", highPoly)


                        # //////////// - COLLISION SETUP - /////////////////////////////////////
                        # ////////////////////////////////////////////////////////////
                        # //////////////////////////////////////////////////////////////////////
                        # This needs re-writing at the moment, collision doesn't require duplication,
                        # just re-naming and intelligent management
                        # Now we know what objects are up for export, we just need to prepare them
                        # If collision is turned on, sort that shit out
                        if expCX is True and int(scn.engine_select) is 1:
                            if collision is not None:
                                tempName = collision.name.replace(addon_prefs.cx_tag, "")
                                collision.name = "UCX_" + tempName + addon_prefs.lp_tag


                        # /////////// - OBJECT MOVEMENT - ///////////////////////////////////////////////////
                        # ///////////////////////////////////////////////////////////////////////////////////
                        print(">>> Collecting Found Objects <<<")
                        exportList = []

                        if auto_assign is True:
                            print("Auto Assign on, searching...")

                            if expHP is True and lowPoly is not None and rootType != 1:
                                print("Appending LP")
                                exportList.append(lowPoly)

                            if expHP is True and highPoly is not None and rootType != 2:
                                print("Appending HP")
                                exportList.append(highPoly)

                            if expCG is True and cage is not None and rootType != 3:
                                print("Appending CG")
                                exportList.append(cage)

                            if expCX is True and collision is not None and rootType != 4:
                                print("Appending CX")
                                exportList.append(collision)

                            if expAR is True and armature is not None:
                                print("Appending AR")
                                exportList.append(armature)

                            MoveObjects(rootObject, exportList, context, (0.0, 0.0, 0.0))

                        else:
                            MoveObject(rootObject, context, (0.0, 0.0, 0.0))

                        print(">>> Asset List Count...", len(exportList))


                        # /////////// - MODIFIERS - ///////////////////////////////////////////////////
                        # ////////////////////////////////////////////////////////////////////////////
                        triangulateList = []
                        triangulateList += exportList

                        if expLP is True:
                            triangulateList.append(rootObject)

                        if useTriangulate is True and applyModifiers is True:
                            for object in triangulateList:
                                if object.type == 'MESH':
                                    stm = object.GXStm
                                    hasTriangulation = False
                                    hasTriangulation = self.AddTriangulate(object)
                                    stm.has_triangulate = hasTriangulation


                        # //////////// - EXPORT PROCESS - ///////////////////////////////////////////
                        # A separate FBX export function call for every corner case isnt actually necessary
                        if exportIndividual is True:
                            print(">>> Exporting Individual Pass <<<")
                            for item in exportList:

                                # Get some information first
                                bpy.ops.object.select_all(action='DESELECT')
                                SelectObject(item)
                                individualFilePath = path + item.name + suffix + ".fbx"

                                # For the time being, manually move the object back and forth to
                                # the world origin point.
                                backupLoc = Vector((0.0, 0.0, 0.0))
                                backupLoc[0] = item.location[0]
                                backupLoc[1] = item.location[1]
                                backupLoc[2] = item.location[2]
                                MoveObject(item, context, (0.0, 0.0, 0.0))

                                self.ExportFBX(individualFilePath, globalScale, axisForward, axisUp, bakeSpaceTransform, applyModifiers, meshSmooth, exportTypes, True, True, True)

                                MoveObject(item, context, backupLoc)

                            if expRoot is True:
                                bpy.ops.object.select_all(action='DESELECT')
                                FocusObject(rootObject)
                                individualFilePath = path + rootObject.name + suffix + ".fbx"

                                self.ExportFBX(individualFilePath, globalScale, axisForward, axisUp, bakeSpaceTransform, applyModifiers, meshSmooth, exportTypes, True, True, True)

                            if expAM is True:
                                print("Exporting separate animation files...")


                        else:
                            print(">>> Exporting Combined Pass <<<")
                            print("Checking export preferences...")

                            for item in exportList:
                                print(item.name, "has export set to", item.GXObj.enable_export)
                                SelectObject(sel)

                            if expRoot is True:
                                SelectObject(rootObject)

                            objectFilePath = path + objectName + suffix + ".fbx"

                            if expAM is True:
                                print("Exporting animations...")
                                export_anim = True
                                export_anim_actions = True
                                export_anim_optimise = True

                                if expLP is False and expHP is False and expCG is False and expCX is False:
                                    if expAR is True:
                                        exportTypes = {'ARMATURE'}

                            self.ExportFBX(objectFilePath, globalScale, axisForward, axisUp, bakeSpaceTransform, applyModifiers, meshSmooth, exportTypes, export_anim, export_anim_actions, export_anim_optimise)


                        # /////////// - DELETE/RESTORE - ///////////////////////////////////////////////////
                        # ///////////////////////////////////////////////////////////////////////////////////
                        if expCX is True and scn.engine_select is '1':
                            if collision is not None:
                                tempName = collision.name.replace("UCX_", "")
                                tempName2 = tempName.replace(addon_prefs.lp_tag, "")
                                print(tempName2)
                                collision.name = tempName2 + addon_prefs.cx_tag

                        # Remove any triangulation modifiers
                        if useTriangulate is True and applyModifiers is True:
                            for item in triangulateList:
                                if item.type == 'MESH':
                                    if item.GXStm.has_triangulate is False:
                                        print("Object has created triangulation, remove it.")
                                        self.RemoveTriangulate(item)

                        for item in exportList:
                            print("Checking ", item.name)
                            print("Checking object position... ", item.location)

                        if auto_assign is True:
                            MoveObjects(rootObject, exportList, context, rootObjectLocation)

                        else:
                            MoveObject(rootObject, context, rootObjectLocation)

                        exportedPasses += 1

                        print(">>> Pass Complete <<<")

                    print(">>> Object Export Complete <<<")

                    # Count up exported objects
                    exportedObjects += 1



        # Now hold up, its group time!
        for group in bpy.data.groups:
            if group.GXGrp.export_group is True:

                # Before we do anything, check that a root object exists
                hasRootObject = True
                rootObject = None
                rootObjectLocation = Vector((0.0, 0.0, 0.0))

                if group.GXGrp.root_object == "":
                    hasRootObject = False

                for object in group.objects:
                    if object.name == group.GXGrp.root_object:
                        hasRootObject = True
                        rootObject = object
                        rootObjectLocation[0] = object.location[0]
                        rootObjectLocation[1] = object.location[1]
                        rootObjectLocation[2] = object.location[2]

                print("Checking root position... ", rootObjectLocation)

                if rootObject == None:
                    hasRootObject = False

                if hasRootObject is False:
                    statement = "The group object " + group.name + " has no valid root object.  Ensure the root object exists in the group."
                    self.report({'WARNING'}, statement)
                    return {'FINISHED'}

                if rootObject.name.find(addon_prefs.lp_tag) == -1 and group.GXGrp.auto_assign is True:
                    statement = "The group object " + group.name + " has no low-poly root object.  Ensure it has the right suffix or change the object used."
                    self.report({'WARNING'}, statement)
                    return {'FINISHED'}


                #Get the export default for the object
                expKey = int(group.GXGrp.export_default) - 1
                exportDefault = defaults.export_defaults[expKey]

                for objPass in exportDefault.passes:

                    print("Group Exporting... ", group.name)
                    print("Export Default used...", exportDefault.name)
                    print("Pass processing...", objPass.name)

                    completeList = []
                    lowPolyList = []
                    highPolyList = []
                    cageList = []
                    collisionList = []
                    animationList = []
                    armatureList = []

                    # Obtain some object-specific preferences
                    applyModifiers = objPass.apply_modifiers
                    useTriangulate = objPass.triangulate
                    exportIndividual = objPass.export_individual
                    hasTriangulation = False
                    meshSmooth = 'FACE'
                    exportTypes = {'MESH', 'ARMATURE'}

                    # Obtain Object Component Information
                    expLP = objPass.export_lp
                    expHP = objPass.export_hp
                    expCG = objPass.export_cg
                    expCX = objPass.export_cx
                    expAR = objPass.export_ar
                    expAM = objPass.export_am

                    export_anim = False
                    export_anim_actions = False
                    export_anim_optimise = False

                    # Also set file path name
                    path = ""
                    filePath = ""
                    objectFilePath = ""
                    suffix = objPass.file_suffix

                    auto_assign = group.GXGrp.auto_assign

                    #/////////////////// - FILE NAME - /////////////////////////////////////////////////
                    print("Obtaining File...")
                    print("File Enumerator = ", group.GXGrp.location_default)
                    filePath = ""
                    filePath = self.GetfilePath(group.GXGrp.location_default, group.name)


                    if filePath == "":
                        self.report({'WARNING'}, "Welp, something went wrong.  Contact the developer.")
                        return {'CANCELLED'}

                    if filePath == {'1'}:
                        self.report({'WARNING'}, 'One of the groups has no set file path default.  Set it plzplzplz.')
                        return {'CANCELLED'}

                    if filePath == {'2'}:
                        self.report({'WARNING'}, 'One of the groups file path default has no file path.  A file path is required to export.')
                        return {'CANCELLED'}

                    if filePath == {'3'}:
                        self.report({'WARNING'}, 'One of the groups file path default is using a relative file path name, please tick off the Relative Path option when choosing the file path.')
                        return {'CANCELLED'}

                    path = filePath.replace(group.name, "")

                    #/////////////////// - FIND OBJECTS - /////////////////////////////////////////////////
                    # First we have to find all objects in the group that are of type MESHHH
                    # If auto-assignment is on, use the names to filter into lists, otherwise forget it.

                    print(">>>> Collecting Objects <<<<")

                    if auto_assign is False:
                        print("Auto Assign off, collecting all group objects....")
                        for object in group.objects:
                            if object.name != rootObject.name:
                                if object.type == 'MESH' or object.type == 'ARMATURE':
                                    print("Collected", object.name, "...")
                                    completeList.append(object)

                        print("Collected", len(completeList), "objects.")

                    else:
                        print("Auto Assign on, collecting group objects....")
                        for object in group.objects:
                            print("Group Object...", object.name)
                            if object != rootObject:
                                if object.type == 'MESH':

                                    # Sorts based on name suffix
                                    if object.name.find(addon_prefs.lp_tag) != -1 and expLP is True:
                                        if object.name != rootObject.name:
                                            lowPolyList.append(object)

                                    elif object.name.find(addon_prefs.hp_tag) != -1 and expHP is True:
                                        highPolyList.append(object)

                                    elif object.name.find(addon_prefs.cg_tag) != -1 and expCG is True:
                                        cageList.append(object)

                                    # Collision objects are only added if it can find a name match with a static mesh
                                    elif object.name.find(addon_prefs.cx_tag) != -1 and expCX is True:
                                        collisionName = object.name
                                        collisionName = collisionName.replace(addon_prefs.cx_tag, "")

                                        for staticObject in group.objects:

                                            if staticObject != object:
                                                if staticObject.name.find(collisionName + addon_prefs.lp_tag) != -1 and staticObject.type == 'MESH':

                                                    print("Collision Confirmed")
                                                    collisionList.append(object)

                                elif object.type == 'ARMATURE' and expAR is True:
                                    print("Collected armature,", object.name, "...")
                                    armatureList.append(object)

                    print("Total armatures....", len(armatureList))


                    # Need to obtain animations (if applicable)



                    # Now we know what objects are up for export, we just need to prepare them
                    # If collision is turned on, sort that shit out
                    if expCX is True and int(scn.engine_select) is 1:
                        for object in collisionList:
                            tempName = object.name.replace(addon_prefs.cx_tag, "")
                            object.name = "UCX_" + tempName + addon_prefs.lp_tag


                    # /////////// - OBJECT MOVEMENT - ///////////////////////////////////////////////////
                    # ///////////////////////////////////////////////////////////////////////////////////
                    exportList = []
                    if auto_assign is True:
                        if expLP is True:
                            exportList += lowPolyList

                        if expHP is True:
                            exportList += highPolyList

                        if expCG is True:
                            exportList += cageList

                        if expCX is True:
                            exportList += collisionList

                        if expAR is True:
                            exportList += armatureList

                    else:
                        exportList += completeList

                    MoveObjects(rootObject, exportList, context, (0.0, 0.0, 0.0))



                    # /////////// - MODIFIERS - ///////////////////////////////////////////////////
                    # ////////////////////////////////////////////////////////////////////////////
                    triangulateList = []
                    triangulateList += exportList

                    if expLP is True:
                        triangulateList.append(rootObject)

                    if useTriangulate is True and applyModifiers is True:
                        for object in triangulateList:
                            if object.type == 'MESH':
                                stm = object.GXStm
                                hasTriangulation = False
                                hasTriangulation = self.AddTriangulate(object)
                                stm.has_triangulate = hasTriangulation


                    # /////////// - EXPORT - ///////////////////////////////////////////////////
                    # ///////////////////////////////////////////////////////////////////////////////////
                    print(">>>> Exporting Objects <<<<")
                    bpy.ops.object.select_all(action='DESELECT')



                    if exportIndividual is True:
                        print("Individual Pass, exporting....")
                        for object in exportList:

                            # Get some information first
                            bpy.ops.object.select_all(action='DESELECT')
                            SelectObject(object)
                            individualFilePath = path + object.name + suffix + ".fbx"

                            # For the time being, manually move the object back and forth to
                            # the world origin point.
                            backupLoc = Vector((0.0, 0.0, 0.0))
                            backupLoc[0] = object.location[0]
                            backupLoc[1] = object.location[1]
                            backupLoc[2] = object.location[2]
                            MoveObject(object, context, (0.0, 0.0, 0.0))

                            self.ExportFBX(individualFilePath, globalScale, axisForward, axisUp, bakeSpaceTransform, applyModifiers, meshSmooth, exportTypes, True, True, True)

                            MoveObject(object, context, backupLoc)

                        if expLP is True:
                            bpy.ops.object.select_all(action='DESELECT')
                            FocusObject(rootObject)
                            individualFilePath = path + rootObject.name + suffix + ".fbx"

                            self.ExportFBX(individualFilePath, globalScale, axisForward, axisUp, bakeSpaceTransform, applyModifiers, meshSmooth, exportTypes, True, True, True)

                        if expAM is True:
                            print("Exporting separate animation files...")


                    else:
                        print("Combined Pass, exporting....")
                        for object in exportList:
                            SelectObject(object)

                        if expLP is True:
                            SelectObject(rootObject)

                        objectFilePath = filePath + suffix + ".fbx"

                        if expAM is True:
                            print("Exporting animations...")
                            export_anim = True
                            export_anim_actions = True
                            export_anim_optimise = True

                            if expLP is False and expHP is False and expCG is False and expCX is False:
                                if expAR is True:
                                    exportTypes = {'ARMATURE'}

                        self.ExportFBX(objectFilePath, globalScale, axisForward, axisUp, bakeSpaceTransform, applyModifiers, meshSmooth, exportTypes, export_anim, export_anim_actions, export_anim_optimise)


                    # /////////// - DELETE/RESTORE - ///////////////////////////////////////////////////
                    # ///////////////////////////////////////////////////////////////////////////////////
                    if expCX is True and scn.engine_select is '1':
                        for object in collisionList:
                            tempName = object.name.replace("UCX_", "")
                            tempName2 = tempName.replace(addon_prefs.lp_tag, "")
                            print(tempName2)
                            object.name = tempName2 + addon_prefs.cx_tag

                    # Remove any triangulation modifiers
                    if useTriangulate is True and applyModifiers is True:
                        for object in triangulateList:
                            if object.type == 'MESH':
                                if object.GXStm.has_triangulate is False:
                                    print("Object has created triangulation, remove it.")
                                    self.RemoveTriangulate(object)

                    for object in exportList:
                        print("Checking ", object.name)
                        print("Checking object position... ", object.location)

                    MoveObjects(rootObject, exportList, context, rootObjectLocation)

                    exportedPasses += 1

                    print(""*100)

                exportedGroups += 1



        # Re-select the objects previously selected
        FocusObject(active)

        for sel in selected:
            SelectObject(sel)

        textGroupSingle = " group"
        textGroupMultiple = " groups"
        dot = "."

        output = "Finished exporting "

        if exportedObjects > 1:
            output += str(exportedObjects) + " objects"
        elif exportedObjects == 1:
            output += str(exportedObjects) + " object"

        if exportedObjects > 0 and exportedGroups > 0:
            output += " and "

        if exportedGroups > 1:
            output += str(exportedGroups) + " groups"
        elif exportedGroups == 1:
            output += str(exportedGroups) + " group"

        output += ".  "

        output += "Total of "

        if exportedPasses > 1:
            output += str(exportedPasses) + " passes."
        elif exportedPasses == 1:
            output += str(exportedPasses) + " pass."

        # Output a nice report
        if exportedObjects == 0 and exportedGroups == 0:
            self.report({'WARNING'}, 'No objects were exported.  Ensure any objects tagged for exporting are enabled.')

        else:
            self.report({'INFO'}, output)


        return {'FINISHED'}


class GT_UI_Group_Separate(Operator):
    """Toggles the drop-down menu for separate group export options"""

    bl_idname = "scene.gx_grpseparate"
    bl_label = ""

    def execute(self, context):
        print(self)

        scn = context.scene.GXScn
        ui = context.scene.GXUI

        if ui.group_separate_dropdown is True:
            ui.group_separate_dropdown = False
        else:
            ui.group_separate_dropdown = True

        return {'FINISHED'}

class GT_UI_Group_Options(Operator):
    """Toggles the drop-down menu for separate group export options"""

    bl_idname = "scene.gx_grpoptions"
    bl_label = ""

    def execute(self, context):
        print(self)

        scn = context.scene.GXScn
        ui = context.scene.GXUI

        if ui.group_options_dropdown is True:
            ui.group_options_dropdown = False
        else:
            ui.group_options_dropdown = True

        return {'FINISHED'}
