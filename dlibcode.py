import dlib
from skimage import io
import cv2
from timeit import default_timer as timer
from math import *

IMAGE_WIDTH = 640
IMAGE_HEIGHT = 480
DRONE_DIS_LOWER = 60
DRONE_DIS_UPPER = 90


def tracking(image, x, y, dis):
    global IMGAE_WIDTH, IMAGE_HEIGHT
    print("x y dis = ", x, " ", y, " ", dis)
    cv2.rectangle(image, (x-1, y-1), (x+2, y+2), (255, 0, 255), 2)
    if x < IMAGE_WIDTH / 2 * 0.3 :
        print("左端")
    elif x < IMAGE_WIDTH / 2 * 0.8 :
        print("左中")
    elif x > IMAGE_WIDTH - (IMAGE_WIDTH / 2 * 0.3):
        print("右端")
    elif x > IMAGE_WIDTH - (IMAGE_WIDTH / 2 * 0.8) : 
        print("右中")
    else : 
        print("真ん中")

    if y < IMAGE_HEIGHT / 2 * 0.3 :
        print("下端")
    elif y < IMAGE_HEIGHT / 2 * 0.8 :
        print("下中")
    elif y > IMAGE_HEIGHT - (IMAGE_HEIGHT / 2 * 0.3):
            print("上端")
    elif y > IMAGE_HEIGHT - (IMAGE_HEIGHT / 2 * 0.8) : 
            print("上中")
    else : 
            print("真ん中")
    
    if dis < DRONE_DIS_LOWER:
        print("遠い")
    elif dis < DRONE_DIS_UPPER:
        print("ちょうどいい")
    else:
        print("近い")


def detect_video(detector, video_path, output_path=""):
    global IMGAE_WIDTH, IMAGE_HEIGHT
    vid = cv2.VideoCapture(video_path)
    if not vid.isOpened():
        raise IOError("Couldn't open webcam or video")
    video_FourCC    = int(vid.get(cv2.CAP_PROP_FOURCC))
    video_fps       = vid.get(cv2.CAP_PROP_FPS)
    video_size      = (int(vid.get(cv2.CAP_PROP_FRAME_WIDTH)),
                        int(vid.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    isOutput = True if output_path != "" else False
    if isOutput:
        print("!!! TYPE:", type(output_path), type(video_FourCC), type(video_fps), type(video_size))
        out = cv2.VideoWriter(output_path, video_FourCC, video_fps, video_size)
    accum_time = 0
    curr_fps = 0
    fps = "FPS: ??"
    prev_time = timer()
    while True:
        return_value, frame = vid.read()
        #print(type(frame))
        result = detector(frame, 1)
        curr_time = timer()
        exec_time = curr_time - prev_time
        prev_time = curr_time
        accum_time = accum_time + exec_time
        curr_fps = curr_fps + 1
        #print(frame.shape)
        if accum_time > 1:
            accum_time = accum_time - 1
            fps = "FPS: " + str(curr_fps)
            curr_fps = 0
        for i, face_rect in enumerate(result):
            #ここが処理部分
            cv2.rectangle(frame, tuple([face_rect.left(),face_rect.top()]), tuple([face_rect.right(),face_rect.bottom()]), (0, 0,255), thickness=2)
            tracking(frame, (int)((face_rect.right() + face_rect.left()) / 2),
                (int)((face_rect.top() + face_rect.bottom()) / 2),
               sqrt((face_rect.right() - face_rect.left())*(face_rect.bottom() - face_rect.top())))
            #print("顔の長さ ", sqrt((face_rect.right() - face_rect.left())*(face_rect.bottom() - face_rect.top())))
        #cv2.putText(result, text=fps, org=(3, 15), fontFace=cv2.FONT_HERSHEY_SIMPLEX,
#                    fontScale=0.50, color=(255, 0, 0), thickness=2)
        #cv2.namedWindow("result", cv2.WINDOW_NORMAL)
        cv2.imshow("result", frame)
        if isOutput:
            out.write(result)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break



face_detector = dlib.get_frontal_face_detector()
file_name = "pic1.jpg"    #ここに対象のファイル名を入力私の場合はpic1.jpgです
image = cv2.imread(file_name)
#print(type(image))
detect_video(face_detector, 0)
#detected_faces = face_detector(image, 1)
'''
save_image = cv2.imread(file_name, cv2.IMREAD_COLOR)

for i, face_rect in enumerate(detected_faces):
    #ここが処理部分
    cv2.rectangle(save_image, tuple([face_rect.left(),face_rect.top()]), tuple([face_rect.right(),face_rect.bottom()]), (0, 0,255), thickness=2)
    cv2.imwrite('complete_'+file_name, save_image)
'''