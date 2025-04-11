import os
import xml.etree.ElementTree as ET

# 경로 설정
train_txt_path = "/home/choi/hwang/workspace/HeadHunter/datasets/SCUT_HEAD/SCUT_HEAD_Part_B/ImageSets/Main/test.txt"
annotations_dir = "/home/choi/hwang/workspace/HeadHunter/datasets/SCUT_HEAD/SCUT_HEAD_Part_B/Annotations"
image_base_path = "/home/choi/hwang/workspace/HeadHunter/datasets/test"
output_txt_path = "/home/choi/hwang/workspace/HeadHunter/datasets/test/1_scut_head_B.txt"

# train.txt에 있는 이미지 이름들 가져오기
with open(train_txt_path, 'r') as f:
    image_ids = [line.strip() for line in f.readlines()]

# 출력 파일 열기
with open(output_txt_path, 'w') as out_f:
    for img_id in image_ids:
        xml_file = os.path.join(annotations_dir, f"{img_id}.xml")
        tree = ET.parse(xml_file)
        root = tree.getroot()

        # 이미지 경로 먼저 작성
        image_path = os.path.join(image_base_path, f"{img_id}.jpg")
        out_f.write(f"{image_path}\n")

        for obj in root.findall("object"):
            name = obj.find("name").text
            if name != "person":
                continue

            bndbox = obj.find("bndbox")
            xmin = bndbox.find("xmin").text
            ymin = bndbox.find("ymin").text
            xmax = bndbox.find("xmax").text
            ymax = bndbox.find("ymax").text

            out_f.write(f"{xmin},{ymin},{xmax},{ymax}\n")

print(f"완성! ➜ {output_txt_path}")
