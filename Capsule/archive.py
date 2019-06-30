# This is code I might need later but don't right now.

# From export_operators.py
# ///////////////////////////////////////////

def StartSceneMovement(self, context, target, targetObjects, targetRot):
    """
    Moves the focus of the export to the desired location, performing any preparation work as needed.
    """

    # FIXME: WHY IS THIS HERE?

    # /////////// - OBJECT MOVEMENT - ///////////////////////////////////////////////////
    # ///////////////////////////////////////////////////////////////////////////////////
    #self.forwardRotations = []
    #self.reverseRotations = []

    # We need to record rotations in case they need to be restored
    # for when Unity completely destroys them <3
    #for item in targetObjects:
        #forwardRot = (item.rotation_euler[0], item.rotation_euler[1], item.rotation_euler[2])
        #reverseRot = (-item.rotation_euler[0], -item.rotation_euler[1], -item.rotation_euler[2])
        #print("COLLECTING ROTATIONS...", forwardRot)
        #self.forwardRotations.append(forwardRot)
        #self.reverseRotations.append(reverseRot)

    # was removed since 1.01 due to unknown bugs and issues... *spooky*

    # If the user wanted to reset the rotation, time to add more
    # annoying levels of complexity to the mix and reset the rotation!
    #if self.reset_rotation is True:
        #print("Reset Rotation active, resetting rotations!")
        #reverseRotation = (-targetRot[0], -targetRot[1], -targetRot[2])
        #RotateAllSafe(target, context, reverseRotation, False)

    # If the user wanted unity, time to stomp on the rotation
    # only the objects being exported should be applied

    # might be fixed in 2.79, remove for now.

    # if self.x_unity_rotation_fix is True:

    #     print("Unity rotation fix active!")
    #     object_transform.RotateAllSafe(target, context, (radians(-90), 0, 0), True)
    #     bpy.ops.object.select_all(action='DESELECT')

    #     for item in targetObjects:
    #         SelectObject(item)
    #         ActivateObject(item)

    #     bpy.ops.object.transform_apply(
    #         location=False,
    #         rotation=True,
    #         scale=False
    #         )
    #     RotateAllSafe(target, context, (radians(90), 0, 0), True)

    if self.origin_point is "Object":
        print("Moving scene...")
        object_transform.MoveAll_TEST(target, context, [0.0, 0.0, 0.0], self.region_override)

def FinishSceneMovement(self, context, target, targetObjects, targetLoc, targetRot):
    """
    Moves the focus of the export back from the desired location, after the export is complete.
    """

    # was removed since 1.01 due to unknown bugs and issues... *spooky*
    # if self.reset_rotation is True:
    #     object_transform.RotateAllSafe(self.root_object, context, targetRot, True)

    if self.origin_point is "Object":
        object_transform.MoveAll_TEST(self.root_object, context, targetLoc, self.region_override)

    # since Blender 2.79 + Unity 2017.3, this is no longer needed.
    # if self.export_preset.format_type == 'FBX':
    #     if self.export_preset.data_fbx.x_unity_rotation_fix is True:
    #         bpy.ops.object.select_all(action='DESELECT')

    #         for item in targetObjects:
    #             select_utils.SelectObject(item)
    #             select_utils.ActivateObject(item)
    #         bpy.ops.object.transform_apply(
    #             location=False,
    #             rotation=True,
    #             scale=False
    #             )

            #for i, item in enumerate(targetObjects):
                #RotateObjectSafe(item, context, self.reverseRotations[i], False)

            #bpy.ops.object.select_all(action='DESELECT')
            #for item in targetObjects:
                #SelectObject(item)
                #ActivateObject(item)
            #bpy.ops.object.transform_apply(
                #location=False,
                #rotation=True,
                #scale=False
                #)

            #for i, item in enumerate(targetObjects):
                #RotateObjectSafe(item, context, self.forwardRotations[i], True)