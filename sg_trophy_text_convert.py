from lxml import etree
import os
os.chdir(os.path.dirname(__file__))

def parse_tbl_file(tbl_path):
    """
    逐行读取.tbl文件，解析为字典。
    格式：xxxx=一个字符 (xxxx为四位大写hex)
    如果字符（key）重复，则跳过不更新。
    """
    char_to_hex_map = {}

    try:
        with open(tbl_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.rstrip('\r\n')
                if not line or '=' not in line:
                    continue

                parts = line.split('=', 1)  # 最多分割一次，防止字符本身包含=
                if len(parts) != 2:
                    continue
                hex_str, char = parts

                # 如果字符已经在字典里，则跳过不更新
                if char in char_to_hex_map:
                    continue

                char_to_hex_map[char] = int(hex_str,16)
    except FileNotFoundError:
        raise FileNotFoundError(f"错误：找不到tbl文件 {tbl_path}")
    except Exception as e:
        raise Exception(f"解析tbl文件时发生错误：{e}")
        
    return char_to_hex_map

def parse_sfm_and_convert_chars(sfm_path, char_to_hex_map, output_path='.'):
    """
    解析SFM(XML)文件，提取并转换name和detail标签的文本内容。
    将文本内容的字符记录为“已出现”和“未出现”两类。
    """
    found_chars = []   # 在tbl字典中出现的字符
    not_found_chars = []  # 未在tbl字典中出现的字符
    
    try:
        tree = etree.parse(sfm_path)
        root = tree.getroot()
        
        # 遍历XML中所有的 name 和 detail 标签
        for tag_name in ['name', 'detail']:
            for elem in root.iter(tag_name):
                if elem.text:
                    text_content = elem.text
                    new_text = ""
                    for char in text_content:
                        if char in char_to_hex_map:
                            if char not in found_chars:
                                found_chars.append(char)
                            new_text += chr(char_to_hex_map[char]-0x8000+0xe000)
                        else:
                            if char not in not_found_chars:
                                not_found_chars.append(char)
                    elem.text = new_text
                else:
                    raise Exception(f"Find empty tag <{tag_name}> text")
        
        # 保存转换过的SFM文件
        new_sfm_path = os.path.join(output_path, os.path.basename(sfm_path).upper().replace('.SFM','_mod.SFM'))
        tree.write(new_sfm_path, encoding='utf-8', pretty_print=True)
        print(f"转换后的SFM文件保存在{new_sfm_path}")
    except FileNotFoundError:
        raise FileNotFoundError(f"错误：找不到sfm文件 {sfm_path}")
    except Exception as e:
        raise Exception(f"解析SFM(XML)文件时发生错误：{e}")
    
    pad_size = os.path.getsize(sfm_path) - os.path.getsize(new_sfm_path)
    if pad_size > 0:
        pad_new_sfm_path = os.path.join(output_path, os.path.basename(sfm_path).upper().replace('.SFM','_mod_SFM_pad.bin'))
        with open(pad_new_sfm_path,"wb") as pad_f:
            new_f = open(new_sfm_path, "rb")
            pad_f.write(new_f.read())
            new_f.close()
            pad_f.write(b'\x00'*pad_size)
        print(f"转换后的SFM文件原文件小{pad_size} bytes，对齐数据保存在{pad_new_sfm_path}")
    elif pad_size<0:
        print(f"请注意：转换后的SFM文件比原文件大{abs(pad_size)} bytes")
        
    return found_chars, not_found_chars

def save_found_chars_to_txt(found_chars, char_to_hex_map, output_path):
    """
    将已出现的字符按对应的hex值正序排列记录入txt文件。
    格式：xxxx=出现的字符
    """
    # 准备排序用的数据：(hex值, 字符)
    sorted_data = [(char_to_hex_map[char], char) for char in found_chars ]

    # 按hex值正序排列
    sorted_data.sort(key=lambda x: x[0])

    try:
        log_path = os.path.join(output_path,"trophy_used_chars.txt")
        with open(log_path, 'w', encoding='utf-8') as f:
            for hex_val, char in sorted_data:
                f.write(f"{hex_val:4x}={char}\n")
        print(f"已出现于tbl中的字符结果已保存至：{log_path}")
    except Exception as e:
        print(f"写入记录文件时发生错误：{e}")


def main():
    # 在此处修改为实际的中文字库文件和TROP文件和保存文件位置
    tbl_file_path = r'\Charset.tbl'       # .tbl 文件路径
    sfm_file_path = r'TROP_mod.SFM'       # .SFM 文件路径
    output_path = r'.'   # 结果输出 .txt 文件路径
    
    print("开始处理...")

    # 1. 解析tbl文件
    print(f"正在解析tbl文件：{tbl_file_path}")
    char_to_hex_map = parse_tbl_file(tbl_file_path)
    if not char_to_hex_map:
        print("tbl字典为空，程序终止。")
        return
    print(f"tbl解析完成，共加载 {len(char_to_hex_map)} 个唯一字符映射。")
    # 2. 解析SFM并转换字符
    print(f"正在解析SFM(XML)文件：{sfm_file_path}")
    found_chars, not_found_chars = parse_sfm_and_convert_chars(sfm_file_path, char_to_hex_map, output_path)
    print(f"SFM name&detail 文本解析并转换完成。在tbl中使用到的字符数：{len(found_chars)}")
    # 3. 排序并保存已出现的字符到txt
    save_found_chars_to_txt(found_chars, char_to_hex_map, output_path)
    # 4. 打印未出现的字符
    if not not_found_chars:
        print("没有未出现于tbl中的字符")
    else:
        print(f"不存在于tbl中{len(not_found_chars)}个字符：{''.join(not_found_chars)}")
    
    print("\n处理全部完成。")


if __name__ == '__main__':
    main()
