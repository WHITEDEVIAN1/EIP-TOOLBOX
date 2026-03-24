import sys, os
from pathlib import Path
sys.path.insert(0, os.path.abspath('.'))
from modules.image.processor import ImageProcessor
p = ImageProcessor()
try:
    print('Starting compress Q75...')
    info75 = p.compress(Path('../test_shape.jpg'), Path('out75.webp'), quality=75)
    print(info75)
    
    print('Starting compress Q10...')
    info10 = p.compress(Path('../test_shape.jpg'), Path('out10.webp'), quality=10)
    print(info10)
except Exception as e:
    import traceback
    traceback.print_exc()
