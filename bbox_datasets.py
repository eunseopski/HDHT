import cv2
import matplotlib.pyplot as plt
import os

def draw_bboxes_from_file(txt_path, show=True, save_dir=None):
    os.makedirs(save_dir, exist_ok=True) if save_dir else None

    with open(txt_path, 'r') as f:
        lines = f.readlines()

    current_img = None
    bboxes = []
    img_filename = None

    for line in lines:
        line = line.strip()
        if line.startswith('#'):
            # 이전 이미지 처리
            if current_img is not None:
                for bbox in bboxes:
                    x1, y1, x2, y2, _ = bbox
                    cv2.rectangle(current_img, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)

                if save_dir:
                    save_path = os.path.join(save_dir, os.path.basename(img_filename))
                    cv2.imwrite(save_path, current_img)
                    print(f"[저장 완료] {save_path}")

                if show:
                    plt.imshow(cv2.cvtColor(current_img, cv2.COLOR_BGR2RGB))
                    plt.title(img_filename)
                    plt.axis('off')
                    plt.show()

            # 새 이미지 준비
            img_filename = line[1:]  # '#' 제거
            current_img = cv2.imread(img_filename)
            bboxes = []

        elif line:
            bbox = list(map(float, line.split(',')))
            bboxes.append(bbox)

    # 마지막 이미지 처리
    if current_img is not None:
        for bbox in bboxes:
            x1, y1, x2, y2, _ = bbox
            cv2.rectangle(current_img, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)

        if save_dir:
            save_path = os.path.join(save_dir, os.path.basename(img_filename))
            cv2.imwrite(save_path, current_img)
            print(f"[저장 완료] {save_path}")

        if show:
            plt.imshow(cv2.cvtColor(current_img, cv2.COLOR_BGR2RGB))
            plt.title(img_filename)
            plt.axis('off')
            plt.show()

# 사용 예시
draw_bboxes_from_file(
    '/home/choi/hwang/workspace/HeadHunter/datasets/train/1_crowdhuman_tem.txt',
    show=False,
    save_dir='/home/choi/hwang/workspace/HeadHunter/bboxes_images'
)
