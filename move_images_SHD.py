import os
import shutil

# txt 파일 경로
input_txt = "/home/choi/hwang/workspace/HeadHunter/datasets/test/1_scut_head_B.txt"

# 이미지가 있는 원본 폴더
source_dir = "/home/choi/hwang/workspace/HeadHunter/datasets/SCUT_HEAD/SCUT_HEAD_Part_B/JPEGImages"

# 복사할 대상 폴더
target_dir = "/home/choi/hwang/workspace/HeadHunter/datasets/test"

# 파일 열어서 이미지 경로만 추출
with open(input_txt, 'r') as f:
    lines = f.readlines()

# 이미지 경로는 "/"로 시작하고 ".jpg"로 끝남
image_paths = [line.strip() for line in lines if line.strip().endswith(".jpg")]

# 각 이미지 복사
for full_path in image_paths:
    filename = os.path.basename(full_path)
    src = os.path.join(source_dir, filename)
    dst = os.path.join(target_dir, filename)

    if os.path.exists(src):
        shutil.copy(src, dst)
    else:
        print(f"❗ {filename} 파일 없음! (복사 생략)")

print("🎉 이미지 복사 완료!")
