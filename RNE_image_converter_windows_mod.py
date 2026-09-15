# 游戏: 《Robotics;Notes Elite》
# 平台: PSVita/PS3
# 背景及CG图片转码（bin转png）
# 作者: wetor (www.wetor.top / wetor.top@gmail.com)
# 时间: 2020.5.8
# RNE_image_converter 0.1

# 目前仅支持RGBA格式，256色图像 转成 bin


# 时间: 2022.6.27
# 改编: manicsteiner (github.com/manicsteiner)
# 此脚本现在会批量转换bin目录下的所有文件
# 时间: 2026.7.1
# 改编: root-none (github.com/lzhhzl)
# 添加了imagequant和unknow_flag=2字库纹理的支持

import os
import struct

from PIL import Image


def getFileNameWithoutExtension(path):
    return path.split('\\').pop().split('/').pop().rsplit('.', 1)[0]


def bin2png(file, saveDir='.'):
    fl = open(file, 'rb')
    filename = getFileNameWithoutExtension(file)
    fileDir = os.path.dirname(file) if saveDir == '.' else saveDir
    width,height = struct.unpack('<HH', fl.read(4))
    pixelFormat,unKnow = struct.unpack('<HH', fl.read(4))
    img = Image.new('RGBA', (width, height))
    if pixelFormat == 8 and unKnow==2:
        pixelColor = {}
        for y in range(height):
            for x in range(width):
                color = fl.read(1)
                img.putpixel((x, y), (255, 255, 255, color[0]))
    elif pixelFormat == 8:
        pixelColor = {}
        for i in range(256):
            color = fl.read(4)
            pixelColor.update({i: (color[2], color[1], color[0], color[3])})

        for y in range(height):
            for x in range(width):
                img.putpixel((x, y), pixelColor[fl.read(1)[0]])
        # 或者
        # pixelColor = b''
        # for _ in range(256):
        #     color = fl.read(4)
        #     pixelColor += bytes([color[2], color[1], color[0], color[3]])
        # img = Image.frombytes(
        #     "P",
        #     [width, height],
        #     fl.read(width * height),
        #     decoder_name="raw",
        # )
        # img.putpalette(pixelColor, rawmode="RGBA")
    elif pixelFormat == 32:
        for y in range(height):
            for x in range(width):
                color = fl.read(4)
                img.putpixel((x, y), (color[1], color[2], color[3], color[0]))

    fl.close()
    img.save(fileDir + '\\' + filename + '.png', 'png')
    print("bin2png: '" + file + "' convert png success! Save as '" + fileDir + '/' + filename + '.png' + "'")


def png2bin(file, pixelFormat, unknow_flag=0, saveDir='.'):
    img = Image.open(os.path.abspath(file))
    # print(len(img.getcolors(256*256*256)))
    if pixelFormat == 8 and img.mode not in ('P','RGBA'):
        if img.mode=='RGB':
            img = img.convert('RGBA')
        else:
            print('输入不是256色8位调色板量化或RGBA格式的图像！')
            return
    if pixelFormat == 32 and img.mode != 'RGBA':
        print('输入不是RGBA格式的图像！')
        return
    width = img.size[0]
    height = img.size[1]
    filename = getFileNameWithoutExtension(file)
    fileDir = os.path.dirname(os.path.abspath(file)) if saveDir == '.' else saveDir
    saveAs = fileDir + '\\' + filename + '.bin'
    fl = open(saveAs, 'wb')
    fl.write(struct.pack('<HHHH', width, height, pixelFormat, unknow_flag))
    # pixelColor = {}
    if pixelFormat == 8:
        if img.mode == 'P' and unknow_flag!=2:
            palette = img.getpalette()
            transparency = img.info['transparency']
            for i in range(256):
                color = (palette[i*3], palette[i*3+1], palette[i*3+2])
                fl.write(bytes([color[2], color[1], color[0], transparency[i]]))
            for y in range(height):
                for x in range(width):
                    fl.write(struct.pack('<B', img.getpixel((x, y))))
        elif img.mode == 'RGBA' and unknow_flag==2:
            for y in range(height):
                for x in range(width):
                    color = img.getpixel((x, y))
                    fl.write(bytes([color[3]]))
        else:
            import imagequant
            input_image_data = imagequant._pil_image_to_raw_bytes(img)
            output_img_data, palette = imagequant.quantize_raw_rgba_bytes(
                input_image_data,
                img.width,
                img.height,
                dithering_level=1.0,
                max_colors=256,
                min_quality=0,
                max_quality=100,
            )
            for i in range(256):
                fl.write(bytes([palette[i*4+2], palette[i*4+1], palette[i*4], palette[i*4+3]]))
            fl.write(output_img_data)
    else:
        for y in range(height):
            for x in range(width):
                color = img.getpixel((x, y))
                fl.write(bytes([color[3], color[0], color[1], color[2]]))

    img.close()
    fl.close()
    print(f"png2bin: '{file}' convert {pixelFormat=} {unknow_flag=} bin success! Save as '{saveAs}'")


if __name__ == '__main__':
    # for root,dirs,files in os.walk('.\\bin'):
    #     for file in files:
    #         bin2png(os.path.join(root,file), '.\\png')
    # bin2png('.\\data\\bin\\00128', '.\\data\\png')

    for root,dirs,files in os.walk('.\\test'):
        for file in files:
            png2bin(os.path.join(root,file), 8)
    # png2bin('./0000P.png', 8)
    # bin2png('./data/png/1.bin', './data/png')
