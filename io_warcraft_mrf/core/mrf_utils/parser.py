# See spec for details: https://github.com/wiselencave/Warcraft_MRF_Blender/blob/main/mrf_spec.md
from typing import List, Tuple, BinaryIO
from pathlib import Path

from .header import Header
from .model_data import ModelData
from .binary_utils import (
    read_uint32, read_float, read_vector3,
    read_vector2, read_triangle
)

class MRFParser:
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.data = None

    def read(self):
        with self.file_path.open('rb') as f:
            self.data = self._read_all(f)

    def _read_all(self, f: BinaryIO) -> ModelData:
        if f.read(4) != b'Morf':
            raise ValueError("Invalid magic header")

        nFrames = read_uint32(f)
        nVerts = read_uint32(f)
        nIndices = read_uint32(f)
        frameDuration = read_float(f)
        pivot = read_vector3(f)
        boundsRadius = read_float(f)
        elapsedTime = read_float(f)
        debugFlag = read_uint32(f)
        #_ = f.read(24)
        reserved_data = tuple(read_uint32(f) for _ in range(6))
        texture_offset = read_uint32(f)
        face_offset = read_uint32(f)
        mapping_offset = read_uint32(f)
        keyframe_offsets = [read_uint32(f) for _ in range(nFrames)]

        header = Header(
            nFrames=nFrames,
            nVerts=nVerts,
            nIndices=nIndices,
            frameDuration=frameDuration,
            pivot=pivot,
            boundsRadius=boundsRadius,
            elapsedTime=elapsedTime,
            debugFlag=debugFlag,
            reserved_data = reserved_data,
            offsets={
                'texture': texture_offset,
                'faces': face_offset,
                'mapping': mapping_offset,
                'keyframes': keyframe_offsets,
            }
        )

        texture_path = self._read_texture(f, texture_offset, face_offset)
        faces = self._read_faces(f, face_offset, nIndices)
        uvs = self._read_uvs(f, mapping_offset, nVerts)
        keyframes = [self._read_keyframe(f, offset, nVerts) for offset in keyframe_offsets]

        return ModelData(header, texture_path, faces, uvs, keyframes)

    def _read_texture(self, f: BinaryIO, offset: int, face_offset: int) -> str:
        length = face_offset - offset
        f.seek(offset)
        raw = f.read(length)
        raw = raw.rstrip(b'\x00')
        return raw.decode('ascii')

    def _read_faces(self, f: BinaryIO, offset: int, nIndices: int) -> List[Tuple[int, int, int]]:
        f.seek(offset)
        face_count = nIndices // 3
        faces = [read_triangle(f) for _ in range(face_count)]
        return faces

    def _read_uvs(self, f: BinaryIO, offset: int, nVerts: int) -> List[Tuple[float, float]]:
        f.seek(offset)
        uvs = [(u, 1 - v) for _ in range(nVerts) for u, v in [read_vector2(f)]]
        return uvs

    def _read_keyframe(self, f: BinaryIO, offset: int, nVerts: int) -> List[Tuple[Tuple[float, float, float], Tuple[float, float, float]]]:
        f.seek(offset)
        verts = []
        for _ in range(nVerts):
            pos = read_vector3(f)
            normal = read_vector3(f)
            verts.append((pos, normal))
        return verts