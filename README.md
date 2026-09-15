# sg_psv_localize

These are some localization stuff I use in PSV Steins;Gate translation.

- **fonts**, some `Charset.utf8` `CompoundCharacters.tbl` `Charset.tbl` I mod for Psv JP and Steam JP/CN.

- **build_mages_tbl.py**, my script for building Charset.tbl base on Charset.utf8 and CompoundCharacters.tbl.

- **quant_to_p8_tga.py**, my simple image script which is used to quant RGBA image to Palatte images and save in TGA format.

- **p_to_rgba.py**, easy script use pillow to convert Palatte image to RGBA image.

- **sg_elf_dump_utf16_table.py** and **sg_eboot_utf16le_table.txt**, utfl6-le map table dump in eboot, trophy text use this table to match mages engine font.

- **sg_trophy_text_convert.py**, script use a crafty way to caculate and convert trophy TROP.SFM utf8 text to mages engine font codes, must use with Charset.tbl.

- **RNE_image_converter_windows_mod.py**, simple mod base [RNE_image_converter](https://github.com/Manicsteiner/RNE_image_converter), support more Steins;Gate CG convert and rebuilt.
