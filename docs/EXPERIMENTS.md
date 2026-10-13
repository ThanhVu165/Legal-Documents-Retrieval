# Quy ước thí nghiệm

Chưa chạy thí nghiệm; không có metrics hoặc kết quả mẫu.

- R1 = BM25.
- R2 = BKAI pretrained.
- R3 = BKAI fine-tuned.

Đánh giá chung trên cùng corpus/split/query/relevance labels, ranking cấp
document. Cutoffs dự kiến 5, 10, 20. Precision@k = số document relevant ở
top-k chia k; Recall@k chia tổng relevant đã annotate. MRR dùng reciprocal
rank relevant đầu tiên; MAP dùng trung bình AP; NDCG@k dùng graded relevance
và logarithmic discount. Trước TASK 07 phải khóa quy tắc unjudged documents,
query không có relevance, ties, label scale và cutoff của AP/MRR.

Mỗi run cần lưu: run ID/time, Git SHA, corpus/model revision/hash/license,
annotation/split version, config/hyperparameters/seed, dependency versions,
hardware/driver/CUDA thực đo, preprocessing/chunking/index/aggregation,
metrics theo query và tổng hợp, error analysis, checkpoint/log paths.

Latency cần ghi đơn vị, warmup, số query, batch size, p50/p95 và ranh giới
đo (encoding/retrieval/aggregation); index size ghi byte và file nào được tính.
Không so sánh latency hoặc index size nếu phạm vi đo khác nhau.
