from statistics import mode

import cv2
from keras.models import load_model
import numpy as np

from utils.datasets import get_labels
from utils.inference import detect_faces
from utils.inference import draw_text
from utils.inference import draw_bounding_box
from utils.inference import apply_offsets
from utils.inference import load_detection_model
from utils.preprocessor import preprocess_input


detection_model_path = '../trained_models/haarcascade_frontalface_default.xml'
gender_model_path = '../trained_models/CNN.hdf5'
gender_labels = get_labels('imdb', 'Adience', 'imfdb')
font = cv2.FONT_HERSHEY_SIMPLEX

frame_window = 10
gender_offsets = (30, 60)

face_detection = load_detection_model(detection_model_path)
gender_classifier = load_model(gender_model_path, compile=False)

gender_target_size = gender_classifier.input_shape[1:3]

gender_window = []

cv2.namedWindow('window_frame')
video_capture = cv2.VideoCapture('x.MP4')
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('Save.avi', fourcc, 25.0, (1280, 720))
while True:

    bgr_image = video_capture.read()[1]
    rgb_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2RGB)
    faces = detect_faces(face_detection, bgr_image)#gray_image)

    for face_coordinates in faces:

        x1, x2, y1, y2 = apply_offsets(face_coordinates, gender_offsets)
        rgb_face = rgb_image[y1:y2, x1:x2]
        try:
            rgb_face = cv2.resize(rgb_face, (gender_target_size))
        except:
            continue

        rgb_face = np.expand_dims(rgb_face, 0)
        rgb_face = preprocess_input(rgb_face, False)
        gender_prediction = gender_classifier.predict(rgb_face)
        gender_label_arg = np.argmax(gender_prediction)
        gender_text = gender_labels[gender_label_arg]
        gender_window.append(gender_text)

        if len(gender_window) > frame_window:
            gender_window.pop(0)
        try:
            gender_mode = mode(gender_window)
        except:
            continue

        if gender_text == gender_labels[0]:
            color = (0, 0, 255)
        else:
            color = (255, 0, 0)

        draw_bounding_box(face_coordinates, rgb_image, color)
        draw_text(face_coordinates, rgb_image, gender_mode,
                  color, 0, -20, 1, 1)
    
    bgr_image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2BGR)
    out.write(bgr_image)    
    cv2.imshow('window_frame', bgr_image)
	
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

out.release()
