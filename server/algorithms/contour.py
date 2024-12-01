import imageio
import cv2
import os
import numpy as np

# Each algorithm should be in a file like this, any number of subdiretories or other files can be added, 
# but this root file with a proc_call function must be present.
# This function with these parameters is required from all algorithms for them to be called consistently within the worker.
def proc_call(token, store_path, out_path) -> tuple[int, str]:
    print(f"Successful SAMPLE proc call {token}")
    print(f"Filepath: {store_path}")
    if not os.path.exists(out_path):
        os.makedirs(out_path)
    if not os.path.isfile(store_path):
        raise Exception("File does not exist")
    status, msg = process(token,store_path,out_path)
    if status != 0:
        raise Exception(msg)
    return status, msg


def process(token, store_path, out_path):
    reader = imageio.get_reader(store_path)
    md = reader.get_meta_data()
    fps = md['fps']
    w,h = md['size']
    duration = md['duration']
    frames = reader.count_frames()
    writer = imageio.get_writer(os.path.join(out_path, f"OTHER_{token}.mp4"),fps=fps, macro_block_size=None)

    w_eighth = int(w/8)
    h_eighth = int(h/8)

    object_detector = cv2.createBackgroundSubtractorMOG2(history=100, varThreshold=40)

    for i, frame in enumerate(reader):
        roi = frame[w_eighth:(w-w_eighth), h_eighth:(h-h_eighth)]
        mask = object_detector.apply(frame)
        _, mask = cv2.threshold(mask, 254, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            # Calculate area and remove small elements
            area = cv2.contourArea(cnt)
            if area > 100:
                cv2.drawContours(frame, [cnt], -1, (0, 255, 0), 2)
                x, y, w, h = cv2.boundingRect(cnt)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)

        writer.append_data(frame)

    writer.close()
    reader.close()
    