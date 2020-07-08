import numpy as np
import cv2
import argparse

parser = argparse.ArgumentParser(description='Save thumbnail of smiliest frame in video')
parser.add_argument('video_fn', type=str,
                    help='filename for video to analyse')
parser.add_argument('image_fn', type=str,
                    help='filename for output thumbnail')
parser.add_argument('--verbose', action='store_true',
                    help='verbose mode')

args = parser.parse_args()

face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
smile_cascade = cv2.CascadeClassifier('haarcascade_smile.xml')

def detect(gray, frame):
    faces = face_cascade.detectMultiScale(gray, 1.1, 3)
    num_smiles = 0

    for (x, y, w, h) in faces:
        if args.verbose:
            cv2.rectangle(frame, (x, y), ((x + w), (y + h)), (255, 0, 0), 2)

        roi_gray = gray[y:y+h, x:x+w]
        roi_color = frame[y:y+h, x:x+w]

        smiles = smile_cascade.detectMultiScale(roi_gray, 1.05, 6)
        if len(smiles):
            num_smiles += 1

        if args.verbose:
            for (sx, sy, sw, sh) in smiles:
                cv2.rectangle(roi_color, (sx, sy), ((sx + sw), (sy + sh)), (0, 0, 255), 2)

    return num_smiles, frame

counts = []
quan = 0.95

print("Pre analysis stage")

cap = cv2.VideoCapture(args.video_fn)
ret, prev_frame = cap.read()

while 1:
    ret, frame = cap.read()

    if not ret:
        break

    diff = cv2.absdiff(frame, prev_frame)
    non_zero_count = np.count_nonzero(diff)

    counts.append(non_zero_count)
    prev_frame = frame

thresh = np.quantile(counts, quan)
print("Threshold:", thresh)

print("Smile detection stage")

cap = cv2.VideoCapture(args.video_fn)
ret, prev_frame = cap.read()

best_image = prev_frame
max_smiles = -1

while 1:
    ret, frame = cap.read()

    if not ret:
        break

    diff = cv2.absdiff(frame, prev_frame)
    non_zero_count = np.count_nonzero(diff)

    if non_zero_count < thresh:
        prev_frame = frame
        continue

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # call the detector function
    num_smiles, image = detect(gray, frame.copy())

    if num_smiles > max_smiles:
        max_smiles = num_smiles
        best_image = image
        if args.verbose:
            print(max_smiles)
            cv2.imshow('Video', best_image)
            cv2.waitKey(1)

    prev_frame = frame

print("Number of smiles found:", max_smiles)
cv2.imwrite(args.image_fn, best_image)
cap.release()
cv2.destroyAllWindows()
