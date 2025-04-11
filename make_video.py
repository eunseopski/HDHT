import cv2
import os

# 이미지가 저장된 폴더 경로
image_folder = '/home/choi/hwang/workspace/HeadHunter/MOT17_results'  # 예: 'C:/images/'

# 동영상으로 저장할 파일 경로 및 이름
output_video = '/home/choi/hwang/workspace/HeadHunter/MOT17_results.avi'


# 폴더 내 이미지 파일 리스트 불러오기
images = [img for img in os.listdir(image_folder) if img.endswith(".png") or img.endswith(".jpg")]

# 이미지 이름을 알파벳, 숫자 순으로 정렬
images.sort()  # 기본적으로 알파벳 순으로 정렬

# 이미지들로 동영상을 만들기 위해 첫 번째 이미지에서 크기 추출
first_image = cv2.imread(os.path.join(image_folder, images[0]))
height, width, _ = first_image.shape

# 동영상 저장을 위한 VideoWriter 객체 생성 (프레임 레이트는 30fps로 설정)
fourcc = cv2.VideoWriter_fourcc(*'XVID')  # 코덱 설정 (avi 형식)
out = cv2.VideoWriter(output_video, fourcc, 25, (width, height))

# 이미지들을 순차적으로 동영상에 추가
for image in images:
    img = cv2.imread(os.path.join(image_folder, image))
    out.write(img)  # 동영상에 이미지 추가

# 작업 완료 후 VideoWriter 객체 해제
out.release()

print("동영상이 생성되었습니다!")
