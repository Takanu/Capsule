import bpy, bmesh, os
from bpy.types import Operator
from bpy.props import IntProperty, BoolProperty, FloatProperty, EnumProperty, PointerProperty, StringProperty, CollectionProperty
from .definitions import SelectObject, FocusObject, ActivateObject, DuplicateObject, DuplicateObjects, DeleteObject, MoveObject, MoveObjects, MoveAll, CheckSuffix, CheckPrefix, CheckForTags, RemoveObjectTag, IdentifyObjectTag, CompareObjectWithTag, FindObjectWithTag, GetDependencies, AddParent, ClearParent, FindWorldSpaceObjectLocation
from mathutils import Vector

class CAP_Export_Assets(Operator):
    """Updates the origin point based on the option selected, for all selected objects"""

    bl_idname = "scene.cap_export"
    bl_label = "Export"

    def ExportFBX(self, filePath):

        print("Exporting", "*"*70)
        bpy.ops.export_scene.fbx(check_existing=False,
        filepath=filePath,
        filter_glob="*.fbx",
        version='BIN7400',
        use_selection=True,
        global_scale=self.globalScale,
        axis_forward=self.axisForward,
        axis_up=self.axisUp,
        bake_space_transform=self.bakeSpaceTransform,
        object_types=self.exportTypes,
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

    def PrepareExportIndividual(self, context, targets, path, suffix):
        print(">>> Individual Pass <<<")
        for item in targets:
            print("-"*70)
            print("Exporting...... ", item.name)
            individualFilePath = path + item.name + suffix + ".fbx"
            print("Final File Path.", individualFilePath)

            # For the time being, manually move the object back and forth to
            # the world origin point.
            tempLoc = Vector((0.0, 0.0, 0.0))
            tempLoc[0] = item.location[0]
            tempLoc[1] = item.location[1]
            tempLoc[2] = item.location[2]
            print("Moving location to centre...")
            MoveObject(item, context, (0.0, 0.0, 0.0))

            bpy.ops.object.select_all(action='DESELECT')
            FocusObject(item)

            self.ExportFBX(individualFilePath)

            print("Moving location back to root-orientated centre...")
            print("tempLoc - ", tempLoc)
            MoveObject(item, context, tempLoc)
            print("Location..........", item.location)
            print("tempLoc - ", tempLoc)

    def PrepareExportCombined(self, targets, path, exportName, suffix):
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

    def AddTriangulate(self, object):

        modType = {'TRIANGULATE'}

        for modifier in object.modifiers:
            #print("Looking for modifier...")
            if modifier.type in modType:
                #print("Already found triangulation.")
                return True

        FocusObject(object)
        bpy.ops.object.modifier_add(type='TRIANGULATE')

        for modifier in object.modifiers:
            if modifier.type in modType:
                #print("Triangulation Found")
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

    def GetFilePath(self, context, locationEnum, fileName):
        # Get the file extension.  If the index is incorrect (as in, the user didnt set the fucking path)
        scn = context.scene.CAPScn
        enumIndex = int(locationEnum)
        filePath = ""

        enumIndex -= 1

        defaultFilePath = scn.location_defaults[enumIndex].path
        print("Obtained location default: ", scn.location_defaults[enumIndex].path)

        if defaultFilePath == "":
            return {'2'}

        if defaultFilePath.find('//') != -1:
            return {'3'}

        filePath = defaultFilePath

        return filePath

    def CalculateFilePath(self, context, locationDefault, objectName, sub_directory, useBlendDirectory, useObjectDirectory):

        # Does the proper calculation and error handling for the file path, in conjunction with GetFilePath()
        print("Obtaining File...")
        print("File Enumerator = ", locationDefault)

        if int(locationDefault) == 0:
            return "WARNING: " + objectName + " has no location preset defined, please define one!"


        path = self.GetFilePath(context, locationDefault, objectName)

        if path == "":
            return "WARNING: Welp, something went wrong.  Contact Crocadillian! D:."

        if path == {'1'}:
            return "WARNING: " + objectName + " is not using a location preset.  Set it plzplzplz."

        if path == {'2'}:
            return "WARNING: " + objectName + " is using an empty location preset.  A file path is required to export."

        if path == {'3'}:
            return "WARNING: " + objectName + " is using a location preset with a relative file path name, please tick off the Relative Path option when choosing the file path."

        print("Current Path: ", path)

        # //////////// - FILE DIRECTORY - ///////////////////////////////////////////
        # Need to extract the information from the pass name to see
        # if a sub-directory needs creating in the location default
        if sub_directory != "" or useObjectDirectory is True or useBlendDirectory is True:
            newPath = ""

            if useBlendDirectory is True:
                print(bpy.data.filepath)
                pathSplit = bpy.data.filepath.rsplit("/")
                blendFile = pathSplit.pop()
                blendSplit = blendFile.rsplit(".")
                blendName = blendSplit[0]

                newPath = path + blendName + "/"

            if useObjectDirectory is True:
                newPath = newPath + objectName + "/"

            if sub_directory.replace(" ", "") != "":
                newPath = newPath + sub_directory + "/"

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

    def GetNormals(self, enum):

        if enum == '1':
            return 'EDGE'
        if enum == '2':
            return 'FACE'
        if enum == '3':
            return 'OFF'

    def GetExportInfo(self, exportDefault):

        self.exportTypes = exportDefault.export_types
        self.bundle_textures = exportDefault.bundle_textures
        self.batch_mode = 'AUTO'
        if self.bundle_textures is True:
            self.batch_mode = 'COPY'

        self.axisForward = exportDefault.axis_forward
        self.axisUp = exportDefault.axis_up
        self.globalScale = exportDefault.global_scale
        self.bakeSpaceTransform = exportDefault.bake_space_transform

        self.apply_unit_scale = exportDefault.apply_unit_scale
        self.loose_edges = exportDefault.loose_edges
        self.tangent_space = exportDefault.tangent_space

        self.use_armature_deform_only = exportDefault.use_armature_deform_only
        self.add_leaf_bones = exportDefault.add_leaf_bones
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

    def SetupScene(self, context):
        # Keep a record of the selected and active objects to restore later
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

        # Keep a record of the current object mode
        mode = bpy.context.mode
        bpy.ops.object.mode_set(mode='OBJECT')

        # Ensure all layers are visible
        self.layersBackup = []
        for layer in context.scene.layers:
            layerVisibility = layer
            self.layersBackup.append(layerVisibility)

        context.scene.layers = (True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True)

        # NOW FOR A ONCE AND FOR ALL OBJECT MOVEMENT FIX
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

        # For each object, find certain offending constraints, and turn them off for now
        self.constraintList = []

        con_types_target = {'COPY_LOCATION', 'COPY_TRANSFORMS'}

        for item in context.scene.objects:
            i = 0
            for constraint in item.constraints:
                if constraint.type in con_types_target:
                    copyLocation = Vector((0.0, 0.0, 0.0))
                    copyLocation[0] = item.location[0]

                    entry = {'object_name': item.name, 'index': i, 'enabled': constraint.mute, 'influence': constraint.influence}
                    self.constraintList.append(entry)

                    constraint.mute = True
                    constraint.influence = 0.0

                i += 1

        # If an object has locked Location/Rotation/Scale values, store them and turn it on
        self.translateList = []

        for item in context.scene.objects:
            if item.lock_location != (False, False, False) or item.lock_rotation != (False, False, False) or item.lock_scale != (False, False, False):
                entry = {'object_name': item.name, 'lock_location': item.lock_location, 'lock_rotation': item.lock_rotation, 'lock_scale': item.lock_scale}
                self.translateList.append(entry)

        for item in context.scene.objects:
            item.lock_location = (False, False, False)
            item.lock_rotation = (False, False, False)
            item.lock_scale = (False, False, False)

        # Now we can unhide and deselect everything
        bpy.ops.object.hide_view_clear()
        bpy.ops.object.select_all(action='DESELECT')
        print("Rawr")

    def RestoreScene(self, context):

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
        self.translateList = []

        while len(self.translateList) != 0:
            entry = self.translateList.pop()
            item = bpy.data.objects[entry['object_name']]
            item.lock_location = entry['lock_location']
            item.lock_rotation = entry['lock_location']
            item.lock_scale = entry['lock_location']

        # Re-select the objects previously selected
        if self.active is not None:
            FocusObject(self.active)

        for sel in self.selected:
            SelectObject(sel)

        if self.active is None and len(self.selected) == 0:
            bpy.ops.object.select_all(action='DESELECT')

        print("Rawr")

    def CheckForErrors(self, context):

        scn = context.scene.CAPScn

        # Checks for any easily-preventable errors
        for object in context.scene.objects:
            if object.CAPObj.enable_export is True:

                # Check Export Key
                expKey = int(object.CAPObj.export_default) - 1
                if expKey == -1:
                    statement = "The selected object " + object.name + " has no export default selected.  Please define!"
                    FocusObject(object)
                    return statement

                # Check Location Default
                if int(object.CAPObj.location_default) == 0:
                    statement =  "The selected object " + object.name + " has no location preset defined, please define one!"
                    FocusObject(object)
                    return statement

                self.exportCount += 1

        for group in bpy.data.groups:
            if group.CAPGrp.export_group is True:

                # Check Export Key
                expKey = int(group.CAPGrp.export_default) - 1
                if expKey == -1:
                    statement = "The group " + group.name + " has no export default selected.  Please define!"
                    return statement

                # Check Location Default
                if int(group.CAPGrp.location_default) == 0:
                    statement =  "The selected object " + group.name + " has no location preset defined, please define one!"
                    return statement

                self.exportCount += 1

        # Check Paths
        i = 0
        while i < len(scn.location_defaults):
            enumIndex = i
            filePath = ""
            enumIndex -= 1

            defaultFilePath = scn.location_defaults[enumIndex].path

            if defaultFilePath == "":
                statement = "The path for " + scn.location_defaults[enumIndex].name + " cannot be empty.  Please give the Location a valid file path."
                return statement

            if defaultFilePath.find('//') != -1:
                statement =  "The Location " + scn.location_defaults[enumIndex].name + " is using a location preset with a relative file path name, please tick off the Relative Path option when choosing the file path."
                return statement

            i += 1

        return None

    def CheckAnimation(self, context):
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

    def execute(self, context):
        print("Self = ")
        print(self)

        scn = context.scene.CAPScn
        user_preferences = context.user_preferences
        self.addon_prefs = user_preferences.addons[__package__].preferences

        self.exportCount = 0
        self.exportedObjects = 0
        self.exportedGroups = 0
        self.exportedPasses = 0

        # Check for stupid errors before continuing
        result = self.CheckForErrors(context)
        print("RAAAWR")
        print(result)
        if result is not None:
            print("RAAAWR")
            self.report({'WARNING'}, result)
            return {'FINISHED'}

        # Setup the scene
        self.SetupScene(context)

        context.window_manager.progress_begin(0, self.exportCount)

        # OBJECT CYCLE
        ###############################################################
        ###############################################################
        # Cycle through the available objects
        for object in context.scene.objects:
            if object.CAPObj.enable_export is True:

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


                exportDefault = self.addon_prefs.export_defaults[expKey]
                useBlendDirectory = exportDefault.use_blend_directory
                useObjectDirectory = exportDefault.use_sub_directory
                self.GetExportInfo(exportDefault)

                rootObject = object
                rootType = IdentifyObjectTag(context, rootObject, exportDefault)
                useSceneOrigin = rootObject.CAPObj.use_scene_origin

                print("Root Type is...", rootType)

                # Need to get the movement location.  If the user wants to use the scene origin though,
                # just make it 0
                rootObjectLocation = Vector((0.0, 0.0, 0.0))

                if useSceneOrigin is False:
                    tempROL = FindWorldSpaceObjectLocation(rootObject, context)
                    rootObjectLocation = Vector((0.0, 0.0, 0.0))
                    rootObjectLocation[0] = tempROL[0]
                    rootObjectLocation[1] = tempROL[1]
                    rootObjectLocation[2] = tempROL[2]

                # Collect hidden defaults to restore afterwards.
                objectName = ""

                # Lists for the UE4 renaming feature
                renameNameList = []
                renameObjectList = []

                # Get the object's base name
                if rootType != -1:
                    objectName = RemoveObjectTag(context, rootObject, exportDefault)
                    print("objectName =", objectName)
                else:
                    objectName = rootObject.name


                for objPass in exportDefault.passes:

                    print("-"*109)
                    print("NEW PASS", "-"*100)
                    print("-"*109)
                    print("Export pass", objPass.name, "being used on object", object.name)

                    # Obtain some pass-specific preferences
                    self.applyModifiers = objPass.apply_modifiers
                    useTriangulate = objPass.triangulate
                    exportIndividual = objPass.export_individual
                    objectUseTags = objPass.object_use_tags
                    self.exportAnim = False
                    self.meshSmooth = self.GetNormals(rootObject.CAPObj.normals)

                    activeTags = []
                    foundObjects = []
                    i = 0

                    if exportIndividual is True and objectUseTags is True:
                        for passTag in objPass.tags:
                            activeTags.append(exportDefault.tags[i])
                            i += 1

                    # Create a list for every tag in use
                    else:
                        print("Processing tags...")
                        for passTag in objPass.tags:
                            if passTag.use_tag is True:
                                print("Active Tag Found: ", passTag.name)
                                activeTags.append(exportDefault.tags[i])

                            i += 1

                    # Also set file path name
                    path = ""                                # Path given from the location default
                    fileName = ""                            # File name for the object (without tag suffixes)
                    suffix = objPass.file_suffix             # Additional file name suffix
                    sub_directory = objPass.sub_directory    # Whether a sub-directory needs to be created


                    # Lets see if the root object can be exported...
                    expRoot = False

                    if rootType == -1:
                        if len(activeTags) == 0:
                            expRoot = True
                    elif len(activeTags) == 0:
                        expRoot = True
                    if objPass.tags[rootType].use_tag is True or (exportIndividual is True and objectUseTags is True):
                        expRoot = True

                    if exportDefault.filter_render is True and rootObject.hide_render is True:
                        expRoot = False

                    print("Export Root = ", expRoot)


                    #/////////////////// - FILE NAME - /////////////////////////////////////////////////
                    path = self.CalculateFilePath(context, rootObject.CAPObj.location_default, objectName, sub_directory, useBlendDirectory, useObjectDirectory)

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

                    if len(activeTags) > 0:
                        print(">>>> Tags On, searching... <<<")

                        # For each tag, try to search for an object that matches the tag
                        for tag in activeTags:
                            if FindObjectWithTag(context, objectName, tag) is not None:
                                item = FindObjectWithTag(context, objectName, tag)

                                if item != None:
                                    if item.name != rootObject.name:
                                        if exportDefault.filter_render is False or (exportDefault.filter_render is True and item.hide_render is False):
                                            foundObjects.append(item)

                                            print("Tag", tag.name, "Found...", item.name)

                                            # If the active tag has the ability to replace names, do it here.
                                            if tag.x_ue4_collision_naming is True and exportIndividual is False:
                                                print("SUPER SECRET REPLACE NAME FUNCTION USED!")
                                                renameObjectList.append(item)
                                                renameNameList.append(item.name)

                                                item.name = item.name.replace(tag.name_filter, "")
                                                item.name = "UCX_" + item.name + exportDefault.tags[1].name_filter

                                                print("Name replaced...", item.name)


                    # Debug check for found objects
                    print("Checking found objects...")
                    for item in foundObjects:
                        print(item.name)


                    # /////////// - OBJECT MOVEMENT - ///////////////////////////////////////////////////
                    # ///////////////////////////////////////////////////////////////////////////////////
                    if useSceneOrigin is False:
                        MoveAll(rootObject, context, Vector((0.0, 0.0, 0.0)))

                    print(">>> Asset List Count...", len(foundObjects))

                    # /////////// - MODIFIERS - ///////////////////////////////////////////////////
                    # ////////////////////////////////////////////////////////////////////////////
                    print(">>> Triangulating Objects <<<")
                    triangulateList = []
                    triangulateList += foundObjects

                    if expRoot is True:
                        triangulateList.append(rootObject)

                    if useTriangulate is True and self.applyModifiers is True:
                        for item in triangulateList:
                            if item.type == 'MESH':
                                print("Triangulating Mesh...", item.name)
                                stm = item.CAPStm
                                hasTriangulation = False
                                hasTriangulation = self.AddTriangulate(item)
                                stm.has_triangulate = hasTriangulation


                    # //////////// - EXPORT PROCESS - ///////////////////////////////////////////
                    # A separate FBX export function call for every corner case isnt actually necessary
                    finalExportList = []
                    finalExportList += foundObjects

                    if expRoot is True:
                        print("expRoot = ", expRoot)
                        finalExportList.append(rootObject)

                    if len(finalExportList) > 0:
                        if exportIndividual is True:
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
                    if useTriangulate is True and self.applyModifiers is True:
                        for item in triangulateList:
                            if item.type == 'MESH':
                                if item.CAPStm.has_triangulate is False:
                                    print("Object has created triangulation, remove it.")
                                    self.RemoveTriangulate(item)

                    # Move objects back
                    if useSceneOrigin is False:
                        MoveAll(rootObject, context, rootObjectLocation)

                    self.exportedPasses += 1
                    print(">>> Pass Complete <<<")

                # Count up exported objects
                self.exportedObjects += 1
                self.exportCount += 1
                context.window_manager.progress_update(self.exportCount)
                print(">>> Object Export Complete <<<")

        # GROUP CYCLE
        ###############################################################
        ###############################################################
        # Now hold up, its group time!
        for group in bpy.data.groups:
            if group.CAPGrp.export_group is True:

                print("-"*79)
                print("NEW JOB", "-"*70)
                print("-"*79)
                print(group.name)

                # Before we do anything, check that a root object exists
                rootObject = None
                rootObjectName = ""
                rootType = 0
                rootObjectInGroup = False

                # Find the root object in a group, if thats where it's located
                for item in group.objects:
                    if item.name == group.CAPGrp.root_object:
                        rootObject = item
                        rootObjectName = item.name
                        rootObjectInGroup = True

                # Otherwise, find it elsewhere
                if rootObjectInGroup == False:
                    for item in context.scene.objects:
                        if item.name == group.CAPGrp.root_object:
                            rootObject = item
                            rootObjectName = item.name

                if rootObject == None:
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

                exportDefault = self.addon_prefs.export_defaults[expKey]
                useBlendDirectory = exportDefault.use_blend_directory
                useObjectDirectory = exportDefault.use_sub_directory
                self.GetExportInfo(exportDefault)
                print("Using Export Default...", exportDefault.name, ".  Export Key", expKey)


                # Identify what tag the root object has
                if rootObject != None:
                    rootType = IdentifyObjectTag(context, rootObject, exportDefault)
                    print("Root type is...", rootType)

                # Get the root object location for later use
                rootObjectLocation = Vector((0.0, 0.0, 0.0))
                if rootObject != None:
                    tempROL = FindWorldSpaceObjectLocation(rootObject, context)
                    rootObjectLocation[0] = tempROL[0]
                    rootObjectLocation[1] = tempROL[1]
                    rootObjectLocation[2] = tempROL[2]

                print("ROOT OBJECT LOCAATTTIIIOOOOON", rootObjectLocation)

                for objPass in exportDefault.passes:

                    print("-"*59)
                    print("NEW PASS", "-"*50)
                    print("-"*59)
                    print("Export pass", objPass.name, "being used on the group", group.name)
                    print("Root object.....", rootObjectName)

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
                    useTriangulate = objPass.triangulate
                    exportIndividual = objPass.export_individual
                    self.exportAnim = False
                    self.meshSmooth = self.GetNormals(group.CAPGrp.normals)

                    hasTriangulation = False
                    print("EXPORT TYPES:", self.exportTypes)

                    # Also set file path name
                    path = ""
                    filePath = ""
                    objectFilePath = ""
                    suffix = objPass.file_suffix
                    sub_directory = objPass.sub_directory

                    # Lets see if the root object can be exported...
                    expRoot = False
                    print("Checking Root Exportability...")
                    if rootObject != None and rootObjectInGroup is True:
                        print("Well we have a root...")
                        if len(activeTags) == 0:
                            expRoot = True
                        elif objPass.tags[rootType].use_tag is True:
                            expRoot = True
                        if exportDefault.filter_render == True and rootObject.hide_render == True:
                            expRoot = False

                    print("expRoot:", expRoot)


                    #/////////////////// - FILE NAME - /////////////////////////////////////////////////
                    path = self.CalculateFilePath(context, group.CAPGrp.location_default, objectName, sub_directory, useBlendDirectory, useObjectDirectory)

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
                                    if item.name != rootObjectName:
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
                            if item.name != rootObjectName:
                                if exportDefault.filter_render == False:
                                    print("ITEM FOUND: ", item.name)
                                    objectList.append(item)
                                elif exportDefault.filter_render == True and item.hide_render == False:
                                    print("ITEM FOUND: ", item.name)
                                    objectList.append(item)

                    print("Object List...", objectList)


                    # /////////// - OBJECT MOVEMENT - ///////////////////////////////////////////////////
                    # ///////////////////////////////////////////////////////////////////////////////////
                    if rootObject != None:
                        MoveAll(rootObject, context, Vector((0.0, 0.0, 0.0)))

                    # /////////// - MODIFIERS - ///////////////////////////////////////////////////
                    # ////////////////////////////////////////////////////////////////////////////
                    print(">>> Triangulating Objects <<<")
                    triangulateList = []
                    triangulateList += objectList

                    if expRoot is True:
                        triangulateList.append(rootObject)

                    if useTriangulate is True and self.applyModifiers is True:
                        for item in triangulateList:
                            if item.type == 'MESH':
                                stm = item.CAPStm
                                hasTriangulation = False
                                hasTriangulation = self.AddTriangulate(item)
                                stm.has_triangulate = hasTriangulation

                    # /////////// - EXPORT - ///////////////////////////////////////////////////
                    # ///////////////////////////////////////////////////////////////////////////////////
                    print(">>>> Exporting Objects <<<<")
                    bpy.ops.object.select_all(action='DESELECT')

                    canExport = True
                    if rootObject != None:
                        print("Root Location...", rootObject.location)

                    if len(objectList) == 0 and expRoot is False:
                        print("No objects found in pass, stopping export...")
                        canExport = False


                    elif canExport is True:
                        finalExportList = []
                        finalExportList += objectList
                        print("Final Export List:", finalExportList)

                        if expRoot is True:
                            finalExportList.append(rootObject)

                        if len(finalExportList) > 0:
                            if exportIndividual is True:
                                self.PrepareExportIndividual(context, finalExportList, path, suffix)

                            else:
                                self.PrepareExportCombined(finalExportList, path, group.name, suffix)

                    bpy.ops.object.select_all(action='DESELECT')

                    # /////////// - DELETE/RESTORE - ///////////////////////////////////////////////////
                    # ///////////////////////////////////////////////////////////////////////////////////
                    # Restore names
                    i = 0
                    for item in renameObjectList:
                        item.name = renameNameList[i]
                        i += 1

                    # Remove any triangulation modifiers
                    if useTriangulate is True and self.applyModifiers is True:
                        for object in triangulateList:
                            if object.type == 'MESH':
                                if object.CAPStm.has_triangulate is False:
                                    self.RemoveTriangulate(object)

                    # Move objects back
                    if rootObject != None:
                        MoveAll(rootObject, context, rootObjectLocation)

                    self.exportedPasses += 1
                    print(">>> Pass Complete <<<")


                self.exportedGroups += 1
                self.exportCount += 1
                context.window_manager.progress_update(self.exportCount)
                print(">>> Group Export Complete <<<")


        self.RestoreScene(context)
        context.window_manager.progress_end()

        textGroupSingle = " group"
        textGroupMultiple = " groups"
        dot = "."

        output = "Finished exporting "

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

        if self.exportedPasses > 1:
            output += str(self.exportedPasses) + " passes."
        elif self.exportedPasses == 1:
            output += str(self.exportedPasses) + " pass."

        # Output a nice report
        if self.exportedObjects == 0 and self.exportedGroups == 0:
            self.report({'WARNING'}, 'No objects were exported.  Ensure any objects tagged for exporting are enabled.')

        else:
            self.report({'INFO'}, output)


        return {'FINISHED'}
