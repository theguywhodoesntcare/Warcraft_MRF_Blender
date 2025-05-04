*Unofficial Specification for the .mrf (Morf) File Format for Warcraft III*

<hr>

# Data types 

| Name  | Description |
|------|-------|
| **byte** | 1 byte |
| **uint16** | 2 byte unsigned integer (Little-Endian) |
| **uint32** | 4 byte unsigned integer (Little-Endian) |
| **float** | 4 byte floating point number (Little-Endian) |
| **str** | string (not null-terminated)|

### Derived data types
| Name  | Description |
|------|-------|
| **vector3** | 3 floats (X, Y, Z) |
| **vector2** | 2 floats (U, V) |
| **triangle** | 3 uint16 (vertex 0 ID, vertex 1 ID, vertex 2 ID) |

# Chunk Structure
The file consists of a header followed by multiple logical chunks, stored sequentially. Chunks do not have explicit identifiers or length fields; their locations are determined by offsets defined in the header.

**Chunks are typically aligned to 16-byte boundaries. Padding with zeros to reach alignment is strongly recommended if a chunk’s length is not already a multiple of 16 bytes, although the game parser itself does not enforce this requirement.**

- Header
- Texture Path
- Face Data
- Mapping Data
- Keyframe 0 (first)
- ...
- Keyframe N (last)

# Chunks Description

## Header
Header contains the magic id, 3D model specification and offsets of chunks.

#### Chunk structure
| Type  | Description |
|------|-------|
| **byte[4]** | Magic string `Morf`, represented as ASCII bytes: `4D 6F 72 66` |
| **uint32** | Number of keyframes (used as `nFrames`) |
| **uint32** | Number of vertices (used as `nVerts`) |
| **uint32** | Number of face indices (used as `nIndices`) |
| **float** | ``frameDuration``. Interval between frames or frame duration in seconds |
| **vector3** | Pivot point. Has no effect in game |
| **float** | Bounds radius. Has no effect in game |
| **float** | Elapsed Time. Animation playback offset in seconds. Defines how far into the animation playback begins. Must satisfy ``0.0 <= elapsedTime <= (nFrames - 1) × frameDuration``
| **uint32** | Debug flag. Reserved for internal development use. Should be ``0``. Non-zero values may trigger assertions or debug checks in development builds, but have no effect in retail versions
| **uint32[6]** | Ignored. Can contain any arbitrary data, typically zeros |
| **uint32**  | Offset of Texture Path |
| **uint32**  | Offset of Face Data |
| **uint32**  | Offset of Mapping Data |
| **uint32[nFrames]**  | Offsets of keyframes. Starting from keyframe `0` and ending with keyframe `nFrames - 1` |
| **byte[]** | Padding to align to the next 16-byte boundary (if necessary) |

## Texture Path
Warcraft engine parses the string from the beginning of the chunk to the first dot character (`.`). 
After the dot there may be zeros or any arbitrary data. Accordingly, the extension of the texture file is not required.
#### Chunk structure
| Type  | Description |
|------|-------|
| **str** | Texture path  |
| **byte[]** | Padding to align to the next 16-byte boundary (if necessary) |

## Face Data
Each face is represented as three `uint16` with vertex numbers. All faces go one after another. The number of faces is in the [Header](#header).
#### Chunk structure
| Type  | Description |
|------|-------|
| **triangle[nIndices / 3]** | Face (3 vertex IDs). Starting from face `0` and ending with face `nIndices / 3 - 1`  |
| **byte[]** | Padding to align to the next 16-byte boundary (if necessary) |

## Mapping Data
`U` and `V` are stored for each vertex. We can represent this as `vector2`. 
The number of vertices is in the [Header](#header). 

**Note**: The V coordinate is flipped (`v = 1 - v`), following the DirectX UV convention.

#### Chunk structure
| Type  | Description |
|------|-------|
| **vector2[nVerts]** | Vertex UV coordinates. Starting from vertex `0` and ending with vertex `nVerts - 1` |
| **byte[]** | Padding to align to the next 16-byte boundary (if necessary) |

## Keyframe 
The `vector3` of the absolute (world) position of the vertex, and the `vector3` of its normal in a given frame are stored here. Repeats for each vertex.  
Each keyframe has its own chunk. The number of keyframes is in the [Header](#header).
#### Chunk structure
| Type  | Description |
|------|-------|
| **(vector3, vector3)[nVerts]** | Vertex position and vertex normal. Each vertex stores a position followed by its normal, in an interleaved layout. Starting from vertex `0` and ending with vertex `nVerts - 1` |
| **byte[]** | Padding to align to the next 16-byte boundary (if necessary) |