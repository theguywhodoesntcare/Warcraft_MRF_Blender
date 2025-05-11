import struct
from typing import BinaryIO, Tuple

# === Reading ===

def read_byte(f: BinaryIO) -> int:
    return struct.unpack('<B', f.read(1))[0]

def read_uint16(f: BinaryIO) -> int:
    return struct.unpack('<H', f.read(2))[0]

def read_uint32(f: BinaryIO) -> int:
    return struct.unpack('<I', f.read(4))[0]

def read_float(f: BinaryIO) -> float:
    return struct.unpack('<f', f.read(4))[0]

def read_vector2(f: BinaryIO) -> Tuple[float, float]:
    return struct.unpack('<ff', f.read(8))

def read_vector3(f: BinaryIO) -> Tuple[float, float, float]:
    return struct.unpack('<fff', f.read(12))

def read_triangle(f: BinaryIO) -> Tuple[int, int, int]:
    return struct.unpack('<HHH', f.read(6))


# === Writing ===

def write_byte(value: int) -> bytes:
    return struct.pack('<B', value)

def write_uint16(value: int) -> bytes:
    return struct.pack('<H', value)

def write_uint32(value: int) -> bytes:
    return struct.pack('<I', value)

def write_float(value: float) -> bytes:
    return struct.pack('<f', value)

def write_vector2(v: Tuple[float, float]) -> bytes:
    return struct.pack('<ff', *v)

def write_vector3(v: Tuple[float, float, float]) -> bytes:
    return struct.pack('<fff', *v)

def write_triangle(t: Tuple[int, int, int]) -> bytes:
    return struct.pack('<HHH', *t)


# === Utility ===

def align16(data: bytes) -> bytes:
    padding = (16 - len(data) % 16) % 16
    return data + b'\x00' * padding
