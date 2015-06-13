import bpy, bmesh, time
from math import *

#//////////////////// - BASIC DEFINITIONS - ///////////////////////

def FocusObject(target):
    
    # If the target isnt visible, MAKE IT FUCKING VISIBLE.
    if target.hide is True:
        target.hide = False
        
    if target.hide_select is True:
        target.hide_select = False
    
    #### Select and make target active
    bpy.ops.object.select_all(action='DESELECT')  
    bpy.context.scene.objects.active = bpy.data.objects[target.name]
    bpy.ops.object.select_pattern(pattern=target.name) 
    
def SelectObject(target):
    
    # If the target isnt visible, MAKE IT FUCKING VISIBLE.
    if target.hide is True:
        target.hide = False
        
    if target.hide_select is True:
        target.hide_select = False
    
    target.select = True
    
def ActivateObject(target):
    
    # If the target isnt visible, MAKE IT FUCKING VISIBLE.
    if target.hide is True:
        target.hide = False
        
    if target.hide_select is True:
        target.hide_select = False
    
    bpy.context.scene.objects.active = bpy.data.objects[target.name]
    
def DuplicateObject(target):
    
    #### Select and make target active
    bpy.ops.object.select_all(action='DESELECT')  
    bpy.context.scene.objects.active = bpy.data.objects[target.name]
    bpy.ops.object.select_pattern(pattern=target.name)
    
    # Duplicate the object
    bpy.ops.object.duplicate_move()
    
    # Now switch the active object to the duplicate
    duplicate = bpy.context.active_object
    
    # Now set the transform details
    duplicate.rotation_euler = target.rotation_euler
    duplicate.rotation_axis_angle = target.rotation_axis_angle
    
    # To preserve the scale, it has to be applied.  Sorreh!
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    
def DeleteObject(target):
    
    # This needs proper data deletion, and all delete operations need to use this
    FocusObject(target)
    bpy.ops.object.delete()
    
    # Currently removing just in case...
    DeleteObjectByMemory(target)  
    
def DeleteObjectByMemory(target):
    
    try:
        ob = bpy.data.objects[target.name]
    
    except:
        ob = None
    
    if ob != None:
        ob.user_clear()
        bpy.data.objects.remove(ob) 
        
    return