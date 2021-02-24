# Usage: python watermarkIt.py --watermark <path to watermark image> --input <input_dir> --output <output_dir>

from imutils import paths
import numpy as np
import argparse
import cv2
import os

ap = argparse.ArgumentParser()
ap.add_argument("-w", "--watermark", required=True, help="path to watermark image")
ap.add_argument("-i", "--input", required=True, help="path to input directory")
ap.add_argument("-o", "--output", required=True, help="path to output directory")
ap.add_argument("-a", "--alpha", type=float, default=0.25, help="alpha transparency of the overlay (smaller is more transparent")
ap.add_argument("-c", "--correct", type=int, default=1, help="flag used to handle if bug is displayed or not")
args = vars(ap.parse_args())

# load watermark image, retain the 4th channel which contains alpha transparency
watermark = cv2.imread(args["watermark"], cv2.IMREAD_UNCHANGED)
(wH, wW) = watermark.shape[:2]

# split watermark into 4 different channels
if args["correct"] > 0:
    watermark = cv2.cvtColor(watermark, cv2.COLOR_BGR2BGRA)
    (B, G, R, A) = cv2.split(watermark)
    B = cv2.bitwise_and(B, B, mask=A)
    G = cv2.bitwise_and(G, G, mask=A)
    R = cv2.bitwise_and(R, R, mask=A)
    watermark = cv2.merge([B, G, R, A])

for imagePath in paths.list_images(args["input"]):
    image = cv2.imread(imagePath)
    (h, w) = image.shape[:2]
    image = np.dstack([image, np.ones((h, w), dtype='uint8') * 255])

    # construct overlay with same size as the input then add watermark to this overlay
    overlay = np.zeros((h, w, 4), dtype="uint8")
    overlay[h-wH-10 : h-10, w-wW-10 : w-10] = watermark

    # blend the two images together using transparent overlays
    output = image.copy()
    cv2.addWeighted(overlay, args["alpha"], output, 1.0, 0, output)

    # write image to disk
    filename = imagePath[imagePath.rfind(os.path.sep) + 1:]
    p = os.path.sep.join((args["output"], filename))
    cv2.imwrite(p, output)

print('Done')