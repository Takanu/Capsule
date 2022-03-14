
# ///////////////////////////////////////////////////////////////////
# Gathers collections of important datablocks or properties.
# ///////////////////////////////////////////////////////////////////

import bpy

# batfinger you legend
def TraverseCollectionTree(t):
    """
    Returns a list from a recursive search
    """
    yield t
    for child in t.children:
        yield from TraverseCollectionTree(child)


def GetActiveCollection():
    """
    Used when Capsule needs the "most important" active collection in the scene.
    """

    # TODO: Not sure if I ever need to verify if it equals none or not
    return bpy.context.layer_collection.collection


def GetSceneCollections(scene, hasObjects = False):
    """
    Returns all collections that belong to the scene, by searching through all objects belonging in it.
    """

    # batfinger is too good at this
    collections = [
        c for c in bpy.data.collections 
        if bpy.context.scene.user_of_id(c) and
        (hasObjects is False or len(c.objects) > 0)
    ]

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

    # TODO: Unable to get the selected IDs in the Outliner as of Blender 3.1
    # try again layer!
    # outliner_ids = []
    # for area in context.screen.areas:
    #     if area.type == 'OUTLINER':
    #         outliner_ids = bpy.context.selected_ids
    #         print(outliner_ids)
    #         bpy.ops.outliner.id_copy()
    
    # As of 3.1 there is always an active_object, but never always selected_objects
    # There is ALWAYS a layer_collection
    # print(context.layer_collection)
    # print(context.active_object)
    # print(context.selected_objects)

    # If no objects are selected it means we can disregard the active object and just use the collection
    if len(context.selected_objects) == 0:
        collections_found.append(context.layer_collection.collection)

     # Otherwise fetch every collection in every selected object.
    else:
        for obj in context.selected_objects:
            for col in obj.users_collection:
                # print(col in collections_found)
                # print(bpy.context.scene.user_of_id(col))
                if bpy.context.scene.user_of_id(col):
                    if col not in collections_found:
                        # print("winner")
                        collections_found.append(col)

    #print(collections_found)
    return collections_found


def GetCollectionObjectTree(context, collection, child_export_option):
    """
    Returns a list of objects that can be exported by the given collection, based on it's child settings.
    """

    # TODO: Ensure that somewhere in our export chain if Filter by Render Visibility is used,
    # that only objects where the parent collection is not hidden will be exported.

    # Now setup the recursive tree search.
    def ExportTreeSearch(current_layer, max_layer, current_collection):

        object_list = []
        
        # If we've over-extended, return
        if current_layer > max_layer and max_layer != -1:
            return []
            
        # If not, add the current objects
        object_list += current_collection.objects

        # Now search further
        for new_collection in current_collection.children:
            new_objects = ExportTreeSearch(current_layer + 1, max_layer, new_collection)
            object_list += new_objects
        
        return object_list


    object_list = []

    if child_export_option == "All":
        object_list += collection.all_objects
        return object_list
    
    elif child_export_option == "Immediate":
        object_list += collection.objects
        return object_list

    # If we get here, we need to search and cancel by layers.  First get the layer max.
    max_layers = 0
    if child_export_option == "Down 1":
        max_layers = 1
    if child_export_option == "Down 2":
        max_layers = 2
    if child_export_option == "Down 3":
        max_layers = 3
    if child_export_option == "Down 4":
        max_layers = 4
    if child_export_option == "Down 5":
        max_layers = 5

    
    object_list = ExportTreeSearch(0, max_layers, collection)
    return object_list