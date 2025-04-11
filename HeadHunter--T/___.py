import torch

# CUDA가 사용 가능한지 확인
cuda_available = torch.cuda.is_available()

# CUDA 정보 출력
if cuda_available:
    print("CUDA is available!")
    print("CUDA Version:", torch.version.cuda)
    print("Number of GPUs:", torch.cuda.device_count())
    print("Current GPU:", torch.cuda.current_device())
    print("GPU Name:", torch.cuda.get_device_name(torch.cuda.current_device()))
else:
    print("CUDA is not available. Running on CPU.")
