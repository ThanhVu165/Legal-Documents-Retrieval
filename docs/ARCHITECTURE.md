# Kiến trúc dự kiến

Luồng: Data → BM25/BKAI → Ranking → Evaluation → Streamlit.
Tất cả module nghiệp vụ dưới đây **Not implemented**.

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

`configs/` là đề xuất, chưa có loader nghiệp vụ. Không tạo API hoặc logic giả.
Raw → interim → processed phải giữ liên kết nguồn, ID/hash/revision;
schema và quyết định chunking chờ TASK 02. BM25 score và cosine similarity
khác thang đo; chưa triển khai fusion. Đánh giá ở cấp document sau aggregation.
Artifacts lưu local, manifests có thể commit sau review.
