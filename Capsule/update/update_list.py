import bpy
from math import *

from ..tk_utils import select as select_utils
from ..tk_utils import object_ops

# OBJECT LIST PROPERTIES
# /////////////////////////////////////////////////
# /////////////////////////////////////////////////


def UpdateObjectList(scene, object, enableExport):
    """
    Used when properties are updated outside the scope of the Export List
    to ensure that all UI elements are kept in sync.
    """
    scn = scene.CAPScn
    #print("Hey, this object is %s" % object)

    if object is None:
        return

    # Check a list entry for the object doesn't already exist.
    for item in scene.CAPScn.object_list:
        if item.object.name == object.name:
            #print("Changing", object.name, "'s export from list.'")
            item.enable_export = enableExport
            return

    # If an entry couldn't be found in the list, add it.
    if enableExport is True:
        #print("Adding", object.name, "to list.")
        entry = scn.object_list.add()
        entry.object = object
        entry.enable_export = enableExport

        object.CAPObj.in_export_list = True

    return None

def CAP_Update_FocusObject(self, context):
    """
    Focuses the camera to a particular object, ensuring the object is clearly within the camera frame.  
    """

    preferences = context.preferences
    addon_prefs = preferences.addons['Capsule'].preferences
            
    bpy.ops.object.select_all(action= 'DESELECT')
    select_utils.SelectObject(self.object)

    override = object_ops.Find3DViewContext()
    
    with context.temp_override(window = override['window'], area = override['area'], 
            region = override['region']):

            bpy.ops.view3d.view_selected()

    return None


def CAP_Update_SelectObject(self, context):
    """
    Selects (but doesn't focus) the given object.
    """

    bpy.ops.object.select_all(action= 'DESELECT')
    select_utils.ActivateObject(self.object)
    select_utils.SelectObject(self.object)

    return None



def CAP_Update_ObjectListExport(self, context):
    """
    Updates the "Enable Export" object status once changed from the list menu.
    Note - Do not use this in any other place apart from when an object is represented in a list.
    """

    self.object.CAPObj.enable_export = self.enable_export
    
    # TODO / WARNING
    # If the object is the active selection we should really change the proxy so it fits right?
    proxy = context.scene.CAPProxy



    return None


def CAP_Update_ObjectListRemove(self, context):
    """
    Used in a list to remove an object from both the export list, while disabling it's "Enable Export" status.
    """
    
    scn = context.scene.CAPScn
    object_list = context.scene.CAPScn.object_list

    # To avoid issues within the list, the selected list item needs to be preserved.
    backupListIndex = scn.object_list_index
    backupListLength = len(object_list)

    # TODO: Ensure it can handle deleted objects!

    # Remove it as an export candidate
    if self.object != None:
        self.object.CAPObj.enable_export = False
        self.object.CAPObj.in_export_list = False
    
    # Find the index and remove it from the list
    # TODO: There's probably a more efficient way right?
    i = None
    try:
        i = object_list.values().index(self)
        object_list.remove(i)

    except ValueError:
        return
    
    # If the index is more than the list, bring it down one
    if scn.object_list_index > i:
        scn.object_list_index -= 1

    return
                

            


# COLLECTION LIST PROPERTIES
# /////////////////////////////////////////////////
# /////////////////////////////////////////////////

def UpdateCollectionList(scene, collection, enableExport):
    """
    Used when properties are updated outside the scope of the Export List
    to ensure that all UI elements are kept in sync.
    """
    scn = scene.CAPScn

    # Check a list entry for the collection doesn't already exist.

    for item in scene.CAPScn.collection_list:
        if item:
            if item.collection:
                if item.collection.name == collection.name:
                    #print("Changing", collection.name, "'s export from list.'")
                    item.enable_export = enableExport
                    return

    if enableExport is True:
        #print("Adding", collection.name, "to list.")
        entry = scn.collection_list.add()
        entry.collection = collection
        entry.enable_export = enableExport
        collection.CAPCol.in_export_list = True


def CAP_Update_FocusCollection(self, context):

    """
    Focuses the camera to a particular collection, moving it to ensure all objects are in the frame and can be seen clearly.
    TODO 2.0: The camera movement interpolation no longer works.
    """
    bpy.ops.object.select_all(action= 'DESELECT')

    for object in self.collection.objects:
        object.select_set(True)
        bpy.context.view_layer.objects.active = object

    override = object_ops.Find3DViewContext()
    
    with context.temp_override(window = override['window'], area = override['area'], 
            region = override['region']):

            bpy.ops.view3d.view_selected()

    return None

def CAP_Update_SelectCollection(self, context):

    """
    Selects (but doesn't focus) the given collection.
    """
    bpy.ops.object.select_all(action= 'DESELECT')

    for object in self.collection.objects:
        object.select_set(True)
        bpy.context.view_layer.objects.active = object

    return None


def CAP_Update_CollectionListExport(self, context):
    """
    Updates the "Enable Export" collection status once changed from the list menu.
    Note - Do not use this in any other place apart from when an object is represented in a list.
    """

    self.collection.CAPCol.enable_export = self.enable_export
    return None


def CAP_Update_CollectionListRemove(self, context):
    """
    Used in a list to remove a collection from both the export list, while disabling it's "Enable Export" status.
    """

    print(self)
    
    i = 0
    scn = context.scene.CAPScn
    # To avoid issues within the list, the selected list item needs to be preserved.
    backupListIndex = scn.collection_list_index
    backupListLength = len(scn.collection_list)

    # If the list item is dead, remove it now and forget about the rest.
    # if self is None or self.collection is None:


    for item in scn.collection_list:
        if item.collection is not None:
            if item.collection.name == self.collection.name:

                self.collection.CAPCol.enable_export = False
                self.collection.CAPCol.in_export_list = False

                # Whether or not we find a successful match in the scene,
                # remove it from the list
                context.scene.CAPScn.collection_list.remove(i)

                # If the index is more than the list, bring it down one
                # to ensure a list item gets selected
                scn.collection_list_index = i

                if i == (backupListLength - 1):
                    scn.collection_list_index = i - 1

                return

            i += 1