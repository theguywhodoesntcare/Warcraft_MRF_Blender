import bpy
from bpy_extras.io_utils import ImportHelper
from bpy.types import Operator
from ..core.mrf_utils.parser import MRFParser
from ..core.importer import MRFImporter

class ImportMRFOperator(Operator, ImportHelper):
    """Import MRF"""
    bl_idname = "import.mrf"
    bl_label = "Import MRF"
    filename_ext = ".mrf"

    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    filter_glob: bpy.props.StringProperty(default="*.mrf", options={'HIDDEN'})
    divisor: bpy.props.FloatProperty(name="Divisor", default=50.0, min=1.0)
    shade_smooth: bpy.props.BoolProperty(name="Shade Smooth", description="Apply Shade Smooth to imported mesh", default=False)

    def draw(self, context):
        layout = self.layout
        layout.label(text="Import settings:")
        box = layout.box()
        box.label(text="Warcraft sizes will be too large for Blender!", icon='ERROR')
        box.label(text="Use a divisor to reduce model by N times")
        box.prop(self, 'divisor')
        layout.label(text="Options:")
        layout.prop(self, 'shade_smooth')

    def check(self, context):
        return True

    def execute(self, context):
        try:
            parser = MRFParser(self.filepath)
            parser.read()
            importer = MRFImporter(parser.data, divisor=self.divisor, shadesmooth=self.shade_smooth)
            importer.import_model()
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Failed to import MRF: {e}")
            return {'CANCELLED'}
