# W01 — Kiểm định corpus pháp luật tiếng Việt

## 1. Tổng quan dataset

Dataset: `th1nhng0/vietnamese-legal-documents`; revision: `8977887f17be2defae4c5171d55562e1cde7d695`.
Audit UTC: 2026-10-13T02:50:33.598820+00:00; mode: **full**.

Phạm vi: metadata, content và relationships hiện hành; không lấy legacy.
Đã quét đầy đủ các bảng được chọn.

## 2. Nguồn dữ liệu và giấy phép

```json
{
  "claimed_license": "cc-by-4.0",
  "license_status": "claimed_source_rights_unresolved",
  "source_urls_from_card": [
    "https://vbpl.vn"
  ],
  "source_rights": "unverified",
  "card_url": "https://huggingface.co/datasets/th1nhng0/vietnamese-legal-documents/blob/8977887f17be2defae4c5171d55562e1cde7d695/README.md",
  "card_sha256": "32343afdde47451cf9f0a9b8a26892efc0a45f8f77e0b5027b7cdd781423d6c4",
  "method": "pinned Hub API/card, actual Parquet footer and checksum-verified cache",
  "source_portal_access": {
    "status": "unverified",
    "error": "HTTP Error 403: Forbidden"
  }
}
```

## 3. Kiểm tra schema

- `metadata/data` (document): `id: string`, `title: string`, `so_ky_hieu: string`, `ngay_ban_hanh: string`, `loai_van_ban: string`, `ngay_co_hieu_luc: string`, `ngay_het_hieu_luc: string`, `nguon_thu_thap: string`, `ngay_dang_cong_bao: string`, `nganh: string`, `linh_vuc: string`, `co_quan_ban_hanh: string`, `chuc_danh: string`, `nguoi_ky: string`, `pham_vi: string`, `thong_tin_ap_dung: string`, `tinh_trang_hieu_luc: string`
- `relationships/data` (relationship): `doc_id: string`, `other_doc_id: string`, `relationship: string`
- `content/data` (document): `id: string`, `content_html: string`

## 4. Số lượng dữ liệu

| Config/split | Footer rows | Audited rows | Coverage | Row group |
| --- | ---: | ---: | --- | ---: |
| metadata/data | 171556 | 171556 | complete | None |
| relationships/data | 1033255 | 1033255 | complete | None |
| content/data | 170824 | 170824 | complete | None |

## 5. Quan hệ giữa metadata, content và relationships

Join trên toàn bộ ID an toàn của các bảng đã quét đầy đủ; mismatch là số đo chính xác của snapshot.

```json
{
  "metadata->content": {
    "scope": "full_tables",
    "shared_distinct_ids": 170824,
    "metadata_only_distinct_ids": 732,
    "content_only_distinct_ids": 0,
    "observed_cardinality": "one_to_one"
  },
  "metadata->relationships": {
    "scope": "full_tables",
    "shared_distinct_ids": 145945,
    "metadata_only_distinct_ids": 25611,
    "content_only_distinct_ids": 0,
    "observed_cardinality": "one_to_many"
  },
  "metadata->relationship_targets": {
    "scope": "full_tables",
    "shared_distinct_ids": 101519,
    "metadata_only_distinct_ids": 70037,
    "content_only_distinct_ids": 17706,
    "observed_cardinality": "one_to_many"
  }
}
```

## 6. Phân tích trường thiếu và trùng lặp

| Config | ID null/blank | Unsafe ID | Duplicate key extra rows | Missing fields (count / audited) |
| --- | ---: | ---: | ---: | --- |
| metadata | 0 | 0 | 0 | title: 10/171556 (0.0%); so_ky_hieu: 11/171556 (0.0%); ngay_ban_hanh: 97/171556 (0.1%); ngay_co_hieu_luc: 4929/171556 (2.9%); ngay_het_hieu_luc: 91238/171556 (53.2%); nguon_thu_thap: 86944/171556 (50.7%); ngay_dang_cong_bao: 126248/171556 (73.6%); nganh: 64175/171556 (37.4%); linh_vuc: 4785/171556 (2.8%); co_quan_ban_hanh: 750/171556 (0.4%); chuc_danh: 5436/171556 (3.2%); nguoi_ky: 1886/171556 (1.1%); pham_vi: 51/171556 (0.0%); thong_tin_ap_dung: 171556/171556 (100.0%) |
| relationships | 0 | 0 | 887310 | 0 observed |
| content | 0 | 0 | 0 | 0 observed |

Relationships ở cấp edge: lặp doc_id là degree, không phải duplicate document/edge.

## 7. Chất lượng text và HTML

Diagnostic text bỏ head/script/style chỉ để đo; không lưu processed text. HTML parser khoan dung không xác nhận HTML hợp lệ.
| Config | Null | Blank source | Empty visible | Non-NFC | Same text/different IDs groups | HTML flags |
| ---    | ---: | ---:  | ---: | ---: | ---: | ---: |
| content | 0 | 0 | 12229 | 0 | 128 | 0 |

Phân bố ngày tháng và metadata (chỉ tổng hợp, không trích nội dung/tên người ký):

```json
{
  "metadata": {
    "dates": {
      "ngay_ban_hanh": {
        "invalid": 0,
        "future": 1,
        "years": {
          "1997": 2473,
          "2014": 6174,
          "2024": 7568,
          "2012": 5161,
          "2003": 4537,
          "1994": 1064,
          "2017": 5778,
          "2016": 6446,
          "2006": 7113,
          "2021": 5382,
          "2020": 4798,
          "1980": 245,
          "2022": 5478,
          "2018": 5120,
          "2008": 5818,
          "2007": 7167,
          "1991": 687,
          "2025": 10495,
          "1999": 3200,
          "2011": 4987,
          "2004": 5380,
          "2023": 5473,
          "2013": 5426,
          "1998": 2887,
          "1983": 295,
          "2019": 5154,
          "2010": 4700,
          "2000": 2999,
          "1986": 385,
          "2005": 5833,
          "2026": 4601,
          "2009": 5194,
          "2015": 5593,
          "2002": 3742,
          "1995": 1545,
          "1993": 811,
          "1992": 815,
          "2001": 3503,
          "1952": 34,
          "1953": 34,
          "1957": 106,
          "1960": 56,
          "1990": 533,
          "1978": 157,
          "1969": 16,
          "1989": 519,
          "1988": 410,
          "1985": 388,
          "1945": 88,
          "1987": 409,
          "1948": 128,
          "1946": 244,
          "1956": 70,
          "1996": 1567,
          "1964": 56,
          "1958": 75,
          "1963": 52,
          "1979": 138,
          "1982": 358,
          "1961": 59,
          "1950": 139,
          "1984": 329,
          "1959": 94,
          "1949": 120,
          "1977": 227,
          "1981": 349,
          "1951": 52,
          "1976": 86,
          "1965": 21,
          "1955": 29,
          "1967": 8,
          "1968": 22,
          "1962": 63,
          "1971": 34,
          "1947": 109,
          "1975": 94,
          "1966": 29,
          "1970": 28,
          "1972": 35,
          "1974": 40,
          "1973": 19,
          "1954": 6,
          "1925": 1,
          "3024": 1
        }
      },
      "ngay_co_hieu_luc": {
        "invalid": 0,
        "future": 27,
        "years": {
          "1997": 2326,
          "2014": 5899,
          "2024": 7104,
          "2012": 5019,
          "2003": 4156,
          "1994": 1003,
          "2013": 5268,
          "2017": 6252,
          "2016": 5828,
          "2006": 6726,
          "2021": 5382,
          "2020": 4801,
          "1980": 239,
          "2023": 5353,
          "2018": 5108,
          "2008": 5556,
          "2007": 7215,
          "1991": 610,
          "2025": 9752,
          "1999": 3110,
          "2022": 5605,
          "2011": 4881,
          "2005": 5434,
          "2004": 4888,
          "1983": 297,
          "2019": 4963,
          "2010": 4551,
          "2000": 2821,
          "1986": 382,
          "2026": 5667,
          "2009": 5174,
          "2002": 3437,
          "1995": 1481,
          "2015": 5607,
          "1993": 787,
          "1992": 783,
          "1998": 2729,
          "2001": 3234,
          "1952": 32,
          "1953": 30,
          "1957": 103,
          "1960": 63,
          "1990": 507,
          "1978": 153,
          "1989": 508,
          "1988": 394,
          "1945": 80,
          "1985": 396,
          "1987": 394,
          "1948": 125,
          "1946": 246,
          "1996": 1498,
          "1964": 43,
          "1958": 73,
          "1963": 50,
          "1979": 138,
          "1982": 350,
          "1961": 57,
          "1950": 144,
          "1984": 305,
          "1959": 81,
          "1949": 109,
          "1977": 226,
          "1981": 315,
          "1951": 54,
          "1976": 99,
          "1965": 25,
          "1955": 30,
          "1967": 8,
          "1968": 20,
          "1962": 64,
          "1975": 86,
          "1971": 33,
          "1947": 113,
          "1956": 56,
          "2027": 17,
          "1969": 12,
          "1966": 28,
          "1970": 28,
          "1973": 20,
          "1972": 35,
          "1974": 37,
          "1954": 4,
          "1944": 1,
          "1913": 1,
          "2984": 1,
          "1920": 1,
          "3018": 1,
          "1916": 1,
          "1925": 1,
          "2949": 1,
          "4998": 1,
          "3024": 1
        }
      },
      "ngay_het_hieu_luc": {
        "invalid": 0,
        "future": 323,
        "years": {
          "2017": 4021,
          "2010": 1978,
          "2026": 6682,
          "2021": 3810,
          "2016": 3344,
          "2020": 2956,
          "2024": 5429,
          "2015": 3202,
          "1999": 914,
          "2018": 2850,
          "2006": 1326,
          "1998": 1061,
          "2019": 3055,
          "2025": 12731,
          "2022": 3270,
          "2000": 482,
          "2023": 3282,
          "2004": 619,
          "2012": 1776,
          "2003": 728,
          "1960": 363,
          "1953": 2,
          "2013": 2331,
          "2009": 2612,
          "2005": 1118,
          "2007": 1585,
          "2014": 3238,
          "2008": 1559,
          "2002": 444,
          "2011": 1776,
          "2030": 101,
          "2031": 15,
          "1980": 63,
          "1997": 108,
          "1975": 239,
          "1993": 59,
          "1994": 46,
          "2001": 495,
          "2027": 117,
          "2028": 15,
          "1989": 19,
          "1992": 126,
          "1995": 54,
          "1996": 94,
          "1984": 10,
          "1952": 10,
          "2121": 1,
          "1990": 12,
          "1985": 13,
          "1988": 8,
          "1972": 1,
          "1991": 40,
          "1949": 24,
          "1958": 6,
          "1987": 7,
          "1946": 12,
          "1986": 9,
          "2032": 1,
          "1955": 2,
          "1983": 5,
          "1957": 2,
          "1981": 14,
          "1979": 2,
          "1961": 1,
          "1945": 2,
          "1913": 1,
          "1948": 6,
          "1982": 6,
          "1976": 3,
          "1947": 2,
          "1950": 5,
          "1977": 2,
          "2202": 1,
          "1965": 1,
          "2029": 4,
          "1959": 1,
          "3023": 1,
          "1978": 1,
          "2949": 1,
          "1964": 2,
          "3000": 2,
          "1956": 1,
          "1962": 1
        }
      },
      "ngay_dang_cong_bao": {
        "invalid": 0,
        "future": 535,
        "years": {
          "2013": 2770,
          "2014": 3096,
          "1980": 5,
          "2007": 2995,
          "2003": 1135,
          "2011": 2648,
          "2023": 626,
          "2004": 1140,
          "2022": 615,
          "2017": 1199,
          "1986": 191,
          "2009": 2769,
          "2006": 2580,
          "2024": 672,
          "2015": 2538,
          "2012": 2809,
          "1997": 245,
          "2001": 543,
          "2008": 2563,
          "1960": 29,
          "2026": 616,
          "2016": 1403,
          "1992": 167,
          "2018": 1014,
          "2005": 1772,
          "1999": 495,
          "1985": 204,
          "2010": 2386,
          "1998": 338,
          "2002": 578,
          "2019": 825,
          "2025": 439,
          "2020": 657,
          "2000": 276,
          "9999": 528,
          "2021": 687,
          "1958": 16,
          "1946": 88,
          "1990": 28,
          "1984": 181,
          "1982": 140,
          "1995": 156,
          "1994": 91,
          "1993": 67,
          "1988": 62,
          "1961": 19,
          "1987": 173,
          "1989": 102,
          "1967": 1,
          "1983": 31,
          "1981": 183,
          "1991": 33,
          "1962": 13,
          "1957": 25,
          "1978": 12,
          "2027": 5,
          "1959": 38,
          "1996": 119,
          "1970": 9,
          "1975": 47,
          "1977": 5,
          "1974": 8,
          "1964": 9,
          "1966": 5,
          "1956": 16,
          "2028": 1,
          "1945": 17,
          "1971": 4,
          "1968": 5,
          "1972": 6,
          "1973": 3,
          "1963": 15,
          "1976": 6,
          "1979": 11,
          "1965": 1,
          "1969": 1,
          "1925": 1,
          "2101": 1,
          "1954": 1
        }
      }
    },
    "metadata": {
      "loai_van_ban": {
        "Quyết định": 91183,
        "Nghị quyết": 28337,
        "Thông tư": 17232,
        "Bản dịch văn bản": 10952,
        "Chỉ thị": 8543,
        "Nghị định": 5328,
        "Thông tư liên tịch": 3519,
        "Văn bản hợp nhất": 2232,
        "Sắc lệnh": 981,
        "Văn bản hệ thống hóa": 762,
        "Công văn": 732,
        "Luật": 610
      },
      "nguon_thu_thap": {
        "Bản chính": 4164,
        "Công báo điện tử;": 3435,
        "Bản chính văn bản": 3333,
        "Công báo Thành phố Hồ Chí Minh": 2243,
        "bản chính": 1679,
        "Văn bản gốc": 1582,
        "Công báo": 1474,
        "Công báo điện tử Thành phố Hồ Chí Minh": 1226,
        "bản chính văn bản": 1187,
        "Bản gốc văn bản": 990,
        "văn bản gốc": 948,
        "công báo": 909
      },
      "nganh": {
        "Tài chính": 19686,
        "Nội vụ": 10619,
        "Lao động - Thương binh và Xã hội": 9881,
        "Tài nguyên và Môi trường": 6673,
        "Nông nghiệp và phát triển nông thôn": 6410,
        "Xây dựng": 5168,
        "Tư pháp": 4025,
        "Công Thương": 3907,
        "Giáo dục và đào tạo": 3872,
        "Giao thông Vận tải": 3472,
        "Y tế": 3387,
        "Kế hoạch và Đầu tư": 3244
      },
      "linh_vuc": {
        "Chưa phân loại": 113772,
        "Đất đai": 2916,
        "Quản lý thuế, phí, lệ phí và thu khác của ngân sách nhà nước": 2390,
        "Quản lý thuế, phí và lệ phí": 1742,
        "Lĩnh vực giá": 1656,
        "Lao động, tiền lương, tiền công": 1479,
        "Tổ chức- Biên chế": 1302,
        "Ngân sách nhà nước": 1289,
        "Quản lý ngân sách": 1228,
        "Quản lý ngân sách nhà nước": 1085,
        "Chính quyền địa phương": 880,
        "Đường bộ": 874
      },
      "co_quan_ban_hanh": {
        "Bộ Tài chính": 10778,
        "Thủ tướng Chính phủ": 7893,
        "Chính phủ": 7421,
        "UBND Thành phố Hồ Chí Minh": 5534,
        "UBND Tỉnh Lào Cai": 2542,
        "UBND Tỉnh Nghệ An": 2503,
        "Bộ Nông nghiệp và Phát triển nông thôn": 2450,
        "UBND tỉnh Bình Phước": 2422,
        "UBND Thành phố Hà Nội": 2345,
        "Ngân hàng Nhà nước Việt Nam": 2314,
        "UBND Thành phố Hải Phòng": 2258,
        "UBND thành phố Đà Nẵng": 2153
      },
      "pham_vi": {
        "Địa phương": 114360,
        "Trung ương": 56730,
        "TỈNH BÌNH PHƯỚC": 122,
        "Toàn quốc": 106,
        "Tỉnh Hà Giang": 40,
        "Tỉnh Đồng Nai": 21,
        "Tỉnh Quảng Ninh": 12,
        "Tỉnh Tuyên Quang": 10,
        "Tỉnh Thừa Thiên Huế": 9,
        "Huyện Yên Minh": 8,
        "Tỉnh Cao Bằng": 6,
        "Tuyên Quang": 6
      },
      "tinh_trang_hieu_luc": {
        "Hết hiệu lực toàn bộ": 90721,
        "Còn hiệu lực": 71619,
        "Hết hiệu lực một phần": 5235,
        "Chưa xác định": 3205,
        "Ngưng hiệu lực": 373,
        "Không còn phù hợp": 255,
        "Chưa có hiệu lực": 146,
        "Ngưng hiệu lực một phần": 2
      }
    }
  },
  "relationships": {
    "dates": {},
    "metadata": {
      "relationship": {
        "Căn cứ": 668173,
        "Dẫn chiếu": 72554,
        "Văn bản quy định hết hiệu lực": 50939,
        "Quy định chi tiết, hướng dẫn thi hành": 39419,
        "Thay thế": 37146,
        "Văn bản HD, QĐ chi tiết": 34392,
        "Bãi bỏ": 32479,
        "Văn bản căn cứ": 26515,
        "Sửa đổi, bổ sung": 17674,
        "Văn bản bổ sung": 12853,
        "Văn bản hết hiệu lực": 12247,
        "Văn bản sửa đổi": 7466
      }
    }
  }
}
```

## 8. Phân bố độ dài


| Config | Metric | n | min | median | mean | p90 | p95 | p99 | max |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| content | characters | 170824 | 5 | 5026.0 | 12892.57 | 27639.7 | 42272.55 | 114467.41 | 6272990 |
| content | whitespace_words | 170824 | 0 | 990.0 | 2414.96 | 5506.0 | 8283.0 | 20479.77 | 880350 |
| content | source_characters | 170824 | 58 | 9832.0 | 29638.3 | 48747.1 | 82869.25 | 333944.08 | 15436746 |


## 9. Cấu trúc văn bản pháp luật

Regex heuristic: số record có dấu hiệu, không phải số điều/khoản chính xác.

```json
{
  "content": {
    "chuong": 31366,
    "muc": 11287,
    "dieu": 133772,
    "khoan": 116399,
    "diem": 88977,
    "phu_luc": 26691,
    "legal_reference": 66930,
    "tables": 75077
  }
}
```

## 10. Đề xuất chọn corpus tìm kiếm

Số đo full để quyết định W02: 732 metadata thiếu content; 12,229/170,824 content không có text hiển thị (7.16%); 128 nhóm text diagnostic giống nhau nhưng khác ID. Median 5,026, p99 114,467.41 và max 6,272,990 ký tự cho thấy cần kiểm tra cấu trúc và tokenizer trước khi chốt chunk, không dùng toàn văn dài làm một input mặc định.

Metadata có 10 title thiếu, 11 số ký hiệu thiếu; trường thông tin áp dụng thiếu 100%. Lĩnh vực có 113,772 giá trị Chưa phân loại và 4,785 null/blank; lọc domain chỉ dựa trường này có thể làm mất tài liệu liên quan. Không tự chọn domain hay loại các record đó.

Graph có 17,706 target ID ngoài metadata snapshot. Trong khóa metadata->relationship_targets, content_only_distinct_ids chỉ target không có metadata, không phải content mồ côi. Doc_id lặp là degree hợp lệ; số edge trùng chính xác là 0.

Các nhóm trùng chỉ so sánh text diagnostic không rỗng sau parser; chưa đo near-duplicate hoặc chứng minh toàn văn tương đương pháp lý. HTML flags bằng 0 không xác nhận HTML hợp lệ: parser khoan dung và chỉ flag một số bất thường của head/script/style/table.

Có thể nghiên cứu retrieval với metadata + content hiện hành; chưa đủ bằng chứng chất lượng để chốt corpus.
Đề xuất W02: index chunk theo Điều/khoản khi cấu trúc đủ rõ, fallback theo đoạn; trả kết quả và đánh giá ở cấp document.
Chunk giữ source ID, revision, config/split/file, vị trí gốc và document ID; chưa chốt token budget.

| Phương án | Lợi ích | Hạn chế / ảnh hưởng retrieval | Quyết định |
| --- | --- | --- | --- |
| Metadata + content hiện hành | Có HTML và metadata phục vụ filter | Nội dung rỗng/thiếu và trùng lặp cần review | Phạm vi đã chọn, chưa loại record |
| Stratify theo loại + năm | Tránh bias của prefix; metadata hỗ trợ filter | Ngày thiếu/sai và lệch lớp cần strata riêng | Đề xuất sau kiểm tra coverage |
| Filter lĩnh vực | Gọn và có mục đích | Giá trị missing/Chưa phân loại không chứng minh ngoài domain | Nhóm chọn domain sau review |

Filter dùng loai_van_ban/co_quan_ban_hanh/ngay_ban_hanh/linh_vuc nếu có giá trị; title + so_ky_hieu dùng hiển thị.
Source reference phải giữ portal ID và snapshot; chưa xác minh URL chi tiết cho từng tài liệu.


## 11. Công việc tiếp theo cho W02

Bảo toàn raw, xử lý NFC trên bản derived, review empty/image-only/HTML tables/encoding/date flags; không loại chỉ dựa độ dài.
Kiểm tra join và duplicate đầy đủ trước labels/splits; tạo nhóm duplicate chống leakage.
Lấy mẫu phân tầng theo năm/loại và review nguồn; kiểm tra tokenizer thật trước quyết định chunk tokens/overlap.
Quyền sử dụng, tiêu chí loại/giữ và corpus selection cần được nhóm nghiệm thu.
