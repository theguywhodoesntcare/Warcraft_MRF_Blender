import os
import struct
import bpy

from .utils import *

from mathutils import Vector
from . import MessageBox

def load_morf(filepath, divisor, shadesmooth):
    def get_magic(data):
        #4 bytes
        magic_string = struct.unpack('4s', data[:4])[0].decode('utf-8')
        if  magic_string == 'Morf':
            return True

    def read_offsetsTable(data, offset, kfsnumber):
        #number of frames taken as argument
        #plus more offsets of 4 chunks
        #offset of the table itself is not specified in the table
        
        chunks = kfsnumber + 4
        offsetsTable = []
        counter = 0
        
        for i in range(chunks):
            dword, offset = get_dword(data, offset)
            counter += 1
            offsetsTable.append(dword)
        
        #print('Значений в таблице сдвигов:', counter)    
        return offsetsTable  

    def set_material(obj, texture):
        mat = bpy.data.materials.new(name='MRFMaterial')
        mat.mrf_texture_props.texture_path = texture
        obj.data.materials.append(mat)

    def read_texture(data, offset, offsetend):
        texture = get_strn(data, offset, offsetend) 
        return texture #but we wont
    
        #it looks like Warcraft cuts the string to the first dot
        #we can do the same
        dot_index = texture.find('.')
        if dot_index != -1:
            texture = texture[:dot_index]

                
    def read_faces(data, offset, fnumber):
        #triangles, 3 words each.
        faces = []
        for i in range(fnumber):
            face, offset = get_triangle(data, offset)
            faces.append(face)
        
        #print('Количество треугольников: ', len(faces))
        return faces

    def read_uv(data, offset, vnumber):
        #two floats per vertex
        uv = []
        
        for i in range(vnumber):
            vertex, offset = get_uv(data, offset)
            uv.append(vertex)    
        
        #print('Количество вершин в uv секции: ', len(uv))
        return uv
        
    def read_vectors(data, offset, vnumber):
        #two vectors per vertex
        #first vector is position, second is normal

        vertices = []
        for i in range(vnumber*2):
            vertex, offset = get_vector(data, offset, divisor)
            if i % 2 == 0:  #skip normals
                vertices.append(vertex)
            
        #print('Количество векторов в блоке: ', len(vertices)) 
        return vertices

    def create_mesh(verts, faces, uv, pivot, filename):
        mesh = bpy.data.meshes.new(name=filename)
        obj = bpy.data.objects.new(name=filename, object_data=mesh)
        bpy.context.collection.objects.link(obj)

        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)

        mesh.from_pydata(verts[0], [], faces)
        mesh.update()

        uv_layer = mesh.uv_layers.new(name='New UV Map')

        for poly in mesh.polygons:
            for loop_index in poly.loop_indices:
                loop = mesh.loops[loop_index]
                uv_layer.data[loop.index].uv = uv[loop.vertex_index]
        
        """
        set origin (pivot point)     
        
        cursor_location = Vector(bpy.context.scene.cursor.location)
        
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.scene.cursor.location = pivot
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
        
        bpy.context.scene.cursor.location = cursor_location
        """
        #This makes some sense, but if later we want to export the mesh again to the MRF format, 
        #then it will shift by the difference between the world center of coordinates and the Origin. 
        #So it's not worth it.

        if shadesmooth:
            bpy.ops.object.shade_smooth()
        
        create_shapeanim(obj, verts)
        return obj
        

    def create_shapeanim(obj, verts):        
        #Morf animation can be thought as Shape Keys animation
        for frame in range(0, len(verts)): 
            vertices = verts[frame] 

            shape_key = obj.shape_key_add(name=f"Frame{frame+1}")
            
            for i, coord in enumerate(vertices):
                shape_key.data[i].co = coord

            shape_key.value = 0.0
            if frame != 0: #there is no need to create keyframe in position 0, since there will be a double
                shape_key.keyframe_insert(data_path="value", frame=frame)
                shape_key.value = 1.0
                shape_key.keyframe_insert(data_path="value", frame=frame+1)
            if frame < len(verts) - 1:
                shape_key.value = 0.0
                shape_key.keyframe_insert(data_path="value", frame=frame+2)
                
        bpy.context.scene.frame_set(0) #переключимся в нулевой кадр
        #чтобы видеть стартовую позицию во вьюпорте
                    
            
    def read_file(data, offset, filename):
        kfnumber, offset = get_dword(data, offset)
        print('Number of keyframes: ', kfnumber)

        vertexnumber, offset = get_dword(data, offset) 
        print('Vertices Number: ', vertexnumber)
        
        facesnumber, offset = get_dword(data, offset)
        facesnumber = facesnumber//3
        print('Faces Number: ', facesnumber)
            
        time, offset = get_float(data, offset) 
        fps = round(1/time)
        print('Frame Rate: ', fps, 'fps') #1/fps
        #in Arthas' cape it is equal to 1/30 seconds
        
        pivot, offset = get_vector(data, offset, divisor) 
        print('Pivot Point: ', pivot) #(?)
        
        bounds, offset = get_float(data, offset) 
        bounds = bounds/divisor
        print('Bounds Radius: ', bounds) #(?)
        
        #на 0x0040 (64) сдвиге начинается таблица сдвигов.   
        offsets = read_offsetsTable(data, 64, kfnumber)
        texture = read_texture(data, offsets[1], offsets[2])
        print('Texture path: ', texture)

        faces = read_faces(data, offsets[2], facesnumber)
        uv = read_uv(data, offsets[3], vertexnumber)
        
        kf_counter = 0
        keyframes = []
        for i in range(4, kfnumber + 4):
            vertices = read_vectors(data, offsets[i], vertexnumber)
            keyframes.append(vertices)
            kf_counter += 1
            #print(kf_counter)
        
        bpy.context.scene.render.fps = fps #спорно, но пусть будет    
        obj = create_mesh(keyframes, faces, uv, pivot, filename)  
        set_material(obj, texture)
        MessageBox.show(texture, "MRF Texture path:", 'TEXTURE')  


    #os.system('cls')
    with open(filepath, 'rb') as file:
        data = file.read()
        filename = os.path.splitext(os.path.basename(filepath))[0]
        if get_magic(data):
            print('\nLoading Morf file...')
            read_file(data, 4, filename)
            print("The Morf file has been successfully loaded!\n")