import cv2
import os

def extract_frames(video_path, output_dir, step=1):
    os.makedirs(output_dir, exist_ok=True)

    cap = cv2.VideoCapture(video_path)
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    idx = 1
    frame_idx = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # step 만큼 건너뛰며 저장
        if frame_idx % step == 0:
            filename = f"{idx:06d}.jpg"
            cv2.imwrite(os.path.join(output_dir, filename), frame)
            idx += 1

        frame_idx += 1

    cap.release()
    print(f"[Done] Extracted {idx - 1} frames to {output_dir}")

# 사용 예시
extract_frames("sample_video/gymnasts.mp4", "sample_sequence", step=5)
