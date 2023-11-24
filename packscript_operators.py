import bpy

from bpy.types import Operator
from bpy.props import EnumProperty

from .tk_utils import search as search_utils
from .tk_utils import select as select_utils
from .tk_utils import object_ops
from .export_formats import CAP_ExportFormat


class CAPSULE_OT_PackScript_CreateTest(Operator):
    """This is currently a work in progress and won't work, but maybe soon?"""
    # """Copies the selected Object or Collection into a new scene and runs the Pack Script on it to show you the results, useful for writing and checking Pack Scripts before exporting with them.  NOTE - This can only be used on one Object or Collection at a time"""
    bl_idname = "cap.packscript_create_test"
    bl_label = "Test Pack Script"

    # Defines the method that a target should be tested by.  UI elements should
    # be using this depending on the context.

    # NOTE - This doesn't include a list operator mode as this operator is all about 3D View inspection.
    set_mode: EnumProperty(
        name = "Export Mode",
        items = [
            ('ACTIVE_OBJECT', "Selected", "Export the currently active object"),
            ('ACTIVE_COLLECTION', "Selected Collections", "Exports only selected collection"),
            ],
        default = 'ACTIVE_OBJECT',
        description = "Execution mode", 
        options = {'HIDDEN'},
    )

    @classmethod
    def poll(cls, context):
        
        scn = context.scene.CAPScn
        select_tab = int(str(scn.selection_switch))

        if select_tab == 1:
            if len(context.selected_objects) > 1:
                return False

        else:
            if len(search_utils.GetSelectedCollections()) > 1:
                return False
        
        return True


    def execute(self, context):
        
        preferences = context.preferences
        addon_prefs = preferences.addons[__package__].preferences
        cap_scn = context.scene.CAPScn

        target_object = None
        target_collection = None


        # ////////////////////////////////////////////
        # CLEAN PACK SCRIPT ENVIRONMENT
        # This is needed here as the test might have failed previously


        # ////////////////////////////////////////////
        # IDENTIFY TEST CANDIDATES
        targets = []

        # this is for the object tab of the 3D view menu
        if self.set_mode == 'ACTIVE_OBJECT':
            target_object = context.active_object
            targets = [target_object]

            if target_object.CAPObj.pack_script is None:
                self.report({'WARNING'}, 'The target object or collection has no Pack Script, assign one!')
                return {'FINISHED'}
            
        
        # this is for the collections tab of the 3D view menu
        elif self.set_mode == 'ACTIVE_COLLECTION':
            self.report({'WARNING'}, "Pack Script testing currently doesn't work with Collections, sorry m8.")
            return {'FINISHED'}
        
            target_collection = search_utils.GetActiveCollection()
            targets = target_collection.all_objects

            if target_collection.CAPCol.pack_script is None:
                self.report({'WARNING'}, 'The target object or collection has no Pack Script, assign one!')
                return {'FINISHED'}

        
        # ////////////////////////////////////////////
        # SEARCH DEPENDENCIES

        object_tree = search_utils.GetObjectReferenceTree(targets)

        search_utils.FindObjectDependencies(context, object_tree)
        
        # Another rudimentary test script?  idk what this is.
        # print(object_tree)
        # print([m for m in bpy.data.materials 
        #        if target_object.user_of_id(m)])
        
        duplicate = object_ops.DuplicateWithDatablocks(context, target_object, target_object.name + " CAP")


        # ////////////////////////////////////////////
        # SETUP PACK SCRIPT ENVIRONMENT
        # TODO : Ensure object + collection gathering code in export_operators can be used here.
        
        current_scene = context.scene

        bpy.ops.scene.new(type = 'NEW')
        test_scene = context.scene
        test_scene.name = "> Capsule Test Scene <"
        test_scene.CAPScn.scene_before_test = current_scene
        test_scene.CAPScn.is_pack_script_scene = True
        test_scene.CAPScn.test_pack_script = target_object.CAPObj.pack_script

        for col in duplicate.users_collection:
            current_scene.collection.objects.unlink(duplicate)
        test_scene.collection.objects.link(duplicate)

        input_collection = bpy.data.collections.new("> Pack Script Input <")
        output_collection = bpy.data.collections.new("> Pack Script Output <")
        linked_collection = bpy.data.collections.new("> Linked Objects <")

        test_scene.collection.children.link(input_collection)
        test_scene.collection.children.link(output_collection)
        test_scene.collection.children.link(linked_collection)

        input_collection.objects.link(duplicate)
        test_scene.collection.objects.unlink(duplicate)


        # ////////////////////////////////////////////
        # EXECUTE PACK SCRIPT
        export_status = context.scene.CAPStatus
        export_status.target_name = target_object.name
        export_status.target_status = 'BEFORE_EXPORT'
        export_status['target_input'] = [duplicate]
        export_status['target_output'] = []

        bpy.ops.object.select_all(action= 'DESELECT')

        code = target_object.CAPObj.pack_script.as_string()
            
        # Perform code execution in a try block to catch issues and revert the export state early.
        exec(code)

        # TODO: Find a robust way to test for type
        for item in export_status['target_output']:
            select_utils.SelectObject(item)

        for obj in export_status['target_output']:
            output_collection.objects.link(obj)



        return {'FINISHED'}


class CAPSULE_OT_PackScript_DestroyTest(Operator):
    """Fully deletes a Pack Script test scene including all datablocks contained in it"""
    bl_idname = "cap.packscript_destroy_test"
    bl_label = "Delete Test"


    def execute(self, context):

        preferences = context.preferences
        addon_prefs = preferences.addons[__package__].preferences

        test_scene = context.scene
        scene_before_test = test_scene.CAPScn.scene_before_test
        
        # ////////////////////////////////////////////////////////
        # NOTE TO SELF - KEEP CLEAN LISTS OF ALL DEPENDENCIES SO THEY CAN BE QUICKLY DESTROYED
        purge_objects = set(o.data for o in context.selected_objects if o.data)
        purge_collections = search_utils.GetSceneCollections(context.scene)

        # batch_remove is experimental and won't stop you from potentially destroying things.  Be careful!
        # ISSUE - Purging doesn't clear datablocks like Materials
        bpy.data.batch_remove(purge_objects)
        bpy.data.batch_remove(purge_collections)
        bpy.ops.scene.delete()
        context.window.scene = scene_before_test

        return {'FINISHED'}
    

class CAPSULE_OT_PackScript_RetryTest(Operator):
    """Runs the currently defined Pack Script on the Pack Script Target collection and outputs the results to the Pack Script Output collection"""
    bl_idname = "cap.packscript_retry_test"
    bl_label = "Retry Test"

    def execute(self, context):
        return {'FINISHED'}


class CAPSULE_OT_PackScript_Warning(Operator):
    """Opens a message to warn the user not to use untrusted scripts"""
    bl_idname = "scene.cap_tut_activepresets"
    bl_label = ""

    def execute(self, context):

        def tutorial_layout(self, context):
            self.layout.label(text = "Pack Scripts let you run Python scripts found in your Blend file,")
            self.layout.label(text = "PLEASE make sure the scripts you run are ones you trust.")
            self.layout.label(text = "")
            self.layout.label(text = "Check the Capsule GitHub Wiki for more information on Pack Scripts.")

        # Get the current export data
        bpy.context.window_manager.popup_menu(tutorial_layout, title="Active Export Presets", icon='HELP')


        return {'FINISHED'}