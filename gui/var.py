
#========== General Variables ==========
# verbose print level:
#   0: no print out
#   1: succinct (default)
#   2: verbose
#   3: detailed info
#   4: detailed debug info
VERBOSE = 1

#========== View Variables ==========

#VIZ_ZOOMIN is a int >= 1, default 1
VIZ_ZOOMIN = 1

#VIZ_SCALE is a float <= 1, default 1
VIZ_SCALE = 1

# These are paddings of window size that can fit image content exactly in the window
# Exact values map to the 'GUI window border thickness' which are platform dependent:
#  Win10 - 2
#  Win7 - 4
VIZ_AREA_PADDING_W = 4
VIZ_AREA_PADDING_H = 4

SCREEN_RES_W = 1024
SCREEN_RES_H = 768

#3.0/4 #7.0/8
SCREEN_MARGIN_W = 50
SCREEN_MARGIN_H = 250

#========== DrawCmd Variables ==========

DRAWCMD_LIST = []
DRAWCMD_LIST_2 = []




#========== Font ==========

TEXT_FONT_SZ = 12

#========== Color Lists ==========

RAINBOW_COLORS = [
  [255,   0,   0],   #0, red
  [255, 128,   0],   #1, orange
  [255, 255,   0],   #2, yellow
  [128, 255,   0],   #3, light-green
  [  0, 255,   0],   #4, green
  [  0, 255, 128],   #5, green-cyan
  [  0, 255, 255],   #6, cyan
  [  0, 128, 255],   #7, cyan-blue
  [  0,   0, 255],   #8, blue
  [128,   0, 255],   #9, blue-pink
  [255,   0, 255],   #10,pink
  [255,   0, 128],   #11, red-pink
]

def color_from_id (id):
  NCOLOR = len (RAINBOW_COLORS)
  c = (id) % NCOLOR
  color = RAINBOW_COLORS[c]
  return color

#========== Other Variables ==========