# def add_ignore_flag_to_file(file_path):
#     with open(file_path, 'r') as f:
#         lines = f.readlines()
#
#     new_lines = []
#     for line in lines:
#         line = line.strip()
#         if line.startswith('#') or line == '':
#             new_lines.append(line)
#         else:
#             new_lines.append(f'{line},0')
#
#     with open(file_path, 'w') as f:
#         f.write('\n'.join(new_lines))
#     print(f"Updated file: {file_path}")
#
#
# # 사용 예시
# add_ignore_flag_to_file('/home/choi/hwang/workspace/HeadHunter/datasets/train/1_crowdhuman.txt')
# add_ignore_flag_to_file('/home/choi/hwang/workspace/HeadHunter/datasets/valid/1_crowdhuman.txt')

def remove_single_ignore_flag(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()

    new_lines = []
    for line in lines:
        line = line.strip()
        if line.startswith('#') or line == '':
            new_lines.append(line)
        elif line.endswith(',0'):
            new_lines.append(line[:-2])  # 맨 끝의 ',0'만 제거
        else:
            new_lines.append(line)

    with open(file_path, 'w') as f:
        f.write('\n'.join(new_lines))
    print(f"Cleaned file: {file_path}")


# 사용 예시
remove_single_ignore_flag('/home/choi/hwang/workspace/HeadHunter/datasets/train/1_crowdhuman.txt')
remove_single_ignore_flag('/home/choi/hwang/workspace/HeadHunter/datasets/valid/1_crowdhuman.txt')
