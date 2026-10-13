# Hệ thống tìm kiếm văn bản pháp luật tiếng Việt theo ngữ nghĩa

Đồ án NLP xây dựng tìm kiếm văn bản pháp luật tiếng Việt, so sánh BM25,
BKAI pretrained và BKAI fine-tuned.

## Phạm vi và trạng thái

W01 đã chạy và xác minh audit toàn bộ ba bảng metadata, content, relationships
hiện hành (1.375.635 dòng, gồm cả quan hệ); không lấy legacy. Quyền dữ liệu nguồn còn chưa xác minh. Chưa xây index,
huấn luyện hoặc tạo dữ liệu processed. Xem [CORPUS_AUDIT](docs/CORPUS_AUDIT.md).

| Module | Trạng thái |
| --- | --- |
| Packaging, config, smoke tests, CI definition | Scaffold; chạy theo hướng dẫn dưới đây |
| Dataset inspection/audit W01 | Pipeline full cho ba bảng hiện hành; xem bằng chứng W01 |
| Data cleaning/segmentation/chunking | Not implemented |
| BM25, dense retrieval, ranking/search service | Not implemented |
| BKAI fine-tuning | Not implemented |
| Metrics, error analysis | Not implemented |
| Streamlit, highlighting, feedback | Not implemented |

## Kiến trúc và công nghệ dự kiến

Data → BM25 / BKAI → Ranking ở cấp văn bản → Evaluation → Streamlit.
Python 3.11; BM25 là lexical baseline; semantic model dự kiến:
`bkai-foundation-models/vietnamese-bi-encoder`. Corpus dự kiến:
`th1nhng0/vietnamese-legal-documents`; revision khóa trong configs/corpus.yaml,
schema xác minh bằng footer Parquet. Card công bố CC BY 4.0; quyền nguồn chưa xác minh.
GPU dự kiến NVIDIA T4 trên Colab/Kaggle, chưa khẳng định khả năng huấn luyện.

Package dùng PyYAML và PyArrow cho audit; dev dùng pytest và ruff. PyTorch, Transformers,
Sentence Transformers, thư viện BM25/FAISS và Streamlit sẽ được bổ sung
sau khi kiểm tra tương thích; cài đặt hiện tại không tải model.

## Cấu trúc

```text
.
├── .github/workflows/ci.yml
├── .gitignore, .env.example, pyproject.toml
├── requirements.txt, requirements-dev.txt, app.py
├── configs/                  # corpus, retrieval, training YAML
├── data/                     # raw, interim, processed, annotations, manifests
├── notebooks/                # colab_setup.ipynb
├── scripts/                  # check_environment.py
├── src/legal_retrieval/
│   ├── data/                 # cleaning, segmentation, chunking
│   ├── retrieval/            # bm25, dense, search_service
│   ├── models/               # train_bkai
│   ├── evaluation/           # metrics, error_analysis
│   ├── app/                  # highlighting, feedback
│   └── utils/
├── tests/
├── artifacts/                # indices, checkpoints, embeddings
├── results/                  # figures, tables, logs
├── reports/                  # paper, slides, demo
└── docs/                     # ARCHITECTURE, ROADMAP, EXPERIMENTS
```

## Clone và tạo môi trường

```bash
git clone https://github.com/ThanhVu165/Legal-Documents-Retrieval.git
cd Legal-Documents-Retrieval
```

Windows PowerShell:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Nếu policy chặn activation, dùng trực tiếp `.\.venv\Scripts\python.exe`
thay cho `python` trong các lệnh bên dưới; không cần đổi policy.

Linux/macOS:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

## Cài đặt và kiểm tra

```bash
python -m pip install -e ".[dev]"
python -m pytest -q
python -m ruff check .
python -m compileall -q src scripts
python scripts/check_environment.py
python app.py
```

Lệnh cuối chỉ in thông báo `Not implemented`, không chạy Streamlit.
Trong workspace Windows có dấu (`C:\Đồ án cuối kì NLP`), setuptools/Python
3.11 có thể lỗi encoding khi ghi `.pth` cho editable install. Cách đã kiểm tra:

```powershell
$env:PYTHONUTF8 = '1'
python -m pip install ".[dev]"
```

Cài thường cần chạy lại sau khi sửa source. Để phát triển editable, clone
vào đường dẫn không dấu rồi dùng lệnh `-e` ở trên.
`requirements.txt` tham chiếu package editable; `requirements-dev.txt`
tham chiếu extra dev, không sao chép dependency sang nhiều nơi.
Các dependency trực tiếp được khóa phiên bản trong `pyproject.toml`;
dependency bắc cầu chưa có lockfile.

## Colab/Kaggle

Mở `notebooks/colab_setup.ipynb` bằng Jupyter/Colab hoặc import vào Kaggle.
Chạy các cell để xem phiên bản Python, platform và `nvidia-smi` nếu có.
Notebook không tải dataset/model và không cài thư viện ML.
Runtime hosted có thể không dùng Python 3.11: kết quả notebook sẽ báo rõ;
không giả định môi trường đó tương thích package. GPU hiển thị qua driver
không chứng minh PyTorch/CUDA hoặc fine-tuning đã hoạt động.

## Roadmap

TASK 02: audit dữ liệu → TASK 03: BM25 → TASK 04: annotation/split →
TASK 05: BKAI pretrained → TASK 06: fine-tuning → TASK 07: evaluation →
TASK 08: demo → TASK 09: tái lập và nộp bài.
Chi tiết: [ROADMAP](docs/ROADMAP.md), [ARCHITECTURE](docs/ARCHITECTURE.md),
[EXPERIMENTS](docs/EXPERIMENTS.md). W01 không tự chuyển sang W02.

## W01 — audit toàn corpus hiện hành

Phạm vi duy nhất: `metadata/data`, `content/data`, `relationships/data` tại revision
đã khóa trong `configs/corpus.yaml`. Legacy không được đọc hay đưa vào báo cáo.
CLI mặc định `full`; không giới hạn record và bắt đầu từ row group 0.

Lệnh chạy từ root repository:

```powershell
.\.venv\Scripts\python.exe -X utf8 scripts/inspect_dataset.py
.\.venv\Scripts\python.exe -X utf8 scripts/audit_corpus.py --inspection results/w01/inspection.json --mode full --configs metadata content relationships --output results/w01_full
```

Inspection tự phát hiện config/split/file qua API/card tại SHA khóa và chỉ đọc footer
của ba config được chọn. Cache Hugging Face chỉ được dùng sau khi SHA-256 và kích
thước khớp pinned Hub LFS. File còn lại đọc HTTP Range, từ chối server bỏ qua Range.
Lần full này lưu bản relationships 9 MB đã xác minh checksum trong `data/raw/`
(bị ignore); metadata/content dùng cache đã xác minh. Không cần token hay GPU.

Reader đọc batch 64 dòng; SQLite tạm lưu ID, hash và độ dài để tính thống kê chính
xác mà không giữ toàn corpus trong RAM. Mỗi row group bị giới hạn 256 MiB compressed
và uncompressed, đồng thời kiểm tra lại footer thật trước decode. Định dạng nguồn
hiện tại có một file/split mỗi config; cấu trúc nhiều shards bị từ chối rõ ràng.

Output full tại `results/w01_full/`: `corpus_audit.json`, `corpus_audit_manifest.json`
và `CORPUS_AUDIT.md`; log tiến độ tại `results/logs/w01_full.log`. JSON runtime và raw
không commit. Báo cáo tổng hợp/manifest nhỏ được kiểm tra trước khi commit.
Báo cáo không trích HTML, title hoặc tên người ký; ví dụ record chỉ chứa kiểu,
độ dài, trường thiếu và hash ID. Markdown hiển thị top 12 mỗi metadata field;
JSON giữ đủ mọi tần suất đã đo.

`coverage=complete` chỉ khi số dòng đã đọc khớp footer, chế độ full và start group 0.
`audit_completed=true` chỉ khi mọi bảng được chọn đều đạt điều kiện đó, không có lỗi.
Join có scope `full_tables` khi hai bảng liên quan đã quét đầy đủ; khi đó số thiếu
counterpart là số đo chính xác trong snapshot, không phải suy ra từ mẫu.

Công cụ vẫn hỗ trợ `--mode sample --max-records 1000 --seed 42` cho kiểm thử nhỏ:
chọn một row group và các vị trí trong group theo seed, không đại diện theo năm/loại.
Bảng sample cũ đã được thay bằng báo cáo full hiện tại. `--max-records` và
`--start-group N` làm phạm vi partial; không tự gộp các lượt chạy lại. Full không
chạy trong CI, CI dùng fixtures giả nhỏ và không cần Internet.

Whitespace words không phải BKAI tokens. Text/HTML/encoding/structure flags chỉ là
kiểm định bằng heuristic, chưa chứng minh corpus sạch hoặc extractor đủ tốt.
Xem [CORPUS_AUDIT](docs/CORPUS_AUDIT.md), [DATA_CONTRACT](docs/DATA_CONTRACT.md)
và [W01_VERIFICATION](docs/W01_VERIFICATION.md). Chưa chuyển sang W02.

## Dữ liệu, checkpoint và secrets

Không commit corpus hoặc model weights; chỉ giữ `.gitkeep` trong các thư mục
dữ liệu/output bị ignore. `data/manifests/` cho provenance được review.
Ví dụ dữ liệu chỉ đưa vào thư mục tài liệu sau khi xác minh giấy phép và review;
không có ví dụ dữ liệu được tạo ở TASK 01. Không commit token/private key;
`.env.example` chỉ chứa giá trị rỗng. Luôn kiểm tra diff staged trước commit.
Chưa chọn giấy phép cho code nên chưa tạo LICENSE; trạng thái public không
tự cấp quyền sử dụng corpus hay code.

## Tái lập thí nghiệm sau khi module hoàn thiện

Khóa revision/hash corpus và model; lưu schema, split/annotation version,
config, seed, commit SHA, dependency versions, phần cứng, index metadata và
metrics thật cho mỗi run theo EXPERIMENTS. Đánh giá R1/R2/R3 trên cùng
query/relevance labels và split. Hiện chưa có lệnh chạy thí nghiệm.

## Git và CI

CI Ubuntu/Python 3.11 chạy install, lint, smoke tests và compileall;
không cần secrets/dataset/GPU. Sau commit local, người dùng tự push:

```bash
git push -u origin main
```

Sau push, đối chiếu SHA trên GitHub và kết quả Actions. TASK 01 chưa được
nghiệm thu toàn bộ cho đến khi push và kiểm chứng GitHub thành công.
