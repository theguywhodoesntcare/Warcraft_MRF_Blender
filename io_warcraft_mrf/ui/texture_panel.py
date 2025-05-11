import bpy

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
