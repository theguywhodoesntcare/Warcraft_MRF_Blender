*Written by theguywhodoesntcare (sorry, I'm not a native English speaker lol). RU version hosted on XGM [here](https://xgm.guru/p/wc3/morf).*

The format specification is in the [mrf_spec.md](mrf_spec.md) file.

# Introduction

I do not have access to the Warcraft source code and cannot know exactly all the details of the MRF format and the details of parsing this format by the game. This information and [specification](mrf_spec.md) is based solely on the study of six existing MRF files and experimental data obtained by me.

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