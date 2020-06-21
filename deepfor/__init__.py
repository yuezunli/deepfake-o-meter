
import sys, os
root = os.path.dirname(__file__) + '/../'
sys.path.append(root)
from deepfor.methods.deepforensics_cls import MesoNet, XceptionNet, ClassNSeg, VA, CapsuleNet, FWA, DSPFWA, Upconv, WM


# if method_name.lower() == 'xceptionnet-c23':
#         method = XceptionNet('c23')
# if method_name.lower() == 'xceptionnet-c40':
#     method = XceptionNet('c40')
# if method_name.lower() == 'xceptionnet-raw':
#     method = XceptionNet('raw')

# if method_name.lower() == 'meso4':
#     method = MesoNet('meso4')
# if method_name.lower() == 'mesoinception4':
#     method = MesoNet('mesoinception4')

# if method_name.lower() == 'va':
#     method = VA()

# if method_name.lower() == 'multi-task':
#     method = ClassNSeg()

# if method_name.lower() == 'capsule':
#     method = CapsuleNet()
# if method_name.lower() == 'fwa':
#     method = FWA()
# if method_name.lower() == 'dsp-fwa':
#     method = DSPFWA()
