import torch

# 1. 경로에 있는 weight 파일 로드
state = torch.load('model/FT_R50_epoch_24.pth', map_location='cpu')

# 2. 키 출력
print("== 전체 key 목록 ==")
for key in state.keys():
    print(key)

# 3. state_dict 안에 'state_dict'나 'model' 키가 있을 경우
if 'state_dict' in state:
    print("\n== 내부 'state_dict' 키 목록 ==")
    for k in state['state_dict'].keys():
        print(k)
elif 'model' in state:
    print("\n== 내부 'model' 키 목록 ==")
    for k in state['model'].keys():
        print(k)
else:
    print("\n== 상위 key들이 곧바로 weight일 가능성 ==")
    for k in state.keys():
        print(k)
