bl_info = {
    "name": "Extended Materials and UV Tools",
    "author": "thelazyone",
    "version": (1, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > Lazy Tools",
    "description": "Provides multiple tools for handling materials and UV maps",
    "warning": "",
    "wiki_url": "",
    "category": "Mesh",
}

import bpy
from bpy.types import Operator, Panel
from bpy.props import IntProperty
import math as m
import random   # for UV settings
import colorsys  # for Palette


# Setting for the plugin.
class ExtendedMaterialSettings(bpy.types.PropertyGroup):
    palette_rows: bpy.props.IntProperty(
        name="Rows",
        description="Number of rows in the color palette",
        default=1, min=1, max=4
    )
    palette_columns: bpy.props.IntProperty(
        name="Columns",
        description="Number of columns in the color palette",
        default=1, min=1, max=4
    )
    color_index: bpy.props.IntProperty(
        name="Color Index",
        description="Index of the color to apply",
        default=1, min=1, max=16
    )

class MATERIAL_OT_delete_materials(Operator):
    bl_idname = "material.delete_materials"
    bl_label = "Delete Materials"
    bl_description = "Deletes all materials from selected objects"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.object is not None and \
            context.object.type == 'MESH' and  \
            len(context.selected_objects) == 1 and \
            context.mode == 'OBJECT'
        
    def execute(self, context):
        selected_objects = context.selected_objects
        for obj in selected_objects:
            if obj.type == 'MESH':
                obj.data.materials.clear()                
        self.report({'INFO'}, "Deleted materials from selected objects")
        return {'FINISHED'}
    
class MATERIAL_OT_generate_materials(Operator):
    bl_idname = "uv.generate_materials"
    bl_label = "Generate Materials and UVs"
    bl_description = "Generates Materials, UVs and Textures for color and AO"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.type == 'MESH' and \
            len(context.selected_objects) == 1 and context.mode == 'OBJECT'
    
    def execute(self, context):
        selected_objects = context.selected_objects
        for obj in selected_objects:
            if obj.type == 'MESH':
                
                # Apply transformations
                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.ops.object.select_all(action='DESELECT')
                obj.select_set(True)
                bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

                # Define unique names based on the object name
                texture_color_name = f"{obj.name}_texture_color"
                texture_ao_name = f"{obj.name}_texture_ao"
                material_color_name = f"{obj.name}_Material_Color"
                material_ao_name = f"{obj.name}_Material_AO"

                # Ensure UV maps are added if they do not exist
                uv_layers = obj.data.uv_layers
                if "uv_color" not in uv_layers:
                    uv_layers.new(name="uv_color")
                if "uv_ao" not in uv_layers:
                    uv_layers.new(name="uv_ao")

                # Switch to edit mode to perform UV operations
                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.mode_set(mode='EDIT')

                # Unwrap each UV map separately with adjusted settings
                bpy.ops.object.mode_set(mode='EDIT')
                for uv_name in ["uv_color", "uv_ao"]:
                    uv_layers.active = uv_layers[uv_name]
                    bpy.ops.mesh.select_all(action='SELECT')
                    bpy.ops.uv.smart_project(
                        angle_limit=m.radians(66),
                        island_margin=0.00,
                        area_weight=0.00,
                        margin_method='SCALED',
                        correct_aspect=True,
                        scale_to_bounds=False
                )
                    
                # Switch back to object mode after unwrapping
                bpy.ops.object.mode_set(mode='OBJECT')

                # Manage existing textures
                old_texture_color = bpy.data.images.get(texture_color_name)
                if old_texture_color:
                    if old_texture_color.users == 1:
                        bpy.data.images.remove(old_texture_color)
                    else:
                        old_texture_color.user_clear()  # Clear users if more than one

                old_texture_ao = bpy.data.images.get(texture_ao_name)
                if old_texture_ao:
                    if old_texture_ao.users == 1:
                        bpy.data.images.remove(old_texture_ao)
                    else:
                        old_texture_ao.user_clear()

                # Create or find textures
                if texture_color_name not in bpy.data.images:
                    texture_color = bpy.data.images.new(name=texture_color_name, width=1024, height=1024, alpha=True)
                    # Fill the image with green color
                    fill_color = (0.0, 1.0, 0.0, 1.0)  # RGBA for green
                    texture_color.pixels = [val for _ in range(texture_color.size[0] * texture_color.size[1]) for val in fill_color]
                else:
                    texture_color = bpy.data.images[texture_color_name]

                if texture_ao_name not in bpy.data.images:
                    texture_ao = bpy.data.images.new(name=texture_ao_name, width=1024, height=1024, alpha=True)
                    # Fill the image with white color
                    fill_color = (1.0, 1.0, 1.0, 1.0)  # RGBA for white
                    texture_ao.pixels = [val for _ in range(texture_ao.size[0] * texture_ao.size[1]) for val in fill_color]
                else:
                    texture_ao = bpy.data.images[texture_ao_name]

                # Create or find materials
                mat_color = bpy.data.materials.get(material_color_name) or bpy.data.materials.new(name=material_color_name)
                mat_ao = bpy.data.materials.get(material_ao_name) or bpy.data.materials.new(name=material_ao_name)

                # Setup material node tree for color
                if mat_color.use_nodes:
                    bsdf_color = mat_color.node_tree.nodes.get('Principled BSDF')
                else:
                    mat_color.use_nodes = True
                    bsdf_color = mat_color.node_tree.nodes.get('Principled BSDF')
                tex_image_color = mat_color.node_tree.nodes.new('ShaderNodeTexImage')
                tex_image_color.image = texture_color
                uv_map_color = mat_color.node_tree.nodes.new('ShaderNodeUVMap')
                uv_map_color.uv_map = "uv_color"
                mat_color.node_tree.links.new(uv_map_color.outputs['UV'], tex_image_color.inputs['Vector'])
                mat_color.node_tree.links.new(bsdf_color.inputs['Base Color'], tex_image_color.outputs['Color'])

                # Setup material node tree for AO
                if mat_ao.use_nodes:
                    bsdf_ao = mat_ao.node_tree.nodes.get('Principled BSDF')
                else:
                    mat_ao.use_nodes = True
                    bsdf_ao = mat_ao.node_tree.nodes.get('Principled BSDF')
                tex_image_ao = mat_ao.node_tree.nodes.new('ShaderNodeTexImage')
                tex_image_ao.image = texture_ao
                uv_map_ao = mat_ao.node_tree.nodes.new('ShaderNodeUVMap')
                uv_map_ao.uv_map = "uv_ao"
                mat_ao.node_tree.links.new(uv_map_ao.outputs['UV'], tex_image_ao.inputs['Vector'])
                mat_ao.node_tree.links.new(bsdf_ao.inputs['Base Color'], tex_image_ao.outputs['Color'])

                # Assign materials to the object
                obj.data.materials.clear()
                obj.data.materials.append(mat_color)
                obj.data.materials.append(mat_ao)

        self.report({'INFO'}, "UV maps, textures, and materials uniquely created or updated for each object")
        return {'FINISHED'}


class MATERIAL_OT_create_palette(Operator):
    bl_idname = "material.create_palette"
    bl_label = "Create Color Palette"
    bl_description = "Creates a color palette based on specified grid size"
    bl_options = {'REGISTER', 'UNDO'}
    #palette_rows: IntProperty(name="Rows", min=1, max=4, default=1)
    #palette_columns: IntProperty(name="Columns", min=1, max=4, default=1)

    @classmethod
    def poll(cls, context):
        return context.object is not None and \
            "uv_color" in context.object.data.uv_layers.keys() and \
            context.mode == 'OBJECT'
    
    def execute(self, context):
        obj = context.active_object
        texture_name = f"{obj.name}_texture_color"
        texture = bpy.data.images.get(texture_name)
        if not texture:
            self.report({'ERROR'}, "Texture not found")
            return {'CANCELLED'}

        width, height = texture.size
        pixels = list(texture.pixels)

        settings = context.scene.extended_material_settings
        palette_rows = settings.palette_rows
        palette_columns = settings.palette_columns

        # Calculate the size of each grid cell
        cell_width = int(width / palette_columns)
        cell_height = int(height / palette_rows)

        # Function to generate a random color
        def random_color():
            hue = random.random()  # Random hue
            saturation = 0.75  # Fixed saturation
            value = 1.0  # Fixed value
            return colorsys.hsv_to_rgb(hue, saturation, value)  # Returns an RGB tuple

        # Iterate over each cell in the grid
        for row in range(palette_rows):
            for col in range(palette_columns):
                color = random_color()  # Get RGB tuple

                # Fill the cell with the color
                for y in range(row * cell_height, (row + 1) * cell_height):
                    for x in range(col * cell_width, (col + 1) * cell_width):
                        index = (y * width + x) * 4  # Pixel index (each pixel has 4 values: RGBA)
                        pixels[index:index+3] = color  # Set RGB
                        pixels[index+3] = 1.0  # Set Alpha

        # Update the texture
        texture.pixels = pixels
        texture.update()

        self.report({'INFO'}, "Color palette created")
        return {'FINISHED'}
    

class MATERIAL_OT_set_face_color(Operator):
    bl_idname = "material.set_face_color"
    bl_label = "Set Face Color"
    bl_description = "Sets the selected faces to a specific color in the palette"
    bl_options = {'REGISTER', 'UNDO'}
    color_index: IntProperty(name="Color Index", min=1, max=16, default=1)

    @classmethod
    def poll(cls, context):
        return context.object is not None and \
            "uv_color" in context.object.data.uv_layers.keys() and \
            context.mode == 'EDIT_MESH' and \
            context.object.data.total_face_sel > 0

    def execute(self, context):
        # Placeholder for setting face color
        self.report({'INFO'}, "Face color set")
        return {'FINISHED'}

class MATERIAL_OT_bake_ao(Operator):
    bl_idname = "material.bake_ao"
    bl_label = "Bake AO"
    bl_description = "Bakes ambient occlusion for the current model"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj is not None and \
               "uv_ao" in obj.data.uv_layers.keys() and \
               obj.type == 'MESH' and \
               len(context.selected_objects) == 1 and \
               context.mode == 'OBJECT'

    def execute(self, context):
        # Ensure the scene's renderer is set to Cycles
        context.scene.render.engine = 'CYCLES'

        obj = context.active_object

        # Define unique material and texture names based on object name
        material_ao_name = f"{obj.name}_Material_AO"
        texture_ao_name = f"{obj.name}_texture_ao"

        # Find or create the AO material and image
        mat_ao = bpy.data.materials.get(material_ao_name)
        if not mat_ao:
            self.report({'ERROR'}, "AO Material not found: " + material_ao_name)
            return {'CANCELLED'}
        
        image_ao = bpy.data.images.get(texture_ao_name)
        if not image_ao:
            self.report({'ERROR'}, "AO Texture not found: " + texture_ao_name)
            return {'CANCELLED'}
        
        # Prepare the object for baking by selecting it and assigning the AO material
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        context.view_layer.objects.active = obj

        obj.data.materials.clear()
        obj.data.materials.append(mat_ao)

        # Create a new image node for the AO texture and set it as active for baking
        node_tree = mat_ao.node_tree
        bake_node = node_tree.nodes.new(type='ShaderNodeTexImage')
        bake_node.image = image_ao
        node_tree.nodes.active = bake_node

        # Configure bake settings
        context.scene.cycles.bake_type = 'AO'
        context.scene.render.bake.use_selected_to_active = False
        context.scene.render.bake.use_clear = True
        context.scene.render.bake.margin = 2  # Adjust based on your needs

        # Perform the bake
        bpy.ops.object.bake(type='AO')

        # Clean up: remove the temporary image node
        node_tree.nodes.remove(bake_node)

        self.report({'INFO'}, "AO baked successfully")
        return {'FINISHED'}

class MATERIAL_PT_custom_panel(Panel):
    bl_label = "Extended Material Tools"
    bl_idname = "MATERIAL_PT_custom_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Lazy Tools'
    bl_context = "" # If nothing is set here it'll work in edit mode too.


    def draw(self, context):
        layout = self.layout
        settings = context.scene.extended_material_settings

        layout.operator(MATERIAL_OT_delete_materials.bl_idname)

        layout.separator()
        layout.label(text="UV Mapping")
        layout.operator(MATERIAL_OT_generate_materials.bl_idname)

        layout.separator()
        layout.label(text="Color Palette")
        col = layout.column()
        col.enabled = "uv_color" in context.active_object.data.uv_layers.keys() and context.mode == 'OBJECT'
        row = col.row()
        row.prop(settings, "palette_rows", text="Rows")
        row.prop(settings, "palette_columns", text="Columns")
        col.operator(MATERIAL_OT_create_palette.bl_idname)

        layout.separator()
        layout.label(text="Set Face Color")
        col = layout.column()
        col.enabled = context.mode == 'EDIT_MESH' and context.active_object.data.total_face_sel > 0
        col.prop(settings, "color_index", text="Color Index")
        col.operator(MATERIAL_OT_set_face_color.bl_idname)

        layout.separator()
        layout.label(text="AO Baking")
        col = layout.column()
        col.enabled = "uv_ao" in context.active_object.data.uv_layers.keys() and context.mode == 'OBJECT'
        col.operator(MATERIAL_OT_bake_ao.bl_idname)


def register():
    bpy.utils.register_class(ExtendedMaterialSettings)
    bpy.types.Scene.extended_material_settings = bpy.props.PointerProperty(type=ExtendedMaterialSettings)

    bpy.utils.register_class(MATERIAL_OT_delete_materials)
    bpy.utils.register_class(MATERIAL_OT_generate_materials)
    bpy.utils.register_class(MATERIAL_OT_bake_ao)
    bpy.utils.register_class(MATERIAL_OT_create_palette)
    bpy.utils.register_class(MATERIAL_OT_set_face_color)
    bpy.utils.register_class(MATERIAL_PT_custom_panel)

def unregister():
    bpy.utils.unregister_class(ExtendedMaterialSettings)
    del bpy.types.Scene.extended_material_settings

    bpy.utils.unregister_class(MATERIAL_OT_delete_materials)
    bpy.utils.unregister_class(MATERIAL_OT_generate_materials)
    bpy.utils.unregister_class(MATERIAL_OT_bake_ao)
    bpy.utils.unregister_class(MATERIAL_OT_create_palette)
    bpy.utils.unregister_class(MATERIAL_OT_set_face_color)
    bpy.utils.unregister_class(MATERIAL_PT_custom_panel)

if __name__ == "__main__":
    register()
