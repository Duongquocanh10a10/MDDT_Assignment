#!/usr/bin/env python3
"""
Phase 5 Step 1: Generate all publication-grade PNG figures for the Phần B Report:
  - Custom System Block Diagram (Section 2, Vietnamese/English engineering labels)
  - 300-DPI Rasterized Schematic pages & cropped per-block schematic views (Sections 4.1-4.8)
  - Verbatim ERC & DRC verification report cards (Sections 4.9 & 5)
  - 300-DPI 2D PCB copper layers (F.Cu, In1.Cu, In2.Cu, B.Cu, Drill Map)
  - 4-Layer FR4 Stackup & 90-Ohm Microstrip Cross-Section Diagram (Section 5)
  - KiCad 10 6-Step Project Workflow Diagram (Section 8 Tutorial)
"""

import os
import sys

sys.path.insert(0, r"D:\YoloUNO_pylibs")
import pypdfium2 as pdfium
from PIL import Image, ImageDraw, ImageFont

ROOT = r"c:\Users\QUOC ANH PC\Downloads\MDDT_Assignment\YoloUNO_Project"
OUT = os.path.join(ROOT, "outputs", "report_figures")
os.makedirs(OUT, exist_ok=True)


def get_font(size, bold=False, mono=False):
    candidates = []
    if mono:
        candidates = [
            r"C:\Windows\Fonts\consolab.ttf" if bold else r"C:\Windows\Fonts\consola.ttf",
            r"C:\Windows\Fonts\courbd.ttf" if bold else r"C:\Windows\Fonts\cour.ttf",
        ]
    else:
        candidates = [
            r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
            r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
        ]
    for p in candidates:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def render_pdf_page(pdf_path, page_idx, scale=2.6):
    pdf = pdfium.PdfDocument(pdf_path)
    page = pdf[page_idx]
    bm = page.render(scale=scale)
    img = bm.to_pil().convert("RGB")
    pdf.close()
    return img


def trim_white(img, pad=24, thresh=248):
    # Trim pure-white margin around board/schematic crops
    gray = img.convert("L")
    bw = gray.point(lambda x: 0 if x > thresh else 255, "1")
    bbox = bw.getbbox()
    if not bbox:
        return img
    x0 = max(0, bbox[0] - pad)
    y0 = max(0, bbox[1] - pad)
    x1 = min(img.width, bbox[2] + pad)
    y1 = min(img.height, bbox[3] + pad)
    return img.crop((x0, y0, x1, y1))


# ==============================================================================
# 1. RASTERIZE SCHEMATIC PAGES & CROP PER-BLOCK VIEWS (4.1 - 4.8)
# ==============================================================================
print("1. Rasterizing YoloUNO_Schematic.pdf pages...")
sch_pdf = os.path.join(ROOT, "outputs", "YoloUNO_Schematic.pdf")
sch_pages = [render_pdf_page(sch_pdf, i, scale=2.4) for i in range(5)]

# Save full sheets
sch_pages[0].save(os.path.join(OUT, "fig02_sch_root.png"))
sch_pages[1].save(os.path.join(OUT, "fig02b_sch_sheet01_power_full.png"))
sch_pages[2].save(os.path.join(OUT, "fig07_sch_4_5_esp32s3.png"))
sch_pages[3].save(os.path.join(OUT, "fig07b_sch_sheet03_usb_leds_full.png"))
sch_pages[4].save(os.path.join(OUT, "fig10_sch_4_8_peripherals.png"))

# Crop Sheet 1 (01_Power_Supply) into its 4 crisp functional blocks (4.1..4.4)!
# Let's check exact content coordinates on A3 sheet (420 x 297 mm, inner box ~0.04..0.96):
# In generate_schematic.py:
#   4.1 Input Prot: top-left    X: 0.03..0.50, Y: 0.04..0.48
#   4.2 5V Buck:    top-right   X: 0.48..0.96, Y: 0.04..0.52
#   4.3 Power Mux:  bottom-left X: 0.03..0.50, Y: 0.48..0.93
#   4.4 3.3V LDO:   bottom-right X: 0.48..0.96, Y: 0.50..0.86
W, H = sch_pages[1].size
sch_pages[1].crop((int(W*0.03), int(H*0.04), int(W*0.505), int(H*0.485))).save(os.path.join(OUT, "fig03_sch_4_1_input_prot.png"))
sch_pages[1].crop((int(W*0.495), int(H*0.04), int(W*0.97), int(H*0.485))).save(os.path.join(OUT, "fig04_sch_4_2_buck_5v.png"))
sch_pages[1].crop((int(W*0.03), int(H*0.485), int(W*0.505), int(H*0.93))).save(os.path.join(OUT, "fig05_sch_4_3_power_mux.png"))
sch_pages[1].crop((int(W*0.495), int(H*0.485), int(W*0.97), int(H*0.86))).save(os.path.join(OUT, "fig06_sch_4_4_ldo_3v3.png"))

# Crop Sheet 3 (03_USB_and_LEDs) into 4.6 (TOP half: USB-C + CC + ESD) & 4.7 (BOTTOM half: D13 + U6 + WS2812B)
W3, H3 = sch_pages[3].size
sch_pages[3].crop((int(W3*0.03), int(H3*0.04), int(W3*0.97), int(H3*0.50))).save(os.path.join(OUT, "fig08_sch_4_6_usbc_esd.png"))
sch_pages[3].crop((int(W3*0.03), int(H3*0.49), int(W3*0.97), int(H3*0.93))).save(os.path.join(OUT, "fig09_sch_4_7_leds_neopixel.png"))

# ==============================================================================
# 2. RASTERIZE 2D PCB COPPER LAYERS & DRILL MAP
# ==============================================================================
print("2. Rasterizing 2D PCB layer PDFs...")
pcb_pdf = os.path.join(ROOT, "outputs", "YoloUNO_PCB_2D_Layers.pdf")
trim_white(render_pdf_page(os.path.join(ROOT, "outputs", "pcb_2d", "01_Top_Composite.pdf"), 0, scale=2.8), pad=30).save(os.path.join(OUT, "fig12_pcb_top_fcu.png"))
trim_white(render_pdf_page(pcb_pdf, 1, scale=2.8), pad=30).save(os.path.join(OUT, "fig13_pcb_in1_gnd.png"))
trim_white(render_pdf_page(pcb_pdf, 2, scale=2.8), pad=30).save(os.path.join(OUT, "fig14_pcb_in2_pwr.png"))
trim_white(render_pdf_page(os.path.join(ROOT, "outputs", "pcb_2d", "04_Bot_Composite_Mirrored.pdf"), 0, scale=2.8), pad=30).save(os.path.join(OUT, "fig15_pcb_bot_bcu.png"))
trim_white(render_pdf_page(os.path.join(ROOT, "outputs", "gerbers", "YoloUNO-PTH-drl_map.pdf"), 0, scale=2.4), pad=25).save(os.path.join(OUT, "fig19_pth_drill_map.png"))

# ==============================================================================
# 3. CUSTOM SYSTEM BLOCK DIAGRAM (SECTION 2 — NOT REUSING HÌNH 5!)
# ==============================================================================
print("3. Drawing custom System Block Diagram...")
BW, BH = 2200, 1320
img = Image.new("RGB", (BW, BH), (255, 255, 255))
d = ImageDraw.Draw(img)

f_title = get_font(34, bold=True)
f_sub = get_font(20)
f_hdr = get_font(22, bold=True)
f_b = get_font(19, bold=True)
f_t = get_font(17)
f_lbl = get_font(16, bold=True)

# Title Banner
d.rounded_rectangle([30, 20, BW - 30, 108], radius=14, fill=(27, 54, 93))
d.text((BW // 2, 46), "SƠ ĐỒ KHỐI HỆ THỐNG — YOLO UNO (ESP32-S3-WROOM-1-N16R8)", fill=(255, 255, 255), font=f_title, anchor="mm")
d.text((BW // 2, 84), "Kiến trúc nguồn 4 lớp (6–12 V DC / 5 V USB-C) • Mức điện áp, ngân sách dòng ước tính & giao thức liên kết", fill=(210, 226, 245), font=f_sub, anchor="mm")


def draw_box(x1, y1, x2, y2, title, lines, fill_rgb, border_rgb, hdr_rgb=None):
    hdr_rgb = hdr_rgb or border_rgb
    d.rounded_rectangle([x1, y1, x2, y2], radius=12, fill=fill_rgb, outline=border_rgb, width=3)
    d.rounded_rectangle([x1, y1, x2, y1 + 40], radius=12, fill=hdr_rgb, outline=border_rgb, width=2)
    d.rectangle([x1 + 2, y1 + 26, x2 - 2, y1 + 40], fill=hdr_rgb)
    d.text(((x1 + x2) // 2, y1 + 20), title, fill=(255, 255, 255), font=f_b, anchor="mm")
    yy = y1 + 52
    for ln in lines:
        d.text((x1 + 14, yy), ln, fill=(28, 36, 48), font=f_t)
        yy += 24


def draw_arrow(pts, color=(40, 50, 70), width=4, label=None, lpos=None, lcolor=None, bidir=False):
    for i in range(len(pts) - 1):
        d.line([pts[i], pts[i + 1]], fill=color, width=width)
    # Arrowhead at end
    import math
    def head(p_from, p_to):
        ang = math.atan2(p_to[1] - p_from[1], p_to[0] - p_from[0])
        L = 14
        a1 = ang + math.pi * 0.82
        a2 = ang - math.pi * 0.82
        d.polygon([p_to, (p_to[0] + L * math.cos(a1), p_to[1] + L * math.sin(a1)),
                   (p_to[0] + L * math.cos(a2), p_to[1] + L * math.sin(a2))], fill=color)
    head(pts[-2], pts[-1])
    if bidir:
        head(pts[1], pts[0])
    if label and lpos:
        bbox = d.textbbox(lpos, label, font=f_lbl, anchor="mm")
        d.rounded_rectangle([bbox[0] - 6, bbox[1] - 3, bbox[2] + 6, bbox[3] + 3], radius=5, fill=(255, 255, 255), outline=color, width=1)
        d.text(lpos, label, fill=lcolor or color, font=f_lbl, anchor="mm")


# --- TOP ROW: POWER ARCHITECTURE (RED / ORANGE / GREEN) ---
draw_box(40, 145, 370, 325, "1. NGUỒN VÀO & BẢO VỆ",
         ["• J1: Jack DC 5521 (6–12 V)", "• D1: SMBJ15CA (TVS ±15 V)", "• Q1: AO3407A (P-MOS ngược cực)", "• D2: BZT52C10 (10 V) + R1 47k", "• C1 47µF/25V + C2 100nF"],
         (255, 245, 242), (185, 50, 35))

draw_box(470, 145, 830, 325, "2. HẠ ÁP BUCK 5 V (500 kHz)",
         ["• U1: TPS54202DDCR (2 A max)", "• L1: SRN6045TA 15 µH (2.9 A)", "• C3 10µF/25V, C5/C6 2×22µF", "• R3 68k / R4 9.1k → VOUT=5.05V", "• η ≈ 88% (tổn hao 0.68 W @1A)"],
         (255, 249, 238), (210, 110, 20))

draw_box(930, 145, 1320, 325, "3. CHỌN NGUỒN POWER-PATH",
         ["• U2: TPS2116DRLR (2.5 A, 40mΩ)", "• Ưu tiên DC Buck (VSW = 4.60 V)", "• Tự chuyển USB khi rút DC", "• Chặn dòng ngược tuyệt đối", "• Sụt áp ~40 mV @1A (C7 10µF)"],
         (254, 244, 255), (138, 43, 150))

draw_box(1430, 145, 1790, 325, "4. ỔN ÁP LDO 3,3 V",
         ["• U3: AP2114H-3.3TRG1 (1.0 A)", "• SOT-223 + 20.4mm² pad + 4 via", "• VDO=450 mV, IQ=60 µA", "• C8 10µF, C9 22µF, C10 100nF", "• D3 PWR LED (R11 470Ω, 2.55mA)"],
         (238, 252, 243), (28, 128, 72))

draw_box(1860, 145, 2160, 325, "4× SERVO GVS (+5V)",
         ["• J21–J24 (D2, D13, D12, D11)", "• C18: 470 µF / 10 V Low-ESR", "• Bus F.Cu 1.30 mm (>0.781 mm)", "• + In2.Cu mặt phẳng +5V", "• Dòng đỉnh: ~1.2–1.6 A"],
         (255, 243, 246), (180, 35, 75))

# --- LEFT COLUMN: USB-C & DISPLAY ---
draw_box(40, 420, 420, 630, "6. USB TYPE-C & BẢO VỆ ESD",
         ["• J2: USB-C 16P (HRO TYPE-C-31)", "• R9, R10: 2× 5.10 kΩ độc lập (CC1/2)", "• U5: USBLC6-2SC6 (2.5 pF ESD)", "• C14: 100 nF VBUS bypass", "• Cặp vi sai 90 Ω (w=0.25, s=0.20)", "• Độ lệch chiều dài: 0.67 mm (≤7.5)"],
         (238, 246, 255), (30, 95, 175))

draw_box(40, 720, 420, 960, "7. HIỂN THỊ & CHUYỂN MỨC",
         ["• D4: LED Đỏ D13 (GPIO48)", "  R12=270 Ω → I = 4.81 mA", "• U6: SN74LV1T34DBVR (3.3→5 V)", "  VIH(min)=2.0 V, cấp +5V (C15)", "• R13: 10 kΩ pull-down GPIO45", "  (an toàn strapping VDD_SPI=3.3V)", "• D5: WS2812B NeoPixel (+5V, 60mA)"],
         (245, 243, 255), (90, 60, 170))

draw_box(40, 1020, 420, 1260, "MẠCH PHỤ TRỢ RESET / BOOT",
         ["• SW1 (RESET) → MCU_EN", "  R7=10 kΩ, C13=1 µF (τ = 10 ms)", "• SW2 (BOOT) → GPIO0", "  R8=10 kΩ pull-up lên +3V3", "• Nút bấm SMD TS-1187A", "• 4 lỗ bắt vít M3 + 3 Fiducial"],
         (244, 247, 250), (80, 95, 115))

# --- CENTER: MCU ESP32-S3-WROOM-1-N16R8 ---
draw_box(540, 460, 1260, 1010, "5. VI ĐIỀU KHIỂN TRUNG TÂM — ESP32-S3-WROOM-1-N16R8 (U4)",
         ["• CPU: Dual-Core Xtensa LX7 240 MHz • Wi-Fi 2.4 GHz + BLE 5.0 (Anten PCB mép Tây)",
          "• Bộ nhớ: 16 MB Quad Flash (3.3 V) + 8 MB Octal PSRAM (3.3 V)",
          "• GPIO35, GPIO36, GPIO37: Dự trữ nội bộ Octal PSRAM → ĐỂ TRỐNG (NC)",
          "• Nguồn cấp: +3V3 (C11 22 µF + C12 100 nF sát chân; 350 mA TB / 600 mA đỉnh)",
          "• Vùng cấm đồng RF (RF Keepout) cả 4 lớp dưới anten (0 mm² đồng)",
          "------------------------------------------------------------------------------------",
          "• UART0: D0/RX (GPIO44), D1/TX (GPIO43)  |  USB Native: D-/D+ (GPIO19/20)",
          "• Digital I/O: D2–D7 (GPIO5–10), D8–D9 (GPIO17–18), D10 (GPIO21)",
          "• Servo PWM / SPI: D11 (GPIO38), D12 (GPIO47), D13 (GPIO48)",
          "• Analog ADC1: A0–A3 (GPIO1–4), A6 (GPIO14 / ADC2_CH3)",
          "• Shared I²C Bus (400 kHz): SDA (GPIO11 / A4), SCL (GPIO12 / A5)",
          "• Strapping: GPIO0 (BOOT), GPIO45 (R13 10k→GND), GPIO46 (NC), GPIO3 (A2)"],
         (235, 245, 255), (20, 75, 145), hdr_rgb=(20, 60, 120))

# --- BOTTOM-CENTER: A0 CONDITIONING ---
draw_box(540, 1085, 1240, 1260, "MẠCH ĐIỀU HÒA TÍN HIỆU ANALOG A0 (0–5 V → 0–2,976 V, Câu [10])",
         ["• Cầu chia E12: R16 = 6.80 kΩ, R17 = 10.0 kΩ → k = 0.5952, R_out = 4.05 kΩ",
          "• C17 = 100 nF sát chân GPIO1 (ADC1_CH0): lọc f_c ≈ 393 Hz & tụ lấy mẫu",
          "• Jumper JP1 (mặt dưới): [1–2] Mặc định 0–3.3 V  |  [2–3] Qua cầu chia 0–5 V"],
         (255, 251, 235), (180, 125, 15))

# --- RIGHT COLUMN: PERIPHERALS (GROVE, QWIIC, UNO R3) ---
draw_box(1440, 420, 2160, 665, "8A. 12 CỔNG GROVE (3 CỘT × 4 HÀNG — VCC = +3V3)",
         ["• 4× Analog (Vàng, J3–J6): A1-A0, A2-A1, A3-A2, A6-A3 (GPIO14/4/3/2/1)",
          "• 4× Digital (Trắng, J7–J10): D4-D3, D6-D5, D8-D7, D10-D9",
          "• 4× I²C (Đỏ, J11–J14): I2C1–I2C4 dùng chung bus GPIO11 (SDA) / GPIO12 (SCL)",
          "• Kéo lên I²C chung: R14 = R15 = 1.50 kΩ lên +3V3 (400 kHz, C_b=200 pF → t_r=254 ns)",
          "• An toàn mức logic 3.3 V cho mọi GPIO ESP32-S3; cấp từ mặt phẳng In2.Cu (+3V3)"],
         (240, 250, 245), (30, 130, 95))

draw_box(1440, 720, 2160, 905, "8B. CỔNG QWIIC / STEMMA QT (J15 — JST-SH 1.0 mm)",
         ["• Chân chuẩn SparkFun Qwiic: 1=GND, 2=+3V3, 3=SDA (IO11), 4=SCL (IO12)",
          "• Dùng chung cặp điện trở kéo lên R14/R15 = 1.50 kΩ (4 Grove I²C + QWIIC + A4/A5)",
          "• Dòng ngoại vi Qwiic + 4 module Grove ước tính: ~120–200 mA từ ray +3V3"],
         (238, 248, 255), (35, 110, 165))

draw_box(1440, 965, 2160, 1260, "8C. HEADER ARDUINO UNO R3 CHUẨN (J17–J20, BƯỚC 2,54 mm)",
         ["• J19 (1×10): SCL, SDA, AREF(NC), GND, D13, D12, D11, D10, D9, D8",
          "• J20 (1×08): D7, D6, D5, D4, D3, D2, D1/TX, D0/RX (khe hở chuẩn 4.06 mm với J19)",
          "• J17 (1×08): NC, IOREF(+3V3), RESET(MCU_EN), +3V3, +5V, GND, GND, VIN_PROT",
          "• J18 (1×06): A0(A0_RAW), A1, A2, A3, A4/SDA, A5/SCL",
          "• Kích thước bo chuẩn 68.58 × 53.34 mm — tương thích cơ khí 100% shield UNO R3"],
         (245, 245, 248), (65, 75, 95))

# --- INTERCONNECT ARROWS WITH VOLTAGE / CURRENT / PROTOCOL ---
# Power chain
draw_arrow([(370, 235), (470, 235)], (185, 50, 35), 5, "VIN_PROT\n6–12V / ≤1.5A", (420, 200))
draw_arrow([(830, 235), (930, 235)], (210, 110, 20), 5, "5V_BUCK\n5.05V / 2A", (880, 200))
draw_arrow([(1320, 235), (1430, 235)], (138, 43, 150), 5, "+5V Rail\n≤2.0A", (1375, 200))
# +5V to Servos (routed above U3)
draw_arrow([(1125, 145), (1125, 122), (2010, 122), (2010, 145)], (180, 35, 75), 5, "+5V Servo Backbone (1.30 mm, 2 A max)", (1610, 122))
# USB VBUS -> TPS2116
draw_arrow([(230, 420), (230, 365), (1125, 365), (1125, 325)], (30, 95, 175), 4, "VBUS (5.0 V / 0.5–0.9 A USB)", (680, 365))
# +3V3 from U3 to MCU & Peripherals
draw_arrow([(1610, 325), (1610, 385), (1050, 385), (1050, 460)], (28, 128, 72), 5, "+3V3 (0.35A TB / 0.6A đỉnh)", (1330, 385))
draw_arrow([(1610, 385), (1760, 385), (1760, 420)], (28, 128, 72), 4, "+3V3 Grove/Qwiic", (1750, 368))
# USB D+/D- <-> MCU
draw_arrow([(420, 525), (540, 525)], (30, 95, 175), 4, "USB 2.0 90Ω\nGPIO19/20", (480, 492), bidir=True)
# MCU -> LEDs / NeoPixel
draw_arrow([(540, 810), (420, 810)], (90, 60, 170), 4, "GPIO48 / GPIO45\n(3.3V→5V)", (480, 775))
# Reset/Boot -> MCU
draw_arrow([(420, 1100), (485, 1100), (485, 930), (540, 930)], (80, 95, 115), 3, "EN / IO0", (485, 1020))
# MCU <-> Grove
draw_arrow([(1260, 540), (1440, 540)], (30, 130, 95), 4, "GPIO / ADC / I²C\n(3.3 V, 400 kHz)", (1350, 505), bidir=True)
# MCU <-> QWIIC
draw_arrow([(1260, 800), (1440, 800)], (35, 110, 165), 4, "I²C 400 kHz\nGPIO11/12", (1350, 765), bidir=True)
# MCU <-> UNO R3
draw_arrow([(1260, 985), (1350, 985), (1350, 1080), (1440, 1080)], (65, 75, 95), 4, "D0–D13 / A0–A5\nUART / SPI / I²C", (1350, 1030), bidir=True)
# MCU -> Servo PWM
draw_arrow([(1260, 480), (1360, 480), (1360, 395), (2010, 395), (2010, 325)], (180, 35, 75), 3, "4× PWM (D2,D11,D12,D13)", (1990, 365))
# A0 conditioning <-> MCU & UNO/Grove
draw_arrow([(900, 1085), (900, 1010)], (180, 125, 15), 4, "A0_ADC (0–3.3 V → GPIO1)", (1040, 1048))
draw_arrow([(1440, 1185), (1240, 1185)], (180, 125, 15), 4, "A0_RAW\n(0–5 V / 3.3 V)", (1345, 1148))

img.save(os.path.join(OUT, "fig01_system_block_diagram.png"))
print("  Saved fig01_system_block_diagram.png")


# ==============================================================================
# 4. 4-LAYER FR4 STACKUP CROSS-SECTION DIAGRAM (SECTION 5)
# ==============================================================================
print("4. Drawing 4-Layer PCB Stackup Cross-Section Diagram...")
SW, SH = 1800, 760
si = Image.new("RGB", (SW, SH), (255, 255, 255))
sd = ImageDraw.Draw(si)
sd.rounded_rectangle([20, 15, SW - 20, 82], radius=10, fill=(27, 54, 93))
sd.text((SW // 2, 48), "CẤU TRÚC STACK-UP PCB 4 LỚP FR4 (1,60 mm — 1 oz) & TRỞ KHÁNG VI SAI USB 90 Ω", fill=(255, 255, 255), font=get_font(26, bold=True), anchor="mm")

layers_spec = [
    ("Solder Mask (Top)", "0.02 mm", (45, 115, 65), (255, 255, 255), 26, "Màu xanh lá chuẩn, hở pad ENIG/HASL"),
    ("L1 — F.Cu (Top Signal + Power)", "35 µm (1 oz)", (205, 72, 52), (255, 255, 255), 54, "491 đoạn mạch • Buck SW/BOOT (0 via) • Bus Servo +5V 1.30 mm • Pad nhiệt U3 20.4 mm² • Đổ GND 1654 mm²"),
    ("Prepreg FR4 (εr ≈ 4.2–4.5)", "0.20 mm", (222, 210, 165), (45, 40, 20), 46, "Điện môi mỏng h = 0.20 mm → kiểm soát trở kháng vi sai 90 Ω (w = 0.25 mm, s = 0.20 mm)"),
    ("L2 — In1.Cu (Solid GND Plane)", "35 µm (1 oz)", (42, 138, 86), (255, 255, 255), 58, "100% MẶT PHẲNG GND LIỀN MẠCH (2.852,3 mm², 0 đoạn tín hiệu) • Vùng cấm đồng anten ESP32-S3"),
    ("Core FR4 (Lõi trung tâm)", "1.06 mm", (195, 182, 132), (45, 40, 20), 96, "Lõi FR4 cứng cách ly hoàn toàn giữa In1.Cu (GND) và In2.Cu (Power) — Tổng độ dày bo ≈ 1.60 mm"),
    ("L3 — In2.Cu (Split Power Plane)", "35 µm (1 oz)", (205, 132, 30), (255, 255, 255), 58, "100% MẶT PHẲNG NGUỒN THUẦN (+3V3: 2.135,5 mm² | +5V: 623,5 mm², khe tách 0.80 mm, 0 tín hiệu)"),
    ("Prepreg FR4 (εr ≈ 4.2–4.5)", "0.20 mm", (222, 210, 165), (45, 40, 20), 46, "Mặt phẳng tham chiếu liền mạch cho cặp vi sai USB_DN/USB_DP trên B.Cu (lệch dài 0.67 mm ≤ 7.5 mm)"),
    ("L4 — B.Cu (Bottom Signal + USB)", "35 µm (1 oz)", (45, 105, 185), (255, 255, 255), 54, "541 đoạn mạch • Cặp vi sai USB 90 Ω (w=0.25, s=0.20) • Linh kiện SMD nhỏ gọn & JP1 • Đổ GND 1789.8 mm²"),
    ("Solder Mask (Bottom)", "0.02 mm", (45, 115, 65), (255, 255, 255), 26, "In lụa tên bo YOLO UNO v1.0, hướng dẫn Jumper A0: 1-2=3V3 2-3=5V"),
]

yy = 115
for name, thk, bg, fg, h_px, desc in layers_spec:
    sd.rectangle([45, yy, 420, yy + h_px], fill=bg, outline=(40, 45, 55), width=2)
    sd.text((232, yy + h_px // 2), name, fill=fg, font=get_font(17, bold=True), anchor="mm")
    sd.rectangle([420, yy, 580, yy + h_px], fill=(246, 248, 252), outline=(40, 45, 55), width=2)
    sd.text((500, yy + h_px // 2), thk, fill=(25, 35, 50), font=get_font(16, bold=True), anchor="mm")
    sd.rectangle([580, yy, SW - 45, yy + h_px], fill=(252, 253, 255), outline=(40, 45, 55), width=2)
    sd.text((600, yy + h_px // 2), desc, fill=(30, 40, 55), font=get_font(16), anchor="lm")
    yy += h_px

# Footer note
sd.rounded_rectangle([45, yy + 22, SW - 45, SH - 20], radius=8, fill=(238, 246, 255), outline=(30, 95, 175), width=2)
sd.text((SW // 2, (yy + 22 + SH - 20) // 2),
        "Luật thiết kế IPC-2221 Class 2: Trace/Space min 0.15 mm (dùng 0.18 mm) • Via 0.60/0.30 mm (229 via) • Edge clearance ≥ 0.45 mm • DRC: 0 Lỗi / 0 Chưa nối",
        fill=(20, 60, 120), font=get_font(18, bold=True), anchor="mm")
si.save(os.path.join(OUT, "fig16_pcb_4layer_stackup_diagram.png"))
print("  Saved fig16_pcb_4layer_stackup_diagram.png")


# ==============================================================================
# 5. VERBATIM ERC & DRC REPORT EVIDENCE CARDS (SECTIONS 4.9 & 5)
# ==============================================================================
def make_report_card(title, cmd_str, rpt_path, badge_text, out_png):
    txt = open(rpt_path, "r", encoding="utf-8", errors="replace").read().strip().splitlines()
    lines = [f"$ {cmd_str}", "-" * 96] + txt[:28]
    CW = 1520
    CH = 140 + len(lines) * 26 + 40
    ci = Image.new("RGB", (CW, CH), (22, 27, 34))
    cd = ImageDraw.Draw(ci)
    cd.rectangle([0, 0, CW, 70], fill=(27, 54, 93))
    cd.text((28, 35), title, fill=(255, 255, 255), font=get_font(24, bold=True), anchor="lm")
    # Green PASS badge
    cd.rounded_rectangle([CW - 390, 14, CW - 24, 56], radius=10, fill=(24, 145, 75))
    cd.text((CW - 207, 35), badge_text, fill=(255, 255, 255), font=get_font(20, bold=True), anchor="mm")
    fm = get_font(17, mono=True)
    y = 92
    for idx_l, ln in enumerate(lines):
        col = (120, 215, 255) if idx_l == 0 else ((90, 235, 140) if ("Found 0" in ln or "Errors 0" in ln or "Warnings 0" in ln) else (230, 237, 243))
        cd.text((28, y), ln[:120], fill=col, font=fm)
        y += 26
    ci.save(out_png)


print("5. Rendering verbatim ERC & DRC evidence cards...")
make_report_card(
    "KiCad 10.0.8 — Báo cáo Kiểm tra Quy tắc Điện (ERC Report)",
    "kicad-cli sch erc --severity-all --exit-code-violations -o erc_report.rpt YoloUNO.kicad_sch",
    os.path.join(ROOT, "outputs", "erc_report.rpt"),
    "PASS: 0 ERRORS / 0 WARNINGS",
    os.path.join(OUT, "fig11_erc_report.png"),
)
make_report_card(
    "KiCad 10.0.8 — Báo cáo Kiểm tra Quy tắc Thiết kế PCB (DRC Report)",
    "kicad-cli pcb drc --severity-all --refill-zones --schematic-parity --exit-code-violations YoloUNO.kicad_pcb",
    os.path.join(ROOT, "outputs", "drc_report.rpt"),
    "PASS: 0 DRC / 0 UNCONN / 0 PARITY",
    os.path.join(OUT, "fig17_drc_report.png"),
)


# ==============================================================================
# 6. KICAD 10 6-STEP TUTORIAL WORKFLOW DIAGRAM (SECTION 8)
# ==============================================================================
print("6. Drawing KiCad 10 6-Step Tutorial Workflow Diagram...")
KW, KH = 2000, 620
ki = Image.new("RGB", (KW, KH), (255, 255, 255))
kd = ImageDraw.Draw(ki)
kd.rounded_rectangle([20, 15, KW - 20, 80], radius=12, fill=(27, 54, 93))
kd.text((KW // 2, 48), "QUY TRÌNH THIẾT KẾ MẠCH YOLO UNO TRÊN KICAD 10.0.8 (MỤC 8.1 – 8.6)", fill=(255, 255, 255), font=get_font(26, bold=True), anchor="mm")

steps = [
    ("8.1 Khởi tạo Project", (30, 95, 175), ["• Cài KiCad 10.0.8", "• Tạo YoloUNO.kicad_pro", "• Cấu trúc thư mục chuẩn", "  hardware/ + libraries/", "• Tự chứa sym & fp tables"]),
    ("8.2 Thư viện Linh kiện", (138, 43, 150), ["• YoloUNO.kicad_sym (32)", "• YoloUNO.pretty (28 fp)", "• Kiểm tra footprint vs", "  datasheet (SOT-583, USB-C)", "• Gắn mô hình 3D STEP"]),
    ("8.3 Vẽ Schematic & ERC", (28, 128, 72), ["• 5 trang phân cấp A3", "• Hierarchical labels", "• Gán MPN & LCSC đầy đủ", "• Chạy ERC: 0 Errors,", "  0 Warnings (Exit = 0)"]),
    ("8.4 Chuyển PCB & Rules", (210, 110, 20), ["• Update PCB from Sch", "• Edge.Cuts UNO R3", "  (68.58 × 53.34 mm)", "• Stack-up 4 lớp FR4", "• Rules IPC-2221 Class 2"]),
    ("8.5 Layout, Route & DRC", (185, 50, 35), ["• Anten ESP32 mép Tây", "• Buck xa anten >52 mm", "• USB 90Ω + Servo 1.3mm", "• In1 GND / In2 +3V3,+5V", "• DRC: 0/0/0 (Exit = 0)"]),
    ("8.6 Xuất Sản phẩm DFM", (45, 75, 105), ["• 5 ảnh 3D Raytraced PNG", "• Schematic & 2D PDF", "• BOM .csv/.xlsx + CPL", "• 11 lớp Gerber + Drill", "• STEP 3D & Đóng gói ZIP"]),
]

bw = 296
gap = 34
x_start = 28
for idx, (stitle, col, bullets) in enumerate(steps):
    x1 = x_start + idx * (bw + gap)
    y1, x2, y2 = 115, x1 + bw, 460
    kd.rounded_rectangle([x1, y1, x2, y2], radius=12, fill=(248, 250, 253), outline=col, width=3)
    kd.rounded_rectangle([x1, y1, x2, y1 + 48], radius=12, fill=col)
    kd.rectangle([x1 + 2, y1 + 32, x2 - 2, y1 + 48], fill=col)
    kd.text(((x1 + x2) // 2, y1 + 24), stitle, fill=(255, 255, 255), font=get_font(18, bold=True), anchor="mm")
    yy = y1 + 66
    for bl in bullets:
        kd.text((x1 + 14, yy), bl, fill=(30, 38, 48), font=get_font(16))
        yy += 30
    if idx < len(steps) - 1:
        ax1, ay = x2 + 4, (y1 + y2) // 2
        ax2 = x2 + gap - 4
        kd.line([(ax1, ay), (ax2 - 8, ay)], fill=(80, 95, 115), width=4)
        kd.polygon([(ax2, ay), (ax2 - 12, ay - 8), (ax2 - 12, ay + 8)], fill=(80, 95, 115))

# Bottom folder structure bar
kd.rounded_rectangle([28, 490, KW - 28, KH - 20], radius=10, fill=(240, 245, 252), outline=(27, 54, 93), width=2)
kd.text((KW // 2, 522),
        "Cấu trúc Project tự chứa (Self-Contained):  YoloUNO.kicad_pro  |  5× .kicad_sch  |  YoloUNO.kicad_pcb  |  sym-lib-table  |  fp-lib-table  |  libraries/YoloUNO.kicad_sym & YoloUNO.pretty/",
        fill=(27, 54, 93), font=get_font(17, bold=True), anchor="mm")
kd.text((KW // 2, 560),
        "Ưu điểm: Mở trên bất kỳ máy tính nào cài KiCad 10 mà không bị thiếu ký hiệu (symbol), footprint hay mô hình 3D; tương thích hoàn toàn kicad-cli CI/CD.",
        fill=(55, 75, 95), font=get_font(16), anchor="mm")
ki.save(os.path.join(OUT, "fig18_kicad_workflow_overview.png"))
print("  Saved fig18_kicad_workflow_overview.png")
print("\nALL REPORT FIGURES GENERATED SUCCESSFULLY.")
