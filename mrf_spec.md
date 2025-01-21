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

# Chunk Array
The structure of chunks is linear, that is, they simply follow each other. Chunk do not have any identifiers, their offsets are stored in the offsets table.  
**Chunk lengths should be a multiple of 16**. Any remaining space can be padded with zeros.


- Header (Fixed size: 64 bytes) 
- Offset Table (Offset 0x0040 or 64) 
- Texture Path
- Face Data
- Mapping Data
- Keyframe 0 (first)
- ...
- Keyframe N (last)

# Chunks Description

## Header
Header contains the magic id and the 3D model specification. It should have a fixed size of 64 bytes.

#### Chunk structure
| Type  | Description |
|------|-------|
| **byte[4]** | Magic String. 4 byte "Morf" identifier |
| **uint32** | Number of keyframes. *(var nKf)* |
| **uint32** | Number of vertices. *(var nVerts)* |
| **uint32** | Number of verices of triangles (loops or face corners). *(var nCorners)* |
| **float** | Interval between frames or frame duration in seconds. In a sense, the parameter is inverse FPS (1/fps) |
| **vector3** | (?) Presumably Pivot Point. Has no effect in game |
| **float** | (?) Presumably Bounds Radius. Has no effect in screen space but not sure about world space |
| **byte[28]** | Unused. Can contain 0x00 or any other arbitrary data |


## Offset Table
There are only uint32 here.  
Each uint32 stores the offset of some chunk. The number of values equals the number of keyframes +4.  

It looks like this chunk should always start at offset 0x0040.  

#### Chunk structure
| Type  | Description |
|-------|-------|
| **uint32**  | It's always zeros (0x0000). Maybe this means offset of the Header?  |
| **uint32**  | Offset of Texture Path |
| **uint32**  | Offset of Face Data |
| **uint32**  | Offset of Mapping Data |
| **uint32[nKf]**  | Offsets of keyframes. Starting from keyframe 0 and ending with keyframe **nKf - 1** |
| **byte[]** | Padding to align to the next 16-byte boundary (if necessary) |



## Texture Path
Warcraft engine parses the string from the beginning of the chunk to the first dot character (.). 
After the dot there may be zeros or any arbitrary data. Accordingly, the extension of the texture file is not required.
#### Chunk structure
| Type  | Description |
|------|-------|
| **str** | Texture path  |
| **byte[]** | Padding to align to the next 16-byte boundary (if necessary) |


## Face Data
Each face is represented as three uint16 with vertex numbers. All faces go one after another. The number of faces is in the Header.
#### Chunk structure
| Type  | Description |
|------|-------|
| **triangle[nCorners / 3]** | Face (3 vertex IDs). Starting from face 0 and ending with face **nCorners / 3 - 1**  |
| **byte[]** | Padding to align to the next 16-byte boundary (if necessary) |


## Mapping Data
U and V are stored for each vertex. We can represent this as vector2. 
The number of vertices is in the Header.  
**The V coordinate of the UV mapping is inverted in Warcraft 3 *(v = 1 - v)***.

#### Chunk structure
| Type  | Description |
|------|-------|
| **vector2[nVerts]** | Vertex UV coordinates. Starting from vertex 0 and ending with vertex **nVerts - 1** |
| **byte[]** | Padding to align to the next 16-byte boundary (if necessary) |



## Keyframe 
The vector3 of the absolute (world) position of the vertex, and the vector3 of its normal in a given frame are stored here. Repeats for each vertex.  
Each keyframe has its own chunk. The number of keyframes is in the Header.
#### Chunk structure
| Type  | Description |
|------|-------|
| **(vector3, vector3)[nVerts]** | Vertex position and vertex normal. Starting from vertex 0 and ending with vertex **nVerts - 1** |
| **byte[]** | Padding to align to the next 16-byte boundary (if necessary) |
