import bpy, bmesh, os, platform
from mathutils import Vector
from math import pi, radians, degrees
from bpy.types import Operator
from bpy.props import IntProperty, BoolProperty, FloatProperty, EnumProperty, PointerProperty, StringProperty, CollectionProperty

from .definitions import SelectObject, FocusObject, ActivateObject, DuplicateObject, DuplicateObjects, DeleteObject, SwitchObjectMode, MoveObject, MoveObjects, RotateObjectSafe, MoveBone, MoveObjects, MoveAll, RotateAll, RotateAllSafe, ScaleAll, CheckSuffix, CheckPrefix, CheckForTags, RemoveObjectTag, IdentifyObjectTag, CompareObjectWithTag, FindObjectWithTag, FindObjectsWithName, GetDependencies, AddParent, ClearParent, FindWorldSpaceObjectLocation, FindWorldSpaceBoneLocation, GetSceneGroups


class CAP_Export_Assets(Operator):
    """Exports all objects and groups in the scene that are marked for export."""

    bl_idname = "scene.cap_export"
    bl_label = "Export"

    def ExportFBX(self, filePath):
        # Calls the FBX Export API to make the export happen

        print("APPLY UNIT SCALE, IS IT FUCKING ON?", self.apply_unit_scale)

        print("Exporting", "*"*70)
        bpy.ops.export_scene.fbx(check_existing=False,
        filepath=filePath,
        filter_glob="*.fbx",
        version='BIN7400',
        use_selection=True,
        global_scale=self.global_scale,
        apply_unit_scale=self.apply_unit_scale,
        axis_forward=self.axisForward,
        axis_up=self.axisUp,
        bake_space_transform=self.bakeSpaceTransform,
        object_types=self.export_types,
        use_mesh_modifiers=self.applyModifiers,
        mesh_smooth_type=self.meshSmooth,
        use_mesh_edges=self.loose_edges,
        use_tspace=self.tangent_space,
        use_custom_props=False,
        use_armature_deform_only=self.use_armature_deform_only,
        add_leaf_bones=self.add_leaf_bones,
        bake_anim=self.exportAnim,
        bake_anim_use_all_bones=self.bake_anim_use_all_bones,
        bake_anim_use_nla_strips=self.bake_anim_use_nla_strips,
        bake_anim_use_all_actions=self.bake_anim_use_all_actions,
        bake_anim_force_startend_keying=self.bake_anim_force_startend_keying,
        #idk what this even is
        use_anim=self.exportAnim,
        use_anim_action_all=self.bake_anim_use_all_actions,
        use_default_take=self.use_default_take,
        use_anim_optimize=self.optimise_keyframes,
        anim_optimize_precision=6.0,
        path_mode=self.batch_mode,
        embed_textures=True,
        batch_mode='OFF',
        use_batch_own_dir=False,
        use_metadata=False)

        self.exportedFiles += 1

    def PrepareExportIndividual(self, context, targets, path, suffix):
        # Prepares export for multiple FBX files, each containing a separate
        # object.
        print(">>> Individual Pass <<<")
        for item in targets:
            print("-"*70)
            print("Exporting...... ", item.name)
            individualFilePath = path + item.name + suffix + ".fbx"
            print("Final File Path.", individualFilePath)

            # For the time being, manually move the object back and forth to
            # the world origin point.
            tempLoc = FindWorldSpaceObjectLocation(item, context)

            #print("Moving location to centre...")
            MoveObject(item, context, (0.0, 0.0, 0.0))

            bpy.ops.object.select_all(action='DESELECT')
            FocusObject(item)
            self.ExportFBX(individualFilePath)
            MoveObject(item, context, tempLoc)


    def PrepareExportCombined(self, targets, path, exportName, suffix):
        # Prepares export for an FBX file comprising of multiple objects
        print(">>> Exporting Combined Pass <<<")
        print("Checking export preferences...")

        bpy.ops.object.select_all(action='DESELECT')

        for item in targets:
            print("Exporting: ", item.name)
            print(item.name, "has export set to", item.CAPObj.enable_export)
            SelectObject(item)

        print(path)
        print(exportName)
        print(suffix)

        objectFilePath = path + exportName + suffix + ".fbx"
        print("Final File Path.", objectFilePath)

        self.ExportFBX(objectFilePath)

    def AddTriangulate(self, targetList):

        modType = {'TRIANGULATE'}

        for item in targetList:
            if item.type == 'MESH':
                stm = item.CAPStm
                stm.has_triangulate = False

                for modifier in item.modifiers:
                    if modifier.type in modType:
                        stm.has_triangulate = True

                # if we didn't find any triangulation, add it!
                if stm.has_triangulate == False:
                    FocusObject(item)
                    bpy.ops.object.modifier_add(type='TRIANGULATE')

                    for modifier in item.modifiers:
                        if modifier.type in modType:
                            #print("Triangulation Found")
                            modifier.quad_method = 'FIXED_ALTERNATE'
                            modifier.ngon_method = 'CLIP'
                            stm.has_triangulate = False

    def RemoveTriangulate(self, targetList):

        modType = {'TRIANGULATE'}

        for item in targetList:
            if item.type == 'MESH':
                if item.CAPStm.has_triangulate is False:
                    for modifier in item.modifiers:
                        if modifier.type in modType:
                            FocusObject(item)
                            bpy.ops.object.modifier_remove(modifier=modifier.name)

    def GetFilePath(self, context, locationEnum, fileName):
        # Get the file extension.  If the index is incorrect (as in, the user didnt set the fucking path)
        enumIndex = int(locationEnum)
        filePath = ""

        enumIndex -= 1

        defaultFilePath = self.exportInfo.location_presets[enumIndex].path
        print("Obtained location default: ", self.exportInfo.location_presets[enumIndex].path)

        if defaultFilePath == "":
            return {'2'}

        if defaultFilePath.find('//') != -1:
            return {'3'}

        filePath = defaultFilePath

        return filePath

    def CalculateFilePath(self, context, locationDefault, objectName, subDirectory):

        # Does the proper calculation and error handling for the file path, in conjunction with GetFilePath()
        print("Obtaining File...")
        print("File Enumerator = ", locationDefault)

        path = self.GetFilePath(context, locationDefault, objectName)

        print("Current Path: ", path)

        # //////////// - FILE DIRECTORY - ///////////////////////////////////////////
        # Need to extract the information from the pass name to see
        # if a sub-directory needs creating in the location default
        if subDirectory != "" or self.use_sub_directory is True or self.use_blend_directory is True:
            newPath = ""
            slash = "/"
            if platform.system() == 'Windows':
                slash = "\\"

            print("Constructing path...")

            if self.use_blend_directory is True:
                print(bpy.path.basename(bpy.context.blend_data.filepath))
                blendName = bpy.path.basename(bpy.context.blend_data.filepath)
                blendName = blendName.replace(".blend", "")
                print(blendName)
                if self.replaceInvalidChars is True:
                    blendName = self.ReplaceSystemChar(context, blendName)

                newPath = path + blendName + slash

            if self.use_sub_directory is True:
                if self.replaceInvalidChars is True:
                    objectName = self.ReplaceSystemChar(context, objectName)
                newPath = newPath + objectName + slash

            if subDirectory.replace(" ", "") != "":
                if self.replaceInvalidChars is True:
                    subDirectory = self.ReplaceSystemChar(context, subDirectory)
                newPath = newPath + subDirectory + slash

            if newPath == "":
                newPath = path

            print("newPath = ", newPath)
            print(">>> Sub-Directory found, appending...")

            if not os.path.exists(newPath):
                os.makedirs(newPath)

            print("Old Path: ", path)
            path = newPath
            print("New Path: ", path)

        return path

    # CHANGE ME PLZ
    def GetNormals(self, enum):
        # I should change this, this is redundant.

        if enum == '1':
            return 'EDGE'
        if enum == '2':
            return 'FACE'
        if enum == '3':
            return 'OFF'

    def GetExportInfo(self, exportDefault):
        # Stores a whole load of export-related settings for re-use throughout
        # the operator

        self.use_blend_directory = exportDefault.use_blend_directory
        self.use_sub_directory = exportDefault.use_sub_directory
        self.bundle_textures = exportDefault.bundle_textures
        self.filter_render = exportDefault.filter_render
        self.export_types = exportDefault.export_types

        export_types = exportDefault.export_types
        self.bundle_textures = exportDefault.bundle_textures
        self.batch_mode = 'AUTO'
        if self.bundle_textures is True:
            self.batch_mode = 'COPY'

        self.axisForward = exportDefault.axis_forward
        self.axisUp = exportDefault.axis_up
        self.global_scale = exportDefault.global_scale
        self.bakeSpaceTransform = exportDefault.bake_space_transform
        self.reset_rotation = exportDefault.reset_rotation

        self.apply_unit_scale = exportDefault.apply_unit_scale
        self.loose_edges = exportDefault.loose_edges
        self.tangent_space = exportDefault.tangent_space

        self.use_armature_deform_only = exportDefault.use_armature_deform_only
        self.add_leaf_bones = exportDefault.add_leaf_bones
        self.preserve_armature_constraints = exportDefault.preserve_armature_constraints
        self.primary_bone_axis = exportDefault.primary_bone_axis
        self.secondary_bone_axis = exportDefault.secondary_bone_axis
        self.armature_nodetype = exportDefault.armature_nodetype

        self.bake_anim_use_all_bones = exportDefault.bake_anim_use_all_bones
        self.bake_anim_use_nla_strips = exportDefault.bake_anim_use_nla_strips
        self.bake_anim_use_all_actions = exportDefault.bake_anim_use_all_actions
        self.bake_anim_force_startend_keying = exportDefault.bake_anim_force_startend_keying
        self.use_default_take = exportDefault.use_default_take
        self.optimise_keyframes = exportDefault.optimise_keyframes
        self.bake_anim_step = exportDefault.bake_anim_step
        self.bake_anim_simplify_factor = exportDefault.bake_anim_simplify_factor

        self.x_unity_rotation_fix = exportDefault.x_unity_rotation_fix

    def SetupScene(self, context):
        # Stores various scene settings and display features to restore later
        # when the plugin is finished

        self.active = None
        self.selected = []

        if context.active_object is not None:
            for sel in context.selected_objects:
                if sel.name != context.active_object.name:
                    self.selected.append(sel)
        else:
            for sel in context.selected_objects:
                self.selected.append(sel)

        self.active = context.active_object

        # Save the current cursor location
        cursor_loc = bpy.data.scenes[bpy.context.scene.name].cursor_location
        self.cursorLocation = [cursor_loc[0], cursor_loc[1], cursor_loc[2]]

        # Keep a record of the current object mode
        mode = bpy.context.mode
        bpy.ops.object.mode_set(mode='OBJECT')

        # Ensure all layers are visible
        self.layersBackup = []
        for layer in context.scene.layers:
            layerVisibility = layer
            self.layersBackup.append(layerVisibility)

        context.scene.layers = (True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True)

        # Record object visibility
        self.hiddenList = []
        self.selectList = []
        self.hiddenObjectList = []

        for item in context.scene.objects:
            self.hiddenObjectList.append(item)
            isHidden = item.hide
            self.hiddenList.append(isHidden)
            isSelectable = item.hide_select
            self.selectList.append(isSelectable)

        for item in context.scene.objects:
            item.hide_select = False

        # If an object has locked Location/Rotation/Scale values, store them and turn it on
        self.translateList = []
        print("Checking locked objects")
        for item in context.scene.objects:
            boolList = []
            for i, x in enumerate(item.lock_location):
                boolList.append(item.lock_location[i])
            for i, x in enumerate(item.lock_rotation):
                boolList.append(item.lock_rotation[i])
            for i, x in enumerate(item.lock_scale):
                boolList.append(item.lock_scale[i])

            if True in boolList:
                entry = {'object_name': item.name, 'lock_list': boolList}
                self.translateList.append(entry)

        for item in context.scene.objects:
            item.lock_location = (False, False, False)
            item.lock_rotation = (False, False, False)
            item.lock_scale = (False, False, False)

        # If any armatures are in any non-object modes, we need to change this
        self.armatureMode = []
        for item in context.scene.objects:
            if item.type == 'ARMATURE':
                mode = SwitchObjectMode('OBJECT', item)
                if mode != None:
                    entry = {'object_name': item.name, 'mode': mode}
                    self.armatureMode.append(entry)

        # Find objects affected by specific constraints, and work out how much
        # they need to be moved by, in order to keep the scene representative
        self.constraintList = []
        self.constraintObjects = []
        print("Searching for constraints...")
        for item in context.scene.objects:
            i = 0

            for constraint in item.constraints:
                if item not in self.constraintObjects:
                    # Record the current object location for later
                    trueLocation = FindWorldSpaceObjectLocation(item, context)
                    constraintLocation = Vector((0.0, 0.0, 0.0))
                    print("TrueLocation", trueLocation)
                    print("constraintLocation", constraintLocation)

                    entry = {'object_name': item.name, 'true_location': trueLocation, 'constraint_location': constraintLocation}
                    self.constraintObjects.append(entry)

                entry = {'object_name': item.name, 'index': i, 'enabled': constraint.mute, 'influence': constraint.influence}
                self.constraintList.append(entry)

                i += 1

        # NOW WE CAN FUCKING MUTE THEM
        for entry in self.constraintList:
            item = context.scene.objects[entry['object_name']]
            constraint = item.constraints[entry['index']]

            # Mute the constraint
            constraint.mute = True
            constraint.influence = 0.0

        # Reset the constraint location now we have a 'true' location
        for entry in self.constraintObjects:
            item = context.scene.objects[entry['object_name']]
            entry['constraint_location'] = FindWorldSpaceObjectLocation(item, context)
            print("NEW CONSTRAINT LOCATION", item.name, entry['constraint_location'])

        # Now all problematic constraints have been turned off, we can safely move
        # objects to their initial positions
        for entry in self.constraintObjects:
            item = context.scene.objects[entry['object_name']]
            print("Moving Object...", item.name, entry['true_location'])
            MoveObject(item, context, entry['true_location'])
            print("New Object Location = ", item.location)
            print("-"*20)


        # Now we can unhide and deselect everything
        bpy.ops.object.hide_view_clear()
        bpy.ops.object.select_all(action='DESELECT')

    def RestoreScene(self, context):
        # Restores all previously held scene settings and display features
        # after the operator is done shuffling it

        # Restore constraint object positions
        for entry in self.constraintObjects:
            item = context.scene.objects[entry['object_name']]
            print(entry)
            print("Moving Object...", item.name, entry['constraint_location'])
            MoveObject(item, context, entry['constraint_location'])
            print("New Object Location = ", item.name, item.location)

        # Restore Constraint Defaults
        for entry in self.constraintList:
            item = bpy.data.objects[entry['object_name']]
            index = entry['index']
            item.constraints[index].mute = entry['enabled']
            item.constraints[index].influence = entry['influence']

        # Restore visibility defaults
        while len(self.hiddenObjectList) != 0:
            item = self.hiddenObjectList.pop()
            hide = self.hiddenList.pop()
            hide_select = self.selectList.pop()

            item.hide = hide
            item.hide_select = hide_select

        # Turn off all other layers
        i = 0
        while i < 20:
            context.scene.layers[i] = self.layersBackup[i]
            i += 1

        # If an object has locked Location/Rotation/Scale values, store them and turn it on
        while len(self.translateList) != 0:
            entry = self.translateList.pop()
            item = bpy.data.objects[entry['object_name']]
            boolList = entry['lock_list']

            item.lock_location[0] = boolList[0]
            item.lock_location[1] = boolList[1]
            item.lock_location[2] = boolList[2]
            item.lock_rotation[0] = boolList[3]
            item.lock_rotation[1] = boolList[4]
            item.lock_rotation[2] = boolList[5]
            item.lock_scale[0] = boolList[6]
            item.lock_scale[1] = boolList[7]
            item.lock_scale[2] = boolList[8]

        # Restore armature modes
        while len(self.armatureMode) != 0:
            entry = self.armatureMode.pop()
            mode = SwitchObjectMode(entry['mode'], bpy.data.objects[entry['object_name']])

        # Re-select the objects previously selected
        if self.active is not None:
            FocusObject(self.active)

        for sel in self.selected:
            SelectObject(sel)

        if self.active is None and len(self.selected) == 0:
            bpy.ops.object.select_all(action='DESELECT')

        # Restore the 3D cursor
        bpy.data.scenes[bpy.context.scene.name].cursor_location = self.cursorLocation

        print("Rawr")

    def StartSceneMovement(self, context, target, targetObjects, targetRot):

        # /////////// - OBJECT MOVEMENT - ///////////////////////////////////////////////////
        # ///////////////////////////////////////////////////////////////////////////////////
        #self.forwardRotations = []
        #self.reverseRotations = []

        # We need to record rotations in case they need to be restored
        # for when Unity completely destroys them <3
        #for item in targetObjects:
            #forwardRot = (item.rotation_euler[0], item.rotation_euler[1], item.rotation_euler[2])
            #reverseRot = (-item.rotation_euler[0], -item.rotation_euler[1], -item.rotation_euler[2])
            #print("COLLECTING ROTATIONS...", forwardRot)
            #self.forwardRotations.append(forwardRot)
            #self.reverseRotations.append(reverseRot)

        # If the user wanted to reset the rotation, time to add more
        # annoying levels of complexity to the mix and reset the rotation!
        #if self.reset_rotation is True:
            #print("Reset Rotation active, resetting rotations!")
            #reverseRotation = (-targetRot[0], -targetRot[1], -targetRot[2])
            #RotateAllSafe(target, context, reverseRotation, False)

        # If the user wanted unity, time to stomp on the rotation
        # only the objects being exported should be applied
        if self.x_unity_rotation_fix is True:
            print("Unity rotation fix active!")
            RotateAllSafe(target, context, (radians(-90), 0, 0), True)
            bpy.ops.object.select_all(action='DESELECT')
            for item in targetObjects:
                SelectObject(item)
                ActivateObject(item)

            bpy.ops.object.transform_apply(
                location=False,
                rotation=True,
                scale=False
                )
            RotateAllSafe(target, context, (radians(90), 0, 0), True)

        if self.use_scene_origin is False:
            print("Moving scene...")
            MoveAll(target, context, Vector((0.0, 0.0, 0.0)))

    def FinishSceneMovement(self, context, target, targetObjects, targetLoc, targetRot):
        # Move objects back
        if self.reset_rotation is True:
            RotateAllSafe(self.RO, context, targetRot, True)

        if self.use_scene_origin is False:
            MoveAll(self.RO, context, targetLoc)

        if self.x_unity_rotation_fix is True:
            bpy.ops.object.select_all(action='DESELECT')

            for item in targetObjects:
                SelectObject(item)
                ActivateObject(item)
            bpy.ops.object.transform_apply(
                location=False,
                rotation=True,
                scale=False
                )

            #for i, item in enumerate(targetObjects):
                #RotateObjectSafe(item, context, self.reverseRotations[i], False)

            #bpy.ops.object.select_all(action='DESELECT')
            #for item in targetObjects:
                #SelectObject(item)
                #ActivateObject(item)
            #bpy.ops.object.transform_apply(
                #location=False,
                #rotation=True,
                #scale=False
                #)

            #for i, item in enumerate(targetObjects):
                #RotateObjectSafe(item, context, self.forwardRotations[i], True)

    def SetupMovement(self, context):

        if self.preserve_armature_constraints is True:
            return

        # We need to do similar constraint evaluation for armatures
        # Find translate constraints. mute them and move the affected bones
        # to make the plugin movement successful.
        self.armatureConstraintList = []
        self.armatureConstraintObjects = []
        for item in context.scene.objects:
            if item.type == 'ARMATURE':
                for bone in item.pose.bones:
                    i = 0
                    for constraint in bone.constraints:
                        if item not in self.armatureConstraintObjects:
                            trueLocation = FindWorldSpaceBoneLocation(item, context, bone)
                            constraintLocation = Vector((bone.location[0], bone.location[1], bone.location[2]))

                            entry = {'object_name': item.name, 'bone_name': bone.name, 'true_location': trueLocation, 'constraint_location': constraintLocation}
                            self.armatureConstraintObjects.append(entry)

                        entry = {'object_name': item.name, 'bone_name': bone.name, 'index': i, 'enabled': constraint.mute, 'influence': constraint.influence}
                        self.armatureConstraintList.append(entry)

                        i += 1

        print("-"*40)
        print("-"*40)

        # NOW WE CAN FUCKING MUTE THEM
        for entry in self.armatureConstraintList:
            item = context.scene.objects[entry['object_name']]
            for bone in item.pose.bones:
                if bone.name == entry['bone_name']:
                    constraint = bone.constraints[entry['index']]

                    # Mute the constraint
                    constraint.mute = True
                    constraint.influence = 0.0

        print("-"*40)
        print("-"*40)

        # Reset the constraint location now we have a 'true' location
        for entry in self.armatureConstraintObjects:
            item = context.scene.objects[entry['object_name']]
            for bone in item.pose.bones:
                if bone.name == entry['bone_name']:
                    entry['constraint_location'] = FindWorldSpaceBoneLocation(item, context, bone)
                    print("NEW CONSTRAINT LOCATION", item.name, bone.name, entry['constraint_location'])

        print("-"*40)
        print("-"*40)

        # Now all problematic constraints have been turned off, we can safely move
        # objects to their initial positions
        for entry in self.armatureConstraintObjects:
            item = context.scene.objects[entry['object_name']]
            for bone in item.pose.bones:
                if bone.name == entry['bone_name']:
                    #print("Moving Bone...", item.name, bone.name, entry['true_location'])
                    MoveBone(item, bone, context, entry['true_location'])
                    #print("New Bone Location = ", bone.location)

        print("-"*40)
        print("-"*40)

    def FinishMovement(self, context):
        if self.preserve_armature_constraints is True:
            return

        # Restore constraint object positions
        for entry in self.armatureConstraintObjects:
            item = context.scene.objects[entry['object_name']]
            for bone in item.pose.bones:
                if bone.name == entry['bone_name']:
                    #print("Moving Bone...", item.name, bone.name)
                    MoveBone(item, bone, context, entry['constraint_location'])
                    #print("New Bone Location = ", bone.location)

        # Restore Constraint Defaults
        for entry in self.armatureConstraintList:
            item = bpy.data.objects[entry['object_name']]
            for bone in item.pose.bones:
                if bone.name == entry['bone_name']:
                    index = entry['index']
                    bone.constraints[index].mute = entry['enabled']
                    bone.constraints[index].influence = entry['influence']

    def ReplaceSystemChar(self, context, name):
        # Replaces invalid directory characters in names

        print("Checking Directory...", name)
        returnName = name
        if platform.system() == 'Windows':
            invalidCharacters = ["/", "*", "?", "\"", "<", ">", "|", ":"]
            for char in invalidCharacters:
                returnName = returnName.replace(char, "_")

        elif platform.system() == 'Darwin':
            invalidCharacters = [":", "/"]
            for char in invalidCharacters:
                returnName = returnName.replace(char, "_")

        elif platform.system() == 'linux' or platform.system() == 'linux2':
            invalidCharacters = [":", "/"]
            for char in invalidCharacters:
                returnName = returnName.replace(char, "_")

        return returnName

    def CheckSystemChar(self, context, name):
        # Checks for invalid directory characters in names

        print("Checking Directory...", name)
        if platform.system() == 'Windows':
            invalidCharacters = ["/", "*", "?", "\"", "<", ">", "|", ":"]
            invalidCaptured = []
            for char in invalidCharacters:
                if name.find(char) != -1:
                    invalidCaptured.append(char)

        elif platform.system() == 'Darwin':
            invalidCharacters = [":", "/"]
            invalidCaptured = []
            for char in invalidCharacters:
                if name.find(char) != -1:
                    invalidCaptured.append(char)

        elif platform.system() == 'linux' or platform.system() == 'linux2':
            invalidCharacters = [":", "/"]
            invalidCaptured = []
            for char in invalidCharacters:
                if name.find(char) != -1:
                    invalidCaptured.append(char)

        print("Invalid characters found...", invalidCaptured)
        return invalidCaptured

    def CheckForErrors(self, context):
        # Ensures that the scene is setup with correct settings, before proceeding
        # with the export.

        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__package__].preferences
        exp = bpy.data.objects[addon_prefs.default_datablock].CAPExp

        # Check all active file presets for valid directory names
        # These lists will be analysed later
        nameCheck = []
        for export in exp.file_presets:
            if export.use_blend_directory is True:
                blendName = bpy.path.basename(bpy.context.blend_data.filepath)
                nameCheck.append([" Blend Name", blendName, " Preset", export.name])
            for ePass in export.passes:
                if ePass.sub_directory != "":
                    nameCheck.append([" Pass Folder", ePass.sub_directory, " Preset", export.name])
                if ePass.file_suffix != "":
                    nameCheck.append([" File Suffix", ePass.file_suffix, " Preset", export.name])

        print("names found...", nameCheck)

        # Checks for any easily-preventable errors
        for object in context.scene.objects:
            if object.CAPObj.enable_export is True:

                # Check Export Key
                expKey = int(object.CAPObj.export_default) - 1
                if expKey == -1:
                    statement = "The selected object " + object.name + " has no export default selected.  Please define!"
                    FocusObject(object)
                    return statement

                # Check Export Sub-Directory
                export = exp.file_presets[expKey]
                if export.use_sub_directory is True:
                    objName = object.name
                    nameCheck.append([" Object Name", objName, " Preset", export.name])

                # Check Location Default
                if int(object.CAPObj.location_default) == 0:
                    statement =  "The selected object " + object.name + " has no location preset defined, please define one!"
                    FocusObject(object)
                    return statement

                self.exportCount += 1

        # If we're using Unity export options, ensure that every object mesh has a single user
        if export.x_unity_rotation_fix is True:
            for item in context.scene.objects:
                data = item.data
                if data is not None:
                    print(data.users)
                    if data.users > 1:
                        FocusObject(item)
                        statement = "Sorry, but currently, this Unity Export Preset requires that all scene objects be single-user only.  Please ensure all objects have only one user, before using it."
                        return statement


        # Check all scene groups for potential errors
        for group in GetSceneGroups(context.scene, True):
            if group.CAPGrp.enable_export is True:

                # Check Export Key
                expKey = int(group.CAPGrp.export_default) - 1
                if expKey == -1:
                    bpy.ops.object.select_all(action='DESELECT')
                    for item in group.objects:
                        SelectObject(item)
                    statement = "The selected group " + group.name + " has no export default selected.  Please define!"
                    return statement

                # Check Export Sub-Directory
                export = exp.file_presets[expKey]
                if export.use_sub_directory is True:
                    name = group.name
                    nameCheck.append([" Group Name", name, " Preset", export.name])

                # Check Location Default
                if int(group.CAPGrp.location_default) == 0:
                    bpy.ops.object.select_all(action='DESELECT')
                    for item in group.objects:
                        SelectObject(item)
                    statement =  "The selected group " + group.name + " has no location preset defined, please define one!"
                    return statement

                self.exportCount += 1

        # Check Paths to ensure the chatacters contained are valid.
        i = 0
        while i < len(exp.location_presets):
            enumIndex = i
            filePath = ""
            enumIndex -= 1

            defaultFilePath = exp.location_presets[enumIndex].path
            print("Checking File Paths...", defaultFilePath)

            if defaultFilePath == "":
                statement = "The path for " + exp.location_presets[enumIndex].name + " cannot be empty.  Please give the Location a valid file path."
                return statement

            if defaultFilePath.find('//') != -1:
                statement =  "The path " + exp.location_presets[enumIndex].name + "is using a relative file path name, please turn off the Relative Path option when choosing a file path in the file browser."
                return statement

            i += 1

        # Check all collected names for invalid characters
        if self.replaceInvalidChars is False:
            for name in nameCheck:
                print("Checking Directory...", name)
                result = self.CheckSystemChar(context, name[1])
                returnStatement = ""

                if len(result) != 0:
                    characterlead = ", is using the invalid file character "
                    end = ".  Please remove the invalid character from the path name."

                    if len(result) > 1:
                        characterlead = ", is using the invalid file characters "
                        end = ".  Please remove the invalid characters from the path name."

                    while len(result) != 0:
                        text = result.pop()
                        returnStatement += text + " "

                    statement = "The" + name[0] + " " + name[1] + ", belonging to the export, " + name[3] + characterlead + returnStatement + end
                    return statement

        return None

    def CheckAnimation(self, context):
        # Not currently used until further notice

        for item in context.scene.objects:
            print(item.name)
            print(item.animation_data)

            if item.animation_data is not None:
                print(item.animation_data.action)
                print(item.animation_data.drivers)
                print(item.animation_data.nla_tracks)

                for driver in item.animation_data.drivers:
                    print("------Driver:", driver)
                    print(len(driver.driver.variables))

                    for variable in driver.driver.variables:
                        print("---Variable:", variable.name)
                        print(len(variable.targets))

                        for target in variable.targets:
                            print("-Target:", target)
                            print("Bone Target.....", target.bone_target)
                            print("Data Path.......", target.data_path)
                            print("ID..............", target.id)
                            print("ID Type.........", target.id_type)
                            print("Transform Space.", target.transform_space)
                            print("Transform Type..", target.transform_type)

                if item.animation_data.action is not None:
                    action = item.animation_data.action
                    print("FCurves......", action.fcurves)
                    print("Frame Range..", action.frame_range)
                    print("Groups.......", action.groups)
                    print("ID Root......", action.id_root)

                    for curve in action.fcurves:
                        print(curve.driver.data_path)
                        #for variable in curve.driver.variables:
                            #for target in variable.targets:
                                #print("-Target:", target)
                                #print("Bone Target.....", target.bone_target)
                                #print("Data Path.......", target.data_path)
                            #    print("ID..............", target.id)
                            #    print("ID Type.........", target.id_type)
                            #    print("Transform Space.", target.transform_space)
                            #    print("Transform Type..", target.transform_type)


        print(">>>> CHECKED ANIMATION <<<<")

    ###############################################################
    # EXECUTE
    ###############################################################
    def execute(self, context):
        scn = context.scene.CAPScn
        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__package__].preferences
        self.exportInfo = bpy.data.objects[addon_prefs.default_datablock].CAPExp
        self.replaceInvalidChars = addon_prefs.substitute_directories

        self.exportCount = 0
        self.exportedObjects = 0
        self.exportedGroups = 0
        self.exportedFiles = 0

        print("")
        print("")
        print("")
        print("#"*70)
        print(">>>>>>>>>>>>>>>>>>>>> BEGIN EXPORT PROCESS >>>>>>>>>>>>>>>>>>>>>")
        print("#"*70)

        # Check for stupid errors before continuing
        result = self.CheckForErrors(context)
        if result is not None:
            self.report({'WARNING'}, result)
            return {'FINISHED'}


        # Setup and store scene variables, to be restored when complete
        self.SetupScene(context)
        context.window_manager.progress_begin(0, self.exportCount)


        ###############################################################
        # OBJECT CYCLE
        ###############################################################
        # Cycle through the available objects
        for object in context.scene.objects:
            if object.CAPObj.enable_export is True:

                # Before we get to pass-specific data, this section gets and calculates
                # important data, applicable to all passes

                print("-"*109)
                print("NEW JOB", "-"*100)
                print("Object", object.name, "found.")
                print("-"*109)

                #Get the export default for the object
                expKey = int(object.CAPObj.export_default) - 1

                if expKey == -1:
                    statement = "The selected object " + object.name + " has no export default selected.  Please define!"
                    FocusObject(object)
                    self.report({'WARNING'}, statement)
                    self.RestoreScene(context)
                    return {'FINISHED'}

                # Get the export default and set the variables here
                exportDefault = self.exportInfo.file_presets[expKey]
                self.GetExportInfo(exportDefault)

                # Get the root object and set some more variables!
                # RO = Root Object, keeps it short and snappy.
                self.RO = object
                self.ROType = IdentifyObjectTag(context, self.RO, exportDefault)
                self.use_scene_origin = self.RO.CAPObj.use_scene_origin

                # If they asked us not preserve armature constraints, we can
                # do our jerb and ensure they don't screw things up beyond this code
                if self.preserve_armature_constraints is False:
                    self.SetupArmatureConstraints(context)

                # Need to get the movement location.  If the user wants to use the scene origin though,
                # just make it 0
                ROLoc = Vector((0.0, 0.0, 0.0))
                RORot = (0.0, 0.0, 0.0)

                if self.use_scene_origin is False:
                    tempROL = FindWorldSpaceObjectLocation(self.RO, context)
                    ROLoc = Vector((tempROL[0], tempROL[1], tempROL[2]))
                    RORot = (self.RO.rotation_euler[0], self.RO.rotation_euler[1], self.RO.rotation_euler[2])


                # Get the object's base name
                objectName = ""
                if self.ROType != -1:
                    objectName = RemoveObjectTag(context, self.RO, exportDefault)
                else:
                    objectName = self.RO.name


                for objPass in exportDefault.passes:
                    print("-"*109)
                    print("NEW PASS", "-"*100)
                    print("-"*109)
                    print("Export pass", objPass.name, "being used on object", object.name)

                    # Obtain some pass-specific preferences
                    self.applyModifiers = objPass.apply_modifiers
                    self.useTriangulate = objPass.triangulate
                    self.exportIndividual = objPass.export_individual
                    self.objectUseTags = objPass.use_tags_on_objects
                    self.exportAnim = objPass.export_animation
                    self.meshSmooth = self.GetNormals(self.RO.CAPObj.normals)

                    activeTags = []
                    i = 0

                    # If the user wishes object exports to use tags, we need to
                    # create a list for every tag in use
                    if self.objectUseTags is True:
                        print("Processing tags...")
                        for passTag in objPass.tags:
                            if passTag.use_tag is True:
                                print("Active Tag Found: ", passTag.name)
                                activeTags.append(exportDefault.tags[i])

                            i += 1

                    # Collect information on path names for later
                    path = ""                                # Path given from the location default
                    fileName = ""                            # File name for the object (without tag suffixes)
                    suffix = objPass.file_suffix             # Additional file name suffix
                    subDirectory = objPass.sub_directory     # Whether a sub-directory needs to be created

                    # Lists for the renaming feature
                    renameNameList = []
                    renameObjectList = []

                    # Lets see if the root object can be exported...
                    expRoot = False

                    if self.ROType == -1:
                        if len(activeTags) == 0:
                            expRoot = True
                    elif len(activeTags) == 0:
                        expRoot = True
                    elif objPass.tags[self.ROType].use_tag is True or (self.exportIndividual is True and self.objectUseTags is True):
                        expRoot = True

                    if exportDefault.filter_render is True and self.RO.hide_render is True:
                        expRoot = False

                    print("Export Root = ", expRoot)



                    #/////////////////// - FILE NAME - /////////////////////////////////////////////////
                    path = self.CalculateFilePath(context, self.RO.CAPObj.location_default, objectName, subDirectory)

                    if path.find("WARNING") == 0:
                        path = path.replace("WARNING: ", "")
                        self.report({'WARNING'}, path)
                        self.RestoreScene(context)
                        return {'CANCELLED'}

                    print("Path created...", path)



                    #/////////////////// - FIND OBJECTS - /////////////////////////////////////////////////
                    # In this new system, we only have to search through objects that meet the criteria using one function,
                    # only for the tags that are active
                    print(">>>> Collecting Objects <<<<")
                    objectList = []

                    # We first want to collect all objects that share the same name,
                    # then if any tags are on, we filter those results
                    if self.objectUseTags is True:
                        results = FindObjectsWithName(context, objectName)
                        while len(results) != 0:
                            item = results.pop()
                            if item.name != self.RO.name:
                                objectList.append(item)

                        print("Objects found...", objectList)

                        # If we have any active tags, we then need to filter our results
                        if len(activeTags) > 0:
                            print(">>>> Tags On, searching... <<<")
                            results = []

                            # For each tag, try to search for an object that matches the tag
                            for tag in activeTags:
                                print(tag.name)
                                for item in objectList:
                                    print(item)
                                    if CompareObjectWithTag(context, item, tag) is True:
                                        results.append(item)

                                        # If the active tag has the ability to replace names, do it here.
                                        if tag.x_ue4_collision_naming is True and self.exportIndividual is False:
                                            print("SUPER SECRET REPLACE NAME FUNCTION USED!")
                                            renameObjectList.append(item)
                                            renameNameList.append(item.name)

                                            item.name = item.name.replace(tag.name_filter, "")
                                            item.name = "UCX_" + item.name + exportDefault.tags[1].name_filter

                                            print("Name replaced...", item.name)

                            objectList.clear()
                            for item in results:
                                objectList.append(item)

                        # If Filter by Rendering is on, we need to check our results against that
                        if exportDefault.filter_render is True:
                            results = []

                            while len(objectList) != 0:
                                item = objectList.pop()
                                if item.hide_render is False:
                                    results.append(item)

                            for item in results:
                                objectList.append(item)

                    # Debug check for found objects
                    print("Checking found objects...")
                    for item in objectList:
                        print(item.name)


                    # /////////// - OBJECT MOVEMENT - ///////////////////////////////////////////////////
                    # ///////////////////////////////////////////////////////////////////////////////////
                    movedObjects = []
                    movedObjects += objectList
                    movedObjects.append(self.RO)
                    sceneOrigin = None

                    if self.use_scene_origin is False:
                        self.StartSceneMovement(context, self.RO, movedObjects, RORot)
                    else:
                        bpy.ops.view3d.snap_cursor_to_center()
                        bpy.ops.object.select_all(action='DESELECT')
                        bpy.ops.object.empty_add(type='PLAIN_AXES')
                        sceneOrigin = bpy.context.scene.objects.active
                        self.StartSceneMovement(context, sceneOrigin, movedObjects, RORot)

                    # /////////// - MODIFIERS - ///////////////////////////////////////////////////
                    # ////////////////////////////////////////////////////////////////////////////
                    print(">>> Triangulating Objects <<<")
                    triangulateList = []
                    triangulateList += objectList

                    if expRoot is True:
                        triangulateList.append(self.RO)

                    if self.useTriangulate is True and self.applyModifiers is True:
                         self.AddTriangulate(triangulateList)

                    # //////////// - EXPORT PROCESS - ///////////////////////////////////////////
                    # A separate FBX export function call for every corner case isnt actually necessary
                    finalExportList = []
                    finalExportList += objectList

                    if expRoot is True:
                        print("expRoot = ", expRoot)
                        finalExportList.append(self.RO)

                    if len(finalExportList) > 0:
                        if self.exportIndividual is True:
                            self.PrepareExportIndividual(context, finalExportList, path, suffix)

                        else:
                            self.PrepareExportCombined(finalExportList, path, objectName, suffix)


                    # /////////// - DELETE/RESTORE - ///////////////////////////////////////////////////
                    # ///////////////////////////////////////////////////////////////////////////////////
                    # Restore names
                    i = 0
                    for item in renameObjectList:
                        item.name = renameNameList[i]
                        i += 1

                    # Remove any triangulation modifiers
                    if self.useTriangulate is True and self.applyModifiers is True:
                         self.RemoveTriangulate(triangulateList)

                    # Reverse movement and rotation
                    if self.use_scene_origin is False:
                        self.FinishSceneMovement(context, self.RO, movedObjects, ROLoc, RORot)
                    else:
                        self.FinishSceneMovement(context, sceneOrigin, movedObjects, ROLoc, RORot)
                        DeleteObject(sceneOrigin)

                    print(">>> Pass Complete <<<")

                if self.preserve_armature_constraints is False:
                    self.RestoreArmatureConstraints(context)

                # Count up exported objects
                if len(exportDefault.passes) > 0:
                    self.exportedObjects += 1
                    self.exportCount += 1
                    context.window_manager.progress_update(self.exportCount)
                    print(">>> Object Export Complete <<<")


        ###############################################################
        # GROUP CYCLE
        ###############################################################
        # Now hold up, its group time!
        for group in GetSceneGroups(context.scene, True):
            if group.CAPGrp.enable_export is True:

                print("-"*79)
                print("NEW JOB", "-"*70)
                print("-"*79)
                print(group.name)

                # Before we do anything, check that a root object exists
                self.RO = None
                self.ROName = ""
                self.ROType = 0
                self.use_scene_origin = False
                rootObjectInGroup = False

                # Find the root object in a group, if thats where it's located
                for item in group.objects:
                    if item.name == group.CAPGrp.root_object:
                        self.RO = item
                        self.ROName = item.name
                        rootObjectInGroup = True

                # Otherwise, find it elsewhere
                if rootObjectInGroup == False:
                    for item in context.scene.objects:
                        if item.name == group.CAPGrp.root_object:
                            self.RO = item
                            self.ROName = item.name

                if self.RO == None:
                    self.use_scene_origin = True
                    print("No root object is currently being used, proceed!")

                #Get the export default for the object
                expKey = int(group.CAPGrp.export_default) - 1

                if expKey == -1:
                    statement = "The group " + group.name + " has no export default selected.  Please define!"
                    self.report({'WARNING'}, statement)
                    self.RestoreScene(context)
                    return {'FINISHED'}

                # Collect hidden defaults to restore afterwards.
                objectName = group.name

                exportDefault = self.exportInfo.file_presets[expKey]
                self.use_blend_directory = exportDefault.use_blend_directory
                self.use_sub_directory = exportDefault.use_sub_directory
                self.GetExportInfo(exportDefault)
                print("Using Export Default...", exportDefault.name, ".  Export Key", expKey)


                # Identify what tag the root object has
                if self.RO != None:
                    self.ROType = IdentifyObjectTag(context, self.RO, exportDefault)
                    print("Root type is...", self.ROType)

                # Get the root object location for later use
                ROLoc = Vector((0.0, 0.0, 0.0))
                RORot = (0.0, 0.0, 0.0)

                if self.RO != None:
                    tempROL = FindWorldSpaceObjectLocation(self.RO, context)
                    ROLoc = Vector((tempROL[0], tempROL[1], tempROL[2]))
                    RORot = (self.RO.rotation_euler[0], self.RO.rotation_euler[1], self.RO.rotation_euler[2])

                #/////////////////// - PASSES - /////////////////////////////////////////////////
                for objPass in exportDefault.passes:

                    print("-"*59)
                    print("NEW PASS", "-"*50)
                    print("-"*59)
                    print("Export pass", objPass.name, "being used on the group", group.name)
                    print("Root object.....", self.ROName)

                    activeTags = []
                    taggedList = []
                    objectList = []

                    # Lists for the UE4 renaming feature
                    renameNameList = []
                    renameObjectList = []

                    # Create a list for every tag in use
                    i = 0
                    print("Processing tags...")
                    for passTag in objPass.tags:
                        if passTag.use_tag is True:
                            print("Active Tag Found: ", passTag.name)
                            activeTags.append(exportDefault.tags[i])

                        i += 1

                    # Obtain some object-specific preferences
                    self.applyModifiers = objPass.apply_modifiers
                    self.useTriangulate = objPass.triangulate
                    self.exportIndividual = objPass.export_individual
                    self.exportAnim = objPass.export_animation
                    self.meshSmooth = self.GetNormals(group.CAPGrp.normals)

                    hasTriangulation = False
                    print("EXPORT TYPES:", self.export_types)

                    # Also set file path name
                    path = ""
                    filePath = ""
                    objectFilePath = ""
                    suffix = objPass.file_suffix
                    subDirectory = objPass.sub_directory

                    # Lets see if the root object can be exported...
                    expRoot = False
                    print("Checking Root Exportability...")
                    if self.RO != None and rootObjectInGroup is True:
                        print("Well we have a root...")
                        if len(activeTags) == 0:
                            expRoot = True
                        elif objPass.tags[self.ROType].use_tag is True:
                            expRoot = True
                        if exportDefault.filter_render == True and self.RO.hide_render == True:
                            expRoot = False

                    print("expRoot:", expRoot)


                    #/////////////////// - FILE NAME - /////////////////////////////////////////////////
                    path = self.CalculateFilePath(context, group.CAPGrp.location_default, objectName, subDirectory)

                    if path.find("WARNING") == 0:
                        path = path.replace("WARNING: ", "")
                        self.report({'WARNING'}, path)
                        self.RestoreScene(context)
                        return {'CANCELLED'}

                    print("Path created...", path)


                    #/////////////////// - FIND OBJECTS - /////////////////////////////////////////////////
                    # First we have to find all objects in the group that are of type MESHHH
                    # If auto-assignment is on, use the names to filter into lists, otherwise forget it.

                    print(">>>> Collecting Objects <<<<")

                    # If we have any active tags in use, export only by filtering them
                    if len(activeTags) > 0:
                        print("Using tags to sort objects...")
                        for tag in activeTags:
                            print("Current tag...", tag.name)
                            list = []

                            for item in group.objects:
                                print("Found item...", item.name)
                                checkItem = CompareObjectWithTag(context, item, tag)

                                if checkItem == True:
                                    if item.name != self.ROName:
                                        print(item.hide_render)

                                        if exportDefault.filter_render == False or (exportDefault.filter_render == True and item.hide_render == False):
                                            print("ITEM FOUND: ", item.name)
                                            list.append(item)
                                            objectList.append(item)

                                            if tag.x_ue4_collision_naming is True:
                                                print("SUPER SECRET REPLACE NAME FUNCTION USED!", item.name)
                                                renameObjectList.append(item)
                                                renameNameList.append(item.name)

                                                item.name = item.name.replace(tag.name_filter, "")
                                                item.name = "UCX_" + item.name + exportDefault.tags[1].name_filter

                                                print("Name replaced...", item.name)

                            taggedList.append(list)
                            print("-"*10)

                    # If not, export everything
                    else:
                        print("No tags found, processing objects...")
                        for item in group.objects:
                            if item.name != self.ROName:
                                if exportDefault.filter_render == False:
                                    print("ITEM FOUND: ", item.name)
                                    objectList.append(item)
                                elif exportDefault.filter_render == True and item.hide_render == False:
                                    print("ITEM FOUND: ", item.name)
                                    objectList.append(item)

                    print("Object List...", objectList)


                    # /////////// - OBJECT MOVEMENT - ///////////////////////////////////////////////////
                    # ///////////////////////////////////////////////////////////////////////////////////
                    movedObjects = []
                    movedObjects += objectList
                    sceneOrigin = None

                    # If we have a usable root object, use that as the origin point
                    if self.RO != None:
                        movedObjects.append(self.RO)
                        self.StartSceneMovement(context, self.RO, movedObjects, RORot)

                    # If not, create one now, and get rid of it later
                    else:
                        bpy.ops.view3d.snap_cursor_to_center()
                        bpy.ops.object.select_all(action='DESELECT')
                        bpy.ops.object.empty_add(type='PLAIN_AXES')
                        sceneOrigin = bpy.context.scene.objects.active
                        self.StartSceneMovement(context, sceneOrigin, movedObjects, RORot)


                    # /////////// - MODIFIERS - //////////////////////////////////////////////
                    # ////////////////////////////////////////////////////////////////////////
                    print(">>> Triangulating Objects <<<")
                    triangulateList = []
                    triangulateList += objectList

                    if expRoot is True:
                        triangulateList.append(self.RO)

                    if self.useTriangulate is True and self.applyModifiers is True:
                         self.AddTriangulate(triangulateList)

                    # /////////// - EXPORT - ///////////////////////////////////////////////////
                    # //////////////////////////////////////////////////////////////////////////
                    print(">>>> Exporting Objects <<<<")
                    bpy.ops.object.select_all(action='DESELECT')

                    canExport = True
                    if self.RO != None:
                        print("Root Location...", self.RO.location)

                    if len(objectList) == 0 and expRoot is False:
                        print("No objects found in pass, stopping export...")
                        canExport = False


                    elif canExport is True:
                        finalExportList = []
                        finalExportList += objectList
                        print("Final Export List:", finalExportList)

                        if expRoot is True:
                            finalExportList.append(self.RO)

                        if len(finalExportList) > 0:
                            if self.exportIndividual is True:
                                self.PrepareExportIndividual(context, finalExportList, path, suffix)

                            else:
                                self.PrepareExportCombined(finalExportList, path, group.name, suffix)

                    bpy.ops.object.select_all(action='DESELECT')

                    # /////////// - DELETE/RESTORE - //////////////////////////////////////////
                    # /////////////////////////////////////////////////////////////////////////
                    # Restore names
                    i = 0
                    for item in renameObjectList:
                        item.name = renameNameList[i]
                        i += 1

                    # Remove any triangulation modifiers
                    if self.useTriangulate is True and self.applyModifiers is True:
                         self.RemoveTriangulate(triangulateList)

                    # Move objects back
                    if self.RO != None:
                        self.FinishSceneMovement(context, self.RO, movedObjects, ROLoc, RORot)
                    else:
                        self.FinishSceneMovement(context, sceneOrigin, movedObjects, ROLoc, RORot)
                        DeleteObject(sceneOrigin)

                    print(">>> Pass Complete <<<")

                if len(exportDefault.passes) > 0:
                    self.exportedGroups += 1
                    self.exportCount += 1
                    context.window_manager.progress_update(self.exportCount)

                    print(">>> Group Export Complete <<<")


        self.RestoreScene(context)
        context.window_manager.progress_end()

        textGroupSingle = " group"
        textGroupMultiple = " groups"

        output = "Finished processing "

        if self.exportedObjects > 1:
            output += str(self.exportedObjects) + " objects"
        elif self.exportedObjects == 1:
            output += str(self.exportedObjects) + " object"

        if self.exportedObjects > 0 and self.exportedGroups > 0:
            output += " and "
        if self.exportedGroups > 1:
            output += str(self.exportedGroups) + " groups"
        elif self.exportedGroups == 1:
            output += str(self.exportedGroups) + " group"

        output += ".  "
        output += "Total of "

        if self.exportedFiles > 1:
            output += str(self.exportedFiles) + " files exported."
        elif self.exportedFiles == 1:
            output += str(self.exportedFiles) + " file."

        # Output a nice report
        if self.exportedObjects == 0 and self.exportedGroups == 0:
            self.report({'WARNING'}, 'No objects were exported.  Ensure you have objects tagges for export, and passes in your export presets.')

        else:
            self.report({'INFO'}, output)


        return {'FINISHED'}
