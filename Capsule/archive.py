# This is code I might need later but don't right now.

# From export_operators.py
# ///////////////////////////////////////////

def StartSceneMovement(self, context, target, targetObjects, targetRot):
    """
    Moves the focus of the export to the desired location, performing any preparation work as needed.
    """

    if self.origin_point is "Object":
        #print("Moving scene...")
        object_transform.MoveAll_TEST(target, context, [0.0, 0.0, 0.0], self.region_override)

def FinishSceneMovement(self, context, target, targetObjects, targetLoc, targetRot):
    """
    Moves the focus of the export back from the desired location, after the export is complete.
    """

    if self.origin_point is "Object":
        object_transform.MoveAll_TEST(self.root_object, context, targetLoc, self.region_override)
