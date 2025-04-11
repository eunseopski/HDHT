import json
import os

# 원본 파일 경로
input_path = "/home/choi/hwang/workspace/HeadHunter/datasets/crowdhuman/annotation_val.odgt"
# 출력 파일 경로
output_path = "/home/choi/hwang/workspace/HeadHunter/datasets/valid/crowdhuman.txt"
base_path = "/home/choi/hwang/workspace/HeadHunter/datasets/valid"

with open(input_path, 'r') as f:
    lines = f.readlines()

data = []
for line in lines:
    obj = json.loads(line)
    img_id = obj["ID"]
    hboxes = [
        box["hbox"]
        for box in obj["gtboxes"]
        if (
            "hbox" in box
            and box.get("tag") == "person"
            and box.get("head_attr", {}).get("ignore", 0) != 1
        )
    ]
    data.append((img_id, hboxes))

# ID 기준 정렬
data.sort(key=lambda x: x[0])

# 포맷에 맞게 저장
with open(output_path, 'w') as f:
    for img_id, hboxes in data:
        image_path = os.path.join(base_path, img_id + ".jpg")
        f.write(f"{image_path}\n")
        for hbox in hboxes:
            x_min, y_min, w, h = hbox
            x_max = x_min + w
            y_max = y_min + h
            f.write(f"{x_min},{y_min},{x_max},{y_max}\n")

print(f"완성! ➜ {output_path}")
