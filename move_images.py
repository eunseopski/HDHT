import os
import shutil
from glob import glob

src_dirs = [
    "/home/choi/hwang/workspace/HeadHunter/datasets/crowdhuman/CrowdHuman_train01/Images",
    "/home/choi/hwang/workspace/HeadHunter/datasets/crowdhuman/CrowdHuman_train02/Images",
    "/home/choi/hwang/workspace/HeadHunter/datasets/crowdhuman/CrowdHuman_train03/Images",
]

dst_dir = "/home/choi/hwang/workspace/HeadHunter/datasets/train"
os.makedirs(dst_dir, exist_ok=True)

for src_dir in src_dirs:
    img_files = glob(os.path.join(src_dir, "*.jpg"))
    for img_path in img_files:
        filename = os.path.basename(img_path)
        dst_path = os.path.join(dst_dir, filename)
        
        # 이름 겹치면 경고 출력
        if os.path.exists(dst_path):
            print(f"⚠️ 중복 파일 있음: {filename} → 덮어쓰거나 이름 바꿔야 함!")
        else:
            shutil.copy2(img_path, dst_path)

print("이미지 복사 완료!")
