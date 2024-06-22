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
                # Ensure UV maps are added if they do not exist
                uv_layers = obj.data.uv_layers
                if "uv_color" not in uv_layers:
                    uv_layers.new(name="uv_color")
                if "uv_ao" not in uv_layers:
                    uv_layers.new(name="uv_ao")

                # Switch to edit mode to perform UV operations
                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.mode_set(mode='EDIT')

                # Unwrap each UV map separately
                for uv_name in ["uv_color", "uv_ao"]:
                    uv_layers.active = uv_layers[uv_name]
                    bpy.ops.mesh.select_all(action='SELECT')
                    bpy.ops.uv.smart_project()

                # Switch back to object mode
                bpy.ops.object.mode_set(mode='OBJECT')

                # Create image textures
                bpy.ops.image.new(name="texture_color", width=1024, height=1024, color=(0.0, 1.0, 0.0, 1.0))  # Green
                bpy.ops.image.new(name="texture_ao", width=1024, height=1024, color=(1.0, 1.0, 1.0, 1.0))  # White

                # Create materials and assign them textures and UV maps
                mat_color = bpy.data.materials.new(name="Material_Color")
                mat_ao = bpy.data.materials.new(name="Material_AO")
                mat_color.use_nodes = True
                mat_ao.use_nodes = True
                
                # Set up nodes for color material
                bsdf_color = mat_color.node_tree.nodes.get('Principled BSDF')
                tex_image_color = mat_color.node_tree.nodes.new('ShaderNodeTexImage')
                tex_image_color.image = bpy.data.images['texture_color']
                uv_map_color = mat_color.node_tree.nodes.new('ShaderNodeUVMap')
                uv_map_color.uv_map = "uv_color"
                mat_color.node_tree.links.new(uv_map_color.outputs['UV'], tex_image_color.inputs['Vector'])
                mat_color.node_tree.links.new(bsdf_color.inputs['Base Color'], tex_image_color.outputs['Color'])
                
                # Set up nodes for AO material
                bsdf_ao = mat_ao.node_tree.nodes.get('Principled BSDF')
                tex_image_ao = mat_ao.node_tree.nodes.new('ShaderNodeTexImage')
                tex_image_ao.image = bpy.data.images['texture_ao']
                uv_map_ao = mat_ao.node_tree.nodes.new('ShaderNodeUVMap')
                uv_map_ao.uv_map = "uv_ao"
                mat_ao.node_tree.links.new(uv_map_ao.outputs['UV'], tex_image_ao.inputs['Vector'])
                mat_ao.node_tree.links.new(bsdf_ao.inputs['Base Color'], tex_image_ao.outputs['Color'])
                
                # Assign materials to the object
                if obj.data.materials:
                    obj.data.materials[0] = mat_color
                    if len(obj.data.materials) > 1:
                        obj.data.materials[1] = mat_ao
                    else:
                        obj.data.materials.append(mat_ao)
                else:
                    obj.data.materials.append(mat_color)
                    obj.data.materials.append(mat_ao)

        self.report({'INFO'}, "UV maps, textures, and materials created")
        return {'FINISHED'}



class MATERIAL_OT_create_palette(Operator):
    bl_idname = "material.create_palette"
    bl_label = "Create Color Palette"
    bl_description = "Creates a color palette based on specified grid size"
    bl_options = {'REGISTER', 'UNDO'}
    palette_rows: IntProperty(name="Rows", min=1, max=4, default=1)
    palette_columns: IntProperty(name="Columns", min=1, max=4, default=1)

    @classmethod
    def poll(cls, context):
        return context.object is not None and \
            "uv_color" in context.object.data.uv_layers.keys() and \
            context.mode == 'OBJECT'
    
    def execute(self, context):
        # Placeholder for creating the palette
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
        return context.object is not None and \
            context.object.type == 'MESH' and  \
            len(context.selected_objects) == 1 and \
            context.mode == 'OBJECT'
        
    def execute(self, context):
        context.scene.render.engine = 'CYCLES'
        # Placeholder for baking AO
        self.report({'INFO'}, "AO baked")
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
