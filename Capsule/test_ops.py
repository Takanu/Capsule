import bpy
from bpy.types import Operator
class CAP_TestDuplicate(Operator):
    """A test for duplicating objects while avoiding ghost animation data."""

    bl_idname = "testcap.duplicate"
    bl_label = "Test Duplication"

    def execute(self, context):
        print("="*100)
        print("New Test")
        print("="*100)
        print(" "*100)

        sel = context.selected_objects
        for item in sel:
            print("+"*40)
            print(item.name)

            if item.animation_data is not None:
                a_d = item.animation_data
                print(a_d.nla_tracks)
                print(a_d.action)
                print(a_d.drivers)
                print("-"*40)

                for track in a_d.nla_tracks:
                    print(track.name)

        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.duplicate(linked=False, mode='INIT')

        context.active_object.animation_data.action.user_clear()

        return {'FINISHED'}
