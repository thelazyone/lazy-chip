bl_info = {
    "name": "Lazy Z Flattener",
    "author": "Giacomo Pantalone + GPT4",
    "version": (0, 1),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > Lazy Tools",
    "description": "Crops meshes along the Z axis",
    "category": "Mesh",
}

import bpy
from bpy.types import Operator, Panel
from bpy.props import FloatProperty
import math
import bmesh


class ZFlattenerSettings(bpy.types.PropertyGroup):
    z_level: FloatProperty(
        name="Z coordinate",
        description="The Z value to flatten the vertices to",
        default=0.0,
    )

class MESH_flatten_vertices(Panel):
    bl_idname = "LazyFlattening"
    bl_label = "Lazy Flattening"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Lazy Tools'
    bl_context = "objectmode"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type == 'MESH'

    def draw(self, context):
        layout = self.layout
        settings = context.scene.z_flattener_settings
        layout.prop(settings, "z_level", text="Z coordinate")
        layout.operator(MESH_OT_flatten_vertices.bl_idname)
        

class MESH_OT_flatten_vertices(Operator):
    bl_idname = "mesh.flatten_vertices"
    bl_label = "Flatten Vertices"
    bl_description = "Split faces along the Z=0 plane, remove vertices below Z=0, and fill the area"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type == 'MESH'

    def execute(self, context):
        obj = context.active_object
        mesh = obj.data

        # Store the object's location
        original_location = obj.location.copy()

        # Move the object to the world origin
        obj.location = (0, 0, 0)

        # Enter edit mode
        bpy.ops.object.mode_set(mode='EDIT')

        # Bisect along Z=0 plane
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.bisect(plane_co=(0, 0, 0), plane_no=(0, 0, 1), use_fill=True)

        # Remove vertices below Z=-0.001
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT')
        for v in mesh.vertices:
            if v.co.z < -0.001:
                v.select = True
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.delete(type='VERT')

        # Separate disconnected parts of the mesh
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.separate(type='LOOSE')

        # Return to object mode
        bpy.ops.object.mode_set(mode='OBJECT')

        # Process each island separately
        for separated_obj in context.selected_objects:
            if separated_obj != obj:
                bpy.context.view_layer.objects.active = separated_obj

                # Enter edit mode
                bpy.ops.object.mode_set(mode='EDIT')

                # Fill the area
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.mesh.region_to_loop()
                bpy.ops.object.mode_set(mode='OBJECT')

                # Create a custom function to connect vertices within a threshold distance
                def connect_vertices_within_threshold(obj, threshold):
                    mesh = obj.data
                    bm = bmesh.new()
                    bm.from_mesh(mesh)

                    # Find vertices on Z = 0 plane
                    z0_vertices = [v for v in bm.verts if abs(v.co.z) < 0.001]

                    # Connect vertices within the threshold distance
                    connected = set()
                    for v1 in z0_vertices:
                        for v2 in z0_vertices:
                            if v1 != v2 and (v1, v2) not in connected and (v2, v1) not in connected:
                                if (v1.co - v2.co).length < threshold:
                                    connected.add((v1, v2))
                                    bmesh.ops.connect_verts(bm, verts=[v1, v2])

                    # Update the mesh
                    bm.to_mesh(mesh)
                    bm.free()

                # Call the custom function for the active object
                connect_vertices_within_threshold(separated_obj, 0.1)

                # Return to object mode
                bpy.ops.object.mode_set(mode='OBJECT')
                
        # Restore the original object's location
        obj.location = original_location

        return {'FINISHED'}


def register():
    bpy.utils.register_class(MESH_OT_flatten_vertices)
    bpy.utils.register_class(MESH_flatten_vertices)
    bpy.utils.register_class(ZFlattenerSettings)

    bpy.types.Scene.z_flattener_settings = bpy.props.PointerProperty(type=ZFlattenerSettings)

def unregister():
    bpy.utils.register_class(MESH_OT_flatten_vertices)
    bpy.utils.register_class(MESH_flatten_vertices)
    bpy.utils.unregister_class(ZFlattenerSettings)

    del bpy.types.Scene.z_flattener_settings


if __name__ == "__main__":
    register()