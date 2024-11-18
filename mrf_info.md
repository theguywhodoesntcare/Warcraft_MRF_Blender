*Written by theguywhodoesntcare (sorry, I'm not a native English speaker lol)*


# Introduction

I do not have access to the Warcraft source code and cannot know exactly all the details of the MRF format and the details of parsing this format by the game. This specification is based solely on the study of six existing MRF files and experimental data obtained by me.

# Description

.mrf is a three-dimensional model format that contains one vertex animation. These models were used by Blizzard for Arthas' cape in the classic cinematic model of the battle between Arthas and Illidan.

Speaking of Reforged, it seems that the correct render of the MRF is only possible in the classic version of the graphic (SD), while in the HD there are some troubles with blending.

An array of triangles (faces), a UV Mapping and a path to a image texture are stored in the model as static data.
The vertex data is divided into an array of keyframes. Each keyframe is represented as an array of coordinates and normals for each vertex. Keyframes replace each other at a given frequency, and the graphics engine interpolates the movement of the mesh between them.  

It looks like MRF only supports one static texture without blending. Transparent pixels are rendered as black. 

# Import description

MRF files are linked to the MDX/MDL model through tracks of Event Objects (EVTS) with ***MRF*** (for example MRFx0000) and ***MRD*** (for example MRDx0000) identifiers.

The ID of the event object is part of the path to the mrf file. A constant part of this path is **doodads\cinematic\arthasillidanfight\arthascape**. In fact, ID is nothing more than an arbitrary string.  
Here are examples in the table.

| MRF (show)  | MRD (hide) | Path |
|------|-------|-------|
| MRFX**0000** | MRDX**0000** | *doodads\cinematic\arthasillidanfight\arthascape**0000**.mrf* |
| MRFX**12345** | MRDX**12345** | *doodads\cinematic\arthasillidanfight\arthascape**12345**.mrf* |
| MRFX**helloworld** | MRDX**helloworld** | *doodads\cinematic\arthasillidanfight\arthascape**helloworld**.mrf* |

Warcraft completely ignores the pivot point of the event object, as well as the translation, rotation and scaling tracks.

Since the link to the mrf is part of the MDX/MDL, theoretically MRF can be played in any space where models can be played. But in fact, MRF *animation* is not supported everywhere.

There are three options to display the MRF model and play its animation:
- Output a SPRITE frame using a camera from the MDX/MDL model. 
*If a world frame is used as the parent, then the global lighting model (DNC with default directional light) from the current map will be used as the light source.*

- Native PlayModelCinematic(MDX/MDL model) function.  For example *PlayModelCinematic( "Doodads\\Cinematic\\ArthasIllidanFight\\ArthasIllidanFight.mdl" )*

- Using a model as a unit portrait. The portrait space uses the MDX internal camera, so we can also see the MRF animation.

As for the world space and the space of 3D menu screens and campaigns (in pre-reforged patches), MRF will also be rendered there, but only as a static object, that is, the mesh from zero frame of the MRF will be loaded.

At the same time, MRF will not inherit the coordinates of the MDX model, that is, the world coordinates from zero frame of the MRF itself will be used.

**Based on the above, we can understand that MPF animation works only in screen space and only during the game.**

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
