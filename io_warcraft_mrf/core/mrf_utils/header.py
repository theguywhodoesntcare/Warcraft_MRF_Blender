# See spec for details: https://github.com/wiselencave/Warcraft_MRF_Blender/blob/main/mrf_spec.md
# Note: In this implementation, keyframe offsets are placed within the Header structure for convenience. 

from dataclasses import dataclass
from typing import Optional, Tuple, List


@dataclass
class Header:
    nFrames: int
    nVerts: int
    nIndices: int
    frameDuration: float
    pivot: Tuple[float, float, float]
    boundsRadius: float
    elapsedTime: float
    debugFlag: int
    offsets: dict  # keys: 'texture', 'faces', 'mapping', 'keyframes'
    reserved_data: Optional[Tuple[int, int, int, int, int, int]] = None