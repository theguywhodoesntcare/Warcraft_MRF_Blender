import os
import struct
import bpy
import bmesh
from mathutils import geometry
from . import MessageBox
#os.system('cls')

def save_morf(filepath, obj, scale_factor, texture_path, kf_range):
    def set_dword(data, value):
        data.extend(struct.pack('<I', value))
        return data

    def set_float(data, value):
        data.extend(struct.pack('<f', value))
        return data

    def set_str(data, value):
        b = value.encode('utf-8')
        data.extend(struct.pack('%ds' % len(b), b))
        return data

    def set_vector(data, vector):
        data.extend(struct.pack('<fff', *vector))
        return data

    def set_triangle(data, triangle):
        data.extend(struct.pack('<HHH', *triangle))
        return data

    def set_uv(data, uv):
        data.extend(struct.pack('<ff', *uv))
        return data

    def pad_chunk(data):
        #Fill the chunk with zeros so that its length is a multiple of 16
        padding = 16 - (len(data) % 16)
        
        if padding == 16:
            return data

        data.extend([0]*padding)
        return data

    def pad_chunk_size(data, chunk_size):
        #Fill the chunk with zeros so that its size is equal to the specified size
        padding = chunk_size - (len(data) % chunk_size)
        
        if padding == chunk_size:
            return data

        data.extend([0]*padding)
        return data

    def write_data_chunk(data, nkeyframes, nverts, nfaces, duration):
        set_str(data, 'Morf') #mrf id
        set_dword(data, nkeyframes) #Number of keyframes
        set_dword(data, nverts) #Number of vertices
        set_dword(data, nfaces * 3) #Number of vertices of triangles
        set_float(data, duration) #frame duration (1/fps)
        set_vector(data, (0, 0, 0)) # (?) Maybe Pivot
        set_float(data, 30) # (?) Maybe Bounds Radius

        data = pad_chunk_size(data, 64)
        return data

    def write_texture(path):
        data = bytearray()
        data = set_str(data, path)
        data = pad_chunk(data)
        return data
    
    def get_keyframes(obj, frame_start, frame_end):
        #Get vertex position and normals from every frame
        number = frame_end - frame_start + 1

        sce = bpy.context.scene
        animdata = bytearray()

        for f in range(frame_start, frame_end + 1):  #set frame range
            sce.frame_set(f)
            
            depsgraph = bpy.context.evaluated_depsgraph_get()
            
            mesh = obj.evaluated_get(depsgraph).to_mesh()
            
            framedata = bytearray()
            
            for v in mesh.vertices:
                global_coord = obj.matrix_world @ v.co
                global_coord = global_coord * scale_factor
                framedata = set_vector(framedata, global_coord)
                
                normal = v.normal
                framedata = set_vector(framedata, normal)
            
            framedata = pad_chunk(framedata)
            animdata.extend(framedata)
            
            obj.evaluated_get(depsgraph).to_mesh_clear()
            
        fps = bpy.context.scene.render.fps #get fps
        dur = 1/fps

        length = len(animdata)//number
        print('frame length: ', length)
        return animdata, number, dur, length

    def get_triangle_representation(obj):
        #Get faces in a triangular representation.
        #Currently the mesh is forced to be triangulated before export, so this is unnecessary
        #But in the future, triangulation must be excluded

        bpy.ops.object.mode_set(mode='EDIT')
        bm = bmesh.from_edit_mesh(obj.data)

        triangle_count = 0
        data = bytearray()
        for i, face in enumerate(bm.faces):
            triangle = ()
            #If a face has more than 3 vertices, divide it into triangles
            if len(face.verts) > 3:
                coords = [v.co for v in face.verts]
                triangles = geometry.tessellate_polygon([coords])

                for tri in triangles:
                    #print(f"face {i} = {tuple(face.verts[v].index for v in tri)}")
                    triangle = tuple(face.verts[v].index for v in tri)
                    triangle_count += 1
                    data = set_triangle(data, triangle)
            else:
                #print(f"face {i} = {tuple(v.index for v in face.verts)}")
                triangle = tuple(v.index for v in face.verts)
                triangle_count += 1
                data = set_triangle(data, triangle)

        bpy.ops.object.mode_set(mode='OBJECT')

        #print(f"Total number of triangles: {triangle_count}")

        data = pad_chunk(data)
        return data, triangle_count


    def get_uv_coords(obj):
        #why tf get uv is so hard?
        data = bytearray()
        if bpy.context.mode != 'EDIT_MESH':
            bpy.ops.object.mode_set(mode='EDIT')

        me = obj.data
        bm = bmesh.from_edit_mesh(me)

        uv_layer = bm.loops.layers.uv.verify()

        unique_uvs = {}

        for v in bm.verts:
            for l in v.link_loops:
                luv = l[uv_layer]

                if v.index in unique_uvs:
                    continue
                
                luv.uv.y = 1 - luv.uv.y #Mirror UV along the Y-axis
                unique_uvs[v.index] = luv.uv

        for vert_index, uv in unique_uvs.items():
            data = set_uv(data, uv)
            #print(f'Vertex index: {vert_index}, UV coordinates: {uv}')
        
        bm.free()
        data = pad_chunk(data)
        bpy.ops.object.mode_set(mode='OBJECT')

        return data


    def write_offset_table(kfcount, length):
        data = bytearray()
        data = set_dword(data, 0)

        #calculate table length
        table_length = (kfcount + 4) * 4
        if table_length % 16 != 0:
            table_length = ((table_length // 16) + 1) * 16

        offset = 64 + table_length
        data = set_dword(data, offset)

        offset += len(texturedata)
        data = set_dword(data, offset)

        offset += len(facesdata)
        data = set_dword(data, offset)

        offset += len(uvdata)
        data = set_dword(data, offset)

        for kf in range(kfcount):
            offset += length
            data = set_dword(data, offset)

        data = pad_chunk(data)
        return data


    #starting export

    #Triangulating an object in a scene is a bad approach
    #Rework needed!

    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.quads_convert_to_tris(quad_method='BEAUTY', ngon_method='BEAUTY')

    nvertices = len(obj.data.vertices)
    texturedata = write_texture(texture_path)
    facesdata, nfaces = get_triangle_representation(obj)
    uvdata = get_uv_coords(obj)
    animdata, kfcount, duration, length = get_keyframes(obj, kf_range[0], kf_range[1])
    offsettable = write_offset_table(kfcount, length)
    data_list = [offsettable, texturedata, facesdata, uvdata, animdata]
    
    mrfdata = bytearray()  
    mrfdata = write_data_chunk(mrfdata, kfcount, nvertices, nfaces, duration)
    
    for data in data_list:
        mrfdata.extend(data)
    
    with open(filepath, 'wb') as f:             
        f.write(mrfdata) 
