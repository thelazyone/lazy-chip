import bpy
from bpy.types import Operator, Panel, PropertyGroup
from bpy.props import IntProperty, FloatProperty, PointerProperty, BoolProperty
import math
import bmesh
from mathutils.bvhtree import BVHTree
from mathutils import Vector

import random
from math import radians

bl_info = {
    "name": "Smart Cracks",
    "author": "thelazyone",
    "version": (1, 0, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > Lazy Tools",
    "description": "Apply volumetric cracks with infill",
    "warning": "",
    "wiki_url": "",
    "category": "Mesh",
}

class crack_settings(bpy.types.PropertyGroup):
    fill_crack: bpy.props.BoolProperty(name="Fill Crack", default=False)
    noise_scale: bpy.props.FloatProperty(name="Noise Scale", default=2.5, min=0.1, max=10.0)
    thickness: bpy.props.FloatProperty(name="Thickness", default=0.005, min=0.001, max=0.1)
    noise_intensity: bpy.props.FloatProperty(name="Noise Intensity", default=1.0, min=0.1, max=10.0)


class operator_crack(Operator):
    bl_idname = "mesh.crack"
    bl_label = "Crack Volumes"
    bl_description = "Performs a volumetric crack on a given volume with infill"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type == 'MESH'
    
    def modal(self, context, event):
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.editmode_toggle()

        # Moving the mouse handles the displacement
        if event.type == 'MOUSEMOVE':
            self.displace_cracker(context, event.mouse_x - self.mouse_x, event.mouse_y - self.mouse_y)
            self.mouse_x, self.mouse_y = event.mouse_x, event.mouse_y
        
        # Mouse wheel handles the rotation of the crack
        elif event.type == 'WHEELUPMOUSE' or event.type == 'WHEELDOWNMOUSE':  # Handle rotation
            self.rotate_cracker(context, event.type)

        # Click or enter simply applies the modal operator
        elif event.type in {'RET', 'NUMPAD_ENTER', 'LEFTMOUSE'}:  # Apply crack
            if self.apply_crack(context):
                return {'FINISHED'}
            else:
                return {'CANCELLED'}
        elif event.type in {'RIGHTMOUSE', 'ESC'}:  # Cancel operation
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

        
    def invoke(self, context, event):
        self.mouse_x, self.mouse_y = event.mouse_x, event.mouse_y
        self.create_cracker(context)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}
    
    def create_cracker(self, context):

        # Ensure the texture exists before using it
        if "cracker_texture" not in bpy.data.textures:
            cracker_texture = bpy.data.textures.new(name="cracker_texture", type='CLOUDS')
            cracker_texture.noise_basis = 'BLENDER_ORIGINAL'
            cracker_texture.noise_scale = 2.5
        else:
            cracker_texture = bpy.data.textures["cracker_texture"]
            
        # Store target obj
        targetName = bpy.context.object.name
        targetObj = bpy.data.objects[targetName]

        dimx = bpy.context.object.dimensions.x
        dimy = bpy.context.object.dimensions.y
        dimz = bpy.context.object.dimensions.z

        dimensions = (dimx, dimy, dimz)
        dimMax = max(dimensions)
        randomLoc = random.uniform(dimMax/-4, dimMax/4)

        locX = bpy.data.objects[targetName].location[0] + randomLoc/2
        locY = bpy.data.objects[targetName].location[1] 
        locZ = bpy.data.objects[targetName].location[2] + randomLoc/2

        crackerLoc = (locX, locY, locZ)
        crackerRot = math.pi * random.uniform(-30, 30)

        # empty creation
        bpy.ops.object.empty_add(type='PLAIN_AXES', align='VIEW', location=(crackerLoc))
        bpy.context.object.name = "cracker_empty"
        bpy.ops.object.hide_view_set(unselected=False)

        # Cracker obj creation
        bpy.ops.mesh.primitive_plane_add(size=dimMax*2.5, enter_editmode=False, align='VIEW',location = (crackerLoc), scale=(1, 1, 1))
        bpy.context.object.rotation_euler[0] += 1.5708
        bpy.context.object.rotation_euler.rotate_axis('Y', radians(crackerRot))

        bpy.ops.object.shade_smooth()
        bpy.ops.object.hide_view_set(unselected=False)

        bpy.context.object.name = "cracker"
        crackerName = bpy.context.object.name
        crackerObj = bpy.data.objects["cracker"]
        crackerEmpty = bpy.data.objects["cracker_empty"]

        crackerObj.parent = crackerEmpty
        crackerObj.matrix_parent_inverse = crackerEmpty.matrix_world.inverted()

        bpy.data.objects[crackerName].modifiers.new("Cracker_Subd", type='SUBSURF')
        bpy.data.objects[crackerName].modifiers["Cracker_Subd"].subdivision_type = 'SIMPLE'
        bpy.data.objects[crackerName].modifiers["Cracker_Subd"].levels = 5

        bpy.data.objects[targetName].modifiers.new("cracker", type='BOOLEAN')
        bpy.data.objects[targetName].modifiers["cracker"].solver = 'FAST'
        bpy.data.objects[targetName].modifiers["cracker"].object = crackerObj
        bpy.data.objects[targetName].modifiers["cracker"].operation = 'DIFFERENCE'

        bpy.data.objects['cracker'].modifiers.new("Cracker_Bend", type='SIMPLE_DEFORM')
        bpy.data.objects['cracker'].modifiers["Cracker_Bend"].deform_method = 'BEND'
        bpy.data.objects['cracker'].modifiers["Cracker_Bend"].deform_axis = 'Z'
        bpy.data.objects['cracker'].modifiers["Cracker_Bend"].angle = 0
        bpy.data.objects['cracker'].modifiers["Cracker_Bend"].origin = crackerEmpty

        bpy.data.objects['cracker'].modifiers.new("Cracker_Displace", type='DISPLACE')
        bpy.data.objects['cracker'].modifiers["Cracker_Displace"].texture = cracker_texture
        bpy.data.objects['cracker'].modifiers["Cracker_Displace"].strength = 0.5

        bpy.data.objects['cracker'].modifiers.new("Cracker_Solid", type='SOLIDIFY')
        bpy.data.objects['cracker'].modifiers["Cracker_Solid"].thickness = 0.005
        bpy.data.objects['cracker'].modifiers["Cracker_Solid"].offset = 0

        bpy.data.objects[targetName].select_set(True)
        bpy.context.view_layer.objects.active = targetObj

        pass

    def displace_cracker(self, context, dx, dy):
        # Code to displace the cracker object based on mouse movement
        pass

    def rotate_cracker(self, context, wheel_direction):
        # Code to rotate the cracker object based on mouse wheel
        pass

    def apply_crack(self, context):
        original_active_object = context.view_layer.objects.active  # Store the original active object
        original_active_object_name = original_active_object.name  # Store the original active object's name for comparison

        # Apply the crack modifier
        for mod in original_active_object.modifiers:
            if mod.name == "cracker":
                bpy.ops.object.modifier_apply(modifier=mod.name)

        # Remove the cracker and empty objects
        object_to_delete = bpy.data.objects.get('cracker')
        empty_to_delete = bpy.data.objects.get('cracker_empty')
        if object_to_delete:
            bpy.data.objects.remove(object_to_delete, do_unlink=True)
        if empty_to_delete:
            bpy.data.objects.remove(empty_to_delete, do_unlink=True)

        # Ensure we're in Object mode
        if bpy.context.active_object.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

        bpy.ops.object.select_all(action='DESELECT')  # Deselect all objects

        # Reselect the original object and separate it into loose parts
        original_active_object.select_set(True)
        context.view_layer.objects.active = original_active_object
        bpy.ops.object.mode_set(mode='EDIT')  # Switch to Edit Mode
        bpy.ops.mesh.select_all(action='SELECT')  # Select all mesh parts
        bpy.ops.mesh.separate(type='LOOSE')  # Separate by loose parts
        bpy.ops.object.mode_set(mode='OBJECT')  # Switch back to Object Mode

        # Iterate through the objects to find new ones and set them to shade flat
        for obj in bpy.data.objects:
            if obj.name != original_active_object_name and obj.type == 'MESH':
                obj.select_set(True)
                context.view_layer.objects.active = obj  # Make the object active
                bpy.ops.object.shade_flat()  # Set shading to flat

        # Cleanup: Deselect all and reselect the original object
        bpy.ops.object.select_all(action='DESELECT')
        original_active_object.select_set(True)
        context.view_layer.objects.active = original_active_object

        return True

    # def execute(self, context):
    #     objects = context.selected_objects
    #     total_objects = len(objects)
    #     settings = context.scene.crack_settings

    #     # Cracking here.      

    #     self.report({'INFO'}, "Finished processing all objects")
    #     return {'FINISHED'}

class panel_crack(Panel):
    bl_idname = "LazyCrack"
    bl_label = "Lazy Crack"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Lazy Tools'
    bl_context = "objectmode"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type == 'MESH'

    def draw(self, context):
        layout = self.layout
        settings = context.scene.crack_settings

        layout.prop(settings, "fill_crack")
        layout.prop(settings, "noise_scale")
        layout.prop(settings, "thickness")
        layout.prop(settings, "noise_intensity")

        # Apply Crack button
        layout.operator("mesh.crack", text="Apply Crack")



def register():
    bpy.utils.register_class(operator_crack)
    bpy.utils.register_class(panel_crack)
    bpy.utils.register_class(crack_settings)
    bpy.types.Scene.crack_settings = bpy.props.PointerProperty(type=crack_settings)

def unregister():
    bpy.utils.unregister_class(operator_crack)
    bpy.utils.unregister_class(panel_crack)
    bpy.utils.unregister_class(crack_settings)
    del bpy.types.Scene.crack_settings

if __name__ == "__main__":
    register()