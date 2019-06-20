
import bpy, bmesh, os, platform, sys
from mathutils import Vector
from math import pi, radians, degrees
from bpy.types import Operator
from bpy.props import (
    IntProperty, 
    BoolProperty,
    FloatProperty, 
    EnumProperty, 
    PointerProperty, 
    StringProperty, 
    CollectionProperty,
)

from .tk_utils import collections as collection_utils
from .tk_utils import select as select_utils
from .tk_utils import locations as loc_utils
from .tk_utils import object_ops
from .tk_utils import object_transform
from .tk_utils import paths as path_utils

from . import tag_ops
from .export_utils import CheckAnimation, AddTriangulate, RemoveTriangulate

class CAPSULE_OT_ExportAssets(Operator):
    """Exports all objects and collections in the scene that are marked for export."""

    bl_idname = "scene.cap_export"
    bl_label = "Export"

    def PrepareExportIndividual(self, context, targets, path):
        """
        Exports a selection of objects, saving each object into it's own file.
        """

        print(">>> Individual Pass <<<")
        for item in targets:
            print("-"*70)
            print("Exporting...... ", item.name)
            individualFilePath = path + item.name
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
            if self.export_preset.format_type == 'FBX':
                self.export_preset.data_fbx.export(self.export_preset, individualFilePath)

            elif self.export_preset.format_type == 'OBJ':
                self.export_preset.data_obj.export(self.export_preset, individualFilePath)

            elif self.export_preset.format_type == 'GLTF':
                self.export_preset.data_gltf.export(context, self.export_preset, path, item.name)
            
            elif self.export_preset.format_type == 'Alembic':
                self.export_preset.data_abc.export(context, self.export_preset, individualFilePath)

            elif self.export_preset.format_type == 'Collada':
                self.export_preset.data_dae.export(self.export_preset, individualFilePath)

            elif self.export_preset.format_type == 'STL':
                self.export_preset.data_stl.export(context, self.export_preset, individualFilePath)


            # tick up the exports and move the object back.
            self.export_stats['file_export_count'] += 1

            object_transform.MoveObject(item, context, tempLoc)


    def PrepareExportCombined(self, context, targets, path, exportName):
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


        objectFilePath = path + exportName
        print("Final File Path.", objectFilePath)


        # based on the export location, send it to the right place
        if self.export_preset.format_type == 'FBX':
            self.export_preset.data_fbx.export(self.export_preset, objectFilePath)

        elif self.export_preset.format_type == 'OBJ':
            self.export_preset.data_obj.export(self.export_preset, objectFilePath)

        elif self.export_preset.format_type == 'GLTF':
            self.export_preset.data_gltf.export(context, self.export_preset, path, exportName)

        elif self.export_preset.format_type == 'Alembic':
            self.export_preset.data_abc.export(context, self.export_preset, objectFilePath)

        elif self.export_preset.format_type == 'Collada':
            self.export_preset.data_dae.export(self.export_preset, objectFilePath)
        
        elif self.export_preset.format_type == 'STL':
            self.export_preset.data_stl.export(context, self.export_preset, objectFilePath)
        
       

        self.export_stats['file_export_count'] += 1


    # FIXME : Unsure of relevance...
    def GetExportInfo(self, export_preset):
        """
        Builds a list of export information 
        """

        # Stores a whole load of export-related settings for re-use throughout
        # the operator

        #self.bundle_textures = self.export_preset.bundle_textures
        self.filter_render = export_preset.filter_render
        # self.reset_rotation = export_preset.reset_rotation
        #self.export_types = self.export_preset.export_types

        # FIXME: Take note of this!

        #self.bundle_textures = self.export_preset.bundle_textures
        #self.batch_mode = 'AUTO'
        #if self.bundle_textures is True:
        #    self.batch_mode = 'COPY'

    def SetupScene(self, context):
        """
        Stores important scene information while also preparing it for the export process.
        States stored here will be restored with the 'RestoreScene' function.
        """

        print("NEW SETUP SCENE PROCESS")

        self.scene_records = {}

        # If the current context isn't the 3D View, we need to change that before anything else.
        self.scene_records['active_area_type'] = bpy.context.area.type

        for area in context.screen.areas:
            if area != context.area:
                self.region_override = area.regions[0]
                break

        context.area.type = 'VIEW_3D'
        

        # We also need to store current 3D View selections.
        selected_record = []
        if context.active_object is not None:
            for sel in context.selected_objects:
                if sel.name != context.active_object.name:
                    selected_record.append(sel)
        else:
            for sel in context.selected_objects:
                selected_record.append(sel)

        self.scene_records['active_object'] = context.active_object
        self.scene_records['selected_objects'] = selected_record

        # Save the current cursor location
        cursor_loc = bpy.data.scenes[bpy.context.scene.name].cursor.location
        self.scene_records['cursor_location'] = [cursor_loc[0], cursor_loc[1], cursor_loc[2]]

        # Keep a record of the current object mode
        self.scene_records['view_mode'] = bpy.context.mode
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
        # Preserve all scene object information
        
        self.object_records = []
        self.constraint_record = []

        for item in context.scene.objects:
            record = {}
            record['item'] = item
            record['item_name'] = item.name

            # Record object visibility
            # FIXME : hide_viewport is a global property, and isn't the same as Outliner/3D View hides.  Need to get and set that data when fixed.
            # https://devtalk.blender.org/t/view-layer-api-access-wishlist-collection-expand-set/5517
            record['is_hidden'] = item.hide_viewport
            record['is_selectable'] = item.hide_select
            print('Hide records = ', record['is_hidden'], ' ', record['is_selectable'])

            item.hide_select = False


            # Record object loc/rot/scale locks if applicable
            transform_locks = []
            for i, x in enumerate(item.lock_location):
                transform_locks.append(item.lock_location[i])
            for i, x in enumerate(item.lock_rotation):
                transform_locks.append(item.lock_rotation[i])
            for i, x in enumerate(item.lock_scale):
                transform_locks.append(item.lock_scale[i])
            
            if True in transform_locks:
                record['transform_locks'] = transform_locks
            
            item.lock_location = (False, False, False)
            item.lock_rotation = (False, False, False)
            item.lock_scale = (False, False, False)


             # If any armatures are in any non-object modes, we need to change this
            print("Searching for armatures...")
            if item.type == 'ARMATURE':
                mode = object_ops.SwitchObjectMode('OBJECT', item)
                
                if mode != None:
                    record['armature_mode'] = mode


            # Add constraint records if the object has any.
            if len(item.constraints) > 0:

                constraint_list = []

                # Record the current object location for later
                true_location = loc_utils.FindWorldSpaceObjectLocation(item, context)

                # Placeholder for later, once all constraints are isolated and muted.
                constraint_location = Vector((0.0, 0.0, 0.0))

                print("true_location", true_location)
                print("constraint_location", constraint_location)
                record['true_location'] = true_location
                record['constraint_location'] = constraint_location

                # Iterate through and save constraint settings
                i = 0
                for constraint in item.constraints:
                    constraint_list.append( {'index': i, 'enabled': constraint.mute, 'influence': constraint.influence} )
                    i += 1
                
                record['constraint_list'] = constraint_list

                # Mute and isolate them
                for entry in self.constraint_list:
                    constraint = item.constraints[entry['index']]

                    # Mute the constraint
                    constraint.mute = True
                    constraint.influence = 0.0

            # Add the new record
            self.object_records.append(record)

        
        # Now the records have been created, we can alter constraint and object positions.
        for record in self.object_records:
            if 'constraint_list' in record:
                item = record['item']
                record['constraint_location'] = loc_utils.FindWorldSpaceObjectLocation(item, context)
                
                print("NEW CONSTRAINT LOCATION", item.name, entry['constraint_location'])

                print("Moving Object...", item.name, record['true_location'])
                object_transform.MoveObject(item, context, record['true_location'])
                print("New Object Location = ", item.location)
                print("-"*20)
        
        return

        # Now we can unhide and deselect everything
        bpy.ops.object.hide_view_clear()
        bpy.ops.object.select_all(action='DESELECT')



    def RestoreScene(self, context):
        """
        Restores all scene information preserved with the 'SetupScene' function.
        """

        for record in self.object_records:
            item = record['item']
            
             # Restore constraint object positions
            if 'constraint_list' in record:
                print(record)
                print("Moving Object...", item.name, record['constraint_location'])
                object_transform.MoveObject(item, context, record['constraint_location'])
                print("New Object Location = ", item.name, item.location)

                # Restore Constraint Defaults
                for constraint_record in record['constraint_list']:
                    index = constraint_record['index']
                    item.constraints[index].mute = econstraint_recordntry['enabled']
                    item.constraints[index].influence = constraint_record['influence']
            
            # Restore visibility defaults
            print('Hide records = ', record['is_hidden'], ' ', record['is_selectable'])
            item.hide_set(record['is_hidden'])
            item.hide_select = record['is_selectable']

            # Restore transform locks
            if 'transform_locks' in record:
                lock_list = record['transform_locks']

                item.lock_location[0] = lock_list[0]
                item.lock_location[1] = lock_list[1]
                item.lock_location[2] = lock_list[2]
                item.lock_rotation[0] = lock_list[3]
                item.lock_rotation[1] = lock_list[4]
                item.lock_rotation[2] = lock_list[5]
                item.lock_scale[0] = lock_list[6]
                item.lock_scale[1] = lock_list[7]
                item.lock_scale[2] = lock_list[8]
            
            # Restore armature mode
            if 'armature_mode' in record:
                mode = object_ops.SwitchObjectMode(record['armature_mode'], item)


        # Not sure if I need this anymore with view layers.  Test and report back.
        # ======================
        # # Turn off all other layers
        # i = 0
        # while i < 20:
        #     context.scene.layers[i] = self.layersBackup[i]
        #     i += 1

        # Re-select the objects previously selected
        if self.scene_records['active_object'] is not None:
            select_utils.FocusObject(self.scene_records['active_object'])

        for sel in self.scene_records['selected_objects']:
            select_utils.SelectObject(sel)

        if self.scene_records['active_object'] is None and len(self.scene_records['selected_objects']) == 0:
            bpy.ops.object.select_all(action='DESELECT')

        # Restore the 3D view mode
        bpy.ops.object.mode_set(mode = self.scene_records['view_mode'])

        # Restore the 3D cursor
        bpy.data.scenes[bpy.context.scene.name].cursor.location = self.scene_records['cursor_location']

        # Restore the panel type
        # FIXME : This currently doesn't work with the Blender 2.8 area bug.
        context.area.type = self.scene_records['active_area_type']

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
            object_transform.MoveAll_TEST(target, context, [0.0, 0.0, 0.0], self.region_override)

    def FinishSceneMovement(self, context, target, targetObjects, targetLoc, targetRot):
        """
        Moves the focus of the export back from the desired location, after the export is complete.
        """

        # was removed since 1.01 due to unknown bugs and issues... *spooky*
        # if self.reset_rotation is True:
        #     object_transform.RotateAllSafe(self.root_object, context, targetRot, True)

        if self.use_scene_origin is False:
            object_transform.MoveAll_TEST(self.root_object, context, targetLoc, self.region_override)

        # since Blender 2.79 + Unity 2017.3, this is no longer needed.
        # if self.export_preset.format_type == 'FBX':
        #     if self.export_preset.data_fbx.x_unity_rotation_fix is True:
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

    # FIXME : Check if needed and/or is working.
    def SetupArmatureConstraints(self, context):
        """
        Handles armature constraints, turning them off and re-positioning all bones to ensure they are in their
        original positions, ready to be moved by Capsule.
        """

        # This process may fail, so if the user doesn't want us to process the armature constraints then stop right here.
        if self.export_preset.preserve_armature_constraints is True:
            return

        # We need to do similar constraint evaluation for armatures
        # Find translate constraints. mute them and move the affected bones
        # to make the plugin movement successful.
        self.armarture_constraint_list = []
        self.armarture_constraint_objects = []
        for item in context.scene.objects:
            if item.type == 'ARMATURE':
                for bone in item.pose.bones:
                    i = 0
                    for constraint in bone.constraints:
                        if item not in self.armarture_constraint_objects:
                            trueLocation = loc_utils.FindWorldSpaceBoneLocation(item, context, bone)
                            constraintLocation = Vector((bone.location[0], bone.location[1], bone.location[2]))

                            entry = {'object_name': item.name, 'bone_name': bone.name, 'true_location': trueLocation, 'constraint_location': constraintLocation}
                            self.armarture_constraint_objects.append(entry)

                        entry = {'object_name': item.name, 'bone_name': bone.name, 'index': i, 'enabled': constraint.mute, 'influence': constraint.influence}
                        self.armarture_constraint_list.append(entry)

                        i += 1

        print("-"*40)
        print("-"*40)

        # NOW WE CAN FUCKING MUTE THEM
        for entry in self.armarture_constraint_list:
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
        for entry in self.armarture_constraint_objects:
            item = context.scene.objects[entry['object_name']]
            for bone in item.pose.bones:
                if bone.name == entry['bone_name']:
                    entry['constraint_location'] = loc_utils.FindWorldSpaceBoneLocation(item, context, bone)
                    print("NEW CONSTRAINT LOCATION", item.name, bone.name, entry['constraint_location'])

        print("-"*40)
        print("-"*40)

        # Now all problematic constraints have been turned off, we can safely move
        # objects to their initial positions
        for entry in self.armarture_constraint_objects:
            item = context.scene.objects[entry['object_name']]
            for bone in item.pose.bones:
                if bone.name == entry['bone_name']:
                    #print("Moving Bone...", item.name, bone.name, entry['true_location'])
                    object_transform.MoveBone(item, bone, context, entry['true_location'])
                    #print("New Bone Location = ", bone.location)

        print("-"*40)
        print("-"*40)

    # FIXME : Check if needed and/or is working.
    def RestoreArmatureConstraints(self, context):
        """
        Restores any armature constraint changes that were made to prepare the scene for export.
        """

        if self.export_preset.preserve_armature_constraints is True:
            return

        # Restore constraint object positions
        for entry in self.armarture_constraint_objects:
            item = context.scene.objects[entry['object_name']]
            for bone in item.pose.bones:
                if bone.name == entry['bone_name']:
                    #print("Moving Bone...", item.name, bone.name)
                    object_transform.MoveBone(item, bone, context, entry['constraint_location'])
                    #print("New Bone Location = ", bone.location)

        # Restore Constraint Defaults
        for entry in self.armarture_constraint_list:
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
        sub_directory_check = []

        # Checks for any easily-preventable errors
        for item in context.scene.objects:
            if item.CAPObj.enable_export is True:

                # Check Export Key
                expKey = int(item.CAPObj.export_preset) - 1
                if expKey == -1:
                    statement = "The selected object " + item.name + " has no export default selected.  Please define!"
                    select_utils.FocusObject(item)
                    return statement

                # Check Location Preset
                if int(item.CAPObj.location_preset) == 0:
                    statement =  "The selected object " + item.name + " has no location preset defined, please define one!"
                    select_utils.FocusObject(item)
                    return statement

                self.export_stats['expected_export_quantity'] += 1


        # If we're using Unity export options, ensure that every object mesh has a single user
        # FIXME : Determine if this is still needed or not.

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
                exp_key = int(collection.CAPCol.export_preset) - 1
                if exp_key == -1:

                    bpy.ops.object.select_all(action='DESELECT')
                    for item in collection.all_objects:
                        select_utils.SelectObject(item)
                    statement = "The selected collection " + collection.name + " has no export default selected.  Please define!"
                    return statement

                # Check Export Location
                if int(collection.CAPCol.location_preset) == 0:
                    print("FOUND BAD COLLECTION LOCATION - ", collection)
                    bpy.ops.object.select_all(action='DESELECT')
                    for item in collection.all_objects:
                        select_utils.SelectObject(item)
                    statement =  "The selected collection " + collection.name + " has no location preset defined, please define one!"
                    return statement

                self.export_stats['expected_export_quantity'] += 1

        # Check all Location Presets to ensure the chatacters contained are valid.
        i = 0
        while i < len(exp.location_presets):
            enumIndex = i
            enumIndex -= 1

            defaultFilePath = exp.location_presets[enumIndex].path
            print("Checking File Paths...", defaultFilePath)

            if defaultFilePath == "":
                statement = "The path for " + exp.location_presets[enumIndex].name + " cannot be empty.  Please give the Location a valid file path."
                return statement

            i += 1

        # Check all collected sub-directory names for invalid characters if we can't replace them.
        if self.replace_invalid_characters is False:
            for name in sub_directory_check:
                print("Checking Directory...", name)
                result = path_utils.CheckSystemChar(context, name[1])
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
        self.export_info = bpy.data.objects[addon_prefs.default_datablock].CAPExp
        self.replace_invalid_characters = addon_prefs.substitute_directories

        # Set export counts here just in case
        self.export_stats = {}
        self.export_stats['expected_export_quantity'] = 0
        self.export_stats['object_export_count'] = 0
        self.export_stats['collection_export_count'] = 0
        self.export_stats['file_export_count'] = 0

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

        print('scene setup complete...')

        # FIXME
        # 2.80 - Commenting out until I fix the rest
        # context.window_manager.progress_begin(0, self.export_stats['expected_export_quantity'])
        


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
                expKey = int(object.CAPObj.export_preset) - 1

                if expKey == -1:
                    statement = "The selected object " + object.name + " has no export default selected.  Please define!"
                    select_utils.FocusObject(object)
                    self.report({'WARNING'}, statement)
                    self.RestoreScene(context)
                    return {'FINISHED'}

                # Get the export default and send it to a function to create additional instance properties
                self.export_preset = self.export_info.file_presets[expKey]
                self.GetExportInfo(self.export_preset)

                # Get the root object and set some more variables!
                self.root_object = object
                self.use_scene_origin = self.root_object.CAPObj.use_scene_origin

                # FIXME: Is this needed anymore?
                # If they asked us not preserve armature constraints, we can
                # do our jerb and ensure they don't screw things up beyond this code
                # Prepares the object for movement, will only work if Preserve Armature Constraints is false.
                self.SetupArmatureConstraints(context)

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
                object_name = self.root_object.name


                # FILE NAME
                # /////////////////////////////////////////////////
                location_preset_index = int(self.root_object.CAPObj.location_preset) - 1
                location_preset = exp.location_presets[location_preset_index]

                path = path_utils.CreateFilePath(location_preset, [self.root_object], None, self.replace_invalid_characters)

                # If while calculating a file path a warning was found, return early.
                if path.find("WARNING") == 0:
                    path = path.replace("WARNING: ", "")
                    self.report({'WARNING'}, path)
                    self.RestoreScene(context)
                    return {'CANCELLED'}

                print("Path created...", path)


                # OBJECT MOVEMENT PREPARATION
                # /////////////////////////////////////////////////
                scene_origin = None

                if self.use_scene_origin is False:
                    self.StartSceneMovement(context, self.root_object, [self.root_object], root_object_rotation)

                else:
                    bpy.ops.view3d.snap_cursor_to_center()
                    bpy.ops.object.select_all(action='DESELECT')
                    bpy.ops.object.empty_add(type='PLAIN_AXES')

                    scene_origin = bpy.context.view_layer.objects.active
                    self.StartSceneMovement(context, scene_origin, [self.root_object], root_object_rotation)


                # MODIFIERS
                # /////////////////////////////////////////////////
                # FIXME / 2.0 : add new command system here?


                # EXPORT PROCESS
                # /////////////////////////////////////////////////

                # A separate FBX export function call for every corner case isnt actually necessary
                self.PrepareExportCombined(context, [self.root_object], path, object_name)



                # DELETE/RESTORE 
                # /////////////////////////////////////////////////
                # Reverse movement and rotation
                if self.use_scene_origin is False:
                    self.FinishSceneMovement(context, self.root_object, [self.root_object], root_object_location, root_object_rotation)
                else:
                    self.FinishSceneMovement(context, scene_origin, [self.root_object], root_object_location, root_object_rotation)
                    object_ops.DeleteObject(scene_origin)

                print(">>> Pass Complete <<<")

                # Cleans up any armature constraint modification (only works if Preserve Armature Constraints is off)
                self.RestoreArmatureConstraints(context)


                # TRACKER
                # /////////////////////////////////////////////////
                # Count up exported objects
                self.export_stats['object_export_count'] += 1
                self.export_stats['expected_export_quantity'] += 1
                # context.window_manager.progress_update(self.export_stats['expected_export_quantity'])
                print(">>> Object Export Complete <<<")


        ###############################################################
        # COLLECTION CYCLE
        ###############################################################
        # Now hold up, its collection time!
        for collection in collection_utils.GetSceneCollections(context.scene, True):
            if collection.CAPCol.enable_export is True:

                print('stepping through new collection...')

                print("-"*79)
                print("NEW JOB", "-"*70)
                print("-"*79)
                print(collection.name)

                # Before we do anything, check that a root object exists
                self.root_object = None
                self.root_object_name = ""
                self.root_object_type = 0
                self.use_scene_origin = False
                is_root_in_collection = False

                # Find the root object in a collection, if thats where it's located
                for item in collection.all_objects:
                    if item.name == collection.CAPCol.root_object:
                        self.root_object = item
                        self.root_object_name = item.name
                        is_root_in_collection = True

                # Otherwise, find it elsewhere
                if is_root_in_collection == False:
                    for item in context.scene.objects:
                        if item.name == collection.CAPCol.root_object:
                            self.root_object = item
                            self.root_object_name = item.name

                if self.root_object == None:
                    self.use_scene_origin = True
                    print("No root object is currently being used, proceed!")

                #Get the export default for the object
                expKey = int(collection.CAPCol.export_preset) - 1

                if expKey == -1:
                    statement = "The collection " + collection.name + " has no export default selected.  Please define!"
                    self.report({'WARNING'}, statement)
                    self.RestoreScene(context)
                    return {'FINISHED'}

                # Collect hidden defaults to restore afterwards.
                object_name = collection.name
                self.export_preset = self.export_info.file_presets[expKey]
                self.GetExportInfo(self.export_preset)
                print("Using Export Default...", self.export_preset.name, ".  Export Key", expKey)
                
                # Get the root object location for later use
                root_object_location = [0.0, 0.0, 0.0]
                root_object_rotation = [0.0, 0.0, 0.0]

                if self.root_object != None:
                    tempROL = loc_utils.FindWorldSpaceObjectLocation(self.root_object, context)
                    root_object_location = [tempROL[0], tempROL[1], tempROL[2]]
                    root_object_rotation = [self.root_object.rotation_euler[0], self.root_object.rotation_euler[1], self.root_object.rotation_euler[2]]

                
                #/////////////////// - FILE NAME - /////////////////////////////////////////////////
                location_preset_index = int(collection.CAPCol.location_preset) - 1
                location_preset = exp.location_presets[location_preset_index - 1]
                path = path_utils.CreateFilePath(location_preset, collection.all_objects, collection, self.replace_invalid_characters)

                if path.find("WARNING") == 0:
                    path = path.replace("WARNING: ", "")
                    self.report({'WARNING'}, path)
                    self.RestoreScene(context)
                    return {'CANCELLED'}

                print("Path created...", path)


                #/////////////////// - FIND OBJECTS - /////////////////////////////////////////////////
                # First we have to find all objects in the collection that are of type MESHHH
                # If auto-assignment is on, use the names to filter into lists, otherwise forget it.

                object_list = []

                print(">>>> Collecting Objects <<<<")
                for item in collection.all_objects:
                    if item.name != self.root_object_name:

                        if self.export_preset.filter_render == False:
                            print("ITEM FOUND: ", item.name)
                            object_list.append(item)

                        elif self.export_preset.filter_render == True and item.hide_render == False:
                            print("ITEM FOUND: ", item.name)
                            object_list.append(item)

                print("Object List...", object_list)


                # /////////// - OBJECT MOVEMENT - ///////////////////////////////////////////////////
                # ///////////////////////////////////////////////////////////////////////////////////
                moved_objects = []
                moved_objects += object_list
                scene_origin = None

                # If we have a usable root object, use that as the origin point
                if self.root_object != None:
                    moved_objects.append(self.root_object)
                    self.StartSceneMovement(context, self.root_object, moved_objects, root_object_rotation)

                # If not, create one now, and get rid of it later
                else:
                    bpy.ops.view3d.snap_cursor_to_center()
                    bpy.ops.object.select_all(action='DESELECT')
                    bpy.ops.object.empty_add(type='PLAIN_AXES')
                    scene_origin = bpy.context.view_layer.objects.active
                    self.StartSceneMovement(context, scene_origin, moved_objects, root_object_rotation)


                # /////////// - MODIFIERS - //////////////////////////////////////////////
                # ////////////////////////////////////////////////////////////////////////
                # FIXME / 2.0 : add new command system here?


                # /////////// - EXPORT - ///////////////////////////////////////////////////
                # //////////////////////////////////////////////////////////////////////////
                print(">>>> Exporting Objects <<<<")
                bpy.ops.object.select_all(action='DESELECT')

                is_collection_exportable = True
                if self.root_object != None:
                    print("Root Location...", self.root_object.location)

                if len(object_list) == 0:
                    print("No objects found in pass, stopping export...")
                    is_collection_exportable = False


                elif is_collection_exportable is True:
                    finalExportList = []
                    finalExportList += object_list

                    if self.root_object != None:
                        finalExportList.append(self.root_object)

                    print("Final Export List:", finalExportList)

                    if len(finalExportList) > 0:
                        self.PrepareExportCombined(context, finalExportList, path, collection.name)

                bpy.ops.object.select_all(action='DESELECT')

                # /////////// - DELETE/RESTORE - //////////////////////////////////////////
                # /////////////////////////////////////////////////////////////////////////

                # Move objects back
                if self.root_object != None:
                    self.FinishSceneMovement(context, self.root_object, moved_objects, root_object_location, root_object_rotation)
                else:
                    self.FinishSceneMovement(context, scene_origin, moved_objects, root_object_location, root_object_rotation)
                    object_ops.DeleteObject(scene_origin)



                self.export_stats['collection_export_count'] += 1
                self.export_stats['expected_export_quantity'] += 1
                # context.window_manager.progress_update(self.export_stats['expected_export_quantity'])

                print(">>> Collection Export Complete <<<")


        self.RestoreScene(context)
        # context.window_manager.progress_end()

        # 2.80 BONUS TEST TIME
        bpy.context.area.type = 'VIEW_3D'

        textCollectionSingle = " collection"
        textCollectionPlural = " collections"

        output = "Finished processing "

        if self.export_stats['object_export_count'] > 1:
            output += str(self.export_stats['object_export_count']) + " objects"
        elif self.export_stats['object_export_count'] == 1:
            output += str(self.export_stats['object_export_count']) + " object"

        if self.export_stats['object_export_count'] > 0 and self.export_stats['collection_export_count'] > 0:
            output += " and "
        if self.export_stats['collection_export_count'] > 1:
            output += str(self.export_stats['collection_export_count']) + " collections"
        elif self.export_stats['collection_export_count'] == 1:
            output += str(self.export_stats['collection_export_count']) + " collection"

        output += ".  "
        output += "Total of "

        if self.export_stats['file_export_count'] > 1:
            output += str(self.export_stats['file_export_count']) + " files exported."
        elif self.export_stats['file_export_count'] == 1:
            output += str(self.export_stats['file_export_count']) + " file."

        # Output a nice report
        if self.export_stats['object_export_count'] == 0 and self.export_stats['collection_export_count'] == 0:
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
