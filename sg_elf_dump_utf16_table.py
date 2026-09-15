import struct
bin = open("eboot.bin.elf","rb")

dat_810e4000 = {"start":0x000E3CC2, "end":0x000E3D70}
bin.seek(dat_810e4000["start"],0)
data_block_810e4000 = bin.read(dat_810e4000["end"]-dat_810e4000["start"])
dat_810e40b2 = {"start":0x000E3D74, "end":0x000E5222}
bin.seek(dat_810e40b2["start"],0)
data_block_810e40b2 = bin.read(dat_810e40b2["end"]-dat_810e40b2["start"])

txt = open("sg_psv_utf16_table.txt","w",encoding="utf-16-le")
txt.write("&DAT_810e4000\n")
for i in range(len(data_block_810e4000)//2):
  code_data = data_block_810e4000[i*2:i*2+2]
  txt.write(f"{bytes(reversed(code_data)).hex()}={code_data.decode("utf-16-le")}\n")
txt.write("\n&DAT_810e40b2\n")
for i in range(len(data_block_810e40b2)//2):
  code_data = data_block_810e40b2[i*2:i*2+2]
  txt.write(f"{bytes(reversed(code_data)).hex()}={code_data.decode("utf-16-le")}\n")

txt.close()
bin.close()