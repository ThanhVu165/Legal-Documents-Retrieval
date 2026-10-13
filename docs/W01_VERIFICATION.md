# W01 — Bằng chứng full audit

Audit UTC: 2026-10-13T02:50:33.598820+00:00; Python 3.11.9 trên Windows.
Phạm vi: chỉ metadata, content, relationships; không lấy legacy.

## Lệnh đã chạy và kết quả

| Kiểm tra | Kết quả |
| --- | --- |
| `python -m pytest -q` trong .venv | 45 passed, 0 failed |
| `python -m ruff check .` | All checks passed |
| `python -m compileall -q src scripts` | Exit 0 |
| Inspection tại SHA khóa | Exit 0; chỉ 3 footer đã chọn |
| Full audit không giới hạn record, start group 0 | Exit 0; audit_completed=true |

```powershell
.\.venv\Scripts\python.exe -X utf8 scripts/inspect_dataset.py
.\.venv\Scripts\python.exe -X utf8 scripts/audit_corpus.py --inspection results/w01/inspection.json --mode full --configs metadata content relationships --output results/w01_full
```

## Đối chiếu số dòng thực tế

| Bảng | Đã audit | Footer | Phạm vi |
| --- | ---: | ---: | --- |
| metadata | 171556 | 171556 | complete |
| relationships | 1033255 | 1033255 | complete |
| content | 170824 | 170824 | complete |

Tổng 1375635 dòng; bao gồm edges, không gọi tổng này là số document.
Mọi decoded_rows khớp scanned_records; không sử dụng max-records hay start-group khác 0.
Mọi join có scope full_tables. JSON chứa missing/duplicate/date/HTML/length/metadata và cấu trúc pháp luật.

## Artifact và checksum

`results/w01_full/corpus_audit.json` là số đo thật; `corpus_audit_manifest.json` chứa hash JSON/config/code và ba file nguồn.
`results/logs/w01_full.log` ghi tiến độ và kết thúc. SHA-256 của ba nguồn đã đối chiếu trước và sau full audit với pinned Hub LFS.
Hash JSON/config/code đều được đọc lại và đối chiếu thành công. Manifest ghi HEAD lúc chạy và working tree dirty vì audit trước delivery commit.
Báo cáo Markdown và manifest nhỏ đã thay thế bản sample. Toàn bộ output sample và full có giới hạn cũ đã xóa; chỉ giữ inspection mới của ba bảng.

## Review và giới hạn

Có review độc lập; không thấy lỗi triển khai quan trọng. Docstring tiếng Anh còn sót ở app.py đã được dịch.
AST/tokenizer đã kiểm tra comment/docstring tiếng Việt trong source, scripts, tests và app.py; noqa là chỉ thị lint được giữ nguyên.
Góp ý nhỏ để sau: bổ sung test CLI kết hợp giới hạn/restart để assert audit_completed=false và scope partial; các nhánh hiện tại được review và reader đã có test limit/start-group.
Không quét legacy, không chạy tokenizer/GPU/model hay W02. HTML/encoding/structure là heuristic, near-duplicate và chất lượng nhãn chưa đo.
Quyền dữ liệu nguồn còn chưa xác minh; CC BY 4.0 là publisher claim, truy cập portal nguồn trả 403. Full audit không phải nghiệm thu corpus sạch.
GitHub Actions của delivery commit chưa chạy vì không push; định nghĩa CI dùng tests offline, không full audit.

Trạng thái: **full audit kỹ thuật của ba bảng hiện hành đã được xác minh**; quyền nguồn và nghiệm thu preprocessing/retrieval vẫn pending.
