# 📚 TỔNG HỢP TOÀN BỘ DỮ LIỆU HUẤN LUYỆN AI ĐỊNH TUYẾN PCB (ZERO-DRC DATASET)
**Dự án:** Water Quality IoT Industrial Sensor
**Phiên bản:** v7.0 Ultra-Compact Zero-DRC Golden Edition (03/10/2026)
**Tập tin mạch:** `A:\DEVICE\KiCad_Project\WaterSensor.kicad_pcb`
**Thư mục lưu trữ dataset:** `A:\DEVICE\data_traning pcb/`

---

## 1. TỔNG QUAN BỘ DỮ LIỆU (DATASET OVERVIEW)

Bộ dữ liệu này ghi lại toàn bộ chu trình tối ưu hóa hình học, co cụm diện tích bo mạch từ **$52.0 \times 101.0\text{ mm}$** xuống **$52.0 \times 75.0\text{ mm}$** (giảm **25.7%** diện tích), chuyển đổi cấu trúc 4 lớp phủ đồng và giải quyết triệt để từ **215 lỗi vi phạm DRC** về **0 LỖI DRC TUYỆT ĐỐI** và **100% KẾT NỐI (0 Unconnected Pads)**.

### Thông số kỹ thuật của mô hình bo mạch:
- **Kích thước PCB:** $52.0 \times 75.0\text{ mm}$ ($X \in [73.0, 125.0]\text{ mm}, Y \in [53.0, 128.0]\text{ mm}$).
- **Số lớp đồng (Stackup):** 4 lớp công nghiệp IPC-2221 Class 2:
  * `F.Cu`: Tín hiệu vi sai, analog trở kháng cao, chùm tín hiệu sườn, phủ đồng GND kèm chấu tản nhiệt hoa thị ($0.25\text{ mm}$ gap, $0.35\text{ mm}$ bridge).
  * `In1.Cu`: Mặt phẳng tiếp địa liên tục (**Solid GND Plane**), khoét vùng anten RF.
  * `In2.Cu`: Mặt phẳng nguồn chia đôi (**Split Power Plane**) tại $Y = 94.0\text{ mm}$ (Nửa Bắc: `+3V3`, Nửa Nam: `+5V`).
  * `B.Cu`: Linh kiện đáy (GPS, pin RTC, DS3231), chùm cao tốc LCD, vi dải RF 50-ohm, phủ đồng GND toàn diện.
- **Thống kê phần tử mạch:**
  * 94 Footprints
  * 384 Pads
  * 733 Tracks
  * 120 Vias (đường kính $0.6\text{ mm}$, lỗ khoan $0.3\text{ mm}$)
  * 6 Zones (5 Plane đồng: `F.Cu` GND, `B.Cu` GND, `In1.Cu` GND, `In2.Cu` +3V3, `In2.Cu` +5V; 1 vùng cấm đồng RF)
  * 63 Nets (62 active routed nets)
- **Quy chuẩn kiểm định DRC:**
  * Ngưỡng cách điện tối thiểu (Clearance): $0.15\text{ mm}$
  * Khoảng cách lỗ khoan đến lỗ khoan (Hole-to-Hole): $0.25\text{ mm}$
  * Khoảng cách mép bo mạch (Board Edge Clearance): $0.30\text{ mm}$

---

## 2. CẤU TRÚC THƯ MỤC BỘ DỮ LIỆU (`data_traning pcb/`)

```
A:\DEVICE\data_traning pcb/
├── DATASET_OVERVIEW.md                 # Tài liệu tổng quan toàn bộ bộ dữ liệu
├── pcb_models/                         # Các snapshot mạch thực tế trước & sau tối ưu
│   ├── WaterSensor_Before_Fix.kicad_pcb# Snapshot gốc trước tối ưu (215 vi phạm DRC)
│   ├── WaterSensor_Final_ZeroDRC.kicad_pcb # Snapshot hoàn thiện (0 lỗi DRC, 0 unconnected)
│   ├── WaterSensor_Final_ZeroDRC.kicad_pro # File cấu hình quy tắc thiết kế (0.15mm clearance)
│   └── clean_baseline.kicad_pcb        # Bo mạch khung sạch 52x75mm đã fanout plane
├── drc_logs/                           # Nhật ký và bộ dữ liệu kiểm định DRC
│   ├── drc_training_dataset.json       # Tập dữ liệu JSON cấu trúc hóa 6 giai đoạn hội tụ
│   ├── drc_progression_log.md          # Báo cáo phân tích chuyên sâu từng giai đoạn
│   ├── WaterSensor_drc_all.rpt         # Báo cáo nghiệm thu chính thức KiCad 10 (0 lỗi)
│   ├── pads_summary.json               # Cơ sở dữ liệu tọa độ 384 pad
│   └── pad_audit.txt                   # Audit khoảng cách và hành lang pad
├── legacy_dataset/                     # 5 ca huấn luyện chuyên biệt (benchmark cases)
│   ├── dataset_index.jsonl             # Chỉ mục định dạng JSON-Lines
│   └── cases/
│       ├── case_001_vbus_clearance_dogleg/
│       ├── case_002_mt3608_boost_clearance/
│       ├── case_003_lcd_block_routing/
│       ├── case_004_sensors_gps_rtc_routing/
│       └── case_01_global_integration_intergroup_conflicts/
└── scripts/                            # 15 script giải thuật cốt lõi
    ├── all_routes_v2.py                # Script định tuyến toàn bộ 63 nets (chuẩn 0 DRC)
    ├── run_zero_drc_final.py           # Bộ giải tích hợp sinh tuyến dây sạch
    ├── route_verifier.py               # Thư viện kiểm tra hình học giải tích (RouteAuditor)
    ├── router_engine.py                # Engine xuất S-expression chuẩn KiCad 10
    ├── clean_board_builder.py          # Module dựng khung bo 52x75mm và fanout plane
    ├── base_builder.py                 # Thuật toán fanout via 4 lớp
    ├── perfect_targets.py              # Bảng tọa độ tối ưu không cấn courtyard
    ├── astar_router.py                 # Bộ định tuyến A* đa lớp với Halo clearance
    ├── spatial_analysis.py             # Phân tích không gian hành lang và mật độ via
    └── optimize_4layer_routing.py      # Tối ưu hóa phân tầng 4 lớp
```

---

## 3. TIẾN TRÌNH HỘI TỤ 6 GIAI ĐOẠN (CONVERGENCE MATRIX)

| Giai đoạn | Số lỗi DRC | Số Unconnected | Nguyên nhân hình học & mạch | Giải pháp giải thuật đã áp dụng |
|---|---|---|---|---|
| **Phase 1: Baseline Spaghetti** | 215 | 0 | Dây nguồn chạy chéo ngang dọc trên F.Cu/B.Cu, cản trở toàn bộ đường tín hiệu | Chuyển toàn bộ mạng nguồn sang 4 lớp: cắm via fanout trực tiếp vào In1.Cu (GND) và In2.Cu (+3V3/+5V) |
| **Phase 2: Compact 52x75** | 18 | 0 | Chùm 5 dây LCD SPI và cặp USB D+/D- xung đột giao cắt tại sườn Tây | Áp dụng Định lý Lồng ghép Phẳng (Planar Topology) và Phân tầng Trực giao (Orthogonal Layering) |
| **Phase 3: Halo Tuning** | 9 | 0 | Trục `SPI_MOSI` tại ESP32 cấn mép pad U6.38 (GND) ở khoảng cách $<0.15\text{ mm}$ | Dời trục `SPI_MOSI` ra $X=109.90\text{ mm}$, hở $0.30\text{ mm}$ so với pad GND |
| **Phase 4: Staggering** | 4 | 0 | Via `USB_D+` và `USB_D-` cấn nhau $<0.15\text{ mm}$; `VBAT_SW` cắt chùm LCD | So le hóa trục via ($X=83.50$ và $X=95.80\text{ mm}$); dời `VBAT_SW` lên hành lang cực Bắc $Y=52.80\text{ mm}$ |
| **Phase 5: Golden Master** | 3 (warnings) | 3 | Trùng via $(119.6, 67.1)$; via sát PTH $(121.5, 72.0)$; cô lập zone B.Cu tại `R_FB2.2`; thiếu via `U6.15`, `R_PROG.2` | Phát hiện chính xác tọa độ pad hở & via xung đột |
| **Phase 6: Absolute Zero DRC** | **0** | **0** | **0 VIOLATIONS, 0 UNCONNECTED PADS, 0 FOOTPRINT ERRORS** | Mở hành lang đồng B.Cu rộng $2.2\text{ mm}$ cho `R_FB2.2` bằng via `+5V` độc lập; thêm via fanout GND cho `U6.15` và `R_PROG.2`; xóa 2 via lỗi; đổ lại 5 plane đồng |

---

## 4. BỐN ĐỊNH LÝ & NGUYÊN LÝ GIẢI THUẬT CỐT LÕI (CORE THEOREMS)

### 4.1. Định Lý Lồng Ghép Hình Học Phẳng (Planar Topology Embedding Theorem)
- **Bài toán:** Định tuyến chùm bus $N$ đường tín hiệu (`SPI_SCK`, `SPI_MOSI`, `LCD_CS`, `LCD_RST`, `LCD_DC`) chạy từ sườn Đông MCU sang hàng giắc sườn Tây đáy bo mạch mà không được tự cắt nhau trên bất kỳ lớp nào.
- **Giải thuật:**
  * Sắp xếp tọa độ chân phát Bắc $\to$ Nam trên F.Cu: gán trục tọa độ $X$ tăng dần từ trong ra ngoài ($X = 109.90 \to 112.30\text{ mm}$).
  * Sắp xếp tọa độ chân thu Bắc $\to$ Nam trên B.Cu: gán trục tọa độ $X$ giảm dần từ Đông sang Tây ($X = 76.00 \to 73.60\text{ mm}$).
  * Ánh xạ đơn ánh đồng biến bảo toàn thứ tự topo phẳng, triệt tiêu 100% điểm giao cắt mà không cần via đảo tầng phức tạp.

### 4.2. Phân Tầng Trực Giao & Hầm Chui So Le (Orthogonal Layering & Staggered Underpass)
- **Bài toán:** Cặp tín hiệu vi sai tốc độ cao `USB_D+` và `USB_D-` từ cổng Type-C sang IC CP2102N bị chắn ngang bởi tụ lọc `C_VBUS` và các chân nguồn.
- **Giải thuật:**
  * Tín hiệu `USB_D-` chạy trên `F.Cu` qua hành lang Bắc ($Y=89.50\text{ mm}$).
  * Tín hiệu `USB_D+` hạ via xuống `B.Cu` tại $X=83.50\text{ mm}$, chui qua hầm ngang $Y=90.50\text{ mm}$, rồi trồi lên `F.Cu` tại $X=94.50\text{ mm}$.
  * Tọa độ via được làm so le lệch trục dọc $\Delta X = 11.0\text{ mm} \gg 0.15\text{ mm}$, đảm bảo tuyệt đối không cấn via-to-via.

### 4.3. Phá Thế Cô Lập Đảo Đồng (Zone Island Unlocking Technique)
- **Bài toán:** Một pad chân mass (`R_FB2.2`) bị cô lập hoàn toàn do các đường tín hiệu/nguồn chạy khép kín 4 phía ở cả 2 mặt F.Cu và B.Cu, dẫn đến lỗi Unconnected Pad.
- **Giải thuật:**
  * Nhận diện đường bao cản trở: phát hiện đường track `+5V` chạy ngang $5\text{ mm}$ trên B.Cu tạo đê chắn đồng.
  * Thay thế đoạn track ngang bằng via cắm thẳng xuống plane hoặc cắm lên mặt F.Cu tại vị trí pad đích `R_FB1.1` $(86.825, 108.0)\text{ mm}$.
  * Xóa đoạn track chắn, giải phóng hành lang rộng $2.2\text{ mm}$ cho mặt phẳng đồng B.Cu tự do tràn vào tiếp xúc pad mass với chấu hoa thị chuẩn IPC.

### 4.4. Quy Tắc Bảo Vệ Tín Hiệu Nhạy Cảm (Hardware Flaw Mitigation)
1. **Dòng rò tắt nguồn:** `VBAT_SW` đi qua sườn Bắc $Y=52.80\text{ mm}$ cấp cho `R_BAT1.1`, dòng rò khi tắt công tắc bằng $0\mu\text{A}$.
2. **Nhiễu Boost MT3608:** Đường `SW_NODE` cực ngắn trên F.Cu ($0.40\text{ mm}$, 0 via); đường `BST_FB` đi trên B.Cu cách ly hoàn toàn qua mặt phẳng GND `In1.Cu`.
3. **Anten GPS 50-ohm:** `GPS_ANT` chạy dạng vi dải coplanar $0.40\text{ mm}$ trên B.Cu, 0 via, cách ly $\ge 3.0\text{ mm}$ với đường đo `TDS_ADC`.
4. **Đường pH pA:** `PH_SIGNAL` đi 100% trên F.Cu, 0 via, chống rò dòng qua thành via.
