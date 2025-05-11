from ..utils.message_box import MessageBox
import bpy

class ExportContextBuilder:
    DEFAULT_TEXTURE = "Textures/white"
    DEFAULT_RANGE = (0, 29)

    MARKER_RANGE_NAME = "MRF"
    MARKER_ELAPSED_NAME = "MRF_START"

    def __init__(self, obj):
        self.obj = obj

    def get_texture_path(self):
        mat = self.obj.active_material
        if mat and mat.mrf_texture_props.texture_path:
            return mat.mrf_texture_props.texture_path
        MessageBox.show(f"Default texture set: {self.DEFAULT_TEXTURE}", "No texture found", "ERROR")
        return self.DEFAULT_TEXTURE

    def get_keyframe_range(self):
        markers = [m for m in bpy.context.scene.timeline_markers if m.name.upper() == self.MARKER_RANGE_NAME]
        if len(markers) >= 2:
            markers.sort(key=lambda m: m.frame)
            return markers[0].frame, markers[1].frame
        MessageBox.show(f"Default keyframe range {self.DEFAULT_RANGE} used", f"Markers '{self.MARKER_RANGE_NAME}' not found!", "ERROR")
        return self.DEFAULT_RANGE

    def get_elapsed_marker_frame(self, start: int, end: int) -> int:
        marker = next((m for m in bpy.context.scene.timeline_markers if m.name.upper() == self.MARKER_ELAPSED_NAME), None)
        if marker and start <= marker.frame <= end:
            return marker.frame
        return start
