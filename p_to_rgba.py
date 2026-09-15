import sys
from PIL import Image
img = Image.open(sys.argv[1])
new_img = img.convert("RGBA")
new_img.save(sys.argv[1].replace(" (Image 0)",""))
new_img.close()
img.close()
