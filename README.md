# Hệ thống tìm kiếm văn bản pháp luật tiếng Việt theo ngữ nghĩa

Đồ án NLP xây dựng tìm kiếm văn bản pháp luật tiếng Việt, so sánh BM25,
BKAI pretrained và BKAI fine-tuned.

## Phạm vi và trạng thái

W01 đã bổ sung inspection và audit dữ liệu nguồn ở chế độ sample, với báo cáo
thật và tests offline. Chất lượng `legacy_content` chưa đo được vì file có một
row group quá lớn; quyền dữ liệu nguồn chưa xác minh. Chưa xây index, huấn luyện
hoặc tạo dữ liệu processed. Xem [CORPUS_AUDIT](docs/CORPUS_AUDIT.md).

| Module | Trạng thái |
| --- | --- |
| Packaging, config, smoke tests, CI definition | Scaffold; chạy theo hướng dẫn dưới đây |
| Dataset inspection/audit W01 | Implemented; sample audit partial, see evidence |
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

## W01 — inspection và audit

Chạy từ root repository, với Python của môi trường đã cài package:

```powershell
.\.venv\Scripts\python.exe -X utf8 scripts/inspect_dataset.py
.\.venv\Scripts\python.exe -X utf8 scripts/audit_corpus.py --inspection results/w01/inspection.json --mode sample --max-records 1000 --seed 42
```

Hai lệnh trên đã chạy thật. Inspection truy cập API/card tại SHA khóa, tự phát
hiện config/split/file và đọc footer Parquet. Cache chuẩn Hugging Face, nếu có,
chỉ dùng sau đối chiếu SHA-256 và kích thước với pinned Hub LFS. File còn lại
đọc HTTP Range, không tải dump. Không cần token hoặc GPU.

Sample chọn đều một row group mỗi file bằng seed, rồi chọn đều tối đa 1000 vị trí
trong group đó, giữ thứ tự đọc. Đây là cluster sample, không đại diện theo loại/năm;
không phải 1000 record đầu. `decoded_rows` là số hàng batch đã decode, khác với
`scanned_records` là số record được tính thống kê. Seed cố định chỉ tái lập khi
revision, file, PyArrow/Python và layout row group không đổi.

Giới hạn 256 MiB compressed và uncompressed mỗi row group áp dụng cả sample/full để tránh PyArrow
nạp column chunk khổng lồ; sample remote có thêm ngân sách HTTP 256 MiB/file.
`legacy_content` có một group khoảng 3,5 GB nên quality statistics là null,
exit code sample toàn bộ = 1 (partial_failure). Schema và footer rows vẫn được giữ.
Không dùng preview có revision chưa xác minh hoặc nội dung truncated thay dữ liệu gốc.
API preview legacy đã trả 500/501 trong lần kiểm tra này.

Output tại `results/w01/`: inspection.json, corpus_audit.json,
corpus_audit_manifest.json và CORPUS_AUDIT.md. `results/` bị ignore;
chỉ báo cáo tổng hợp và manifest nhỏ được review để commit.
Report không chứa raw HTML, title/signer excerpts; sample profiles chỉ chứa kiểu,
độ dài, null fields và hash ID. JSON đầy đủ metadata frequencies; Markdown hiển thị top 12.

Full có giới hạn đã kiểm tra thật trên 20 rows metadata + 20 rows content:

```powershell
.\.venv\Scripts\python.exe -X utf8 scripts/audit_corpus.py --inspection results/w01/inspection.json --mode full --configs metadata content --max-records 20 --output results/w01_full_bounded
```

Lệnh full không giới hạn bên dưới **chưa chạy**; đọc toàn bộ current tables theo
batch 64 và SQLite tạm cho IDs/hashes/quantiles. Không chạy trong CI:

```powershell
.\.venv\Scripts\python.exe -X utf8 scripts/audit_corpus.py --mode full --configs metadata content relationships --output results/w01_full
```

`--max-records` giới hạn mỗi file; `--configs` phải là config đã phát hiện.
Nguồn hiện tại có một file/split mỗi config. Nếu nguồn chuyển sang nhiều file/split
trong cùng config, CLI từ chối rõ ràng để tránh thiếu IDs/join/totals; chưa hỗ trợ gộp shards.
`--start-group N` chỉ áp dụng full: bắt đầu lại từ group N, lưu output mới và coi
đó là partial scan. Không tự merge các lần restart; muốn exact full totals phải
chạy từ group 0 đến cuối, không giới hạn. Legacy content cần được re-shard từ
nguồn trước full audit bằng reader này; W01 không sửa file nguồn để làm việc đó.

Join chỉ thuộc records được audit; independently sampled tables có nhiều IDs
không giao nhau không chứng minh orphan. Whitespace words không phải BKAI tokens.
HTML visible-text/encoding/structure flags là diagnostics, chưa chứng minh extractor
đủ tốt. [DATA_CONTRACT](docs/DATA_CONTRACT.md) phân biệt source fields và schema W02 đề xuất.

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
