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
parser.add_argument('--threshold', type=int, default=0,
                    help='threshold of difference over which we analyse an image')
parser.add_argument('--quantile', type=float, default=0.95,
                    help='quantile of images to analyse')

args = parser.parse_args()

# Load the metrics for the face and smile detectors
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
smile_cascade = cv2.CascadeClassifier('haarcascade_smile.xml')

def detect(gray, frame):
    # detect faces within the greyscale version of the frame
    faces = face_cascade.detectMultiScale(gray, 1.1, 3)
    num_smiles = 0

    # For each face we find...
    for (x, y, w, h) in faces:
        if args.verbose: # draw rectangle if in verbose mode
            cv2.rectangle(frame, (x, y), ((x + w), (y + h)), (255, 0, 0), 2)

        # Calculate the "region of interest", ie the are of the frame
        # containing the face
        roi_gray = gray[y:y+h, x:x+w]
        roi_color = frame[y:y+h, x:x+w]

        # Within the grayscale ROI, look for smiles 
        smiles = smile_cascade.detectMultiScale(roi_gray, 1.05, 6)

        # If we find smiles then increment our counter
        if len(smiles):
            num_smiles += 1

        # If verbose, draw a rectangle on the image indicating where the smile was found
        if args.verbose:
            for (sx, sy, sw, sh) in smiles:
                cv2.rectangle(roi_color, (sx, sy), ((sx + sw), (sy + sh)), (0, 0, 255), 2)

    return num_smiles, frame

# We just want to check 5% of frames most different from their predecessor
quan = args.quantile
thresh = args.threshold
counts = []

if thresh == 0:
    # No threhold supplied so run first stage to calculate
    # threshold in which we try to work out how different
    # each frame is
    print("Pre analysis stage")

    # Open the image file and extract first frame
    cap = cv2.VideoCapture(args.video_fn)
    ret, prev_frame = cap.read()

    while 1:
        # Read each frame of the video
        ret, frame = cap.read()

        # End of file, so break loop
        if not ret:
            break

        # Calculate the pixel difference between the current
        # frame and the previous one
        diff = cv2.absdiff(frame, prev_frame)
        non_zero_count = np.count_nonzero(diff)

        # Append the count to our list of counts
        counts.append(non_zero_count)
        prev_frame = frame

    thresh = int(np.quantile(counts, quan))

print("Threshold:", thresh)

# The second stage in which we do the actual analysis
print("Smile detection stage")

# Open the file and capture first frame
cap = cv2.VideoCapture(args.video_fn)
ret, prev_frame = cap.read()

# Keep track of best frame and the high water mark of
# smiles found in each frame
best_image = prev_frame
max_smiles = -1

while 1:
    # Read each frame
    ret, frame = cap.read()

    # End of file, so break loop
    if not ret:
        break

    # Calculate the difference of frame to previous one
    diff = cv2.absdiff(frame, prev_frame)
    non_zero_count = np.count_nonzero(diff)

    # If not "different enough" then short circuit this loop
    if non_zero_count < thresh:
        prev_frame = frame
        continue

    # Convert the frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Call the detector function
    num_smiles, image = detect(gray, frame.copy())

    # Check if we have more smiles in this frame
    # than out "best" frame
    if num_smiles > max_smiles:
        max_smiles = num_smiles
        best_image = image
        # If verbose then show the image to console
        if args.verbose:
            print(max_smiles)
            cv2.imshow('Video', best_image)
            cv2.waitKey(1)

    prev_frame = frame

# Write out our "best" frame and clean up
print("Number of smiles found:", max_smiles)
cv2.imwrite(args.image_fn, best_image)
cap.release()
cv2.destroyAllWindows()
