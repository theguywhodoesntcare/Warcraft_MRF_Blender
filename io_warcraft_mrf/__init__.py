bl_info = {
    "name": "Warcraft MORF (.mrf) Importer",
    "author": "wiselen",
    "version": (1, 0, 0),
    "blender": (4, 4, 0),
    "location": "File > Import/Export > Warcraft MORF (.mrf)",
    "description": "Import/export Warcraft .mrf mesh with Shape Keys.",
    "doc_url": "https://github.com/wiselencave/Warcraft_MRF_Blender",
    "tracker_url": "https://github.com/wiselencave/Warcraft_MRF_Blender",
    "category": "Import-Export",
}

import bpy
from .operators.import_operator import ImportMRFOperator
from .operators.export_operator import ExportMRFOperator
from .ui.texture_panel import MRFTextureProperties, MATERIAL_PT_mrf_texture

def menu_func_import(self, context):
    self.layout.operator(ImportMRFOperator.bl_idname, text="Warcraft MORF (.mrf)")

def menu_func_export(self, context):
    self.layout.operator(ExportMRFOperator.bl_idname, text="Warcraft MORF (.mrf)")

classes = (
    MRFTextureProperties,
    MATERIAL_PT_mrf_texture,
    ImportMRFOperator,
    ExportMRFOperator,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Material.mrf_texture_props = bpy.props.PointerProperty(type=MRFTextureProperties)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Material.mrf_texture_props
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)
