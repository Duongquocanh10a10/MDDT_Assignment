#!/usr/bin/env python3
"""
Phase 5 Step 3: Assemble & Verify Final Submission Package `2410053_2510284_Project1.zip`
Strictly follows HCMUT CO2037 Project 1 Table 3 deliverables and verifies:
  1. Self-contained `YoloUNO_KiCad_Project.zip` (no locks/caches/backups)
  2. Standalone portability test: extracts `YoloUNO_KiCad_Project.zip` to a clean folder on D:
     and runs KiCad 10 CLI ERC + DRC (--severity-all --schematic-parity --exit-code-violations)
  3. Final archive `2410053_2510284_Project1.zip` placed at workspace root with clean Table 3 layout
"""

import os
import shutil
import subprocess
import zipfile

WORKSPACE = r"c:\Users\QUOC ANH PC\Downloads\MDDT_Assignment"
PROJ_ROOT = os.path.join(WORKSPACE, "YoloUNO_Project")
HW_DIR = os.path.join(PROJ_ROOT, "hardware")
OUT_DIR = os.path.join(PROJ_ROOT, "outputs")
KICAD_CLI = r"D:\KiCad\bin\kicad-cli.exe"

INNER_KICAD_ZIP = os.path.join(OUT_DIR, "YoloUNO_KiCad_Project.zip")
FINAL_ZIP = os.path.join(WORKSPACE, "2410053_2510284_Project1.zip")
VERIFY_DIR = r"D:\YoloUNO_verify_extract"

EXCLUDE_DIRS = {"YoloUNO-backups", "__pycache__", ".git"}
EXCLUDE_EXTS = {".lck", ".bak", ".kicad_pcb-bak", ".kicad_sch-bak", ".kicad_prl"}
EXCLUDE_NAMES = {"fp-info-cache", ".DS_Store", "Thumbs.db"}


def build_inner_kicad_zip():
    if os.path.exists(INNER_KICAD_ZIP):
        os.remove(INNER_KICAD_ZIP)
    count = 0
    with zipfile.ZipFile(INNER_KICAD_ZIP, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for root, dirs, files in os.walk(HW_DIR):
            dirs[:] = sorted(d for d in dirs if d not in EXCLUDE_DIRS and not d.endswith("-backups"))
            for fname in sorted(files):
                if fname in EXCLUDE_NAMES or fname.startswith("~"):
                    continue
                if any(fname.endswith(ext) for ext in EXCLUDE_EXTS):
                    continue
                fpath = os.path.join(root, fname)
                rel = os.path.relpath(fpath, HW_DIR)
                arcname = os.path.join("YoloUNO", rel).replace("\\", "/")
                zf.write(fpath, arcname)
                count += 1
    size_kb = os.path.getsize(INNER_KICAD_ZIP) / 1024
    print(f"[OK] Built self-contained KiCad ZIP: {INNER_KICAD_ZIP} ({count} files, {size_kb:.1f} KB)")


def verify_portability():
    if os.path.exists(VERIFY_DIR):
        shutil.rmtree(VERIFY_DIR)
    os.makedirs(VERIFY_DIR, exist_ok=True)
    with zipfile.ZipFile(INNER_KICAD_ZIP, "r") as zf:
        zf.extractall(VERIFY_DIR)

    sch = os.path.join(VERIFY_DIR, "YoloUNO", "YoloUNO.kicad_sch")
    pcb = os.path.join(VERIFY_DIR, "YoloUNO", "YoloUNO.kicad_pcb")
    erc_out = os.path.join(VERIFY_DIR, "erc_check.rpt")
    drc_out = os.path.join(VERIFY_DIR, "drc_check.rpt")

    r_erc = subprocess.run(
        [KICAD_CLI, "sch", "erc", "--severity-all", "--exit-code-violations", "-o", erc_out, sch],
        capture_output=True, text=True
    )
    print(f"[PORTABILITY TEST] Extracted ERC exit={r_erc.returncode}")
    if r_erc.returncode != 0:
        print(r_erc.stdout, r_erc.stderr)
        raise RuntimeError("Extracted KiCad project failed ERC!")

    r_drc = subprocess.run(
        [KICAD_CLI, "pcb", "drc", "--severity-all", "--refill-zones", "--schematic-parity",
         "--exit-code-violations", "-o", drc_out, pcb],
        capture_output=True, text=True
    )
    print(f"[PORTABILITY TEST] Extracted DRC exit={r_drc.returncode}")
    if r_drc.returncode != 0:
        print(r_drc.stdout, r_drc.stderr)
        raise RuntimeError("Extracted KiCad project failed DRC!")

    shutil.rmtree(VERIFY_DIR)
    print("[OK] Standalone portability verified: 0 ERC / 0 DRC / 0 Parity on fresh isolated extraction!")


def build_final_submission_zip():
    manifest = [
        # 01_Report (DOCX + PDF)
        (os.path.join(OUT_DIR, "report", "2410053_2510284_BaoCao_Project1_YoloUNO.docx"),
         "01_Report/2410053_2510284_BaoCao_Project1_YoloUNO.docx"),
        (os.path.join(OUT_DIR, "report", "2410053_2510284_BaoCao_Project1_YoloUNO.pdf"),
         "01_Report/2410053_2510284_BaoCao_Project1_YoloUNO.pdf"),
        # 02_KiCad_Project (Self-contained ZIP)
        (INNER_KICAD_ZIP,
         "02_KiCad_Project/YoloUNO_KiCad_Project.zip"),
        # 03_3D_Renders (+ 2D PCB layers PDF)
        (os.path.join(OUT_DIR, "3d_renders", "YoloUNO_3D_Top.png"),
         "03_3D_Renders/YoloUNO_3D_Top.png"),
        (os.path.join(OUT_DIR, "3d_renders", "YoloUNO_3D_Bottom.png"),
         "03_3D_Renders/YoloUNO_3D_Bottom.png"),
        (os.path.join(OUT_DIR, "3d_renders", "YoloUNO_3D_Isometric.png"),
         "03_3D_Renders/YoloUNO_3D_Isometric.png"),
        (os.path.join(OUT_DIR, "3d_renders", "YoloUNO_3D_Isometric_WestPorts.png"),
         "03_3D_Renders/YoloUNO_3D_Isometric_WestPorts.png"),
        (os.path.join(OUT_DIR, "3d_renders", "YoloUNO_3D_Isometric_Bottom.png"),
         "03_3D_Renders/YoloUNO_3D_Isometric_Bottom.png"),
        (os.path.join(OUT_DIR, "YoloUNO_PCB_2D_Layers.pdf"),
         "03_3D_Renders/YoloUNO_PCB_2D_Layers.pdf"),
        # 04_Schematic_PDF
        (os.path.join(OUT_DIR, "YoloUNO_Schematic.pdf"),
         "04_Schematic_PDF/YoloUNO_Schematic.pdf"),
        # 05_BOM
        (os.path.join(OUT_DIR, "bom", "YoloUNO_BOM_Final.xlsx"),
         "05_BOM/YoloUNO_BOM_Final.xlsx"),
        (os.path.join(OUT_DIR, "bom", "YoloUNO_BOM_Final.csv"),
         "05_BOM/YoloUNO_BOM_Final.csv"),
        (os.path.join(OUT_DIR, "bom", "YoloUNO_CPL_Pos.csv"),
         "05_BOM/YoloUNO_CPL_Pos.csv"),
        # 06_Gerbers_and_Verification
        (os.path.join(OUT_DIR, "YoloUNO_Gerbers_4Layer.zip"),
         "06_Gerbers_and_Verification/YoloUNO_Gerbers_4Layer.zip"),
        (os.path.join(OUT_DIR, "YoloUNO_3D_Assembly.step"),
         "06_Gerbers_and_Verification/YoloUNO_3D_Assembly.step"),
        (os.path.join(OUT_DIR, "erc_report.rpt"),
         "06_Gerbers_and_Verification/erc_report.rpt"),
        (os.path.join(OUT_DIR, "drc_report.rpt"),
         "06_Gerbers_and_Verification/drc_report.rpt"),
    ]

    for src, _ in manifest:
        if not os.path.exists(src):
            raise FileNotFoundError(f"Missing required deliverable: {src}")

    if os.path.exists(FINAL_ZIP):
        os.remove(FINAL_ZIP)

    with zipfile.ZipFile(FINAL_ZIP, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for src, arc in manifest:
            zf.write(src, arc)

    size_mb = os.path.getsize(FINAL_ZIP) / (1024 * 1024)
    print(f"\n[SUCCESS] Final Submission Archive ready: {FINAL_ZIP} ({size_mb:.2f} MB)")
    print("Archive Contents:")
    with zipfile.ZipFile(FINAL_ZIP, "r") as zf:
        bad = zf.testzip()
        if bad is not None:
            raise RuntimeError(f"Corrupt ZIP entry: {bad}")
        for info in zf.infolist():
            print(f"  - {info.filename:62s} {info.file_size/1024:8.1f} KB")
    print("[OK] ZIP CRC integrity check: PASSED (0 corrupt entries)")


if __name__ == "__main__":
    build_inner_kicad_zip()
    verify_portability()
    build_final_submission_zip()
