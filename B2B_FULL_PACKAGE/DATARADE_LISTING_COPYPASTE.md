# HƯỚNG DẪN TỪNG BƯỚC ĐĂNG BÁN TRÊN DATARADE
# (Copy-paste từng mục, mất khoảng 20 phút)

## ===== BƯỚC 1: TẠO TÀI KHOẢN PROVIDER =====

1. Vào: https://datarade.ai/providers/sign-up
2. Điền form:
   - Company Name: [Tên công ty/cá nhân của bạn]
   - Email: [email của bạn]
   - Country: Vietnam
   - Category: "AI & Machine Learning Training Data"
3. Xác nhận email → đăng nhập

## ===== BƯỚC 2: TẠO PRODUCT LISTING =====

Vào Dashboard → "Add Product" → điền các mục sau:

### --- PRODUCT TITLE ---
(Copy nguyên dòng dưới)

PCB Design Rule Check (DRC) AI Training Dataset — Production-Grade 4-Layer KiCad Board

### --- SHORT DESCRIPTION (150 chars) ---

First-ever production-grade PCB DRC training data: 6 bad→fixed benchmark pairs, 798→0 violation convergence, 387 Python scripts, KiCad 10 S-Expression.

### --- LONG DESCRIPTION ---
(Copy toàn bộ khối dưới)

## Overview

The first publicly available AI training dataset for PCB (Printed Circuit Board) Design Rule Check automation. Extracted from a production-grade 4-layer IoT sensor board (52.0 × 75.0 mm, IPC-2221 Class 2).

## What's Inside

**Training Data:**
- 6 benchmark bad→fixed PCB file pairs with DRC JSON annotations and unified diff patches
- 1 complete board pair: 798 DRC violations → 0 violations (full convergence)
- 15+ DRC progression snapshots documenting step-by-step convergence
- Structured DRC dataset with 384-pad coordinate database
- Machine-readable metadata catalog with SHA-256 integrity checksums
- JSON Schema for automated validation

**Algorithms & Scripts (387 files):**
- A* multi-layer router with halo clearance
- Manhattan topology ordering engine
- KiCad S-Expression track/via generator
- Geometric DRC pre-check library (RouteAuditor)
- 4-layer via fanout builder
- Zone fill automation
- Complete 63-net routing pipeline achieving 0 DRC violations

**Research Documentation:**
- 4 novel routing theorems with mathematical proofs:
  1. Planar Topology Embedding Theorem
  2. Orthogonal Layering & Staggered Underpass
  3. Zone Island Unlocking Technique
  4. Sensitive Signal Protection Rules
- 6 detailed case studies with full algorithm analysis
- AI Engineer evaluation guide with Python dataloader code

## Board Specifications

- Dimensions: 52.0 × 75.0 mm
- Layers: 4 (F.Cu Signal / In1.Cu Solid GND Plane / In2.Cu Split +3V3/+5V Power / B.Cu Signal)
- Components: 94 footprints, 384 pads, 63 nets
- Standard: IPC-2221 Class 2 (0.15mm clearance, 0.25mm drill-to-hole)
- EDA: KiCad 10 (open-source S-Expression format)

## Error Types Covered (12 categories)

clearance, crossing, unconnected_items, hole_to_hole, holes_co_located, copper_edge_clearance, pad_collision, component_collision, layer_conflict, via_obstruction, intergroup_conflict, isolated_island

## AI/ML Use Cases

1. DRC Error Classification & Localization
2. Automated PCB Repair (bad→fixed transformation learning)
3. DRC Score Prediction from layout features
4. Graph Neural Networks for PCB connectivity
5. Reinforcement Learning for fix strategy optimization
6. LLM Fine-Tuning on KiCad S-Expression CAD syntax
7. Design Rule Extraction from successful corrections

## Verification

Every fixed PCB file verified with official KiCad CLI:
kicad-cli pcb drc --severity-all → 0 violations, 0 unconnected pads, 0 footprint errors

All file integrity verified via SHA-256 checksums in dataset_catalog.json.

### --- CATEGORIES / TAGS ---
(Chọn hoặc gõ các tag sau)

- AI Training Data
- Machine Learning
- Electronics
- Manufacturing
- CAD/EDA
- IoT
- PCB Design
- Quality Assurance
- Automation

### --- DATA FORMAT ---

- KiCad S-Expression (.kicad_pcb)
- JSON (.json)
- CSV (.csv)
- Python scripts (.py)
- Markdown documentation (.md)
- Unified diff patches (.patch)
- KiCad DRC reports (.rpt)

### --- GEOGRAPHIC COVERAGE ---

Global (hardware design data, not geographically bound)

### --- UPDATE FREQUENCY ---

Quarterly (new benchmark cases and DRC progression data)

### --- DELIVERY METHOD ---

Download (ZIP archive, ~23 MB)

### --- PRICING ---

(Chọn "Custom pricing" hoặc điền 3 tiers)

| Tier | Price | License |
|---|---|---|
| Researcher | $500 – $1,500 | Non-commercial, academic use |
| Professional | $5,000 – $15,000 | Commercial, single organization |
| Enterprise | $15,000 – $50,000/year | Commercial + support + updates |

### --- SAMPLE DATA ---

Upload file: B2B_SALE_PACKAGE\README.md
(hoặc zip một case benchmark nhỏ: case_001_vbus_clearance_dogleg)


## ===== BƯỚC 3: UPLOAD SAMPLE =====

Tạo file zip mẫu miễn phí để người mua preview:

1. Mở thư mục: A:\DEVICE\B2B_FULL_PACKAGE\01_training_data\benchmark_cases\case_001_vbus_clearance_dogleg
2. Nén (zip) thư mục đó
3. Upload lên Datarade mục "Sample Data"


## ===== BƯỚC 4: SUBMIT & CHỜ DUYỆT =====

1. Review lại tất cả thông tin
2. Click "Submit for Review"
3. Datarade team sẽ review trong 1-3 ngày làm việc
4. Sau khi duyệt → listing xuất hiện trên marketplace
5. Khi có buyer quan tâm → Datarade gửi lead về email bạn


## ===== LƯU Ý QUAN TRỌNG =====

- Datarade là marketplace B2B kiểu lead-gen: người mua liên hệ bạn qua Datarade, 
  bạn thương lượng giá và giao hàng trực tiếp
- Datarade thu commission trên mỗi deal đóng (thường 10-20%)
- Listing miễn phí, chỉ trả phí khi có giao dịch
- Bạn giữ quyền kiểm soát: chọn ai được mua, giá bao nhiêu

## ===== SONG SONG: ĐĂNG TRÊN HUGGING FACE =====

Nhanh hơn Datarade, reach lớn hơn cho cộng đồng AI:

```powershell
# 1. Cài CLI
pip install huggingface_hub

# 2. Đăng nhập (cần tạo tài khoản trước tại huggingface.co)
huggingface-cli login

# 3. Upload dataset
huggingface-cli upload YOUR_USERNAME/pcb-drc-ai-training "A:\DEVICE\B2B_FULL_PACKAGE" . --repo-type dataset

# 4. Copy file HUGGINGFACE_DATASET_CARD.md thành README.md trong repo
# 5. Vào Settings → bật "Gated access" → "Manual approval"
```
