import bpy

def SearchModifiers(target, currentList):
    """
    Searches and returns a list of objects that were found as targets or that were linked 
    to any of the modifiers the target object has.
    """

    print(">>> Searching Modifiers <<<")
    print(target.name)

    object_list = []

    mod_types = {'ARRAY', 
                 'BOOLEAN', 
                 'MIRROR', 
                 'SCREW', 
                 'ARMATURE', 
                 'CAST', 
                 'CURVE', 
                 'HOOK', 
                 'LATTICE', 
                 'MESH_DEFORM', 
                 'SHRINKWRAP', 
                 'SIMPLE_DEFORM', 
                 'WARP', 
                 'WAVE'}

    # This is used to define all modifiers that share the same object location property
    mod_normal_types = {'BOOLEAN', 'SCREW', 'ARMATURE', 'CAST', 'CURVE', 'HOOK', 'LATTICE', 'MESH_DEFORM'}

    #Finds all the components in the object through modifiers that use objects
    for modifier in target.modifiers:
        if modifier.type in mod_types:
            print("Modifier Found...", modifier)

            #Normal Object Types
            if modifier.type in mod_normal_types:
                if modifier.object is not None:
                    print("Object Found In", modifier.name, ":", modifier.object.name)

                    # Find out if this object matches others in the list before adding it.
                    if (modifier.object in currentList) == False:
                        print("Object successfully added.")
                        object_list.append(modifier.object)
                        currentList.append(modifier.object)

            #Array
            elif modifier.type == 'ARRAY':
                if modifier.start_cap is not None:
                    print("Object Found In", modifier.name, ":", modifier.start_cap.name)

                    if (modifier.start_cap in currentList) == False:
                        print("Object successfully added.")
                        object_list.append(modifier.start_cap)
                        currentList.append(modifier.start_cap)

            #Mirror
            elif modifier.type == 'MIRROR':
                if modifier.mirror_object is not None:
                    print("Object Found In", modifier.name, ":", modifier.mirror_object.name)

                    if (modifier.mirror_object in currentList) == False:
                        print("Object successfully added.")
                        object_list.append(modifier.mirror_object)
                        currentList.append(modifier.mirror_object)

            #Shrinkwrap
            elif modifier.type == 'SHRINKWRAP':
                if modifier.target is not None:
                    print("Object Found In", modifier.name, ":", modifier.target.name)

                    if (modifier.target in currentList) == False:
                        print("Object successfully added.")
                        object_list.append(modifier.target)
                        currentList.append(modifier.target)

            #Simple Deform
            elif modifier.type == 'SIMPLE_DEFORM':
                if modifier.origin is not None:
                    print("Object Found In", modifier.name, ":", modifier.origin.name)

                    if (modifier.origin in currentList) == False:
                        print("Object successfully added.")
                        object_list.append(modifier.origin)
                        currentList.append(modifier.origin)

            #Warp
            elif modifier.type == 'WARP':
                if modifier.object_from is not None:
                    print("Object Found In", modifier.name, ":", modifier.object_from.name)

                    if (modifier.object_from in currentList) == False:
                        print("Object successfully added.")
                        object_list.append(modifier.object_from)
                        currentList.append(modifier.object_from)

                if modifier.object_to is not None:
                    print("Object Found In", modifier.name, ":", modifier.object_to.name)

                    if (modifier.object_to in currentList) == False:
                        print("Object successfully added.")
                        object_list.append(modifier.object_to)
                        currentList.append(modifier.object_to)

            #Wave
            elif modifier.type == 'WAVE':
                if modifier.start_position_object is not None:
                    print("Object Found In", modifier.name, ":", modifier.start_position_object.name)

                    if (modifier.start_position_object in currentList) == False:
                        print("Object successfully added.")
                        object_list.append(modifier.start_position_object)
                        currentList.append(modifier.start_position_object)


    return object_list

def SearchConstraints(target, currentList):
    """
    Searches and returns a list of objects that have been found as targets.
    """

    print(">>> Searching Constraints <<<")
    print(target.name)

    object_list = []

    con_types_target = {'COPY_LOCATION', 
                        'COPY_ROTATION', 
                        'COPY_SCALE', 
                        'COPY_TRANSFORMS', 
                        'LIMIT_DISTANCE', 
                        'TRANSFORM', 
                        'CLAMP_TO', 
                        'DAMPED_TRACK', 
                        'LOCKED_TRACK', 
                        'STRETCH_TO', 
                        'TRACK_TO', 
                        'ACTION', 
                        'FLOOR', 
                        'FOLLOW_PATH', 
                        'PIVOT', 
                        'SHRINKWRAP'}

    con_types_alt = {'RAWR'}

    for constraint in target.constraints:
        #Normal Object Types
        if constraint.type in con_types_target:
            if constraint.target is not None:
                print("Object Found In", constraint.name, ":", constraint.target.name)

                if (constraint.target in currentList) == False:
                    print("Object successfully added.")
                    object_list.append(constraint.target)
                    currentList.append(constraint.target)

    return object_list

def GetDependencies(objectList):
    """
    Searches and returns a list of all objects that the given objects are dependant on for modifiers or constraints.
    """

    print(">>> Getting Dependencies <<<")

    totalFoundList = []
    totalFoundList += objectList

    print("objectList...", objectList)

    checkedList = []
    currentList = []
    currentList += objectList

    while len(currentList) != 0:
        item = currentList.pop()
        print("Checking new objects...", item.name)

        modifierOutput = SearchModifiers(item, totalFoundList)
        constraintOutput = SearchConstraints(item, totalFoundList)

        currentList += modifierOutput
        currentList += constraintOutput

        checkedList.append(item)
        totalFoundList.append(item)

        # Parents can affect the export indirectly, so it needs to be looked at.
        if item.parent != None:
            if (item.parent in totalFoundList) is False:
                print("Parent found in", item.name, ":", item.parent.name)
                currentList.append(item.parent)

    print("Total found objects...", len(checkedList))
    print(checkedList)

    return checkedList