import bpy
from . import ui
from . import preset_operators

bl_info = {
    "name": "Lazy Chip",
    "author": "thelazyone",
    "location": "View3d > Toolbar > Weathering",
    "blender": (4, 0, 0),
    "category": "Object",
    "version": (0, 0, 1),
    "description": "A suite of tools for mesh weathering and manipulation."
}

# Function to automatically register all classes from the modules
def register_classes_from_module(module):
    for attr_name in dir(module):
        print(f"Trying register {attr_name}")
        attr = getattr(module, attr_name)
        if isinstance(attr, type) and (issubclass(attr, bpy.types.Operator) or issubclass(attr, bpy.types.Panel)):
            try:
                bpy.utils.register_class(attr)
            except ValueError as e:
                print(f"Skipping registration for {attr.__name__}: {e}")
                

def register():

    # Registering the other files first:
    ui.register()
    preset_operators.register()
    
    # # TODO maybe redundant?
    # register_classes_from_module(ui)
    # register_classes_from_module(preset_operators)

    # # Registering the weathering props
    # bpy.utils.register_class(ui.WeatheringProps)
    # bpy.types.Scene.weathering_props = bpy.props.PointerProperty(type=ui.WeatheringProps)


def unregister():
    del bpy.types.Scene.weathering_props

    for attr_name in dir(preset_operators):
        attr = getattr(preset_operators, attr_name)
        if isinstance(attr, type) and (issubclass(attr, bpy.types.Operator) or issubclass(attr, bpy.types.Panel)):
            bpy.utils.unregister_class(attr)
    for attr_name in dir(ui):
        attr = getattr(ui, attr_name)
        if isinstance(attr, type) and (issubclass(attr, bpy.types.Operator) or issubclass(attr, bpy.types.Panel)):
            bpy.utils.unregister_class(attr)
    del bpy.types.Scene.weathering_props


if __name__ == "__main__":
    register()
