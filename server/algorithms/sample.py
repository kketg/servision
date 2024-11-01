import cv2
import os
import numpy as np

# Each algorithm should be in a file like this, any number of subdiretories or other files can be added, 
# but this root file with a proc_call function must be present.
# This function with these parameters is required from all algorithms for them to be called consistently within the worker.
def proc_call(token, store_path, out_path) -> tuple[int, str]:
    print(f"Successful SAMPLE proc call {token}")
    return slay(token, store_path, out_path)

    
# sample algorithm that uses opencv to split the video into 4 parts
def slay(token, store_path, out_path):
    
    cap = cv2.VideoCapture(store_path)
    ret, frame = cap.read()
    frames = cap.get(cv2.CAP_PROP_FRAME_COUNT) 
    fps = cap.get(cv2.CAP_PROP_FPS) 
    if frames == 0 or fps == 0:
        return 1, "Given video file may be empty"
    h,w,_ = frame.shape
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writers = [cv2.VideoWriter(os.path.join(out_path, f"SAMPLE_{token}__{i}.mp4"),fourcc,fps,(w,h)) for i in range(4)]
    
    parts = 1
    f = 0
    while ret:
        f+=1
        # Gets most dominant color from frame
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pixels = img.reshape((-1, 3))
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
        _, _, centers = cv2.kmeans(np.float32(pixels), 1, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
        dominant_color = centers[0].astype(np.uint8)
        # Prints dominant color onto the frame
        cv2.putText(frame, f"COLOR: {dominant_color}",(25,25), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_4)

        # Advances cursor to next frame
        if f == frames*(parts/4):
            parts+=1
        writers[parts-1].write(frame)
        ret, frame = cap.read()

    for w in writers:
        w.release()

    cap.release()

    return 0, out_path
