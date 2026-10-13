# Kiến trúc dự kiến

Luồng: Data → BM25/BKAI → Ranking → Evaluation → Streamlit.
Các module retrieval/preprocessing dưới đây **Not implemented**.
W01 đã triển khai data/schema.py (config và ID), data/inspection.py (nguồn và footer),
data/audit.py (diagnostics offline và SQLite tạm), cùng hai CLI inspection/audit.
Không tạo processed text; diagnostics text chỉ tồn tại trong bộ nhớ từng record.

| Vị trí | Trách nhiệm dự kiến |
| --- | --- |
| data/cleaning.py | Chuẩn hóa có traceability, bảo toàn raw |
| data/segmentation.py | Phân đoạn tiếng Việt theo quyết định sau audit |
| data/chunking.py | Chunk theo cấu trúc và token budget; giữ document ID |
| retrieval/bm25.py | Lexical baseline, điểm BM25 |
| retrieval/dense.py | BKAI embeddings và cosine similarity |
| retrieval/search_service.py | Retrieval/ranking và aggregation cấp document |
| models/train_bkai.py | Fine-tuning sau annotation/split |
| evaluation/metrics.py | Precision/Recall@k, MRR, MAP, NDCG@k |
| evaluation/error_analysis.py | Phân tích query lỗi và nhóm văn bản |
| app/highlighting.py | Highlight bằng chứng trong kết quả |
| app/feedback.py | Thu feedback có nguồn và version |
| utils/ | Chỉ thêm tiện ích khi có nhu cầu thực tế |

Corpus config có loader kiểm tra dataset ID/revision. Retrieval/training vẫn là đề xuất.
Raw → interim → processed phải giữ liên kết nguồn, ID/hash/revision;
Schema nguồn xem DATA_CONTRACT; quyết định extraction/chunking chờ W02. BM25 score và cosine similarity
khác thang đo; chưa triển khai fusion. Đánh giá ở cấp document sau aggregation.
Artifacts lưu local, manifests có thể commit sau review.
