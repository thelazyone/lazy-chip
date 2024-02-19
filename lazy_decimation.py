bl_info = {
    "name": "Experimental Remesh and Fix",
    "author": "thelazyone",
    "version": (1, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > Lazy Tools",
    "description": "Decimate and crops meshes",
    "warning": "",
    "wiki_url": "",
    "category": "Mesh",
}

import bpy
from bpy.types import Operator, Panel
from bpy.props import FloatProperty
import math
import bmesh


def check_non_manifold(mesh):
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.mesh.select_non_manifold()
    bpy.ops.object.mode_set(mode='OBJECT')
    return any(v.select for v in mesh.vertices)


def fix_non_manifold(mesh):
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.mesh.select_non_manifold()
    bpy.ops.mesh.fill_holes()
    bpy.ops.mesh.intersect(mode='SELECT', separate_mode='CUT')
    bpy.ops.object.mode_set(mode='OBJECT')
    
class DecimateAndFixSettings(bpy.types.PropertyGroup):
    decimate_ratio: FloatProperty(
        name="Decimate Ratio",
        description="Decimate ratio for the modifier",
        min=0.01,
        max=0.5,
        default=0.1,
    )

class MESH_OT_decimate_and_fix(Operator):
    bl_idname = "mesh.decimate_and_fix"
    bl_label = "Decimate and Fix"
    bl_description = "Automates the process of adding a Decimate modifier, applying it, and fixing non-manifold geometry"

    decimate_ratio: FloatProperty(
        name="Decimate Ratio",
        description="Decimate ratio for the modifier",
        min=0.01,
        max=0.5,
        default=0.1,
    )

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type == 'MESH'
        
    def invoke(self, context, event):
        return self.execute(context)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "decimate_ratio", text="Decimate Ratio")

    def execute(self, context):
        objects = context.selected_objects
        total_objects = len(objects)
        settings = context.scene.decimate_and_fix_settings

        for index, obj in enumerate(objects, start=1):
            if obj.type != 'MESH':
                continue  # Skip non-mesh objects

            self.report({'INFO'}, f"Processing object {index}/{total_objects}: {obj.name}")

            mesh = obj.data

            # Add and apply Decimate modifier
            modifier = obj.modifiers.new(name="Decimate", type='DECIMATE')
            modifier.ratio = settings.decimate_ratio
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.modifier_apply(modifier="Decimate")
            
            # Fix non-manifold geometry if necessary
            if check_non_manifold(mesh):
                self.report({'INFO'}, f"Fixing non-manifold geometry in {obj.name}")
                fix_non_manifold(mesh)

        self.report({'INFO'}, "Finished processing all objects")

        return {'FINISHED'}


class MESH_PT_decimate_and_fix(Panel):
    bl_idname = "LazyDecimation"
    bl_label = "Lazy Decimation"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Lazy Tools'
    bl_context = "objectmode"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type == 'MESH'

    def draw(self, context):
        layout = self.layout
        layout.operator(MESH_OT_decimate_and_fix.bl_idname)

        settings = context.scene.decimate_and_fix_settings
        layout.prop(settings, "decimate_ratio", text="Decimate Ratio")
        
        

def register():
    bpy.utils.register_class(MESH_OT_decimate_and_fix)
    bpy.utils.register_class(MESH_PT_decimate_and_fix)
    bpy.utils.register_class(DecimateAndFixSettings)

    bpy.types.Scene.decimate_and_fix_settings = bpy.props.PointerProperty(type=DecimateAndFixSettings)

def unregister():
    bpy.utils.unregister_class(MESH_OT_decimate_and_fix)
    bpy.utils.unregister_class(MESH_PT_decimate_and_fix)
    bpy.utils.unregister_class(DecimateAndFixSettings)

    del bpy.types.Scene.decimate_and_fix_settings


if __name__ == "__main__":
    register()