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
                self.object.GXObj.collision_object = context.selected_objects[0].name
                FocusObject(self.object)

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
        obj = context.active_object.GXObj

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

        # Deselect all objects, then go into the modal loop
        self.object = context.scene.objects.active

        # Add the modal handler and LETS GO!
        context.window_manager.modal_handler_add(self)

        # Add a timer to enable a search for a selected object
        self._timer = context.window_manager.event_timer_add(0.05, context.window)

        bpy.ops.object.select_all(action='DESELECT')

        # Set the header text with USEFUL INSTRUCTIONS :O
        context.area.header_text_set(
            "Select the object you want to use as a root object.  " +
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

                entry = context.scene.GXScn.group_list[context.scene.GXScn.group_list_index]
                for group in bpy.data.groups:
                    if group.name == entry.name:

                        for object in group.objects:
                            if object.name == context.selected_objects[0].name:
                                if object.name.find("_LP") != -1:
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
            if modifier.type in modType:
                return True

        bpy.ops.object.modifier_add(type='TRIANGULATE')

        for modifier in object.modifiers:
            if modifier.type in modType:
                print("Triangulation Found")
                modifier.quad_method = 'FIXED_ALTERNATE'
                modifier.ngon_method = 'CLIP'
                return False

    def RemoveTriangulate(self, object):

        modType = {'TRIANGULATE'}

        for modifier in object.modifiers:
            if modifier.type in modType:
                bpy.ops.object.modifier_remove(modifier=modifier.name)


    def GetObjectFilePath(self, scn, locationEnum, fileName):
        # Get the file extension.  If the index is incorrect (as in, the user didnt set the fucking path)
        enumIndex = int(locationEnum)
        objectFilePath = ""

        if enumIndex == 0:
            return {'1'}

        print("Are we still going for some reason?")
        enumIndex -= 1
        defaultFilePath = scn.path_defaults[enumIndex].path

        if defaultFilePath == "":
            return {'2'}

        if defaultFilePath.find('//') != -1:
            return {'3'}

        objectFilePath = defaultFilePath
        objectFilePath += fileName
        objectFilePath += ".fbx"

        return objectFilePath



    def execute(self, context):
        print("Self = ")
        print(self)

        scn = context.scene.GXScn
        obj = context.active_object.GXObj

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
                    useAnim = False
                    useAnimAction = False
                    useAnimOptimise = False

                    exportAnimSeparate = False

                    # See if the object is an armature
                    for modifier in object.modifiers:
                        if modifier.type == 'ARMATURE':
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


                    # //////////// - FILE PATH - ////////////////////////////////////////////////////////
                    # ///////////////////////////////////////////////////////////////////////////////////
                    # ///////////////////////////////////////////////////////////////////////////////////
                    objectFilePath = ""
                    objectFilePath = self.GetObjectFilePath(scn, object.GXObj.location_default, object.name)

                    if objectFilePath == "":
                        self.report({'WARNING'}, "Welp, something went wrong.  Contact the developer.")
                        return {'CANCELLED'}

                    if objectFilePath == {'1'}:
                        self.report({'WARNING'}, 'The selected object has no set file path default.  Set it plzplzplz.')
                        return {'CANCELLED'}

                    if objectFilePath == {'2'}:
                        self.report({'WARNING'}, 'The selected objects file path default has no file path.  A file path is required to export.')
                        return {'CANCELLED'}

                    if objectFilePath == {'3'}:
                        self.report({'WARNING'}, 'The selected objects file path default is using a relative file path name, please tick off the Relative Path option when choosing the file path.')
                        return {'CANCELLED'}

                    print(objectFilePath)

                    # Store the objects initial position for object movement
                    # Also set file path names
                    collision = None
                    collisionFilePath = ""
                    animationFilePath = ""

                    originalLoc = Vector((0.0, 0.0, 0.0))
                    originalLoc[0] = object.location[0]
                    originalLoc[1] = object.location[1]
                    originalLoc[2] = object.location[2]


                    # //////////// - COLLISION SETUP - ////////////////////////////////////////////////////////
                    # ///////////////////////////////////////////////////////////////////////////////////
                    # ///////////////////////////////////////////////////////////////////////////////////

                    # If collision is turned on, sort that shit out
                    if object.GXObj.use_collision is True and isArmature is False:

                        # Setup the collision object
                        if object.GXObj.separate_collision is False:
                            DuplicateObject(context.active_object)
                            collision = context.active_object

                            # Generate collision on request
                            if object.GXObj.generate_convex is True:
                                bpy.ops.object.editmode_toggle()
                                bpy.ops.mesh.select_all(action='SELECT')

                                # From: http://www.blender.org/api/blender_python_api_2_62_1/bmesh.html#bmesh.from_edit_mesh
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

                            bpy.ops.object.select_all(action='DESELECT')
                            bpy.ops.object.select_pattern(pattern=object.GXObj.collision_object)

                            # A nice little error report if they have a bogus object name
                            if len(context.selected_objects) == 0:
                                self.report({'WARNING'}, 'The selected object has no defined collision object.')

                                FocusObject(object)

                                return {'FINISHED'}

                            bpy.context.scene.objects.active = bpy.data.objects[object.GXObj.collision_object]

                            DuplicateObject(context.active_object)
                            collision = context.active_object

                            collisionLoc = (0, 0, 0)
                            collisionLoc[0] = collision.location[0] - originalLoc[0]
                            collisionLoc[1] = collision.location[1] - originalLoc[1]
                            collisionLoc[2] = collision.location[2] - originalLoc[2]
                            MoveObject(collision, context, collisionLoc)


                        # If need be, setup the collision file path
                        if object.GXObj.export_collision is True or int(scn.engine_select) is 2:
                            collisionFilePath = defaultFilePath + object.name + "_CX" + ".fbx"

                        # Out of formality and bug checking, name the collision object
                        if int(scn.engine_select) is 1:
                            collision.name = "UCX_" + object.name

                        elif int(scn.engine_select) is 2:
                            collision.name = object.name + "_CX"


                    # //////////// - ANIMATION SETUP - ///////////////////////////////////////////////////////
                    # ///////////////////////////////////////////////////////////////////////////////////
                    if isArmature is True:
                        print("Animation is true?")

                        if exportAnimSeparate is True:
                            animFileName = defaultFilePath + object.name + "_AM" + ".fbx"

                    # //////////// - MODIFIER SETUP - ///////////////////////////////////////////////////////
                    # ///////////////////////////////////////////////////////////////////////////////////
                    if useTriangulate is True and applyModifiers is True:
                        hasTriangulate = self.AddTriangulate(object)


                    # /////////// - OBJECT MOVEMENT - ////////////////////////////////////////////////////////
                    # ///////////////////////////////////////////////////////////////////////////////////
                    if object.GXObj.use_collision is True and isArmature is False:
                        targets = [collision]
                        MoveObjects(object, targets, context, (0.0, 0.0, 0.0))

                    elif isArmature is True:
                        print("Moving Armature")
                        targets = [armature]
                        MoveObjects(object, targets, context, (0.0, 0.0, 0.0))

                    else:
                        MoveObject(object, context, (0.0, 0.0, 0.0))


                    print("Rawr")
                    print(globalScale)

                    # //////////// - EXPORT PROCESS - ////////////////////////////////////////////////////////
                    # ///////////////////////////////////////////////////////////////////////////////////
                    if object.GXObj.use_collision is True and isArmature is False:

                        if object.GXObj.export_collision is False and int(scn.engine_select) is not 2:
                            print("UE4 Combined Collision Export")
                            FocusObject(object)
                            SelectObject(collision)
                            self.ExportFBX(objectFilePath, globalScale, axisForward, axisUp, bakeSpaceTransform, applyModifiers, meshSmooth, objectTypes, useAnim, useAnimAction, useAnimOptimise)

                        else:
                            FocusObject(object)
                            self.ExportFBX(objectFilePath, globalScale, axisForward, axisUp, bakeSpaceTransform, applyModifiers, meshSmooth, objectTypes, useAnim, useAnimAction, useAnimOptimise)

                            FocusObject(collision)
                            self.ExportFBX(collisionFilePath, globalScale, axisForward, axisUp, bakeSpaceTransform, applyModifiers, meshSmooth, objectTypes, useAnim, useAnimAction, useAnimOptimise)

                    # Animation Export
                    elif isArmature is True:

                        print("Armature Export")

                        # If Animations need to be exported separately
                        if exportAnimSeparate is True:
                            objectTypes = {'MESH'}
                            animTypes = {'ARMATURE'}

                            FocusObject(object)
                            SelectObject(armature)
                            self.ExportFBX(objectFilePath, globalScale, axisForward, axisUp, bakeSpaceTransform, applyModifiers, meshSmooth, objectTypes, False, False, False)

                            self.ExportFBX(animFileName, globalScale, axisForward, axisUp, bakeSpaceTransform, applyModifiers, meshSmooth, animTypes, True, True, True)


                        else:
                            FocusObject(object)
                            SelectObject(armature)
                            self.ExportFBX(objectFilePath, globalScale, axisForward, axisUp, bakeSpaceTransform, applyModifiers, meshSmooth, objectTypes, useAnim, useAnimAction, useAnimOptimise)

                    else:
                        print("Standard Export")
                        FocusObject(object)
                        self.ExportFBX(objectFilePath, globalScale, axisForward, axisUp, bakeSpaceTransform, applyModifiers, meshSmooth, objectTypes, useAnim, useAnimAction, useAnimOptimise)


                    # Delete the collision object if a duplicate has been created.
                    if collision is not None and object.GXObj.separate_collision is False:
                        DeleteObject(collision)

                    # Otherwise move everything back to their initial positions
                    if object.GXObj.use_collision is True and isArmature is False:
                        targets = [collision]
                        MoveObjects(object, targets, context, originalLoc)

                    elif isArmature is True:
                        print("Moving Armature")
                        targets = [armature]
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
                    statement = "The group object " + group.name + " has no valid root object.  No root object, no exporting omo"
                    self.report({'WARNING'}, statement)
                    return {'FINISHED'}

                staticList = []
                collisionList = []
                armatureList = []

                # Obtain some object-specific preferences
                applyModifiers = True
                meshSmooth = 'OFF'
                objectTypes = {'MESH', 'ARMATURE'}
                useAnim = False
                useAnimAction = False
                useAnimOptimise = False

                exportAnimSeparate = False

                #/////////////////// - FILE NAME - /////////////////////////////////////////////////
                objectFilePath = ""
                objectFilePath = self.GetObjectFilePath(scn, group.GXGrp.location_default, group.name)

                if objectFilePath == "":
                    self.report({'WARNING'}, "Welp, something went wrong.  Contact the developer.")
                    return {'CANCELLED'}

                if objectFilePath == {'1'}:
                    self.report({'WARNING'}, 'One of the groups has no set file path default.  Set it plzplzplz.')
                    return {'CANCELLED'}

                if objectFilePath == {'2'}:
                    self.report({'WARNING'}, 'One of the groups file path default has no file path.  A file path is required to export.')
                    return {'CANCELLED'}

                if objectFilePath == {'3'}:
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
                            if object.name.find("_LP") != -1 and object.type == 'MESH':
                                staticList.append(object)

                            # Collision objects are only added if it can find a name match with a static mesh
                            elif object.name.find("_CX") != -1 and object.type == 'MESH':
                                collisionName = object.name
                                collisionName = collisionName.replace("_CX", "")

                                print("Collision Object Found")
                                print(object.name)
                                print(collisionName)

                                for staticObject in group.objects:

                                    if staticObject != object:
                                        if staticObject.name.find(collisionName + "_LP") != -1 and staticObject.type == 'MESH':

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
                if len(collisionList) > 0 and len(armatureList) == 0:
                    for object in collisionList:

                        # Give the collision object the right name, we will change it back afterwards
                        if int(scn.engine_select) is 1:
                            tempName = object.name.replace("_CX", "")
                            object.name = "UCX_" + tempName + "_LP"


                # /////////// - OBJECT MOVEMENT - ///////////////////////////////////////////////////
                # ///////////////////////////////////////////////////////////////////////////////////
                moveCenter = staticList + collisionList + armatureList
                MoveObjects(rootObject, moveCenter, context, (0.0, 0.0, 0.0))

                # /////////// - EXPORT - ///////////////////////////////////////////////////
                # ///////////////////////////////////////////////////////////////////////////////////

                FocusObject(rootObject)

                for object in staticList:
                    SelectObject(object)

                if len(armatureList) == 0:
                    for object in collisionList:
                        SelectObject(object)

                for object in armatureList:
                    SelectObject(object)

                self.ExportFBX(objectFilePath, globalScale, axisForward, axisUp, bakeSpaceTransform, applyModifiers, meshSmooth, {'MESH', 'ARMATURE'}, True, True, True)


                # /////////// - DELETE/RESTORE - ///////////////////////////////////////////////////
                # ///////////////////////////////////////////////////////////////////////////////////
                if len(armatureList) == 0:
                    for object in collisionList:
                        tempName = object.name.replace("UCX_", "")
                        tempName2 = tempName.replace("_LP", "")
                        print(tempName2)
                        object.name = tempName2 + "_CX"

                moveBack = staticList + collisionList + armatureList
                MoveObjects(rootObject, moveBack, context, rootObjectLocation)

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
