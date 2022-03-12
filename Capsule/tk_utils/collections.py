import bpy


def GetActiveCollection():
    """
    Used when Capsule needs the "most important" active collection in the scene.
    """
    
    collection = bpy.context.view_layer.active_layer_collection.collection
    if collection != None:
        return collection
    
    return None

def GetSceneCollections(scene, hasObjects):
    """
    Returns all collections that belong to the scene, by searching through all objects belonging in it.
    """

    # TODO - There 100% is a more efficient way of doing this

    collections = []

    for item in scene.objects:
        for collection in item.users_collection:
            collection_added = False

            for found_collection in collections:
                if found_collection.name == collection.name:
                    collection_added = True

            if hasObjects is False or len(collection.objects) > 0:
                if collection_added == False:
                    collections.append(collection)

    return collections


def GetEditableCollections(context):
    """
    Finds collections that can have their values edited.
    """
    collected = [] 

    # TODO - Reintroduce multiple collections at some point
    collection = bpy.context.view_layer.active_layer_collection.collection
    if collection != None:
        if collection.CAPCol.enable_edit is True:
            collected.append(collection)


    return collected

def GetSelectedObjectCollections():
    """
    Returns a unique list of all collections that belong to the currently selected objects.
    """
    collections_found = []

    # TODO - Reintroduce multiple collections at some point
    collection = bpy.context.view_layer.active_layer_collection.collection
    if collection != None:
        collections_found.append(collection)

    return collections_found


def GetExportableCollectionObjects(context, collection, child_export_option):
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