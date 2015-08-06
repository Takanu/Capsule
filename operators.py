import bpy, bmesh
from bpy.types import Operator
from .definitions import SelectObject, FocusObject, ActivateObject, DuplicateObject, DuplicateObjects, DeleteObject, MoveObject, MoveObjects
from mathutils import Vector

class GT_Add_Path(Operator):
    """Creates a path from the menu"""

    bl_idname = "scene.gx_addpath"
    bl_label = "Add"

    def execute(self, context):
        print(self)

        scn = context.scene.GXScn
        obj = context.active_object.GXObj

        newPath = scn.path_defaults.add()
        newPath.name = "New Path"
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

        scn = context.scene.GXScn
        obj = context.active_object.GXObj

        print(scn.path_list_index)

        scn.path_defaults.remove(scn.path_list_index)

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


    def GetfilePath(self, scn, locationEnum, fileName):
        # Get the file extension.  If the index is incorrect (as in, the user didnt set the fucking path)
        enumIndex = int(locationEnum)
        filePath = ""

        if enumIndex == 0:
            return {'1'}

        print("Are we still going for some reason?")
        enumIndex -= 1
        defaultFilePath = scn.path_defaults[enumIndex].path

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

        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons["GEX"].preferences

        exportedObjects = 0
        exportedGroups = 0

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

        # Generate some other system details in Blender to ensure the movement process doesn't interfere

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
                if object.GXObj.enable_export is True:

                    FocusObject(object)

                    # Obtain some object-specific preferences
                    applyModifiers = object.GXObj.apply_modifiers
                    useTriangulate = object.GXObj.triangulate
                    hasTriangulate = False
                    meshSmooth = 'EDGE'
                    isArmature = False
                    armature = None

                    objectTypes = {'MESH'}

                    # Also set file path names
                    collision = None
                    exportCollision = False
                    collisionNameBackup = ""
                    collisionFilePath = ""
                    animationFilePath = ""

                    if object.GXObj.export_collision is True:
                        exportCollision = True

                    elif int(scn.engine_select) is 2 and object.GXObj.use_collision is True:
                        exportCollision = True


                    useAnim = False
                    useAnimAction = False
                    useAnimOptimise = False

                    exportAnim = object.GXObj.export_anim
                    exportAnimSeparate = False

                    # See if the object is an armature
                    # Should I allow multiple armatures for one object?  Do i make a menu element
                    # to select between potential target armatures?  I just don't know...
                    for modifier in object.modifiers:
                        if modifier.type == 'ARMATURE' and exportAnim is True:
                            isArmature = True
                            objectTypes = {'MESH', 'ARMATURE'}

                            if exportAnimSeparate is True:
                                useAnim = False
                                useAnimAction = False
                                useAnimOptimise = False

                            else:
                                useAnim = object.GXObj.export_anim
                                useAnimAction = object.GXObj.export_anim
                                useAnimOptimise = object.GXObj.export_anim

                            armature = modifier.object

                            exportAnimSeparate = object.GXObj.export_anim_file





                    # //////////// - FILE PATH - //////////////////////////////////////////////
                    # /////////////////////////////////////////////////////////////////////
                    # //////////////////////////////////////////////////////////////////////
                    # Same as the group export, keep :D

                    filePath = ""
                    filePath = self.GetfilePath(scn, object.GXObj.location_default, object.name)


                    if filePath == "":
                        self.report({'WARNING'}, "Welp, something went wrong.  Contact the developer.")
                        return {'CANCELLED'}

                    if filePath == {'1'}:
                        FocusObject(object)
                        self.report({'WARNING'}, 'The selected object has no set file path default.  Set it plzplzplz.')
                        return {'CANCELLED'}

                    if filePath == {'2'}:
                        FocusObject(object)
                        self.report({'WARNING'}, 'The selected object file path default has no file path.  A file path is required to export.')
                        return {'CANCELLED'}

                    if filePath == {'3'}:
                        FocusObject(object)
                        self.report({'WARNING'}, 'The selected object file path default is using a relative file path name, please tick off the Relative Path option when choosing the file path.')
                        return {'CANCELLED'}

                    print(filePath)

                    objectFilePath = filePath + ".fbx"

                    # Store the objects initial position for object movement

                    originalLoc = Vector((0.0, 0.0, 0.0))
                    originalLoc[0] = object.location[0]
                    originalLoc[1] = object.location[1]
                    originalLoc[2] = object.location[2]

                    print("Object Location:")
                    print(originalLoc)


                    # //////////// - COLLISION SETUP - /////////////////////////////////////
                    # ////////////////////////////////////////////////////////////
                    # //////////////////////////////////////////////////////////////////////
                    # This needs re-writing at the moment, collision doesn't require duplication,
                    # just re-naming and intelligent management


                    # If collision is turned on, sort that shit out
                    if object.GXObj.use_collision is True and isArmature is False:

                        # Generate collision on request
                        if object.GXObj.generate_convex is True:
                            bpy.ops.object.editmode_toggle()
                            bpy.ops.mesh.select_all(action='SELECT')

                            # From: http://www.blender.org/api/blender_python_api_2_62_1/bmesh.html#bmesh.from_edit_mesh
                            # This currently doesn't work, D:

                            # Get a BMesh representation
                            collisionMesh = bpy.data.objects[collision.name].data
                            bm = bmesh.new()   # create an empty BMesh
                            bm.from_mesh(collisionMesh)   # fill it in from a Mesh

                            verts = [v for v in bm.verts if (v.select==True and not v.hide)]
                            edges = [e for e in bm.edges if (e.select==True and not e.hide)]
                            faces = [f for f in bm.faces if (f.select==True and not f.hide)]

                            # Modify the BMesh, can do anything here...
                            output = bmesh.ops.convex_hull(bm, input=(verts, edges, faces), use_existing_faces=True)

                            # Finish up, write the bmesh back to the mesh
                            bm.to_mesh(me)
                            bm.free()

                            bpy.ops.mesh.select_all(action='DESELECT')
                            bpy.ops.object.editmode_toggle()

                            print("Lovemesenpai.")

                        elif object.GXObj.separate_collision is True:
                            # Try to select the collision object
                            bpy.ops.object.select_all(action='DESELECT')
                            bpy.ops.object.select_pattern(pattern=object.GXObj.collision_object)

                            # A nice little error report if they have a bogus object name
                            if len(context.selected_objects) == 0:
                                self.report({'WARNING'}, 'The selected object has no defined collision object.')

                                FocusObject(object)

                                return {'FINISHED'}

                            collision = context.selected_objects[0]
                            FocusObject(collision)

                        # If need be, setup the collision file path
                        if exportCollision is True:
                            collisionFilePath = filePath + "_CX" + ".fbx"

                        # If were using UE4 export, name the
                        elif int(scn.engine_select) is 1:
                            collisionNameBackup = collision.name
                            collision.name = "UCX_" + object.name



                    # //////////// - ANIMATION SETUP - ////////////////////////////////////////
                    # /////////////////////////////////////////////////////////////////////////
                    if isArmature is True:
                        print("Animation is true?")

                        if exportAnimSeparate is True:
                            animFileName = filePath + "_AM" + ".fbx"

                    # //////////// - MODIFIER SETUP - ////////////////////////////////////////
                    # ////////////////////////////////////////////////////////////////////////
                    if useTriangulate is True and applyModifiers is True:
                        hasTriangulate = self.AddTriangulate(object)


                    # /////////// - OBJECT MOVEMENT - ////////////////////////////////////////
                    # ////////////////////////////////////////////////////////////////////////
                    # All exportable objects should be moved together, no duplication of any kind
                    targets = []

                    if collision is not None:
                        targets.append(collision)

                    if armature is not None:
                        targets.append(armature)

                    if len(targets) > 0:
                        MoveObjects(object, targets, context, (0.0, 0.0, 0.0))

                    else:
                        MoveObject(object, context, (0.0, 0.0, 0.0))




                    # //////////// - EXPORT PROCESS - ///////////////////////////////////////////
                    # A separate FBX export function call for every corner case isnt actually necessary
                    FocusObject(object)

                    if collision is not None and exportCollision is False:
                        SelectObject(collision)

                    if armature is not None:
                        SelectObject(armature)

                    self.ExportFBX(objectFilePath, globalScale, axisForward, axisUp, bakeSpaceTransform, applyModifiers, meshSmooth, {'MESH', 'ARMATURE'}, useAnim, useAnimAction, useAnimOptimise)

                    if exportCollision is True:
                        FocusObject(collision)

                        self.ExportFBX(collisionFilePath, globalScale, axisForward, axisUp, bakeSpaceTransform, applyModifiers, meshSmooth, {'MESH', 'ARMATURE'}, False, False, False)



                    # ////////////////// - WRAP UP - //////////////////////////////////////
                    # Rename objects
                    if collision is not None and exportCollision is False:
                        collision.name = collisionNameBackup

                    # Otherwise move everything back to their initial positions
                    if len(targets) > 0:
                        print(">>> Moving Objects")
                        MoveObjects(object, targets, context, originalLoc)

                    else:
                        MoveObject(object, context, originalLoc)

                    # Remove any triangulation modifiers
                    if useTriangulate is True and applyModifiers is True and hasTriangulate is False:
                        self.RemoveTriangulate(object)

                    # Count up exported objects
                    exportedObjects += 1



        # Now hold up, its group time!
        for group in bpy.data.groups:
            if group.GXGrp.export_group is True:

                grp = group.GXGrp

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

                if rootObject == None:
                    hasRootObject = False

                if hasRootObject is False:
                    statement = "The group object " + group.name + " has no valid root object.  Ensure the root object exists in the group."
                    self.report({'WARNING'}, statement)
                    return {'FINISHED'}

                if rootObject.name.find(addon_prefs.lp_tag) == -1 and grp.auto_assign is True:
                    statement = "The group object " + group.name + " has no low-poly root object.  Ensure it has the right suffix or change the object used."
                    self.report({'WARNING'}, statement)
                    return {'FINISHED'}

                staticList = []
                highPolyList = []
                cageList = []
                collisionList = []
                armatureList = []

                # Obtain some object-specific preferences
                applyModifiers = grp.apply_modifiers
                useTriangulate = True
                meshSmooth = 'OFF'
                objectTypes = {'MESH', 'ARMATURE'}
                useAnim = False
                useAnimAction = False
                useAnimOptimise = False

                exportAnimSeparate = False

                #/////////////////// - FILE NAME - /////////////////////////////////////////////////
                filePath = ""
                filePath = self.GetfilePath(scn, group.GXGrp.location_default, group.name)

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

                #/////////////////// - FIND OBJECTS - /////////////////////////////////////////////////
                # First we have to find all objects in the group that are of type MESHHH
                # If auto-assignment is on, use the names to filter into lists, otherwise forget it.
                if group.GXGrp.auto_assign is False:
                    for object in group.objects:
                        if object != rootObject:
                            if object.type == 'MESH':
                                staticList.append(object)
                            elif object.type == 'ARMATURE':
                                armatureList.append(object)

                else:
                    for object in group.objects:
                        if object != rootObject:
                            #print("Object not root, looking...")
                            #print(object.name)
                            #print(str(object.name.find("_LP")))
                            #print(str(object.name.find("_CX")))

                            # Sorts based on name suffix
                            if object.name.find(addon_prefs.lp_tag) != -1 and object.type == 'MESH':
                                staticList.append(object)

                            # Sorts based on name suffix
                            elif object.name.find(addon_prefs.hp_tag) != -1 and object.type == 'MESH':
                                highPolyList.append(object)

                            # Sorts based on name suffix
                            elif object.name.find(addon_prefs.cg_tag) != -1 and object.type == 'MESH':
                                cageList.append(object)

                            # Collision objects are only added if it can find a name match with a static mesh
                            elif object.name.find(addon_prefs.cx_tag) != -1 and object.type == 'MESH':
                                collisionName = object.name
                                collisionName = collisionName.replace(addon_prefs.cx_tag, "")

                                print("Collision Object Found")
                                print(object.name)
                                print(collisionName)

                                for staticObject in group.objects:

                                    if staticObject != object:
                                        if staticObject.name.find(collisionName + addon_prefs.lp_tag) != -1 and staticObject.type == 'MESH':

                                            print("Collision Confirmed")
                                            collisionList.append(object)

                            elif object.type == 'ARMATURE':
                                armatureList.append(object)

                print("Object search report")
                print("Statics Found:")
                print(len(staticList))
                print("Collisions Found:")
                print(len(collisionList))
                print("Armatures Found:")
                print(len(armatureList))

                # Now we know what objects are up for export, we just need to prepare them
                # If collision is turned on, sort that shit out
                if len(collisionList) > 0:
                    for object in collisionList:

                        # Give the collision object the right name, we will change it back   afterwards
                        if int(scn.engine_select) is 1:
                            tempName = object.name.replace(addon_prefs.cx_tag, "")
                            object.name = "UCX_" + tempName + addon_prefs.lp_tag


                # /////////// - OBJECT MOVEMENT - ///////////////////////////////////////////////////
                # ///////////////////////////////////////////////////////////////////////////////////
                exportMoveList = staticList + armatureList

                if grp.export_hp is True:
                    exportMoveList += highPolyList

                if grp.export_cg is True:
                    exportMoveList += cageList

                if grp.export_cx is True or scn.engine_select is '1':
                    exportMoveList += collisionList

                MoveObjects(rootObject, exportMoveList, context, (0.0, 0.0, 0.0))

                # /////////// - MODIFIERS - ///////////////////////////////////////////////////
                # ///////////////////////////////////////////////////////////////////////////////////
                triangulateList = staticList + highPolyList + cageList + collisionList
                triangulateList.append(rootObject)

                if useTriangulate is True and applyModifiers is True:
                    for object in triangulateList:
                        stm = object.GXStm
                        hasTriangulate = False
                        hasTriangulate = self.AddTriangulate(object)
                        stm.has_triangulate = hasTriangulate

                # /////////// - EXPORT - ///////////////////////////////////////////////////
                # ///////////////////////////////////////////////////////////////////////////////////

                FocusObject(rootObject)

                for object in staticList:
                    SelectObject(object)

                if scn.engine_select is '1':
                    for object in collisionList:
                        SelectObject(object)

                for object in armatureList:
                    SelectObject(object)

                objectFilePath = filePath + ".fbx"

                self.ExportFBX(objectFilePath, globalScale, axisForward, axisUp, bakeSpaceTransform, applyModifiers, meshSmooth, {'MESH', 'ARMATURE'}, True, True, True)



                if grp.export_lp is True and len(staticList) != 0:
                    bpy.ops.object.select_all(action='DESELECT')
                    for object in staticList:
                        SelectObject(object)

                    SelectObject(rootObject)

                    lpFilePath = filePath + addon_prefs.lp_tag + ".fbx"

                    self.ExportFBX(lpFilePath, globalScale, axisForward, axisUp, bakeSpaceTransform, applyModifiers, meshSmooth, {'MESH'}, False, False, False)


                if grp.export_hp is True and len(highPolyList) != 0:
                    bpy.ops.object.select_all(action='DESELECT')
                    for object in highPolyList:
                        SelectObject(object)

                    hpFilePath = filePath + addon_prefs.hp_tag + ".fbx"

                    self.ExportFBX(hpFilePath, globalScale, axisForward, axisUp, bakeSpaceTransform, applyModifiers, meshSmooth, {'MESH'}, False, False, False)


                if grp.export_cg is True and len(cageList) != 0:
                    bpy.ops.object.select_all(action='DESELECT')
                    for object in cageList:
                        SelectObject(object)

                    cgFilePath = filePath + addon_prefs.cg_tag + ".fbx"

                    self.ExportFBX(cgFilePath, globalScale, axisForward, axisUp, bakeSpaceTransform, applyModifiers, meshSmooth, {'MESH'}, False, False, False)


                if grp.export_cx is True and len(collisionList) != 0:
                    bpy.ops.object.select_all(action='DESELECT')
                    for object in collisionList:
                        SelectObject(object)

                    cxFilePath = filePath + addon_prefs.cx_tag + ".fbx"

                    self.ExportFBX(cxFilePath, globalScale, axisForward, axisUp, bakeSpaceTransform, applyModifiers, meshSmooth, {'MESH'}, False, False, False)



                # /////////// - DELETE/RESTORE - ///////////////////////////////////////////////////
                # ///////////////////////////////////////////////////////////////////////////////////
                if scn.engine_select is '1':
                    for object in collisionList:
                        tempName = object.name.replace("UCX_", "")
                        tempName2 = tempName.replace(addon_prefs.lp_tag, "")
                        print(tempName2)
                        object.name = tempName2 + addon_prefs.cx_tag

                # Remove any triangulation modifiers
                if useTriangulate is True and applyModifiers is True:
                    for object in triangulateList:
                        if object.GXStm.has_triangulate is False:
                            print("Object has created triangulation, remove it.")
                            self.RemoveTriangulate(object)

                MoveObjects(rootObject, exportMoveList, context, rootObjectLocation)

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

        output += "."

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
