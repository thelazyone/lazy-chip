import bpy
from bpy.types import Operator

class LAZYCHIP_OT_fix_manifold(bpy.types.Operator):
    bl_idname = "lazychip.op_fixmanifold"
    bl_label = "Fix Manifold"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        for obj in context.selected_objects:
            if obj.type == 'MESH':
                context.view_layer.objects.active = obj
                self.fix_manifold(obj.data)
        return {'FINISHED'}

    def fix_manifold(self, mesh):
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.select_non_manifold()
        bpy.ops.mesh.fill_holes()
        bpy.ops.mesh.intersect(mode='SELECT', separate_mode='CUT')
        bpy.ops.object.mode_set(mode='OBJECT')

def register():
    bpy.utils.register_class(LAZYCHIP_OT_fix_manifold)

def unregister():
    bpy.utils.unregister_class(LAZYCHIP_OT_fix_manifold)
