
import bpy, bmesh, os, platform, sys

from datetime import datetime
from mathutils import Vector
from math import pi, radians, degrees

from bpy.types import Operator
from bpy.props import EnumProperty

from .tk_utils import search as search_utils
from .tk_utils import select as select_utils
from .tk_utils import locations as loc_utils
from .tk_utils import object_ops
from .tk_utils import object_transform
from .tk_utils import paths as path_utils
from .tk_utils import record as record_utils

from . import tag_ops



class CAPSULE_OT_Export(Operator):
    """Exports objects and collections in the scene."""

    bl_idname = "scene.cap_export"
    bl_label = "Export All"

    # This is important, pay attention :eyes:
    set_mode: EnumProperty(
        name = "Export Mode",
        items = [
            ('ALL', "All Active", "Exports everything in the scene"),
            ('SELECTED_ALL', "Selected", "Exports only selected objects and collections"),
            ('SELECTED_OBJECTS', "Selected Objects", "Exports only selected object"),
            ('SELECTED_COLLECTIONS', "Selected Collections", "Exports only selected collection"),
            ('ACTIVE_LIST', "Active List", "Exports the active list selection")
            ],
        default = 'ALL',
        description = "Execution mode", 
        options = {'HIDDEN'},
    )

    def execute(self, context):
        
        preferences = context.preferences
        addon_prefs = preferences.addons[__package__].preferences
        cap_scn = context.scene.CAPScn
        cap_file = None

        # /////////////////////////////////////////////////
        # FETCH

        # Fetch objects and collections for export
        # (fetching MUST be done first to preserve selection data)

        print('>> EXPORT OPERATOR <<')

        export_objects = []
        export_collections = []

        if self.set_mode == 'ALL':
            for object in context.scene.objects:
                if object.CAPObj.enable_export is True:
                    export_objects.append(object)
            
            for collection in search_utils.GetSceneCollections(context.scene, False):
                if collection.CAPCol.enable_export is True:
                    export_collections.append(collection)
        
        # this is for the pie menu!
        elif self.set_mode == 'SELECTED_ALL':
            for object in context.selected_objects:
                if object.CAPObj.enable_export is True:
                    export_objects.append(object)
            
            for collection in search_utils.GetSelectedCollections():
                if collection.CAPCol.enable_export is True:
                    export_collections.append(collection)
        
        # this is for the object tab of the 3D view menu
        elif self.set_mode == 'SELECTED_OBJECTS':
            for object in context.selected_objects:
                if object.CAPObj.enable_export is True:
                    export_objects.append(object)
        
        # this is for the collections tab of the 3D view menu
        elif self.set_mode == 'SELECTED_COLLECTIONS':
            for collection in search_utils.GetSelectedCollections():
                if collection.CAPCol.enable_export is True:
                    export_collections.append(collection)
        
        # this is for the list menu
        elif self.set_mode == 'ACTIVE_LIST':
            list_tab = int(str(cap_scn.list_switch))

            if list_tab == 1:
                index = cap_scn.object_list_index
                export_objects.append(cap_scn.object_list[index].object)

            elif list_tab == 2:
                index = cap_scn.collection_list_index
                export_collections.append(cap_scn.collection_list[index].collection)

        
        # print(export_objects)
        # print(export_collections)


        # /////////////////////////////////////////////////
        # SETUP
    
        # For the new pie menu, we need to see if any data exists before continuing
        try:
            cap_file = bpy.data.objects[addon_prefs.default_datablock].CAPFile
        except KeyError:
            self.report({'WARNING'}, "No Capsule Data for this blend file exists.  Please create it using the Toolshelf or Addon Preferences menu.")
            return {'FINISHED'}

        # Make a record of the scene before we do anything
        global_record = record_utils.BuildSceneContext(context)

        # We need to make a separate definition set for preserving and restoring scene data.
        result = record_utils.CheckCapsuleErrors(context)

        if result is not None:
            record_utils.RestoreSceneContext(context, global_record)
            self.report({'WARNING'}, result)
            return {'FINISHED'}
        

        # Set export counts here
        export_stats = {}
        # export_stats['expected_export_quantity'] = 0
        export_stats['obj_exported'] = 0
        export_stats['col_exported'] = 0
        total_exp_count = 0
        
        # get the current time for later
        global_record['export_time'] = datetime.now()


        # /////////////////////////////////////////////////
        # EXPORT TASK PROCESSING

        object_export_result = BuildObjectExportTasks(context, cap_file, export_objects, global_record)
        collection_export_result = BuildCollectionExportTasks(context, cap_file, export_collections, global_record)

        export_tasks = object_export_result[0] + collection_export_result[0]
        col_list_result = collection_export_result[1]
        object_list_result = object_export_result[1]
        
        export_stats['obj_exported'] = object_list_result['export_count']
        export_stats['obj_hidden'] = object_list_result['export_hidden']
        export_stats['col_exported'] = col_list_result['export_count']
        export_stats['col_hidden'] = col_list_result['export_hidden']
        

        # /////////////////////////////////////////////////
        # EXPORT TASKS

        for export_task in export_tasks:

            GetExportTaskDirectory(context, export_task)
            PerformExportTask(context, export_task)


        # /////////////////////////////////////////////////
        # EXPORT SUMMARY  

        export_info = GetExportSummary(export_stats)
        self.report({export_info[0]}, export_info[1])


        record_utils.RestoreSceneContext(context, global_record)

        return {'FINISHED'}



def BuildObjectExportTasks(context, cap_file, object_list, global_record):
    """
    Builds an initial list of export tasks given a list of objects, allowing export tasks
    to contain additional data and be modified as needed.

    This is separated to allow test functions to use the same sorting and preparation
    systems as the main export function.

    Returns a list of export tasks and some statistics.
    """

    result = {}
    result['export_count'] = 0
    result['export_hidden'] = 0

    export_tasks = []

    for item in object_list:
        export_task = {}
        export_task['export_start_time'] = datetime.now()

        # Get the export preset for the object
        export_preset_index = int(item.CAPObj.export_preset) - 1
        export_preset = cap_file.export_presets[export_preset_index]

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


        # SUCCESSFUL INCLUSION
        export_task['export_name'] = item.name
        export_task['export_preset'] = export_preset
        export_task['targets'] = [item]
        location_preset_index = int(item.CAPObj.location_preset) - 1
        export_task['location_preset'] = cap_file.location_presets[location_preset_index]

        export_task['origin_object'] = None
        if item.CAPObj.origin_point == 'Object':
            export_task['origin_object'] = item

        export_task['pack_script'] = item.CAPObj.pack_script
        
        # Add to stack and increment stats
        export_tasks.append(export_task)
        result['export_count'] += 1
    
    return [export_tasks, result]


def BuildCollectionExportTasks(context, cap_file, collection_list, global_record):
    """
    Builds an initial list of export tasks given a list of objects, allowing export tasks
    to contain additional data and be modified as needed.

    This is separated to allow test functions to use the same sorting and preparation
    systems as the main export function.

    Returns a list of export tasks and some statistics.
    """

    result = {}
    result['export_count'] = 0
    result['export_hidden'] = 0

    export_tasks = []
    
    for collection in collection_list:
        export_task = {}
        export_task['export_start_time'] = datetime.now()

        # Get the export default for the object
        export_preset_index = int(collection.CAPCol.export_preset) - 1
        export_preset = cap_file.export_presets[export_preset_index]

        # Collect all objects that are applicable for this export
        child_export_option = collection.CAPCol.child_export_option
        targets = search_utils.GetCollectionObjectTree(context, collection, child_export_option)

        
        # TODO : Find an efficient way to filter out objects that have rendering turned off by the collections they're in.
        # Filter by rendering
        if export_preset.filter_by_rendering is True:
            renderable = []

            for target in targets:
                object_hidden = False

                if target.hide_render is True:
                    object_hidden = True

                else:
                    for render_search_col in target.users_collection:
                        if render_search_col.hide_render is True:
                            object_hidden = True
                            break
                
                if object_hidden == False:
                    renderable.append(target)
            
            targets = renderable
            # print("Filtered Export Targets = ", targets)

        # If our targets list is empty this collection shouldn't be included.
        if len(targets) == 0:
            result['export_hidden'] += 1
            continue

        
        # SUCCESSFUL INCLUSION
        export_task['export_name'] = collection.name
        export_task['export_preset'] = export_preset
        export_task['targets'] = targets

        location_preset_index = int(collection.CAPCol.location_preset) - 1
        export_task['location_preset'] = cap_file.location_presets[location_preset_index]

        export_task['origin_object'] = None
        if collection.CAPCol.origin_point == 'Object':
            export_task['origin_object'] = bpy.context.scene.objects.get(collection.CAPCol.root_object.name)

        export_task['pack_script'] = collection.CAPCol.pack_script

        # Add to stack and increment stats
        export_tasks.append(export_task)
        result['export_count'] += 1
    
    return [export_tasks, result]


def GetExportTaskDirectory(context, export_task):
    """
    Gets and sets the file path using information in the export task.
    """
    preferences = context.preferences
    addon_prefs = preferences.addons[__package__].preferences

    export_directory = path_utils.CreateFilePath(export_task["location_preset"], export_task["targets"], 
        None, addon_prefs.substitute_directories, export_task)

    if addon_prefs.substitute_directories is True:
        export_task['export_name'] = path_utils.SubstituteNameCharacters(export_task['export_name'])

    export_task['export_directory'] = export_directory



def PerformExportTask(context, export_task):
    """
    Exports a selection of objects into a single file.
    """

    print('>> FINALIZE EXPORT <<')

    # TODO: This should really be shared in some manner.
    cap_scn = context.scene.CAPScn
    preferences = context.preferences
    addon_prefs = preferences.addons[__package__].preferences

    # Unpack key export task values
    export_preset = export_task['export_preset']
    pack_script = export_task['pack_script']


    # ////////////////////////////////
    # SETUP SCENE

    # TODO 1.2 : Is this needed anymore?
    if export_preset.preserve_armature_constraints == True:
        export_task['armature_record'] = record_utils.MuteArmatureConstraints(context)

    origin_location = {}
    if export_task["origin_object"] is not None:

        export_task["origin_object_loc"] = GetOriginObjectLocation(context, export_task['export_name'], export_task['origin_object'])
        object_transform.MoveAllFailsafe(context, export_task["origin_object"], [0.0, 0.0, 0.0])
    

    # ////////////////////////////////
    # PACK SCRIPT INTRO

    export_status = context.scene.CAPStatus
    export_status.target_name = export_task['export_name']
    export_status.target_status = 'BEFORE_EXPORT'
    export_status['target_input'] = export_task['targets']
    export_status['target_output'] = []

    bpy.ops.object.select_all(action= 'DESELECT')

    if addon_prefs.use_pack_scripts is True and pack_script is not None:
        code = pack_script.as_string()
        
        # Perform code execution in a try block to catch issues and revert the export state early.
        try:
            exec(code)
        except Exception as e:
            message = getattr(e, 'message', repr(e))
            
            # Undo scene state changes.
            EmergencySceneRestore(context, export_task)

            # Raise the exception
            raise Exception("Pack Script Error for", export_task['export_name'],
                " ", message)


        if len(export_status['target_output']) == 0:
            return "A Pack Script used provided no target objects to export."

        # TODO: Find a robust way to test for type
        for item in export_status['target_output']:
            select_utils.SelectObject(item)

    else:
        for item in export_task['targets']:
            #print("Exporting: ", item.name)
            select_utils.SelectObject(item)

    object_file_path = export_task['export_directory'] + export_task['export_name']


    # ////////////////////////////////
    # EXPORT ! ! ! 

    # based on the export location, send it to the right place
    if export_preset.format_type == 'FBX':
        export_preset.data_fbx.export(export_preset, object_file_path)

    elif export_preset.format_type == 'OBJ':
        export_preset.data_obj.export(export_preset, object_file_path)

    elif export_preset.format_type == 'GLTF':
        export_preset.data_gltf.export(context, export_preset, 
            export_task['export_directory'], export_task['export_name'])

    elif export_preset.format_type == 'Alembic':
        export_preset.data_abc.export(context, export_preset, object_file_path)

    elif export_preset.format_type == 'Collada':
        export_preset.data_dae.export(export_preset, object_file_path)
    
    elif export_preset.format_type == 'STL':
        export_preset.data_stl.export(context, export_preset, object_file_path)

    elif export_preset.format_type == 'USD':
        export_preset.data_usd.export(context, export_preset, object_file_path)


    # ////////////////////////////////
    # PACK SCRIPT OUTRO

    export_status = context.scene.CAPStatus
    export_status.target_name = export_task['export_name']
    export_status.target_status = 'AFTER_EXPORT'

    if addon_prefs.use_pack_scripts is True and export_task['pack_script'] is not None:
        code = pack_script.as_string()
        exec(code)

    # Reset the Export Status state
    export_status = context.scene.CAPStatus
    export_status.target_name = ""
    export_status.target_status = 'NONE'
    export_status['target_input'] = []
    export_status['target_output'] = []


    # /////////////////////////////////////////////////
    # RESTORE SCENE

    # Reverse movement and rotation
    if export_task["origin_object"] is not None:
        object_transform.MoveAllFailsafe(context, export_task["origin_object"], 
            export_task["origin_object_loc"]['location'])

    # Cleans up any armature constraint modification (only works if Preserve Armature Constraints is off)
    if export_preset.preserve_armature_constraints == True:
        record_utils.RestoreArmatureConstraints(context, export_task["armature_record"])



def EmergencySceneRestore(context, export_task):
    """
    Restores the scene assuming the worst state conditions (such as a pack script failure), attempting
    to avoid as many context issues as possible.
    """

    preferences = context.preferences
    addon_prefs = preferences.addons[__package__].preferences

    export_status = context.scene.CAPStatus
    export_status.target_name = export_task['export_name']
    export_status.target_status = 'AFTER_EXPORT'

    # Reset the Export Status state
    export_status = context.scene.CAPStatus
    export_status.target_name = ""
    export_status.target_status = 'NONE'
    export_status['target_input'] = []
    export_status['target_output'] = []


    # /////////////////////////////////////////////////
    # RESTORE SCENE

    # Reverse movement and rotation
    if export_task["origin_object"] is not None:
        object_transform.MoveAllFailsafe(context, export_task["origin_object"], 
            export_task["origin_object_loc"]['location'])

    # Cleans up any armature constraint modification (only works if Preserve Armature Constraints is off)
    if export_task['export_preset'].preserve_armature_constraints == True:
        record_utils.RestoreArmatureConstraints(context, export_task['armature_record'])



def GetOriginObjectLocation(context, export_name, origin_target):
    """
    Filters through potential origin point definitions to return a world-space location and rotation
    for a given export.
    """

    result = {}
    result['location'] = [0.0, 0.0, 0.0]
    result['rotation'] = [0.0, 0.0, 0.0]

    # TODO - Does this need changing in any substantial way?

    temp_rol = loc_utils.FindWorldSpaceObjectLocation(context, origin_target)
    result['location'] = [temp_rol[0], 
                            temp_rol[1], 
                            temp_rol[2]]
    result['rotation'] = [origin_target.rotation_euler[0], 
                            origin_target.rotation_euler[1], 
                            origin_target.rotation_euler[2]]
    
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

    

