# W01 — Corpus Audit

## 1. Dataset Overview

Dataset: `th1nhng0/vietnamese-legal-documents`; revision: `8977887f17be2defae4c5171d55562e1cde7d695`.
Audit UTC: 2026-10-13T02:26:26.193146+00:00; mode: **sample**.

## 2. Data Source and Licensing

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

License công bố chưa chứng minh quyền với mọi tài liệu nguồn. Không có raw dump trong báo cáo.

## 3. Schema Inspection

- `metadata/data` (document): `id: string`, `title: string`, `so_ky_hieu: string`, `ngay_ban_hanh: string`, `loai_van_ban: string`, `ngay_co_hieu_luc: string`, `ngay_het_hieu_luc: string`, `nguon_thu_thap: string`, `ngay_dang_cong_bao: string`, `nganh: string`, `linh_vuc: string`, `co_quan_ban_hanh: string`, `chuc_danh: string`, `nguoi_ky: string`, `pham_vi: string`, `thong_tin_ap_dung: string`, `tinh_trang_hieu_luc: string`
- `relationships/data` (relationship): `doc_id: string`, `other_doc_id: string`, `relationship: string`
- `content/data` (document): `id: string`, `content_html: string`
- `legacy_metadata/metadata` (document): `id: int64`, `document_number: large_string`, `title: large_string`, `legal_type: large_string`, `legal_sectors: large_string`, `issuing_authority: large_string`, `issuance_date: large_string`, `effect_date: large_string`, `effectless_date: large_string`, `effect_status: large_string`, `signers: large_string`
- `legacy_content/content` (document): `id: int64`, `content: large_string`

## 4. Data Volume

Footer Parquet là thống kê file, chưa phải full scan nội dung. Số đo chất lượng chỉ thuộc các record đã audit.

| Config/split | Footer rows | Audited rows | Coverage | Row group |
| --- | ---: | ---: | --- | ---: |
| metadata/data | 171556 | 1000 | partial | 7 |
| relationships/data | 1033255 | 1000 | partial | 163 |
| content/data | 170824 | 1000 | partial | 7 |
| legacy_metadata/metadata | 518601 | 1000 | partial | 0 |
| legacy_content/content | 518235 | None | unmeasured | 0 |

## 5. Metadata/Content Relationships

Join chỉ trên ID quan sát được; phía không có trong mẫu khác không phải orphan toàn corpus.

```json
{
  "metadata->content": {
    "scope": "observed_records_only",
    "shared_distinct_ids": 11,
    "metadata_only_distinct_ids": 989,
    "content_only_distinct_ids": 989,
    "observed_cardinality": "one_to_one"
  },
  "metadata->legacy_metadata": {
    "scope": "observed_records_only",
    "shared_distinct_ids": 1,
    "metadata_only_distinct_ids": 999,
    "content_only_distinct_ids": 999,
    "observed_cardinality": "one_to_one"
  },
  "metadata->relationships": {
    "scope": "observed_records_only",
    "shared_distinct_ids": 3,
    "metadata_only_distinct_ids": 997,
    "content_only_distinct_ids": 990,
    "observed_cardinality": "one_to_many"
  },
  "metadata->relationship_targets": {
    "scope": "observed_records_only",
    "shared_distinct_ids": 5,
    "metadata_only_distinct_ids": 995,
    "content_only_distinct_ids": 698,
    "observed_cardinality": "one_to_many"
  }
}
```

## 6. Missing and Duplicate Analysis

| Config | ID null/blank | Unsafe ID | Duplicate key extra rows | Missing fields (count / audited) |
| --- | ---: | ---: | ---: | --- |
| metadata | 0 | 0 | 0 | ngay_co_hieu_luc: 33/1000 (3.3%); ngay_het_hieu_luc: 553/1000 (55.3%); nguon_thu_thap: 495/1000 (49.5%); ngay_dang_cong_bao: 709/1000 (70.9%); nganh: 370/1000 (37.0%); linh_vuc: 24/1000 (2.4%); co_quan_ban_hanh: 5/1000 (0.5%); chuc_danh: 28/1000 (2.8%); nguoi_ky: 8/1000 (0.8%); thong_tin_ap_dung: 1000/1000 (100.0%) |
| relationships | 0 | 0 | 7 | 0 observed |
| content | 0 | 0 | 0 | 0 observed |
| legacy_metadata | 0 | 0 | 0 | effectless_date: 764/1000 (76.4%) |
| legacy_content | unmeasured | unmeasured | unmeasured | audit unavailable |

Relationships ở cấp edge: lặp doc_id là degree, không phải duplicate document/edge.

## 7. Text/HTML Quality

Diagnostic text bỏ head/script/style chỉ để đo; không lưu processed text. HTML parser khoan dung không xác nhận HTML hợp lệ.
| Config | Null | Blank source | Empty visible | Non-NFC | Same text/different IDs groups | HTML flags |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| content | 0 | 0 | 64 | 0 | 0 | 0 |

Date/metadata distributions (aggregate values; no signer or title excerpts):

```json
{
  "metadata": {
    "dates": {
      "ngay_ban_hanh": {
        "invalid": 0,
        "future": 0,
        "years": {
          "2022": 37,
          "2007": 47,
          "1994": 4,
          "2014": 44,
          "2023": 25,
          "2016": 32,
          "2004": 30,
          "2019": 29,
          "2017": 33,
          "2015": 49,
          "2008": 36,
          "2021": 25,
          "2006": 37,
          "2018": 31,
          "2010": 18,
          "1981": 3,
          "1995": 7,
          "1999": 17,
          "2000": 21,
          "1993": 4,
          "2026": 27,
          "2012": 29,
          "2024": 51,
          "2009": 37,
          "1997": 12,
          "2005": 43,
          "1991": 4,
          "1989": 3,
          "2011": 29,
          "2003": 31,
          "1998": 18,
          "2002": 22,
          "2013": 29,
          "2025": 39,
          "2020": 32,
          "1987": 5,
          "1962": 1,
          "1996": 9,
          "1966": 1,
          "1992": 3,
          "1948": 1,
          "1975": 1,
          "2001": 20,
          "1988": 3,
          "1982": 3,
          "1957": 1,
          "1946": 2,
          "1977": 2,
          "1973": 1,
          "1958": 1,
          "1983": 1,
          "1984": 2,
          "1947": 1,
          "1986": 1,
          "1980": 1,
          "1950": 1,
          "1945": 2,
          "1965": 1,
          "1990": 1
        }
      },
      "ngay_co_hieu_luc": {
        "invalid": 0,
        "future": 0,
        "years": {
          "2022": 40,
          "2007": 48,
          "1994": 3,
          "2015": 46,
          "2023": 22,
          "2014": 38,
          "2016": 31,
          "2004": 28,
          "2019": 23,
          "2018": 30,
          "2024": 49,
          "2008": 33,
          "2017": 39,
          "2021": 25,
          "2006": 36,
          "2010": 21,
          "1981": 3,
          "1995": 7,
          "1999": 18,
          "2000": 19,
          "1993": 4,
          "2026": 34,
          "2012": 27,
          "2009": 34,
          "1997": 12,
          "2005": 42,
          "1991": 4,
          "1989": 2,
          "2003": 25,
          "1998": 14,
          "2002": 20,
          "2013": 31,
          "2025": 36,
          "2020": 33,
          "1987": 5,
          "2011": 29,
          "1962": 1,
          "2001": 18,
          "1996": 8,
          "1966": 1,
          "1992": 3,
          "1948": 1,
          "1975": 1,
          "1988": 3,
          "1982": 2,
          "1957": 1,
          "1983": 2,
          "1946": 2,
          "1977": 2,
          "1973": 1,
          "1984": 2,
          "1947": 1,
          "1986": 1,
          "1980": 1,
          "1950": 1,
          "1945": 2,
          "1965": 1,
          "1990": 1
        }
      },
      "ngay_het_hieu_luc": {
        "invalid": 0,
        "future": 0,
        "years": {
          "2025": 73,
          "2017": 23,
          "2024": 33,
          "2026": 28,
          "2021": 22,
          "2020": 19,
          "2014": 14,
          "2012": 12,
          "2023": 16,
          "2016": 18,
          "2018": 21,
          "2000": 3,
          "2007": 12,
          "1997": 2,
          "2022": 21,
          "2013": 16,
          "2019": 20,
          "2006": 5,
          "2009": 13,
          "2010": 10,
          "2011": 10,
          "2008": 7,
          "2003": 5,
          "2015": 20,
          "1999": 7,
          "2001": 1,
          "1949": 1,
          "1913": 1,
          "2004": 2,
          "1998": 5,
          "2005": 5,
          "1975": 1,
          "2002": 1
        }
      },
      "ngay_dang_cong_bao": {
        "invalid": 0,
        "future": 1,
        "years": {
          "2007": 17,
          "1994": 1,
          "2014": 20,
          "2019": 6,
          "2011": 20,
          "2008": 18,
          "1982": 1,
          "1999": 2,
          "2001": 6,
          "2012": 14,
          "2006": 20,
          "2018": 6,
          "1997": 1,
          "2009": 16,
          "2016": 10,
          "2015": 24,
          "2004": 8,
          "2002": 5,
          "2013": 20,
          "2003": 10,
          "2005": 15,
          "2026": 2,
          "2023": 2,
          "1992": 1,
          "2020": 7,
          "2025": 3,
          "2010": 10,
          "1998": 2,
          "2022": 3,
          "2024": 4,
          "9999": 1,
          "1981": 2,
          "1988": 1,
          "1973": 1,
          "1987": 2,
          "2021": 3,
          "2017": 2,
          "1986": 1,
          "1996": 2,
          "1945": 1,
          "1990": 1
        }
      }
    },
    "metadata": {
      "loai_van_ban": {
        "Quyết định": 531,
        "Nghị quyết": 162,
        "Thông tư": 97,
        "Bản dịch văn bản": 69,
        "Chỉ thị": 54,
        "Nghị định": 36,
        "Thông tư liên tịch": 15,
        "Văn bản hợp nhất": 13,
        "Sắc lệnh": 7,
        "Công văn": 4,
        "Văn bản hệ thống hóa": 4,
        "Lệnh": 2
      },
      "nguon_thu_thap": {
        "Bản chính văn bản": 25,
        "Bản chính": 22,
        "Công báo điện tử;": 16,
        "bản chính": 14,
        "Văn bản gốc": 9,
        "Công báo Thành phố Hồ Chí Minh": 8,
        "Công báo": 8,
        "Văn phòng UBND tỉnh": 7,
        "công báo": 7,
        "Bản gốc văn bản": 7,
        "bản chính, bản gốc văn bản": 6,
        "Công báo điện tử Thành phố Hồ Chí Minh": 6
      },
      "nganh": {
        "Tài chính": 120,
        "Nội vụ": 57,
        "Tài nguyên và Môi trường": 48,
        "Lao động - Thương binh và Xã hội": 47,
        "Nông nghiệp và phát triển nông thôn": 38,
        "Xây dựng": 31,
        "Giáo dục và đào tạo": 29,
        "Tư pháp": 27,
        "Công Thương": 27,
        "Giao thông Vận tải": 21,
        "Khoa học và công nghệ": 19,
        "Kế hoạch và Đầu tư": 18
      },
      "linh_vuc": {
        "Chưa phân loại": 657,
        "Đất đai": 19,
        "Quản lý thuế, phí, lệ phí và thu khác của ngân sách nhà nước": 12,
        "Lĩnh vực giá": 12,
        "Tổ chức- Biên chế": 10,
        "Ngân sách nhà nước": 9,
        "Lao động, tiền lương, tiền công": 9,
        "Quản lý ngân sách": 9,
        "Thi đua, khen thưởng": 9,
        "Quản lý ngân sách nhà nước": 6,
        "Quản lý thuế, phí và lệ phí": 6,
        "Công chức, viên chức": 6
      },
      "co_quan_ban_hanh": {
        "Bộ Tài chính": 67,
        "Chính phủ": 46,
        "Thủ tướng Chính phủ": 43,
        "UBND Thành phố Hồ Chí Minh": 30,
        "UBND Thành phố Hà Nội": 17,
        "UBND Tỉnh Nghệ An": 16,
        "Bộ Nông nghiệp và Phát triển nông thôn": 16,
        "UBND Tỉnh Gia Lai": 15,
        "UBND tỉnh Bình Phước": 15,
        "UBND tỉnh Thừa Thiên Huế": 15,
        "Ngân hàng Nhà nước Việt Nam": 14,
        "UBND Tỉnh Đồng Nai": 13
      },
      "pham_vi": {
        "Địa phương": 665,
        "Trung ương": 335
      },
      "tinh_trang_hieu_luc": {
        "Hết hiệu lực toàn bộ": 523,
        "Còn hiệu lực": 427,
        "Hết hiệu lực một phần": 30,
        "Chưa xác định": 17,
        "Ngưng hiệu lực": 2,
        "Không còn phù hợp": 1
      }
    }
  },
  "relationships": {
    "dates": {},
    "metadata": {
      "relationship": {
        "Căn cứ": 636,
        "Dẫn chiếu": 71,
        "Văn bản quy định hết hiệu lực": 50,
        "Thay thế": 37,
        "Bãi bỏ": 36,
        "Quy định chi tiết, hướng dẫn thi hành": 36,
        "Văn bản HD, QĐ chi tiết": 36,
        "Văn bản căn cứ": 34,
        "Văn bản bổ sung": 17,
        "Sửa đổi, bổ sung": 15,
        "Văn bản quy định hết hiệu lực 1 phần": 10,
        "Văn bản hết hiệu lực": 10
      }
    }
  },
  "legacy_metadata": {
    "dates": {
      "issuance_date": {
        "invalid": 0,
        "future": 0,
        "years": {
          "2025": 64,
          "2026": 10,
          "2022": 52,
          "2020": 48,
          "2024": 66,
          "2015": 47,
          "2018": 57,
          "2012": 35,
          "2017": 46,
          "2023": 49,
          "2010": 35,
          "2021": 56,
          "2019": 50,
          "2009": 29,
          "2013": 52,
          "1992": 1,
          "2011": 28,
          "2007": 28,
          "2016": 44,
          "2004": 19,
          "2014": 37,
          "2001": 11,
          "1997": 3,
          "2003": 13,
          "2005": 16,
          "2006": 26,
          "2002": 16,
          "2008": 28,
          "1959": 2,
          "1974": 1,
          "1980": 1,
          "1999": 2,
          "1996": 1,
          "1994": 2,
          "1995": 1,
          "1990": 2,
          "1998": 3,
          "2000": 3,
          "1988": 1,
          "1978": 2,
          "1971": 1,
          "1962": 3,
          "1945": 1,
          "1982": 1,
          "1977": 1,
          "1946": 2,
          "1963": 1,
          "1975": 2,
          "1957": 1
        }
      },
      "effect_date": {
        "invalid": 0,
        "future": 0,
        "years": {
          "2025": 65,
          "2026": 12,
          "2022": 52,
          "2020": 47,
          "2024": 63,
          "2015": 47,
          "2019": 49,
          "2012": 35,
          "2017": 45,
          "2023": 50,
          "2010": 33,
          "2018": 57,
          "2021": 59,
          "2009": 30,
          "2013": 50,
          "1992": 1,
          "2007": 28,
          "2016": 44,
          "2004": 16,
          "2011": 29,
          "2014": 39,
          "2001": 10,
          "1997": 3,
          "2003": 12,
          "2005": 16,
          "2006": 28,
          "2002": 17,
          "2008": 29,
          "1980": 3,
          "1974": 1,
          "1999": 2,
          "1996": 1,
          "1994": 3,
          "1995": 1,
          "1990": 2,
          "1998": 3,
          "2000": 3,
          "1988": 1,
          "1979": 1,
          "1971": 1,
          "1977": 4,
          "1984": 1,
          "1993": 2,
          "1976": 1,
          "1978": 1,
          "1975": 2,
          "1982": 1
        }
      },
      "effectless_date": {
        "invalid": 0,
        "future": 0,
        "years": {
          "2025": 42,
          "2023": 11,
          "2022": 7,
          "2024": 18,
          "2021": 20,
          "2019": 10,
          "2020": 10,
          "2016": 15,
          "2018": 9,
          "2014": 6,
          "2009": 7,
          "2017": 14,
          "2005": 2,
          "2015": 11,
          "1998": 1,
          "2002": 1,
          "2008": 8,
          "2013": 4,
          "2000": 4,
          "2007": 7,
          "2011": 8,
          "2026": 7,
          "2010": 7,
          "2006": 3,
          "2012": 4
        }
      }
    },
    "metadata": {
      "legal_type": {
        "Decision": 456,
        "Official Dispatch": 261,
        "Resolution": 84,
        "Kế hoạch": 57,
        "Directive": 41,
        "Announcement": 30,
        "Circular": 27,
        "Decree of Government": 12,
        "Integrated document": 9,
        "Báo cáo": 7,
        "Joint circular": 5,
        "Official Telegram": 4
      },
      "legal_sectors": {
        "Administrative apparatus": 156,
        "Taxes - Fees - Charges": 57,
        "Government finance": 45,
        "Culture - Society": 45,
        "Natural resources – Environment": 36,
        "Sports - Health": 34,
        "Export & Import": 26,
        "Construction – Urban Planning": 26,
        "Other": 25,
        "Real estate": 25,
        "Export & Import, Taxes - Fees - Charges": 25,
        "Administrative apparatus, Government finance": 23
      },
      "issuing_authority": {
        "Tổng cục Hải quan": 57,
        "Tổng cục Thuế": 42,
        "Thủ tướng Chính phủ": 36,
        "Văn phòng Chính phủ": 32,
        "Thành phố Hà Nội": 26,
        "Bộ Tài chính": 24,
        "Thành phố Hồ Chí Minh": 23,
        "Bộ Xây dựng": 22,
        "Tỉnh Thanh Hóa": 18,
        "Tỉnh Khánh Hòa": 15,
        "Bộ Công thương": 15,
        "Bộ Nông nghiệp và Phát triển nông thôn": 13
      },
      "effect_status": {
        "In effect": 635,
        "Expired": 236,
        "Unknown": 89,
        "No longer applicable": 40
      }
    }
  }
}
```

Top 12 displayed per metadata field; complete observed frequencies are in JSON.

## 8. Length Distribution

Characters = diagnostic text length; whitespace words không phải BKAI tokens. Quantile dùng nội suy rank q*(n-1).

| Config | Metric | n | min | median | mean | p90 | p95 | p99 | max |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| content | characters | 1000 | 5 | 4917.5 | 11990.2 | 27558.1 | 40192.55 | 105614.9 | 488288 |
| content | whitespace_words | 1000 | 0 | 946.0 | 2252.93 | 5510.5 | 7676.5 | 17763.35 | 52607 |
| content | source_characters | 1000 | 83 | 10452.5 | 24260.24 | 47005.0 | 79789.5 | 249850.05 | 1547192 |

Token count: **unverified**, tokenizer chưa cài/chạy.

## 9. Legal Document Structure

Regex heuristic: số record có dấu hiệu, không phải số điều/khoản chính xác.

```json
{
  "content": {
    "chuong": 191,
    "muc": 61,
    "dieu": 799,
    "khoan": 668,
    "diem": 496,
    "phu_luc": 162,
    "legal_reference": 379,
    "tables": 422
  }
}
```

## 10. Recommended Corpus Selection

Có thể nghiên cứu retrieval với metadata + content hiện hành; chưa đủ bằng chứng chất lượng để chốt corpus.
Đề xuất W02: index chunk theo Điều/khoản khi cấu trúc đủ rõ, fallback theo đoạn; trả kết quả và đánh giá ở cấp document.
Chunk giữ source ID, revision, config/split/file, vị trí gốc và document ID; chưa chốt token budget.

| Phương án | Lợi ích | Hạn chế / ảnh hưởng retrieval | Quyết định |
| --- | --- | --- | --- |
| Current metadata + content | HTML và metadata filter đã kiểm tra schema | Nội dung rỗng/thiếu cần review; mẫu không xác nhận mọi join | Đề xuất ưu tiên, chưa chọn subset |
| Stratify theo loại + năm | Tránh bias của prefix; metadata hỗ trợ filter | Ngày thiếu/sai và lệch lớp cần strata riêng | Đề xuất sau kiểm tra coverage |
| Filter lĩnh vực | Gọn và có mục đích | Giá trị missing/Chưa phân loại không chứng minh ngoài domain | Chờ đo đầy đủ và nhóm chọn domain |
| Trộn legacy | Tăng coverage lịch sử | ID int, metadata English, plain text; nguy cơ duplicate/leakage | Không trộn tự động |

Filter dùng loai_van_ban/co_quan_ban_hanh/ngay_ban_hanh/linh_vuc nếu có giá trị; title + so_ky_hieu dùng hiển thị.
Source reference phải giữ portal ID và snapshot; chưa xác minh URL chi tiết cho từng tài liệu.

## 11. Risks and Limitations

- License is a publisher claim; source rights remain unresolved.
- Cluster sample is not representative by year/type/domain; no population extrapolation.
- Partial joins compare independently sampled records; observed sample-only IDs are not corpus orphans.
- HTML visible-text/structure diagnostics are heuristics; no cleaning or processed corpus produced.
- FAILED legacy_content/content/legacy/content.parquet: Selected row group exceeds 256 MiB memory guard; source requires re-sharding; statistics unavailable
- Không có relevance labels/split. Rủi ro fine-tuning chính: nhãn yếu, false negatives, duplicate/leakage và truncate văn bản dài.
- HTML flags, mojibake, date tương lai là dấu hiệu review; không tự động chứng minh record sai.

## 12. Next Steps for W02

Bảo toàn raw, xử lý NFC trên bản derived, review empty/image-only/HTML tables/encoding/date flags; không loại chỉ dựa độ dài.
Kiểm tra join và duplicate đầy đủ trước labels/splits; tạo nhóm duplicate chống leakage.
Lấy mẫu phân tầng theo năm/loại và review nguồn; kiểm tra tokenizer thật trước quyết định chunk tokens/overlap.
Quyền sử dụng, tiêu chí loại/giữ và corpus selection cần được nhóm nghiệm thu.
