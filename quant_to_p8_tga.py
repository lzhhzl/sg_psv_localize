import argparse
import os
import sys
from PIL import Image
import imagequant
import struct

def quantize_and_save(input_path, output_path):
    """
    将RGBA PNG量化为256色并保存为palette TGA格式
    """
    try:
        # 打开图像
        img = Image.open(input_path)
        assert img.mode=="RGBA"
        
        # 使用 imagequant 进行量化 (最多256色), imagequant 会自动处理透明通道 (Alpha)
        # output_img = imagequant.quantize_pil_image(
        #     img,
        #     max_colors=256
        # )
        input_image_data = imagequant._pil_image_to_raw_bytes(img)
        output_img_data, output_palette = imagequant.quantize_raw_rgba_bytes(
            input_image_data,
            img.width,
            img.height,
            dithering_level=1.0,
            max_colors=256,
            min_quality=0,
            max_quality=100,
        )

        output_img = Image.frombytes(
            "P",
            [img.width, img.height],
            output_img_data,
            decoder_name="raw",
        )
        output_img.putpalette(output_palette, rawmode="RGBA")
        
        # 保存为 index palette TGA 格式
        # output_img.save(output_path)
        # TGA 32位调色板颜色顺序是 B, G, R, A
        tga_palette = bytearray()
        for i in range(256):
            r = output_palette[i * 4]
            g = output_palette[i * 4 + 1]
            b = output_palette[i * 4 + 2]
            a = output_palette[i * 4 + 3]
            # 按照 TGA 规范写入 BGRA 顺序
            tga_palette.extend(struct.pack('BBBB', b, g, r, a))
        with open(output_path,'wb') as tga:
            width, height = output_img.size
            colormap_type = 1  # 使用调色板
            image_type = 1     # 索引颜色图像（带调色板）
            colormap_first_entry_index = 0
            colormap_length = 256  # 8bpp
            colormap_depth = 32  # 每个调色板条目 32 位（RGBA）
            bits_per_pixel = 8

            # Image Descriptor Byte:
            # Bit 5: 1 → top-left origin
            # Bits 3-0: 8 → 8-bit alpha
            image_descriptor = 0b00100000 | 0b00001000  # 32 + 8 = 40

            # TGA 文件头结构
            tga_header = struct.pack(
                '<BBBHHBHHHHBB',
                0,  # id_length
                colormap_type,
                image_type,
                # Color Map Specification
                colormap_first_entry_index,
                colormap_length,
                colormap_depth,
                # Image Specification
                0,  # x_origin
                0,  # y_origin
                width,
                height,
                bits_per_pixel,
                image_descriptor
            )
            tga.write(tga_header)
            tga.write(tga_palette)
            tga.write(output_img_data)
        print(f"✅ 成功! 256色 TGA 图像已保存至: {os.path.abspath(output_path)}")
        
    except FileNotFoundError:
        print(f"错误: 找不到文件 '{input_path}'")
        sys.exit(1)
    except Exception as e:
        raise e

def main():
    parser = argparse.ArgumentParser(description="将 RGBA PNG 量化为 256 色并保存为 palette TGA 格式")
    parser.add_argument("-i", "--input", required=True, help="目标 PNG 文件的路径")
    parser.add_argument("-o", "--output", default=None, help="输出 palette TGA 文件的路径 (可选，默认保存在脚本同目录下)")
    
    args = parser.parse_args()
    input_path = args.input
    
    # 如果未指定 -o，则默认输出到脚本所在路径，文件名与原文件相同但后缀为 *.tga
    if args.output:
        output_path = args.output
    else:
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_path = os.path.join(script_dir, f"{base_name}.tga")
        
    quantize_and_save(input_path, output_path)

if __name__ == "__main__":
    main()