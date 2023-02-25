import cv2
import numpy as np
import dlib
from imutils import face_utils
import imutils


class FaceDetection:
    def __init__(self):
        self.face_detector = dlib.get_frontal_face_detector()
        self.shape_predictor = dlib.shape_predictor("shape_predictor_68.dat")
        self.face_aligner = face_utils.FaceAligner(
            self.shape_predictor, desiredFaceWidth=256
        )

    def detect_face(self, frame):
        if frame is None:
            return

        status = False

        face = np.zeros((10, 10, 3), np.uint8)
        mask = np.zeros((10, 10, 3), np.uint8)

        ROI1 = np.zeros((10, 10, 3), np.uint8)
        ROI2 = np.zeros((10, 10, 3), np.uint8)

        # convert the input frame from BGR to grayscale
        grayscale = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # detect faces in the grayscale frame
        rect = self.face_detector(grayscale, 0)

        # check to see if a face was detected
        if len(rect) > 0:
            status = True

            # convert the dlib rectangle into an OpenCV bounding box
            (x, y, w, h) = face_utils.rect_to_bb(rect[0])

            if y < 0:
                print("Invalid face detected!")
                return frame, face, ROI1, ROI2, status, mask

            # get the face from the frame
            face = frame[y : y + h, x : x + w]

            # resize the face to 256x256
            if face.shape[:2][1] != 0:
                face = imutils.resize(face, width=256)

            # align the face
            face = self.face_aligner.align(frame, grayscale, rect[0])

            gray_face = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
            rect_face = self.face_detector(gray_face, 0)

            if len(rect_face) > 0:
                shape = self.shape_predictor(gray_face, rect_face[0])
                shape = face_utils.shape_to_np(shape)

                # right cheek
                ROI1 = face[
                    shape[29][1] : shape[33][1],
                    shape[54][0] : shape[12][0],
                ]

                # left cheek
                ROI2 = face[
                    shape[29][1] : shape[33][1],
                    shape[4][0] : shape[48][0],
                ]

        else:
            print("No face detected!")
            status = False

        return frame, face, ROI1, ROI2, status
