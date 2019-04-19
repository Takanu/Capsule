
import bpy, bmesh, os, platform, sys
from mathutils import Vector
from math import pi, radians, degrees
from bpy.types import Operator
from bpy.props import IntProperty, BoolProperty, FloatProperty, EnumProperty, PointerProperty, StringProperty, CollectionProperty


from .tk_utils import collections as collection_utils
from .tk_utils import select as select_utils
from .tk_utils import locations as loc_utils
from .tk_utils import object_ops
from .tk_utils import object_transform
from . import tag_ops
from .export_utils import ReplaceSystemChar, CheckSystemChar, CheckAnimation, AddTriangulate, RemoveTriangulate

class CAPSULE_OT_ExportAssets(Operator):
    """Exports all objects and collections in the scene that are marked for export."""

    bl_idname = "scene.cap_export"
    bl_label = "Export"

    def PrepareExportIndividual(self, context, targets, path, suffix):
        """
        Exports a selection of objects, saving each object into it's own file.
        """

        print(">>> Individual Pass <<<")
        for item in targets:
            print("-"*70)
            print("Exporting...... ", item.name)
            individualFilePath = path + item.name + suffix
            print("Final File Path.", individualFilePath)

            # For the time being, manually move the object back and forth to
            # the world origin point.
            tempLoc = loc_utils.FindWorldSpaceObjectLocation(item, context)

            # FIXME: Doesn't distinguish between "Use Scene Origin".

            # moves each target to the centre individually, even though these objects have
            # already been moved before collectively.
            object_transform.MoveObject(item, context, (0.0, 0.0, 0.0))

            bpy.ops.object.select_all(action='DESELECT')
            select_utils.FocusObject(item)


            # based on the export location, send it to the right place
            if self.exportPreset.format_type == 'FBX':
                self.exportPreset.data_fbx.export(self.exportPreset, self.exportPass, individualFilePath)

            elif self.exportPreset.format_type == 'OBJ':
                self.exportPreset.data_obj.export(self.exportPreset, self.exportPass, individualFilePath)

            elif self.exportPreset.format_type == 'GLTF':
                self.exportPreset.data_gltf.export(context, self.exportPreset, self.exportPass, individualFilePath)
            
            elif self.exportPreset.format_type == 'Alembic':
                self.exportPreset.data_abc.export(context, self.exportPreset, self.exportPass, individualFilePath)

            elif self.exportPreset.format_type == 'Collada':
                self.exportPreset.data_dae.export(self.exportPreset, self.exportPass, individualFilePath)

            elif self.exportPreset.format_type == 'STL':
                self.exportPreset.data_stl.export(context, self.exportPreset, self.exportPass, individualFilePath)


            # tick up the exports and move the object back.
            self.exportedFiles += 1

            object_transform.MoveObject(item, context, tempLoc)


    def PrepareExportCombined(self, context, targets, path, exportName, suffix):
        """
        Exports a selection of objects into a single file.
        """

        print(">>> Exporting Combined Pass <<<")
        print("Checking export preferences...")

        bpy.ops.object.select_all(action='DESELECT')

        for item in targets:
            print("Exporting: ", item.name)
            print(item.name, "has export set to", item.CAPObj.enable_export)
            select_utils.SelectObject(item)

        print(path)
        print(exportName)
        print(suffix)

        objectFilePath = path + exportName + suffix
        print("Final File Path.", objectFilePath)


        # based on the export location, send it to the right place
        if self.exportPreset.format_type == 'FBX':
            self.exportPreset.data_fbx.export(self.exportPreset, self.exportPass, objectFilePath)

        elif self.exportPreset.format_type == 'OBJ':
            self.exportPreset.data_obj.export(self.exportPreset, self.exportPass, objectFilePath)

        elif self.exportPreset.format_type == 'GLTF':
            self.exportPreset.data_gltf.export(context, self.exportPreset, self.exportPass, path, exportName + suffix)

        elif self.exportPreset.format_type == 'Alembic':
            self.exportPreset.data_abc.export(context, self.exportPreset, self.exportPass, objectFilePath)

        elif self.exportPreset.format_type == 'Collada':
            self.exportPreset.data_dae.export(self.exportPreset, self.exportPass, objectFilePath)
        
        elif self.exportPreset.format_type == 'STL':
            self.exportPreset.data_stl.export(context, self.exportPreset, self.exportPass, objectFilePath)
        
       

        self.exportedFiles += 1


    def GetFilePath(self, context, locationEnum, fileName):
        """
        Attempts to fetch and retrieve the selected file path for 'CalculateFilePath'
        """

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

    def CalculateFilePath(self, context, locationDefault, object_name, subDirectory):
        """
        Attempts to create a file path based on the given location default and export settings.
        """

        print("Obtaining File...")
        print("File Enumerator = ", locationDefault)

        path = self.GetFilePath(context, locationDefault, object_name)

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
                    blendName = ReplaceSystemChar(context, blendName)

                newPath = path + blendName + slash

            if self.use_sub_directory is True:
                if self.replaceInvalidChars is True:
                    object_name = ReplaceSystemChar(context, object_name)
                newPath = newPath + object_name + slash

            if subDirectory.replace(" ", "") != "":
                if self.replaceInvalidChars is True:
                    subDirectory = ReplaceSystemChar(context, subDirectory)
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

    def GetExportInfo(self, exportPreset):
        """
        Builds a list of export information 
        """

        # Stores a whole load of export-related settings for re-use throughout
        # the operator

        self.use_blend_directory = exportPreset.use_blend_directory
        self.use_sub_directory = exportPreset.use_sub_directory
        #self.bundle_textures = self.exportPreset.bundle_textures
        self.filter_render = exportPreset.filter_render
        self.reset_rotation = exportPreset.reset_rotation
        #self.export_types = self.exportPreset.export_types

        # FIXME: Take note of this!

        #self.bundle_textures = self.exportPreset.bundle_textures
        #self.batch_mode = 'AUTO'
        #if self.bundle_textures is True:
        #    self.batch_mode = 'COPY'

    def SetupScene(self, context):
        """
        Stores important scene information while also preparing it for the export process.
        States stored here will be restored with the 'RestoreScene' function.
        """

        self.active = None
        self.selected = []

        # If the current context isn't the 3D View, we need to change that before anything else.
        self.previous_area_type = bpy.context.area.type
        if self.previous_area_type != 'VIEW_3D':
            bpy.context.area.type = 'VIEW_3D'

        # We also need to store current 3D View selections.
        if context.active_object is not None:
            for sel in context.selected_objects:
                if sel.name != context.active_object.name:
                    self.selected.append(sel)
        else:
            for sel in context.selected_objects:
                self.selected.append(sel)

        self.active = context.active_object

        # Save the current cursor location
        cursor_loc = bpy.data.scenes[bpy.context.scene.name].cursor.location
        self.cursorLocation = [cursor_loc[0], cursor_loc[1], cursor_loc[2]]

        # Keep a record of the current object mode
        self.view_mode = bpy.context.mode
        bpy.ops.object.mode_set(mode='OBJECT')


        # not sure if I need this anymore with view layers, test and report back.
        # ======================
        # Ensure all layers are visible

        # self.layersBackup = []
        # for layer in context.scene.layers:
        #     layerVisibility = layer
        #     self.layersBackup.append(layerVisibility)

        # context.scene.layers = (True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True)

        # ======================

        # Record object visibility
        self.hiddenList = []
        self.selectList = []
        self.hiddenObjectList = []

        for item in context.scene.objects:
            self.hiddenObjectList.append(item)
            isHidden = item.hide_viewport
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
                mode = object_ops.SwitchObjectMode('OBJECT', item)
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
                    trueLocation = loc_utils.FindWorldSpaceObjectLocation(item, context)
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
            entry['constraint_location'] = loc_utils.FindWorldSpaceObjectLocation(item, context)
            print("NEW CONSTRAINT LOCATION", item.name, entry['constraint_location'])

        # Now all problematic constraints have been turned off, we can safely move
        # objects to their initial positions
        for entry in self.constraintObjects:
            item = context.scene.objects[entry['object_name']]
            print("Moving Object...", item.name, entry['true_location'])
            object_transform.MoveObject(item, context, entry['true_location'])
            print("New Object Location = ", item.location)
            print("-"*20)


        # Now we can unhide and deselect everything
        bpy.ops.object.hide_view_clear()
        bpy.ops.object.select_all(action='DESELECT')

    def RestoreScene(self, context):
        """
        Restores all scene information preserved with the 'SetupScene' function.
        """

        # Restore constraint object positions
        for entry in self.constraintObjects:
            item = context.scene.objects[entry['object_name']]
            print(entry)
            print("Moving Object...", item.name, entry['constraint_location'])
            object_transform.MoveObject(item, context, entry['constraint_location'])
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

            item.hide_viewport = hide
            item.hide_select = hide_select

        # Not sure if I need this anymore with view layers.  Test and report back.
        # ======================
        # # Turn off all other layers
        # i = 0
        # while i < 20:
        #     context.scene.layers[i] = self.layersBackup[i]
        #     i += 1
        

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
            mode = object_ops.SwitchObjectMode(entry['mode'], bpy.data.objects[entry['object_name']])

        # Re-select the objects previously selected
        if self.active is not None:
            select_utils.FocusObject(self.active)

        for sel in self.selected:
            select_utils.SelectObject(sel)

        if self.active is None and len(self.selected) == 0:
            bpy.ops.object.select_all(action='DESELECT')

        # Restore the 3D view mode
        bpy.ops.object.mode_set(mode=self.view_mode)

        # Restore the 3D cursor
        bpy.data.scenes[bpy.context.scene.name].cursor.location = self.cursorLocation

        # Restore the panel type if necessary
        if self.previous_area_type != 'VIEW_3D':
            bpy.context.area.type = self.previous_area_type

        print("Rawr")

    def StartSceneMovement(self, context, target, targetObjects, targetRot):
        """
        Moves the focus of the export to the desired location, performing any preparation work as needed.
        """

        # FIXME: WHY IS THIS HERE?

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

        # was removed since 1.01 due to unknown bugs and issues... *spooky*

        # If the user wanted to reset the rotation, time to add more
        # annoying levels of complexity to the mix and reset the rotation!
        #if self.reset_rotation is True:
            #print("Reset Rotation active, resetting rotations!")
            #reverseRotation = (-targetRot[0], -targetRot[1], -targetRot[2])
            #RotateAllSafe(target, context, reverseRotation, False)

        # If the user wanted unity, time to stomp on the rotation
        # only the objects being exported should be applied

        # might be fixed in 2.79, remove for now.

        # if self.x_unity_rotation_fix is True:

        #     print("Unity rotation fix active!")
        #     object_transform.RotateAllSafe(target, context, (radians(-90), 0, 0), True)
        #     bpy.ops.object.select_all(action='DESELECT')

        #     for item in targetObjects:
        #         SelectObject(item)
        #         ActivateObject(item)

        #     bpy.ops.object.transform_apply(
        #         location=False,
        #         rotation=True,
        #         scale=False
        #         )
        #     RotateAllSafe(target, context, (radians(90), 0, 0), True)

        if self.use_scene_origin is False:
            print("Moving scene...")
            object_transform.MoveAll(target, context, [0.0, 0.0, 0.0])

    def FinishSceneMovement(self, context, target, targetObjects, targetLoc, targetRot):
        """
        Moves the focus of the export back from the desired location, after the export is complete.
        """

        # was removed since 1.01 due to unknown bugs and issues... *spooky*
        # if self.reset_rotation is True:
        #     object_transform.RotateAllSafe(self.root_object, context, targetRot, True)

        if self.use_scene_origin is False:
            object_transform.MoveAll(self.root_object, context, targetLoc)

        # since Blender 2.79 + Unity 2017.3, this is no longer needed.
        # if self.exportPreset.format_type == 'FBX':
        #     if self.exportPreset.data_fbx.x_unity_rotation_fix is True:
        #         bpy.ops.object.select_all(action='DESELECT')

        #         for item in targetObjects:
        #             select_utils.SelectObject(item)
        #             select_utils.ActivateObject(item)
        #         bpy.ops.object.transform_apply(
        #             location=False,
        #             rotation=True,
        #             scale=False
        #             )

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
        """
        Handles armature constraints, turning them off and re-positioning all bones to ensure they are in their
        original positions, ready to be moved by Capsule.
        """

        # This process may fail, so if the user doesn't want us to process the armature constraints then stop right here.
        if self.exportPreset.preserve_armature_constraints is True:
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
                            trueLocation = loc_utils.FindWorldSpaceBoneLocation(item, context, bone)
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
                    entry['constraint_location'] = loc_utils.FindWorldSpaceBoneLocation(item, context, bone)
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
                    object_transform.MoveBone(item, bone, context, entry['true_location'])
                    #print("New Bone Location = ", bone.location)

        print("-"*40)
        print("-"*40)

    def FinishMovement(self, context):
        """
        Restores any armature constraint changes that were made to prepare the scene for export.
        """

        if self.exportPreset.preserve_armature_constraints is True:
            return

        # Restore constraint object positions
        for entry in self.armatureConstraintObjects:
            item = context.scene.objects[entry['object_name']]
            for bone in item.pose.bones:
                if bone.name == entry['bone_name']:
                    #print("Moving Bone...", item.name, bone.name)
                    object_transform.MoveBone(item, bone, context, entry['constraint_location'])
                    #print("New Bone Location = ", bone.location)

        # Restore Constraint Defaults
        for entry in self.armatureConstraintList:
            item = bpy.data.objects[entry['object_name']]
            for bone in item.pose.bones:
                if bone.name == entry['bone_name']:
                    index = entry['index']
                    bone.constraints[index].mute = entry['enabled']
                    bone.constraints[index].influence = entry['influence']

    def CheckForErrors(self, context):
        # Ensures that the scene is setup with correct settings, before proceeding
        # with the export.

        preferences = context.preferences
        addon_prefs = preferences.addons[__package__].preferences
        exp = bpy.data.objects[addon_prefs.default_datablock].CAPExp

        # Check all active file presets for valid directory names
        # These lists will be analysed later
        nameCheck = []
        gltfRequired = False

        for export in exp.file_presets:
            if export.use_blend_directory is True:
                blendName = bpy.path.basename(bpy.context.blend_data.filepath)
                nameCheck.append([" Blend Name", blendName, " Preset", export.name])
            for ePass in export.passes:
                if ePass.sub_directory != "":
                    nameCheck.append([" Pass Folder", ePass.sub_directory, " Preset", export.name])
                if ePass.file_suffix != "":
                    nameCheck.append([" File Suffix", ePass.file_suffix, " Preset", export.name])

            if export.format_type == 'GLTF':
                gltfRequired = True

        print("names found...", nameCheck)

        # Checks for any easily-preventable errors
        for object in context.scene.objects:
            if object.CAPObj.enable_export is True:

                # Check Export Key
                expKey = int(object.CAPObj.export_default) - 1
                if expKey == -1:
                    statement = "The selected object " + object.name + " has no export default selected.  Please define!"
                    select_utils.FocusObject(object)
                    return statement

                # Check Export Sub-Directory
                export = exp.file_presets[expKey]
                if export.use_sub_directory is True:
                    objName = object.name
                    nameCheck.append([" Object Name", objName, " Preset", export.name])

                # Check Location Default
                if int(object.CAPObj.location_default) == 0:
                    statement =  "The selected object " + object.name + " has no location preset defined, please define one!"
                    select_utils.FocusObject(object)
                    return statement

                self.exportCount += 1


        # If we're using Unity export options, ensure that every object mesh has a single user

        # Support for Unity 5 was removed since 2017.3 + Blender 2.79 fixes those problems.
        # if export.format_type == 'FBX' and export.data_fbx.x_unity_rotation_fix is True:
        #     for item in context.scene.objects:
        #         data = item.data
        #         if data is not None:
        #             print(data.users)
        #             if data.users > 1:
        #                 select_utils.FocusObject(item)
        #                 statement = "Sorry, but currently, this Unity Export Preset requires that all scene objects be single-user only.  Please ensure all objects have only one user, before using it."
        #                 return statement


        # Check all scene collections for potential errors
        for collection in collection_utils.GetSceneCollections(context.scene, True):
            if collection.CAPCol.enable_export is True:

                # Check Export Key
                expKey = int(collection.CAPCol.export_default) - 1
                if expKey == -1:
                    bpy.ops.object.select_all(action='DESELECT')
                    for item in collection.all_objects:
                        select_utils.SelectObject(item)
                    statement = "The selected collection " + collection.name + " has no export default selected.  Please define!"
                    return statement

                # Check Export Sub-Directory
                export = exp.file_presets[expKey]
                if export.use_sub_directory is True:
                    name = collection.name
                    nameCheck.append([" Collection Name", name, " Preset", export.name])

                # Check Export Location
                if int(collection.CAPCol.location_default) == 0:
                    bpy.ops.object.select_all(action='DESELECT')
                    for item in collection.all_objects:
                        select_utils.SelectObject(item)
                    statement =  "The selected collection " + collection.name + " has no location preset defined, please define one!"
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

    ###############################################################
    # EXECUTE
    ###############################################################
    def execute(self, context):
        scn = context.scene.CAPScn
        preferences = context.preferences
        addon_prefs = preferences.addons[__package__].preferences
        exp = None

        # For the new pie menu, we need to see if any data exists before continuing
        try:
            exp = bpy.data.objects[addon_prefs.default_datablock].CAPExp
        except KeyError:
            self.report({'WARNING'}, "No Capsule Data for this blend file exists.  Please create it using the Toolshelf or Addon Preferences menu.")
            return {'FINISHED'}

        # Now the checks over, time to assign some export information
        self.exportInfo = bpy.data.objects[addon_prefs.default_datablock].CAPExp
        self.replaceInvalidChars = addon_prefs.substitute_directories

        # Set export counts here just in case
        self.exportCount = 0
        self.exportedObjects = 0
        self.exportedCollections = 0
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
        
        # 2.80 - Commenting out until I fix the rest
        # context.window_manager.progress_begin(0, self.exportCount)
        


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
                    select_utils.FocusObject(object)
                    self.report({'WARNING'}, statement)
                    self.RestoreScene(context)
                    return {'FINISHED'}

                # Get the export default and send it to a function to create additional instance properties
                self.exportPreset = self.exportInfo.file_presets[expKey]
                self.GetExportInfo(self.exportPreset)

                # Get the root object and set some more variables!
                self.root_object = object
                self.root_object_type = tag_ops.IdentifyObjectTag(context, self.root_object, self.exportPreset)
                self.use_scene_origin = self.root_object.CAPObj.use_scene_origin

                # FIXME: Is this needed anymore?
                # If they asked us not preserve armature constraints, we can
                # do our jerb and ensure they don't screw things up beyond this code
                # Prepares the object for movement, will only work if Preserve Armature Constraints is false.
                self.SetupMovement(context)

                # Need to get the movement location.  If the user wants to use the scene origin though,
                # just make it 0
                root_object_location = [0.0, 0.0, 0.0]
                root_object_rotation = [0.0, 0.0, 0.0]

                if self.use_scene_origin is False:

                    tempROL = loc_utils.FindWorldSpaceObjectLocation(self.root_object, context)
                    root_object_location = [tempROL[0], 
                                            tempROL[1], 
                                            tempROL[2]]
                    root_object_rotation = [self.root_object.rotation_euler[0], 
                                            self.root_object.rotation_euler[1], 
                                            self.root_object.rotation_euler[2]]


                # Get the object's base name
                object_name = ""

                if self.root_object_type != -1:
                    object_name = tag_ops.RemoveObjectTag(context, self.root_object, self.exportPreset)
                else:
                    object_name = self.root_object.name


                ###############################################################
                # PASSES
                ###############################################################

                for object_pass in self.exportPreset.passes:

                    self.exportPass = object_pass

                    # If the pass isn't enabled, skip it
                    if object_pass.enable is False:
                        continue

                    print("-"*109)
                    print("NEW PASS", "-"*100)
                    print("-"*109)
                    print("Export pass", object_pass.name, "being used on object", object.name)

                    # Obtain some pass-specific preferences
                    self.applyModifiers = object_pass.apply_modifiers
                    self.useTriangulate = object_pass.triangulate
                    self.exportIndividual = object_pass.export_individual
                    self.objectUseTags = object_pass.use_tags_on_objects
                    self.exportAnim = object_pass.export_animation

                    activeTags = []
                    i = 0

                    # If the user wishes object exports to use tags, we need to
                    # create a list for every tag in use
                    if self.objectUseTags is True:
                        print("Processing tags...")
                        for passTag in object_pass.tags:
                            if passTag.use_tag is True:
                                print("Active Tag Found: ", passTag.name)
                                activeTags.append(self.exportPreset.tags[i])

                            i += 1

                    # Collect information on path names for later

                    path = ""                                    # Path given from the location default
                    fileName = ""                                # File name for the object (without tag suffixes)
                    suffix = object_pass.file_suffix             # Additional file name suffix
                    subDirectory = object_pass.sub_directory     # Whether a sub-directory needs to be created


                    # Lists for the renaming feature
                    renameNameList = []
                    renameObjectList = []


                    # Lets see if the root object can be exported...
                    expRoot = False

                    if self.root_object_type == -1:
                        if len(activeTags) == 0:
                            expRoot = True
                    elif len(activeTags) == 0:
                        expRoot = True
                    elif object_pass.tags[self.root_object_type].use_tag is True or (self.exportIndividual is True and self.objectUseTags is True):
                        expRoot = True

                    if self.exportPreset.filter_render is True and self.root_object.hide_render is True:
                        expRoot = False

                    print("Export Root = ", expRoot)



                    #/////////////////// - FILE NAME - /////////////////////////////////////////////////
                    path = self.CalculateFilePath(context, self.root_object.CAPObj.location_default, object_name, subDirectory)

                    # If while calculating a file path a warning was found, return early.
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
                        results = object_ops.FindObjectsWithName(context, object_name)

                        while len(results) != 0:
                            item = results.pop()

                            if item.name != self.root_object.name:
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

                                    if tag_ops.CompareObjectWithTag(context, item, tag) is True:
                                        results.append(item)

                                        # If the active tag has the ability to replace names, do it here.
                                        if self.self.exportPreset.format_type == 'FBX':
                                            if tag.data_fbx.x_ue4_collision_naming is True and self.exportIndividual is False:
                                                print("SUPER SECRET REPLACE NAME FUNCTION USED!")
                                                renameObjectList.append(item)
                                                renameNameList.append(item.name)

                                                item.name = item.name.replace(tag.name_filter, "")
                                                item.name = "UCX_" + item.name + self.exportPreset.tags[1].name_filter

                                                print("Name replaced...", item.name)

                            objectList.clear()

                            for item in results:
                                objectList.append(item)

                        # If Filter by Rendering is on, we need to check our results against that
                        if self.exportPreset.filter_render is True:
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


                    # /////////// - OBJECT MOVEMENT PREPARATION - /////////////////
                    # /////////////////////////////////////////////////
                    movedObjects = []
                    movedObjects += objectList
                    movedObjects.append(self.root_object)
                    sceneOrigin = None

                    if self.use_scene_origin is False:
                        self.StartSceneMovement(context, self.root_object, movedObjects, root_object_rotation)

                    else:
                        bpy.ops.view3d.snap_cursor_to_center()
                        bpy.ops.object.select_all(action='DESELECT')
                        bpy.ops.object.empty_add(type='PLAIN_AXES')
                        sceneOrigin = bpy.context.view_layer.objects.active
                        self.StartSceneMovement(context, sceneOrigin, movedObjects, root_object_rotation)


                    # /////////// - MODIFIERS - ///////////////////////
                    # /////////////////////////////////////////////////
                    print(">>> Triangulating Objects <<<")
                    triangulateList = []
                    triangulateList += objectList

                    if expRoot is True:
                        triangulateList.append(self.root_object)

                    if self.useTriangulate is True and self.applyModifiers is True:
                         AddTriangulate(triangulateList)


                    # //////////// - EXPORT PROCESS - ///////////////////////////////////////////
                    # A separate FBX export function call for every corner case isnt actually necessary
                    finalExportList = []
                    finalExportList += objectList

                    if expRoot is True:
                        print("expRoot = ", expRoot)
                        finalExportList.append(self.root_object)

                    if len(finalExportList) > 0:

                        if self.exportIndividual is True:
                            self.PrepareExportIndividual(context, finalExportList, path, suffix)

                        else:
                            self.PrepareExportCombined(context, finalExportList, path, object_name, suffix)


                    # /////////// - DELETE/RESTORE - ///////////////////
                    # //////////////////////////////////////////////////
                    # Restore names
                    i = 0
                    for item in renameObjectList:
                        item.name = renameNameList[i]
                        i += 1

                    # Remove any triangulation modifiers
                    if self.useTriangulate is True and self.applyModifiers is True:
                         RemoveTriangulate(triangulateList)

                    # Reverse movement and rotation
                    if self.use_scene_origin is False:
                        self.FinishSceneMovement(context, self.root_object, movedObjects, root_object_location, root_object_rotation)
                    else:
                        self.FinishSceneMovement(context, sceneOrigin, movedObjects, root_object_location, root_object_rotation)
                        object_ops.DeleteObject(sceneOrigin)

                    print(">>> Pass Complete <<<")

                # Cleans up any armature constraint modification (only works if Preserve Armature Constraints is off)
                self.FinishMovement(context)

                # Count up exported objects
                if len(self.exportPreset.passes) > 0:
                    self.exportedObjects += 1
                    self.exportCount += 1
                    # context.window_manager.progress_update(self.exportCount)
                    print(">>> Object Export Complete <<<")


        ###############################################################
        # COLLECTION CYCLE
        ###############################################################
        # Now hold up, its collection time!
        for collection in collection_utils.GetSceneCollections(context.scene, True):
            if collection.CAPCol.enable_export is True:

                print("-"*79)
                print("NEW JOB", "-"*70)
                print("-"*79)
                print(collection.name)

                # Before we do anything, check that a root object exists
                self.root_object = None
                self.root_object_name = ""
                self.root_object_type = 0
                self.use_scene_origin = False
                rootObjectInCollection = False

                # Find the root object in a collection, if thats where it's located
                for item in collection.all_objects:
                    if item.name == collection.CAPCol.root_object:
                        self.root_object = item
                        self.root_object_name = item.name
                        rootObjectInCollection = True

                # Otherwise, find it elsewhere
                if rootObjectInCollection == False:
                    for item in context.scene.objects:
                        if item.name == collection.CAPCol.root_object:
                            self.root_object = item
                            self.root_object_name = item.name

                if self.root_object == None:
                    self.use_scene_origin = True
                    print("No root object is currently being used, proceed!")

                #Get the export default for the object
                expKey = int(collection.CAPCol.export_default) - 1

                if expKey == -1:
                    statement = "The collection " + collection.name + " has no export default selected.  Please define!"
                    self.report({'WARNING'}, statement)
                    self.RestoreScene(context)
                    return {'FINISHED'}

                # Collect hidden defaults to restore afterwards.
                object_name = collection.name

                self.exportPreset = self.exportInfo.file_presets[expKey]
                self.use_blend_directory = self.exportPreset.use_blend_directory
                self.use_sub_directory = self.exportPreset.use_sub_directory
                self.GetExportInfo(self.exportPreset)
                print("Using Export Default...", self.exportPreset.name, ".  Export Key", expKey)


                # Identify what tag the root object has
                if self.root_object != None:
                    self.root_object_type = tag_ops.IdentifyObjectTag(context, self.root_object, self.exportPreset)
                    print("Root type is...", self.root_object_type)

                # Get the root object location for later use
                root_object_location = [0.0, 0.0, 0.0]
                root_object_rotation = [0.0, 0.0, 0.0]

                if self.root_object != None:
                    tempROL = loc_utils.FindWorldSpaceObjectLocation(self.root_object, context)
                    root_object_location = [tempROL[0], tempROL[1], tempROL[2]]
                    root_object_rotation = [self.root_object.rotation_euler[0], self.root_object.rotation_euler[1], self.root_object.rotation_euler[2]]

                #/////////////////// - PASSES - /////////////////////////////////////////////////
                for object_pass in self.exportPreset.passes:

                    self.exportPass = object_pass

                    # If the pass isn't enabled, skip it
                    if object_pass.enable is False:
                        continue

                    print("-"*59)
                    print("NEW PASS", "-"*50)
                    print("-"*59)
                    print("Export pass", object_pass.name, "being used on the collection", collection.name)
                    print("Root object.....", self.root_object_name)

                    activeTags = []
                    taggedList = []
                    objectList = []

                    # Lists for the UE4 renaming feature
                    renameNameList = []
                    renameObjectList = []

                    # Create a list for every tag in use
                    i = 0
                    print("Processing tags...")
                    for passTag in object_pass.tags:
                        if passTag.use_tag is True:
                            print("Active Tag Found: ", passTag.name)
                            activeTags.append(self.exportPreset.tags[i])

                        i += 1

                    # Obtain some object-specific preferences
                    self.applyModifiers = object_pass.apply_modifiers
                    self.useTriangulate = object_pass.triangulate
                    self.exportIndividual = object_pass.export_individual
                    self.exportAnim = object_pass.export_animation

                    hasTriangulation = False
                    #print("EXPORT TYPES:", self.export_types)

                    # Also set file path name
                    path = ""
                    filePath = ""
                    objectFilePath = ""
                    suffix = object_pass.file_suffix
                    subDirectory = object_pass.sub_directory

                    # Lets see if the root object can be exported...
                    expRoot = False
                    print("Checking Root Exportability...")
                    if self.root_object != None and rootObjectInCollection is True:
                        print("Well we have a root...")
                        if len(activeTags) == 0:
                            expRoot = True
                        elif object_pass.tags[self.root_object_type].use_tag is True:
                            expRoot = True
                        if self.exportPreset.filter_render == True and self.root_object.hide_render == True:
                            expRoot = False

                    print("expRoot:", expRoot)


                    #/////////////////// - FILE NAME - /////////////////////////////////////////////////
                    path = self.CalculateFilePath(context, collection.CAPCol.location_default, object_name, subDirectory)

                    if path.find("WARNING") == 0:
                        path = path.replace("WARNING: ", "")
                        self.report({'WARNING'}, path)
                        self.RestoreScene(context)
                        return {'CANCELLED'}

                    print("Path created...", path)


                    #/////////////////// - FIND OBJECTS - /////////////////////////////////////////////////
                    # First we have to find all objects in the collection that are of type MESHHH
                    # If auto-assignment is on, use the names to filter into lists, otherwise forget it.

                    print(">>>> Collecting Objects <<<<")

                    # If we have any active tags in use, export only by filtering them
                    if len(activeTags) > 0:
                        print("Using tags to sort objects...")
                        for tag in activeTags:
                            print("Current tag...", tag.name)
                            list = []

                            for item in collection.all_objects:
                                print("Found item...", item.name)
                                checkItem = tag_ops.CompareObjectWithTag(context, item, tag)

                                if checkItem == True:
                                    if item.name != self.root_object_name:
                                        print(item.hide_render)

                                        if self.exportPreset.filter_render == False or (self.exportPreset.filter_render == True and item.hide_render == False):
                                            print("ITEM FOUND: ", item.name)
                                            list.append(item)
                                            objectList.append(item)

                                            # If the active tag has the ability to replace names, do it here.
                                            if self.self.exportPreset.format_type == 'FBX':
                                                if tag.data_fbx.x_ue4_collision_naming is True:
                                                    print("SUPER SECRET REPLACE NAME FUNCTION USED!", item.name)
                                                    renameObjectList.append(item)
                                                    renameNameList.append(item.name)

                                                    item.name = item.name.replace(tag.name_filter, "")
                                                    item.name = "UCX_" + item.name + self.exportPreset.tags[1].name_filter

                                                    print("Name replaced...", item.name)

                            taggedList.append(list)
                            print("-"*10)

                    # If not, export everything
                    else:
                        print("No tags found, processing objects...")
                        for item in collection.all_objects:
                            if item.name != self.root_object_name:
                                if self.exportPreset.filter_render == False:
                                    print("ITEM FOUND: ", item.name)
                                    objectList.append(item)
                                elif self.exportPreset.filter_render == True and item.hide_render == False:
                                    print("ITEM FOUND: ", item.name)
                                    objectList.append(item)

                    print("Object List...", objectList)


                    # /////////// - OBJECT MOVEMENT - ///////////////////////////////////////////////////
                    # ///////////////////////////////////////////////////////////////////////////////////
                    movedObjects = []
                    movedObjects += objectList
                    sceneOrigin = None

                    # If we have a usable root object, use that as the origin point
                    if self.root_object != None:
                        movedObjects.append(self.root_object)
                        self.StartSceneMovement(context, self.root_object, movedObjects, root_object_rotation)

                    # If not, create one now, and get rid of it later
                    else:
                        bpy.ops.view3d.snap_cursor_to_center()
                        bpy.ops.object.select_all(action='DESELECT')
                        bpy.ops.object.empty_add(type='PLAIN_AXES')
                        sceneOrigin = bpy.context.view_layer.objects.active
                        self.StartSceneMovement(context, sceneOrigin, movedObjects, root_object_rotation)


                    # /////////// - MODIFIERS - //////////////////////////////////////////////
                    # ////////////////////////////////////////////////////////////////////////
                    print(">>> Triangulating Objects <<<")
                    triangulateList = []
                    triangulateList += objectList

                    if expRoot is True:
                        triangulateList.append(self.root_object)

                    if self.useTriangulate is True and self.applyModifiers is True:
                         AddTriangulate(triangulateList)

                    # /////////// - EXPORT - ///////////////////////////////////////////////////
                    # //////////////////////////////////////////////////////////////////////////
                    print(">>>> Exporting Objects <<<<")
                    bpy.ops.object.select_all(action='DESELECT')

                    canExport = True
                    if self.root_object != None:
                        print("Root Location...", self.root_object.location)

                    if len(objectList) == 0 and expRoot is False:
                        print("No objects found in pass, stopping export...")
                        canExport = False


                    elif canExport is True:
                        finalExportList = []
                        finalExportList += objectList
                        print("Final Export List:", finalExportList)

                        if expRoot is True:
                            finalExportList.append(self.root_object)

                        if len(finalExportList) > 0:
                            if self.exportIndividual is True:
                                self.PrepareExportIndividual(context, finalExportList, path, suffix)

                            else:
                                self.PrepareExportCombined(context, finalExportList, path, collection.name, suffix)

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
                         RemoveTriangulate(triangulateList)

                    # Move objects back
                    if self.root_object != None:
                        self.FinishSceneMovement(context, self.root_object, movedObjects, root_object_location, root_object_rotation)
                    else:
                        self.FinishSceneMovement(context, sceneOrigin, movedObjects, root_object_location, root_object_rotation)
                        object_ops.DeleteObject(sceneOrigin)

                    print(">>> Pass Complete <<<")

                if len(self.exportPreset.passes) > 0:
                    self.exportedCollections += 1
                    self.exportCount += 1
                    # context.window_manager.progress_update(self.exportCount)

                    print(">>> Collection Export Complete <<<")


        self.RestoreScene(context)
        # context.window_manager.progress_end()

        # 2.80 BONUS TEST TIME
        bpy.context.area.type = 'VIEW_3D'

        textCollectionSingle = " collection"
        textCollectionPlural = " collections"

        output = "Finished processing "

        if self.exportedObjects > 1:
            output += str(self.exportedObjects) + " objects"
        elif self.exportedObjects == 1:
            output += str(self.exportedObjects) + " object"

        if self.exportedObjects > 0 and self.exportedCollections > 0:
            output += " and "
        if self.exportedCollections > 1:
            output += str(self.exportedCollections) + " collections"
        elif self.exportedCollections == 1:
            output += str(self.exportedCollections) + " collection"

        output += ".  "
        output += "Total of "

        if self.exportedFiles > 1:
            output += str(self.exportedFiles) + " files exported."
        elif self.exportedFiles == 1:
            output += str(self.exportedFiles) + " file."

        # Output a nice report
        if self.exportedObjects == 0 and self.exportedCollections == 0:
            self.report({'WARNING'}, 'No objects were exported.  Ensure you have objects tagged for export, and at least one pass in your export presets.')

        else:
            self.report({'INFO'}, output)


        return {'FINISHED'}

# ////////////////////// - CLASS REGISTRATION - ////////////////////////
# decided to do it all in __init__ instead, skipping for now.

# def register():
#     bpy.utils.register_class(CAPSULE_OT_ExportAssets)

# def unregister():
#     bpy.utils.unregister_class(CAPSULE_OT_ExportAssets)
