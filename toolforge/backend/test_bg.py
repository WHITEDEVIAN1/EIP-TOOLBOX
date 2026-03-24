import sys, os
from pathlib import Path
sys.path.insert(0, os.path.abspath('.'))
from modules.image.processor import ImageProcessor
p = ImageProcessor()
try:
    print('Starting BG removal...')
    out = p.remove_background(Path('../test_shape.jpg'), Path('test_shape_nobg.png'))
    print('Success')
except Exception as e:
    import traceback
    traceback.print_exc()
