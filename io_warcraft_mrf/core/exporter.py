import bpy
from dataclasses import dataclass
from typing import Tuple, List
from mathutils import Vector

from ..core.mrf_utils.header import Header
from ..core.mrf_utils.model_data import ModelData

class MRFExporter:
    def __init__(self, obj: bpy.types.Object, scale_factor: float, texture_path: str, kf_range: Tuple[int, int], elapsed_frame: int, 
                    deduplicate: bool = True, 
                    reverse_keyframes: bool = False, 
                    auto_bounds: bool = False, 
                    playback_delay: float = 0):
        
        self.obj = obj
        self.scale = scale_factor
        self.texture_path = texture_path
        self.kf_start, self.kf_end = kf_range

        self.elapsed_frame = elapsed_frame
        self.deduplicate = deduplicate
        self.reverse_keyframes = reverse_keyframes
        self.auto_bounds = auto_bounds
        self.playback_delay = playback_delay

    def export_to_modeldata(self) -> ModelData:
        uniq_vertices, triangles_list = self.get_mesh_data()
        uvs = [tuple(v['uv']) for v in uniq_vertices]
        nverts = len(uniq_vertices)

        keyframes, duration = self.get_keyframes(uniq_vertices)

        elapsed_time = self._calculate_elapsed_time(duration)

        base_vertices = [v['position'] for v in uniq_vertices]

        pivot = (0.0, 0.0, 0.0)
        bounds_radius = 0.0

        if self.auto_bounds:
            pivot = self._compute_pivot(base_vertices)
            bounds_radius = self._compute_bounds_radius(base_vertices, pivot)

        header = Header(
            nFrames=len(keyframes),
            nVerts=nverts,
            nIndices=len(triangles_list) * 3,
            frameDuration=duration,
            pivot=pivot,  
            boundsRadius=bounds_radius,
            elapsedTime=elapsed_time,
            debugFlag=0,
            offsets={},
        )

        model = ModelData(
            header=header,
            texture_path=self.texture_path,
            faces=triangles_list,
            uvs=uvs,
            keyframes=keyframes
        )

        return model

    def get_mesh_data(self):
        mesh = self.obj.data
        uv_layer = mesh.uv_layers.active.data

        if self.deduplicate:
            return self._get_deduplicated_mesh(mesh, uv_layer)
        else:
            return self._get_raw_mesh(mesh, uv_layer)

    def _get_vertex_key(self, vert, uv) -> Tuple:
        return (
            round(vert.co.x, 6), round(vert.co.y, 6), round(vert.co.z, 6),
            round(vert.normal.x, 6), round(vert.normal.y, 6), round(vert.normal.z, 6),
            round(uv.x, 6), round(uv.y, 6)
        )

    def _make_vert_info(self, vert, uv) -> dict:
        return {
            'index': vert.index,
            'position': vert.co.copy(),
            'normal': vert.normal.copy(),
            'uv': uv.copy()
        }

    def _get_deduplicated_mesh(self, mesh, uv_layer):
        vertex_map = {}
        uniq_vertices = []
        triangles = []

        for tri in mesh.loop_triangles:
            triangle = []
            for loop_index in tri.loops:
                loop = mesh.loops[loop_index]
                vert = mesh.vertices[loop.vertex_index]
                uv = uv_layer[loop.index].uv

                key = self._get_vertex_key(vert, uv)
                if key not in vertex_map:
                    vertex_map[key] = len(uniq_vertices)
                    uniq_vertices.append(self._make_vert_info(vert, uv))

                triangle.append(vertex_map[key])
            triangles.append(tuple(triangle))

        return uniq_vertices, triangles

    def _get_raw_mesh(self, mesh, uv_layer):
        uniq_vertices = []
        triangles = []

        for tri in mesh.loop_triangles:
            triangle = []
            for loop_index in tri.loops:
                loop = mesh.loops[loop_index]
                vert = mesh.vertices[loop.vertex_index]
                uv = uv_layer[loop.index].uv

                index = len(uniq_vertices)
                uniq_vertices.append(self._make_vert_info(vert, uv))
                triangle.append(index)
            triangles.append(tuple(triangle))

        return uniq_vertices, triangles
    
    def _compute_pivot(self, vertices: List[Vector]) -> Tuple[float, float, float]:
        center = sum((Vector(v) for v in vertices), Vector()) / len(vertices)
        return tuple(center * self.scale)

    def _compute_bounds_radius(self, vertices: List[Vector], pivot: Tuple[float, float, float]) -> float:
        pivot_vec = Vector(pivot)
        return max((Vector(v) * self.scale - pivot_vec).length for v in vertices)
    
    def _calculate_elapsed_time(self, duration: float) -> float:
        if self.playback_delay > 0.0:
            return self.playback_delay
        if self.elapsed_frame == self.kf_start:
            return 0.0

        if self.reverse_keyframes:
            offset = self.kf_end - self.elapsed_frame
        else:
            offset = self.elapsed_frame - self.kf_start

        return max(0.0, offset * duration)


    def get_keyframes(self, vertex_list):
        scene = bpy.context.scene
        old_frame = scene.frame_current
        fps = scene.render.fps
        duration = 1.0 / fps

        keyframes = []

        frame_range = range(self.kf_start, self.kf_end + 1)
        if self.reverse_keyframes:
            frame_range = reversed(frame_range)

        for frame in frame_range:
            scene.frame_set(frame)
            depsgraph = bpy.context.evaluated_depsgraph_get()
            eval_obj = self.obj.evaluated_get(depsgraph)
            mesh = eval_obj.to_mesh()

            frame_data = []
            for vert_info in vertex_list:
                v = mesh.vertices[vert_info['index']]
                pos = tuple((self.obj.matrix_world @ v.co) * self.scale)
                norm = tuple(v.normal)
                frame_data.append((pos, norm))

            keyframes.append(frame_data)
            eval_obj.to_mesh_clear()

        scene.frame_set(old_frame)
        return keyframes, duration