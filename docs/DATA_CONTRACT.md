# W01 → W02 Data Contract

Trạng thái: giao diện **đề xuất**, chưa tạo corpus processed và chưa nghiệm thu selection/cleaning/chunking.
Snapshot nguồn đã xác minh: `th1nhng0/vietnamese-legal-documents` tại
`8977887f17be2defae4c5171d55562e1cde7d695`. Xem [CORPUS_AUDIT](CORPUS_AUDIT.md).

## Trường nguồn đã xác minh bằng footer Parquet và dữ liệu mẫu

| Bảng/config + split | Cấp record | ID | Nội dung / metadata |
| --- | --- | --- | --- |
| metadata/data | document | id: string | title, so_ky_hieu, ngay_ban_hanh, loai_van_ban, ngay_co_hieu_luc, ngay_het_hieu_luc, nguon_thu_thap, ngay_dang_cong_bao, nganh, linh_vuc, co_quan_ban_hanh, chuc_danh, nguoi_ky, pham_vi, thong_tin_ap_dung, tinh_trang_hieu_luc: string |
| content/data | document | id: string | content_html: string, HTML gốc |
| relationships/data | directed edge | doc_id, other_doc_id: string | relationship: string; doc_id có thể lặp hợp lệ |
| legacy_metadata/metadata | document | id: int64 | document_number, title, legal_type, legal_sectors, issuing_authority, issuance_date, effect_date, effectless_date, effect_status, signers: large_string |
| legacy_content/content | document | id: int64 | content: large_string, plain text theo card; schema đã đo, giá trị chưa audit được do một row group quá lớn |

Metadata/content hiện hành join bằng `id`. Quan hệ join `doc_id` hoặc `other_doc_id`
với metadata.id. Legacy metadata/content dùng integer ID riêng; chuyển số nguyên sang
chuỗi an toàn để **khảo sát** overlap không chứng minh hai record đồng nhất.
Không dùng `doc_id` làm khóa duy nhất của edge. Mẫu W01 không xác nhận cardinality toàn corpus.

## Giao diện document đề xuất sau W02

Các tên dưới đây là **trường derived đề xuất**, không tuyên bố đã có trong nguồn.

| Trường derived | Quy tắc |
| --- | --- |
| document_id | Khóa có namespace dataset/revision/config/source_id; không dùng số thứ tự dòng |
| source_id | Bảo toàn cả giá trị và kiểu ID gốc; không strip, cast float, bỏ số 0 đầu |
| title | Từ metadata.title; null giữ nguyên, không dùng body để bịa tên |
| document_type | metadata.loai_van_ban; legacy legal_type chỉ map sau review |
| raw_html / raw_text | Bản gốc content_html / legacy content; không ghi đè |
| text | Bản derived riêng sau cleaning đã được review; W01 chưa xuất |
| metadata | Giữ nguyên field/value, kể cả null, 0, Không, Chưa phân loại |
| source_reference | dataset ID, revision, config, split, file, ID gốc, checksum nguồn nếu đã đo |
| source_url | null cho đến khi xác minh URL chi tiết đúng record; không bịa URL vbpl từ ID |
| review_status / quality_flags | ID/content/join/date/encoding/HTML/duplicate flags và lý do |
| content_group | Nhóm duplicate sau review để ngăn leakage; chưa có ở W01 |

## Missing, loại bản ghi và dẫn nguồn

- Null/blank vẫn giữ traceability. Trường không có trong schema không được điền giá trị giả.
- Không có content counterpart trong hai mẫu độc lập không đủ để loại metadata.
- Thiếu/unsafe ID: đưa vào review/quarantine, không tự sinh source ID mới.
- Null/blank/invisible/image-only/title-only content: review trước inclusion; không loại bằng ngưỡng độ dài đơn lẻ.
- Duplicate ID/content: bảo toàn bản gốc và nhóm liên quan; không merge/drop trước quyết định của nhóm.
- Ngày không parse được hoặc tương lai được flag; không sửa ngày. Tình trạng hiệu lực chỉ là snapshot claim.
- Nguồn ký tên không cần hiển thị trong demo nếu không phục vụ mục đích tìm kiếm.
- Demo citation giữ title, số ký hiệu, source ID, snapshot và reference đã xác minh;
  không thể hiện trạng thái hiệu lực như xác nhận pháp lý hiện tại.
- License CC BY 4.0 là publisher claim; quyền đối với nguồn chưa xác minh, không đưa dump public mặc định.

## Giao diện chunk đề xuất, chưa triển khai

`chunk_id`, `document_id`, source ID/revision, đường dẫn cấu trúc Chương/Điều/khoản,
vị trí trong raw và derived text, extraction version và checksum. Chunk phải ánh xạ
về văn bản gốc và nguồn cụ thể. Không khóa max_tokens/overlap trước đo tokenizer.
Giữ bảng/caption/cell context khi thử extractor. Kiểm tra duplicate/near-duplicate,
query/relevance labels và split theo nhóm trước đánh giá/fine-tuning.

## Điều kiện bàn giao

W02 chỉ bắt đầu sau khi nhóm chọn corpus/subset và review các gate về nguồn,
trường thiếu, extraction, inclusion và mapping. W01 không lựa chọn domain,
không tạo labels/splits, không đánh dấu cleaning/chunking hoàn thành.
