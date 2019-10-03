import sys
import traceback
import tellopy
import av
import cv2.cv2 as cv2  # for avoidance of pylint error
import numpy
import time


def main():
    drone = tellopy.Tello()
    face_cascade = 'haarcascade_frontalface_default.xml'
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
                faces = cascade.detectMultiScale(image)
                for (x, y, w, h) in faces:
                    cv2.rectangle(image, (x,y),(x+w,y+h),(255,0,0),2)
                cv2.imshow('Original', image)
                cv2.imshow('Gray', gray)
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

#
#img = cv2.imread('img.jpg')
#gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#カスケードファイルの読み込み
#face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
#カスケードファイルと使って顔認証
#faces = face_cascade.detectMultiScale(gray)
#for (x,y,w,h) in faces:
#    #顔部分を四角で囲う
#    cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
#    cv2.imshow('img',img)
#    cv2.waitKey(0)
#    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
