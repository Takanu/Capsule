import bpy

# Should help me avoid the bus issue.
def AddParent(child, parent):
    """
    Adds a parent to the given object, preserving translation in the process.
    """
    # I now have to add the cursor stuff here too, just in case...
    cursor_loc = bpy.data.scenes[bpy.context.scene.name].cursor_location
    previous_cursor_loc = [cursor_loc[0], cursor_loc[1], cursor_loc[2]]
    FocusObject(child)
    bpy.ops.view3D.snap_cursor_to_selected()

    bpy.ops.object.select_all(action='DESELECT')

    SelectObject(parent)
    SelectObject(child)

    bpy.context.scene.objects.active = parent

    bpy.ops.object.parent_set()

    # Now move the object
    FocusObject(child)
    bpy.ops.view3D.snap_selected_to_cursor()
    bpy.data.scenes[bpy.context.scene.name].cursor_location = previous_cursor_loc

def ClearParent(child):
    """
    Clears the parent from the given object, preserving it's translation in the process.
    """

    # Prepare the 3D cursor so it can keep the object in it's current location
    # After it stops being a component
    cursor_loc = bpy.data.scenes[bpy.context.scene.name].cursor_location
    previous_cursor_loc = [cursor_loc[0], cursor_loc[1], cursor_loc[2]]

    # Save the transform matrix before de-parenting
    matrixcopy = child.matrix_world.copy()

    # Move the cursor to the selected object
    FocusObject(child)
    bpy.ops.view3D.snap_cursor_to_selected()

    # Clear the parent
    bpy.ops.object.select_all(action='DESELECT')
    SelectObject(child)
    bpy.ops.object.parent_clear()

    # Now move the object
    bpy.ops.view3D.snap_selected_to_cursor()

    # Restore the original cursor location and matrix
    bpy.data.scenes[bpy.context.scene.name].cursor_location = previous_cursor_loc
    child.matrix_world = matrixcopy