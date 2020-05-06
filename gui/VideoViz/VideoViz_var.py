import os


#========== Video Variables ==========

NEW_VIDEO_NF = 1
NEW_VIDEO_FPS = 30
# 'H264' 'XVID'
NEW_VIDEO_FOURCC = 'H264'

#========== Video Playback Variables ==========

LOOP_VIDEO = 1
START_VIDEO_PLAYING = 0
CLOSE_PROGRAM_AT_VIDEO_END = 0

# run mode: 'INTERACTIVE', 'BATCH_RUN'
RUN_MODE = 'INTERACTIVE'

# Video data mode: 'FILE', 'LIVE', 'MEMORY'
INPUT_VIDEO_DATA_MODE = 'FILE'

START_FI = 0
END_FI = -1

# ========== Input / Output Vars ==========

INPUT_PATH = '.'
OUTPUT_PATH = '.'
INPUT_VIDEO = ''
OUTPUT_VIDEO = 'VideoOut.avi'

RUN_SANDBOX_PATH = '../../Run_Sandbox'

# Check computer name
COMPUTERNAME = os.getenv ('COMPUTERNAME')
if COMPUTERNAME == 'XPS':
  INPUT_PATH = '.'
  OUTPUT_PATH = RUN_SANDBOX_PATH
elif COMPUTERNAME == 'EUROCOM': 
  INPUT_PATH = '.'
  OUTPUT_PATH = RUN_SANDBOX_PATH

# ========== Run Cases for Site Specific Configurations ==========

RUNCASE = 'avi_frames'

if RUNCASE == 'avi_frames':
  INPUT_VIDEO = 'avi_frames.avi'
elif RUNCASE == 'ball_rolling':
  INPUT_VIDEO = 'ball_rolling_108x72_1.avi'
elif RUNCASE == 'car':
  INPUT_VIDEO = 'car.avi'
elif RUNCASE == 'Loc1_1a':
  INPUT_VIDEO = 'Loc1_1a.avi'
elif RUNCASE == 'MiceBrainArtery':
  INPUT_VIDEO = 'MiceBrainArtery_seq15c.avi'
elif RUNCASE == 'Track2_9_10s':
  INPUT_VIDEO = 'Track2_9_10s.mp4'

if RUNCASE:
  OUTPUT_VIDEO = RUNCASE + '_' + OUTPUT_VIDEO
  
BATCH_CASES = [ 'avi_frames', 'ball_rolling', 'car', 'Loc1_1a', 'MiceBrainArtery', 'Track2_9_10s' ]
#BATCH_CASES = [ 'avi_frames', 'ball_rolling' ]

RUNPROC = 'negative_img' #'frame_diff'

BATCH_PROCS = [ 'negative_img', 'mirror_img', 'conv_img', 'sobel_gradient', 'morph_dilation', 'morph_erosion', 'morph_opening', 'morph_closing', 'frame_diff' ]