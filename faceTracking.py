import sys
import traceback
import tellopy
import dlib
import av
import cv2.cv2 as cv2  # for avoidance of pylint error
import numpy
import time


def tracking(drone, image, x, y):
    global preX
    global preY
    print(x, " ", y)
    cv2.rectangle(image, (x, y), (x+3, y+3), (255, 0, 255), 2)
    if x < IMAGE_WIDTH / 2 * 0.3 :
        print("左端")
        drone.set_yaw(-0.7)
    elif x < IMAGE_WIDTH / 2 * 0.8 :
        print("左中")
        drone.set_yaw(-0.3)
    elif x > IMAGE_WIDTH - (IMAGE_WIDTH / 2 * 0.3):
        print("右端")
        drone.set_yaw(0.7)
    elif x > IMAGE_WIDTH - (IMAGE_WIDTH / 2 * 0.8) : 
        print("右中")
        drone.set_yaw(0.3)
    else : 
        print("真ん中")
        drone.set_yaw(0)

    if y < IMAGE_HEIGHT / 2 * 0.3 :
        print("下端")
        drone.set_throttle(0.7)
    elif y < IMAGE_HEIGHT / 2 * 0.8 :
        print("下中")
        drone.set_throttle(-0.3)
    elif y > IMAGE_HEIGHT - (IMAGE_HEIGHT / 2 * 0.3):
            print("上端")
            drone.set_throttle(-0.7)
    elif y > IMAGE_HEIGHT - (IMAGE_HEIGHT / 2 * 0.8) : 
            print("上中")
            drone.set_throttle(0.3)
    else : 
            print("真ん中")
            drone.set_throttle(0)

    preX = x
    preY = y

def main():
    drone = tellopy.Tello()
    face_cascade = 'haarcascade_frontalface_default.xml'
    face_dlib = dlib.get_frontal_face_detector()
    cascade = cv2.CascadeClassifier(face_cascade)

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

        # skip first 300 frames
        frame_skip = 300
        while True:
            for frame in container.decode(video=0):
                if 0 < frame_skip:
                    frame_skip = frame_skip - 1
                    continue
                start_time = time.time()
                image = cv2.cvtColor(numpy.array(frame.to_image()), cv2.COLOR_RGB2BGR)
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                # #カスケードファイルと使って顔認証
                #faces = cascade.detectMultiScale(image)
                faces = face_dlib(image, 1)
                '''
                for (x, y, w, h) in faces:
                    cv2.rectangle(image, (x,y),(x+w,y+h),(255,0,0),2)
                '''
                for i, face_rect in enumerate(faces):
                    #ここが処理部分
                    cv2.rectangle(image, tuple([face_rect.left(),face_rect.top()]), tuple([face_rect.right(),face_rect.bottom()]), (0, 0,255), thickness=2)
                    tracking(drone, gray, (int)((face_rect.right() - face_rect.left()) / 2), (int)((face_rect.top() - face_rect.bottom()) / 2))
                    #tracking(drone, image, (int)(x + (w / 2)), (int)(y + (h / 2)))
                cv2.imshow('Original', image)
                #cv2.imshow('Gray', gray)
                cv2.waitKey(1)
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
