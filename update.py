import bpy, bmesh, time
from .definitions import SelectObject, FocusObject, ActivateObject
from math import *

def Update_EnableExport(self, context):

    # Acts as its own switch to prevent endless recursion
    if self == context.active_object.GXObj:

        # Keep a record of the selected objects to update
        selected = []

        for sel in context.selected_objects:
            if sel.name != context.active_object.name:
                selected.append(sel)

        # Obtain the value changed
        enableExport = self.enable_export

        # Run through the objects
        for object in selected:
            object.GXObj.enable_export = enableExport

    return None

def Update_ApplyModifiers(self, context):

    # Acts as its own switch to prevent endless recursion
    if self == context.active_object.GXObj:

        # Keep a record of the selected objects to update
        selected = []

        for sel in context.selected_objects:
            if sel.name != context.active_object.name:
                selected.append(sel)

        # Obtain the value changed
        value = self.apply_modifiers

        # Run through the objects
        for object in selected:
            object.GXObj.apply_modifiers = value

    return None

def Update_Triangulate(self, context):

    # Acts as its own switch to prevent endless recursion
    if self == context.active_object.GXObj:

        # Keep a record of the selected objects to update
        selected = []

        for sel in context.selected_objects:
            if sel.name != context.active_object.name:
                selected.append(sel)

        # Obtain the value changed
        value = self.triangulate

        # Run through the objects
        for object in selected:
            object.GXObj.triangulate = value

    return None

def Update_UseCollision(self, context):

    # Acts as its own switch to prevent endless recursion
    if self == context.active_object.GXObj:

        # Keep a record of the selected objects to update
        selected = []

        for sel in context.selected_objects:
            if sel.name != context.active_object.name:
                selected.append(sel)

        # Obtain the value changed
        value = self.use_collision

        # Run through the objects
        for object in selected:
            object.GXObj.use_collision = value

    return None

def Update_GenerateConvex(self, context):

    # Acts as its own switch to prevent endless recursion
    if self == context.active_object.GXObj:

        # Keep a record of the selected objects to update
        selected = []

        for sel in context.selected_objects:
            if sel.name != context.active_object.name:
                selected.append(sel)

        # Obtain the value changed
        value = self.generate_convex

        # Run through the objects
        for object in selected:
            object.GXObj.generate_convex = value


    return None

def Update_SeparateCollision(self, context):

    # Acts as its own switch to prevent endless recursion
    if self == context.active_object.GXObj:

        # Keep a record of the selected objects to update
        selected = []

        for sel in context.selected_objects:
            if sel.name != context.active_object.name:
                selected.append(sel)

        # Obtain the value changed
        value = self.separate_collision

        # Run through the objects
        for object in selected:
            object.GXObj.separate_collision = value

    return None

def Update_ExportCollision(self, context):

    # Acts as its own switch to prevent endless recursion
    if self == context.active_object.GXObj:

        # Keep a record of the selected objects to update
        selected = []

        for sel in context.selected_objects:
            if sel.name != context.active_object.name:
                selected.append(sel)

        # Obtain the value changed
        value = self.export_collision

        # Run through the objects
        for object in selected:
            object.GXObj.export_collision = value

    return None

def Update_CollisionObject(self, context):

    # Acts as its own switch to prevent endless recursion
    if self == context.active_object.GXObj:

        # Keep a record of the selected objects to update
        selected = []

        for sel in context.selected_objects:
            if sel.name != context.active_object.name:
                selected.append(sel)

        # Obtain the value changed
        value = self.collision_object

        # Run through the objects
        for object in selected:
            object.GXObj.collision_object = value

    return None

def Update_LocationDefault(self, context):

    # Acts as its own switch to prevent endless recursion
    if self == context.active_object.GXObj:

        # Keep a record of the selected objects to update
        selected = []

        for sel in context.selected_objects:
            if sel.name != context.active_object.name:
                selected.append(sel)

        # Obtain the value changed
        value = self.location_default

        # Run through the objects
        for object in selected:
            object.GXObj.location_default = value

    return None


def Update_ExportAnim(self, context):

    # Acts as its own switch to prevent endless recursion
    if self == context.active_object.GXObj:

        # Keep a record of the selected objects to update
        selected = []

        for sel in context.selected_objects:
            if sel.name != context.active_object.name:
                selected.append(sel)

        # Obtain the value changed
        value = self.export_anim

        # Run through the objects
        for object in selected:
            object.GXObj.export_anim = value

    return None

def Update_ExportAnimFile(self, context):

    # Acts as its own switch to prevent endless recursion
    if self == context.active_object.GXObj:

        # Keep a record of the selected objects to update
        selected = []

        for sel in context.selected_objects:
            if sel.name != context.active_object.name:
                selected.append(sel)

        # Obtain the value changed
        value = self.export_anim_file

        # Run through the objects
        for object in selected:
            object.GXObj.export_anim_file = value

    return None

def Update_ExportAnimActions(self, context):

    # Acts as its own switch to prevent endless recursion
    if self == context.active_object.GXObj:

        # Keep a record of the selected objects to update
        selected = []

        for sel in context.selected_objects:
            if sel.name != context.active_object.name:
                selected.append(sel)

        # Obtain the value changed
        value = self.export_anim_actions

        # Run through the objects
        for object in selected:
            object.GXObj.export_anim_actions = value

    return None
