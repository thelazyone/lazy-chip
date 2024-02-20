import bpy
from bpy.types import Operator, Panel, PropertyGroup
from bpy.props import IntProperty, FloatProperty, PointerProperty, BoolProperty
import math
import bmesh
from mathutils.bvhtree import BVHTree
from mathutils import Vector

bl_info = {
    "name": "Smart Decimation",
    "author": "thelazyone",
    "version": (1, 0, 3),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > Lazy Tools",
    "description": "Decimate meshes with extra checks.",
    "warning": "",
    "wiki_url": "",
    "category": "Mesh",
}

def relax_intersecting_faces(obj, iterations=3, relaxation_strength=0.5):
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    bm = bmesh.from_edit_mesh(obj.data)
    bm.verts.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    
    # Create a BVH tree and find intersecting pairs
    bvh = BVHTree.FromBMesh(bm)
    intersecting_pairs = bvh.overlap(bvh)
    
    # Extract vertices from intersecting faces
    vertices_to_relax = set()
    for pair in intersecting_pairs:
        face1, face2 = pair
        for face in [bm.faces[face1], bm.faces[face2]]:
            for vert in face.verts:
                vertices_to_relax.add(vert)
    
    # Relaxation process
    for _ in range(iterations):
        for vert in vertices_to_relax:
            avg_pos = Vector((0, 0, 0))
            for edge in vert.link_edges:
                other_vert = edge.other_vert(vert)
                avg_pos += other_vert.co
            avg_pos /= len(vert.link_edges)
            
            # Move the vertex towards the average position of connected vertices
            vert.co = vert.co.lerp(avg_pos, relaxation_strength)
    
    bmesh.update_edit_mesh(obj.data)
    bpy.ops.object.mode_set(mode='OBJECT')

def fix_intersections_and_recalculate_normals(obj):
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    
    # Recalculate outside normals
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.normals_make_consistent(inside=False)
    
    # Fix intersecting faces
    bpy.ops.mesh.intersect_boolean(operation='UNION')
    
    bpy.ops.object.mode_set(mode='OBJECT')

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

def delete_small_islands(obj, threshold=100):
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    # Make sure we're in object mode
    bpy.ops.object.mode_set(mode='OBJECT')

    # Separate by loose parts
    bpy.ops.mesh.separate(type='LOOSE')
    bpy.context.view_layer.update()  # Ensure the scene is updated

    # Temporarily store the original object's name to avoid renaming issues
    original_name = obj.name

    # Collect objects to delete based on face count threshold
    objects_to_delete = [o for o in bpy.context.selected_objects if len(o.data.polygons) < threshold]

    # Delete objects
    for obj_to_delete in objects_to_delete:
        bpy.data.objects.remove(obj_to_delete, do_unlink=True)

    # Re-select the remaining objects for joining
    for obj in bpy.context.view_layer.objects:
        if obj.name.startswith(original_name):
            obj.select_set(True)
        else:
            obj.select_set(False)

    # Make sure there's more than one object selected for join operation
    if len(bpy.context.selected_objects) > 1:
        bpy.ops.object.join()  # Join the remaining objects

    # Optionally, rename the joined object to the original name
    bpy.context.view_layer.objects.active.name = original_name


class DecimateAndFixSettings(bpy.types.PropertyGroup):
    decimate_ratio: FloatProperty(
        name="Decimate Ratio",
        description="Decimate ratio for the modifier",
        min=0.01,
        max=1.0,
        default=0.1,
    )
    fix_non_manifold: BoolProperty(
        name="Fix Non-Manifold",
        description="Automatically fix non-manifold issues",
        default=True,
    )
    fix_intersections: BoolProperty(
        name="Fix Intersections",
        description="Automatically fix intersecting faces",
        default=True,
    )


class MESH_OT_decimate_and_fix(Operator):
    bl_idname = "mesh.decimate_and_fix"
    bl_label = "Smart Decimation"
    bl_description = "Automates the process of adding a Decimate modifier, applying it, and fixing mesh issues"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type == 'MESH'
        
    def invoke(self, context, event):
        return self.execute(context)

    def execute(self, context):
        objects = context.selected_objects
        total_objects = len(objects)
        settings = context.scene.decimate_and_fix_settings

        for index, obj in enumerate(objects, start=1):
            if obj.type != 'MESH':
                continue

            self.report({'INFO'}, f"Processing object {index}/{total_objects}: {obj.name}")
            mesh = obj.data
            
            # Save current selection mode
            original_select_mode = context.tool_settings.mesh_select_mode[:]
            
            # Ensure we're in object mode to apply modifiers
            bpy.ops.object.mode_set(mode='OBJECT')

            # Add and apply Decimate modifier
            modifier = obj.modifiers.new(name="Decimate", type='DECIMATE')
            modifier.ratio = settings.decimate_ratio
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.modifier_apply(modifier="Decimate")

            # Switch to vertex select mode for operations
            bpy.ops.object.mode_set(mode='EDIT')
            context.tool_settings.mesh_select_mode = (True, False, False)
            
            # Fix non-manifold geometry if necessary
            if settings.fix_non_manifold:
                fix_non_manifold(mesh)
            
            # Fix intersecting faces and recalculate normals if enabled
            if settings.fix_intersections:
                fix_intersections_and_recalculate_normals(obj)
                relax_intersecting_faces(obj)
                delete_small_islands(obj)

            # Restore original selection mode
            context.tool_settings.mesh_select_mode = original_select_mode
            bpy.ops.object.mode_set(mode='OBJECT')            

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
        settings = context.scene.decimate_and_fix_settings
        layout.prop(settings, "decimate_ratio")
        layout.prop(settings, "fix_non_manifold")
        layout.prop(settings, "remove_doubles")
        layout.prop(settings, "fill_holes")
        layout.prop(settings, "fix_intersections")
        layout.prop(settings, "recalculate_normals")
        layout.operator(MESH_OT_decimate_and_fix.bl_idname)

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