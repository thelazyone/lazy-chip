import bpy
from . import ui
from . import damage

# List of classes to register
classes = (
    ui.PolyDamageProps,
    ui.PolyDamagePanel,
    ui.PolyDamageInfoPanel,
    damage.POLYDAMAGE_OP_applydamage,
    damage.POLYDAMAGE_OP_removedamage,
    damage.POLYDAMAGE_OP_resetsettings,
    damage.POLYDAMAGE_OP_woodsmoothing,
    damage.POLYDAMAGE_OP_woodchipping,
    damage.POLYDAMAGE_OP_clearstash,
    damage.POLYDAMAGE_OP_stonemarbling,
    damage.POLYDAMAGE_OP_stonechipping,
    damage.POLYDAMAGE_OP_stoneweathering,
    damage.POLYDAMAGE_OP_concretechippingsurface,
    damage.POLYDAMAGE_OP_concretechippingedges,
)

def register():
    # Register all classes
    for cls in classes:
        bpy.utils.register_class(cls)
    
    # Initialize properties
    bpy.types.Scene.pointer_property = bpy.props.PointerProperty(type=ui.PolyDamageProps)

def unregister():
    # Unregister all classes
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    # Remove properties
    del bpy.types.Scene.pointer_property

if __name__ == "__main__":
    register()
