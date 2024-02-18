import bpy
from bpy.types import Panel, Operator
from bpy.props import PointerProperty
from .presets import DamagePresets

class PolyDamageProps(bpy.types.PropertyGroup):
    resolution_property: bpy.props.IntProperty(name="Resolution", default=DamagePresets.resolution_default, min=DamagePresets.resolution_min, max=DamagePresets.resolution_max)
    edge_relax_property: bpy.props.FloatProperty(name="Edge Relax", default=DamagePresets.edge_relax_default, min=DamagePresets.edge_relax_min, max=DamagePresets.edge_relax_max)
    edge_push_property: bpy.props.FloatProperty(name="Edge Push", default=DamagePresets.edge_push_default, min=DamagePresets.edge_push_min, max=DamagePresets.edge_push_max)
    noise_scale_property: bpy.props.FloatProperty(name="Noise Scale", default=DamagePresets.noise_scale_default, min=DamagePresets.noise_scale_min, max=DamagePresets.noise_scale_max)
    noise_strength_property: bpy.props.FloatProperty(name="Noise Strength", default=DamagePresets.noise_strength_default, min=DamagePresets.noise_strength_min, max=DamagePresets.noise_strength_max)
    noise_contrast_property: bpy.props.FloatProperty(name="Noise Contrast", default=DamagePresets.noise_contrast_default, min=DamagePresets.noise_contrast_min, max=DamagePresets.noise_contrast_max)
    seed_property: bpy.props.IntProperty(name="Seed", default=DamagePresets.seed_default, min=DamagePresets.seed_min, max=DamagePresets.seed_max)
    random_seed_property: bpy.props.BoolProperty(name="Random Seed", default=DamagePresets.random_seed_default)
    fixed_scale_check_property: bpy.props.BoolProperty(name="Use Fixed Scale", default=DamagePresets.fixed_scale_check_default)
    fixed_scale_property: bpy.props.FloatProperty(name="Fixed Scale", default=DamagePresets.fixed_scale_default, min=DamagePresets.fixed_scale_min, max=DamagePresets.fixed_scale_max)
    attempts_property: bpy.props.IntProperty(name="Attempts", default=DamagePresets.attempts_default, min=DamagePresets.attempts_min, max=DamagePresets.attempts_max)

class PolyDamagePanel(Panel):
    bl_label = "PolyDamage"
    bl_idname = "PT_PolyDamage"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Weathering'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        scene_pointer = scene.poly_damage_props

        layout.prop(scene_pointer, "resolution_property")
        layout.prop(scene_pointer, "edge_relax_property")
        layout.prop(scene_pointer, "edge_push_property")
        layout.prop(scene_pointer, "noise_scale_property")
        layout.prop(scene_pointer, "noise_strength_property")
        layout.prop(scene_pointer, "noise_contrast_property")
        layout.prop(scene_pointer, "seed_property")
        layout.prop(scene_pointer, "random_seed_property")
        layout.prop(scene_pointer, "fixed_scale_check_property")
        layout.prop(scene_pointer, "fixed_scale_property")
        layout.prop(scene_pointer, "attempts_property")

        # Example operator button
        layout.operator("polydamage.apply_damage")

# Example operator class
class POLYDAMAGE_OP_applydamage(Operator):
    bl_label = "Apply Damage"
    bl_idname = "polydamage.apply_damage"

    def execute(self, context):
        # Placeholder for operator logic
        self.report({'INFO'}, "Damage Applied")
        return {'FINISHED'}

def register():
    bpy.utils.register_class(PolyDamageProps)
    bpy.types.Scene.poly_damage_props = PointerProperty(type=PolyDamageProps)
    bpy.utils.register_class(PolyDamagePanel)
    bpy.utils.register_class(POLYDAMAGE_OP_applydamage)

def unregister():
    bpy.utils.unregister_class(PolyDamageProps)
    del bpy.types.Scene.poly_damage_props
    bpy.utils.unregister_class(PolyDamagePanel)
    bpy.utils.unregister_class(POLYDAMAGE_OP_applydamage)

if __name__ == "__main__":
    register()