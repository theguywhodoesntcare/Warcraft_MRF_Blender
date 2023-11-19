using mdx2mrd;
using MdxLib.Model;
using MdxLib.ModelFormats;
using System;
using System.IO;

namespace mdx2mrf
{
    internal class Program
    {
        static void Main(string[] args)
        {
            //args = new string[] { @"C:\Users\Administrator\Desktop\KingThrone.mdx" };

            if (args.Length == 0)
                return;

            string filePath = args[0];
            if (!File.Exists(filePath))
                return;

            CModel Model = new CModel();

            using (FileStream fileStream = new FileStream(filePath, FileMode.Open, FileAccess.Read))
            {
                new CMdx().Load(filePath, (Stream)fileStream, Model);

                byte[] mrfData = Parser.Parse(Model);


                string savePath = Path.Combine(Path.GetDirectoryName(filePath), "arthascape" + Path.GetFileNameWithoutExtension(filePath) + ".mrf");

                if (mrfData != null) File.WriteAllBytes(savePath, mrfData);

                Console.ReadLine();
            }
        }
    }
}
