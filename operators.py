import bpy
from bpy.types import Operator
from .definitions import SelectObject, FocusObject, ActivateObject, DuplicateObject, DeleteObject

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


class GT_Export_Assets(Operator):
    """Updates the origin point based on the option selected, for all selected objects"""
    
    bl_idname = "scene.gx_export"
    bl_label = "Export"
    
    def execute(self, context):
        print(self)
        
        scn = context.scene.GXScn
        obj = context.active_object.GXObj
        
        exportedObjects = 0
        
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
        
        # Assign custom properties based on the export target
        if int(scn.engine_select) is 1:
            axisForward = "-Z"
            axisUp = "Y"
            
            if scn._scale_100x is True:
                globalScale = 100.0
                
            else:
                globalScale = 1.0
            
        elif int(scn.engine_select) is 2:
            axisForward = "-Z"
            axisUp = "Y"
            globalScale = 1.0
            
        # Cycle through the available objects
        for object in context.scene.objects:
            if object.GXObj.enable_export is True:
                
                # Obtain some object-specific preferences
                applyModifiers = object.GXObj.apply_modifiers
                meshSmooth = 'EDGE'
                
                # Get the file extension.  If the index is incorrect (as in, the user didnt set the fucking path)
                enumIndex = int(object.GXObj.location_default)
                
                print(obj.location_default)
                print(object.GXObj.location_default)
                print(int(obj.location_default))
                print(int(object.GXObj.location_default))
                print(enumIndex)
                
                if enumIndex == 0:
                    FocusObject(object)
                    self.report({'WARNING'}, 'The selected object has no set file path default.  Set it plzplzplz.')
                    return {'FINISHED'}
                
                enumIndex -= 1
                filePath = scn.path_defaults[enumIndex].path
                
                print(enumIndex)
                
                if filePath == "":
                    self.report({'WARNING'}, 'The currently highlighted file path default has no file path.  A file path is required to export.')
                    return {'FINISHED'}
                    
                if filePath.find('//') != -1:
                    self.report({'WARNING'}, 'Relative path used for the selected path default, please tick off the Relative Path option when choosing the file path.')
                    return {'FINISHED'}
            
                filePath += object.name
                filePath += ".fbx"
                
                objectName = object.name
                object.name = objectName + "TEMP"
        
                # Duplicate the object and reset its position 
                FocusObject(object)
                DuplicateObject(context.active_object)
                context.active_object.location = [0.0, 0.0, 0.0]
                
                duplicate = context.active_object
                collision = None
                
                # If collision is turned on, sort that shit out
                if object.GXObj.export_collision is True:
                    DuplicateObject(context.active_object)
                    collision = context.active_object
                    
                    if int(scn.engine_select) is 1:
                        collision.name = "UCX_" + objectName
                        context.active_object.location = [0.0, 0.0, 0.0]
                    
                    SelectObject(duplicate)
                    ActivateObject(collision)
                    
                # Ensure the names of both objects are in sync
                duplicate.name = objectName
                
                # Export them!
                bpy.ops.export_scene.fbx(check_existing=False, 
                filepath=filePath, 
                filter_glob="*.fbx", 
                version='BIN7400', 
                use_selection=True, 
                global_scale=globalScale, 
                axis_forward=axisForward, 
                axis_up=axisUp, 
                bake_space_transform=False, 
                object_types={'EMPTY', 'ARMATURE', 'LAMP', 'CAMERA', 'MESH'}, 
                use_mesh_modifiers=applyModifiers, 
                mesh_smooth_type=meshSmooth, 
                use_mesh_edges=False,
                use_tspace=False, 
                use_armature_deform_only=False, 
                bake_anim=False, 
                bake_anim_use_nla_strips=False, 
                bake_anim_step=1.0, 
                bake_anim_simplify_factor=1.0, 
                use_anim=True, 
                use_anim_action_all=True, 
                use_default_take=True, 
                use_anim_optimize=True, 
                anim_optimize_precision=6.0, 
                path_mode='AUTO', 
                embed_textures=False, 
                batch_mode='OFF', 
                use_batch_own_dir=False, 
                use_metadata=False)
        
                # Delete all the temporary objects
                DeleteObject(duplicate)
                
                if collision is not None:
                    DeleteObject(collision)
                
                exportedObjects += 1
                
                # Correct the names
                object.name = objectName
                
        # Re-select the objects previously selected
        for sel in selected:
            SelectObject(sel)
        
        ActivateObject(active)
        
        text1 = "Finished exporting "
        text2 = " objects."
        
        outputText = text1 + str(exportedObjects) + text2
        
        # Output a nice report
        if exportedObjects == 0:
            self.report({'WARNING'}, 'No objects were exported.  Ensure any objects tagged for exporting are enabled.')
            
        else:
            self.report({'WARNING'}, outputText)
            
            
        return {'FINISHED'}
        
        