import json
import matplotlib.pyplot as plt
from PIL import Image
import matplotlib.patches as patches

# === STEP 1: 이미지 경로랑 annotation 불러오기 ===
# 👉 실제 이미지 파일 경로로 바꿔줘!
img_path = "/home/choi/hwang/workspace/datasets/crowdhuman/CrowdHuman_train01/Images/273271,11dc7000c35a2f2d.jpg"

# 👉 JSON 데이터 불러오기 (네가 준 내용 여기에 직접 넣어도 됨!)
data = {"ID": "273271,11dc7000c35a2f2d", "gtboxes": [{"tag": "person", "hbox": [781, 944, 275, 396], "head_attr": {"ignore": 0, "occ": 0, "unsure": 0}, "fbox": [306, 866, 1234, 1839], "vbox": [375, 881, 1162, 1175], "extra": {"box_id": 0, "occ": 1}}, {"tag": "person", "hbox": [785, 947, 280, 398], "head_attr": {"ignore": 1, "occ": 0, "unsure": 0}, "fbox": [554, 881, 1287, 1736], "vbox": [666, 882, 1146, 1431], "extra": {"ignore": 0, "box_id": 1, "occ": 1, "unsure": 0}}, {"tag": "person", "hbox": [1094, 999, 229, 303], "head_attr": {"ignore": 0, "occ": 0, "unsure": 0}, "fbox": [961, 965, 869, 1611], "vbox": [961, 965, 869, 1338], "extra": {"box_id": 2, "occ": 0}}, {"tag": "person", "hbox": [293, 220, 205, 284], "head_attr": {"ignore": 0, "occ": 0, "unsure": 0}, "fbox": [-29, 189, 735, 1983], "vbox": [-1, 191, 682, 1368], "extra": {"box_id": 3, "occ": 1}}, {"tag": "person", "hbox": [687, 404, 196, 249], "head_attr": {"ignore": 0, "occ": 0, "unsure": 0}, "fbox": [527, 368, 583, 1801], "vbox": [598, 376, 499, 605], "extra": {"box_id": 4, "occ": 1}}, {"tag": "person", "hbox": [1161, 439, 146, 192], "head_attr": {"ignore": 0, "occ": 0, "unsure": 0}, "fbox": [987, 417, 420, 1481], "vbox": [1010, 431, 400, 943], "extra": {"box_id": 5, "occ": 1}}, {"tag": "person", "hbox": [1472, 1081, 184, 259], "head_attr": {"ignore": 0, "occ": 0, "unsure": 0}, "fbox": [1326, 1052, 861, 1378], "vbox": [1326, 1052, 861, 1251], "extra": {"box_id": 6, "occ": 0}}, {"tag": "person", "hbox": [1540, 444, 164, 216], "head_attr": {"ignore": 0, "occ": 0, "unsure": 0}, "fbox": [1350, 431, 445, 1319], "vbox": [1374, 442, 397, 884], "extra": {"box_id": 7, "occ": 1}}, {"tag": "person", "hbox": [1842, 516, 136, 198], "head_attr": {"ignore": 0, "occ": 0, "unsure": 0}, "fbox": [1676, 495, 429, 1288], "vbox": [1676, 498, 409, 899], "extra": {"box_id": 8, "occ": 1}}, {"tag": "person", "hbox": [2025, 1087, 178, 258], "head_attr": {"ignore": 0, "occ": 0, "unsure": 0}, "fbox": [1903, 1053, 496, 1423], "vbox": [1903, 1053, 496, 1250], "extra": {"box_id": 9, "occ": 0}}, {"tag": "person", "hbox": [2159, 593, 161, 210], "head_attr": {"ignore": 0, "occ": 0, "unsure": 0}, "fbox": [2017, 577, 450, 1252], "vbox": [2052, 591, 396, 818], "extra": {"box_id": 10, "occ": 1}}, {"tag": "person", "hbox": [2412, 1090, 191, 241], "head_attr": {"ignore": 0, "occ": 0, "unsure": 0}, "fbox": [2273, 1069, 684, 1248], "vbox": [2279, 1082, 614, 877], "extra": {"box_id": 11, "occ": 1}}, {"tag": "person", "hbox": [2478, 557, 153, 180], "head_attr": {"ignore": 0, "occ": 0, "unsure": 0}, "fbox": [2348, 527, 436, 1277], "vbox": [2353, 554, 406, 839], "extra": {"box_id": 12, "occ": 1}}, {"tag": "person", "hbox": [2815, 627, 176, 197], "head_attr": {"ignore": 0, "occ": 0, "unsure": 0}, "fbox": [2697, 609, 425, 1331], "vbox": [2697, 617, 420, 773], "extra": {"box_id": 13, "occ": 1}}, {"tag": "person", "hbox": [3099, 540, 172, 219], "head_attr": {"ignore": 0, "occ": 0, "unsure": 0}, "fbox": [3017, 505, 580, 1467], "vbox": [3025, 524, 566, 909], "extra": {"box_id": 14, "occ": 1}}, {"tag": "person", "hbox": [2868, 1093, 167, 214], "head_attr": {"ignore": 0, "occ": 0, "unsure": 0}, "fbox": [2740, 1059, 648, 1363], "vbox": [2748, 1077, 640, 846], "extra": {"box_id": 15, "occ": 1}}, {"tag": "person", "hbox": [3321, 1104, 244, 299], "head_attr": {"ignore": 0, "occ": 0, "unsure": 0}, "fbox": [3225, 1084, 522, 1507], "vbox": [3226, 1104, 520, 982], "extra": {"box_id": 16, "occ": 1}}, {"tag": "person", "hbox": [3690, 1086, 225, 274], "head_attr": {"ignore": 0, "occ": 0, "unsure": 0}, "fbox": [3599, 595, 723, 1956], "vbox": [3634, 598, 615, 1643], "extra": {"box_id": 17, "occ": 1}}]}
# === STEP 2: 이미지 불러오기 ===
image = Image.open(img_path)

# === STEP 3: 시각화 ===
fig, ax = plt.subplots(1)
ax.imshow(image)

for box in data['gtboxes']:
    if box['tag'] != 'person':
        continue  # 사람만 표시!

    hbox = box['hbox']
    x, y, w, h = hbox
    rect = patches.Rectangle(
        (x, y), w, h,
        linewidth=2,
        edgecolor='red' if box['head_attr']['ignore'] else 'green',
        facecolor='none'
    )

    ax.add_patch(rect)

    # box_id를 label로 표시
    box_id = box.get("extra", {}).get("box_id", "N/A")
    label = f"id:{box_id}"
    ax.text(x, y - 5, label, color='yellow', fontsize=10, weight='bold')

plt.axis('off')
plt.title("Head Boxes Visualization (Red = Ignored, Green = Used)")
plt.show()
