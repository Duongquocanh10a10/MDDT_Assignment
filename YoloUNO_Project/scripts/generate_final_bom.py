#!/usr/bin/env python3
"""
Phase 4: Generate Final Production BOM (.csv & multi-sheet styled .xlsx) for Yolo UNO (ESP32-S3).
Cross-verifies 1-to-1 designator parity with KiCad schematic export (YoloUNO_KiCad_BOM.csv).
"""

import os
import sys
import csv
import re

sys.path.insert(0, r"D:\YoloUNO_pylibs")
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

ROOT = r"c:\Users\QUOC ANH PC\Downloads\MDDT_Assignment\YoloUNO_Project"
SRC_BOM = os.path.join(ROOT, "bom", "YoloUNO_BOM.csv")
KICAD_BOM = os.path.join(ROOT, "outputs", "YoloUNO_KiCad_BOM.csv")
OUT_DIR = os.path.join(ROOT, "outputs", "bom")
OUT_CSV = os.path.join(OUT_DIR, "YoloUNO_BOM_Final.csv")
OUT_XLSX = os.path.join(OUT_DIR, "YoloUNO_BOM_Final.xlsx")
os.makedirs(OUT_DIR, exist_ok=True)

# Typical single/small-batch (10-unit) LCSC / DigiKey reference unit prices (USD)
EST_UNIT_PRICE = {
    "PJ-002A": 0.45,
    "SMBJ15CA": 0.08,
    "AO3407A": 0.06,
    "BZT52C10-7-F": 0.04,
    "RC0603FR-0747KL": 0.01,
    "EEE-FK1E470P": 0.22,
    "CL10B104KB8NNNC": 0.01,
    "TPS54202DDCR": 0.65,
    "GRM21BR61E106KA73L": 0.06,
    "SRN6045TA-150M": 0.42,
    "RC0603FR-07100KL": 0.01,
    "RC0603FR-0768KL": 0.01,
    "RC0603FR-079K1L": 0.01,
    "GRM21BR61C226ME44L": 0.07,
    "TPS2116DRLR": 0.88,
    "RC0603FR-0736KL": 0.01,
    "RC0603FR-0710KL": 0.01,
    "CL21A106KOQNNNE": 0.04,
    "AP2114H-3.3TRG1": 0.28,
    "19-217/GHC-YR1S2/3T": 0.04,
    "RC0603FR-07470RL": 0.01,
    "ESP32-S3-WROOM-1-N16R8": 3.80,
    "CL10B105KO8NNNC": 0.02,
    "TS-1187A-B-A-B": 0.08,
    "TYPE-C-31-M-12": 0.24,
    "RC0603FR-075K1L": 0.01,
    "USBLC6-2SC6": 0.14,
    "19-217/R6C-AL1M2VY/3T": 0.03,
    "RC0603FR-07270RL": 0.01,
    "SN74LV1T34DBVR": 0.16,
    "WS2812B-B/W": 0.12,
    "RC0603FR-071K5L": 0.01,
    "RC0603FR-076K8L": 0.01,
    "SJ-3-1.3MM": 0.00,
    "EEE-FK1A471P": 0.34,
    "110990030": 0.14,
    "112060001": 0.14,
    "110990031": 0.14,
    "SM04B-SRSS-TB": 0.18,
    "FH-254-1x08": 0.12,
    "FH-254-1x06": 0.10,
    "FH-254-1x10": 0.14,
    "X6511WV-1x3": 0.04,
}


def expand_refs(ref_str):
    out = []
    for tok in [t.strip() for t in ref_str.split(",") if t.strip()]:
        m = re.match(r"^([A-Za-z]+)(\d+)-\1?(\d+)$", tok)
        if m:
            pfx, a, b = m.group(1), int(m.group(2)), int(m.group(3))
            for k in range(a, b + 1):
                out.append(f"{pfx}{k}")
        else:
            out.append(tok)
    return out


# 1. Read KiCad BOM and extract exact set of placed designators
kicad_refs = set()
with open(KICAD_BOM, "r", encoding="utf-8-sig") as f:
    for row in csv.DictReader(f):
        kicad_refs.update(expand_refs(row["Refs"]))

# 2. Read curated BOM and verify 100% designator parity
rows = []
bom_refs = set()
with open(SRC_BOM, "r", encoding="utf-8-sig") as f:
    for row in csv.DictReader(f):
        refs = expand_refs(row["Designator"])
        qty = int(row["Quantity"])
        assert len(refs) == qty, f"Qty mismatch on {row['Designator']}: {len(refs)} vs {qty}"
        bom_refs.update(refs)
        mpn = row["MPN"].strip()
        up = EST_UNIT_PRICE[mpn]
        rows.append({
            "Item": len(rows) + 1,
            "Block": row["Block"].strip(),
            "Designator": row["Designator"].strip(),
            "Qty": qty,
            "Value": row["Value"].strip(),
            "Description": row["Description"].strip(),
            "Footprint": row["Footprint"].replace("YoloUNO:", "").strip(),
            "Manufacturer": row["Manufacturer"].strip(),
            "MPN": mpn,
            "LCSC": row["LCSC_Part"].strip(),
            "Unit_Price_USD": up,
            "Ext_Price_USD": round(up * qty, 4),
            "Datasheet": row["Datasheet_Source"].strip(),
        })

assert bom_refs == kicad_refs, f"BOM vs KiCad parity mismatch! extra_bom={bom_refs - kicad_refs}, extra_kicad={kicad_refs - bom_refs}"
total_qty = sum(r["Qty"] for r in rows)
total_cost = sum(r["Ext_Price_USD"] for r in rows)
print(f"[VERIFIED] 100% 1-to-1 BOM parity with KiCad schematic: {len(bom_refs)} electrical parts ({len(rows)} block rows), Est. Cost = ${total_cost:.2f} USD")

# 3. Write clean UTF-8-SIG Final CSV
csv_fields = ["Item", "Block", "Designator", "Qty", "Value", "Description", "Footprint", "Manufacturer", "MPN", "LCSC", "Unit_Price_USD", "Ext_Price_USD", "Datasheet"]
with open(OUT_CSV, "w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=csv_fields)
    w.writeheader()
    for r in rows:
        w.writerow(r)
print(f"Wrote {OUT_CSV}")

# 4. Build consolidated MPN view (grouped by MPN for LCSC/JLCPCB ordering)
mpn_groups = {}
for r in rows:
    k = r["MPN"]
    if k not in mpn_groups:
        mpn_groups[k] = {
            "MPN": k,
            "LCSC": r["LCSC"],
            "Manufacturer": r["Manufacturer"],
            "Value": r["Value"],
            "Description": r["Description"],
            "Footprint": r["Footprint"],
            "Refs": [],
            "Qty": 0,
            "Unit_Price_USD": r["Unit_Price_USD"],
        }
    mpn_groups[k]["Refs"].extend(expand_refs(r["Designator"]))
    mpn_groups[k]["Qty"] += r["Qty"]

# Sort consolidated rows nicely by reference prefix
def ref_sort_key(ref):
    m = re.match(r"([A-Za-z]+)(\d+)", ref)
    return (m.group(1), int(m.group(2))) if m else (ref, 0)

cons_rows = []
for g in mpn_groups.values():
    g["Refs"].sort(key=ref_sort_key)
    g["Designator"] = ", ".join(g["Refs"])
    cons_rows.append(g)
cons_rows.sort(key=lambda g: ref_sort_key(g["Refs"][0]))

# 5. Build professionally styled multi-sheet Excel workbook (.xlsx)
wb = openpyxl.Workbook()

# Shared styles
navy_fill = PatternFill("solid", fgColor="1B365D")
sub_fill = PatternFill("solid", fgColor="D9E2EC")
zebra_fill = PatternFill("solid", fgColor="F7FAFC")
total_fill = PatternFill("solid", fgColor="E6F4EA")
hdr_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
title_font = Font(name="Calibri", size=14, bold=True, color="1B365D")
sub_font = Font(name="Calibri", size=10, italic=True, color="486581")
body_font = Font(name="Calibri", size=10)
bold_font = Font(name="Calibri", size=10, bold=True)
thin = Side(style="thin", color="CBD5E0")
med_navy = Side(style="medium", color="1B365D")
cell_border = Border(left=thin, right=thin, top=thin, bottom=thin)
total_border = Border(left=thin, right=thin, top=med_navy, bottom=med_navy)

# --- Sheet 1: BOM_By_Block ---
ws1 = wb.active
ws1.title = "BOM_By_Block"
ws1.views.sheetView[0].showGridLines = True

ws1.merge_cells("A1:M1")
ws1["A1"] = "YOLO UNO (ESP32-S3-WROOM-1-N16R8) — Production Bill of Materials (By Functional Block)"
ws1["A1"].font = title_font
ws1["A1"].alignment = Alignment(vertical="center")
ws1.row_dimensions[1].height = 24

ws1.merge_cells("A2:M2")
ws1["A2"] = "HCMUT CO2037 Project 1 | 4-Layer FR4 Arduino UNO R3 (68.58 x 53.34 mm) | ERC: 0 Violations | DRC: 0 Violations / 0 Unconnected / 0 Parity"
ws1["A2"].font = sub_font
ws1.row_dimensions[2].height = 18

headers1 = ["Item", "Functional Block", "Designator", "Qty", "Value", "Description", "Footprint", "Manufacturer", "MPN", "LCSC Part#", "Est. Unit ($)", "Est. Ext ($)", "Datasheet Reference"]
ws1.append([])  # row 3 blank
ws1.append(headers1)  # row 4 headers
ws1.row_dimensions[4].height = 22
for col_i in range(1, len(headers1) + 1):
    c = ws1.cell(row=4, column=col_i)
    c.fill = navy_fill
    c.font = hdr_font
    c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    c.border = cell_border

for idx, r in enumerate(rows, start=5):
    vals = [
        r["Item"], r["Block"], r["Designator"], r["Qty"], r["Value"], r["Description"],
        r["Footprint"], r["Manufacturer"], r["MPN"], r["LCSC"], r["Unit_Price_USD"],
        f"=D{idx}*K{idx}", r["Datasheet"]
    ]
    ws1.append(vals)
    ws1.row_dimensions[idx].height = 19
    is_even = (idx % 2 == 0)
    for col_i in range(1, len(vals) + 1):
        c = ws1.cell(row=idx, column=col_i)
        c.font = body_font
        c.border = cell_border
        if is_even:
            c.fill = zebra_fill
        if col_i in (1, 4, 10):
            c.alignment = Alignment(horizontal="center", vertical="center")
        elif col_i in (11, 12):
            c.alignment = Alignment(horizontal="right", vertical="center")
            c.number_format = "$#,##0.00"
        else:
            c.alignment = Alignment(horizontal="left", vertical="center")

tot_row = 5 + len(rows)
ws1.cell(row=tot_row, column=1, value="TOTAL").font = bold_font
ws1.cell(row=tot_row, column=3, value=f"{len(rows)} line items").font = bold_font
ws1.cell(row=tot_row, column=4, value=f"=SUM(D5:D{tot_row-1})").font = bold_font
ws1.cell(row=tot_row, column=11, value="Est. BOM:").font = bold_font
ws1.cell(row=tot_row, column=12, value=f"=SUM(L5:L{tot_row-1})").font = bold_font
ws1.row_dimensions[tot_row].height = 22
for col_i in range(1, len(headers1) + 1):
    c = ws1.cell(row=tot_row, column=col_i)
    c.fill = total_fill
    c.border = total_border
    if col_i == 4:
        c.alignment = Alignment(horizontal="center", vertical="center")
    elif col_i == 12:
        c.alignment = Alignment(horizontal="right", vertical="center")
        c.number_format = "$#,##0.00"

ws1.freeze_panes = "A5"
widths1 = [6, 26, 16, 6, 22, 46, 36, 24, 24, 12, 12, 12, 34]
for i, w in enumerate(widths1, start=1):
    ws1.column_dimensions[get_column_letter(i)].width = w

# --- Sheet 2: BOM_Consolidated_MPN (For Ordering) ---
ws2 = wb.create_sheet("BOM_Consolidated_MPN")
ws2.merge_cells("A1:J1")
ws2["A1"] = f"YOLO UNO — Consolidated Procurement BOM ({len(cons_rows)} Unique MPNs / {total_qty} Total Placed Components)"
ws2["A1"].font = title_font
ws2.row_dimensions[1].height = 24

headers2 = ["#", "Designators", "Qty", "Value", "Description", "Footprint", "Manufacturer", "MPN", "LCSC Part#", "Est. Ext ($)"]
ws2.append([])
ws2.append(headers2)  # row 3
ws2.row_dimensions[3].height = 22
for col_i in range(1, len(headers2) + 1):
    c = ws2.cell(row=3, column=col_i)
    c.fill = navy_fill
    c.font = hdr_font
    c.alignment = Alignment(horizontal="center", vertical="center")
    c.border = cell_border

for i, g in enumerate(cons_rows, start=1):
    r_idx = 3 + i
    vals = [
        i, g["Designator"], g["Qty"], g["Value"], g["Description"],
        g["Footprint"], g["Manufacturer"], g["MPN"], g["LCSC"], round(g["Unit_Price_USD"] * g["Qty"], 2)
    ]
    ws2.append(vals)
    ws2.row_dimensions[r_idx].height = 19
    for col_i in range(1, len(vals) + 1):
        c = ws2.cell(row=r_idx, column=col_i)
        c.font = body_font
        c.border = cell_border
        if r_idx % 2 == 0:
            c.fill = zebra_fill
        if col_i in (1, 3, 9):
            c.alignment = Alignment(horizontal="center", vertical="center")
        elif col_i == 10:
            c.alignment = Alignment(horizontal="right", vertical="center")
            c.number_format = "$#,##0.00"

tot2 = 4 + len(cons_rows)
ws2.cell(row=tot2, column=1, value="TOTAL").font = bold_font
ws2.cell(row=tot2, column=2, value=f"{len(cons_rows)} unique MPNs").font = bold_font
ws2.cell(row=tot2, column=3, value=f"=SUM(C4:C{tot2-1})").font = bold_font
ws2.cell(row=tot2, column=10, value=f"=SUM(J4:J{tot2-1})").font = bold_font
for col_i in range(1, len(headers2) + 1):
    c = ws2.cell(row=tot2, column=col_i)
    c.fill = total_fill
    c.border = total_border
    if col_i == 3:
        c.alignment = Alignment(horizontal="center", vertical="center")
    elif col_i == 10:
        c.alignment = Alignment(horizontal="right", vertical="center")
        c.number_format = "$#,##0.00"

ws2.freeze_panes = "A4"
widths2 = [5, 32, 6, 22, 46, 36, 24, 24, 12, 13]
for i, w in enumerate(widths2, start=1):
    ws2.column_dimensions[get_column_letter(i)].width = w

# --- Sheet 3: PCB_DFM_Summary ---
ws3 = wb.create_sheet("PCB_DFM_Summary")
ws3.merge_cells("A1:B1")
ws3["A1"] = "Yolo UNO (ESP32-S3) — Board & Manufacturing Summary"
ws3["A1"].font = title_font
ws3.row_dimensions[1].height = 24

summary_rows = [
    ("Project", "HCMUT CO2037 Project 1 — Redesign of Yolo UNO (ESP32-S3-WROOM-1-N16R8)"),
    ("EDA Tool", "KiCad 10.0.8 (Self-contained YoloUNO.kicad_sym & YoloUNO.pretty libraries)"),
    ("Form Factor", "Arduino UNO R3 (68.58 x 53.34 mm, East notch, R=1.5 mm West fillets)"),
    ("PCB Stackup", "4-Layer FR4 (1.60 mm, 1 oz): F.Cu / In1.Cu Solid GND / In2.Cu Split +3V3 & +5V / B.Cu"),
    ("Design Rules", "IPC-2221 Class 2 (min track 0.15 mm, min clearance 0.15 mm, vias 0.60/0.30 mm)"),
    ("Total PCB Footprints", "81 total (74 placed electrical BOM parts + 4x M3 Mounting Holes H1-H4 + 3x Fiducials FID1-FID3)"),
    ("Unique Procurement MPNs", f"{len(cons_rows)} unique MPNs (estimated prototype BOM cost: ${total_cost:.2f} USD/board excl. PCB fab)"),
    ("Schematic ERC Result", "0 Errors, 0 Warnings (5 hierarchical A3 sheets, 65 nets)"),
    ("PCB DRC Result", "0 Violations, 0 Unconnected Items, 0 Schematic Parity / Footprint Errors"),
    ("Signal Integrity Highlights", "USB 90-Ohm diff pair skew = 0.67 mm (<=7.5 mm); Buck SW 0 vias (>52 mm from antenna); RF 4-layer keepout"),
    ("Power & Thermal Highlights", "Servo +5V 1.30 mm F.Cu backbone + 623.5 mm2 In2.Cu plane; AP2114H-3.3 20.4 mm2 thermal pad + 4 vias"),
    ("Manufacturing Exports", "RS-274X Gerbers (11 layers + gbrjob), Excellon Drills (PTH + NPTH + PDF Map), CPL Pick-and-Place CSV"),
]
for idx, (k, v) in enumerate(summary_rows, start=3):
    c1 = ws3.cell(row=idx, column=1, value=k)
    c2 = ws3.cell(row=idx, column=2, value=v)
    c1.font = bold_font
    c2.font = body_font
    c1.fill = sub_fill
    c1.border = cell_border
    c2.border = cell_border
    ws3.row_dimensions[idx].height = 20
ws3.column_dimensions["A"].width = 28
ws3.column_dimensions["B"].width = 96

wb.save(OUT_XLSX)
print(f"Wrote {OUT_XLSX} ({len(cons_rows)} unique MPNs, {total_qty} total electrical parts, Est. ${total_cost:.2f} USD)")
