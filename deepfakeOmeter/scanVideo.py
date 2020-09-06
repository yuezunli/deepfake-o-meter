from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time, os
import numpy as np


def AnalysisVideo(method, video, pathToSave):
    """
    Select the specific method for video analysis
    :param method: the method selected by user
    :param video: the vidoe uploaded by user
    """

    # the corresponding docker name for each method
    modelToEnv = {
    'DSP-FWA':'dsp0829',  # download things
    'Upconv':'upconv',
    'Capsule':'upconv',
    'ClassNSeg':'upconv',
    'FWA':'fwa08312',
    'MesoNet':'meso08311',
    'VA':'va',
    'XceptionNet':'xcep08291',
    'Selim':'selim',  # time too lonf why??
    'WM':'wm',
    'CNNDetection':'upconv'
    }

    videoPath = 'deepforensics/deepfakeOmeter' + video[1:]
    commenLine = "docker run -p 2500:5000 --runtime=nvidia -e NVIDIA_VISIBLE_DEVICE=3 -v /media/disk/Backup/02congzhang/deepfake/deepforensics/0905/deepforensics/:/deepforensics/ "+modelToEnv[method]+" python deepforensics/deepfakeOmeter/videoProcess.py -v "+videoPath+"  -m "+method
    os.system(commenLine)


class MyDirEventHandler(FileSystemEventHandler):
    def on_moved(self, event):
        print("move", event)
    def on_deleted(self, event):
        print("delete", event)
    def on_modified(self, event):
        print("modified:", event)
    def on_created(self, event):
        filePath = event.src_path
        if os.path.isfile(filePath):
            # if the video has finished save, the detection will be started
            if filePath.split('.')[-1] == 'txt':
                npzDir = filePath[:-len(filePath.split('/')[-1])]
                methods = np.load(os.path.join(npzDir, 'methods.npy'))
                videoPath =filePath.rsplit('.', 1)[0] +'.mp4'
                filePathS = filePath.rsplit('/',4)
                pathToSave = os.path.join( os.path.dirname(__file__), 'result', filePathS[2], filePathS[3])

                if not os.path.isdir(pathToSave):
                    os.makedirs(pathToSave)

                for method in methods:
                    print(method, videoPath)
                    AnalysisVideo(method, videoPath, pathToSave)

                with open(os.path.join(pathToSave, 'finish.txt'), 'w') as f:
                    f.writelines('Finish Save!')



if __name__ == '__main__':
    observer = Observer()
    fileHandler = MyDirEventHandler()
    observer.schedule(fileHandler, "./tmp", True)
    observer.start()
    try:
        while True:
            time.sleep(2)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
