import bpy
from bpy_extras.io_utils import ExportHelper
from bpy.types import Operator
from ..utils.message_box import MessageBox
from ..core.exporter import MRFExporter
from ..core.mrf_utils.writer import MRFWriter
from .context_utils import ExportContextBuilder

class ExportMRFOperator(Operator, ExportHelper):
    """Export MRF"""
    bl_idname = "export.mrf"
    bl_label = "Export MRF"
    filename_ext = ".mrf"

    filter_glob: bpy.props.StringProperty(default="*.mrf", options={'HIDDEN'})
    scale_factor: bpy.props.FloatProperty(name="Scale Factor", default=50.0, min=0.01)
    deduplicate: bpy.props.BoolProperty(name="Deduplicate mesh", description="Removes duplicate vertices with same position, normal, and UV", default=True)
    reverse_keyframes: bpy.props.BoolProperty(name="Reverse Keyframes", description="Export keyframes in reverse order (from end to start)", default=False)
    auto_bounds: bpy.props.BoolProperty(name="Compute Pivot/Radius", description="Automatically compute pivot point and bounds radius from mesh geometry", default=False)
    playback_delay: bpy.props.FloatProperty(name="Playback delay", description="Set animation playback delay in seconds", default=0.0, min=0.0)
    author_sign: bpy.props.BoolProperty(name="Embed export signature", description="Adds a 24-byte signature to the unused header space. Disable for clean exports", default=True)
    game_format: bpy.props.BoolProperty(name="Pack for import", description="Make a copy and apply the path \"doodads/cinematic/arthasillidanfight/arthascape\" to it", default=False)

    def draw(self, context):
        def create_box(layout, label, icon, description, prop):
            box = layout.box()
            box.label(text=label, icon=icon)
            for line in description:
                box.label(text=line)
            box.prop(self, prop)
    
        layout = self.layout
        layout.label(text="Export settings:")
        
        layout.prop(self, 'game_format')
        layout.prop(self, 'author_sign')

        create_box(layout, "Scale Factor", 'ERROR',
                ["Blender sizes will be too small for Warcraft!", 
                    "Use a Scale Factor to scale model by N times."],
                'scale_factor')
        
        layout.label(text="Options:")

        create_box(layout, "Deduplicate Mesh", 'MESH_DATA', 
                ["Removes duplicate vertices with same position, normal, and UV.",
                    "Useful for optimizing size and animation data."],
                'deduplicate')

        create_box(layout, "Playback Delay", 'TIME', 
                ["Set animation playback delay in seconds.", 
                    "This option will overwrite the offset from the MRF_START marker."], 
                'playback_delay')

        create_box(layout, "Compute Pivot/Radius", 'PIVOT_BOUNDBOX', 
                ["Compute pivot point and bounds radius from mesh geometry.",
                    "Not guaranteed to match Blizzard software behavior!"], 
                'auto_bounds')

        create_box(layout, "Reverse Animation", 'PLAY_REVERSE', 
                ["Export keyframes from end to start (reversed playback)."], 
                'reverse_keyframes')


    def check(self, context):
        return True

    def invoke(self, context, event):
        if not any(obj.type == 'MESH' for obj in bpy.context.selected_objects):
            MessageBox.show('Error!', 'No Mesh Object Selected.', 'ERROR')
            return {'CANCELLED'}
        return ExportHelper.invoke(self, context, event)

    def execute(self, context):
        # Export selected mesh
        obj = bpy.context.active_object
        if not obj or obj.type != 'MESH':
            MessageBox.show('Error!', 'No Active Mesh Object.', 'ERROR')
            return {'CANCELLED'}

        try:
            ctx = ExportContextBuilder(obj)
            texture_path = ctx.get_texture_path()
            kf_start, kf_end = ctx.get_keyframe_range()
            elapsed_frame = ctx.get_elapsed_marker_frame(kf_start, kf_end)

            exporter = MRFExporter(obj, self.scale_factor, texture_path, (kf_start, kf_end), 
                                   elapsed_frame=elapsed_frame, 
                                   deduplicate=self.deduplicate, 
                                   reverse_keyframes=self.reverse_keyframes, 
                                   auto_bounds=self.auto_bounds,
                                   playback_delay=self.playback_delay
                                   )
            model_data = exporter.export_to_modeldata()
            file_path = self.filepath
            if not file_path.lower().endswith('.mrf'):
                file_path += '.mrf'

            writer = MRFWriter(model_data, signature=self.author_sign, make_game_copy=self.game_format)
            writer.write(file_path)

            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Failed to export MRF: {e}")
            return {'CANCELLED'}