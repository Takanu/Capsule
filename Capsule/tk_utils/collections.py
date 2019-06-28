import bpy

def GetSceneCollections(scene, hasObjects):
    """
    Returns all collections that belong to the scene, by searching through all objects belonging in it.
    """

    # FIXME - There has to be a more efficient way of doing this...

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

    for item in context.selected_objects:
        for new_collection in item.users_collection: 
            
            if new_collection.CAPCol.enable_edit is False:
                continue

            collection_added = False

            for added_group in collected:
                if added_group.name == new_collection.name:
                    collection_added = True

            if collection_added == False:
                collected.append(new_collection)

    return collected

def GetObjectCollections(objects):
    """
    Returns a unique list of all collections that belong to the given object list,
    by searching through all objects belonging in it.
    """
    collections_found = []
    collections_found.append(currentGroup)

    for item in objects:
        for collection in item.users_collection:
            collection_added = False

            for found_collection in collections_found:
                if found_collection.name == collection.name:
                    collection_added = True

            if collection_added == False:
                collections_found.append(collection)

    return collections_found

def GetSelectedObjectCollections():
    """
    Returns a unique list of all collections that belong to the currently selected objects.
    """
    collections_found = []

    for item in bpy.context.selected_objects:
        for collection in item.users_collection:
            collection_added = False

            for found_collection in collections_found:
                if found_collection.name == collection.name:
                    collection_added = True

            if collection_added == False:
                collections_found.append(collection)

    return collections_found