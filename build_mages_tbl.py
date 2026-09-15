import os
os.chdir(os.path.dirname(__file__))
import unicodedata

PUA = {  # Private Use Area unicode range: char index range
    # "E000-E01A":(100,126),
    # "E01B":268,
    # "E01C":270,
    # "E01D":271,
    # "E01E":272,
    # "E01F":273,
    # "E020-E066":(280,350),
    # "E067":370,
    # "E068-E090":(663,703),
    # "E091":4480,
    # "E092":4481,
    # "E093":4484,
    # "E094":4485,
    # "E095":4486,
    # "E096":4487,
    # "E097":4488,
    # "E098":4489,
    # "E099":4490,
    # "E09A":4491,
    # "E09B":4492,
    # "E09C":4493,
}
PUA_MAP = {}


def init_pua_map():
    map_dict = {}
    for k,v in PUA.items():
        codes = k.split('-')
        if len(codes) == 1:
            code = int(codes[0], 16)
            map_dict[v] = code
        else:
            code_start, code_end = int(codes[0], 16), int(codes[1], 16)
            idx_start, idx_end = v
            for code,i in zip(
                range(code_start, code_end+1),
                range(idx_start, idx_end+1)
            ):
                map_dict[i] = code
    return map_dict


def fix_pua(idx, char):
    assert PUA
    global PUA_MAP
    if not PUA_MAP:
        PUA_MAP = init_pua_map()
    if idx in PUA_MAP and char!=chr(PUA_MAP[idx]):
        return chr(PUA_MAP[idx]), True
    else:
        return char, False


def clean_hex_string(hex_string: str) -> str:
    """清理十六进制字符串"""
    return hex_string.replace("0x", "").replace(" ", "")


def hex_str_to_int32(hex_string: str) -> int:
    """将十六进制字符串转换为 32 位有符号整数"""
    # Python 的 int 会自动处理符号位，如果是 32 位溢出会转为长整型
    value = int(clean_hex_string(hex_string), 16)
    
    # 【关键】C# 的 int 是 32 位有符号整数，如果最高位是 1，Python 需要手动转换为负数
    if value >= 0x80000000:
        value -= 0x100000000
        
    return value


def read_compound_character_table(compound_tbl_path):
    compound_dict = {}
    with open(compound_tbl_path,"r",encoding="utf8") as f:
        for line in f.readlines():
            if not line: continue
            parts = line.rstrip('\n').split('=')
            code_part = parts[0][1:-1]  # 去掉方括号 [...]
            value = parts[1]

            codes = code_part.split('-')
            if len(codes) == 1:
                idx = hex_str_to_int32(codes[0])
                compound_dict[idx] = value
            else:
                code_range_start = hex_str_to_int32(codes[0])
                code_range_end = hex_str_to_int32(codes[1])
                for i in range(code_range_start, code_range_end+1):
                    compound_dict[i] = value
    return compound_dict


utf8_charset_path = r"xxx\Charset.utf8"
compound_tbl_path = r"xxx\CompoundCharacters.tbl"

compound_dict = read_compound_character_table(compound_tbl_path)
with open(utf8_charset_path,"r",encoding="utf8") as f:
    characters = f.read().rstrip('\n')
charset_tbl = []
# pua_char = []
fix_characters = characters if PUA else ""
charset_base = 0x8000
for i,char in enumerate(characters):
    ch = char
    if unicodedata.category(char) == 'Co':
        # pua_char.append(char)
        if PUA:
            fix_char, fix = fix_pua(i, char)
            if fix:
                fix_characters = fix_characters[:i] + fix_char + fix_characters[i+1:]
            ch = compound_dict[ord(fix_char)]
        else:
            ch = compound_dict[ord(char)]
        assert 0xe000<=ord(char)<=0xf8ff  # 检查是不是utf8的code
    charset_tbl.append(f"{hex(charset_base+i)[2:]}={ch}")
if fix_characters:
    with open("Charset_fix.utf8","w",encoding="utf8") as f:
        f.write(fix_characters)
with open(r"Charset.tbl","w",encoding="utf8") as f:
    f.write('\n'.join(charset_tbl))
