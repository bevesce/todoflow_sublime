print('init')
import sys
import os
print(os.path.split(__file__)[0])
sys.path.append(os.path.split(__file__)[0])
print('sublime todoflow')
