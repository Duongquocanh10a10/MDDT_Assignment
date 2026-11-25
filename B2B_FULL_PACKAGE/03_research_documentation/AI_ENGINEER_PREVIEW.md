# 🧪 B2B TECHNICAL PREVIEW & EVALUATION GUIDE
## Dataset: Production-Grade KiCad 4-Layer PCB DRC AI Training Corpus (v1.0 Sample)
**Target Audience:** Machine Learning Engineers, EDA CAD Automation Researchers, AI Product Managers  
**Vendor:** PCB Automation Lab  
**Contact:** [Sales & Licensing: Inquire for Full 417-PCB Dataset]  

---

## 1. EXECUTIVE SUMMARY (DÀNH CHO QUẢN LÝ DỰ ÁN & AI TEAM)

Tập dữ liệu này cung cấp các cặp **bo mạch thực tế trước sửa (Bad) ↔ sau sửa (Fixed)** cùng báo cáo DRC định dạng JSON và patch vi phân hình học (unified diff), trích xuất từ thiết bị quan trắc công nghiệp 4 lớp thu nhỏ $52.0 \times 75.0\text{ mm}$ (94 footprints, 384 pads, 63 nets, IPC-2221 Class 2).

### Tại sao tập dữ liệu này có giá trị cao cho mô hình AI?
1. **Dữ liệu thật 100% (Not Synthetic):** Không phải mạch đồ chơi đơn giản. Chứa đầy đủ các thách thức công nghiệp: IC chân mịn QFN-28 (CP2102N), cổng Type-C vi sai tốc độ cao, nguồn xung Boost $1.2\text{ MHz}$ (MT3608), đường analog nhạy cảm pA, module vi dải RF 50-ohm.
2. **Khớp cặp 100% (Strictly Paired):** Mỗi ca lỗi đều có:
   - `bad.kicad_pcb`: Layout gốc chứa lỗi vi phạm DRC.
   - `bad_drc.json`: Danh sách lỗi dạng máy đọc được kèm tọa độ $(X, Y)$ chính xác.
   - `fixed.kicad_pcb`: Layout đã tối ưu đạt 0 lỗi DRC và 0 unconnected items.
   - `fixed_drc.json`: Xác nhận nghiệm thu 0 lỗi.
   - `diff.patch`: Patch sửa lỗi chuẩn Git, mô tả chính xác những đoạn track/via nào đã được dịch chuyển hoặc vẽ lại.
   - `README.md`: Giải thích cơ chế vật lý và giải thuật hình học đã dùng để sửa lỗi.
3. **Độ tin cậy tuyệt đối:** 100% file `fixed.kicad_pcb` đều được kiểm định bằng công cụ chính thức `kicad-cli pcb drc --severity-all` đạt **0 VIOLATIONS, 0 UNCONNECTED PADS, 0 FOOTPRINT ERRORS**.

---

## 2. BẢN ĐỒ CẤU TRÚC DỮ LIỆU MẪU (SAMPLE DATASET STRUCTURE)

```
A:\DEVICE\B2B_SAMPLE_DATASET\SAMPLE_PACKAGE/
├── dataset_catalog.json          # Machine-readable metadata index (JSON)
├── dataset_catalog.csv           # Spreadsheet metadata index (CSV)
├── README.md                     # Tổng quan thương mại
│
├── benchmark_cases/              # 5 Cặp ca lỗi - sửa lỗi chuyên biệt (Mini-benchmarks)
│   ├── case_001_vbus_clearance_dogleg/
│   │   ├── bad.kicad_pcb         # Lỗi vi phạm clearance đường VBUS vs track ngang B.Cu
│   │   ├── fixed.kicad_pcb       # Sửa bằng kỹ thuật bẻ góc chữ chi (dogleg)
│   │   ├── bad_drc.json          # JSON ghi rõ vi phạm khoảng hở 0.1499mm < 0.150mm
│   │   ├── fixed_drc.json        # JSON 0 lỗi
│   │   ├── diff.patch            # Diffs sửa đổi hình học
│   │   └── README.md             # Thuyết minh kỹ thuật
│   ├── case_002_mt3608_boost_clearance/    # Tối ưu SW_NODE & BST_FB
│   ├── case_003_lcd_block_routing/         # Định tuyến chùm bus LCD bằng Manhattan Topo
│   ├── case_004_sensors_gps_rtc_routing/   # Định tuyến đa khối cảm biến I2C / GPS / RTC
│   └── case_005_isolated_island_and_unconnected_gnd/ # Khắc phục đảo đồng cô lập & cấn via
│
├── full_board_pair/              # Cặp bo mạch nguyên bản hoàn chỉnh (Toàn bộ 63 nets)
│   ├── WaterSensor_Before_Fix.kicad_pcb   # Bản trước tối ưu (215 lỗi vi phạm)
│   ├── WaterSensor_Final_ZeroDRC.kicad_pcb# Bản sau tối ưu (0 lỗi vi phạm, 100% net)
│   └── WaterSensor_Final_ZeroDRC.kicad_pro# Quy tắc thiết kế netclass 0.15mm
│
└── drc_progression/              # 15 Báo cáo DRC thực tế thể hiện đường cong hội tụ
    ├── drc_flawless.rpt          # 798 vi phạm (Baseline ban đầu)
    ├── drc_placed.rpt            # 728 vi phạm (Sau khi xếp cụm)
    ├── drc_compact_new.rpt       # 523 vi phạm (Sau khi co cụm Y: 53-128mm)
    ├── DRC.rpt                   # 237 vi phạm (Trước khi fanout plane nội)
    ├── drc_batch1.rpt            # 88 vi phạm
    ├── drc_after_edge.rpt        # 76 vi phạm
    ├── drc_manhattan.rpt         # 55 vi phạm
    ├── drc_tuned.rpt             # 36 vi phạm
    ├── drc_step1.rpt             # 28 vi phạm
    ├── drc_clean_complete_d.rpt  # 18 vi phạm
    ├── drc_deterministic.rpt     # 12 vi phạm
    ├── drc_clean_placement.rpt   # 4 vi phạm
    ├── drc_zone_test.rpt         # 1 vi phạm
    ├── drc_step.rpt              # 0 vi phạm (còn 8 chân chưa nối)
    └── WaterSensor_drc_all.rpt   # 0 VI PHẠM, 0 CHÂN HỞ (GOLDEN BENCHMARK)
```

---

## 3. CÁC BÀI TOÁN AI / ML CÓ THỂ ÁP DỤNG NGAY

### Bài toán 1: Phân loại & Định vị lỗi DRC (DRC Error Detection & Localization)
- **Input:** File `.kicad_pcb` hoặc đồ thị hình học (GNN graph).
- **Target:** Dự đoán chính xác loại lỗi (`clearance`, `shorting`, `hole_to_hole`, `isolated_island`) và tọa độ $(X, Y)$ của điểm vi phạm.
- **Dữ liệu huấn luyện:** Ánh xạ từ các cặp file trong `benchmark_cases/` và `drc_progression/`.

### Bài toán 2: Đồ thị mạng nơ-ron cho PCB (Graph Neural Networks - GNNs)
- **Cấu trúc đồ thị đề xuất:**
  * **Nodes:** Pads, Vias (thuộc tính: tọa độ X/Y, layer, net_id, pad_type, size).
  * **Edges:** Tracks, Airwires (thuộc tính: width, layer, distance, impedance).
  * **Graph Labels:** Số lượng vi phạm DRC, tỷ lệ kết nối hoàn thành.

### Bài toán 3: Học tăng cường & Tự động sửa lỗi (RL & Generative Auto-Repair)
- **Input:** `bad.kicad_pcb` + `bad_drc.json`.
- **Target:** Sinh ra chuỗi thao tác dời via, vẽ lại track (được thể hiện qua `diff.patch`) để chuyển dịch trạng thái về `fixed.kicad_pcb`.

### Bài toán 4: Huấn luyện LLM sinh mã S-Expression (KiCad CAD-Code Copilot)
- Định dạng `.kicad_pcb` là S-Expression thuần văn bản. Mô hình LLM (như Claude, LLaMA, StarCoder) có thể được fine-tune trực tiếp trên các khối `(segment ...)` và `(via ...)` để học cách đi dây chuẩn công nghiệp.

---

## 4. CODE MẪU: PYTHON DATALOADER TRÍCH XUẤT CẶP DỮ LIỆU

Kỹ sư AI có thể chạy ngay đoạn mã sau để load và tiền xử lý dữ liệu:

```python
import os, json, re

def load_pcb_benchmark_pair(case_dir):
    """
    Load a Bad/Fixed PCB training pair with DRC annotations
    """
    bad_pcb_path = os.path.join(case_dir, "bad.kicad_pcb")
    fixed_pcb_path = os.path.join(case_dir, "fixed.kicad_pcb")
    bad_drc_path = os.path.join(case_dir, "bad_drc.json")
    diff_patch_path = os.path.join(case_dir, "diff.patch")
    
    with open(bad_pcb_path, 'r', encoding='utf-8') as f:
        bad_pcb_text = f.read()
    with open(fixed_pcb_path, 'r', encoding='utf-8') as f:
        fixed_pcb_text = f.read()
    with open(bad_drc_path, 'r', encoding='utf-8') as f:
        bad_drc_data = json.load(f)
    with open(diff_patch_path, 'r', encoding='utf-8') as f:
        diff_text = f.read()
        
    print(f"Loaded case: {os.path.basename(case_dir)}")
    print(f"  - Bad PCB size: {len(bad_pcb_text):,} chars")
    print(f"  - Fixed PCB size: {len(fixed_pcb_text):,} chars")
    print(f"  - Violations before fix: {len(bad_drc_data)}")
    print(f"  - Patch modification lines: {len(diff_text.splitlines())} lines")
    
    return {
        "bad_raw": bad_pcb_text,
        "fixed_raw": fixed_pcb_text,
        "drc_violations": bad_drc_data,
        "diff_patch": diff_text
    }

# Example execution:
# case_data = load_pcb_benchmark_pair(r"A:\DEVICE\B2B_SAMPLE_DATASET\SAMPLE_PACKAGE\benchmark_cases\case_005_isolated_island_and_unconnected_gnd")
```

---

## 5. HƯỚNG DẪN TỰ KIỂM CHỨNG TẠI CHỖ (INDEPENDENT VERIFICATION)

Kỹ sư có thể tự xác minh chất lượng dữ liệu bằng KiCad CLI chính thức:

```powershell
# Chạy DRC kiểm tra file sau sửa (Fixed) trong case_005:
& "kicad-cli" pcb drc --severity-all `
    --output "test_fixed_drc.rpt" `
    "A:\DEVICE\B2B_SAMPLE_DATASET\SAMPLE_PACKAGE\benchmark_cases\case_005_isolated_island_and_unconnected_gnd\fixed.kicad_pcb"

# Kết quả trả về đảm bảo:
# ** Found 0 DRC violations **
# ** Found 0 unconnected pads **
# ** Found 0 Footprint errors **
```

---

## 6. LIÊN HỆ ĐẶT MUA TOÀN BỘ DATASET ĐẦY ĐỦ (FULL COMMERCIAL CORPUS)

Bộ dataset đầy đủ (Full Commercial Edition) bao gồm:
- **417 tập tin `.kicad_pcb`** bao quát mọi trạng thái layout và xung đột đa tầng.
- **58 báo cáo DRC chuẩn KiCad 10** với hơn 3,000 điểm vi phạm thực tế đã phân loại.
- **200+ script Python tự động hóa** giải thuật định tuyến (A*, Manhattan Topo, Planar Ordering, Zone Filling).
- **Trọn gói dự án KiCad gốc:** Sơ đồ nguyên lý `.kicad_sch`, file thư viện, file cấu hình `.kicad_pro`, tệp gia công Gerber RS-274X và file khoan Excellon.

*Liên hệ bộ phận kỹ thuật & bản quyền để nhận báo giá và hợp đồng chuyển giao dữ liệu huấn luyện AI.*
