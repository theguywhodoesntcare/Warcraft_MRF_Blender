using MdxLib.Model;
using MdxLib.Primitives;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace mdx2mrf
{
    internal static class Parser
    {
        internal static List<byte> CreateHeader(int vertices, int angles)
        {
            List<byte> header = new List<byte>();

            byte[] magic = Encoding.UTF8.GetBytes("Morf");
            const int frames = 2; //number of keyframes
            const float frameTime = 2.0f; 

            header.AddRange(magic);
            SetDword(header, frames);
            SetDword(header, vertices);
            SetDword(header, angles);
            SetFloat(header, frameTime);

            header = PadChunkSize(header, 64);

            return header;
        }

        internal static List<byte> CreateTable(
            byte[] texturePath,
            List<byte> faceBytes,
            List<byte> mappingBytes,
            List<byte> vertexBytes,
            int kf_number
        )
        {
            List<byte> table = new List<byte>();

            int table_length = (kf_number + 4) * 4; //длина таблицы
            if (table_length % 16 != 0)
            {
                table_length = ((table_length / 16) + 1) * 16;
            }

            int offset = 0;
            SetDword(table, offset);

            offset += 64;
            offset += table_length;
            SetDword(table, offset);

            offset += texturePath.Count();
            SetDword(table, offset);

            offset += faceBytes.Count();
            SetDword(table, offset);

            offset += mappingBytes.Count();
            SetDword(table, offset);

            for (int i = 0; i < kf_number - 1; i++)
            {
                offset += vertexBytes.Count();
                SetDword(table, offset);
            }

            table = PadChunk(table);

            return table;
        }

        internal static byte[] Parse(CModel Model)
        {
            //GEOSETS BLOCK
            if (Model.HasGeosets) Console.WriteLine("Model Has Geosets"); else return null;

            CGeoset geoset = Model.Geosets[0]; //only first geo

            List<byte> mrfData = new List<byte>();
            //TEXTURE BLOCK

            CMaterial material = geoset.Material.Object;
            CMaterialLayer layer = material.Layers[0];

            string texturePath = layer.Texture.Object.FileName;

            Console.WriteLine(texturePath);

            byte[] textureBytes = Encoding.UTF8.GetBytes(texturePath);
            textureBytes = PadChunk(textureBytes);

            //FACES BLOCK
            int countFaces = geoset.Faces.Count;

            List<byte> faceBytes = new List<byte>();

            for (int i = 0; i < countFaces; i++)
            {
                CGeosetFace face = geoset.Faces[i];
                SetTriangle(faceBytes, face);
            }

            faceBytes = PadChunk(faceBytes);

            //VERTICES BLOCK
            int count = geoset.Vertices.Count;

            List<byte> mappingBytes = new List<byte>();
            List<byte> vertexBytes = new List<byte>();

            for (int i = 0; i < count; i++)
            {
                CGeosetVertex vertex = geoset.Vertices[i];

                SetVector2(mappingBytes, vertex.TexturePosition);

                SetVector3(vertexBytes, vertex.Position);

                SetVector3(vertexBytes, vertex.Normal);
            }
            mappingBytes = PadChunk(mappingBytes);
            vertexBytes = PadChunk(vertexBytes);


            mrfData.AddRange(CreateHeader(count, countFaces * 3));
            mrfData.AddRange(CreateTable(textureBytes, faceBytes, mappingBytes, vertexBytes, 2));
            mrfData.AddRange(textureBytes);
            mrfData.AddRange(faceBytes);
            mrfData.AddRange(mappingBytes);
            mrfData.AddRange(vertexBytes);
            mrfData.AddRange(vertexBytes); //2 keyframes

            byte[] mrfBin = mrfData.ToArray();

            return mrfBin;
        }

        static void SetTriangle(List<byte> list, CGeosetFace face)
        {
            SetWord(list, face.Vertex1.Object.ObjectId);
            SetWord(list, face.Vertex2.Object.ObjectId);
            SetWord(list, face.Vertex3.Object.ObjectId);
        }

        static void SetVector3(List<byte> list, CVector3 vector)
        {
            SetFloat(list, vector.X);
            SetFloat(list, vector.Y);
            SetFloat(list, vector.Z);
        }

        static void SetVector2(List<byte> list, CVector2 vector)
        {
            SetFloat(list, vector.X);
            SetFloat(list, vector.Y);
        }

        static void SetFloat(List<byte> list, float val)
        {
            list.AddRange(BitConverter.GetBytes((float)val));
        }

        static void SetWord(List<byte> list, int val)
        {
            list.AddRange(BitConverter.GetBytes((Int16)val));
        }

        static void SetDword(List<byte> list, int val)
        {
            list.AddRange(BitConverter.GetBytes((Int32)val));
        }

        static byte[] PadChunk(byte[] data)
        {
            int padding = 16 - (data.Length % 16);

            if (padding == 16)
                return data;

            Array.Resize(ref data, data.Length + padding);
            return data;
        }

        static List<byte> PadChunk(List<byte> data)
        {
            int padding = 16 - (data.Count % 16);

            if (padding == 16)
                return data;

            data.AddRange(new byte[padding]);
            return data;
        }

        static List<byte> PadChunkSize(List<byte> data, int chunkSize)
        {
            int padding = chunkSize - (data.Count % chunkSize);

            if (padding == chunkSize)
                return data;

            data.AddRange(new byte[padding]);
            return data;
        }
    }
}
