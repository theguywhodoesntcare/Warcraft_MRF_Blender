import struct

# ===IMPORT===
def get_word(data, offset):
    word, = struct.unpack_from('<H', data, offset)
    offset += 2
    return word, offset

def get_dword(data, offset):
    dword, = struct.unpack_from('<I', data, offset)
    offset += 4
    return dword, offset

def get_float(data, offset):
    float, = struct.unpack_from('<f', data, offset)
    offset += 4
    return float, offset

def get_strn(data, offset, offsetend):
    strn = data[offset:offsetend].decode()
    return strn

def get_vector(data, offset, divisor):
    x, y, z = struct.unpack_from('<fff', data, offset)
    offset += 12
    return (x/divisor, y/divisor, z/divisor), offset

def get_triangle(data, offset):
    word1, word2, word3 = struct.unpack_from('<HHH', data, offset)
    offset += 6
    return (word1, word2, word3), offset

def get_uv(data, offset):
    u, v = struct.unpack_from('<ff', data, offset)
    v = 1 - v #Mirror UV along the Y-axis
    offset += 8
    return (u, v), offset



# ===EXPORT===

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