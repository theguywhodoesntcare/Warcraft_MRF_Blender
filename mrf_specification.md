# Introduction

I do not have access to the Warcraft source code and cannot know exactly all the details of the MRF format and the details of parsing this format by the game. This specification is based solely on the study of six existing MRF files and experimental data obtained by me.

# Description

.mrf is a three-dimensional model format that contains one vertex animation. These models were used by Blizzard for Arthas' cape in the cinematic model of the battle between Arthas and Illidan.

An array of triangles (faces), a UV Mapping and a path to a image texture are stored in the model as static data.
The vertex data is divided into an array of keyframes. Each keyframe is represented as an array of coordinates and normals for each vertex. Keyframes replace each other at a given frequency, and the graphics engine interpolates the movement of the mesh between them.  

MRF files are linked to the MDL model through tracks of Event Objects with ***MRF*** (for example MRFx0000) and ***MRD*** (for example MRDx0000) identifiers.

In the original Warcraft, there are two options to display the MRF model and play its animation:
- Output a SPRITE frame using a camera from the MDX/MDL model.
- Native PlayModelCinematic(MDX/MDL model) function.  For example *PlayModelCinematic( "Doodads\\Cinematic\\ArthasIllidanFight\\ArthasIllidanFight.mdl" )*

# Data types

| Name  | Description |
|------|-------|
| **word** | 2 byte integer |
| **dword** | 4 byte integer |
| **float** | 4 byte floating point number |
| **strn** | non-terminated string  |

### Derived data types
| Name  | Description |
|------|-------|
| **vector3** | 3 floats (X, Y, Z) |
| **vector2** | 2 floats (U, V) |
| **triangle** | 3 words (vertex 0 id, vertex 1 id, vertex 2 id) |



# Chunk Array
The structure of chunks is linear, that is, they simply follow each other and do not have any identifiers. **Chunk lengths must be a multiple of 16**.  
Chunk offsets are stored in the offsets table.

- Data Chunk (Offset 0x0000) 
- Offset Table (Offset 0x0040 or 64) 
- Texture Path
- Face Data
- Mapping Data
- Keyframe 0
- ...
- Keyframe N

# Chunks Description


## Data Chunk
If I understand correctly, it should have a fixed size of 64. 
All the data below goes one after another. The rest of the chunk should be filled with zeros or any other arbitrary data.
    
        Type    Description

        strn    Magic String. 4 byte "Morf" identifier.
        dword   Number of keyframes.
        dword   Number of vertices.
        dword   Number of verices of triangles. Nfaces = Nverts / 3.
        float   Interval between frames or frame duration. In a sense, the parameter is inverse FPS (1/fps).
        vector3 (?) Presumably Pivot Point. Has no effect in game.
        float   (?) Presumably Bounds Radius. Has no effect in game.

## Offset Table
There are only dwords here.  
Each dword stores the offset of some chunk. The number of values equals the number of keyframes +4.  

It looks like this chunk should always start at offset 0x0040.  
An example of such a table is below. Offsets are indicated relative to the beginning of the chunk.
        
        Offset  Description

        0x0000  It's always zeros. Maybe this means offset of the data chunk?
        0x0004  Offset of Texture Path
        0x0008  Offset of Face Data
        0x000C  Offset of Mapping Data
        0x0010  Offset of Keyframe 0
        ...
        Similarly, the offsets of the next key frames continue until the end (last keyframe).

## Texture Path
Warcraft engine parses the string from the beginning of the chunk to the first dot character (.). 
After the dot there may be zeros or any arbitrary data. Accordingly, the extension of the texture file is not required.

        Type    Description

        strn    Texture path

## Face Data
Each face is represented as three words with vertex numbers. All faces go one after another.  
We can get the number of faces from the data chunk.

        Type        Description

        triangle    face 0 
        ...
        triangle    face N 

## Mapping Data
U and V are stored for each vertex. We can represent this as vector2.  
The number of vertices is in the data chunk.

        Type        Description

        vector2     vertex 0 UV
        ...
        vector2     vertex N UV

## Keyframe 
The vector3 of the absolute (world) position of the vertex, and the vector3 of its normal in a given frame are stored here. Repeats for each vertex.  
Each keyframe has its own chunk.

        Type        Description

        vector3     vertex 0 position 
        vector3     vertex 0 normal 
        ...
        vector3     vertex N position 
        vector3     vertex N normal 
    




