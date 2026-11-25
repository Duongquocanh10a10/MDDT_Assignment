#!/usr/bin/env python3
"""
Phase 5 Step 2: Generate Complete Vietnamese Phần B Report (.docx) for HCMUT CO2037 Project 1
Students: Dương Quốc Anh (2410053) & Hoàng Trọng Đại (2510284) | Class: L02 | Lecturer: Nguyễn Văn Hiếu
Includes:
  - Cover page & Table 5 (Group Info)
  - Sections 1 to 11 + Appendices A, B, C strictly following Phần B template
  - Embedded high-res custom block diagram, 8 cropped schematic blocks, ERC/DRC evidence cards,
    4-layer stackup diagram, all 4 2D copper layers, 5 raytraced 3D views, and PTH drill map
  - Complete mathematical derivations for Questions [1]–[13]
  - Comprehensive 4–8 page KiCad 10.0.8 step-by-step tutorial (Section 8)
  - Transparent AI Usage Log (Section 9) & Work Division Table (Section 10)
"""

import os
import sys
import csv

sys.path.insert(0, r"D:\YoloUNO_pylibs")
import docx
from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn, nsdecls

ROOT = r"c:\Users\QUOC ANH PC\Downloads\MDDT_Assignment\YoloUNO_Project"
FIG_DIR = os.path.join(ROOT, "outputs", "report_figures")
R3D_DIR = os.path.join(ROOT, "outputs", "3d_renders")
BOM_CSV = os.path.join(ROOT, "outputs", "bom", "YoloUNO_BOM_Final.csv")
OUT_DIR = os.path.join(ROOT, "outputs", "report")
os.makedirs(OUT_DIR, exist_ok=True)
OUT_DOCX = os.path.join(OUT_DIR, "2410053_2510284_BaoCao_Project1_YoloUNO.docx")

NAVY = RGBColor(0x1B, 0x36, 0x5D)
BLUE = RGBColor(0x1E, 0x5F, 0xAF)
DARK = RGBColor(0x1F, 0x29, 0x37)
MUTED = RGBColor(0x4B, 0x55, 0x63)
GREEN = RGBColor(0x16, 0x7A, 0x45)

doc = docx.Document()

# Page setup: A4, clean 2.0 cm margins
for sec in doc.sections:
    sec.page_width = Cm(21.0)
    sec.page_height = Cm(29.7)
    sec.top_margin = Cm(2.0)
    sec.bottom_margin = Cm(2.0)
    sec.left_margin = Cm(2.2)
    sec.right_margin = Cm(2.0)
    sec.different_first_page_header_footer = True

# Configure base Normal style (Times New Roman / Calibri clean academic Vietnamese typography)
normal = doc.styles["Normal"]
normal.font.name = "Calibri"
normal.font.size = Pt(11)
normal.font.color.rgb = DARK
normal.paragraph_format.space_after = Pt(5)
normal.paragraph_format.line_spacing = 1.15

# Running header & page-number footer (starting page 2)
sec0 = doc.sections[0]
hdr_p = sec0.header.paragraphs[0]
hdr_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
r_h = hdr_p.add_run("CO2037 — Dự án 1: Thiết kế lại bo mạch Yolo UNO (ESP32-S3)  |  L02 — 2410053 & 2510284")
r_h.font.name = "Calibri"
r_h.font.size = Pt(9)
r_h.font.italic = True
r_h.font.color.rgb = MUTED

ftr_p = sec0.footer.paragraphs[0]
ftr_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r_f1 = ftr_p.add_run("Trường ĐH Bách khoa – ĐHQG-HCM  |  Trang ")
r_f1.font.size = Pt(9)
r_f1.font.color.rgb = MUTED
fld = OxmlElement("w:fldSimple")
fld.set(qn("w:instr"), "PAGE")
ftr_p._p.append(fld)
r_f2 = ftr_p.add_run(" / ")
r_f2.font.size = Pt(9)
r_f2.font.color.rgb = MUTED
fld2 = OxmlElement("w:fldSimple")
fld2.set(qn("w:instr"), "NUMPAGES")
ftr_p._p.append(fld2)


# ==============================================================================
# HELPER FUNCTIONS FOR CLEAN STYLING
# ==============================================================================
def set_cell_shading(cell, hex_color):
    shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    cell._tc.get_or_add_tcPr().append(shading)


def set_cell_margins(cell, top=80, bottom=80, left=110, right=110):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement("w:tcMar")
    for m, val in [("top", top), ("bottom", bottom), ("left", left), ("right", right)]:
        node = OxmlElement(f"w:{m}")
        node.set(qn("w:w"), str(val))
        node.set(qn("w:type"), "dxa")
        tcMar.append(node)
    tcPr.append(tcMar)


def set_table_borders(tbl, color="CBD5E0"):
    tblPr = tbl._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="single" w:sz="6" w:space="0" w:color="1B365D"/>'
        f'<w:bottom w:val="single" w:sz="8" w:space="0" w:color="1B365D"/>'
        f'<w:left w:val="single" w:sz="4" w:space="0" w:color="{color}"/>'
        f'<w:right w:val="single" w:sz="4" w:space="0" w:color="{color}"/>'
        f'<w:insideH w:val="single" w:sz="4" w:space="0" w:color="{color}"/>'
        f'<w:insideV w:val="single" w:sz="4" w:space="0" w:color="{color}"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)


def add_h1(text, page_break=False):
    if page_break:
        doc.add_page_break()
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.keep_with_next = True
    # Bottom accent border under H1
    pPr = p._p.get_or_add_pPr()
    pBdr = parse_xml(f'<w:pBdr {nsdecls("w")}><w:bottom w:val="single" w:sz="12" w:space="3" w:color="1B365D"/></w:pBdr>')
    pPr.append(pBdr)
    r = p.add_run(text)
    r.font.name = "Calibri"
    r.font.size = Pt(15)
    r.font.bold = True
    r.font.color.rgb = NAVY
    return p


def add_h2(text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(11)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.keep_with_next = True
    r = p.add_run(text)
    r.font.name = "Calibri"
    r.font.size = Pt(12.5)
    r.font.bold = True
    r.font.color.rgb = BLUE
    return p


def add_h3(text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.keep_with_next = True
    r = p.add_run(text)
    r.font.name = "Calibri"
    r.font.size = Pt(11)
    r.font.bold = True
    r.font.color.rgb = NAVY
    return p


def add_p(text, bold_prefix=None, italic=False, space_after=5):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(space_after)
    if bold_prefix:
        rb = p.add_run(bold_prefix)
        rb.bold = True
        rb.font.color.rgb = DARK
    r = p.add_run(text)
    r.italic = italic
    return p


def add_bullet(text, bold_prefix=None):
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.line_spacing = 1.12
    if bold_prefix:
        rb = p.add_run(bold_prefix)
        rb.bold = True
    p.add_run(text)
    return p


def add_callout(title, body_lines, bg_hex="EEF4FB", border_hex="1E5FAF"):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    tbl.columns[0].width = Cm(16.8)
    c = tbl.cell(0, 0)
    c.width = Cm(16.8)
    set_cell_shading(c, bg_hex)
    set_cell_margins(c, top=100, bottom=100, left=160, right=140)
    tcPr = c._tc.get_or_add_tcPr()
    borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'<w:left w:val="single" w:sz="24" w:space="0" w:color="{border_hex}"/>'
        f'<w:top w:val="single" w:sz="4" w:space="0" w:color="CBD5E0"/>'
        f'<w:right w:val="single" w:sz="4" w:space="0" w:color="CBD5E0"/>'
        f'<w:bottom w:val="single" w:sz="4" w:space="0" w:color="CBD5E0"/>'
        f'</w:tcBorders>'
    )
    tcPr.append(borders)
    p = c.paragraphs[0]
    p.paragraph_format.space_after = Pt(3)
    rt = p.add_run(title)
    rt.bold = True
    rt.font.color.rgb = NAVY
    for ln in body_lines:
        pl = c.add_paragraph()
        pl.paragraph_format.space_after = Pt(2)
        pl.paragraph_format.line_spacing = 1.12
        r = pl.add_run(ln)
        r.font.size = Pt(10.5)
    sp = doc.add_paragraph()
    sp.paragraph_format.space_after = Pt(3)


def add_code_block(code_text):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    c = tbl.cell(0, 0)
    c.width = Cm(16.8)
    set_cell_shading(c, "F1F5F9")
    set_cell_margins(c, top=80, bottom=80, left=140, right=140)
    tcPr = c._tc.get_or_add_tcPr()
    tcPr.append(parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'<w:left w:val="single" w:sz="16" w:space="0" w:color="475569"/>'
        f'<w:top w:val="single" w:sz="4" w:space="0" w:color="CBD5E0"/>'
        f'<w:right w:val="single" w:sz="4" w:space="0" w:color="CBD5E0"/>'
        f'<w:bottom w:val="single" w:sz="4" w:space="0" w:color="CBD5E0"/>'
        f'</w:tcBorders>'
    ))
    p = c.paragraphs[0]
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.05
    r = p.add_run(code_text)
    r.font.name = "Consolas"
    r.font.size = Pt(9.0)
    r.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)
    sp = doc.add_paragraph()
    sp.paragraph_format.space_after = Pt(3)


def add_styled_table(headers, rows, col_widths_cm=None, font_size=9.5, center_cols=None, cell_pad=65):
    center_cols = set(center_cols or [])
    tbl = doc.add_table(rows=1 + len(rows), cols=len(headers))
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    set_table_borders(tbl)

    # Header row
    hdr_row = tbl.rows[0]
    trPr = hdr_row._tr.get_or_add_trPr()
    trPr.append(parse_xml(f'<w:tblHeader {nsdecls("w")}/>'))
    trPr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))
    for j, htxt in enumerate(headers):
        cell = hdr_row.cells[j]
        if col_widths_cm:
            cell.width = Cm(col_widths_cm[j])
        set_cell_shading(cell, "1B365D")
        set_cell_margins(cell, top=cell_pad + 10, bottom=cell_pad + 10, left=80, right=80)
        cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(htxt)
        r.bold = True
        r.font.size = Pt(font_size)
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    for i, rdata in enumerate(rows):
        row = tbl.rows[i + 1]
        row._tr.get_or_add_trPr().append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))
        bg = "F8FAFC" if (i % 2 == 1) else "FFFFFF"
        is_total = str(rdata[0]).upper().startswith(("TỔNG", "TOTAL", "TỈ LỆ"))
        if is_total:
            bg = "E6F4EA"
        for j, val in enumerate(rdata):
            cell = row.cells[j]
            if col_widths_cm:
                cell.width = Cm(col_widths_cm[j])
            set_cell_shading(cell, bg)
            set_cell_margins(cell, top=cell_pad, bottom=cell_pad, left=80, right=80)
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.06
            if j in center_cols:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r = p.add_run(str(val))
            r.font.size = Pt(font_size)
            if is_total or j == 0:
                r.bold = True
    sp = doc.add_paragraph()
    sp.paragraph_format.space_after = Pt(3)
    return tbl


def add_figure(img_path, caption, width_cm=16.0):
    p_img = doc.add_paragraph()
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_img.paragraph_format.space_before = Pt(4)
    p_img.paragraph_format.space_after = Pt(2)
    p_img.paragraph_format.keep_with_next = True
    run = p_img.add_run()
    run.add_picture(img_path, width=Cm(width_cm))

    p_cap = doc.add_paragraph()
    p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap.paragraph_format.space_after = Pt(8)
    rc = p_cap.add_run(caption)
    rc.font.size = Pt(9.5)
    rc.italic = True
    rc.font.color.rgb = MUTED


def add_qa_block(q_num, q_prompt, answer_paragraphs, table_data=None):
    add_h2(f"Câu [{q_num}]")
    add_callout(f"Yêu cầu đề bài (Câu [{q_num}]):", [q_prompt], bg_hex="F3F6FA", border_hex="1B365D")
    for item in answer_paragraphs:
        if isinstance(item, tuple):
            add_p(item[1], bold_prefix=item[0], space_after=4)
        else:
            add_p(item, space_after=4)
    if table_data:
        add_styled_table(*table_data)


# ==============================================================================
# COVER PAGE & BẢNG 5: THÔNG TIN NHÓM (FIT 100% CLEANLY ON PAGE 1)
# ==============================================================================
p_uni = doc.add_paragraph()
p_uni.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_uni.paragraph_format.space_before = Pt(0)
p_uni.paragraph_format.space_after = Pt(1)
ru = p_uni.add_run("ĐẠI HỌC QUỐC GIA THÀNH PHỐ HỒ CHÍ MINH\nTRƯỜNG ĐẠI HỌC BÁCH KHOA\nKHOA KHOA HỌC VÀ KỸ THUẬT MÁY TÍNH")
ru.bold = True
ru.font.size = Pt(11.5)
ru.font.color.rgb = NAVY

p_line = doc.add_paragraph()
p_line.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_line.paragraph_format.space_before = Pt(2)
p_line.paragraph_format.space_after = Pt(6)
rl = p_line.add_run("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
rl.font.color.rgb = BLUE

p_course = doc.add_paragraph()
p_course.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_course.paragraph_format.space_after = Pt(2)
rco = p_course.add_run("BÁO CÁO DỰ ÁN 1 — MÔN HỌC THIẾT KẾ MẠCH ĐIỆN TỬ (CO2037)")
rco.bold = True
rco.font.size = Pt(12)
rco.font.color.rgb = BLUE

p_title = doc.add_paragraph()
p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_title.paragraph_format.space_before = Pt(3)
p_title.paragraph_format.space_after = Pt(4)
rt = p_title.add_run("THIẾT KẾ LẠI BO MẠCH YOLO UNO (ESP32-S3)\nTHEO CHUẨN ARDUINO UNO R3 — PCB 4 LỚP")
rt.bold = True
rt.font.size = Pt(17.5)
rt.font.color.rgb = NAVY

p_sub = doc.add_paragraph()
p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_sub.paragraph_format.space_after = Pt(4)
rs = p_sub.add_run("ESP32-S3-WROOM-1-N16R8 • 12 cổng Grove • QWIIC • 4× Servo GVS • USB-C & DC 6–12 V • Zero-ERC / Zero-DRC")
rs.italic = True
rs.font.size = Pt(9.8)
rs.font.color.rgb = MUTED

# Hero 3D Isometric render right on cover page (sized to keep Table 5 + date on Page 1!)
add_figure(os.path.join(R3D_DIR, "YoloUNO_3D_Isometric.png"),
           "Ảnh phối cảnh 3D sản phẩm thiết kế hoàn chỉnh — Yolo UNO (ESP32-S3, PCB 4 lớp, KiCad 10.0.8)", width_cm=9.8)

p_tbl5 = doc.add_paragraph()
p_tbl5.paragraph_format.space_before = Pt(2)
p_tbl5.paragraph_format.space_after = Pt(2)
p_tbl5.paragraph_format.keep_with_next = True
r_t5 = p_tbl5.add_run("Bảng 5: Thông tin nhóm thực hiện và thông số tổng quan dự án")
r_t5.bold = True
r_t5.font.size = Pt(10)
r_t5.font.color.rgb = NAVY

add_styled_table(
    ["Thông tin", "Nội dung"],
    [
        ["Thành viên 1 (Họ tên – MSSV)", "Dương Quốc Anh – 2410053"],
        ["Thành viên 2 (Họ tên – MSSV)", "Hoàng Trọng Đại – 2510284"],
        ["Lớp / Giảng viên hướng dẫn", "Lớp L02  |  GVHD: Nguyễn Văn Hiếu"],
        ["Phần mềm thiết kế (tên + phiên bản)", "KiCad 10.0.8 (64-bit, thư viện tự chứa YoloUNO.kicad_sym & YoloUNO.pretty)"],
        ["Công cụ AI đã sử dụng", "Google Antigravity (Gemini) hỗ trợ tra cứu datasheet, kiểm chứng tính toán Python, tự động hóa kiểm tra ERC/DRC & đối soát chân"],
        ["Biến thể module ESP32-S3 đã chọn", "ESP32-S3-WROOM-1-N16R8 (16 MB Quad Flash 3,3 V + 8 MB Octal PSRAM 3,3 V, anten PCB)"],
        ["Kích thước bo / số lớp", "68,58 × 53,34 mm (chuẩn Arduino UNO R3) / 4 lớp FR4 (1,60 mm, đồng 1 oz)"],
        ["Kết quả kiểm tra chất lượng", "ERC: 0 Errors, 0 Warnings  |  DRC: 0 Violations, 0 Unconnected, 0 Footprint Errors"],
    ],
    col_widths_cm=[6.0, 10.8],
    font_size=8.8,
    cell_pad=42,
)

p_date = doc.add_paragraph()
p_date.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_date.paragraph_format.space_before = Pt(4)
p_date.paragraph_format.space_after = Pt(0)
rd = p_date.add_run("TP. Hồ Chí Minh, Học kỳ 252 — Năm học 2025–2026")
rd.bold = True
rd.font.size = Pt(10)
rd.font.color.rgb = NAVY


# ==============================================================================
# MỤC 1. GIỚI THIỆU VÀ YÊU CẦU SẢN PHẨM
# ==============================================================================
add_h1("1. Giới thiệu và yêu cầu sản phẩm", page_break=True)

add_p(
    "Yolo UNO là bo mạch phát triển IoT và giáo dục STEM sử dụng vi điều khiển ESP32-S3 của Espressif, kết hợp "
    "hình dáng cơ khí tiêu chuẩn Arduino UNO R3 (68,58 × 53,34 mm) với hệ sinh thái kết nối cắm-là-chạy (plug-and-play) "
    "gồm 12 cổng Grove (4 Analog, 4 Digital, 4 I²C), 1 cổng QWIIC/STEMMA QT, 4 cụm chân Servo GVS (GND–5V–Signal), "
    "cổng USB Type-C tích hợp nạp/debug qua USB-Serial/JTAG nội bộ và ngõ cấp nguồn ngoài DC 6–12 V. Mục tiêu của "
    "Dự án 1 là thiết kế lại hoàn chỉnh phần cứng bo mạch Yolo UNO đạt mức sẵn sàng sản xuất (production-ready): "
    "sơ đồ nguyên lý phân cấp đạt 0 lỗi ERC, layout PCB 4 lớp đạt 0 lỗi DRC/0 chân chưa nối, đầy đủ mô hình 3D thực tế, "
    "bảng BOM có mã linh kiện thương mại mua được và bộ hồ sơ Gerber/Drill chế tạo."
)

add_p("Bảng dưới đây tổng hợp mức độ đáp ứng toàn bộ 11 yêu cầu kỹ thuật R1–R11 trong Bảng 1 của đề bài cùng các nâng cấp kỹ thuật nhóm chủ động bổ sung:")

add_styled_table(
    ["Mã", "Yêu cầu kỹ thuật (Bảng 1)", "Giải pháp thực hiện của nhóm", "Trạng thái"],
    [
        ["R1", "MCU ESP32-S3-WROOM-1, Wi-Fi/BLE, anten PCB", "ESP32-S3-WROOM-1-N16R8 (16 MB Flash, 8 MB Octal PSRAM), anten PCB mép Tây + vùng cấm đồng 4 lớp", "Đạt 100%"],
        ["R2", "Form factor Arduino UNO R3 (≤75×56 mm)", "68,58 × 53,34 mm chính xác bản vẽ UNO R3 (khuyết cạnh Đông, 4 lỗ M3, khe hở header 4,06 mm)", "Đạt 100%"],
        ["R3", "Cấp nguồn kép USB-C 5 V & Jack DC 6–12 V", "Jack DC PJ-002A + TVS SMBJ15CA + P-MOS AO3407A + Buck TPS54202 (5,05 V/2 A) + Mux TPS2116 (chặn dòng ngược)", "Đạt + Nâng cấp"],
        ["R4", "Ổn áp 3,3 V cấp cho MCU & ngoại vi (≥500 mA đỉnh)", "LDO AP2114H-3.3TRG1 (1,0 A, SOT-223, VDO=450 mV) + đồng tản nhiệt 20,4 mm² + 4 via nhiệt xuống In2.Cu", "Đạt 100%"],
        ["R5", "USB Type-C (nạp/Serial/JTAG, CC 5,1 kΩ, ESD)", "HRO TYPE-C-31-M-12 (16P) + 2× 5,10 kΩ độc lập (CC1/CC2) + USBLC6-2SC6 + cặp vi sai 90 Ω (skew 0,67 mm)", "Đạt 100%"],
        ["R6", "Nút nhấn RESET (EN RC) & BOOT (GPIO0)", "SW1/SW2 (TS-1187A) + R7 10 kΩ / C13 1 µF (τ=10 ms) + R8 10 kΩ kéo lên +3V3", "Đạt 100%"],
        ["R7", "LED nguồn, LED D13 (GPIO48), NeoPixel (GPIO45)", "D3 Xanh (R11 470 Ω), D4 Đỏ (R12 270 Ω, 4,81 mA), WS2812B (+5V) qua bộ đệm chuyển mức SN74LV1T34 + R13 10 kΩ", "Đạt + Nâng cấp"],
        ["R8", "Header chuẩn Arduino UNO R3 (D0–D13, A0–A5, Power)", "Đầy đủ J17 (1×8), J18 (1×6), J19 (1×10), J20 (1×8) đúng tọa độ & ánh xạ GPIO Bảng 2", "Đạt 100%"],
        ["R9", "12 cổng Grove (4 Analog, 4 Digital, 4 I²C)", "Bố trí ma trận 3 cột × 4 hàng giữa bo (J3–J14), VCC = +3V3 an toàn cho GPIO 3,3 V, A6 → GPIO14", "Đạt 100%"],
        ["R10", "Cổng QWIIC (JST-SH 1,0 mm) dùng chung bus I²C", "J15 (SM04B-SRSS-TB) đúng chuẩn SparkFun (GND–3V3–SDA–SCL), kéo lên chung R14/R15 = 1,50 kΩ (400 kHz)", "Đạt 100%"],
        ["R11", "4 cụm chân Servo GVS (D2, D11, D12, D13), nguồn 5 V", "J21–J24 + tụ bulk C18 470 µF/10 V sát cụm servo + bus F.Cu 1,30 mm song song mặt phẳng +5V In2.Cu", "Đạt 100%"],
    ],
    col_widths_cm=[1.1, 4.9, 8.6, 2.2],
    font_size=9.0,
    center_cols=[0, 3],
)

add_callout(
    "Các quyết định kỹ thuật & điểm nhóm bổ sung so với tài liệu tham khảo:",
    [
        "1. Xử lý mâu thuẫn Flash (4 MB vs 16 MB): Nhóm chọn ESP32-S3-WROOM-1-N16R8 (16 MB Quad Flash 3,3 V + 8 MB Octal PSRAM 3,3 V). Theo datasheet Espressif, Octal PSRAM chiếm dụng nội bộ GPIO35, GPIO36, GPIO37 nên ba chân này được giữ để trống (NC) hoàn toàn; đồng thời VDD_SPI phải bằng 3,3 V nên GPIO45 được kéo xuống GND bằng R13 = 10 kΩ.",
        "2. Nâng cấp PCB 4 lớp (F.Cu / In1.Cu Solid GND / In2.Cu Split +3V3 & +5V / B.Cu): Với 12 cổng Grove + 4 header UNO + 4 cụm Servo (92 lỗ xuyên) trên diện tích 68,58 × 53,34 mm, cấu trúc 4 lớp đảm bảo mặt phẳng GND hoàn toàn liền mạch (0 đường tín hiệu cắt ngang), kiểm soát trở kháng vi sai USB 90 Ω chính xác (h = 0,20 mm) và cấp nguồn trở kháng thấp cho dòng đỉnh 2 A của Servo.",
        "3. Mạch điều hòa A0 (0–5 V) linh hoạt: Toàn bộ 12 cổng Grove dùng VCC = +3V3 để tuyệt đối không gây quá áp chân GPIO 3,3 V. Riêng chân A0 tích hợp cầu phân áp R16 = 6,80 kΩ / R17 = 10,0 kΩ + tụ lọc C17 = 100 nF cùng jumper hàn 3 cực JP1 (mặc định nối 1–2 trực tiếp 0–3,3 V; chuyển 2–3 để đo cảm biến 0–5 V an toàn theo Câu [10]).",
        "4. Nâng cấp bảo vệ ngược cực & chuyển mức NeoPixel: Dùng TVS hai chiều SMBJ15CA (thay cho đơn chiều SMBJ15A để không gây ngắn mạch khi cắm ngược −12 V), kết hợp P-MOSFET AO3407A, IC mux TPS2116 và bộ đệm đơn kênh SN74LV1T34DBVR cho WS2812B."
    ],
)


# ==============================================================================
# MỤC 2. SƠ ĐỒ KHỐI HỆ THỐNG
# ==============================================================================
add_h1("2. Sơ đồ khối hệ thống", page_break=True)

add_p(
    "Sơ đồ khối tổng thể ở Hình 1 được nhóm tự thiết kế lại hoàn toàn cho kiến trúc thực tế của bản mạch (không sử dụng lại Hình 5 trong đề bài). "
    "Mỗi liên kết giữa các khối ghi rõ mức điện áp danh định, ước lượng dòng tải trung bình/đỉnh và chuẩn giao thức truyền thông."
)

add_figure(os.path.join(FIG_DIR, "fig01_system_block_diagram.png"),
           "Hình 1: Sơ đồ khối hệ thống chi tiết bo mạch Yolo UNO (ESP32-S3-WROOM-1-N16R8) với đầy đủ ray nguồn, ngân sách dòng và giao thức",
           width_cm=16.6)

add_p(
    "Chuỗi phân phối nguồn gồm hai nhánh đầu vào độc lập: nhánh Jack DC 6–12 V đi qua mạch chống quá áp/ngược cực (SMBJ15CA + AO3407A) "
    "tới bộ hạ áp đồng bộ TPS54202 tạo ra 5V_BUCK (5,05 V / 2 A); nhánh USB Type-C cấp VBUS (5,0 V / 0,5–0,9 A). Hai nguồn này hội tụ tại "
    "IC chuyển nguồn ưu tiên TPS2116 (ưu tiên nguồn DC với ngưỡng chuyển V_SW = 4,60 V, chặn dòng ngược tuyệt đối về cổng USB máy tính) tạo thành ray +5V "
    "cấp trực tiếp cho cụm 4 Servo GVS (có tụ bulk 470 µF), bộ đệm mức logic U6 + LED WS2812B, và đầu vào cho LDO AP2114H-3.3. Đầu ra +3V3 (tối đa 1,0 A) "
    "nuôi vi điều khiển ESP32-S3, toàn bộ 12 cổng Grove, cổng QWIIC, kéo lên I²C chung và chân IOREF/3V3 của header UNO R3."
)


# ==============================================================================
# MỤC 3. LỰA CHỌN LINH KIỆN
# ==============================================================================
add_h1("3. Lựa chọn linh kiện", page_break=True)

add_p(
    "Bảng 6 tổng hợp các linh kiện chủ chốt của từng khối chức năng kèm thông số kỹ thuật tra từ datasheet chính thức và lý do lựa chọn "
    "trên cơ sở so sánh định lượng với các phương án thay thế."
)

p_b6 = doc.add_paragraph()
p_b6.paragraph_format.space_after = Pt(3)
p_b6.paragraph_format.keep_with_next = True
rb6 = p_b6.add_run("Bảng 6: Bảng lựa chọn linh kiện chính theo từng khối chức năng")
rb6.bold = True
rb6.font.color.rgb = NAVY

add_styled_table(
    ["Khối", "Linh kiện / Part number", "Thông số then chốt (Datasheet)", "Lý do chọn (So sánh phương án thay thế)"],
    [
        ["Bảo vệ đầu vào", "SMBJ15CA (Littelfuse)\nAO3407A (AOS)\nBZT52C10 (Diodes Inc.)",
         "TVS hai chiều V_RWM=15 V, 600 W;\nP-MOS −30 V, −4,3 A, R_DS(on)≤48 mΩ;\nZener 10 V bảo vệ V_GS≤±20 V",
         "So với diode nối tiếp SS34 (sụt 0,45–0,55 V, tổn hao 0,5 W @1 A), P-MOSFET chỉ sụt ~48 mV (0,048 W). Chọn TVS hai chiều CA thay vì SMBJ15A đơn chiều để không đoản mạch khi cắm ngược −12 V."],
        ["Hạ áp 5 V", "TPS54202DDCR (TI)\nSRN6045TA-150M (Bourns)",
         "V_IN=4,5–28 V, I_OUT=2 A, f_SW=500 kHz, V_FB=0,596 V, SOT-23-6;\nL=15 µH, I_sat=2,9 A, DCR=65 mΩ",
         "Tại 12 V→5 V @1 A: LDO AMS1117-5.0 tỏa nhiệt 7,00 W (cháy mạch); Buck TPS54202 hiệu suất ~88% chỉ tổn hao 0,68 W. So với MP1584 (SOIC-8 lớn), TPS54202 tích hợp synchronous FET (không cần diode Schottky ngoài), vỏ SOT-23-6 rất gọn."],
        ["Chọn nguồn USB/DC", "TPS2116DRLR (TI)",
         "1,6–5,5 V, 2,5 A, R_ON=40 mΩ typ, back-to-back FET chặn dòng ngược, vỏ SOT-583-8",
         "So với cặp diode Schottky OR-ing (sụt 0,45 V → ray 5 V tụt xuống 4,55 V @1 A, làm yếu servo & chạm ngưỡng V_IH), TPS2116 chỉ sụt ~40 mV (ray +5V đạt 4,96–5,01 V), chuyển mạch tự động mượt mà, không rò ngược vào USB PC."],
        ["Ổn áp 3,3 V", "AP2114H-3.3TRG1 (Diodes Inc.)",
         "I_OUT=1,0 A, V_DO=450 mV typ (750 mV max), I_Q=60 µA, PSRR 68 dB, SOT-223, R_θJA=128 °C/W (min pad)",
         "So với AMS1117-3.3 (V_DO=1,1–1,3 V, I_Q=5 mA — dễ tụt áp khi VBUS=4,6 V) và SPX3819/RT9080 (chỉ 500–600 mA, vỏ SOT-23-5 R_θJA≈220 °C/W quá nhiệt ở 600 mA), AP2114H-3.3 đủ 1,0 A, dropout thấp, vỏ SOT-223 tản nhiệt tốt qua đồng PCB."],
        ["Vi điều khiển", "ESP32-S3-WROOM-1-N16R8 (Espressif)",
         "Dual-core LX7 240 MHz, Wi-Fi/BLE 5, 16 MB Quad Flash + 8 MB Octal PSRAM (3,3 V), anten PCB",
         "Đáp ứng cả thông số 16 MB Flash cao hơn trong tài liệu Yolo UNO lẫn đủ 8 MB PSRAM cho AI/MicroPython/màn hình; giữ NC các chân GPIO35–37 theo đúng khuyến cáo Octal PSRAM."],
        ["USB Type-C + ESD", "TYPE-C-31-M-12 (HRO)\nUSBLC6-2SC6 (ST)",
         "USB-C 16P chuẩn USB 2.0;\nESD 2 kênh C_IO=2,5 pF, ±15 kV air / ±8 kV contact, tích hợp kẹp VBUS",
         "USB-C 16P dễ hàn, đủ CC1/CC2 & D+/D− đối xứng hai mặt. USBLC6-2SC6 điện dung ký sinh cực nhỏ (2,5 pF) không méo dạng tín hiệu USB Full-Speed 12 Mbps, bảo vệ đồng thời cả D+, D− và VBUS."],
        ["LED / NeoPixel", "SN74LV1T34DBVR (TI)\nWS2812B-B/W (Worldsemi)\nEverlight 0603 LEDs",
         "Buffer CMOS đơn kênh V_CC=5 V, V_IH(min)=2,0 V < 3,3 V, t_pd≈7 ns, SOT-23-5;\nWS2812B 5050 cấp +5 V",
         "WS2812B cấp 5 V yêu cầu V_IH(min)=0,7×5=3,5 V > 3,3 V của ESP32-S3. SN74LV1T34 dịch mức chuẩn 3,3 V→5,0 V gọn hơn mạch MOSFET rời, không đảo pha, giữ nguyên tín hiệu xung 800 kHz sắc nét."],
        ["Kết nối ngoại vi", "Seeed Grove 4P 2,0 mm (12×)\nJST SM04B-SRSS-TB (QWIIC)\nUNO R3 Female Sockets\nServo Header 1×3 + EEE-FK1A471P",
         "12 Grove 3 màu (Vàng/Trắng/Đỏ);\nQWIIC 1,0 mm ngang;\nTụ bulk 470 µF/10 V Low-ESR cho Servo",
         "Tương thích cơ khí 100% với shield Arduino UNO R3, hệ sinh thái cáp Grove và QWIIC. Tụ bulk 470 µF đặt ngay cạnh 4 cụm servo hấp thụ xung dòng khởi động/kẹt rotor tránh sụt áp reset MCU."],
    ],
    col_widths_cm=[2.4, 3.8, 4.6, 6.0],
    font_size=8.8,
)


# ==============================================================================
# MỤC 4. GIẢI THÍCH SCHEMATIC (4.1 - 4.9)
# ==============================================================================
add_h1("4. Giải thích schematic", page_break=True)

add_p(
    "Toàn bộ sơ đồ nguyên lý được tổ chức theo cấu trúc phân cấp (Hierarchical Schematic) gồm 5 trang chuẩn A3 trong KiCad 10.0.8 "
    "nhằm tách biệt rõ ràng từng miền chức năng (Nguồn, MCU, USB & Hiển thị, Ngoại vi), đầy đủ khung tên dự án, giá trị linh kiện, "
    "mã nhà sản xuất (MPN) và mã LCSC. Hình 2 trình bày trang gốc điều phối 4 trang con cùng các lỗ bắt vít cơ khí H1–H4 và điểm chuẩn quang học FID1–FID3."
)

add_figure(os.path.join(FIG_DIR, "fig02_sch_root.png"),
           "Hình 2: Trang gốc sơ đồ nguyên lý phân cấp (YoloUNO.kicad_sch) kết nối 4 trang con chức năng",
           width_cm=15.8)

# 4.1
add_h2("4.1. Khối nguồn vào và bảo vệ")
add_figure(os.path.join(FIG_DIR, "fig03_sch_4_1_input_prot.png"),
           "Hình 3: Sơ đồ nguyên lý Khối 4.1 — Nguồn vào DC 6–12 V, TVS chống xung và P-MOSFET bảo vệ ngược cực",
           width_cm=15.0)
add_bullet("J1 (PJ-002A): Jack nguồn DC 5,5 × 2,1 mm (chân 1 = dương lõi giữa VIN_RAW, chân 2 & 3 = GND vỏ). Dải điện áp vào 6–12 V DC.", "Ngõ vào DC: ")
add_bullet("D1 (SMBJ15CA): Diode TVS hai chiều điện áp làm việc V_RWM = 15 V (> 12 V có biên dự phòng 25%), điện áp đánh thủng V_BR ≈ 16,7–18,5 V, kẹp xung đột biến V_C ≤ 24,4 V (nhỏ hơn định mức chịu áp 28 V của U1 và 30 V của Q1). Thiết kế dùng bản hai chiều (CA) nên khi cắm ngược −12 V, TVS không dẫn thuận gây chập nguồn.", "Chống quá áp tức thời: ")
add_bullet("Q1 (AO3407A), D2 (BZT52C10), R1 (47 kΩ): Mạch chống ngược cực 'ideal diode'. Chân Drain (3) nối VIN_RAW, Source (2) nối VIN_PROT, Gate (1) kéo xuống GND qua R1 = 47 kΩ và kẹp với Source bằng Zener D2 = 10 V. Khi cấp đúng +12 V: diode ký sinh dẫn ban đầu đưa Source lên ~11,3 V, lúc này V_GS bị D2 kẹp an toàn ở −10 V (trong giới hạn ±20 V của AO3407A), Q1 bão hòa hoàn toàn với R_DS(on) ≤ 48 mΩ (sụt áp chỉ 48 mV @1 A). Khi cắm ngược −12 V: diode ký sinh khóa và V_GS ≈ 0 V → Q1 ngắt tuyệt đối, VIN_PROT = 0 V.", "Bảo vệ ngược cực: ")
add_bullet("C1 (47 µF/25 V, tụ điện phân SMD) và C2 (100 nF/50 V X7R): Lọc gợn tần số thấp và triệt nhiễu cao tần tại nút VIN_PROT trước khi vào khối Buck và chân VIN của Arduino.", "Tụ lọc đầu vào: ")

# 4.2
add_h2("4.2. Khối hạ áp 5 V (Synchronous Buck Converter)")
add_figure(os.path.join(FIG_DIR, "fig04_sch_4_2_buck_5v.png"),
           "Hình 4: Sơ đồ nguyên lý Khối 4.2 — Mạch hạ áp đồng bộ 5 V / 2 A dùng TPS54202DDCR (500 kHz)",
           width_cm=15.2)
add_bullet("U1 (TPS54202DDCR): IC Buck đồng bộ tích hợp sẵn MOSFET trên/dưới (V_IN = 4,5–28 V, I_OUT = 2 A, f_SW = 500 kHz, điện áp tham chiếu hồi tiếp V_FB = 0,596 V theo TI SLVSDF5).", "IC chuyển đổi Buck: ")
add_bullet("R2 (100 kΩ): Kéo chân EN lên VIN_PROT giúp IC tự khởi động khi có nguồn DC. C3 (10 µF/25 V X5R) đặt sát chân VIN–GND khép vòng dòng xung đầu vào.", "Khởi động & lọc vào: ")
add_bullet("C4 (100 nF/50 V X7R): Tụ bootstrap nối giữa BOOT (chân 6) và SW (chân 2) tạo điện áp lái cực cổng cho N-MOSFET nhánh trên.", "Tụ Bootstrap: ")
add_bullet("Cầu chia hồi tiếp R3 = 68,0 kΩ (1%) và R4 = 9,10 kΩ (1%): Tính theo công thức datasheet TI SLVSDF5:", "Thiết lập điện áp đầu ra: ")
add_code_block(
    "V_OUT = V_FB × (1 + R3 / R4) = 0,596 × (1 + 68,0 / 9,10) = 0,596 × 8,4725 = 5,050 V  (+1,0% bù sụt áp đường mạch)"
)
add_bullet("Cuộn cảm L1 = 15 µH (Bourns SRN6045TA-150M, vỏ bọc từ chống nhiễu EMI, I_sat = 2,9 A, I_rms = 2,5 A) & tụ ra C5, C6 = 2 × 22 µF/16 V X5R mắc song song (tổng ~44 µF danh định, ~28 µF hiệu dụng sau DC-bias). Kiểm chứng độ gợn dòng cuộn cảm tại điều kiện xấu nhất V_IN = 12 V, V_OUT = 5,05 V, f_SW = 500 kHz:", "Cuộn cảm & tụ đầu ra: ")
add_code_block(
    "ΔI_L = [V_OUT × (V_IN − V_OUT)] / (V_IN × f_SW × L1) = [5,05 × (12 − 5,05)] / (12 × 500×10³ × 15×10⁻⁶) = 0,390 A\n"
    "I_L(peak) = I_OUT(max) + ΔI_L / 2 = 2,0 + 0,195 = 2,195 A  <  I_sat = 2,90 A  (biên an toàn 32%)"
)

# 4.3
add_h2("4.3. Khối chọn nguồn USB/DC (Auto Power-Path Multiplexer)")
add_figure(os.path.join(FIG_DIR, "fig05_sch_4_3_power_mux.png"),
           "Hình 5: Sơ đồ nguyên lý Khối 4.3 — Bộ chọn nguồn tự động ưu tiên DC không sụt áp ngược dùng TPS2116DRLR",
           width_cm=15.0)
add_bullet("U2 (TPS2116DRLR): IC power-mux tích hợp cặp MOSFET ngược chiều (back-to-back) cho cả hai ngõ vào VIN1 (5V_BUCK) và VIN2 (VBUS), R_ON = 40 mΩ typ, dòng định mức 2,5 A. Chân MODE nối trực tiếp VIN1 kích hoạt chế độ ưu tiên tuyệt đối VIN1 (Priority Mode).", "Nguyên lý chuyển mạch: ")
add_bullet("Cầu chia ngưỡng ưu tiên R5 = 36,0 kΩ (1%) và R6 = 10,0 kΩ (1%) tại chân PR1 (ngưỡng nội bộ V_REF = 1,00 V theo TI SLVSFJ9): Ngưỡng chuyển mạch V_SW = 1,00 × (1 + 36,0 / 10,0) = 4,60 V.", "Tính ngưỡng chuyển nguồn: ")
add_bullet("Trạng thái hoạt động: (1) Chỉ cắm USB → VIN1 = 0 V, PR1 = 0 V → TPS2116 đóng kênh VIN2, +5V lấy từ VBUS (sụt ~20 mV @500 mA); (2) Chỉ cắm DC → VIN1 = 5,05 V > 4,60 V → đóng kênh VIN1, +5V ≈ 5,01 V @1 A; (3) Cắm đồng thời cả USB và DC → PR1 = 1,10 V > 1,00 V → ưu tiên hoàn toàn nguồn DC 2 A và mở khóa FET kênh VIN2, triệt tiêu 100% dòng chảy ngược về cổng USB máy tính. C7 (10 µF/16 V) giữ ổn định điện áp +5V trong thời gian chuyển mạch vài micro-giây.", "3 chế độ làm việc: ")

# 4.4
add_h2("4.4. Khối ổn áp 3,3 V và LED báo nguồn")
add_figure(os.path.join(FIG_DIR, "fig06_sch_4_4_ldo_3v3.png"),
           "Hình 6: Sơ đồ nguyên lý Khối 4.4 — LDO 3,3 V / 1,0 A (AP2114H-3.3TRG1) và LED nguồn xanh D3",
           width_cm=15.0)
add_bullet("U3 (AP2114H-3.3TRG1, vỏ SOT-223 có tab tản nhiệt nối chân 2 VOUT): Ổn áp tuyến tính nhiễu thấp dòng định mức 1,0 A, V_DO = 450 mV typ ở 1 A (dư biên lớn khi +5V ≈ 5,0 V và vẫn ổn áp tốt ngay cả khi VBUS sụt xuống 4,5 V).", "Ổn áp 3,3 V: ")
add_bullet("C8 (10 µF/16 V X5R) lọc đầu vào +5V; C9 (22 µF/16 V X5R) và C10 (100 nF/50 V X7R) đảm bảo độ ổn định vòng hồi tiếp LDO và đáp ứng tức thời xung dòng Wi-Fi 500–600 mA của ESP32-S3.", "Tụ lọc vào/ra: ")
add_bullet("D3 (LED xanh lá 0603, V_F ≈ 2,1 V) nối nối tiếp R11 = 470 Ω trên ray +3V3: I_LED = (3,3 − 2,1) / 470 = 2,55 mA — sáng rõ, tiết kiệm năng lượng (P_R11 = 3,06 mW).", "LED báo nguồn: ")
add_bullet("Công suất tiêu tán nhiệt trên U3 (khi V_IN = 5,0 V): P_avg = (5,0 − 3,3) × 0,35 = 0,595 W; P_peak = (5,0 − 3,3) × 0,60 = 1,020 W (phân tích nhiệt chi tiết ở Câu [2]).", "Đánh giá nhiệt: ")

# 4.5
add_h2("4.5. Khối vi điều khiển ESP32-S3-WROOM-1")
add_figure(os.path.join(FIG_DIR, "fig07_sch_4_5_esp32s3.png"),
           "Hình 7: Sơ đồ nguyên lý Khối 4.5 — Module ESP32-S3-WROOM-1-N16R8, mạch EN/BOOT và decoupling (02_MCU_ESP32S3.kicad_sch)",
           width_cm=15.8)
add_bullet("C11 (22 µF/16 V X5R) + C12 (100 nF/50 V X7R) đặt ngay mặt dưới sát chân 3V3 (Pad 2) và GND (Pad 1, 40, 41) để cung cấp tức thời xung dòng phát RF 2,4 GHz. Pad 41 (thermal/GND giữa bụng module) nối trực tiếp xuống mặt phẳng In1.Cu qua mảng 13 via nhiệt có sẵn trong footprint.", "Decoupling nguồn MCU: ")
add_bullet("Mạch RESET (SW1 + R7 = 10 kΩ + C13 = 1 µF): Tạo trễ khởi động RC với hằng số thời gian τ = R7 × C13 = 10 ms giúp nguồn +3V3 ổn định hoàn toàn trước khi thả reset chip. Khi nhấn SW1, chân EN nối tắt xuống GND (V_EN = 0 V).", "Mạch khởi động EN/RESET: ")
add_bullet("Mạch BOOT (SW2 + R8 = 10 kΩ kéo lên +3V3): Mặc định GPIO0 = 1 (chế độ SPI Boot bình thường); giữ SW2 rồi nhấn SW1 đưa GPIO0 = 0 để vào chế độ USB Download Boot.", "Mạch nạp BOOT: ")
add_bullet("Xử lý chân Strapping & PSRAM: GPIO35/36/37 (chân 28–30) được đánh dấu No-Connect (NC) vì Octal PSRAM sử dụng nội bộ; GPIO45 nối R13 = 10 kΩ kéo xuống GND để đảm bảo VDD_SPI = 3,3 V khi khởi động; GPIO46 giữ NC (mặc định pulldown nội = 0).", "Strapping & PSRAM: ")

p_pin = doc.add_paragraph()
p_pin.paragraph_format.space_after = Pt(3)
rp = p_pin.add_run("Bảng ánh xạ chân thực tế giữa ESP32-S3-WROOM-1-N16R8 và các chuẩn kết nối trên bo mạch:")
rp.bold = True
rp.font.color.rgb = NAVY

add_styled_table(
    ["Tín hiệu mạch", "Chân U4 / GPIO", "Đích kết nối thực tế trên bo mạch", "Ghi chú kỹ thuật"],
    [
        ["D0_RX / D1_TX", "P36 (IO44) / P37 (IO43)", "J20.1 / J20.2 (Arduino UNO Digital)", "UART0 (U0RXD / U0TXD)"],
        ["D2 / D3 / D4", "P5 (IO5) / P6 (IO6) / P7 (IO7)", "J20.3–5, Grove J10 (D4-D3), Servo J21 (D2)", "GPIO + ADC1_CH4..6 + Servo PWM"],
        ["D5 / D6 / D7", "P12 (IO8) / P17 (IO9) / P18 (IO10)", "J20.6–8, Grove J9 (D6-D5), Grove J8 (D8-D7)", "GPIO + ADC1_CH7..9"],
        ["D8 / D9 / D10", "P10 (IO17) / P11 (IO18) / P23 (IO21)", "J19.1–3, Grove J8 (D8-D7), Grove J7 (D10-D9)", "GPIO / ADC2_CH6..7"],
        ["D11 / D12 / D13", "P31 (IO38) / P24 (IO47) / P25 (IO48)", "J19.4–6, Servo J24/J23/J22, LED Đỏ D4 (D13)", "SPI / Servo PWM / LED onboard"],
        ["A0_ADC / A1 / A2 / A3", "P39 (IO1) / P38 (IO2) / P15 (IO3) / P4 (IO4)", "J18.1–4, Grove J6/J5/J4/J3 (A0 qua JP1/R16/R17)", "ADC1_CH0..3 (IO3 strapping an toàn)"],
        ["A6", "P22 (IO14)", "Grove J3.2 (cổng A6–A3)", "ADC2_CH3 (bổ sung theo Hình 4)"],
        ["I2C_SDA / I2C_SCL", "P19 (IO11) / P20 (IO12)", "J18.5–6, J19.9–10, Grove J11–J14, QWIIC J15", "Bus I²C chung, kéo lên R14/R15 = 1,50 kΩ"],
        ["USB_DN / USB_DP", "P13 (IO19) / P14 (IO20)", "ESD U5 → USB-C J2 (A7/B7, A6/B6)", "USB-Serial/JTAG nội bộ, cặp vi sai 90 Ω"],
        ["NEO_GPIO45", "P26 (IO45)", "R13 (10 kΩ→GND) → U6 (SN74LV1T34) → D5", "Strapping VDD_SPI = 3,3 V an toàn"],
        ["BOOT_IO0 / MCU_EN", "P27 (IO0) / P3 (EN)", "SW2 + R8 (10 kΩ) / SW1 + R7 + C13 + J17.3", "Chế độ nạp & Reset phần cứng"],
        ["NC (Dự trữ)", "P28–30 (IO35–37), P16 (IO46)...", "Đánh dấu No-Connect (X) trong Schematic", "Bắt buộc để trống cho Octal PSRAM N16R8"],
    ],
    col_widths_cm=[3.2, 3.8, 5.4, 4.4],
    font_size=8.6,
)

# 4.6
add_h2("4.6. Khối USB Type-C và bảo vệ ESD")
add_figure(os.path.join(FIG_DIR, "fig08_sch_4_6_usbc_esd.png"),
           "Hình 8: Sơ đồ nguyên lý Khối 4.6 — Cổng USB Type-C 16P, điện trở CC1/CC2 độc lập và IC bảo vệ ESD USBLC6-2SC6",
           width_cm=15.6)
add_bullet("J2 (HRO TYPE-C-31-M-12): Cổng USB Type-C 16 chân. Hai cặp D+ (A6, B6) và D− (A7, B7) được nối chập tương ứng ngay sát chân cổng để hoạt động đảo chiều (reversible plug); 4 chân VBUS (A4, A9, B4, B9) và 4 chân GND (A1, A12, B1, B12) được gộp chung để giảm trở kháng tiếp xúc; các chân vỏ kim loại SHIELD nối trực tiếp xuống GND.", "Kết nối đầu nối USB-C: ")
add_bullet("R9 = 5,10 kΩ (1%) trên chân CC1 (A5) và R10 = 5,10 kΩ (1%) độc lập trên chân CC2 (B5) xuống GND: Khai báo thiết bị là UFP (Upstream Facing Port / Sink) chuẩn USB-C, yêu cầu nguồn cấp 5 V từ host/adapter (giải thích chi tiết ở Câu [5]).", "Điện trở cấu hình CC1/CC2: ")
add_bullet("U5 (USBLC6-2SC6) + C14 (100 nF): Bảo vệ phóng tĩnh điện ESD (±15 kV không khí / ±8 kV tiếp xúc) cho cả đường D− (chân 1↔6), D+ (chân 3↔4) và đường nguồn VBUS (chân 5) với điện dung ký sinh cực nhỏ 2,5 pF không ảnh hưởng trở kháng vi sai 90 Ω.", "Bảo vệ ESD: ")

# 4.7
add_h2("4.7. Khối hiển thị (LED D13 và RGB NeoPixel WS2812B)")
add_figure(os.path.join(FIG_DIR, "fig09_sch_4_7_leds_neopixel.png"),
           "Hình 9: Sơ đồ nguyên lý Khối 4.7 — LED người dùng D13 (GPIO48) và NeoPixel WS2812B qua bộ đệm chuyển mức 3,3 V→5 V",
           width_cm=15.6)
add_bullet("LED người dùng D4 (Đỏ 0603, V_F ≈ 2,0 V) nối GPIO48 (D13) qua điện trở hạn dòng R12 = 270 Ω (1%): Dòng thực tế I_F = (3,3 − 2,0) / 270 = 4,81 mA (≈ 5 mA theo Câu [8]), công suất tiêu tán P_R12 = 6,26 mW ≪ 100 mW định mức điện trở 0603.", "LED D13: ")
add_bullet("Bộ đệm chuyển mức U6 (SN74LV1T34DBVR, cấp +5V, tụ bypass C15 = 100 nF) + R13 = 10 kΩ kéo chân GPIO45 xuống GND: Giải quyết triệt để hai vấn đề đồng thời — (a) đảm bảo mức logic cao V_OH = 5,0 V > V_IH(min) = 3,5 V của WS2812B (D5, tụ bypass C16 = 100 nF); (b) đảm bảo chân strapping GPIO45 = 0 khi cấp nguồn (VDD_SPI = 3,3 V, tránh treo flash 3,3 V ở chế độ 1,8 V).", "Chuyển mức NeoPixel & Strapping: ")

# 4.8
add_h2("4.8. Khối kết nối ngoại vi (Arduino UNO R3, 12 Grove, QWIIC, 4 Servo, A0 0–5 V)")
add_figure(os.path.join(FIG_DIR, "fig10_sch_4_8_peripherals.png"),
           "Hình 10: Sơ đồ nguyên lý Khối 4.8 — Header UNO R3, 12 cổng Grove, QWIIC, 4 cụm Servo GVS, kéo lên I²C và mạch điều hòa A0",
           width_cm=16.0)
add_bullet("Header Arduino UNO R3 (J17–J20): Đủ 8 chân nguồn J17 (NC, IOREF/+3V3, RESET, +3V3, +5V, GND, GND, VIN_PROT), 6 chân Analog J18 (A0–A5) và 18 chân Digital J19–J20 (D0–D13, GND, AREF, SDA, SCL).", "Header Arduino UNO R3: ")
add_bullet("12 cổng Grove (J3–J14) cấp VCC = +3V3: Chia 3 nhóm màu — 4 cổng Analog (Vàng: A6-A3, A3-A2, A2-A1, A1-A0), 4 cổng Digital (Trắng: D10-D9, D8-D7, D6-D5, D4-D3) và 4 cổng I²C (Đỏ: I2C1–I2C4). Cấp VCC = +3V3 bảo vệ tuyệt đối các chân GPIO không chịu được 5 V của ESP32-S3.", "12 cổng Grove: ")
add_bullet("Bus I²C chung (GPIO11/SDA, GPIO12/SCL) cho 4 Grove I²C + QWIIC (J15) + A4/A5: Dùng duy nhất 1 cặp điện trở kéo lên chuẩn E12 R14 = R15 = 1,50 kΩ lên +3V3 (tính ở Câu [11] cho 400 kHz, C_b = 200 pF → t_r = 254,2 ns ≤ 300 ns).", "Bus I²C & QWIIC: ")
add_bullet("4 cụm Servo GVS (J21–J24: D2, D13, D12, D11): Chân 1 = GND, chân 2 = +5V, chân 3 = Tín hiệu PWM. Tụ hóa Low-ESR C18 = 470 µF/10 V đặt sát cụm chân cấp dòng tức thời khi nhiều servo khởi động đồng thời.", "4 cụm Servo GVS: ")
add_bullet("Mạch giao tiếp Analog A0 (0–5 V): Cầu phân áp R16 = 6,80 kΩ (trên), R17 = 10,0 kΩ (dưới), tụ lọc C17 = 100 nF sát chân GPIO1 và jumper hàn 3 cực JP1 (mặc định nối 1–2 trực tiếp 0–3,3 V; cắt 1–2 nối 2–3 để chia áp 0–5 V → 0–2,976 V an toàn cho ADC1).", "Mạch điều hòa A0: ")

# 4.9
add_h2("4.9. Kết quả kiểm tra ERC")
add_p(
    "Kiểm tra quy tắc điện (ERC) được thực thi ở mức nghiêm ngặt nhất (--severity-all --exit-code-violations) trên toàn bộ 5 trang phân cấp "
    "(81 ký hiệu/footprint, 65 net). Toàn bộ chân không sử dụng đã được gắn cờ No-Connect (X) chuẩn xác và các nguồn đầu vào được khai báo PWR_FLAG hợp lệ. "
    "Kết quả đạt tuyệt đối 0 Lỗi (0 Errors) và 0 Cảnh báo (0 Warnings)."
)
add_figure(os.path.join(FIG_DIR, "fig11_erc_report.png"),
           "Hình 11: Kết quả kiểm tra ERC bằng KiCad 10.0.8 CLI — 0 Errors, 0 Warnings (Exit Code = 0)",
           width_cm=15.6)


# ==============================================================================
# MỤC 5. LAYOUT PCB
# ==============================================================================
add_h1("5. Layout PCB", page_break=True)

add_h2("5.1. Kích thước cơ khí, cấu trúc Stack-up 4 lớp và Design Rules")
add_p(
    "Bo mạch tuân thủ chính xác tuyệt đối kích thước cơ khí chuẩn Arduino UNO R3: 68,58 × 53,34 mm (nhỏ hơn giới hạn 75 × 56 mm), "
    "gồm đường cắt khuyết cạnh Đông, hai góc bo tròn R = 1,50 mm phía Tây, 4 lỗ bắt vít M3 Ø3,2 mm (H1–H4) và vị trí chính xác đến 0,01 mm "
    "của 4 thanh header cái J17–J20 (bao gồm khe hở 4,06 mm chuẩn UNO giữa D8 và D7)."
)
add_p(
    "Lý do lựa chọn cấu trúc PCB 4 lớp (1,60 mm FR4, đồng 1 oz) thay vì 2 lớp: (1) Giữ lớp L2 (In1.Cu) là mặt phẳng GND liền mạch 100% "
    "(2.852,3 mm², 0 đoạn dây tín hiệu cắt qua) giúp tối thiểu hóa diện tích vòng dòng hồi tiếp và bức xạ EMI từ bộ Buck 500 kHz; "
    "(2) Điện môi prepreg mỏng h = 0,20 mm giữa lớp ngoài và mặt phẳng tham chiếu cho phép kiểm soát trở kháng vi sai USB 90 Ω với "
    "độ rộng dây gọn w = 0,25 mm, khe hở s = 0,20 mm (trên PCB 2 lớp dày 1,6 mm dây 90 Ω sẽ quá to khó nối chân USB-C 0,5 mm); "
    "(3) Lớp L3 (In2.Cu) dành riêng làm mặt phẳng nguồn tách sạch (+3V3: 2.135,5 mm² và +5V: 623,5 mm², 0 dây tín hiệu) đảm bảo sụt áp < 5 mV "
    "cho dòng đỉnh 2 A của 4 Servo và 600 mA phát Wi-Fi."
)

add_figure(os.path.join(FIG_DIR, "fig16_pcb_4layer_stackup_diagram.png"),
           "Hình 12: Cấu trúc Stack-up PCB 4 lớp FR4 (1,60 mm, 1 oz) và kiểm soát trở kháng vi sai USB 90 Ω",
           width_cm=13.8)

add_styled_table(
    ["Thông số Design Rule (IPC-2221 Class 2)", "Ngưỡng tối thiểu", "Giá trị áp dụng thực tế trên bo Yolo UNO"],
    [
        ["Độ rộng đường tín hiệu (Min Trace Width)", "0,15 mm (6 mil)", "0,18 mm (GPIO / I²C / tín hiệu chung); 0,25 mm (USB vi sai)"],
        ["Khe hở đồng tối thiểu (Min Clearance)", "0,15 mm (6 mil)", "≥ 0,165 mm (bước dây lưới 0,40 mm → khe hở thực tế 0,22 mm)"],
        ["Kích thước lỗ xuyên Via (Pad / Drill)", "0,60 / 0,30 mm", "0,60 mm pad / 0,30 mm khoan (vành đồng 0,15 mm, 229 via)"],
        ["Khoảng cách đồng đến mép bo (Edge Clearance)", "0,30 mm", "≥ 0,45 mm cho cả đường mạch và vùng đổ đồng Zone"],
        ["Khoảng cách lỗ-đến-lỗ / lỗ-đến-đồng", "0,25 mm", "≥ 0,30 mm (0 lỗi chạm khoan / hole breakout)"],
        ["Đường mạch nguồn dòng lớn (IPC-2221)", "≥ 0,781 mm (@2 A)", "Servo +5V: 1,30 mm (F.Cu) song song mặt phẳng +5V (623,5 mm² In2.Cu); VIN_RAW: 0,80 mm; 5V_BUCK: 0,70 mm"],
        ["Cặp vi sai USB 2.0 (90 Ω ±10%, lệch ≤7,5 mm)", "w=0,25, s=0,20 mm", "L(USB_DN) = 31,91 mm, L(USB_DP) = 31,24 mm → Độ lệch = 0,67 mm (≪ 7,5 mm), 2 via đối xứng"],
    ],
    col_widths_cm=[5.6, 3.2, 8.0],
    font_size=8.6,
    cell_pad=42,
)

add_h2("5.2. Chiến lược bố trí linh kiện, cách ly EMI/RF và quản lý nhiệt")
add_bullet("Anten ESP32-S3-WROOM-1 (U4): Đặt sát mép Tây (X = 0) với phần anten PCB hướng ra ngoài không gian trống; thiết lập vùng cấm đồng (RF Keepout) trên cả 4 lớp (X ∈ [0; 6,90], Y ∈ [17,80; 36,10]) — diện tích đồng dưới anten bằng 0 mm².", "Cách ly anten RF 2,4 GHz: ")
add_bullet("Cách ly khối Buck 500 kHz: Đặt toàn bộ L1, U1, C3–C6 và U2 tại góc Đông-Nam (X ≈ 56–64 mm), cách xa anten ESP32-S3 hơn 52 mm. Nút đóng cắt SW (U1.2–L1.1–C4.2) và BOOT đi 100% trên lớp F.Cu với 0 via (tổng dài SW = 16,49 mm, rộng 0,60 mm), vòng dòng điện đầu vào cực nhỏ. Hai điện trở hồi tiếp R3/R4 đặt mặt dưới B.Cu được mặt phẳng In1.Cu che chắn khỏi từ trường cuộn cảm L1.", "Tối ưu EMI mạch nguồn xung: ")
add_bullet("Phân bố công thái học 2 mặt: Toàn bộ linh kiện cao và cổng giao tiếp người dùng đặt ở mặt trên F.Cu (Jack DC J1, USB-C J2, QWIIC J15, nút RST/BOOT, LED PWR/D13/NeoPixel, 12 cổng Grove 3×4, 4 Servo + tụ C18 470 µF, 4 header UNO). Các linh kiện SMD phẳng nhỏ (bảo vệ ngược cực D1/Q1/D2, tụ decoupling MCU C11–C13/C17, bộ đệm U6, điện trở kéo lên I²C, jumper JP1) bố trí gọn mặt dưới B.Cu ngoài vùng RF Keepout.", "Bố trí 2 mặt hợp lý: ")
add_bullet("Tản nhiệt LDO AP2114H-3.3 (U3): Tab chân 2 (+3V3) của U3 được mở rộng thành vùng đồng đặc 20,4 mm² trên lớp F.Cu và khâu trực tiếp bằng 4 via nhiệt (0,60/0,30 mm) xuống mặt phẳng +3V3 rộng 2.135,5 mm² ở lớp In2.Cu, hạ R_θJA hiệu dụng từ 128 °C/W xuống ≈ 65 °C/W.", "Tản nhiệt LDO 3,3 V: ")

add_h2("5.3. Hình ảnh Layout 2D các lớp đồng và kết quả kiểm tra DRC")
add_figure(os.path.join(FIG_DIR, "fig12_pcb_top_fcu.png"),
           "Hình 13: Layout 2D Lớp trên (F.Cu + F.Silkscreen + Edge.Cuts) — 491 đoạn mạch, bus Servo 1,30 mm, pad nhiệt U3, vùng cấm đồng anten",
           width_cm=14.6)
add_figure(os.path.join(FIG_DIR, "fig13_pcb_in1_gnd.png"),
           "Hình 14: Layout 2D Lớp nội 1 (In1.Cu) — Mặt phẳng GND liền mạch 100% (2.852,3 mm², 0 đường tín hiệu, tự động khoét trống dưới anten)",
           width_cm=14.6)
add_figure(os.path.join(FIG_DIR, "fig14_pcb_in2_pwr.png"),
           "Hình 15: Layout 2D Lớp nội 2 (In2.Cu) — Mặt phẳng nguồn thuần tách sạch +3V3 (2.135,5 mm²) và +5V (623,5 mm², khe tách 0,80 mm, 0 tín hiệu)",
           width_cm=14.6)
add_figure(os.path.join(FIG_DIR, "fig15_pcb_bot_bcu.png"),
           "Hình 16: Layout 2D Lớp dưới (B.Cu + B.Silkscreen soi gương) — 541 đoạn mạch, cặp vi sai USB 90 Ω, bảo vệ đầu vào & in lụa Jumper A0",
           width_cm=14.6)

add_p(
    "Kiểm tra quy tắc thiết kế (DRC) chạy bằng KiCad 10 CLI với đầy đủ cờ kiểm tra nghiêm ngặt nhất (--severity-all --refill-zones "
    "--schematic-parity --exit-code-violations). Kết quả xác nhận: 0 lỗi DRC, 0 chân chưa nối (319/319 pad thuộc 65 net kết nối hoàn toàn), "
    "0 đảo đồng cô lập và 0 sai khác Schematic–PCB."
)
add_figure(os.path.join(FIG_DIR, "fig17_drc_report.png"),
           "Hình 17: Báo cáo kiểm tra DRC trên KiCad 10.0.8 — 0 DRC Violations, 0 Unconnected Pads, 0 Footprint Errors (Exit Code = 0)",
           width_cm=15.6)


# ==============================================================================
# MỤC 6. KẾT QUẢ 3D
# ==============================================================================
add_h1("6. Kết quả 3D", page_break=True)

add_p(
    "Toàn bộ 81 footprint trên bo mạch (gồm 74 linh kiện điện tử, 4 lỗ bắt vít M3 và 3 fiducial) đều đã được gắn mô hình 3D STEP chuẩn xác "
    "về kích thước, tọa độ chân và hướng cắm cơ khí (kể cả Jack DC 12 V PJ-002A, USB-C 16P, hai nút bấm SMD RESET/BOOT và 12 cổng Grove đứng). "
    "Các hình 18–22 trình bày ảnh kết xuất raytracing độ phân giải cao 2400 × 1800 px từ KiCad 10."
)

add_figure(os.path.join(R3D_DIR, "YoloUNO_3D_Top.png"),
           "Hình 18: Hình 3D mặt trên (Top view, 2400 × 1800 px) — Bố trí ma trận 12 cổng Grove, ESP32-S3, USB-C, DC 12 V, QWIIC, 4 Servo & khối Buck",
           width_cm=15.4)
add_figure(os.path.join(R3D_DIR, "YoloUNO_3D_Bottom.png"),
           "Hình 19: Hình 3D mặt dưới (Bottom view, 2400 × 1800 px) — Linh kiện SMD bảo vệ nguồn, bộ đệm U6, Jumper JP1 (A0), in lụa tên bo & vùng trống anten",
           width_cm=15.4)
add_figure(os.path.join(R3D_DIR, "YoloUNO_3D_Isometric.png"),
           "Hình 20: Hình 3D góc nhìn phối cảnh mặt trước–phải (Isometric view) — Kiểm tra chiều cao linh kiện và khe hở cơ khí",
           width_cm=15.2)
add_figure(os.path.join(R3D_DIR, "YoloUNO_3D_Isometric_WestPorts.png"),
           "Hình 21: Hình 3D góc nhìn phối cảnh cạnh Tây — Các cổng giao tiếp ngoài (DC 6–12 V, anten ESP32-S3, USB-C 5 V, QWIIC) nằm phẳng mép bo",
           width_cm=15.2)
add_figure(os.path.join(R3D_DIR, "YoloUNO_3D_Isometric_Bottom.png"),
           "Hình 22: Hình 3D góc nhìn phối cảnh mặt dưới — Kiểm tra phân bố tụ lọc decoupling sát chân MCU và cụm TVS/P-MOSFET",
           width_cm=15.0)


# ==============================================================================
# MỤC 7. TRẢ LỜI CÂU HỎI (CÂU [1] - CÂU [13])
# ==============================================================================
add_h1("7. Trả lời câu hỏi kỹ thuật (Câu [1] – Câu [13])", page_break=True)

add_p(
    "Dưới đây là lời giải chi tiết cho đầy đủ 13 câu hỏi trong Mục 8.1 Phần A (bao gồm cả câu tuỳ chọn Câu [13]). "
    "Mọi thông số được tra cứu từ datasheet chính thức và toàn bộ phép tính đã được kiểm chứng độc lập bằng Python."
)

# Câu [1]
add_qa_block(
    1,
    "Tìm hiểu và so sánh ít nhất 3 IC ổn áp 3,3 V có thể dùng cho mạch (dòng định mức, điện áp dropout, dòng tĩnh I_Q, kiểu vỏ, giá tham khảo, nguồn tham khảo). Chọn một IC và giải thích lý do.",
    [
        ("So sánh 4 IC ổn áp LDO 3,3 V phổ biến: ", "Nhóm khảo sát 4 mã linh kiện thương mại phổ biến trên LCSC/DigiKey và đối chiếu trực tiếp với yêu cầu dòng đỉnh Wi-Fi 500–600 mA + ngoại vi Grove/QWIIC (~150 mA), tổng tải đỉnh ~750 mA:"),
        ("Lựa chọn của nhóm — AP2114H-3.3TRG1 (Diodes Incorporated): ", "AP2114H-3.3 là phương án tối ưu nhất nhờ đồng thời đáp ứng 4 tiêu chí: (1) dòng định mức 1,0 A dư biên 33% so với tải đỉnh 750 mA (vượt xa SPX3819/RT9080); (2) điện áp dropout thấp V_DO = 450 mV typ (nhỏ hơn 2,5× so với AMS1117), đảm bảo đầu ra ổn định 3,3 V ngay cả khi cấp qua dây USB dài bị sụt còn 4,5 V; (3) dòng tĩnh I_Q chỉ 60 µA (nhỏ hơn AMS1117 tới 83 lần), tối ưu cho chế độ ngủ sâu của ESP32-S3; (4) vỏ SOT-223 có tab đồng lớn tản nhiệt dễ dàng qua mặt phẳng In2.Cu."),
        ("Nguồn tham khảo: ", "Diodes Incorporated AP2114 Datasheet (DS31304); AMS AMS1117 Datasheet; MaxLinear SPX3819 Datasheet; Richtek RT9080 Datasheet.")
    ],
    (
        ["Tiêu chí", "AP2114H-3.3TRG1 (Chọn)", "AMS1117-3.3", "SPX3819M5-L-3-3", "RT9080-33GJ5"],
        [
            ["Nhà sản xuất", "Diodes Inc.", "AMS / CJT", "MaxLinear", "Richtek"],
            ["Dòng định mức I_OUT", "1,0 A (1000 mA)", "1,0 A (800 mA thực)", "500 mA", "600 mA"],
            ["Dropout V_DO (typ/max)", "450 mV / 750 mV @1A", "1,1 V / 1,3 V @1A", "340 mV / 700 mV @0,5A", "310 mV / 560 mV @0,6A"],
            ["Dòng tĩnh I_Q (typ)", "60 µA", "5.000 µA (5 mA)", "90 µA", "2 µA"],
            ["Kiểu vỏ & R_θJA", "SOT-223 (128 °C/W min)", "SOT-223 (90–125 °C/W)", "SOT-23-5 (~220 °C/W)", "SOT-23-5 (~220 °C/W)"],
            ["Độ ổn định tụ gốm", "Tốt (MLCC ≥ 4,7 µF)", "Yêu cầu ESR (dễ dao động)", "Tốt (MLCC ≥ 1 µF)", "Tốt (MLCC ≥ 1 µF)"],
            ["Giá tham khảo (LCSC)", "~0,28 USD (C151275)", "~0,06 USD", "~0,18 USD", "~0,10 USD"],
            ["Đánh giá cho Yolo UNO", "ĐẠT TỐI ƯU (đủ dòng, VDO thấp, tản nhiệt tốt)", "Dropout cao (1,3 V), dễ tụt áp trên USB yếu", "Thiếu dòng đỉnh (<600 mA) & quá nhiệt SOT-23-5", "Sát giới hạn 600 mA, SOT-23-5 quá nhiệt >150 °C"],
        ],
        [3.1, 3.5, 3.4, 3.4, 3.4],
        8.4,
    )
)

# Câu [2]
add_qa_block(
    2,
    "Giả sử ray 3,3 V tiêu thụ trung bình 350 mA và đỉnh 600 mA. Tính công suất tiêu tán trên LDO 3,3 V khi đầu vào là 5 V. Với vỏ linh kiện đã chọn (tra R_θJA), nhiệt độ mối nối ước tính là bao nhiêu khi nhiệt độ môi trường 40 °C? Có đạt yêu cầu không?",
    [
        ("1. Công suất tiêu tán trên AP2114H-3.3TRG1 (V_IN = 5,0 V, V_OUT = 3,3 V, I_Q = 60 µA không đáng kể): ",
         "Áp dụng P_D = (V_IN − V_OUT) × I_LOAD:"),
        ("• Trạng thái trung bình (I_avg = 350 mA): ", "P_avg = (5,0 − 3,3) × 0,350 = 0,595 W."),
        ("• Trạng thái đỉnh phát Wi-Fi (I_peak = 600 mA): ", "P_peak = (5,0 − 3,3) × 0,600 = 1,020 W."),
        ("2. Ước tính nhiệt độ mối nối T_J = T_A + P_D × R_θJA (tại T_A = 40 °C, giới hạn hoạt động T_J(max) = 125 °C theo Datasheet AP2114 mục Thermal Resistance): ", ""),
        ("• Trường hợp diện tích pad tối thiểu (R_θJA = 128 °C/W theo datasheet): ",
         "T_J(avg) = 40 + 0,595 × 128 = 116,16 °C (< 125 °C, nhưng biên an toàn nhỏ chỉ 8,8 °C); "
         "T_J(peak liên tục) = 40 + 1,020 × 128 = 170,56 °C (> 125 °C — sẽ kích hoạt bảo vệ quá nhiệt TSD ở 160 °C nếu chạy 600 mA liên tục không tản đồng!)."),
        ("• Trường hợp thiết kế PCB thực tế của nhóm (pad đồng tản nhiệt 20,4 mm² trên F.Cu + 4 via nhiệt xuống mặt phẳng +3V3 rộng 2.135,5 mm² ở In2.Cu, R_θJA(eff) ≈ 65 °C/W theo hướng dẫn tản nhiệt SOT-223 4 lớp của Diodes Inc. / TI AN-2020): ",
         "T_J(avg) = 40 + 0,595 × 65 = 78,68 °C (rất mát, biên an toàn 46,3 °C); "
         "T_J(peak liên tục) = 40 + 1,020 × 65 = 106,30 °C (< 125 °C — ĐẠT YÊU CẦU AN TOÀN ngay cả khi tải đỉnh 600 mA kéo dài!)."),
        ("Kết luận & Nguồn: ", "ĐẠT YÊU CẦU với điều kiện bắt buộc bổ sung vùng đồng tản nhiệt và via nhiệt như nhóm đã thực hiện trong layout PCB (Hình 13 & 15). Nguồn: Diodes Incorporated AP2114 Datasheet (DS31304, Bảng Absolute Maximum Ratings & Thermal Characteristics); TI Application Note SNVA419C (SOT-223 4-layer thermal impedance).")
    ]
)

# Câu [3]
add_qa_block(
    3,
    "Nếu dùng LDO để hạ VIN = 12 V xuống 5 V với dòng tải 1 A, công suất tiêu tán là bao nhiêu? So sánh với một buck converter có hiệu suất 88 %. Từ đó giải thích lựa chọn khối 5 V của nhóm.",
    [
        ("1. Phương án dùng LDO hạ áp 12 V → 5 V @ I_OUT = 1 A: ",
         "P_OUT = 5,0 × 1,0 = 5,00 W. Công suất tiêu tán thành nhiệt trên LDO: P_loss(LDO) = (12 − 5) × 1,0 = 7,00 W. "
         "Hiệu suất η_LDO = V_OUT / V_IN = 5 / 12 = 41,67%. Với vỏ SOT-223 (R_θJA ≈ 65 °C/W), nhiệt độ mối nối đạt T_J = 40 + 7,0 × 65 = 495 °C — phá hủy hoàn toàn linh kiện, bắt buộc dùng tản nhiệt nhôm rất lớn không thể lắp trên bo UNO."),
        ("2. Phương án dùng Buck Converter hiệu suất η = 88% @ 12 V → 5 V, I_OUT = 1 A: ",
         "P_IN = P_OUT / η = 5,00 / 0,88 = 5,682 W. Công suất tổn hao nhiệt: P_loss(Buck) = P_IN − P_OUT = 5,682 − 5,00 = 0,682 W (nhỏ hơn LDO tới 10,27 lần!). Dòng lấy từ nguồn 12 V chỉ là I_IN = 5,682 / 12 = 0,473 A (giảm hơn một nửa so với LDO lấy 1,0 A)."),
        ("3. Lựa chọn của nhóm: ",
         "Nhóm bắt buộc chọn Synchronous Buck Converter TPS54202DDCR (500 kHz, 2 A, SOT-23-6, η ≈ 88–92% theo đường cong Efficiency Hình 1 datasheet TI SLVSDF5) kết hợp cuộn cảm bọc từ SRN6045TA-150M (15 µH), đảm bảo chạy mát 2 A liên tục cho 4 servo và toàn bộ hệ thống mà không cần tản nhiệt rời."),
        ("Nguồn tham khảo: ", "Texas Instruments TPS54202 Datasheet (SLVSDF5, Section 6.7 Typical Characteristics & Section 8.2 Typical Application).")
    ]
)

# Câu [4]
add_qa_block(
    4,
    "Trình bày giải pháp chọn nguồn USB/DC của nhóm. Điều gì xảy ra nếu nối trực tiếp VBUS và đầu ra 5 V của khối buck? Tính điện áp ray 5 V khi dùng diode Schottky có V_F = 0,45 V ở dòng 1 A.",
    [
        ("1. Nguy cơ nghiêm trọng nếu nối trực tiếp VBUS và 5V_BUCK: ",
         "Khi cắm đồng thời cáp USB và nguồn ngoài DC 12 V, điện áp 5V_BUCK (5,05 V) thường cao hơn VBUS máy tính (4,75–5,00 V). Sự chênh áp ΔV chỉ 0,2–0,3 V trên trở kháng dây ~0,1 Ω sẽ gây dòng chảy ngược (backfeed) hàng ampe vào cổng USB của laptop/PC, có thể kích hoạt cầu chì tự phục hồi, làm sập nguồn cổng USB hoặc phá hỏng bo mạch chủ máy tính. Ngược lại, khi rút DC trong lúc USB đang cắm, dòng từ VBUS chảy ngược qua diode ký sinh của MOSFET nhánh trên trong IC Buck gây hỏng IC nguồn."),
        ("2. Tính điện áp ray 5 V nếu dùng cặp diode Schottky OR-ing (V_F = 0,45 V @1 A): ",
         "V_5V = V_SRC − V_F = 5,00 − 0,45 = 4,55 V (và nếu VBUS máy tính ở mức cận dưới chuẩn USB 4,75 V thì V_5V tụt chỉ còn 4,30 V!). Ngoài ra tổn hao nhiệt trên diode là P_D = 0,45 × 1,0 = 0,45 W (và 0,90 W ở 2 A). Mức 4,55 V làm giảm mô-men xoắn servo SG90 và giảm biên độ ổn áp cho LDO 3,3 V."),
        ("3. Giải pháp vượt trội của nhóm — IC Power-Mux TPS2116DRLR: ",
         "Dùng cặp MOSFET ngược chiều tích hợp (R_ON = 40 mΩ typ), chặn dòng ngược tuyệt đối (I_rev < 1 µA), tự động ưu tiên nguồn DC Buck khi 5V_BUCK > V_SW = 4,60 V (R5 = 36 kΩ, R6 = 10 kΩ). Tại dòng 1 A, sụt áp chỉ ΔV = 1,0 × 0,040 = 0,040 V → điện áp ray +5V đạt 5,05 − 0,04 = 5,01 V (cao hơn phương án Schottky +0,46 V, tổn hao nhiệt chỉ 0,04 W — giảm 11 lần!)."),
        ("Nguồn tham khảo: ", "Texas Instruments TPS2116 Datasheet (SLVSFJ9, Section 8.3 Priority Power Multiplexing); USB 2.0 Specification (VBUS tolerance 4,75–5,25 V).")
    ]
)

# Câu [5]
add_qa_block(
    5,
    "Tại sao mỗi chân CC1, CC2 của cổng USB Type-C phải có một điện trở 5,1 kΩ riêng xuống GND? Điều gì xảy ra nếu bỏ hai điện trở này, hoặc dùng chung một điện trở cho cả hai chân CC, khi cắm cáp USB-C ↔ USB-C?",
    [
        ("1. Vai trò của R_d = 5,1 kΩ độc lập trên CC1 và CC2 (chuẩn USB Type-C Spec Rev 2.x, mục 4.5.1): ",
         "Trong cổng USB Type-C, nguồn cấp (DFP/Source) đặt điện trở kéo lên R_p trên hai chân CC và chỉ cấp 5 V lên VBUS sau khi phát hiện một thiết bị nhận (UFP/Sink) thông qua điện trở kéo xuống R_d = 5,1 kΩ (±1–10%). Đồng thời, hai chân CC1/CC2 cho phép xác định hướng cắm đảo chiều của cáp: chân CC được nối dây CC sẽ kéo xuống R_d, còn chân CC còn lại trở thành nguồn VCONN (5 V) để cấp cho chip e-Marker bên trong cáp USB-C active/5A."),
        ("2. Nếu bỏ hoàn toàn hai điện trở 5,1 kΩ: ",
         "Khi cắm cáp USB-C ↔ USB-C vào laptop hoặc củ sạc chuẩn PD, nguồn DFP thấy cả CC1 và CC2 ở trạng thái hở mạch (không có thiết bị gắn vào) → DFP giữ VBUS = 0 V, bo mạch hoàn toàn không có điện và không thể nạp chương trình! (Chỉ cáp USB-A ↔ USB-C cũ vốn cấp cứng 5 V mới có điện)."),
        ("3. Nếu mắc chập CC1 và CC2 dùng chung MỘT điện trở 5,1 kΩ: ",
         "Với cáp USB-C ↔ USB-C có chip e-Marker (cáp 5 A/100 W hoặc cáp Thunderbolt, bên trong có trở R_a ≈ 800 Ω–1,2 kΩ kéo xuống GND trên đường VCONN), việc chập chung CC1–CC2 khiến điện trở tương đương song song R_eq = 5,1 kΩ ∥ 1,0 kΩ ≈ 836 Ω. Nguồn DFP sẽ nhận nhầm bo mạch là 'Audio Adapter Accessory Mode' (chế độ tai nghe analog yêu cầu R_a trên cả 2 chân) thay vì thiết bị UFP → ngắt VBUS (0 V), bo mạch không lên nguồn! Do đó bắt buộc dùng hai điện trở R9 = 5,10 kΩ và R10 = 5,10 kΩ hoàn toàn độc lập."),
        ("Nguồn tham khảo: ", "USB-IF USB Type-C Cable and Connector Specification, Release 2.2, Section 4.5.1.2.1 & Table 4-26.")
    ]
)

# Câu [6]
add_qa_block(
    6,
    "Trong Hình 6, tính hằng số thời gian τ của mạch RC trên chân EN. Giải thích vì sao ESP32-S3 cần trễ khởi động. Điện áp tại EN bằng bao nhiêu khi nút SW_RST được nhấn?",
    [
        ("1. Tính hằng số thời gian τ của mạch RC trên chân EN (R7 = 10,0 kΩ, C13 = 1,0 µF): ",
         "τ = R7 × C13 = (10 × 10³ Ω) × (1,0 × 10⁻⁶ F) = 10,0 ms. Theo hàm nạp tụ V_EN(t) = V_DD × (1 − e^(−t/τ)), với ngưỡng mức cao V_IH(EN) = 0,75 × V_DD = 2,475 V (theo ESP32-S3 Datasheet), thời gian trễ mở chip thực tế là t_delay = −τ × ln(1 − 0,75) = 10 × 1,386 = 13,86 ms (vượt xa yêu cầu tối thiểu ≥ 50 µs của Espressif)."),
        ("2. Vì sao ESP32-S3 cần trễ khởi động trên chân EN (Power-On Reset Delay): ",
         "Khi cấp nguồn, điện áp ray +3V3 từ LDO cần khoảng 1–5 ms để tăng từ 0 V lên ổn định 3,3 V và nạp đầy các tụ decoupling. Nếu chân EN lên mức cao ngay lập tức trước khi VDD đạt ngưỡng ổn định (~3,0 V), khối dao động thạch anh 40 MHz, mạch PLL, Flash nội và thanh ghi strapping sẽ đọc sai trạng thái dẫn đến treo khởi động hoặc lỗi brownout liên tục. Mạch RC giữ EN ở mức thấp trong ~14 ms đầu để bảo đảm chip chỉ khởi động khi nguồn 3,3 V đã phẳng hoàn toàn."),
        ("3. Điện áp tại chân EN khi nhấn nút SW1 (SW_RST): ",
         "Nút SW1 nối trực tiếp chân EN xuống GND nên khi nhấn SW1, tụ C13 xả tức thời về 0 V → V_EN = 0,0 V (chắc chắn thấp hơn V_IL(max) = 0,25 × 3,3 = 0,825 V), đưa ESP32-S3 vào trạng thái Reset phần cứng. Khi nhả nút, C13 nạp lại qua R7 với τ = 10 ms giúp chống dội cơ khí (debounce) tự nhiên."),
        ("Nguồn tham khảo: ", "Espressif ESP32-S3 Hardware Design Guidelines, Section 2.3.1 (Power-on Sequence and Reset); ESP32-S3-WROOM-1 Datasheet Section 3.4.")
    ]
)

# Câu [7]
add_qa_block(
    7,
    "Liệt kê các chân strapping của ESP32-S3 và mức logic mặc định cần có khi khởi động. Phân tích rủi ro khi nối LED NeoPixel vào GPIO45 và chân Analog A2 vào GPIO3; nhóm đã xử lý như thế nào trong thiết kế?",
    [
        ("1. Bảng 4 chân Strapping của ESP32-S3 (theo ESP32-S3 Datasheet Mục 2.6 Strapping Pins): ", ""),
        ("2. Rủi ro khi nối NeoPixel vào GPIO45 và cách xử lý: ",
         "Module N16R8 sử dụng Flash & Octal PSRAM 3,3 V nên BẮT BUỘC GPIO45 = 0 khi khởi động để chọn VDD_SPI = 3,3 V. Nếu nối trực tiếp GPIO45 tới chân DIN của WS2812B cấp 5 V, dòng rò từ mạch bảo vệ ESD nội của WS2812B (hoặc bộ dịch mức dùng điện trở kéo lên) có thể kéo điện áp chân GPIO45 vượt ngưỡng V_IH tại thời điểm reset → ESP32-S3 tự chuyển VDD_SPI sang 1,8 V làm Flash 3,3 V ngừng hoạt động và treo boot hoàn toàn! "
         "Cách xử lý của nhóm: (a) Đặt điện trở kéo xuống R13 = 10,0 kΩ từ GPIO45 xuống GND để ghim chắc mức logic 0 khi reset (bởi GPIO45 mặc định có pulldown nội yếu ~45 kΩ); (b) Cách ly hoàn toàn GPIO45 khỏi miền 5 V của WS2812B thông qua ngõ vào CMOS trở kháng cao (>10 MΩ, không có diode kẹp ngược về nguồn 5 V) của bộ đệm SN74LV1T34DBVR (U6)."),
        ("3. Rủi ro khi nối Analog A2 vào GPIO3 và cách xử lý: ",
         "GPIO3 chỉ ảnh hưởng đến việc chọn nguồn JTAG (USB-Serial/JTAG vs External JTAG) khi bit eFuse EFUSE_STRAP_JTAG_SEL được lập trình bằng 1 (mặc định xuất xưởng từ Espressif = 0 nên GPIO3 bị bỏ qua). Tuy nhiên, để phòng ngừa trường hợp eFuse đã bị bật và cảm biến analog nối vào A2 đang xuất áp cao (>2,5 V) lúc bật nguồn làm mất kênh debug USB-JTAG, nhóm tách riêng mạch ngoại vi ở mức 3,3 V an toàn, ghi chú rõ đặc tính strapping của A2/GPIO3 trên tài liệu pinout và khuyến cáo không đặt cảm biến trở kháng thấp kéo cứng mức cao trên A2 nếu bật eFuse JTAG."),
        ("Nguồn tham khảo: ", "Espressif ESP32-S3 Series Datasheet v1.9, Section 2.6 (Strapping Pins, Table 2-4 & 2-5); TI SN74LV1T34 Datasheet (SCLS738).")
    ],
    (
        ["Chân Strapping", "Mặc định nội bộ", "Chức năng khi khởi động", "Mức cần có trên Yolo UNO (N16R8)", "Xử lý trong thiết kế"],
        [
            ["GPIO0", "Pull-up yếu (1)", "Chọn chế độ khởi động (1=SPI Boot, 0=Download)", "1 (chạy bình thường); 0 (khi giữ BOOT)", "R8 = 10 kΩ kéo lên +3V3 + nút SW2 kéo xuống GND"],
            ["GPIO46", "Pull-down yếu (0)", "Kết hợp GPIO0 chọn Boot Mode & in log ROM", "0 (bắt buộc để vào SPI/Download Boot)", "Để trống (NC) tuyệt đối trên schematic & PCB"],
            ["GPIO45", "Pull-down yếu (0)", "Chọn điện áp VDD_SPI (0 = 3,3 V; 1 = 1,8 V)", "0 (BẮT BUỘC 3,3 V cho Flash/PSRAM N16R8)", "R13 = 10 kΩ kéo xuống GND + đệm cách ly CMOS U6"],
            ["GPIO3", "Floating", "Chọn nguồn JTAG (chỉ hiệu lực nếu eFuse=1)", "Không ảnh hưởng khi eFuse mặc định = 0", "Nối A2 (Grove/UNO 3,3 V), ghi chú tránh tải kéo cứng"],
        ],
        [2.3, 2.5, 4.2, 3.8, 4.0],
        8.5,
    )
)

# Câu [8]
add_qa_block(
    8,
    "Trong Hình 8, chọn R_LED để dòng qua LED đỏ (V_F ≈ 2 V) khoảng 5 mA khi GPIO xuất 3,3 V. Công suất tiêu tán trên điện trở là bao nhiêu? Nếu cần điều khiển một LED 100 mW thì phải thay đổi mạch như thế nào (gợi ý: dùng transistor)?",
    [
        ("1. Tính chọn điện trở hạn dòng R12 cho LED đỏ D4 (V_OH ≈ 3,3 V, V_F = 2,0 V, I_LED ≈ 5 mA): ",
         "R_LED = (V_OH − V_F) / I_LED = (3,3 − 2,0) / 0,005 = 260 Ω. Chọn giá trị chuẩn E12/E24 gần nhất là R12 = 270 Ω (1%, vỏ 0603). "
         "Kiểm tra lại dòng thực tế: I_actual = (3,3 − 2,0) / 270 = 4,815 mA (sai số −3,7% so với 5 mA — tối ưu và nhỏ hơn nhiều dòng cực đại 40 mA của GPIO ESP32-S3)."),
        ("2. Công suất tiêu tán trên R12: ",
         "P_R12 = I_actual² × R12 = (0,004815)² × 270 = 0,00626 W = 6,26 mW. Định mức điện trở 0603 là 100 mW (0,1 W) → hệ số dự phòng an toàn tới 16 lần!"),
        ("3. Thay đổi mạch khi cần điều khiển LED công suất 100 mW: ",
         "Với LED đỏ công suất 100 mW (V_F ≈ 2,0 V), dòng cần thiết là I_LED = P / V_F = 0,100 / 2,0 = 50 mA — vượt quá dòng khuyến nghị tối đa 40 mA của một chân GPIO ESP32-S3 (và gây sụt V_OH mạnh). Do đó không được lái trực tiếp từ GPIO mà phải dùng mạch khóa nhánh dưới (low-side switch) dùng N-MOSFET tín hiệu nhỏ (như BSS138 / 2N7002, V_GS(th) ≈ 1,2–1,5 V) hoặc BJT NPN (như MMBT3904 / S8050): "
         "• Dùng N-MOSFET 2N7002/AO3400A: Chân Gate nối GPIO qua R_G = 100 Ω và điện trở xả R_PD = 100 kΩ xuống GND; Drain nối cathode LED qua điện trở hạn dòng R_lim = (5,0 − 2,0) / 0,050 = 60 Ω → chọn 62 Ω công suất 1/4 W (vỏ 1206, P_R = 0,05² × 62 = 155 mW), cấp nguồn từ ray +5V để không gây tải lên LDO 3,3 V; Source nối GND. "
         "• Hoặc dùng BJT NPN MMBT3904 (β_min ≈ 100): R_B = (3,3 − 0,7) / (50 mA / 10) = 520 Ω (chọn 470 Ω đảm bảo bão hòa sâu V_CE(sat) ≈ 0,2 V), R_lim = (5,0 − 2,0 − 0,2) / 0,05 = 56 Ω (vỏ 1206, 0,25 W)."),
        ("Nguồn tham khảo: ", "Espressif ESP32-S3 Datasheet (Table 4-4 DC Characteristics, I_OH(max) = 40 mA); Everlight 19-217/R6C Datasheet.")
    ]
)

# Câu [9]
add_qa_block(
    9,
    "LED NeoPixel WS2812B cấp nguồn 5 V có V_IH(min) = 0,7·V_DD. Tín hiệu 3,3 V từ ESP32-S3 có đảm bảo được nhận đúng mức cao không? Đề xuất ít nhất hai giải pháp và chọn một giải pháp cho thiết kế.",
    [
        ("1. Đánh giá độ tin cậy khi lái trực tiếp 3,3 V → WS2812B cấp 5 V: ",
         "Khi V_DD = 5,0 V (trên bo thực tế +5V ≈ 5,01 V từ Buck/Mux), ngưỡng nhận mức cao tối thiểu của WS2812B theo datasheet Worldsemi là V_IH(min) = 0,7 × 5,01 = 3,507 V. Trong khi đó, điện áp ra mức cao tối đa của ESP32-S3 chỉ là V_OH ≤ 3,30 V (thực tế ~3,1–3,25 V). Vì 3,30 V < 3,507 V (thiếu hụt ít nhất 0,21 V — không có biên nhiễu!), mạch KHÔNG ĐẢM BẢO nhận đúng mức cao, dễ gây nhấp nháy sai màu, treo dữ liệu hoặc không sáng khi nguồn 5 V hơi cao hay nhiệt độ thay đổi."),
        ("2. Đề xuất 3 giải pháp kỹ thuật: ",
         "• Giải pháp A (ĐƯỢC CHỌN) — Bộ đệm CMOS đơn kênh chuyển mức SN74LV1T34DBVR (TI): Cấp V_CC = +5V, nhưng thiết kế ngưỡng vào đặc biệt cho phép V_IH(min) = 2,0 V (tại V_CC = 5 V) < 3,3 V (biên nhiễu +1,3 V cực rộng!), đầu ra đẩy-kéo đạt V_OH ≈ 4,95 V > 3,5 V, trễ truyền chỉ ~7 ns đáp ứng dư chuẩn xung 800 kHz (1,25 µs/bit) của WS2812B, vỏ SOT-23-5 siêu gọn và đồng thời cách ly an toàn chân strapping GPIO45.\n"
         "• Giải pháp B — Mạch hạ nguồn cục bộ bằng 1 diode Schottky (1N5819, V_F ≈ 0,4 V) cấp cho WS2812B: Hạ V_DD(LED) xuống ~4,6 V → V_IH(min) = 0,7 × 4,6 = 3,22 V < 3,3 V. Nhược điểm: biên nhiễu cực hẹp (< 80 mV), giảm độ sáng LED xanh dương và V_F thay đổi theo dòng tải/nhiệt độ, kém tin cậy.\n"
         "• Giải pháp C — Mạch dịch mức bằng N-MOSFET (BSS138 + 2 điện trở kéo lên 4,7 kΩ): Hoạt động được nhưng sườn lên chậm do hằng số thời gian RC với điện dung tải, dễ méo xung ngắn T0H = 350 ns của WS2812B và tốn nhiều linh kiện hơn SN74LV1T34."),
        ("Kết luận & Nguồn: ", "Chọn Giải pháp A (SN74LV1T34DBVR — U6) vì đạt chuẩn kỹ thuật cao nhất, biên nhiễu 1,3 V, xung vuông sắc nét, an toàn strapping GPIO45 và giá thành rất rẻ (~0,16 USD). Nguồn: Worldsemi WS2812B Datasheet (V_IH ≥ 0,7 V_DD); Texas Instruments SN74LV1T34 Datasheet (SCLS738, Section 6.5).")
    ]
)

# Câu [10]
add_qa_block(
    10,
    "Một cảm biến analog Grove cấp nguồn 5 V xuất tín hiệu 0–5 V. Thiết kế mạch giao tiếp để đưa tín hiệu vào chân A0 (ADC1) an toàn và tận dụng tối đa tầm đo ADC (cầu phân áp hoặc op-amp). Tính giá trị linh kiện và trở kháng ra của mạch.",
    [
        ("1. Đặc tính tầm đo ADC1 của ESP32-S3 (theo ESP32-S3 Datasheet Mục 4.3.5): ",
         "Ở mức suy giảm nội 11 dB (ADC_ATTEN_DB_12), tầm đo tuyến tính hiệu chuẩn chính xác của ADC1 ESP32-S3 là 0 – 3,10 V (giới hạn tuyệt đối không phá hủy chân GPIO là V_DD + 0,3 = 3,6 V). Do đó, mục tiêu thiết kế là chuyển đổi dải 0–5,0 V về khoảng 0–3,0 V (tận dụng ~96% tầm đo tuyến tính 3,1 V và giữ biên an toàn 0,6 V dưới ngưỡng phá hủy)."),
        ("2. Thiết kế cầu phân áp chuẩn E12 + tụ lọc RC (R16, R17, C17 + Jumper JP1): ",
         "Chọn tỷ số chia k ≈ 3,0 / 5,0 = 0,60 bằng cặp điện trở chuẩn E12 chính xác 1%: R16 (trên) = 6,80 kΩ và R17 (dưới) = 10,0 kΩ.\n"
         "• Hệ số chia áp chính xác: k = R17 / (R16 + R17) = 10,0 / (6,80 + 10,0) = 0,59524.\n"
         "• Điện áp vào ADC cực đại tại V_in = 5,00 V: V_ADC(max) = 5,00 × 0,59524 = 2,976 V (an toàn tuyệt đối < 3,1 V tuyến tính và < 3,6 V giới hạn; tận dụng 96,0% tầm đo tuyến tính ADC1!).\n"
         "• Dòng tiêu thụ tải lên cảm biến tại 5 V: I_div = 5,0 / 16,8 kΩ = 0,298 mA (rất nhỏ, không làm sụt áp ngõ ra cảm biến analog Grove).\n"
         "• Trở kháng ra tương đương Thevenin của cầu phân áp: R_out = R16 ∥ R17 = (6,80 × 10,0) / (6,80 + 10,0) = 4,048 kΩ (≤ 10 kΩ khuyến nghị cho ADC SAR).\n"
         "• Tụ lọc & cấp điện tích lấy mẫu C17 = 100 nF (0603 X7R) đặt sát chân GPIO1: Tần số cắt lọc nhiễu f_c = 1 / (2π × R_out × C17) = 1 / (2π × 4048 × 100×10⁻⁹) = 393,2 Hz (rất phù hợp các cảm biến analog môi trường như ánh sáng, độ ẩm đất, chiết áp, khí gas và loại bỏ nhiễu 500 kHz của Buck; đồng thời C17 lớn hơn tụ lấy mẫu nội C_sample ~5 pF tới 20.000 lần giúp điện áp không bị sụt lúc lấy mẫu!)."),
        ("3. Tích hợp linh hoạt vào bo mạch: ",
         "Nhóm bổ sung jumper hàn 3 cực JP1 trên mặt dưới PCB (mặc định hàn cầu 1–2 nối thẳng A0_RAW → A0_ADC cho cảm biến 3,3 V không suy hao; người dùng cắt cầu 1–2 và hàn 2–3 khi cắm cảm biến 0–5 V). Nếu cần đo tín hiệu tần số cao (> 5 kHz) từ nguồn có trở kháng ra > 10 kΩ, có thể nâng cấp bằng op-amp rail-to-rail (MCP6001) mắc bộ đệm theo áp sau cầu phân áp (R_out < 1 Ω)."),
        ("Nguồn tham khảo: ", "Espressif ESP32-S3 Datasheet (Section 4.3.5 ADC Characteristics) & ESP-IDF ADC Calibration Guide.")
    ]
)

# Câu [11]
add_qa_block(
    11,
    "Bus I2C (4 cổng Grove I2C + QWIIC) hoạt động ở 400 kHz, điện dung bus ước tính C_b = 200 pF. Tính khoảng giá trị điện trở kéo lên hợp lệ biết R_p(max) = t_r / (0,8473·C_b) với t_r = 300 ns, và R_p(min) = (V_DD − V_OL) / I_OL với V_OL = 0,4 V, I_OL = 3 mA. Chọn giá trị chuẩn E12.",
    [
        ("1. Tính giới hạn dưới R_p(min) (đảm bảo chân cực máng hở kéo được mức thấp V_OL ≤ 0,4 V tại I_OL = 3 mA, V_DD = 3,3 V): ",
         "R_p(min) = (V_DD − V_OL) / I_OL = (3,3 − 0,4) / 0,003 = 2,9 / 0,003 = 966,7 Ω."),
        ("2. Tính giới hạn trên R_p(max) (đảm bảo thời gian tăng sườn lên t_r ≤ 300 ns ở chế độ Fast Mode 400 kHz với C_b = 200 pF): ",
         "R_p(max) = t_r / (0,8473 × C_b) = (300 × 10⁻⁹) / (0,8473 × 200 × 10⁻¹²) = 1.770,3 Ω."),
        ("3. Khoảng giá trị hợp lệ và chọn chuẩn E12: ",
         "Khoảng hợp lệ: 966,7 Ω ≤ R_p ≤ 1.770,3 Ω. Trong dãy chuẩn E12 (..., 1,0 kΩ; 1,2 kΩ; 1,5 kΩ; 1,8 kΩ...), các giá trị nằm trong khoảng là 1,0 kΩ, 1,2 kΩ và 1,5 kΩ. Nhóm chọn R14 = R15 = 1,50 kΩ (1%, vỏ 0603) vì:\n"
         "• Thời gian tăng sườn thực tế: t_r = 0,8473 × 1500 × 200×10⁻¹² = 254,2 ns (< 300 ns, dự phòng 15,3%);\n"
         "• Dòng hút mức thấp thực tế: I_OL = (3,3 − 0,4) / 1500 = 1,93 mA (< 3 mA, an toàn kể cả khi 1–2 module cảm biến Grove/QWIIC ngoài có sẵn điện trở kéo lên phụ 10 kΩ mắc song song — lúc đó R_eq = 1,5 kΩ ∥ 10 kΩ ∥ 10 kΩ = 1,15 kΩ vẫn lớn hơn R_p(min) = 966,7 Ω!)."),
        ("Nguồn tham khảo: ", "NXP Semiconductors UM10204 — I²C-bus specification and user manual, Rev. 7.0, Section 7.1 (Pull-up resistor sizing); TI Application Report SLVA689.")
    ]
)

# Câu [12]
add_qa_block(
    12,
    "Lập bảng ngân sách dòng (power budget) cho ray 5 V và 3,3 V trong trường hợp xấu nhất: ESP32-S3 phát Wi-Fi, 4 servo SG90 hoạt động, NeoPixel sáng trắng tối đa, 4 module Grove. Khối nguồn của nhóm có đáp ứng không? Khi chỉ cấp nguồn qua USB (giới hạn 500 mA hoặc 900 mA) thì sao?",
    [
        ("1. Bảng ngân sách dòng (Power Budget) trường hợp xấu nhất (Worst-Case): ",
         "Vì LDO 3,3 V (U3) lấy nguồn trực tiếp từ ray +5V với dòng đầu vào bằng dòng đầu ra (I_IN(LDO) ≈ I_OUT(3V3) + I_Q), tổng dòng tiêu thụ trên ray +5V bằng tổng dòng trực tiếp trên ray 5 V cộng với toàn bộ dòng ray 3,3 V:"),
        ("2. Đánh giá khả năng đáp ứng của khối nguồn nhóm khi cấp qua Jack DC 6–12 V: ",
         "• Ray +3V3: Tổng dòng đỉnh xấu nhất = 808 mA (trong đó ESP32-S3 đỉnh Wi-Fi 600 mA + 4 module Grove ~200 mA + LED/I²C ~8 mA) < 1.000 mA định mức của AP2114H-3.3 → ĐÁP ỨNG ĐẦY ĐỦ (dư biên ~19%).\n"
         "• Ray +5V (Buck TPS54202 = 2.000 mA, Power-Mux TPS2116 = 2.500 mA): Khi 4 servo SG90 chạy có tải bình thường (~250 mA/servo × 4 = 1.000 mA), tổng dòng ray +5V = 1.000 + 60 + 808 = 1.868 mA < 2.000 mA → ĐÁP ỨNG ĐƯỢC. Tuy nhiên, nếu cả 4 servo bị kẹt rotor đồng thời (stall ~550 mA/servo → 2.200 mA riêng servo, tổng ~3.068 mA), TPS54202 sẽ kích hoạt giới hạn dòng (current limit ~2,8–3,5 A) và tụ C18 (470 µF) chỉ đỡ được các xung ngắn vài mili-giây; trong ứng dụng thực tế không nên để quá 2–3 servo kẹt cơ khí đồng thời trên nguồn nội bộ 2 A."),
        ("3. Phân tích khi CHỈ cấp nguồn qua cổng USB (500 mA USB 2.0 hoặc 900 mA USB 3.0): ",
         "• Không cắm Servo (chỉ chạy ESP32-S3 + Wi-Fi + 4 Grove + NeoPixel): Dòng trung bình ~450–550 mA, dòng đỉnh Wi-Fi + NeoPixel trắng ~868 mA. Với cổng USB 3.0 (900 mA) bo mạch chạy ổn định; với cổng USB 2.0 (500 mA) cần giảm độ sáng NeoPixel hoặc hạn chế tải Grove lớn để tránh sụt áp VBUS/brownout.\n"
         "• Cắm 4 Servo khi chỉ dùng USB: Tổng dòng > 1,8 A vượt xa giới hạn 500 mA / 900 mA của cổng USB → cổng USB máy tính sẽ ngắt bảo vệ quá dòng (overcurrent shutdown) hoặc tụt áp gây reset ESP32-S3 liên tục. Do đó, khi điều khiển từ 2 servo trở lên, người dùng BẮT BUỘC phải cắm nguồn ngoài Jack DC 6–12 V (≥ 2 A)."),
        ("Nguồn tham khảo: ", "Espressif ESP32-S3-WROOM-1 Datasheet (RF TX peak current ~355–500 mA); TowerPro SG90 Datasheet (running 100–250 mA, stall ~550–650 mA); Worldsemi WS2812B (60 mA full white); TI TPS54202 & TPS2116 Datasheets.")
    ],
    (
        ["Thành phần tải", "Ray nguồn", "Dòng trung bình", "Dòng đỉnh (Worst-Case)", "Ghi chú / Nguồn"],
        [
            ["ESP32-S3-WROOM-1 (Wi-Fi TX)", "+3V3", "350 mA", "600 mA", "Phát Wi-Fi 802.11b/g/n peak (Espressif)"],
            ["4 module Grove (cảm biến/OLED)", "+3V3", "100 mA", "200 mA", "Ước tính 25–50 mA / module Grove 3,3 V"],
            ["LED PWR (D3) + LED D13 (D4) + I²C", "+3V3", "6 mA", "8 mA", "2,55 mA + 4,81 mA + kéo lên I²C"],
            ["TỔNG RAY +3V3 (LDO AP2114H = 1000 mA)", "+3V3", "456 mA", "808 mA", "ĐẠT (< 1.000 mA, nhiệt độ T_J ≤ 106 °C)"],
            ["Tải chuyển qua LDO U3 (I_IN ≈ I_3V3)", "+5V", "456 mA", "808 mA", "LDO tuyến tính bảo toàn dòng vào/ra"],
            ["NeoPixel WS2812B (sáng trắng tối đa) + U6", "+5V", "30 mA", "60 mA", "3 kênh RGB × 20 mA (Worldsemi)"],
            ["4× Servo SG90 (chạy đồng thời có tải)", "+5V", "600 mA", "1.000 mA (kẹt: 2.200 mA)", "250 mA/servo chạy tải; 550 mA nếu kẹt"],
            ["TỔNG RAY +5V (Buck = 2000 mA, Mux = 2500 mA)", "+5V", "1.086 mA", "1.868 mA (kẹt: 3.068 mA)", "ĐẠT tải chạy bình thường qua DC; KHÔNG chạy 4 servo bằng USB!"],
        ],
        [4.8, 1.8, 2.3, 3.3, 4.6],
        8.5,
        [1, 2],
    )
)

# Câu [13] (Tuỳ chọn)
add_qa_block(
    13,
    "(Tuỳ chọn) Tính độ rộng tối thiểu của đường mạch 5 V cấp cho cụm servo theo IPC-2221 (dòng 2 A, đồng 1 oz, lớp ngoài, ΔT = 10 °C) và so sánh với độ rộng nhóm đã dùng trong layout.",
    [
        ("1. Công thức chuẩn IPC-2221 (Section 6.2, đường mạch lớp ngoài — External Layer): ",
         "I = k × (ΔT)^b × A^c, với k = 0,048, b = 0,44, c = 0,725 (lớp ngoài); I = 2,0 A; ΔT = 10 °C; độ dày đồng 1 oz = 1,378 mil (35 µm)."),
        ("2. Tính tiết diện đồng A (mil²) và độ rộng tối thiểu W_min: ", ""),
        ("• Tiết diện đồng tối thiểu: ",
         "A = [I / (k × ΔT^0,44)]^(1 / 0,725) = [2,0 / (0,048 × 10^0,44)]^1,3793 = [2,0 / (0,048 × 2,7542)]^1,3793 = (15,128)^1,3793 = 42,39 mil²."),
        ("• Độ rộng tối thiểu W_min: ",
         "W_min = A / Thickness = 42,39 / 1,378 = 30,76 mil = 30,76 × 0,0254 = 0,781 mm."),
        ("3. So sánh với giá trị thực tế trong Layout PCB của nhóm: ",
         "Trên lớp ngoài F.Cu, nhóm đi trục chính +5V nối từ tụ bulk C18 (470 µF) qua cả 4 cụm chân Servo (J21–J24) với độ rộng W_actual = 1,30 mm (lớn gấp 1,66 lần mức tối thiểu 0,781 mm!). Không chỉ vậy, toàn bộ 4 chân +5V (PTH) của cụm Servo và tụ C18 còn nối song song trực tiếp với mặt phẳng nguồn +5V rộng 13,7 mm (diện tích 623,5 mm²) trên lớp nội In2.Cu. Khả năng tải dòng tổng hợp vượt trên 6 A với độ tăng nhiệt ΔT < 3 °C và sụt áp đường mạch < 5 mV."),
        ("Nguồn tham khảo: ", "IPC-2221A Generic Standard on Printed Board Design, Section 6.2 (Conductive Material Requirements, Figure 6-4).")
    ]
)


# ==============================================================================
# MỤC 8. HƯỚNG DẪN SỬ DỤNG PHẦN MỀM THIẾT KẾ KICAD 10.0.8 (4-8 TRANG CHI TIẾT)
# ==============================================================================
add_h1("8. Hướng dẫn sử dụng phần mềm thiết kế KiCad 10.0.8", page_break=True)

add_p(
    "Vì nhóm lựa chọn phần mềm mã nguồn mở chuyên nghiệp KiCad 10.0.8 (thay vì Altium Designer), mục này trình bày hướng dẫn thực hành "
    "từng bước áp dụng trực tiếp trên chính dự án bo mạch Yolo UNO (ESP32-S3, 4 lớp) nhằm giúp bất kỳ sinh viên nào cũng có thể tự dựng lại "
    "toàn bộ dự án từ con số 0 đến khi xuất bộ Gerber/3D sẵn sàng đặt mạch."
)

add_figure(os.path.join(FIG_DIR, "fig18_kicad_workflow_overview.png"),
           "Hình 23: Sơ đồ tổng quan 6 bước thiết kế bo mạch Yolo UNO trên KiCad 10.0.8",
           width_cm=16.4)

# 8.1
add_h2("8.1. Cài đặt KiCad 10.0.8 và khởi tạo cấu trúc Project tự chứa")
add_p(
    "Bước 1 — Tải và cài đặt: Tải bộ cài chính thức KiCad 10.0.8 (64-bit) từ https://www.kicad.org/download/windows/. "
    "Nếu ổ hệ thống C: còn ít dung lượng (< 5 GB), nên cài đặt vào ổ đĩa phụ (ví dụ D:\\KiCad) để chứa trọn bộ thư viện Symbol, Footprint và 3D STEP (~3,2 GB). "
    "Kiểm tra cài đặt thành công bằng dòng lệnh PowerShell:"
)
add_code_block(
    '& "D:\\KiCad\\bin\\kicad-cli.exe" --version   # Kết quả: 10.0.8'
)
add_p(
    "Bước 2 — Tạo project mới: Mở KiCad Project Manager → File → New Project... → đặt tên YoloUNO trong thư mục YoloUNO_Project\\hardware\\. "
    "KiCad tự tạo tệp dự án YoloUNO.kicad_pro, trang nguyên lý gốc YoloUNO.kicad_sch và bo mạch YoloUNO.kicad_pcb."
)
add_p(
    "Bước 3 — Tổ chức thư mục chuẩn dự án tự chứa (Self-Contained Project): Khác với thói quen dùng thư viện toàn cục (dễ báo lỗi thiếu symbol/footprint khi mở trên máy giảng viên), "
    "nhóm đóng gói toàn bộ ký hiệu và footprint sử dụng ngay trong thư mục libraries/ của dự án:"
)
add_code_block(
    "YoloUNO_Project/\n"
    "├── hardware/                        # Project KiCad hoàn chỉnh tự chứa\n"
    "│   ├── YoloUNO.kicad_pro            # Cấu hình dự án, netclass & luật DRC\n"
    "│   ├── YoloUNO.kicad_sch            # Trang gốc phân cấp (Root A3)\n"
    "│   ├── 01_Power_Supply.kicad_sch    # Trang con 1: Bảo vệ, Buck 5V, Mux, LDO 3.3V\n"
    "│   ├── 02_MCU_ESP32S3.kicad_sch     # Trang con 2: ESP32-S3-WROOM-1, EN/BOOT\n"
    "│   ├── 03_USB_and_LEDs.kicad_sch    # Trang con 3: USB-C, ESD, D13, U6, NeoPixel\n"
    "│   ├── 04_Peripherals_and_Headers.kicad_sch  # Trang con 4: UNO, 12 Grove, QWIIC, Servo, A0\n"
    "│   ├── YoloUNO.kicad_pcb            # Layout PCB 4 lớp (68.58 x 53.34 mm)\n"
    "│   ├── sym-lib-table                # Ánh xạ thư viện Symbol cục bộ (${KIPRJMOD})\n"
    "│   ├── fp-lib-table                 # Ánh xạ thư viện Footprint cục bộ (${KIPRJMOD})\n"
    "│   └── libraries/\n"
    "│       ├── YoloUNO.kicad_sym        # 32 ký hiệu mạch đã chuẩn hóa (gồm cả Power)\n"
    "│       └── YoloUNO.pretty/          # 28 tệp .kicad_mod kèm đường dẫn 3D STEP\n"
    "├── outputs/                         # Schematic PDF, 2D PDF, 3D PNG, BOM, Gerbers, ERC/DRC\n"
    "└── scripts/                         # Kịch bản Python kiểm chứng & tự động hóa"
)

# 8.2
add_h2("8.2. Quản lý thư viện linh kiện (Symbol, Footprint và mô hình 3D STEP)")
add_p(
    "Bước 1 — Khai báo bảng thư viện dự án (Project-Specific Libraries): Trong Schematic Editor vào Preferences → Manage Symbol Libraries → thẻ Project Specific Libraries "
    "và thêm dòng YoloUNO trỏ tới ${KIPRJMOD}/libraries/YoloUNO.kicad_sym. Tương tự trong PCB Editor (Manage Footprint Libraries), thêm YoloUNO trỏ tới ${KIPRJMOD}/libraries/YoloUNO.pretty."
)
add_p(
    "Bước 2 — Chọn và tạo mới Symbol (Symbol Editor): Với các linh kiện thông dụng (R, C, LED, AP2114H, USBLC6-2SC6, USB_C_Receptacle_USB2.0_16P, ESP32-S3-WROOM-1), "
    "sao chép từ thư viện chuẩn KiCad vào YoloUNO.kicad_sym. Với các IC đặc thù chưa có sẵn đúng ký hiệu như TPS54202DDCR (SOT-23-6), TPS2116DRLR (SOT-583-8) và SN74LV1T34DBVR (SOT-23-5), "
    "tạo mới trong Symbol Editor, đặt đúng Pin Type (Power Input, Power Output, Input, Output, Passive) theo datasheet để bộ kiểm tra ERC phát hiện chính xác lỗi xung đột nguồn hoặc thiếu nguồn."
)
add_p(
    "Bước 3 — Đối chiếu Footprint với Datasheet (Bước tối quan trọng!): Trước khi gán footprint cho linh kiện, luôn mở Footprint Editor đo lại bước chân (pitch) và kích thước pad bằng công cụ thước đo (Ctrl+Shift+M):"
)
add_bullet("TPS2116DRLR: Vỏ SOT-583-8 có bước chân cực nhỏ 0,50 mm (kích thước pad 0,67 × 0,30 mm), đối chiếu đúng thứ tự chân 1=GND, 2=VOUT, 3=VIN1, 4=PR1, 5=MODE, 6=VIN2, 7=VOUT, 8=ST trong TI SLVSFJ9.", "Kiểm tra IC bước chân mịn: ")
add_bullet("ESP32-S3-WROOM-1: Xác minh 40 chân viền bước 1,27 mm, pad nhiệt GND giữa (Pad 41) gồm 13 lỗ via Ø0,20 mm, và đặc biệt là vùng Keepout anten ở phía đầu module.", "Kiểm tra module RF: ")
add_bullet("Gán mô hình 3D STEP: Mở Footprint Properties (phím E) → thẻ 3D Models → thêm đường dẫn tương đối ${KICAD10_3DMODEL_DIR}/.../*.step. Lưu ý thực tế trên KiCad 10: 4 footprint (Jack DC PJ-102AH, USB-C HRO TYPE-C-31, nút nhấn TS-1187A và Grove 1×4) không đi kèm sẵn tệp .step theo tên gốc của hãng; sinh viên cần ánh xạ sang 4 tệp .step cơ khí tương đương có sẵn trong KiCad 10 và căn chỉnh góc xoay/tỷ lệ trực tiếp trên cửa sổ xem trước 3D như bảng sau:", "Gán và căn chỉnh mô hình 3D: ")

add_styled_table(
    ["Footprint trong dự án", "Tệp 3D STEP thay thế có sẵn trong KiCad 10", "Transform (Offset / Scale / Rotate)"],
    [
        ["BarrelJack_CUI_PJ-102AH_Horizontal", "Connector_BarrelJack.3dshapes/BarrelJack_Horizontal.step", "Offset (0,0,0) | Scale (1,1,1) | Rotate Z = −90°"],
        ["USB_C_Receptacle_HRO_TYPE-C-31-M-12", "Connector_USB.3dshapes/USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal.step", "Offset (0,0,0) | Scale (1,1,1) | Rotate (0,0,0)"],
        ["SW_Push_1P1T_XKB_TS-1187A", "Button_Switch_SMD.3dshapes/SW_Push_1P1T_NO_E-Switch_TL3301NxxxxxG.step", "Offset (0,0,0) | Scale (0.70, 0.82, 0.85) | Rotate (0,0,0)"],
        ["NS-Tech_Grove_1x04_P2mm_Vertical", "Connector_JST.3dshapes/JST_PH_B4B-PH-K_1x04_P2.00mm_Vertical.step", "Offset (0,0,0) | Scale (1,1,1) | Rotate Z = +90°"],
    ],
    col_widths_cm=[4.8, 7.2, 4.8],
    font_size=8.6,
)

# 8.3
add_h2("8.3. Vẽ Schematic phân cấp, gán thuộc tính BOM và chạy kiểm tra ERC")
add_p(
    "Bước 1 — Tạo cấu trúc 5 trang phân cấp (Hierarchical Sheets): Trên trang gốc YoloUNO.kicad_sch (khổ giấy A3, File → Page Settings), "
    "nhấn phím S (Add Hierarchical Sheet) vẽ 4 khối chữ nhật cho 01_Power_Supply, 02_MCU_ESP32S3, 03_USB_and_LEDs và 04_Peripherals_and_Headers. "
    "Nhấn đúp vào từng khối để mở trang con; đặt Hierarchical Labels (phím H) cho các tín hiệu liên trang (như VIN_PROT, USB_DN, USB_DP, D0–D13, A0_ADC, I2C_SDA, I2C_SCL), "
    "sau đó quay lại trang gốc nhấn Import Sheet Pin để nối dây liên kết các trang."
)
add_p(
    "Bước 2 — Đặt linh kiện, nguồn và nhãn mạng: Nhấn A để đặt linh kiện từ thư viện YoloUNO, phím P để đặt ký hiệu nguồn toàn cục (+3V3, +5V, GND, VBUS), "
    "phím W để vẽ dây dẫn, phím L để đặt nhãn nội bộ, và phím Q để gắn dấu X (No-Connect) lên mọi chân không dùng (như GPIO35–37, GPIO46, SBU1/SBU2, U2.ST, D5.DOUT, J17.Pin1). "
    "Đặt ký hiệu PWR_FLAG tại các net nguồn vào (VIN_PROT, 5V_BUCK, VBUS, GND) để thông báo với ERC rằng các đường này thực sự được cấp năng lượng từ bên ngoài."
)
add_p(
    "Bước 3 — Gán đầy đủ mã linh kiện (MPN, LCSC) và Footprint: Nhấn Tools → Edit Symbol Fields Table... để kiểm tra và điền hàng loạt 3 trường bắt buộc "
    "(Footprint, MPN, LCSC) cho tất cả 81 ký hiệu trong một bảng duy nhất — tránh bỏ sót linh kiện khi xuất BOM."
)
add_p(
    "Bước 4 — Kiểm tra Quy tắc Điện (ERC): Vào Inspect → Electrical Rules Checker → Run ERC (hoặc dùng dòng lệnh kicad-cli sch erc --severity-all --exit-code-violations). "
    "Mục tiêu bắt buộc là 0 Errors và 0 Warnings (như Hình 11). Các lỗi thường gặp cần xử lý ngay: quên đặt PWR_FLAG trên net nguồn từ jack/connector, "
    "đặt sai tên nhãn (chữ hoa/thường), hoặc quên đánh dấu No-Connect trên chân dự trữ."
)

# 8.4
add_h2("8.4. Chuyển sang PCB, thiết lập đường viền Arduino UNO R3 và Design Rules")
add_p(
    "Bước 1 — Cập nhật PCB từ Schematic: Mở PCB Editor (YoloUNO.kicad_pcb) → nhấn phím F8 (Tools → Update PCB from Schematic...) → chọn 'Update footprints' và 'Delete footprints with no symbols' → Update PCB. "
    "Toàn bộ 81 footprint và 65 net dây bay (ratsnest) sẽ được đưa vào không gian thiết kế."
)
add_p(
    "Bước 2 — Thiết lập Stack-up 4 lớp và Design Rules: Vào File → Board Setup:"
)
add_bullet("Board Stackup → Physical Stackup: Chọn Copper layers = 4, Board thickness = 1,6 mm; đặt tên và chức năng: F.Cu (Signal), In1.Cu (Power/GND), In2.Cu (Power), B.Cu (Signal). Độ dày điện môi prepreg 0,20 mm giúp kiểm soát trở kháng 90 Ω.", "Cấu hình 4 lớp: ")
add_bullet("Design Rules → Constraints: Đặt Minimum clearance = 0,15 mm, Minimum track width = 0,15 mm, Minimum via diameter = 0,60 mm, Minimum via hole = 0,30 mm, Copper to edge clearance = 0,30 mm, Hole to hole clearance = 0,25 mm.", "Cấu hình luật IPC-2221 Class 2: ")
add_bullet("Design Rules → Net Classes: Khai báo 3 lớp mạng: Default (w = 0,18 mm, clearance = 0,15 mm), Power (w = 0,45–1,30 mm cho VIN_PROT, 5V_BUCK, +5V, +3V3), và USB_90Ohm (w = 0,25 mm, differential gap = 0,20 mm).", "Phân lớp Net Class: ")
add_p(
    "Bước 3 — Vẽ đường viền cơ khí chuẩn Arduino UNO R3 trên lớp Edge.Cuts: Chuyển lớp hoạt động sang Edge.Cuts và vẽ chính xác đa giác khép kín 68,58 × 53,34 mm "
    "kèm phần khuyết cạnh Đông (X = 66,04 ↔ 68,58 mm), hai cung bo góc R = 1,50 mm ở cạnh Tây. Sau đó khóa cứng tọa độ 4 lỗ bắt vít M3 (H1–H4) và 4 thanh header UNO R3 "
    "(J19/J20 ở cạnh trên Y = 2,54 mm; J17/J18 ở cạnh dưới Y = 50,80 mm — lưu ý kiểm tra kỹ thứ tự chân từ mặt Top để không bị ngược gương như footprint shield!)."
)

# 8.5
add_h2("8.5. Chiến lược đặt linh kiện (Placement), đi dây (Routing), đổ đồng và kiểm tra DRC")
add_p(
    "Bước 1 — Đặt linh kiện theo phân vùng chức năng (Placement): Đặt các linh kiện cố định cơ khí trước (J1, J2, J15, U4 dọc mép Tây), kế đến ma trận 12 cổng Grove ở trung tâm (3 cột cách nhau 8,4 mm × 4 hàng cách nhau 11,1 mm), "
    "cụm 4 Servo + tụ bulk C18 ở phía Đông-Bắc và toàn bộ mạch Buck U1/L1/C3–C6/U2 ở phía Đông-Nam (> 52 mm xa anten ESP32-S3). Nhấn phím F để lật các linh kiện SMD phẳng (D1, Q1, D2, C11–C13, U6, JP1, R14–R17) xuống mặt B.Cu nhằm tối ưu mật độ mà vẫn giữ toàn bộ cổng cắm ở mặt trên."
)
add_p(
    "Bước 2 — Thiết lập vùng cấm đồng anten RF: Trong PCB Editor, kiểm tra vùng Rule Area (Keepout) tích hợp của U4 bao trùm trọn vùng anten (X ∈ [0; 6,90], Y ∈ [17,80; 36,10]) với cả 4 lớp đồng đều đánh dấu 'Keep out copper pours, tracks, vias'."
)
add_p(
    "Bước 3 — Thứ tự đi dây ưu tiên (Route Critical First, phím X):"
)
add_bullet("Ưu tiên 1 — Nút Buck SW và BOOT: Đi ngắn nhất có thể trên lớp F.Cu, 0 via (SW rộng 0,60 mm, dài 16,49 mm).", "1. Vòng nguồn xung: ")
add_bullet("Ưu tiên 2 — Cặp vi sai USB 2.0 (Route → Route Differential Pair, phím 6): Nối cầu chập A6/B6 và A7/B7 ngay tại cổng USB-C tới U5 trên F.Cu (0 via), sau đó đi song song cặp USB_DN/USB_DP (w = 0,25 mm, s = 0,20 mm) tới U4.13/14 qua 2 via đối xứng; đo lại độ lệch chiều dài đạt 0,67 mm (≪ 7,5 mm).", "2. Cặp vi sai tốc độ cao: ")
add_bullet("Ưu tiên 3 — Đường nguồn dòng lớn & tản nhiệt: Đi bus Servo +5V rộng 1,30 mm trên F.Cu (vượt 0,781 mm IPC-2221), đặt 4 via nhiệt 0,60/0,30 mm ngay trên tab +3V3 của U3 nối xuống In2.Cu.", "3. Đường nguồn & nhiệt: ")
add_bullet("Ưu tiên 4 — Toàn bộ tín hiệu GPIO, I²C, Analog: Đi dây vuông góc/45° ưu tiên ngang trên F.Cu và dọc trên B.Cu (100% không cắt vào hai lớp nội In1.Cu và In2.Cu).", "4. Tín hiệu số & tương tự: ")
add_p(
    "Bước 4 — Đổ đồng 4 lớp (Copper Zones, Ctrl+Shift+Z) và điền đồng (phím B): Tạo 6 vùng Zone với thuộc tính 'Remove islands: Always' để tránh hoàn toàn đảo đồng cô lập: "
    "(1) In1.Cu = GND toàn bo (Priority 0); (2) In2.Cu = +3V3 phía Tây/Giữa & +5V phía Đông + nhánh J17.5 (Priority 1, khe tách 0,80 mm); "
    "(3) F.Cu = vùng tản nhiệt đặc +3V3 cho U3 (Priority 2, Solid connection); (4) F.Cu & B.Cu = đổ GND phụ xung quanh (Priority 0, Thermal relief 0,25/0,35 mm). Nhấn phím B để điền đồng."
)
add_p(
    "Bước 5 — Chạy kiểm tra DRC & đối chiếu Schematic Parity: Vào Inspect → Design Rules Checker → tích chọn 'Refill all zones before performing DRC' và 'Test for parity between PCB and schematic' → Run DRC. "
    "Chỉnh sửa cho đến khi đạt 0 Violations, 0 Unconnected items và 0 Footprint errors (Hình 17)."
)

# 8.6
add_h2("8.6. Xuất hồ sơ sản xuất (3D Renders, Schematic PDF, BOM, Gerber & Excellon Drill)")
add_p(
    "KiCad 10 cho phép xuất toàn bộ hồ sơ sản xuất qua cả giao diện đồ họa (File → Plot / Fabrication Outputs) lẫn tự động hóa 100% bằng dòng lệnh kicad-cli để đảm bảo tính lặp lại nhất quán:"
)
add_code_block(
    '# 1. Xuất Schematic PDF (toàn bộ 5 trang A3)\n'
    'kicad-cli sch export pdf -o YoloUNO_Schematic.pdf YoloUNO.kicad_sch\n\n'
    '# 2. Xuất 3D Raytraced PNG độ phân giải cao (Top, Bottom, Isometric)\n'
    'kicad-cli pcb render --side top --width 2400 --height 1800 --quality high --floor -o YoloUNO_3D_Top.png YoloUNO.kicad_pcb\n'
    'kicad-cli pcb render --side top --rotate "-42,0,28" --width 2400 --height 1800 --quality high --floor -o YoloUNO_3D_Isometric.png YoloUNO.kicad_pcb\n\n'
    '# 3. Xuất BOM, CPL Pick-and-Place và mô hình 3D STEP\n'
    'kicad-cli sch export bom --fields "Reference,Value,Footprint,MPN,LCSC" -o YoloUNO_KiCad_BOM.csv YoloUNO.kicad_sch\n'
    'kicad-cli pcb export pos --format csv --units mm --side both -o YoloUNO_CPL_Pos.csv YoloUNO.kicad_pcb\n'
    'kicad-cli pcb export step --subst-models -o YoloUNO_3D_Assembly.step YoloUNO.kicad_pcb\n\n'
    '# 4. Xuất 11 lớp Gerber RS-274X + Excellon Drill (PTH & NPTH tách riêng) + Bản đồ lỗ khoan PDF\n'
    'kicad-cli pcb export gerbers --layers "F.Cu,In1.Cu,In2.Cu,B.Cu,F.Paste,B.Paste,F.Silkscreen,B.Silkscreen,F.Mask,B.Mask,Edge.Cuts" --subtract-soldermask -o gerbers/ YoloUNO.kicad_pcb\n'
    'kicad-cli pcb export drill --format excellon --excellon-units mm --excellon-separate-th --generate-map --map-format pdf -o gerbers/ YoloUNO.kicad_pcb'
)

add_figure(os.path.join(FIG_DIR, "fig19_pth_drill_map.png"),
           "Hình 24: Bản đồ lỗ khoan mạ đồng (YoloUNO-PTH-drl_map.pdf) xuất từ KiCad 10 — 340 lỗ PTH trên 6 mũi khoan (0,20–1,60 mm)",
           width_cm=12.4)

add_p(
    "Sau khi xuất Gerber, mở KiCad Gerber Viewer (gerbview) nạp toàn bộ 11 tệp Gerber cùng 2 tệp khoan .drl để kiểm tra lần cuối đường viền bo, "
    "cửa sổ hở mặt nạ hàn, vùng cấm đồng dưới anten và căn khớp lỗ khoan trước khi nén thành YoloUNO_Gerbers_4Layer.zip gửi nhà sản xuất."
)

p_sc = doc.add_paragraph()
p_sc.paragraph_format.space_before = Pt(4)
p_sc.paragraph_format.space_after = Pt(2)
p_sc.paragraph_format.keep_with_next = True
rsc = p_sc.add_run("Bảng tra cứu nhanh phím tắt cốt lõi & danh mục rà soát trước khi đặt mạch trên KiCad 10.0.8:")
rsc.bold = True
rsc.font.color.rgb = NAVY

add_styled_table(
    ["Môi trường", "Phím tắt KiCad 10", "Chức năng thực hành & Lưu ý kiểm tra DFM"],
    [
        ["Schematic Editor", "A / P / W / L / H / Q / E", "Đặt linh kiện (A), nguồn (P), vẽ dây (W), nhãn cục bộ (L), nhãn phân cấp (H), No-Connect (Q), thuộc tính (E)"],
        ["PCB Editor (Layout)", "F8 / M / R / F / X / 6 / V", "Cập nhật từ Schematic (F8), di chuyển (M), xoay (R), lật mặt B.Cu (F), đi dây (X), vi sai (6), đặt Via (V)"],
        ["Zone & Kiểm tra 3D", "Ctrl+Shift+Z / B / Alt+3", "Vẽ vùng đổ đồng (Ctrl+Shift+Z), điền lại đồng toàn bo (B), mở cửa sổ 3D Viewer raytracing (Alt+3)"],
        ["Đo khoảng cách", "Ctrl+Shift+M", "Đo trực tiếp bước chân IC (0,50 mm TPS2116), khoảng cách anten đến Buck (>52 mm) và khe hở header UNO (4,06 mm)"],
        ["Cổng kiểm soát DFM", "ERC=0, DRC=0, GerbView", "Bắt buộc kiểm tra đủ 4 yếu tố trước khi gửi xưởng: (1) Edge.Cuts khép kín; (2) PTH/NPTH tách riêng; (3) Silkscreen không đè pad; (4) Anten sạch đồng 4 lớp"],
    ],
    col_widths_cm=[3.2, 3.8, 9.8],
    font_size=8.4,
    cell_pad=42,
)


# ==============================================================================
# MỤC 9. NHẬT KÝ SỬ DỤNG AI
# ==============================================================================
add_h1("9. Nhật ký sử dụng AI", page_break=True)

add_p(
    "Trong quá trình thực hiện Dự án 1, nhóm sử dụng công cụ AI có kiểm soát theo đúng quy định Mục 8.4 Phần A. "
    "Bảng 7 ghi nhận trung thực từng mốc sử dụng AI có ảnh hưởng tới kết quả thiết kế kèm phương pháp kiểm chứng độc lập bằng datasheet, Python và bộ kiểm tra ERC/DRC của KiCad 10."
)

p_b7 = doc.add_paragraph()
p_b7.paragraph_format.space_after = Pt(3)
rb7 = p_b7.add_run("Bảng 7: Nhật ký sử dụng công cụ AI và quy trình kiểm chứng kỹ thuật")
rb7.bold = True
rb7.font.color.rgb = NAVY

add_styled_table(
    ["#", "Công cụ", "Mục đích", "Tóm tắt prompt", "Kết quả nhận được", "Cách kiểm chứng (Bắt buộc)"],
    [
        ["1", "Google Antigravity (Gemini)", "Phân tích đề bài & xử lý mâu thuẫn Flash",
         "Phân tích đặc tả R1–R11, Bảng 2 pinout và xử lý mâu thuẫn 4 MB vs 16 MB Flash trên Yolo UNO.",
         "Đề xuất chọn ESP32-S3-WROOM-1-N16R8, cảnh báo GPIO35–37 bị chiếm bởi Octal PSRAM và rủi ro GPIO45.",
         "Đối chiếu trực tiếp Espressif ESP32-S3-WROOM-1 Datasheet v1.5 mục Pin Definitions (Bảng 2-1) và Strapping Pins (Bảng 2-4)."],
        ["2", "Google Antigravity (Gemini)", "Tính toán & chọn linh kiện nguồn (Câu [1]–[4])",
         "So sánh 4 IC LDO 3,3 V, tính Buck TPS54202 (R3/R4, L1, ΔI_L), Power-Mux TPS2116 và bảo vệ ngược cực.",
         "Đề xuất TPS54202 + TPS2116 + AP2114H-3.3 + AO3407A; ban đầu gợi ý TVS đơn chiều SMBJ15A.",
         "Tự phát hiện lỗi SMBJ15A đoản mạch khi cắm ngược −12 V → nâng cấp thành TVS hai chiều SMBJ15CA; kiểm chứng lại toàn bộ công thức bằng script Python và datasheet TI SLVSDF5, SLVSFJ9, Diodes DS31304."],
        ["3", "Google Antigravity (Gemini)", "Tính I²C, A0 0–5 V, NeoPixel & IPC-2221 (Câu [8]–[13])",
         "Tính R_p I²C 400 kHz, cầu phân áp A0 0–5 V chuẩn E12, giải pháp chuyển mức WS2812B và bề rộng IPC-2221.",
         "Ra kết quả R14/R15 = 1,50 kΩ, R16/R17 = 6,8 kΩ/10 kΩ + JP1, SN74LV1T34DBVR, W_min = 0,781 mm.",
         "Kiểm tra công thức NXP UM10204 (mục 7.1), TI SCLS738 (V_IH=2,0 V), Worldsemi WS2812B (0,7·VDD=3,5 V) và IPC-2221A mục 6.2 bằng Python."],
        ["4", "Google Antigravity (Gemini)", "Dựng Schematic phân cấp 5 trang & thư viện tự chứa",
         "Tạo kịch bản sinh schematic phân cấp 5 trang A3 trong KiCad 10 kèm thư viện YoloUNO.kicad_sym/.pretty.",
         "Sinh thành công 5 trang A3 và netlist 81 footprint / 65 net; vòng đầu xuất hiện lỗi đặt tên J16A–D và cảnh báo thư viện ngoài.",
         "Đổi tên thành J21–J24, đóng gói toàn bộ ký hiệu vào thư viện cục bộ, chạy kicad-cli sch erc --severity-all đạt 0 Errors / 0 Warnings và kiểm tra trực quan từng trang PDF."],
        ["5", "Google Antigravity (Gemini)", "Tọa độ cơ khí UNO R3 & bố trí 2 mặt 4 lớp",
         "Xác minh tọa độ 4 header UNO R3, 4 lỗ M3, anten ESP32-S3 mép Tây và khoảng cách khối Buck.",
         "Phát hiện footprint UNO Shield trong thư viện chuẩn KiCad bị ngược trục Y so với bo chủ; lập bảng tọa độ chuẩn hóa cho 81 linh kiện.",
         "Đối chiếu trực tiếp bản vẽ cơ khí chính thức Arduino UNO R3 (68,58×53,34 mm, khe hở 4,06 mm giữa D8–D7) và xác minh bằng DRC placement = 0 lỗi."],
        ["6", "Google Antigravity (Gemini)", "Tự động đi dây 4 lớp (PathFinder) & đổ đồng",
         "Xây dựng kịch bản đi dây ưu tiên SW 0 via, cặp vi sai USB 90 Ω, bus Servo 1,30 mm, A* PathFinder và đổ đồng 4 lớp.",
         "Vòng đầu gặp lỗi giả self-via và 1 đoạn track lặp 0,20 mm trên D6; sau hiệu chỉnh đạt hội tụ 100% trên F.Cu/B.Cu (0 track ở In1.Cu/In2.Cu).",
         "Chạy kicad-cli pcb drc --severity-all --refill-zones --schematic-parity --exit-code-violations xác nhận Exit=0 (0 DRC / 0 Unconnected / 0 Parity) và kiểm tra mắt thường cả 6 trang 2D PDF."],
        ["7", "Google Antigravity (Gemini)", "Kiểm tra & sửa lỗi thiếu mô hình 3D STEP",
         "Kiểm tra lý do thiếu hình 3D của Jack DC 12 V, USB-C 5 V và 2 nút bấm trong 3D Viewer KiCad 10.",
         "Phát hiện 4 tệp .step vendor không tồn tại trong KiCad 10; ánh xạ sang 4 tệp .step tương đương có sẵn. Vòng đầu Jack DC bị xoay ngược +90°.",
         "Kiểm tra trực quan ảnh render 3D Top/Isometric, chỉnh góc xoay Jack DC về −90° cho khớp khít 3 lỗ PTH và mép Tây, chạy lại DRC = 0."],
        ["8", "Google Antigravity (Gemini)", "Tổng hợp BOM .xlsx, Gerber và xuất báo cáo Phần B",
         "Sinh BOM Excel đa trang có công thức SUM, xuất Gerber/Drill, vẽ sơ đồ khối và biên soạn báo cáo Phần B.",
         "Tạo hoàn chỉnh bộ sản phẩm nộp Table 3 kèm hướng dẫn KiCad 10 và tệp PDF báo cáo.",
         "Rà soát đối chiếu từng con số ERC/DRC/BOM/Gerber, mở kiểm tra trực quan toàn bộ 5 ảnh 3D, sơ đồ khối và từng trang PDF báo cáo."],
    ],
    col_widths_cm=[0.6, 2.3, 2.6, 3.2, 3.8, 4.3],
    font_size=8.0,
    center_cols=[0],
)

add_callout(
    "Đánh giá ngắn về hiệu quả và hạn chế khi sử dụng AI Agent:",
    [
        "• Điểm mạnh của AI: Tăng tốc rất lớn ở khâu tổng hợp thông số so sánh đa linh kiện, kiểm tra nhất quán ánh xạ 81 chân/65 net, viết kịch bản Python kiểm chứng công thức toán học và tự động hóa quy trình lặp ERC/DRC/Gerber bằng kicad-cli.",
        "• Các sai sót thực tế AI gặp phải mà nhóm đã phát hiện và khắc phục: (1) Ban đầu gợi ý TVS đơn chiều SMBJ15A dễ gây chập khi cắm ngược nguồn −12 V (đã sửa thành SMBJ15CA); (2) Suýt dùng nhầm tọa độ ngược trục Y của footprint Arduino Shield (đã sửa theo bản vẽ cơ khí UNO R3 gốc); (3) Không tự phát hiện 4 tệp .step vắng mặt trong KiCad 10 cho tới khi nhóm mở 3D Viewer kiểm tra thực tế và sửa góc xoay Jack DC 12 V.",
        "• Bài học kinh nghiệm: AI là trợ lý kỹ thuật mạnh mẽ, nhưng kỹ sư thiết kế bắt buộc phải làm chủ nguyên lý, luôn đối chiếu trực tiếp với datasheet gốc, kiểm tra bằng công cụ vật lý (ERC/DRC) và thẩm định trực quan trên bản vẽ 2D/3D."
    ],
    bg_hex="F8FAFC",
    border_hex="167A45",
)


# ==============================================================================
# MỤC 10. PHÂN CÔNG CÔNG VIỆC
# ==============================================================================
add_h1("10. Phân công công việc", page_break=True)

add_p("Bảng 8 trình bày chi tiết phân công nhiệm vụ và tỉ lệ đóng góp giữa hai thành viên trong nhóm:")

p_b8 = doc.add_paragraph()
p_b8.paragraph_format.space_after = Pt(3)
p_b8.paragraph_format.keep_with_next = True
rb8 = p_b8.add_run("Bảng 8: Bảng phân công công việc nhóm (Lớp L02)")
rb8.bold = True
rb8.font.color.rgb = NAVY

add_styled_table(
    ["Hạng mục", "Dương Quốc Anh (2410053)", "Hoàng Trọng Đại (2510284)", "Ghi chú"],
    [
        ["Phân tích yêu cầu, sơ đồ khối", "Chủ trì phân tích R1–R11, vẽ sơ đồ khối hệ thống & ngân sách dòng", "Đọc đặc tả Yolo UNO, đối chiếu Bảng 2 pinout & chốt kiến trúc 4 lớp", "Thống nhất cùng nhóm ở Phase 0–1"],
        ["Lựa chọn linh kiện & BOM", "Chọn & so sánh khối nguồn (TVS, P-MOS, Buck TPS54202, Mux TPS2116, LDO AP2114H)", "Chọn khối MCU N16R8, USB-C/ESD, chuyển mức SN74LV1T34, 12 Grove, QWIIC, Servo & tra mã LCSC", "100% đồng bộ 43 mã MPN / 74 linh kiện"],
        ["Schematic & ERC", "Thiết kế trang 01_Power_Supply & 02_MCU_ESP32S3, xây thư viện tự chứa", "Thiết kế trang 03_USB_and_LEDs & 04_Peripherals_and_Headers, rà soát ERC 0 lỗi", "Đạt 0 Errors / 0 Warnings"],
        ["Layout PCB 4 lớp, DRC & 3D", "Định hình Edge.Cuts UNO R3, stack-up 4 lớp, đi dây cặp USB 90 Ω, Buck & vùng đồng", "Bố trí 12 Grove/Servo/SMD mặt dưới, sửa mô hình 3D STEP, rà soát DRC 0 lỗi & xuất Gerber", "Đạt 0 DRC / 0 Unconnected / 0 Parity"],
        ["Trả lời câu hỏi Câu [1]–[13]", "Chủ trì tính toán & trích dẫn datasheet Câu [1]–[6] và Câu [13]", "Chủ trì tính toán & trích dẫn datasheet Câu [7]–[12], kiểm chéo số liệu Python", "Cả hai thành viên nắm vững cả 13 câu"],
        ["Hướng dẫn KiCad, báo cáo & AI Log", "Biên soạn mục 1–5, mục 8 (hướng dẫn KiCad 10) và đóng gói hồ sơ nộp ZIP", "Biên soạn mục 6–7, mục 9–11, Phụ lục BOM/Tài liệu tham khảo và rà soát PDF", "Cùng duyệt cuối trước khi nộp"],
        ["Tỉ lệ đóng góp (%)", "50 %", "50 %", "Hoàn thành đúng tiến độ"],
    ],
    col_widths_cm=[3.4, 4.8, 4.8, 3.8],
    font_size=8.8,
)


# ==============================================================================
# MỤC 11. KẾT LUẬN
# ==============================================================================
add_h1("11. Kết luận")

add_p(
    "Nhóm đã hoàn thành thiết kế lại trọn vẹn bo mạch Yolo UNO sử dụng vi điều khiển ESP32-S3-WROOM-1-N16R8 theo chuẩn cơ khí Arduino UNO R3 "
    "(68,58 × 53,34 mm) trên cấu trúc PCB 4 lớp chuyên nghiệp bằng KiCad 10.0.8. Toàn bộ 11 yêu cầu kỹ thuật R1–R11 đều được đáp ứng 100% "
    "và kiểm chứng nghiêm ngặt: sơ đồ nguyên lý phân cấp 5 trang A3 đạt 0 Errors / 0 Warnings ERC; layout PCB 4 lớp đạt 0 DRC Violations / "
    "0 Unconnected Pads / 0 Schematic Parity Errors với hai lớp nội hoàn toàn thuần khiết (In1.Cu 100% GND liền mạch, In2.Cu 100% nguồn tách +3V3/+5V, "
    "cặp vi sai USB 90 Ω lệch dài chỉ 0,67 mm, trục Servo +5V rộng 1,30 mm kết hợp mặt phẳng +5V, và anten ESP32-S3 không có đồng ở cả 4 lớp). "
    "Bộ sản phẩm kèm đầy đủ 5 ảnh 3D raytracing sắc nét, mô hình cơ khí STEP, BOM thương mại (ước tính $11,30 USD/bo chưa tính gia công PCB), "
    "tệp Pick-and-Place CPL và bộ Gerber/Excellon sẵn sàng đặt mạch thực tế."
)
add_p(
    "Hạn chế còn tồn tại và hướng cải tiến trong phiên bản v2.0: (1) Bộ Buck TPS54202 định mức 2 A đáp ứng tốt 4 servo SG90 hoạt động bình thường "
    "nhưng chưa chịu được kịch bản kẹt cơ khí đồng thời cả 4 servo (~3 A) — phiên bản tiếp theo có thể nâng lên IC Buck 3 A (như TPS54302 hoặc AP63300) "
    "và bổ sung cầu chì tự phục hồi PTC hoặc IC eFuse bảo vệ quá dòng riêng cho cụm Servo/Grove; (2) Có thể tích hợp thêm mạch sạc pin Li-ion 1S (BQ25895/TP4056 + boost 5 V) "
    "để hỗ trợ ứng dụng robot di động không dây; (3) Bổ sung công tắc gạt cứng chọn 3,3 V / 5 V cho từng nhóm cổng Grove nếu cần tương thích trực tiếp với các cảm biến Grove 5 V cũ mà không cần hàn jumper."
)


# ==============================================================================
# PHỤ LỤC A, B, C
# ==============================================================================
add_h1("Phụ lục", page_break=True)

add_h2("Phụ lục A: Bảng kê vật tư đầy đủ (Full Bill of Materials — 74 linh kiện điện / 43 mã MPN)")
add_p("Bảng BOM đầy đủ đồng bộ 1-1 với sơ đồ nguyên lý và PCB (chi tiết file Excel đa trang nằm trong outputs/bom/YoloUNO_BOM_Final.xlsx):")

bom_rows = []
tot_q, tot_p = 0, 0.0
with open(BOM_CSV, "r", encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        q = int(r["Qty"])
        ep = float(r["Ext_Price_USD"])
        tot_q += q
        tot_p += ep
        bom_rows.append([
            r["Item"], r["Designator"], str(q), r["Value"],
            r["Footprint"][:26], r["MPN"], r["LCSC"], f"${ep:.2f}"
        ])
bom_rows.append(["TỔNG", "57 dòng (43 MPN)", str(tot_q), "74 linh kiện điện (+7 cơ khí)", "81 footprint tổng", "Ước tính BOM", "LCSC/DigiKey", f"${tot_p:.2f}"])

add_styled_table(
    ["#", "Designator", "SL", "Giá trị", "Footprint", "MPN", "LCSC", "Thành tiền"],
    bom_rows,
    col_widths_cm=[0.8, 2.3, 0.8, 2.8, 3.6, 3.1, 1.7, 1.7],
    font_size=7.4,
    center_cols=[0, 2, 6, 7],
    cell_pad=34,
)

add_h2("Phụ lục B: Sơ đồ nguyên lý PDF toàn bộ (5 trang A3)")
add_p(
    "Toàn bộ 5 trang sơ đồ nguyên lý khổ A3 vector độ phân giải vô hạn được xuất trực tiếp từ KiCad 10.0.8 và đính kèm trong hồ sơ nộp bài "
    "tại tệp YoloUNO_Schematic.pdf (gồm: Trang 1 — Root Hierarchical Sheet; Trang 2 — 01_Power_Supply; Trang 3 — 02_MCU_ESP32S3; "
    "Trang 4 — 03_USB_and_LEDs; Trang 5 — 04_Peripherals_and_Headers)."
)

add_h2("Phụ lục C: Tài liệu tham khảo và Datasheet chính thức")
refs = [
    "[1] Espressif Systems, ESP32-S3-WROOM-1 / ESP32-S3-WROOM-1U Datasheet, v1.5. https://www.espressif.com/sites/default/files/documentation/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf",
    "[2] Espressif Systems, ESP32-S3 Series Datasheet (v1.9) & ESP32-S3 Hardware Design Guidelines. https://docs.espressif.com",
    "[3] Texas Instruments, TPS54202 4.5-V to 28-V Input, 2-A Output, EMI Friendly Synchronous Step-Down Converter Datasheet (SLVSDF5).",
    "[4] Texas Instruments, TPS2116 1.6-V to 5.5-V, 2.5-A Low IQ Priority Power Multiplexer Datasheet (SLVSFJ9).",
    "[5] Diodes Incorporated, AP2114 1A Low Noise CMOS LDO Regulator with Enable Datasheet (DS31304).",
    "[6] Texas Instruments, SN74LV1T34 Single Power Supply Single Buffer Gate CMOS Logic Level Shifter Datasheet (SCLS738).",
    "[7] STMicroelectronics, USBLC6-2SC6 Very Low Capacitance ESD Protection Datasheet (DS5092).",
    "[8] Alpha & Omega Semiconductor, AO3407A 30V P-Channel MOSFET Datasheet.",
    "[9] Littelfuse, SMBJ Series 600W Surface Mount TVS Diode Datasheet (SMBJ15CA).",
    "[10] Bourns, SRN6045TA Series Semi-Shielded Power Inductors Datasheet (SRN6045TA-150M).",
    "[11] Worldsemi, WS2812B Intelligent Control LED Integrated Light Source Datasheet.",
    "[12] Arduino, Arduino UNO Rev3 Official Documentation & Mechanical Drawing. https://docs.arduino.cc/hardware/uno-rev3",
    "[13] Seeed Studio, Grove System Hardware Specification. https://wiki.seeedstudio.com/Grove_System/",
    "[14] SparkFun Electronics, Qwiic Connect System Specification (JST SH 4-pin 1.0 mm). https://www.sparkfun.com/qwiic",
    "[15] NXP Semiconductors, UM10204 — I²C-bus Specification and User Manual, Rev. 7.0 (2021).",
    "[16] USB Implementers Forum (USB-IF), Universal Serial Bus Type-C Cable and Connector Specification, Release 2.2.",
    "[17] IPC Association Connecting Electronics Industries, IPC-2221A Generic Standard on Printed Board Design (Section 6.2).",
    "[18] KiCad Developers, KiCad 10.0 Documentation & kicad-cli Reference. https://docs.kicad.org",
]
for rf in refs:
    add_p(rf, space_after=2.5)

doc.save(OUT_DOCX)
print(f"[SUCCESS] Generated complete Vietnamese Phần B report: {OUT_DOCX} ({os.path.getsize(OUT_DOCX)/1024/1024:.2f} MB)")
