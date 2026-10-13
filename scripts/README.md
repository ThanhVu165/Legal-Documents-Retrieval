# Scripts

`python scripts/check_environment.py` báo Python/platform và GPU qua
`nvidia-smi` nếu có; timeout 15 giây. Exit 1 nếu Python không phải 3.11.
Không tải dữ liệu/model, không xác nhận training/CUDA hoạt động.
