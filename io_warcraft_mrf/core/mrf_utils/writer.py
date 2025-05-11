# See spec for details: https://github.com/wiselencave/Warcraft_MRF_Blender/blob/main/mrf_spec.md

from os import path, makedirs
from io import BytesIO
from typing import List, Tuple
from .model_data import ModelData
from .header import Header
from .binary_utils import (
    write_uint32, write_float, write_vector2, write_vector3,
    write_triangle, align16
)


class MRFWriter:
    # Signature field: occupies 24 unused bytes in the header.
    # Can be used for export metadata or custom tool identifiers.
    _DEFAULT_SIGNATURE = b'Exported by Wiselen'

    def __init__(self, model: ModelData, signature: bool = True, make_game_copy: bool = False):
        self.model = model
        self.buffer = BytesIO()
        self.offsets = {}
        self.signature = signature
        self.make_game_copy = make_game_copy

    def write(self, file_path: str):
        self._write_header_stub()
        self._write_chunks()
        self._patch_header_offsets()

        with open(file_path, 'wb') as f:
            f.write(self.buffer.getvalue())
      
        if self.make_game_copy:
            self._make_game_ready_copy(file_path)

    def _write_header_stub(self):
        m = self.model
        header_start = self.buffer.tell()

        self.buffer.write(b'Morf')
        self.buffer.write(write_uint32(m.header.nFrames))
        self.buffer.write(write_uint32(m.header.nVerts))
        self.buffer.write(write_uint32(m.header.nIndices))
        self.buffer.write(write_float(m.header.frameDuration))
        self.buffer.write(write_vector3(m.header.pivot))
        self.buffer.write(write_float(m.header.boundsRadius))
        self.buffer.write(write_float(m.header.elapsedTime))
        self.buffer.write(write_uint32(m.header.debugFlag))

        # 24-byte unused field (6 x uint32) — ignored by the game parser.
        # Can be used for custom metadata like export signatures.
        self.buffer.write(self._build_reserved_data_field())

        self.offsets['texture'] = self.buffer.tell(); self.buffer.write(b'\x00' * 4)
        self.offsets['faces'] = self.buffer.tell(); self.buffer.write(b'\x00' * 4)
        self.offsets['mapping'] = self.buffer.tell(); self.buffer.write(b'\x00' * 4)
        self.offsets['keyframes'] = self.buffer.tell()

        for _ in range(m.header.nFrames):
            self.buffer.write(b'\x00' * 4)

        # Explicit 16-byte alignment padding after header
        header_end = self.buffer.tell()
        padding = (16 - (header_end - header_start) % 16) % 16
        self.buffer.write(b'\x00' * padding)


    def _write_chunks(self):
        self.chunk_positions = {}

        # Texture path
        self.chunk_positions['texture'] = self.buffer.tell()
        self.buffer.write(self._build_texture_chunk())

        # Face data
        self.chunk_positions['faces'] = self.buffer.tell()
        self.buffer.write(self._build_faces_chunk())

        # Mapping data
        self.chunk_positions['mapping'] = self.buffer.tell()
        self.buffer.write(self._build_mapping_chunk())

        # Keyframes
        self.keyframe_offsets = []
        for frame in self.model.keyframes:
            self.keyframe_offsets.append(self.buffer.tell())
            self.buffer.write(self._build_keyframe_chunk(frame))

    def _patch_header_offsets(self):
        self.buffer.seek(self.offsets['texture'])
        self.buffer.write(write_uint32(self.chunk_positions['texture']))

        self.buffer.seek(self.offsets['faces'])
        self.buffer.write(write_uint32(self.chunk_positions['faces']))

        self.buffer.seek(self.offsets['mapping'])
        self.buffer.write(write_uint32(self.chunk_positions['mapping']))

        self.buffer.seek(self.offsets['keyframes'])
        for offset in self.keyframe_offsets:
            self.buffer.write(write_uint32(offset))

    def _build_texture_chunk(self) -> bytes:
        data = self.model.texture_path.encode('ascii')
        return align16(data)

    def _build_faces_chunk(self) -> bytes:
        raw = b''.join(write_triangle(f) for f in self.model.faces)
        return align16(raw)

    def _build_mapping_chunk(self) -> bytes:
        raw = b''.join(write_vector2((u, 1 - v)) for u, v in self.model.uvs)
        return align16(raw)

    def _build_keyframe_chunk(self, keyframe: List[Tuple[Tuple[float, float, float], Tuple[float, float, float]]]) -> bytes:
        raw = b''.join(write_vector3(pos) + write_vector3(normal) for pos, normal in keyframe)
        return align16(raw)
        
    def _make_game_ready_copy(self, original_path: str):
        """
        Creates a game-ready copy of the file in:
        doodads\cinematic\\arthasillidanfight\
        (relative to the export directory)
        The filename is prefixed with 'arthascape'.
        """
        export_dir = path.dirname(original_path)
        rel_folder = path.join(export_dir, "doodads", "cinematic", "arthasillidanfight")
        makedirs(rel_folder, exist_ok=True)

        base_name = path.basename(original_path)
        name, ext = path.splitext(base_name)
        new_name = f"arthascape{name}{ext}"
        new_path = path.join(rel_folder, new_name)

        with open(new_path, 'wb') as f:
            f.write(self.buffer.getvalue())
    
    def _build_reserved_data_field(self):
        """
        Writes the 24-byte reserved field in the header:
        - If reserved_data is provided, writes it as 6 x uint32, even if all are zeros.
        - If not, writes the signature if enabled.
        - If neither, writes 24 bytes of null.
        """
        reserved_data = self.model.header.reserved_data
        buffer = BytesIO()

        if reserved_data is not None and len(reserved_data) == 6:
            for value in reserved_data:
                if not isinstance(value, int):
                    raise ValueError(f"Invalid type in reserved_data: expected int, got {type(value)}")
                buffer.write(write_uint32(value))
            return buffer.getvalue()

        if self.signature:
            raw = self._DEFAULT_SIGNATURE
            buffer.write(raw[:24].ljust(24, b'\x00'))
            return buffer.getvalue()

        buffer.write(b'\x00' * 24)
        return buffer.getvalue()