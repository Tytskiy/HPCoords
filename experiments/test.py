"""
Скрипт для проверки корректности импортов
"""

# пока что путь для python окружения проще указывать так
import sys
from os.path import dirname
sys.path.append("../hpcoords")

import hpcoords as hpc

print(hpc.parallel_coordinates)
