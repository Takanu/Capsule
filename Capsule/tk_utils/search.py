
# ///////////////////////////////////////////////////////////////////
# Gathers collections of important datablocks or properties.
# ///////////////////////////////////////////////////////////////////

from re import L
import bpy

# batfinger you legend
def TraverseCollectionTree(t):
    """
    Returns a list from a recursive search
    """
    yield t
    for child in t.children:
        yield from TraverseCollectionTree(child)


def GetSceneCollections(scene, hasObjects = False):
    """
    Returns all collections that belong to the scene, by searching through all objects belonging in it.
    """

    # batfinger is too good at this
    #print(bpy.data.collections)
    collections = [
        c for c in bpy.data.collections 
        if bpy.context.scene.user_of_id(c) and
        (hasObjects is False or len(c.objects) > 0)
    ]

    # bpy.data.collections does not include the top-level collection so we need to include it separately.
    # TODO: Re-enable when the top-level collection scene issue is fixed.
    # if hasObjects is False or len(scene.collection.objects > 0):
    #     collections.insert(0, scene.collection)
    

    return collections


def GetEditableCollections(context):
    """
    Finds collections that can have their values edited for the 
    purposes of Selection Menu editing.
    """

    editables = []
    collections = GetSelectedCollections()

    editables = [
        c for c in collections
        if c.CAPCol.enable_edit is True
    ]

    return editables

def GetActiveCollection():
    """
    Used when Capsule needs the "most important" active collection in the scene.
    """

    context = bpy.context
    scene = context.scene
    layer_col_selection = context.layer_collection.collection

    # The active collection can either be the selection in the outliner
    # OR it can be based on the active object.  Oh No!
    # THIS BEHAVIOUR MUST MATCH GETSELECTEDCOLLECTIONS()
    
    if len(context.selected_objects) == 0:
        # TODO: Remove this check when the top-level collection can be used again
        if scene.collection != layer_col_selection:
            return layer_col_selection

    else:
        active_obj = context.active_object
        target_col = None
        
        if active_obj is not None:
            if layer_col_selection in active_obj.users_collection:
                target_col = layer_col_selection
                
            elif len(active_obj.users_collection):
                target_col = active_obj.users_collection[0]

            if target_col:
                if scene.collection != layer_col_selection:
                    return target_col

            return None

    return bpy.context.layer_collection.collection

def GetSelectedCollections():
    """
    Returns a unique list of all collections that belong to the currently selected objects.

    This should ONLY BE USED FOR SELECTION EDITING.
    """
    # Neither of these work
    # https://devtalk.blender.org/t/get-list-of-selected-collections-in-outliner/17276/2
    # https://blender.stackexchange.com/questions/203729/python-get-selected-objects-in-outliner

    collections_found = []
    context = bpy.context
    scene = context.scene

    # TODO: Unable to get the selected IDs in the Outliner as of Blender 3.1
    # try again layer!
    # outliner_ids = []
    # for area in context.screen.areas:
    #     if area.type == 'OUTLINER':
    #         outliner_ids = bpy.context.selected_ids
    #         print(outliner_ids)
    #         bpy.ops.outliner.id_copy()

    # If no objects are selected it means we can disregard the active object and just use the collection
    if len(context.selected_objects) == 0:
        layer_col_selection = context.layer_collection.collection
        
        # TODO: Remove this check when the top-level collection can be used again
        if scene.collection != layer_col_selection:
            collections_found.append(layer_col_selection)

     # Otherwise fetch every collection in every selected object.
    else:
        for obj in context.selected_objects:
            for col in obj.users_collection:
                
                # TODO: Remove the scene collection check when the top-level collection can be used again
                verified = (scene.user_of_id(col) 
                    and scene.collection != col)

                if verified and col not in collections_found:
                        # print("winner")
                        collections_found.append(col)

    #print(collections_found)
    return collections_found

def GetObjectParentTree(context, target_obj, object_children):
    """
    Returns a list of objects that can be exported by the given object, based on it's child settings.
    """
    # Now setup the recursive tree search.
    def ExportTreeSearch(current_layer, max_layer, current_obj):

        object_list = []
        
        # If we've over-extended, return
        if current_layer >= max_layer and max_layer != -1:
            return []
            
        # If not, add the current objects
        object_list += current_obj.children

        # Now search further
        for new_obj in current_obj.children:
            new_objects = ExportTreeSearch(current_layer + 1, max_layer, new_obj)
            object_list += new_objects
        
        return object_list

    object_list = []

    if object_children == "All":
        object_list += target_obj.children_recursive
        return object_list

    elif object_children == "None":
        return object_list

    # If we get here, we need to search and cancel by layers.  First get the layer max.
    max_layers = 0
    if object_children == "Down 1":
        max_layers = 1
    elif object_children == "Down 2":
        max_layers = 2
    elif object_children == "Down 3":
        max_layers = 3
    elif object_children == "Down 4":
        max_layers = 4
    elif object_children == "Down 5":
        max_layers = 5


    object_list = ExportTreeSearch(0, max_layers, target_obj)
    return object_list



def GetCollectionObjectTree(context, collection, collection_children):
    """
    Returns a list of objects that can be exported by the given collection, based on it's child settings.
    """

    # TODO: Ensure that somewhere in our export chain if Filter by Render Visibility is used,
    # that only objects where the parent collection is not hidden will be exported.

    # Now setup the recursive tree search.
    def ExportTreeSearch(current_layer, max_layer, current_collection):

        object_list = []
        
        # If we've over-extended, return
        if current_layer >= max_layer and max_layer != -1:
            return []
            
        # If not, add the current objects
        object_list += current_collection.objects

        # Now search further
        for new_collection in current_collection.children:
            new_objects = ExportTreeSearch(current_layer + 1, max_layer, new_collection)
            object_list += new_objects
        
        return object_list


    object_list = []

    if collection_children == "All":
        object_list += collection.all_objects
        return object_list
    
    elif collection_children == "None":
        object_list += collection.objects
        return object_list

    # If we get here, we need to search and cancel by layers.  First get the layer max.
    max_layers = 0
    if collection_children == "Down 1":
        max_layers = 1
    if collection_children == "Down 2":
        max_layers = 2
    if collection_children == "Down 3":
        max_layers = 3
    if collection_children == "Down 4":
        max_layers = 4
    if collection_children == "Down 5":
        max_layers = 5

    
    object_list = ExportTreeSearch(0, max_layers, collection)
    return object_list