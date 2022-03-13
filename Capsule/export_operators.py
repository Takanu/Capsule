
import bpy, bmesh, os, platform, sys

from datetime import datetime
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
from .tk_utils import record as record_utils

from . import tag_ops
from .export_utils import CheckAnimation, AddTriangulate, RemoveTriangulate


class CAPSULE_OT_ExportAll(Operator):
    """Exports all objects and collections in the scene that are marked for export."""
    bl_idname = "scene.cap_export_all"
    bl_label = "Export All"

    def execute(self, context):
        scn = context.scene.CAPScn
        preferences = context.preferences
        addon_prefs = preferences.addons[__package__].preferences
        cap_file = None


        # /////////////////////////////////////////////////
        # SETUP
    
        # For the new pie menu, we need to see if any data exists before continuing
        try:
            cap_file = bpy.data.objects[addon_prefs.default_datablock].CAPFile
        except KeyError:
            self.report({'WARNING'}, "No Capsule Data for this blend file exists.  Please create it using the Toolshelf or Addon Preferences menu.")
            return {'FINISHED'}

        # We need to make a separate definition set for preserving and restoring scene data.
        result = record_utils.CheckCapsuleErrors(context)
        if result is not None:
            self.report({'WARNING'}, result)
            return {'FINISHED'}
        
        # Make a record of the scene before we do anything
        global_record = record_utils.SaveSceneContext(context)

        # Set export counts here
        export_stats = {}
        # export_stats['expected_export_quantity'] = 0
        export_stats['obj_exported'] = 0
        export_stats['col_exported'] = 0
        total_exp_count = 0
        
        # get the current time for later
        global_record['export_time'] = datetime.now()


        # /////////////////////////////////////////////////
        # FETCH

        # Fetch objects and collections for export
        export_objects = []
        export_collections = []

        for object in context.scene.objects:
            if object.CAPObj.enable_export is True:
                export_objects.append(object)
        
        for collection in collection_utils.GetSceneCollections(context.scene, True):
            if collection.CAPCol.enable_export is True:
                export_collections.append(collection)
        
        #print(export_objects)
        #print(export_objects)


        # /////////////////////////////////////////////////
        # OBJECT EXPORT

        object_export_result = ExportObjectList(context, cap_file, export_objects, global_record)
        if 'warning' in object_export_result:
            self.report({'WARNING'}, object_export_result['warning'])
            record_utils.RestoreSceneContext(context, global_record)
            return {'FINISHED'}

        export_stats['obj_exported'] = object_export_result['export_count']
        export_stats['obj_hidden'] = object_export_result['export_hidden']
        

        # /////////////////////////////////////////////////
        # COLLECTION EXPORT
        
        collection_export_result = ExportCollectionList(context, cap_file, export_collections, global_record)
        if 'warning' in collection_export_result:
            self.report({'WARNING'}, collection_export_result['warning'])
            record_utils.RestoreSceneContext(context, global_record)
            return {'FINISHED'}

        export_stats['col_exported'] = collection_export_result['export_count']
        export_stats['col_hidden'] = collection_export_result['export_hidden']
        

        # /////////////////////////////////////////////////
        # EXPORT SUMMARY  
        export_info = GetExportSummary(export_stats)
        self.report({export_info[0]}, export_info[1])


        record_utils.RestoreSceneContext(context, global_record)

        return {'FINISHED'}



class CAPSULE_OT_ExportSelected(Operator):
    """Exports all selected objects and collections in the scene that are marked for export."""
    bl_idname = "scene.cap_export_selected"
    bl_label = "Export Selected"

    def execute(self, context):
        scn = context.scene.CAPScn
        preferences = context.preferences
        addon_prefs = preferences.addons[__package__].preferences
        cap_file = None


        # /////////////////////////////////////////////////
        # FETCH

        # Fetch objects and collections for export before we set the scene
        export_objects = []
        export_collections = []

        for object in context.selected_objects:
            if object.CAPObj.enable_export is True:
                export_objects.append(object)
        
        # TODO: Ensure that when the selection list supports multiple objects again that
        # this is remedied
        for collection in collection_utils.GetSelectedObjectCollections():
            if collection.CAPCol.enable_export is True:
                export_collections.append(collection)

        print("Objects to export = ", export_objects)
        print("Collections to export = ", export_collections)


        # /////////////////////////////////////////////////
        # SETUP
    
        # For the new pie menu, we need to see if any data exists before continuing
        try:
            cap_file = bpy.data.objects[addon_prefs.default_datablock].CAPFile
        except KeyError:
            self.report({'WARNING'}, "No Capsule Data for this blend file exists.  Please create it using the Toolshelf or Addon Preferences menu.")
            return {'FINISHED'}

        # We need to make a separate definition set for preserving and restoring scene data.
        result = record_utils.CheckCapsuleErrors(context, export_objects, export_collections)
        if result is not None:
            self.report({'WARNING'}, result)
            return {'FINISHED'}
        
        # Make a record of the scene before we do anything
        global_record = record_utils.SaveSceneContext(context)

        # Set export counts here
        export_stats = {}

        # get the current time for later
        global_record['export_time'] = datetime.now()
        

        # /////////////////////////////////////////////////
        # OBJECT EXPORT

        object_export_result = ExportObjectList(context, cap_file, export_objects, global_record)
        if 'warning' in object_export_result:
            self.report({'WARNING'}, object_export_result['warning'])
            record_utils.RestoreSceneContext(context, global_record)
            return {'FINISHED'}

        export_stats['obj_exported'] = object_export_result['export_count']
        export_stats['obj_hidden'] = object_export_result['export_hidden']
        

        # /////////////////////////////////////////////////
        # COLLECTION EXPORT
        
        collection_export_result = ExportCollectionList(context, cap_file, export_collections, global_record)
        if 'warning' in collection_export_result:
            self.report({'WARNING'}, collection_export_result['warning'])
            record_utils.RestoreSceneContext(context, global_record)
            return {'FINISHED'}

        export_stats['col_exported'] = collection_export_result['export_count']
        export_stats['col_hidden'] = collection_export_result['export_hidden']


        print("Final Export Stats = ", export_stats)        

        # /////////////////////////////////////////////////
        # EXPORT SUMMARY  
        export_info = GetExportSummary(export_stats)
        self.report({export_info[0]}, export_info[1])
        

        record_utils.RestoreSceneContext(context, global_record)

        return {'FINISHED'}




def ExportObjectList(context, cap_file, object_list, global_record):
    """
    Exports a list of given objects
    """

    result = {}
    result['export_count'] = 0
    result['export_hidden'] = 0

    for item in object_list:
        meta = {}
        meta['3d_region'] = global_record['scene']['3d_region_override']
        meta['export_time'] = global_record['export_time']
        meta['export_name'] = item.name

        # Get the export default for the object
        export_preset_index = int(item.CAPObj.export_preset) - 1
        export_preset = cap_file.export_presets[export_preset_index]
        meta['preset_name'] = export_preset.name

        location_preset_index = int(item.CAPObj.location_preset) - 1
        location_preset = cap_file.location_presets[location_preset_index]

        origin_point = item.CAPObj.origin_point

        # Filter by rendering
        object_hidden = False
        if export_preset.filter_by_rendering is True:
            if item.hide_render is True:
                result['export_hidden'] += 1
                object_hidden = True
                continue
            else:
                for collection in item.users_collection:
                    if collection.hide_render is True:
                        result['export_hidden'] += 1
                        object_hidden = True
                        break
        
        if object_hidden == True:
            continue

        # E X P O R T
        export_result = ExportTarget(context, [item], item.name, export_preset, location_preset, origin_point, item, meta)

        # Return early if a warning was triggered.
        if 'warning' in export_result:
            result['warning'] = export_result['warning']
            return result
        
        # Add to stats
        result['export_count'] += 1
    
    return result



def ExportCollectionList(context, cap_file, collection_list, global_record):
    """
    Exports a list of given collections
    """

    result = {}
    result['export_count'] = 0
    result['export_hidden'] = 0
    
    for collection in collection_list:
        meta = {}
        meta['3d_region'] = global_record['scene']['3d_region_override']
        meta['export_time'] = global_record['export_time']
        meta['export_name'] = collection.name

        # Get the export default for the object
        export_preset_index = int(collection.CAPCol.export_preset) - 1
        export_preset = cap_file.export_presets[export_preset_index]
        meta['preset_name'] = export_preset.name

        location_preset_index = int(collection.CAPCol.location_preset) - 1
        location_preset = cap_file.location_presets[location_preset_index]

        origin_point = collection.CAPCol.origin_point
        root_definition = None
        if origin_point == 'Object':
            root_definition = bpy.context.scene.objects.get(collection.CAPCol.root_object.name)
            #print(' R O O T - ', root_definition)

        # Collect all objects that are applicable for this export
        child_export_option = collection.CAPCol.child_export_option
        targets = collection_utils.GetExportableCollectionObjects(context, collection, child_export_option)

        #print("Current Export Targets = ", targets)
        
        # TODO : Find an efficient way to filter out objects that have rendering turned off by the collections they're in.
        # Filter by rendering
        if export_preset.filter_by_rendering is True:
            renderable = []

            for target in targets:
                object_hidden = False

                if target.hide_render is True:
                    object_hidden = True

                else:
                    for collection in target.users_collection:
                        if collection.hide_render is True:
                            object_hidden = True
                            break
                
                if object_hidden == False:
                    renderable.append(target)
            
            targets = renderable
            #print("Filtered Export Targets = ", targets)

            if len(targets) == 0:
                result['export_hidden'] += 1
                return result

        #print("PREPARING TO EXPORT COLLECTION ", collection.name)

        # E X P O R T
        export_result = ExportTarget(context, targets, collection.name, export_preset, location_preset, origin_point, root_definition, meta)

        # Return early if a warning was triggered.
        if 'warning' in export_result:
            result['warning'] = export_result['warning']
            return result
        
        # Add to stats
        result['export_count'] += 1
    
    return result



def ExportTarget(context, targets, export_name, export_preset, location_preset, origin_point, root_definition, meta):
    """
    The main function for exporting objects in Capsule, designed to work with an Operator in being provided
    the right details for the export.
    """

    scn = context.scene.CAPScn
    preferences = context.preferences
    addon_prefs = preferences.addons[__package__].preferences

    result = {}

    # TODO 1.2 : Is this needed anymore?
    # If they asked us not preserve armature constraints, we can
    # do our job and ensure they don't screw things up beyond this code
    # Prepares the object for movement, will only work if Preserve Armature Constraints is false.
    if export_preset.preserve_armature_constraints == True:
        armature_record = record_utils.MuteArmatureConstraints(context)


    # /////////////////////////////////////////////////
    # FILE NAME
    path = path_utils.CreateFilePath(location_preset, targets, None, addon_prefs.substitute_directories, meta)

    if addon_prefs.substitute_directories is True:
        export_name = path_utils.SubstituteDirectoryCharacters(export_name)

    # If while calculating a file path a warning was found, return early.
    if path.find("WARNING") == 0:
        path = path.replace("WARNING: ", "")
        result['warning'] = path
        return result

    #print("Path created...", path)


    # /////////////////////////////////////////////////
    # OBJECT MOVEMENT

    # Get the root location if we can, otherwise return early.
    # FIXME 1.2 - not using the actual location currently, can't </3
    root_location = GetRootLocationDefinition(context, export_name, origin_point, root_definition)
    if 'warning' in root_location:
        result['warning'] = root_location['warning']
        return result

    if origin_point == "Object":
        #print('origin point is object, moving...')
        #print('origin point is object, moving...')
        object_transform.MoveAllFailsafe(context, root_definition, [0.0, 0.0, 0.0], meta['3d_region'])


    # /////////////////////////////////////////////////
    # EXPORT PROCESS

    # A separate export function call for every corner case isnt actually necessary
    PrepareExportCombined(context, targets, path, export_preset, export_name)


    # /////////////////////////////////////////////////
    # DELETE/RESTORE 

    # Reverse movement and rotation
    if origin_point == "Object":
        object_transform.MoveAllFailsafe(context, root_definition, root_location['location'], meta['3d_region'])

    #print(">>> Pass Complete <<<")

    # Cleans up any armature constraint modification (only works if Preserve Armature Constraints is off)
    if export_preset.preserve_armature_constraints == True:
        record_utils.RestoreArmatureConstraints(context, armature_record)


    # /////////////////////////////////////////////////
    # TRACKER

    # Count up exported objects
    # export_stats['obj_exported'] += 1
    # export_stats['expected_export_quantity'] += 1
    # # context.window_manager.progress_update(export_stats['expected_export_quantity'])
    # #print(">>> Object Export Complete <<<")

    return {}


def PrepareExportCombined(context, targets, path, export_preset, export_name):
    """
    Exports a selection of objects into a single file.
    """

    #print(">>> Exporting Combined Pass <<<")
    #print(">>> Exporting Combined Pass <<<")

    bpy.ops.object.select_all(action= 'DESELECT')

    for item in targets:
        #print("Exporting: ", item.name)
        #print("Exporting: ", item.name)
        select_utils.SelectObject(item)


    object_file_path = path + export_name
    #print("Final File Path.", object_file_path)


    # based on the export location, send it to the right place
    if export_preset.format_type == 'FBX':
        export_preset.data_fbx.export(export_preset, object_file_path)

    elif export_preset.format_type == 'OBJ':
        export_preset.data_obj.export(export_preset, object_file_path)

    elif export_preset.format_type == 'GLTF':
        export_preset.data_gltf.export(context, export_preset, path, export_name)

    elif export_preset.format_type == 'Alembic':
        export_preset.data_abc.export(context, export_preset, object_file_path)

    elif export_preset.format_type == 'Collada':
        export_preset.data_dae.export(export_preset, object_file_path)
    
    elif export_preset.format_type == 'STL':
        export_preset.data_stl.export(context, export_preset, object_file_path)

    elif export_preset.format_type == 'USD':
        export_preset.data_usd.export(context, export_preset, object_file_path)



# TODO 2.0 : This probably doesn't work

def PrepareExportIndividual(context, targets, path, export_preset):
    """
    Exports a selection of objects, saving each object into it's own file.
    """

    #print(">>> Individual Pass <<<")
    for item in targets:
        #print("-"*70)
        #print("-"*70)
        individual_file_path = path + item.name
        #print("Final File Path.", individual_file_path)

        # For the time being, manually move the object back and forth to
        # the world origin point.
        tempLoc = loc_utils.FindWorldSpaceObjectLocation(context, item)

        # FIXME: Doesn't distinguish between "Use Scene Origin".

        # moves each target to the centre individually, even though these objects have
        # already been moved before collectively.
        object_transform.MoveObject(item, context, (0.0, 0.0, 0.0))

        bpy.ops.object.select_all(action= 'DESELECT')
        select_utils.FocusObject(item)


        # based on the export location, send it to the right place
        if export_preset.format_type == 'FBX':
            export_preset.data_fbx.export(export_preset, individual_file_path)

        elif export_preset.format_type == 'OBJ':
            export_preset.data_obj.export(export_preset, individual_file_path)

        elif export_preset.format_type == 'GLTF':
            export_preset.data_gltf.export(context, export_preset, path, item.name)
        
        elif export_preset.format_type == 'Alembic':
            export_preset.data_abc.export(context, export_preset, individual_file_path)

        elif export_preset.format_type == 'Collada':
            export_preset.data_dae.export(export_preset, individual_file_path)

        elif export_preset.format_type == 'STL':
            export_preset.data_stl.export(context, export_preset, individual_file_path)


        object_transform.MoveObject(item, context, tempLoc)


def GetRootLocationDefinition(context, export_name, origin_point, root_definition):
    """
    Filters through potential origin point definitions to return a world-space location and rotation.
    """

    result = {}
    result['location'] = [0.0, 0.0, 0.0]
    result['rotation'] = [0.0, 0.0, 0.0]

    #print('AAAAAAAA')

    if origin_point == 'Scene':
        #print('origin point is SCENE')
        return result

    elif origin_point == "Object":
        #print('origin point is OBJECT')
        # Not currently needed
        # if len(targets) > 1:
        #     result['warning'] = "The '" + export_name + "' collection has no root object assigned to it.  ASSIGN ONE."
        #     return result
        
        # TODO 2.0 - Check the root_definition argument to ensure it's the type we expect.

        temp_rol = loc_utils.FindWorldSpaceObjectLocation(context, root_definition)
        result['location'] = [temp_rol[0], 
                                temp_rol[1], 
                                temp_rol[2]]
        result['rotation'] = [root_definition.rotation_euler[0], 
                                root_definition.rotation_euler[1], 
                                root_definition.rotation_euler[2]]
        
        #print('found root location : ', result['location'])
    
    return result


def GetExportSummary(stats):
    """
    Produces an export notification based on gathered statistics.
    """

    output = "Capsule exported "
    output_status = 'INFO'

    total_hide_count = stats['obj_hidden'] + stats['col_hidden']

    # If we didn't get anywhere, return early
    if stats['obj_exported'] == 0 and stats['col_exported'] == 0:
        if total_hide_count > 1:
            output_status = 'WARNING'
            output = 'All exportables were hidden from the Render and excluded for export.  Uncheck "Filter by Render Visibility" in your Export Presets or edit your scene.'
            return [output_status, output]
        else:
            output_status = 'WARNING'
            output = 'No objects were exported.  Ensure you have objects tagged for export, and at least one pass in your export presets.'
            return [output_status, output]


    # This counting wont work for future versions but for now it's oookay.
    total_exp_count = stats['obj_exported'] + stats['col_exported']
        

    if stats['obj_exported'] > 1:
        output += str(stats['obj_exported']) + " objects"
    elif stats['obj_exported'] == 1:
        output += str(stats['obj_exported']) + " object"

    if stats['obj_exported'] > 0 and stats['col_exported'] > 0:
        output += " and "
    if stats['col_exported'] > 1:
        output += str(stats['col_exported']) + " collections"
    elif stats['col_exported'] == 1:
        output += str(stats['col_exported']) + " collection"

    output += "."

    if stats['obj_exported'] > 0 and stats['col_exported'] > 0:
        output += "  "
        output += "A total of "
        output += str(total_exp_count) + " files were exported."

    
    total_hide_count = stats['obj_hidden'] + stats['col_hidden']
    if total_hide_count > 0:
        output += "  "
        if total_hide_count > 1:
            output += str(total_hide_count) + " files were not"
        else:
            output += str(total_hide_count) + " file was not"
        
        output += " exported as their contents were hidden from the Render."

    return [output_status, output]

    

