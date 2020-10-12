from watchdog.observers import Observer
from watchdog.observers.polling import PollingObserver
from watchdog.events import FileSystemEventHandler
import time, os
import numpy as np
import shutil
from email_utils import SendEmail

#pwd = os.path.dirname(os.path.abspath(__file__))

root_folder = '/media/disk1/'
result_folder = os.path.join(root_folder, 'deepfake-o-meter-sync-result/')
received_folder = os.path.join(root_folder, 'deepfake-o-meter-sync-received/')
    

def AnalysisVideo(method, video, result_this_dir):
    """
    Select the specific method for video analysis
    :param method: the method selected by user
    :param video: the vidoe uploaded by user
    """

    # the corresponding docker name for each method
    modelToEnv = {
    'DSP-FWA':'dsp0829',  # download things
    'Upconv':'cnndetection',
    'Capsule':'cnndetection',
    'ClassNSeg':'cnndetection',
    'FWA':'fwa',
    'MesoNet':'meso',
    'VA':'va',
    'XceptionNet':'xcep',
    'Selim':'selim',  # time too lonf why??
    'WM':'wm',
    'CNNDetection':'cnndetection'
    }

    # Copy received video to tmp in web    
    docker_dir = 'deepfake-o-meter/web/tmp/received/'
    docker_videoPath = docker_dir + os.path.basename(video)
    docker_result_dir = 'deepfake-o-meter/web/tmp/result/'
    if not os.path.exists(os.path.join(root_folder, docker_dir)):
        os.makedirs(os.path.join(root_folder, docker_dir))
    if not os.path.exists(os.path.join(root_folder, docker_result_dir)):
        os.makedirs(os.path.join(root_folder, docker_result_dir)) 
        
    shutil.copy(video, os.path.join(root_folder, docker_videoPath))
    commenLine = "docker run -p 2500:5000 --runtime=nvidia -e NVIDIA_VISIBLE_DEVICES=0 -v /media/disk1/deepfake-o-meter/:/deepfake-o-meter/ "+modelToEnv[method]+" python deepfake-o-meter/web/videoProcess.py -v "+docker_videoPath+"  -m "+method+ " -o " + docker_result_dir
    os.system(commenLine)
    for file in os.listdir(os.path.join(root_folder, docker_result_dir)):
        shutil.copy(os.path.join(root_folder, docker_result_dir, file), result_this_dir)
    try:
        if os.path.isdir(os.path.join(root_folder, 'deepfake-o-meter/web/tmp/')):
            shutil.rmtree(os.path.join(root_folder, 'deepfake-o-meter/web/tmp/'))
    except Exception as e:
        print('Failed to delete %s. Reason: %s' % (os.path.join(root_folder, 'deepfake-o-meter/web/tmp/'), e))
    


class MyDirEventHandler(FileSystemEventHandler):
    def on_moved(self, event):
        print("move", event)
    def on_deleted(self, event):
        print("delete", event)
    def on_modified(self, event):
        print("modified:", event)
    def on_created(self, event):
        filePath = event.src_path
        print(filePath)
        if os.path.isfile(filePath):
            # if the video has finished save, the detection will be started
            if filePath.split('.')[-1] == 'csv':
                received_this_dir = os.path.dirname(filePath)
                # npzDir = filePath[:-len(filePath.split('/')[-1])]
                methods = np.load(os.path.join(received_this_dir, 'methods.npy'))
                pin = np.load(os.path.join(received_this_dir, 'pin.npy'))
                date = os.path.basename(received_this_dir)
                email = os.path.basename(os.path.dirname(received_this_dir))
                exts = ['.mp4', '.avi', '.mov', '.wmv']
                for ext in exts:
                    videoPath =filePath.rsplit('.', 1)[0] + ext
                    if os.path.exists(videoPath):
                        break
                        
                result_this_dir = received_this_dir.replace('deepfake-o-meter-sync-received', 'deepfake-o-meter-sync-result')  

                if not os.path.isdir(result_this_dir):
                    os.makedirs(result_this_dir)

                for method in methods:
                    print(method, videoPath)
                    AnalysisVideo(method, videoPath, result_this_dir)

                with open(os.path.join(result_this_dir, 'finish.txt'), 'w') as f:
                    f.writelines('Finish Save!')                
                
                # zip result
                cmd = 'cd {} && zip result.zip ./* && cd -'.format(result_this_dir)
                os.system(cmd)
                #print(npzDir)
                #shutil.make_archive(output_filename, 'zip', result_this_dir)
                print('Zip done')
                
                # Send email
                title = 'Downloading the detection result from DeepFake-o-meter'
                url = 'http://zinc.cse.buffalo.edu/ubmdfl/deep-o-meter/download/' + str(email) + '_' + str(pin) + '_' + str(date)
                content = 'Hello, your results can be downloaded from here: {} \n Note this link will be expired in 2 days.'.format(url)
                SendEmail(email, title, content)
                print('Email sent')
                



if __name__ == '__main__':
    #observer = Observer()
    observer = PollingObserver()
    fileHandler = MyDirEventHandler()
    observer.schedule(fileHandler, received_folder, True)
    observer.start()
    try:
        while True:
            time.sleep(2)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
