import os


os.environ["CUDA_VISIBLE_DEVICES"] = "0"
os.environ["TF_FORCE_GPU_ALLOW_GROWTH"] = "true"


import numpy as np
import sys
import cv2
import re
import time



HP_NET_DIR = os.path.abspath('../')

sys.path.append(HP_NET_DIR)


from HighPull.YoloV5Detector import Detector

detector = Detector()
detector.load()

from HighPull import TextDetector
from HighPull import textPostprocessing

textDetector = TextDetector.get_static_module("ru")()
textDetector.load("latest")

class VideoCamera(object):

    def get_frame(self):
        ret, img = self.camera.read()
        t = time.strftime('%Y-%m-%d_%H:%M:%S')
        img = cv2.putText(img, t, (10,50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 0), 2, cv2.LINE_AA)

        targetBoxes = detector.detect_bbox(img)

        zones = []
        regionNames = []
        for targetBox in targetBoxes:
            x = int(min(targetBox[0], targetBox[2]))
            w = int(abs(targetBox[2] - targetBox[0]))
            y = int(min(targetBox[1], targetBox[3]))
            h = int(abs(targetBox[3] - targetBox[1]))

            image_part = img[y:y + h, x:x + w]
            zones.append(image_part)
            regionNames.append('ru')

        textArr = textDetector.predict(zones)
        textArr = textPostprocessing(textArr, regionNames)


        x=0
        for obj in targetBoxes:
            if not re.match(r'[ABEKMHOPCTYX]\d{3}(?<!000)[ABEKMHOPCTYX]{2}\d{2,3}', textArr[x]):
                continue
            cv2.rectangle(img, (obj[0], obj[1]), (obj[2], obj[3]), (0, 0, 255))
            cv2.putText(img, textArr[x], (obj[0], obj[1]), cv2.FONT_HERSHEY_DUPLEX, 0.7, (255, 255, 225), 1)
            x=+1
        ret, frame = cv2.imencode('.jpg', img)
        return frame.tobytes(), textArr, t, img