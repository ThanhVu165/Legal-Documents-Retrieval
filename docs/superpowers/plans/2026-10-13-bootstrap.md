# TASK 01 implementation plan

**Goal:** Khởi tạo package Python 3.11 và scaffold theo brief TASK 01.
**Architecture:** src/legal_retrieval; module nghiệp vụ chỉ có docstring. PyYAML để đọc config; pytest và ruff cho development. Không cài thư viện ML.
**Scope:** configs, package, smoke tests, environment checker, notebook, README, docs, ignore rules và CI. Workspace chưa có Git, chỉ có venv; không thay đổi venv hiện có.

1. Viết smoke tests cho import, metadata, config và environment checker; xác nhận thất bại khi scaffold chưa có.
2. Tạo package/config/scaffold, entrypoint thông báo Not implemented, notebook kiểm tra môi trường.
3. Tạo tài liệu và CI dùng chung lệnh cài đặt/test/lint.
4. Cài bằng Python 3.11 trong .venv mới; chạy tests, lint, compileall, notebook/schema và kiểm tra ignore.
5. Khởi tạo main, thêm đúng origin, kiểm tra các file staged; commit chore: set up github.
6. Báo người dùng tự push theo mục 9 của brief; GitHub verification/CI pending cho đến khi push.

Không tạo LICENSE khi chưa có quyết định giấy phép. Không tải corpus/model hoặc thực hiện TASK 02.
