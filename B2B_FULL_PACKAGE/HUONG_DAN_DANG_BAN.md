# 🚀 HƯỚNG DẪN ĐĂNG BÁN DATASET — Từng bước cụ thể

## Tổng quan chiến lược 3 kênh

| Kênh | Mục đích | Thời gian setup |
|---|---|---|
| **Hugging Face** | Visibility + lead gen (miễn phí) | 30 phút |
| **Gumroad** | Thu tiền trực tiếp | 15 phút |
| **Liên hệ trực tiếp** | Enterprise deals ($15K–$50K) | Ongoing |

---

## KÊNH 1: HUGGING FACE HUB (Gated Access + Lead Gen)

### Bước 1: Tạo tài khoản
1. Vào https://huggingface.co/join → đăng ký
2. Tạo Organization (nếu muốn dùng tên "PCB Automation Lab"): Settings → Organizations → New

### Bước 2: Tạo Dataset Repository
1. Vào https://huggingface.co/new-dataset
2. **Dataset name:** `pcb-drc-ai-training`
3. **License:** `other` → ghi "Commercial B2B"
4. **Visibility:** Public (nhưng sẽ gated)

### Bước 3: Upload files
```bash
# Cài Hugging Face CLI
pip install huggingface_hub

# Login
huggingface-cli login

# Upload toàn bộ gói bán
huggingface-cli upload YOUR_USERNAME/pcb-drc-ai-training "A:\DEVICE\B2B_FULL_PACKAGE" . --repo-type dataset
```

### Bước 4: Thêm Dataset Card
- Copy nội dung file `B2B_SALE_PACKAGE/HUGGINGFACE_DATASET_CARD.md` → paste vào README.md của repo
- Phần YAML frontmatter (giữa `---`) chứa `extra_gated_fields` → tự động tạo form xin quyền truy cập

### Bước 5: Bật Gated Access
1. Vào Settings của dataset repo
2. Bật "Gated access" → chọn "Manual approval"
3. Khi có người request → bạn nhận email → duyệt hoặc từ chối

---

## KÊNH 2: GUMROAD (Thu tiền trực tiếp)

### Bước 1: Tạo tài khoản
1. Vào https://gumroad.com → Sign up
2. Kết nối PayPal hoặc Stripe để nhận tiền

### Bước 2: Tạo 3 sản phẩm (3 tiers)

#### Tier 1: Researcher ($500)
- **Tên:** "PCB DRC AI Training Dataset — Researcher License"
- **Mô tả:** 6 benchmark cases, 15+ DRC reports, full board pair, non-commercial use
- **File:** Zip folder `B2B_SALE_PACKAGE/` (data-only, không scripts)
- **Price:** $500

#### Tier 2: Professional ($5,000)
- **Tên:** "PCB DRC AI Training Dataset — Professional License"
- **Mô tả:** Everything in Researcher + 387 Python scripts + 4 core theorems + commercial license
- **File:** Zip folder `B2B_FULL_PACKAGE/`
- **Price:** $5,000

#### Tier 3: Enterprise ($15,000)
- **Tên:** "PCB DRC AI Training Dataset — Enterprise License"
- **Mô tả:** Everything + 1-year support + custom format adaptation + quarterly updates
- **Price:** $15,000
- **Note:** Mark as "I want this!" → redirect to email for custom contract

### Bước 3: Tạo landing page
- Gumroad tự tạo landing page: `gumroad.com/l/pcb-drc-dataset`
- Thêm link này vào Hugging Face dataset card

---

## KÊNH 3: LIÊN HỆ TRỰC TIẾP (Enterprise)

### Target companies (AI/EDA):
| Company | AI Product | Contact |
|---|---|---|
| Cadence | Cerebrus AI | partnerships@cadence.com |
| Synopsys | DSO.ai | ai-research@synopsys.com |
| Altium | Cloud PCB + AI | bizdev@altium.com |
| Siemens EDA | HyperLynx | eda-partnerships@siemens.com |
| Quilter (startup) | AI PCB design | hello@quilter.ai |
| Celus (startup) | Automated HW design | info@celus.io |
| Jitx (startup) | Code-driven PCB | info@jitx.com |

### Email template:
```
Subject: Production-Grade PCB DRC AI Training Dataset — 798→0 Violations

Hi [Name],

I've built what I believe is the first production-grade PCB DRC training dataset:
- 417 KiCad PCB files (4-layer, 94 components, IPC-2221 Class 2)
- 6 benchmark bad→fixed pairs with diff patches
- 58 DRC reports documenting 798→0 violation convergence
- 387 Python scripts (A* router, Manhattan topology, zone filler)
- 4 novel routing theorems with proofs

Ideal for training DRC error classification, automated PCB repair, 
and LLM fine-tuning on S-Expression CAD syntax.

Free evaluation sample available on Hugging Face:
[link]

Would your AI/ML team be interested in evaluating the full dataset?

Best regards,
[Your name]
```

---

## KÊNH BỔ SUNG (tuần 2-4):

### Kaggle (miễn phí, community)
1. Upload sample 20 files lên https://www.kaggle.com/datasets/new
2. Viết notebook demo: load PCB → parse violations → visualize convergence
3. Link đến Gumroad/HF cho full version

### AWS Data Exchange (enterprise, tuần 3-4)
1. Đăng ký AWS Marketplace seller: https://aws.amazon.com/marketplace/management/tour
2. Tạo data product → set annual subscription $15,000
3. Mất 2-4 tuần review

---

## ĐỊNH GIÁ THAM KHẢO

### Chi phí tạo dataset này:
- Thiết kế PCB 4 lớp: ~40 giờ × $50/h = $2,000
- Annotation 3000+ DRC violations: ~250 giờ × $50/h = $12,500
- Viết 387 scripts: ~200 giờ × $50/h = $10,000
- Nghiên cứu 4 định lý: ~100 giờ × $75/h = $7,500
- **Tổng chi phí ước tính: ~$32,000**

### Giá bán hợp lý:
- **Researcher:** $500–$1,500 (thu hồi qua volume)
- **Professional:** $5,000–$15,000 (margin tốt)
- **Enterprise:** $15,000–$50,000/năm (giá trị cao nhất)

> **Break-even:** 3 deals Professional hoặc 1 deal Enterprise
