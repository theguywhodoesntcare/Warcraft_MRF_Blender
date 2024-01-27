import os
import struct
import bpy
import bmesh
from mathutils import Vector, geometry
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
        u, v = uv
        v = 1 - v  #mirror Y
        data.extend(struct.pack('<ff', u, v))
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
    
    def get_keyframes(obj, vertices_list, frame_start, frame_end):
        #Get vertex position and normals from every frame
        number = frame_end - frame_start + 1

        sce = bpy.context.scene
        animdata = bytearray()

        for f in range(frame_start, frame_end + 1):  #set frame range
            sce.frame_set(f)
            
            depsgraph = bpy.context.evaluated_depsgraph_get()
            
            mesh = obj.evaluated_get(depsgraph).to_mesh()
            
            framedata = bytearray()
            
            for vert_info in vertices_list:
                v = mesh.vertices[vert_info['index']]

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
    
    def write_faces(faces):
        triangle_count = len(faces)

        data = bytearray()
        for triangle in faces:
            data = set_triangle(data, triangle)

        data = pad_chunk(data)
        return data, triangle_count


    def write_uv(vertices):
        data = bytearray()
        for vert_info in vertices:
            data = set_uv(data, vert_info['uv'])

        data = pad_chunk(data)
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


    def get_mesh_data(obj):
        #get the vertices of triangles!
        #vertices with the same position, uv, and normal can be represented one time
        mesh = obj.data
        uv_layer = mesh.uv_layers.active.data

        unique_verts = []
        triangles = []

        for tri in mesh.loop_triangles:
            triangle = []
            for loop_index in tri.loops:
                loop = mesh.loops[loop_index]
                vert = mesh.vertices[loop.vertex_index]
                uv_data = uv_layer[loop.index].uv

                vert_info = {
                    'index': vert.index,
                    'position': vert.co,
                    'normal': vert.normal,
                    'uv': uv_data
                }

                if vert_info not in unique_verts:
                    unique_verts.append(vert_info)

                triangle.append(unique_verts.index(vert_info))

            triangles.append(triangle)
        return unique_verts, triangles


    #starting export
    uniq_vertices, triangles_list = get_mesh_data(obj)
    nvertices = len(uniq_vertices)

    texturedata = write_texture(texture_path)
    facesdata, nfaces = write_faces(triangles_list)
    uvdata = write_uv(uniq_vertices)

    animdata, kfcount, duration, length = get_keyframes(obj, uniq_vertices, kf_range[0], kf_range[1])

    offsettable = write_offset_table(kfcount, length)
    data_list = [offsettable, texturedata, facesdata, uvdata, animdata]
    
    mrfdata = bytearray()  
    mrfdata = write_data_chunk(mrfdata, kfcount, nvertices, nfaces, duration)
    
    for data in data_list:
        mrfdata.extend(data)
    
    with open(filepath, 'wb') as f:             
        f.write(mrfdata) 
