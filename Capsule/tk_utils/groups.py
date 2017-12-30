import bpy

def GetSceneGroups(scene, hasObjects):
    """
    Returns all groups that belong to the scene, by searching through all objects belonging in it.
    """
    groups = []

    for item in scene.objects:
        for group in item.users_group:
            groupAdded = False

            for found_group in groups:
                if found_group.name == group.name:
                    groupAdded = True

            if hasObjects is False or len(group.objects) > 0:
                if groupAdded == False:
                    groups.append(group)

    return groups

def GetObjectGroups(objects):
    """
    Returns a unique list of all groups that belong to the given object list,
    by searching through all objects belonging in it.
    """
    groups_found = []
    groups_found.append(currentGroup)

    for item in objects:
        for group in item.users_group:
            groupAdded = False

            for found_group in groups_found:
                if found_group.name == group.name:
                    groupAdded = True

            if groupAdded == False:
                groups_found.append(group)

    return groups_found