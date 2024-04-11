bl_info = {
    "name": "Pose",
    "author": "thelazyone",
    "version": (1, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > Lazy Tools",
    "description": "Utils to simplify posing",
    "warning": "",
    "wiki_url": "",
    "category": "Mesh",
}

import bpy
from bpy.types import Operator, Panel
from mathutils import Vector, Matrix

class OBJECT_OT_set_local_z_to_view(Operator):
    bl_idname = "object.set_local_z_to_view"
    bl_label = "Set Local Z to View"
    bl_description = "Sets the object's local Z-axis to align with the current view direction, without changing its global orientation"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type == 'MESH'
    

    def execute(self, context):
        obj = context.active_object

        # Calculate the target view direction, negated to align forwards
        view_direction = context.region_data.view_rotation @ Vector((0.0, 0.0, -1.0))

        # Compute the rotation matrix needed to align the local Z to the view direction
        # This is the current rotation matrix of the object
        align_matrix = obj.rotation_euler.to_matrix().to_4x4()

        # Local Z in world coordinates is the third column of the rotation matrix
        local_z_world = align_matrix @ Vector((0.0, 0.0, 1.0))

        # Find the rotation difference needed to align the local Z with the view direction
        rotation_difference = view_direction.rotation_difference(local_z_world).to_matrix().to_4x4()
        new_matrix = rotation_difference @ align_matrix

        # Convert the rotation difference to a matrix and apply it to the object
        obj.rotation_euler = new_matrix.to_euler()

        # Apply this rotation locally
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)

        # Immediately apply the inverse rotation to revert to the original orientation
        inverse_rotation_matrix = rotation_difference.to_4x4().inverted()
        obj.matrix_world = obj.matrix_world @ inverse_rotation_matrix

        return {'FINISHED'}


class OBJECT_PT_set_local_z_to_view(Panel):
    bl_label = "Set Local Z to View"
    bl_idname = "OBJECT_PT_set_local_z_to_view"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Lazy Tools'
    bl_context = "objectmode"

    def draw(self, context):
        layout = self.layout
        layout.operator(OBJECT_OT_set_local_z_to_view.bl_idname)

def register():
    bpy.utils.register_class(OBJECT_OT_set_local_z_to_view)
    bpy.utils.register_class(OBJECT_PT_set_local_z_to_view)

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_set_local_z_to_view)
    bpy.utils.unregister_class(OBJECT_PT_set_local_z_to_view)

if __name__ == "__main__":
    register()