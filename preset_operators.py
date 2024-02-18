class POLYDAMAGE_OP_resetsettings(Operator):
    bl_label = "Reset Settings"
    bl_idname = "polydamage.op_resetsettings"
    def execute(self, context):
        pointer_property = context.scene.pointer_property
        pointer_property.resolution_property = 64
        pointer_property.edge_relax_property = 3.0
        pointer_property.edge_push_property = 0.7
        pointer_property.noise_scale_property = 40
        pointer_property.noise_strength_property = 8.0
        pointer_property.noise_contrast_property = 1.0
        pointer_property.seed_property = 0
        pointer_property.random_seed_property = True
        pointer_property.fixed_scale_check_property = False
        pointer_property.fixed_scale_property = 1.0
        return {'FINISHED'}
class POLYDAMAGE_OP_woodsmoothing(Operator):
    bl_label = "Set Wood Smoothing"
    bl_idname = "polydamage.op_woodsmoothing"
    def execute(self, context):
        pointer_property = context.scene.pointer_property
        pointer_property.resolution_property = 64
        pointer_property.edge_relax_property = 1.5
        pointer_property.edge_push_property = 0.9
        pointer_property.noise_scale_property = 60
        pointer_property.noise_strength_property = 8.0
        pointer_property.noise_contrast_property = 0.5
        pointer_property.seed_property = 0
        pointer_property.random_seed_property = True
        pointer_property.fixed_scale_check_property = True
        pointer_property.fixed_scale_property = 4.0
        return {'FINISHED'}
class POLYDAMAGE_OP_woodchipping(Operator):
    bl_label = "Set Wood Chipping"
    bl_idname = "polydamage.op_woodchipping"
    def execute(self, context):
        pointer_property = context.scene.pointer_property
        pointer_property.resolution_property = 64
        pointer_property.edge_relax_property = 0.5
        pointer_property.edge_push_property = 0.8
        pointer_property.noise_scale_property = 40
        pointer_property.noise_strength_property = 20
        pointer_property.noise_contrast_property = 2
        pointer_property.seed_property = 0  
        pointer_property.random_seed_property = True
        pointer_property.fixed_scale_check_property = True
        pointer_property.fixed_scale_property = 4.0
        return {'FINISHED'}
class POLYDAMAGE_OP_stonemarbling(Operator):
    bl_label = "Set Stone Marbling"
    bl_idname = "polydamage.op_stonemarbling"
    def execute(self, context):
        pointer_property = context.scene.pointer_property
        pointer_property.resolution_property = 64
        pointer_property.edge_relax_property = 0.0
        pointer_property.edge_push_property = 0.5
        pointer_property.noise_scale_property = 100
        pointer_property.noise_strength_property = 24
        pointer_property.noise_contrast_property = 0.5
        pointer_property.seed_property = 0  
        pointer_property.random_seed_property = True
        pointer_property.fixed_scale_check_property = True
        pointer_property.fixed_scale_property = 3.0
        return {'FINISHED'}
class POLYDAMAGE_OP_stonechipping(Operator):
    bl_label = "Set Stone Chipping"
    bl_idname = "polydamage.op_stonechipping"
    def execute(self, context):
        pointer_property = context.scene.pointer_property
        pointer_property.resolution_property = 64
        pointer_property.edge_relax_property = 4.0
        pointer_property.edge_push_property = 0.8
        pointer_property.noise_scale_property = 40
        pointer_property.noise_strength_property = 12.0
        pointer_property.noise_contrast_property = 1.0
        pointer_property.seed_property = 0
        pointer_property.random_seed_property = True
        pointer_property.fixed_scale_check_property = True
        pointer_property.fixed_scale_property = 4.0
        return {'FINISHED'}
class POLYDAMAGE_OP_stoneweathering(Operator):
    bl_label = "Set Stone Weathering"
    bl_idname = "polydamage.op_stoneweathering"
    def execute(self, context):
        pointer_property = context.scene.pointer_property
        pointer_property.resolution_property = 64
        pointer_property.edge_relax_property = 0.0
        pointer_property.edge_push_property = 0.9
        pointer_property.noise_scale_property = 160
        pointer_property.noise_strength_property = 24
        pointer_property.noise_contrast_property = 3.5
        pointer_property.seed_property = 0  
        pointer_property.random_seed_property = True
        pointer_property.fixed_scale_check_property = True
        pointer_property.fixed_scale_property = 2.0
        return {'FINISHED'}
class POLYDAMAGE_OP_concretechippingsurface(Operator):
    bl_label = "Set Concrete Chipping Surface"
    bl_idname = "polydamage.op_concretechippingsurface"
    def execute(self, context):
        pointer_property = context.scene.pointer_property
        pointer_property.resolution_property = 64
        pointer_property.edge_relax_property = .5
        pointer_property.edge_push_property = 0.9
        pointer_property.noise_scale_property = 40
        pointer_property.noise_strength_property = 30.0
        pointer_property.noise_contrast_property = 2.2
        pointer_property.seed_property = 0
        pointer_property.random_seed_property = True
        pointer_property.fixed_scale_check_property = True
        pointer_property.fixed_scale_property = 4.0
        return {'FINISHED'}
class POLYDAMAGE_OP_concretechippingedges(Operator):
    bl_label = "Set Concrete Chipping Edges"
    bl_idname = "polydamage.op_concretechippingedges"
    def execute(self, context):
        pointer_property = context.scene.pointer_property
        pointer_property.resolution_property = 64
        pointer_property.edge_relax_property = 4.0
        pointer_property.edge_push_property = 0.98
        pointer_property.noise_scale_property = 40
        pointer_property.noise_strength_property = 12.0
        pointer_property.noise_contrast_property = 1.0
        pointer_property.seed_property = 0
        pointer_property.random_seed_property = True
        pointer_property.fixed_scale_check_property = True
        pointer_property.fixed_scale_property = 4.0
        return {'FINISHED'}
