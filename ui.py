import bpy
from bpy.types import Panel, PropertyGroup
from bpy.props import IntProperty, FloatProperty, PointerProperty

class WeatheringProps(PropertyGroup):
    resolution_property: IntProperty(name="Resolution", default=64, min=16, max=4096)
    edge_relax_property: FloatProperty(name="Edge Relax", default=3.0, min=0, max=2048)
    edge_push_property: FloatProperty(name="Edge Push", default=0.7, min=0.0, max=1.0)
    noise_scale_property: FloatProperty(name="Noise Scale", default=40, min=0, max=8192)
    noise_strength_property: FloatProperty(name="Noise Strength", default=8.0, min=0, max=8192)
    noise_contrast_property: FloatProperty(name="Noise Contrast", default=1.0, min=0, max=1024)
    seed_property: IntProperty(name="Seed", default=0, min=0, max=999999)
    random_seed_property: bpy.props.BoolProperty(name="Random Seed", default=True)
    fixed_scale_check_property: bpy.props.BoolProperty(name="Use Fixed Scale", default=False)
    fixed_scale_property: FloatProperty(name="Noise Scale", default=1, min=0, max=20)
    attempts_property: IntProperty(name="Attempts", default=5, min=1, max=100, description="Number of times the script attempts to apply its logic before giving up")

class WeatheringPanel(Panel):
    bl_label = "Lazy Chip"
    bl_idname = "PT_LazyChip"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Weathering'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        scene_pointer = scene.pointer_property
        curr_column = layout.column()
        curr_column.label(text="Lazy Chip", icon='CUBE')
        curr_column = layout.column(align=True)
        curr_column.label(text="Settings:")
        curr_column.prop(scene_pointer, "resolution_property")
        curr_column = layout.column(align=True)
        curr_column.prop(scene_pointer, "edge_relax_property")
        curr_column.prop(scene_pointer, "edge_push_property")
        curr_column = layout.column(align=True)
        curr_column.prop(scene_pointer, "noise_scale_property")
        curr_column.prop(scene_pointer, "noise_strength_property")
        curr_column.prop(scene_pointer, "noise_contrast_property")
        curr_column = layout.column(align=True)
        curr_column.prop(scene_pointer, "seed_property")
        curr_column.prop(scene_pointer, "random_seed_property")
        curr_column.operator("lazychip.op_setdefaultsettings")
        curr_column.label(text="Wood:")
        curr_column.operator("lazychip.op_woodsmoothing")
        curr_column.operator("lazychip.op_woodchipping")
        curr_column.label(text="Stone:")
        curr_column.operator("lazychip.op_stonemarbling")
        curr_column.operator("lazychip.op_stonechipping")
        curr_column.operator("lazychip.op_stoneweathering")
        curr_column.label(text="Concrete:")
        curr_column.operator("lazychip.op_concretechippingsurface")
        curr_column.operator("lazychip.op_concretechippingedges")
        curr_column = layout.column()
        curr_column.label(text="Selected objects: " + str(
            [curr_object.name for curr_object in context.selected_objects if curr_object.type == 'MESH']))
        curr_column = layout.column(align=True)
        curr_column.scale_y = 1.5
        curr_column.prop(scene_pointer, "attempts_property")
        curr_column.operator("lazychip.op_removedamage")
        curr_column.operator("lazychip.op_applydamage")
        curr_column.operator("lazychip.op_clearstash")
        curr_column = layout.column(align=True)
        curr_column.label(text="Proportions:")
        curr_column.prop(scene_pointer, "fixed_scale_check_property")
        curr_column.prop(scene_pointer, "fixed_scale_property")

# TO BE DONE PROPERLY
class LazyChipInfoPanel(Panel):
    bl_label = "Info"
    bl_idname = "PT_LazyChip"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = 'PT_LazyChip'
    bl_options = {'DEFAULT_CLOSED'}
    def draw(self, context):
        layout = self.layout
        curr_column = layout.column()
        curr_column.label(text="About Lazy Chip", icon='INFO')
        curr_column.label(text="Lazy Chip by The Lazy Forger")
        curr_separator = layout.separator()
        curr_column = layout.column(align=True)
        curr_column.label(text="https://github.com/thelazyone/lazy-chip")
        curr_column.label(text="https://www.myminifactory.com/users/TheLazyForger")

def register():
    # Adding the params sliders:
    bpy.utils.register_class(WeatheringProps)
    bpy.types.Scene.weathering_props = PointerProperty(type=WeatheringProps)
    bpy.utils.register_class(WeatheringPanel)

def unregister():
    bpy.utils.unregister_class(WeatheringProps)
    del bpy.types.Scene.weathering_props
    bpy.utils.unregister_class(WeatheringPanel)

if __name__ == "__main__":
    register()