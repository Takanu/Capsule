
import bpy

from mathutils import Vector
from . import collections as collection_utils
from . import select as select_utils
from . import locations as loc_utils
from . import paths as path_utils

from . import object_ops, object_transform


def SaveSceneContext(context):
    """
    Records all selection, edit mode, object constraint and view layer properties and saves it for later.
    """

    print("NEW SETUP SCENE PROCESS")

    scene_records = {}

    # If the current context isn't the 3D View, we need to change that before anything else.
    scene_records['active_area_type'] = bpy.context.area.type

    for area in context.screen.areas:
        if area != context.area:
            scene_records['region_override'] = area.regions[0]
            print("got a region override - ", scene_records['region_override'])
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

    scene_records['active_object'] = context.active_object
    scene_records['selected_objects'] = selected_record

    # Save the current cursor location
    cursor_loc = bpy.data.scenes[bpy.context.scene.name].cursor.location
    scene_records['cursor_location'] = [cursor_loc[0], cursor_loc[1], cursor_loc[2]]

    # Keep a record of the current object mode 
    scene_records['view_mode'] = bpy.context.mode
    bpy.ops.object.mode_set(mode='OBJECT')


    # ======================
    # Setup a new view layer

    # I dont actually need this, might be useful later
    # scene_records['current_view_layer'] = bpy.context.view_layer.name

    bpy.ops.scene.view_layer_add()
    bpy.context.view_layer.name = ">> Capsule <<"
    scene_records['capsule_view_layer'] = ">> Capsule <<"


    # ======================
    # Preserve all scene object information
    
    object_records = []

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
            true_location = loc_utils.FindWorldSpaceObjectLocation(context, item)

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
            for entry in constraint_list:
                constraint = item.constraints[entry['index']]

                # Mute the constraint
                constraint.mute = True
                constraint.influence = 0.0

        # Add the new record
        object_records.append(record)
    
    
    # Now the records have been created, we can alter constraint and object positions.
    for record in object_records:
        if 'constraint_list' in record:
            item = record['item']
            record['constraint_location'] = loc_utils.FindWorldSpaceObjectLocation(context, item)
            
            print("NEW CONSTRAINT LOCATION", item.name, record['constraint_location'])

            print("Moving Object...", item.name, record['true_location'])
            object_transform.MoveObjectFailsafe(item, context, record['true_location'], scene_records['region_override'])
            print("New Object Location = ", item.location)
            print("-"*20)

    # Now we can unhide and deselect everything
    bpy.ops.object.hide_view_clear()
    bpy.ops.object.select_all(action='DESELECT')

    records = {}
    records['scene'] = scene_records
    records['object'] = object_records
    return records


def RestoreSceneContext(context, record):
    """
    Restores all selection, edit mode, object constraint and view layer properties from a previously saved scene context.
    """

    scene_records = record['scene']
    object_records = record['object']

    for record in object_records:
        item = record['item']
        
            # Restore constraint object positions
        if 'constraint_list' in record:
            print(record)
            print("Moving Object...", item.name, record['constraint_location'])
            object_transform.MoveObjectFailsafe(item, context, record['constraint_location'], scene_records['region_override'])
            print("New Object Location = ", item.name, item.location)

            # Restore Constraint Defaults
            for constraint_record in record['constraint_list']:
                index = constraint_record['index']
                item.constraints[index].mute = constraint_record['enabled']
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


    # ======================
    # Delete the created view layer.
    # ======================
    bpy.ops.scene.view_layer_remove()

    # Re-select the objects previously selected
    if scene_records['active_object'] is not None:
        select_utils.FocusObject(scene_records['active_object'])

    for sel in scene_records['selected_objects']:
        select_utils.SelectObject(sel)

    if scene_records['active_object'] is None and len(scene_records['selected_objects']) == 0:
        bpy.ops.object.select_all(action='DESELECT')

    # Restore the 3D view mode
    bpy.ops.object.mode_set(mode = scene_records['view_mode'])

    # Restore the 3D cursor
    bpy.data.scenes[bpy.context.scene.name].cursor.location = scene_records['cursor_location']

    # Restore the panel type
    # FIXME : This currently doesn't work with the Blender 2.8 area bug.
    context.area.type = scene_records['active_area_type']

    print("Rawr")


# FIXME : Check if needed and/or is working.
def MuteArmatureConstraints(context):
    """
    Performs two operations together:
    - Records all armatures and preserves their constraints.
    - Mutes them afterwards to prevent interference in the Capsule export.
    """

    # # This process may fail, so if the user doesn't want us to process the armature constraints then stop right here.
    # if self.export_preset.preserve_armature_constraints is True:
    #     return

    # We need to do similar constraint evaluation for armatures
    # Find translate constraints. mute them and move the affected bones
    # to make the plugin movement successful.
    record = {}
    record['armature_constraints'] = []
    record['armature_objects'] = []

    for item in context.scene.objects:
        if item.type == 'ARMATURE':
            for bone in item.pose.bones:
                i = 0
                for constraint in bone.constraints:
                    if item not in record['armature_objects']:
                        trueLocation = loc_utils.FindWorldSpaceBoneLocation(item, context, bone)
                        constraintLocation = Vector((bone.location[0], bone.location[1], bone.location[2]))

                        entry = {'object_name': item.name, 'bone_name': bone.name, 'true_location': trueLocation, 'constraint_location': constraintLocation}
                        record['armature_objects'].append(entry)

                    entry = {'object_name': item.name, 'bone_name': bone.name, 'index': i, 'enabled': constraint.mute, 'influence': constraint.influence}
                    record['armature_constraints'].append(entry)

                    i += 1

    print("-"*40)
    print("-"*40)

    # NOW WE CAN FUCKING MUTE THEM
    for entry in record['armature_constraints']:
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
    for entry in record['armature_objects']:
        item = context.scene.objects[entry['object_name']]
        for bone in item.pose.bones:
            if bone.name == entry['bone_name']:
                entry['constraint_location'] = loc_utils.FindWorldSpaceBoneLocation(item, context, bone)
                print("NEW CONSTRAINT LOCATION", item.name, bone.name, entry['constraint_location'])

    print("-"*40)
    print("-"*40)

    # Now all problematic constraints have been turned off, we can safely move
    # objects to their initial positions
    for entry in record['armature_objects']:
        item = context.scene.objects[entry['object_name']]
        for bone in item.pose.bones:
            if bone.name == entry['bone_name']:
                #print("Moving Bone...", item.name, bone.name, entry['true_location'])
                object_transform.MoveBone(item, bone, context, entry['true_location'])
                #print("New Bone Location = ", bone.location)

    print("-"*40)
    print("-"*40)

    return record

# FIXME : Check if needed and/or is working.
def RestoreArmatureConstraints(context, record):
    """
    Restores any armature constraint changes that were made to prepare the scene for export.
    """

    # if self.export_preset.preserve_armature_constraints is True:
    #     return

    # Restore constraint object positions
    for entry in record['armature_objects']:
        item = context.scene.objects[entry['object_name']]
        for bone in item.pose.bones:
            if bone.name == entry['bone_name']:
                #print("Moving Bone...", item.name, bone.name)
                object_transform.MoveBone(item, bone, context, entry['constraint_location'])
                #print("New Bone Location = ", bone.location)

    # Restore Constraint Defaults
    for entry in record['armature_constraints']:
        item = bpy.data.objects[entry['object_name']]
        for bone in item.pose.bones:
            if bone.name == entry['bone_name']:
                index = entry['index']
                bone.constraints[index].mute = entry['enabled']
                bone.constraints[index].influence = entry['influence']


def CheckCapsuleErrors(context):
    # Ensures that the scene is setup with correct settings, before proceeding
    # with the export.

    preferences = context.preferences
    addon_prefs = preferences.addons['Capsule'].preferences
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

            # self.export_stats['expected_export_quantity'] += 1


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

            # self.export_stats['expected_export_quantity'] += 1

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
    
    # # Check all collected sub-directory names for invalid characters if we can't replace them.
    if addon_prefs.substitute_directories is False:
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