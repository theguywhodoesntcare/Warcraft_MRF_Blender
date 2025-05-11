# See spec for details: https://github.com/wiselencave/Warcraft_MRF_Blender/blob/main/mrf_spec.md

from dataclasses import dataclass
from typing import List, Tuple
from .header import Header


@dataclass
class ModelData:
    header: Header
    texture_path: str
    faces: List[Tuple[int, int, int]]
    uvs: List[Tuple[float, float]]
    keyframes: List[List[Tuple[Tuple[float, float, float], Tuple[float, float, float]]]]
