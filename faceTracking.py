import sys
import traceback
import tellopy
import dlib
import av
import cv2.cv2 as cv2  # for avoidance of pylint error
import numpy
import time
from math import *
#from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Process, Queue


IMAGE_WIDTH = 960
IMAGE_HEIGHT = 720
DRONE_DIS_LOWER = 90
DRONE_DIS_UPPER = 150

preDrone = False
isDrone = False

def tracking(drone, image, x, y, dis):
    global IMGAE_WIDTH, IMAGE_HEIGHT
    global DRONE_DIS_LOWER, DRONE_DIS_UPPER
    print("x y dis =", x, " ", y, " ", dis)
    cv2.rectangle(image, (x, y), (x+3, y+3), (255, 0, 255), 2)
    #左右方向の制御
    if x < IMAGE_WIDTH * 0.2 :
        print("左端")
        #drone.left(20)
        drone.set_roll(-0.3)
    elif x < IMAGE_WIDTH * 0.4 :
        print("左中")
        #drone.left(10)
        drone.set_roll(-0.1)
    elif x < IMAGE_WIDTH * 0.6:
        print("真中")
        drone.set_roll(0.0)
    elif x < IMAGE_WIDTH * 0.8:
        print("右中")
        #drone.right(10)
        drone.set_roll(0.1)
    else:
        print("右端")
        #drone.right(20)
        drone.set_roll(0.3)

    #上下方向の制御
    if y < IMAGE_HEIGHT / 2 * 0.3 :
        print("上端")
        drone.set_throttle(0.3)
    elif y < IMAGE_HEIGHT / 2 * 0.8 :
        print("上中")
        drone.set_throttle(0.2)
    elif y > IMAGE_HEIGHT - (IMAGE_HEIGHT / 2 * 0.3):
            print("下端")
            drone.set_throttle(-0.3)
    elif y > IMAGE_HEIGHT - (IMAGE_HEIGHT / 2 * 0.8) : 
            print("下中")
            drone.set_throttle(-0.2)
    else : 
            print("真ん中")
            drone.set_throttle(0)
    
    #前後方向の制御
    if dis < DRONE_DIS_LOWER:
        print("遠い")
        #drone.forward(20)
        drone.set_pitch(0.3)
    elif dis < DRONE_DIS_UPPER:
        print("ちょうどいい")
        drone.set_pitch(0.0)
    else:
        print("近い")
        #drone.backward(20)
        drone.set_pitch(-0.3)

def detect(que, faceDlib, image):
    faces = []
    faces = faceDlib(image, 1)
    que.put(faces)
#    future = executor.submit(face_dlib, image, 1)
 



def main():
    global IMGAE_WIDTH, IMAGE_HEIGHT
    global isDrone, preDrone
    timer = 0
    drone = tellopy.Tello()
    face_dlib = dlib.get_frontal_face_detector()
    isDrone = False
    #executor = ThreadPoolExecutor(max_workers=3)

    try:
        drone.connect()
        drone.wait_for_connection(60.0)

        retry = 3
        container = None
        while container is None and 0 < retry:
            retry -= 1
            try:
                container = av.open(drone.get_video_stream())
            except av.AVError as ave:
                print(ave)
                print('retry...')

        drone.takeoff()
        # skip first 300 frames
        frame_skip = 300
        noDrone = time.time()
        futures  = []
        faces = []
        que = Queue()
        
        while True:
            for frame in container.decode(video=0):
                if 0 < frame_skip:
                    frame_skip = frame_skip - 1
                    continue
                start_time = time.time()
                image = cv2.cvtColor(numpy.array(frame.to_image()), cv2.COLOR_RGB2BGR)
                #faces = face_dlib(image, 1)

                #future = executor.submit(detect, que, face_dlib, image)
                future = Process(target=detect, args=(que, face_dlib, image,))
                future.start()
                futures.append(future)

                #futures.append(future)
                #que.put(future)
                if que.empty() == False:
                    faces = que.get() 
                    
                else:
                    faces = []
                """
                for future in futures:
                    if future.done() == True:
                        faces = future.result()
                """
                
                if len(faces) == 0:
                    isDrone = None
                    drone.set_pitch(0.0)
                    drone.set_roll(0.0)
                    drone.set_throttle(0.0)
                else:
                    isDrone = True
                for i, face_rect in enumerate(faces):
                    #ここが処理部分
                    cv2.rectangle(image, tuple([face_rect.left(),face_rect.top()]), tuple([face_rect.right(),face_rect.bottom()]), (0, 0,255), thickness=2)
                    tracking(drone, image, (int)((face_rect.right() + face_rect.left()) / 2), 
                        (int)((face_rect.top() + face_rect.bottom()) / 2),
                        sqrt((face_rect.right() - face_rect.left())*(face_rect.bottom() - face_rect.top())))

                cv2.imshow('image', image)
                cv2.waitKey(1)

               # print(preDrone, " ", isDrone)
                if preDrone == True and isDrone == None:
                    #print("KKKEEEEEEEE")
                    noDrone = time.time()
                elif preDrone == None and isDrone == None:
                    timer =  time.time() - noDrone
                    #print("timer ", noDrone, "  ", time.time())
                    if timer > 10:
                    #    print("asdlfjka;ASDFSDGG")
                        drone.land()
                

                preDrone = isDrone



                if frame.time_base < 1.0/60:
                    time_base = 1.0/60
                else:
                    time_base = frame.time_base
                frame_skip = int((time.time() - start_time)/time_base)
                    

    except Exception as ex:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback)
        print(ex)
    finally:
        drone.quit()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
