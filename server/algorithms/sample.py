import cv2
import imageio
import os
import numpy as np

# Each algorithm should be in a file like this, any number of subdiretories or other files can be added, 
# but this root file with a proc_call function must be present.
# This function with these parameters is required from all algorithms for them to be called consistently within the worker.
def proc_call(token, store_path, out_path) -> tuple[int, str]:
    #os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;udp"
    #print(cv2.getBuildInformation())
    print(f"Successful SAMPLE proc call {token}")
    print(f"Filepath: {store_path}")
    if not os.path.exists(out_path):
        os.makedirs(out_path)
    if not os.path.isfile(store_path):
        raise Exception("File does not exist")
    status, msg = process(token, store_path, out_path)
    if status != 0:
        raise Exception(msg)
    return status, msg

    
# sample algorithm that uses opencv to split the video into 4 parts
def process(token, store_path, out_path):
    reader = imageio.get_reader(store_path)
    md = reader.get_meta_data()
    fps = md['fps']
    # w,h = md['size']
    frames = reader.count_frames()
    writers = [imageio.get_writer(os.path.join(out_path, f"SAMPLE_{token}__{i}.mp4"),fps=fps, macro_block_size=None) for i in range(4)]

    parts = 1
    for i, frame in enumerate(reader):
        print(i)
        # Gets most dominant color from frame
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pixels = img.reshape((-1, 3))
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
        _, _, centers = cv2.kmeans(np.float32(pixels), 1, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
        dominant_color = centers[0].astype(np.uint8)
        
        # Prints dominant color onto the frame
        new_frame = cv2.putText(frame, f"COLOR: {dominant_color}", (50,50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 2, cv2.LINE_4)
        
        # Advances cursor to next frame
        if i == frames*(parts/4):
            parts+=1
        writers[parts-1].append_data(new_frame)

    for w in writers:
        w.close()
    reader.close()

    return 0, out_path
