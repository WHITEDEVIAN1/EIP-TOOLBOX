import sys
sys.path.insert(0, './backend')
from app.modules.image.processor import ImageProcessor
from PIL import Image
p = ImageProcessor()
img = Image.open('test_shape.jpg')
try:
    out = p.remove_background(img)
    print('Success')
except Exception as e:
    import traceback
    traceback.print_exc()
