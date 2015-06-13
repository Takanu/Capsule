import bpy, bmesh
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
        elif event.type == 'TIMER':
            print('TIMER')
            
            # ALSO, check its not a dummy or origin object
            if context.scene.objects.active.name != self.object.name:
                self.object.GXObj.collision_object = context.scene.objects.active.name
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
        
        return {'FINISHED'}



class GT_Export_Assets(Operator):
    """Updates the origin point based on the option selected, for all selected objects"""
    
    bl_idname = "scene.gx_export"
    bl_label = "Export"
    
    def ExportFBX(self, filePath, globalScale, axisForward, axisUp, bakeSpaceTransform, applyModifiers, meshSmooth):
        bpy.ops.export_scene.fbx(check_existing=False, 
        filepath=filePath, 
        filter_glob="*.fbx", 
        version='BIN7400', 
        use_selection=True, 
        global_scale=globalScale, 
        axis_forward=axisForward, 
        axis_up=axisUp, 
        bake_space_transform=bakeSpaceTransform, 
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
        bakeSpaceTransform = False
        
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
            globalScale = 0.1
            bakeSpaceTransform = True
            
            
            
        # Cycle through the available objects
        for object in context.scene.objects:
            if object.GXObj.enable_export is True:
                
                # Obtain some object-specific preferences
                applyModifiers = object.GXObj.apply_modifiers
                meshSmooth = 'EDGE'
                
                # //////////// - FILE PATH - ////////////////////////////////////////////////////////
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
                defaultFilePath = scn.path_defaults[enumIndex].path
                
                print(enumIndex)
                
                if defaultFilePath == "":
                    self.report({'WARNING'}, 'The currently highlighted file path default has no file path.  A file path is required to export.')
                    return {'FINISHED'}
                    
                if defaultFilePath.find('//') != -1:
                    self.report({'WARNING'}, 'Relative path used for the selected path default, please tick off the Relative Path option when choosing the file path.')
                    return {'FINISHED'}
                    
                objectFilePath = defaultFilePath
                objectFilePath += object.name
                objectFilePath += ".fbx"
                
                objectName = object.name
                object.name = objectName + "TEMP"
                
        
                # Duplicate the object and reset its position 
                FocusObject(object)
                DuplicateObject(context.active_object)
                context.active_object.location = [0.0, 0.0, 0.0]
                
                duplicate = context.active_object
                collision = None
                collisionFilePath = ""
                
                
                # //////////// - COLLISION SETUP - ////////////////////////////////////////////////////////
                # If collision is turned on, sort that shit out
                if object.GXObj.use_collision is True:
                    
                    # Setup the collision object
                    if object.GXObj.separate_collision is False:
                        DuplicateObject(context.active_object)
                        collision = context.active_object
                        
                        # Ensure its collidable if the user wants us to
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
                            
                            DeleteObject(duplicate)
                            object.name = objectName
                            FocusObject(object)
                            
                            return {'FINISHED'}
                            
                        DuplicateObject(context.active_object)
                        collision = context.active_object
                        
                        
                        
                    # If need be, setup the collision file path
                    if object.GXObj.export_collision is True or int(scn.engine_select) is 2:
                        collisionFilePath = defaultFilePath + objectName + "_CX" + ".fbx"
                    
                    # Out of formality and bug checking, name the collision object
                    if int(scn.engine_select) is 1:
                        collision.name = "UCX_" + objectName
                        
                    elif int(scn.engine_select) is 2:
                        collision.name = objectName + "_CX"
                        
                    
                    collision.location = [0.0, 0.0, 0.0]
                    
                # Ensure the names of both objects are in sync
                duplicate.name = objectName
                
                print("Rawr")
                print(globalScale)
                
                
                
                # //////////// - EXPORT PROCESS - ////////////////////////////////////////////////////////
                if object.GXObj.use_collision is True:
                    
                    if object.GXObj.export_collision is False and int(scn.engine_select) is not 2:
                        SelectObject(duplicate)
                        ActivateObject(collision)
                        self.ExportFBX(objectFilePath, globalScale, axisForward, axisUp, bakeSpaceTransform, applyModifiers, meshSmooth)
                        
                    else:
                        FocusObject(duplicate)
                        self.ExportFBX(objectFilePath, globalScale, axisForward, axisUp, bakeSpaceTransform, applyModifiers, meshSmooth)
                        
                        FocusObject(collision)
                        self.ExportFBX(collisionFilePath, globalScale, axisForward, axisUp, bakeSpaceTransform, applyModifiers, meshSmooth)
                        
                else:
                    FocusObject(duplicate)
                    self.ExportFBX(objectFilePath, globalScale, axisForward, axisUp, bakeSpaceTransform, applyModifiers, meshSmooth)
        
        
                # Delete all the temporary objects
                DeleteObject(duplicate)
                
                # Re-select the previous junk
                if collision is not None:
                    DeleteObject(collision)
                
                exportedObjects += 1
                
                # Correct the names
                object.name = objectName
                
                
        # Re-select the objects previously selected
        for sel in selected:
            SelectObject(sel)
            
        SelectObject(active)
        ActivateObject(active)
        
        text1 = "Finished exporting "
        text2Single = " object."
        text2Multiple = " objects."
        
        outputTextSingle = text1 + str(exportedObjects) + text2Single
        outputTextMultiple = text1 + str(exportedObjects) + text2Multiple
        
        # Output a nice report
        if exportedObjects == 0:
            self.report({'WARNING'}, 'No objects were exported.  Ensure any objects tagged for exporting are enabled.')
            
        elif exportedObjects == 1:
            self.report({'INFO'}, outputTextSingle)
            
        else:
            self.report({'INFO'}, outputTextMultiple)
            
            
        return {'FINISHED'}
        
        