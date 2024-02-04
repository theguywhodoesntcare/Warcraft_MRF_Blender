bl_info = {
    "name": "Warcraft MORF (.mrf) Importer",
    "author": "poisoNDealer",
    "version": (0, 2, 1),
    "blender": (3, 6, 2),
    "location": "File > Import > Warcraft MORF (.mrf), File > Export > Warcraft MORF (.mrf)",
    "description": "Imports Warcraft .mrf files and reproduces their animations using Shape Keys. Exports the selected mesh from the Blender scene to Warcraft .mrf format.",
    "doc_url": "https://github.com/theguywhodoesntcare/Warcraft_MRF_Blender",
    "tracker_url": "https://github.com/theguywhodoesntcare/Warcraft_MRF_Blender",
    "category": "Import-Export",
}

import bpy
from bpy_extras.io_utils import ImportHelper
from bpy_extras.io_utils import ExportHelper
from bpy.types import Operator

class MessageBox:
    @staticmethod
    def show(message="", title="Message Box", icon='INFO'):
        def draw(self, context):
            self.layout.label(text=message)

        bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)
        print(f"{title} {message}")


from . import import_mrf
from . import export_mrf


class ImportMRFOperator(Operator, ImportHelper):
    bl_idname = "import.mrf"
    bl_label = "Import MRF"
    filename_ext = ".mrf"

    filter_glob: bpy.props.StringProperty(
        default="*.mrf",
        options={'HIDDEN'},
    )

    divisor: bpy.props.FloatProperty(
        name="Divisor",
        description="The scale factor (division) of the imported model",
        default=50,
        min = 1.0
    )

    shade_smooth: bpy.props.BoolProperty(
        name="Shade Smooth",
        description="Apply smooth shading to the imported model",
        default=False,
    )

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.label(text="Warcraft sizes will be too large for Blender!", icon='ERROR')
        box.label(text="Use a divisor to reduce model by N times")
        layout.prop(self, 'divisor')
        layout.prop(self, 'shade_smooth')

    def execute(self, context):
        import_mrf.load_morf(self.filepath, self.divisor, self.shade_smooth)
        return {'FINISHED'}

class ExportMRFOperator(Operator, ExportHelper):
    bl_idname = "export.mrf"
    bl_label = "Export MRF"
    filename_ext = ".mrf"
    default_texture = r'Textures/white'
    kf_start = 0
    kf_end = 23

    filter_glob: bpy.props.StringProperty(default="*.mrf", options={'HIDDEN'})
    scale_factor: bpy.props.FloatProperty(name="Scale Factor", description="The scale factor of the exported model", default=50, min=0.01)

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.label(text="Blender sizes will be too small for Warcraft!", icon='ERROR')
        box.label(text="Use a Scale Factor to scale model by N times")
        layout.prop(self, 'scale_factor')

    def invoke(self, context, event):
        if not bpy.context.selected_objects or not any(obj.type == 'MESH' for obj in bpy.context.selected_objects):
            MessageBox.show('Error!', 'No Mesh Object Selected.', 'ERROR')
            return {'CANCELLED'}

        return ExportHelper.invoke(self, context, event) 

    def execute(self, context):
        obj = bpy.context.active_object
        if not obj or obj.type != 'MESH':
            MessageBox.show('Error!', 'No Active Mesh Object.', 'ERROR')
            return {'CANCELLED'}

        texture_path = self.get_texture_path()
        kf_start, kf_end = self.get_kf_range()

        export_mrf.save_morf(self.filepath, obj, self.scale_factor, texture_path, (kf_start, kf_end))
        
        return {'FINISHED'}

    def get_texture_path(self):
        mat = bpy.context.object.active_material
        if mat and len(mat.mrf_texture_props.texture_path) > 0:
            return r"{}".format(mat.mrf_texture_props.texture_path)
        
        MessageBox.show(f"The path {self.default_texture} has been set", 'Texture path not found. Set the MRF texture path', 'ERROR')
        return self.default_texture

    def get_kf_range(self):
        kf_start, kf_end = self.kf_start, self.kf_end
        mrf_markers = [marker for marker in bpy.context.scene.timeline_markers if marker.name.lower() == "mrf"]

        if len(mrf_markers) >= 2:
            mrf_markers.sort(key=lambda marker: marker.frame)
            kf_start, kf_end = mrf_markers[0].frame, mrf_markers[1].frame
        else:
            MessageBox.show(f"Default Keyframe Range {kf_start} — {kf_end} has been set", 'MRF Markers not found!', 'ERROR')

        return kf_start, kf_end

class MRFTextureProperties(bpy.types.PropertyGroup):
    texture_path: bpy.props.StringProperty(
        name="Path",
        description="Path to the texture file",
        default="",
        maxlen=1024,
        subtype='NONE',
    )

class MATERIAL_PT_mrf_texture(bpy.types.Panel):
    bl_label = "MRF Texture"
    bl_context = "material"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    
    @classmethod
    def poll(cls, context):
        return context.material is not None

    def draw(self, context):
        layout = self.layout
        mat = context.material
        box = layout.box()
        box.prop(mat.mrf_texture_props, "texture_path")

def draw_func(self, context):
    layout = self.layout
    mat = context.material
    if mat is not None:
        box = layout.box()
        box.label(text="MRF Texture")
        box.prop(mat.mrf_texture_props, "texture_path")

def menu_func_import(self, context):
    self.layout.operator(ImportMRFOperator.bl_idname, text="Warcraft MORF (.mrf)")

def menu_func_export(self, context):
    self.layout.operator(ExportMRFOperator.bl_idname, text="Warcraft MORF (.mrf)")

def register():
    bpy.utils.register_class(MRFTextureProperties)
    bpy.utils.register_class(MATERIAL_PT_mrf_texture)
    bpy.utils.register_class(ImportMRFOperator)
    bpy.utils.register_class(ExportMRFOperator)
    bpy.types.Material.mrf_texture_props = bpy.props.PointerProperty(type=MRFTextureProperties)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)
def unregister():
    bpy.utils.unregister_class(MRFTextureProperties)
    bpy.utils.unregister_class(MATERIAL_PT_mrf_texture)
    bpy.utils.unregister_class(ImportMRFOperator)
    bpy.utils.unregister_class(ExportMRFOperator)
    del bpy.types.Material.mrf_texture_props
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)
