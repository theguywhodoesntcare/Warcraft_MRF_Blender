import bpy
from mathutils import Vector
from ..utils.message_box import MessageBox


class MRFImporter:
    def __init__(self, model_data, divisor=1.0, shadesmooth=True):
        self.model_data = model_data
        self.divisor = divisor
        self.shadesmooth = shadesmooth

    def import_model(self):
        data = self.model_data
        header = data.header

        keyframes = [
            [vertex[0] for vertex in frame]  #! Skip normals
            for frame in data.keyframes
        ]
        
        obj = self.create_mesh(
            verts=keyframes,
            faces=data.faces,
            uv=data.uvs,
            pivot=header.pivot,
            filename="MRF_Object"
        )
        self.set_material(obj, data.texture_path)
        MessageBox.show(data.texture_path, "MRF Texture path:", 'TEXTURE')

        # Scene settings
        scene = bpy.context.scene
        scene.render.fps = round(1 / header.frameDuration)
        scene.frame_start = self._get_start_frame(header.elapsedTime, header.frameDuration, header.nFrames)
        scene.frame_end = header.nFrames
        scene.frame_set(0)

    def set_material(self, obj, texture):
        mat = bpy.data.materials.new(name='MRFMaterial')
        mat.mrf_texture_props.texture_path = texture
        obj.data.materials.append(mat)

    def create_mesh(self, verts, faces, uv, pivot, filename):
        # Pivot point and Bounds radius are ignored in this importer.
        # If necessary to use they must be scaled using a divisor, as well as vertices!

        mesh = bpy.data.meshes.new(name=filename)
        obj = bpy.data.objects.new(name=filename, object_data=mesh)
        bpy.context.collection.objects.link(obj)

        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)

        mesh.from_pydata(
            [Vector(v) / self.divisor for v in verts[0]],
            [],
            faces
        )
        mesh.update()

        uv_layer = mesh.uv_layers.new(name='New UV Map')
        for poly in mesh.polygons:
            for loop_index in poly.loop_indices:
                loop = mesh.loops[loop_index]
                uv_layer.data[loop.index].uv = uv[loop.vertex_index]

        if self.shadesmooth:
            bpy.ops.object.shade_smooth()

        self.create_shapeanim(obj, verts)
        return obj

    def create_shapeanim(self, obj, verts):
        for frame, vertices in enumerate(verts):
            shape_key = obj.shape_key_add(name=f"Frame{frame+1}")
            for i, coord in enumerate(vertices):
                shape_key.data[i].co = Vector(coord) / self.divisor

            shape_key.value = 0.0
            if frame != 0: # Position 0 is reserved
                shape_key.keyframe_insert(data_path="value", frame=frame)
                shape_key.value = 1.0
                shape_key.keyframe_insert(data_path="value", frame=frame+1)
            if frame < len(verts) - 1:
                shape_key.value = 0.0
                shape_key.keyframe_insert(data_path="value", frame=frame+2)

    def _get_start_frame(self, elapsed_time: float, frame_duration: float, n_frames: int) -> int:
        # Convert elapsed time to Blender frame index, clamped to [1, nFrames - 1]
        
        if frame_duration <= 0 or n_frames < 2:
            return 1

        frame_index = int(elapsed_time / frame_duration) + 1
        return max(1, min(frame_index, n_frames - 1))