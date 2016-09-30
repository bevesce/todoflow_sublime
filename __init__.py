print('init')
import sys
import os
ply_path = os.path.join(os.path.split(__file__)[0], 'ply')
sys.path.append(ply_path)
print(ply_path)
