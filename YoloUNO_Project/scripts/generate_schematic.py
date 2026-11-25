#!/usr/bin/env python3
"""
Deterministic Multi-Sheet KiCad 10 Schematic Generator for Yolo UNO Redesign (CO2037 Project 1).
- 100% self-contained: bundles all symbols in `libraries/YoloUNO.kicad_sym` (+ `sym-lib-table` + embedded `lib_symbols`)
  and copies all official KiCad 10 footprints into `libraries/YoloUNO.pretty` (+ `fp-lib-table`).
- Generates 5 hierarchical A3 schematic pages covering Blocks 4.1 through 4.8 + Mechanical/Fiducials.
- Visually polished (left/right justified labels, staggered power stubs, zero overlapping text) and passes
  `kicad-cli sch erc --severity-all --exit-code-violations` with 0 errors and 0 warnings.
"""

import os
import re
import math
import json
import uuid
import shutil

KICAD_SYM_DIR = r"D:\KiCad\share\kicad\symbols"
KICAD_FP_DIR = r"D:\KiCad\share\kicad\footprints"
HW_DIR = r"c:\Users\QUOC ANH PC\Downloads\MDDT_Assignment\YoloUNO_Project\hardware"
LIB_DIR = os.path.join(HW_DIR, "libraries")
PRETTY_DIR = os.path.join(LIB_DIR, "YoloUNO.pretty")

os.makedirs(PRETTY_DIR, exist_ok=True)

_uuid_counter = 0
def make_uuid(tag=""):
    global _uuid_counter
    _uuid_counter += 1
    return str(uuid.uuid5(uuid.NAMESPACE_OID, f"yolouno-co2037-v3-{tag}-{_uuid_counter}"))


# ---------------- Copy Self-Contained Footprints ----------------
FOOTPRINT_SOURCES = {
    "BarrelJack_CUI_PJ-102AH_Horizontal": ("Connector_BarrelJack.pretty", "BarrelJack_CUI_PJ-102AH_Horizontal.kicad_mod"),
    "D_SMB": ("Diode_SMD.pretty", "D_SMB.kicad_mod"),
    "SOT-23-3": ("Package_TO_SOT_SMD.pretty", "SOT-23-3.kicad_mod"),
    "SOT-23-5": ("Package_TO_SOT_SMD.pretty", "SOT-23-5.kicad_mod"),
    "SOT-23-6": ("Package_TO_SOT_SMD.pretty", "SOT-23-6.kicad_mod"),
    "SOT-583-8": ("Package_TO_SOT_SMD.pretty", "SOT-583-8.kicad_mod"),
    "SOT-223-3_TabPin2": ("Package_TO_SOT_SMD.pretty", "SOT-223-3_TabPin2.kicad_mod"),
    "D_SOD-123": ("Diode_SMD.pretty", "D_SOD-123.kicad_mod"),
    "R_0603_1608Metric": ("Resistor_SMD.pretty", "R_0603_1608Metric.kicad_mod"),
    "C_0603_1608Metric": ("Capacitor_SMD.pretty", "C_0603_1608Metric.kicad_mod"),
    "C_0805_2012Metric": ("Capacitor_SMD.pretty", "C_0805_2012Metric.kicad_mod"),
    "CP_Elec_6.3x5.4": ("Capacitor_SMD.pretty", "CP_Elec_6.3x5.4.kicad_mod"),
    "CP_Elec_8x10.5": ("Capacitor_SMD.pretty", "CP_Elec_8x10.5.kicad_mod"),
    "L_Bourns_SRN6045TA": ("Inductor_SMD.pretty", "L_Bourns_SRN6045TA.kicad_mod"),
    "ESP32-S3-WROOM-1": ("RF_Module.pretty", "ESP32-S3-WROOM-1.kicad_mod"),
    "SW_Push_1P1T_XKB_TS-1187A": ("Button_Switch_SMD.pretty", "SW_Push_1P1T_XKB_TS-1187A.kicad_mod"),
    "USB_C_Receptacle_HRO_TYPE-C-31-M-12": ("Connector_USB.pretty", "USB_C_Receptacle_HRO_TYPE-C-31-M-12.kicad_mod"),
    "LED_0603_1608Metric": ("LED_SMD.pretty", "LED_0603_1608Metric.kicad_mod"),
    "LED_WS2812B_PLCC4_5.0x5.0mm_P3.2mm": ("LED_SMD.pretty", "LED_WS2812B_PLCC4_5.0x5.0mm_P3.2mm.kicad_mod"),
    "SolderJumper-3_P1.3mm_Bridged12_Pad1.0x1.5mm": ("Jumper.pretty", "SolderJumper-3_P1.3mm_Bridged12_Pad1.0x1.5mm.kicad_mod"),
    "NS-Tech_Grove_1x04_P2mm_Vertical": ("Connector.pretty", "NS-Tech_Grove_1x04_P2mm_Vertical.kicad_mod"),
    "JST_SH_SM04B-SRSS-TB_1x04-1MP_P1.00mm_Horizontal": ("Connector_JST.pretty", "JST_SH_SM04B-SRSS-TB_1x04-1MP_P1.00mm_Horizontal.kicad_mod"),
    "PinHeader_1x03_P2.54mm_Vertical": ("Connector_PinHeader_2.54mm.pretty", "PinHeader_1x03_P2.54mm_Vertical.kicad_mod"),
    "PinSocket_1x06_P2.54mm_Vertical": ("Connector_PinSocket_2.54mm.pretty", "PinSocket_1x06_P2.54mm_Vertical.kicad_mod"),
    "PinSocket_1x08_P2.54mm_Vertical": ("Connector_PinSocket_2.54mm.pretty", "PinSocket_1x08_P2.54mm_Vertical.kicad_mod"),
    "PinSocket_1x10_P2.54mm_Vertical": ("Connector_PinSocket_2.54mm.pretty", "PinSocket_1x10_P2.54mm_Vertical.kicad_mod"),
    "MountingHole_3.2mm_M3": ("MountingHole.pretty", "MountingHole_3.2mm_M3.kicad_mod"),
    "Fiducial_1mm_Mask2mm": ("Fiducial.pretty", "Fiducial_1mm_Mask2mm.kicad_mod"),
}

for fp_name, (src_pretty, src_mod) in FOOTPRINT_SOURCES.items():
    dst_fp = os.path.join(PRETTY_DIR, f"{fp_name}.kicad_mod")
    if not os.path.exists(dst_fp):
        shutil.copyfile(os.path.join(KICAD_FP_DIR, src_pretty, src_mod), dst_fp)

fp_lib_table_txt = """(fp_lib_table
  (version 7)
  (lib (name "YoloUNO")(type "KiCad")(uri "${KIPRJMOD}/libraries/YoloUNO.pretty")(options "")(descr "Yolo UNO Project Self-Contained Footprint Library"))
)
"""
with open(os.path.join(HW_DIR, "fp-lib-table"), "w", encoding="utf-8") as f:
    f.write(fp_lib_table_txt)


# ---------------- S-expression parser & serializer ----------------
def tokenize(s):
    tokens, i, n = [], 0, len(s)
    while i < n:
        c = s[i]
        if c.isspace():
            i += 1
        elif c in "()":
            tokens.append(c)
            i += 1
        elif c == '"':
            j = i + 1
            buf = ['"']
            while j < n:
                if s[j] == "\\" and j + 1 < n:
                    buf.append(s[j : j + 2])
                    j += 2
                elif s[j] == '"':
                    buf.append('"')
                    j += 1
                    break
                else:
                    buf.append(s[j])
                    j += 1
            tokens.append("".join(buf))
            i = j
        else:
            j = i
            while j < n and (not s[j].isspace()) and s[j] not in '()"':
                j += 1
            tokens.append(s[i:j])
            i = j
    return tokens


def parse_sexp(s):
    tokens = tokenize(s)
    pos = 0

    def read():
        nonlocal pos
        tok = tokens[pos]
        pos += 1
        if tok == "(":
            lst = []
            while tokens[pos] != ")":
                lst.append(read())
            pos += 1
            return lst
        return tok

    return read()


def unq(s):
    return s[1:-1] if isinstance(s, str) and s.startswith('"') and s.endswith('"') else s


def q(s):
    escaped = str(s).replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
    return f'"{escaped}"'


def fmt_num(v):
    if abs(v - round(v)) < 1e-6:
        return str(int(round(v)))
    s = f"{v:.4f}".rstrip("0").rstrip(".")
    return "0" if s == "-0" else s


def dump_sexp(node, indent=0):
    sp = "\t" * indent
    if not isinstance(node, list):
        return str(node)
    if not node:
        return "()"
    head = str(node[0])
    if all(not isinstance(x, list) for x in node):
        return f"({' '.join(str(x) for x in node)})"
    lines = [f"{sp}({head}"]
    idx = 1
    first_atoms = []
    while idx < len(node) and not isinstance(node[idx], list):
        first_atoms.append(str(node[idx]))
        idx += 1
    if first_atoms:
        lines[0] += " " + " ".join(first_atoms)
    for child in node[idx:]:
        if isinstance(child, list):
            if all(not isinstance(x, list) for x in child) and len(child) <= 5:
                lines.append(f"{sp}\t({' '.join(str(x) for x in child)})")
            else:
                lines.append(dump_sexp(child, indent + 1))
        else:
            lines.append(f"{sp}\t{child}")
    lines.append(f"{sp})")
    return "\n".join(lines)


# ---------------- Load & Flatten KiCad 10 Symbols ----------------
_lib_cache = {}


def load_sym_lib(lib_name):
    if lib_name not in _lib_cache:
        p = os.path.join(KICAD_SYM_DIR, f"{lib_name}.kicad_sym")
        with open(p, "r", encoding="utf-8") as f:
            _lib_cache[lib_name] = parse_sexp(f.read())
    return _lib_cache[lib_name]


def copy_tree(node):
    return [copy_tree(x) for x in node] if isinstance(node, list) else node


def extract_flattened_symbol(src_lib, src_name, dst_lib, dst_name, default_fp="", fix_tps2116=False):
    tree = load_sym_lib(src_lib)
    node = next(
        copy_tree(it)
        for it in tree[1:]
        if isinstance(it, list) and it[0] == "symbol" and unq(it[1]) == src_name
    )

    ext_name = None
    for ch in node[2:]:
        if isinstance(ch, list) and ch[0] == "extends":
            ext_name = unq(ch[1])
            break

    if ext_name:
        parent = next(
            copy_tree(it)
            for it in tree[1:]
            if isinstance(it, list) and it[0] == "symbol" and unq(it[1]) == ext_name
        )
        child_props = {
            unq(ch[1]): ch
            for ch in node[2:]
            if isinstance(ch, list) and ch[0] == "property"
        }
        merged = ["symbol", q(dst_name)]
        seen_props = set()
        for pch in parent[2:]:
            if isinstance(pch, list) and pch[0] == "property":
                pname = unq(pch[1])
                seen_props.add(pname)
                merged.append(copy_tree(child_props.get(pname, pch)))
            elif isinstance(pch, list) and pch[0] == "symbol":
                sub = copy_tree(pch)
                old_sub = unq(sub[1])
                suffix = re.search(r"(_\d+_\d+)$", old_sub)
                sub[1] = q(dst_name + (suffix.group(1) if suffix else "_0_1"))
                merged.append(sub)
            else:
                merged.append(copy_tree(pch))
        for k, cprop in child_props.items():
            if k not in seen_props:
                merged.append(copy_tree(cprop))
        node = merged
    else:
        node[1] = q(dst_name)
        for ch in node[2:]:
            if isinstance(ch, list) and ch[0] == "symbol":
                old_sub = unq(ch[1])
                suffix = re.search(r"(_\d+_\d+)$", old_sub)
                ch[1] = q(dst_name + (suffix.group(1) if suffix else "_0_1"))

    for ch in node[2:]:
        if isinstance(ch, list) and ch[0] == "property" and unq(ch[1]) == "Footprint":
            ch[2] = q(default_fp)

    if fix_tps2116:
        for ch in node[2:]:
            if isinstance(ch, list) and ch[0] == "symbol":
                for el in ch[2:]:
                    if isinstance(el, list) and el[0] == "pin":
                        num = next((unq(x[1]) for x in el[3:] if isinstance(x, list) and x[0] == "number"), "")
                        if num == "7":
                            el[1] = "passive"

    pins = {}
    for ch in node[2:]:
        if isinstance(ch, list) and ch[0] == "symbol":
            for el in ch[2:]:
                if isinstance(el, list) and el[0] == "pin":
                    ptype = el[1]
                    at = next(x for x in el[3:] if isinstance(x, list) and x[0] == "at")
                    px, py = float(at[1]), float(at[2])
                    pang = float(at[3]) if len(at) > 3 else 0.0
                    pnum = next(unq(x[1]) for x in el[3:] if isinstance(x, list) and x[0] == "number")
                    pname = next(unq(x[1]) for x in el[3:] if isinstance(x, list) and x[0] == "name")
                    pins[pnum] = {"x": px, "y": py, "angle": pang, "name": pname, "type": ptype}

    standalone_node = copy_tree(node)
    lib_node = copy_tree(node)
    lib_node[1] = q(f"{dst_lib}:{dst_name}")
    return lib_node, standalone_node, pins


SYMBOL_DEFS_SPEC = [
    ("power", "+3V3", "YoloUNO", "+3V3", "", False),
    ("power", "+5V", "YoloUNO", "+5V", "", False),
    ("power", "GND", "YoloUNO", "GND", "", False),
    ("power", "VBUS", "YoloUNO", "VBUS", "", False),
    ("power", "PWR_FLAG", "YoloUNO", "PWR_FLAG", "", False),
    ("Connector", "Barrel_Jack_Switch", "YoloUNO", "PJ-002A_BarrelJack", "YoloUNO:BarrelJack_CUI_PJ-102AH_Horizontal", False),
    ("Device", "D_TVS", "YoloUNO", "SMBJ15CA", "YoloUNO:D_SMB", False),
    ("Transistor_FET", "AO3401A", "YoloUNO", "AO3407A", "YoloUNO:SOT-23-3", False),
    ("Device", "D_Zener", "YoloUNO", "BZT52C10", "YoloUNO:D_SOD-123", False),
    ("Device", "R", "YoloUNO", "R", "YoloUNO:R_0603_1608Metric", False),
    ("Device", "C", "YoloUNO", "C", "YoloUNO:C_0603_1608Metric", False),
    ("Device", "C_Polarized", "YoloUNO", "C_Polarized", "YoloUNO:CP_Elec_6.3x5.4", False),
    ("Device", "L", "YoloUNO", "L", "YoloUNO:L_Bourns_SRN6045TA", False),
    ("Device", "LED", "YoloUNO", "LED", "YoloUNO:LED_0603_1608Metric", False),
    ("Regulator_Switching", "TPS54202DDC", "YoloUNO", "TPS54202DDCR", "YoloUNO:SOT-23-6", False),
    ("Power_Management", "TPS2116DRL", "YoloUNO", "TPS2116DRLR", "YoloUNO:SOT-583-8", True),
    ("Regulator_Linear", "AMS1117-3.3", "YoloUNO", "AP2114H-3.3TRG1", "YoloUNO:SOT-223-3_TabPin2", False),
    ("RF_Module", "ESP32-S3-WROOM-1", "YoloUNO", "ESP32-S3-WROOM-1-N16R8", "YoloUNO:ESP32-S3-WROOM-1", False),
    ("Switch", "SW_Push", "YoloUNO", "TS-1187A", "YoloUNO:SW_Push_1P1T_XKB_TS-1187A", False),
    ("Connector", "USB_C_Receptacle_USB2.0_16P", "YoloUNO", "TYPE-C-31-M-12", "YoloUNO:USB_C_Receptacle_HRO_TYPE-C-31-M-12", False),
    ("Power_Protection", "USBLC6-2SC6", "YoloUNO", "USBLC6-2SC6", "YoloUNO:SOT-23-6", False),
    ("Logic_LevelTranslator", "SN74LV1T34DBV", "YoloUNO", "SN74LV1T34DBVR", "YoloUNO:SOT-23-5", False),
    ("LED", "WS2812B", "YoloUNO", "WS2812B-B", "YoloUNO:LED_WS2812B_PLCC4_5.0x5.0mm_P3.2mm", False),
    ("Jumper", "SolderJumper_3_Bridged12", "YoloUNO", "SolderJumper_3_Bridged12", "YoloUNO:SolderJumper-3_P1.3mm_Bridged12_Pad1.0x1.5mm", False),
    ("Connector_Generic", "Conn_01x03", "YoloUNO", "Servo_GVS_1x03", "YoloUNO:PinHeader_1x03_P2.54mm_Vertical", False),
    ("Connector_Generic", "Conn_01x04", "YoloUNO", "Grove_1x04", "YoloUNO:NS-Tech_Grove_1x04_P2mm_Vertical", False),
    ("Connector_Generic_MountingPin", "Conn_01x04_MountingPin", "YoloUNO", "QWIIC_JST_SH_1x04", "YoloUNO:JST_SH_SM04B-SRSS-TB_1x04-1MP_P1.00mm_Horizontal", False),
    ("Connector_Generic", "Conn_01x06", "YoloUNO", "UNO_Header_1x06", "YoloUNO:PinSocket_1x06_P2.54mm_Vertical", False),
    ("Connector_Generic", "Conn_01x08", "YoloUNO", "UNO_Header_1x08", "YoloUNO:PinSocket_1x08_P2.54mm_Vertical", False),
    ("Connector_Generic", "Conn_01x10", "YoloUNO", "UNO_Header_1x10", "YoloUNO:PinSocket_1x10_P2.54mm_Vertical", False),
    ("Mechanical", "MountingHole", "YoloUNO", "MountingHole_M3", "YoloUNO:MountingHole_3.2mm_M3", False),
    ("Mechanical", "Fiducial", "YoloUNO", "Fiducial_1mm", "YoloUNO:Fiducial_1mm_Mask2mm", False),
]

SYM_CATALOG = {}
YOLONO_STANDALONE_SYMS = []
for s_lib, s_name, d_lib, d_name, def_fp, fix_tps in SYMBOL_DEFS_SPEC:
    lnode, snode, pins = extract_flattened_symbol(s_lib, s_name, d_lib, d_name, def_fp, fix_tps)
    lid = f"{d_lib}:{d_name}"
    SYM_CATALOG[lid] = {"lib_node": lnode, "pins": pins}
    YOLONO_STANDALONE_SYMS.append(snode)

sym_lib_sexp = [
    "kicad_symbol_lib",
    ["version", "20241209"],
    ["generator", q("kicad_symbol_editor")],
    ["generator_version", q("10.0")],
] + YOLONO_STANDALONE_SYMS

with open(os.path.join(LIB_DIR, "YoloUNO.kicad_sym"), "w", encoding="utf-8") as f:
    f.write(dump_sexp(sym_lib_sexp) + "\n")

sym_lib_table_txt = """(sym_lib_table
  (version 7)
  (lib (name "YoloUNO")(type "KiCad")(uri "${KIPRJMOD}/libraries/YoloUNO.kicad_sym")(options "")(descr "Yolo UNO Project Self-Contained Symbol Library"))
)
"""
with open(os.path.join(HW_DIR, "sym-lib-table"), "w", encoding="utf-8") as f:
    f.write(sym_lib_table_txt)


# ---------------- Coordinate Math & Sheet Builder ----------------
GRID = 1.27


def transform_pin(sx, sy, rot_deg, px, py, pang):
    rad = math.radians(rot_deg)
    rx = px * math.cos(rad) - py * math.sin(rad)
    ry = px * math.sin(rad) + py * math.cos(rad)
    wx = round(sx + rx, 2)
    wy = round(sy - ry, 2)
    out_yup = (pang + 180.0 + rot_deg) % 360.0
    ux = round(math.cos(math.radians(out_yup)))
    uy_down = round(-math.sin(math.radians(out_yup)))
    return wx, wy, ux, uy_down


PROJECT_NAME = "YoloUNO"
ROOT_UUID = make_uuid("root-sheet")
PWR_Counter = 100
POWER_SYMBOL_NAMES = {"+3V3", "+5V", "GND", "VBUS", "PWR_FLAG"}


class PlacedSymbol:
    def __init__(self, sheet, lib_id, ref, value, footprint, sx, sy, rot=0, mpn="", lcsc="", datasheet="", in_bom=True, on_board=True, ref_offset=None, val_offset=None, text_justify="left"):
        self.sheet = sheet
        self.lib_id = lib_id
        self.ref = ref
        self.value = value
        self.footprint = footprint
        self.sx = round(sx, 2)
        self.sy = round(sy, 2)
        self.rot = rot
        self.mpn = mpn
        self.lcsc = lcsc
        self.datasheet = datasheet
        self.in_bom = in_bom
        self.on_board = on_board
        self.uuid = make_uuid(f"sym-{ref}-{sx}-{sy}")
        self.ref_offset = ref_offset
        self.val_offset = val_offset
        self.text_justify = text_justify

    def pin_xy(self, pnum):
        pinfo = SYM_CATALOG[self.lib_id]["pins"][str(pnum)]
        wx, wy, _, _ = transform_pin(self.sx, self.sy, self.rot, pinfo["x"], pinfo["y"], pinfo["angle"])
        return wx, wy

    def to_sexp(self):
        sym_short = self.lib_id.split(":", 1)[1]
        is_pwr = sym_short in POWER_SYMBOL_NAMES

        # Clean default offsets for vertical vs horizontal passives so text never touches symbol body
        if self.ref_offset is not None:
            rx, ry = self.sx + self.ref_offset[0], self.sy + self.ref_offset[1]
        else:
            rx, ry = (self.sx + 2.032, self.sy - 1.27) if self.rot == 0 else (self.sx - 2.54, self.sy - 4.445)

        if self.val_offset is not None:
            vx, vy = self.sx + self.val_offset[0], self.sy + self.val_offset[1]
        else:
            vx, vy = (self.sx + 2.032, self.sy + 1.524) if self.rot == 0 else (self.sx - 2.54, self.sy + 4.445)

        just_clause = [["justify", self.text_justify]] if self.text_justify in ("left", "right") else []

        if is_pwr:
            if self.rot == 0:
                vx, vy = self.sx, (self.sy + 3.81 if self.value == "GND" else self.sy - 3.81)
                just_clause = []
            elif self.rot in (90, 270):
                vx, vy = self.sx - 3.175, self.sy
                just_clause = [["justify", "right"]]

        props = [
            [
                "property", q("Reference"), q(self.ref),
                ["at", fmt_num(rx), fmt_num(ry), "0"],
                *( [["hide", "yes"]] if is_pwr else [] ),
                ["effects", ["font", ["size", "1.15", "1.15"]], *just_clause],
            ],
            [
                "property", q("Value"), q(self.value),
                ["at", fmt_num(vx), fmt_num(vy), "0"],
                *( [["hide", "yes"]] if self.ref.startswith("#FLG") else [] ),
                ["effects", ["font", ["size", "1.0", "1.0"] if is_pwr else ["size", "1.15", "1.15"]], *just_clause],
            ],
            [
                "property", q("Footprint"), q(self.footprint),
                ["at", fmt_num(self.sx), fmt_num(self.sy), "0"],
                ["hide", "yes"],
                ["effects", ["font", ["size", "1.27", "1.27"]]],
            ],
            [
                "property", q("Datasheet"), q(self.datasheet),
                ["at", fmt_num(self.sx), fmt_num(self.sy), "0"],
                ["hide", "yes"],
                ["effects", ["font", ["size", "1.27", "1.27"]]],
            ],
        ]
        if not is_pwr:
            props.append([
                "property", q("MPN"), q(self.mpn),
                ["at", fmt_num(self.sx), fmt_num(self.sy), "0"],
                ["hide", "yes"],
                ["effects", ["font", ["size", "1.27", "1.27"]]],
            ])
            props.append([
                "property", q("LCSC"), q(self.lcsc),
                ["at", fmt_num(self.sx), fmt_num(self.sy), "0"],
                ["hide", "yes"],
                ["effects", ["font", ["size", "1.27", "1.27"]]],
            ])

        pin_entries = [
            ["pin", q(pnum), ["uuid", q(make_uuid(f"pin-{self.uuid}-{pnum}"))]]
            for pnum in SYM_CATALOG[self.lib_id]["pins"].keys()
        ]

        inst_path = f"/{ROOT_UUID}" if self.sheet.is_root else f"/{ROOT_UUID}/{self.sheet.sheet_inst_uuid}"
        return [
            "symbol",
            ["lib_id", q(self.lib_id)],
            ["at", fmt_num(self.sx), fmt_num(self.sy), fmt_num(self.rot)],
            ["unit", "1"],
            ["exclude_from_sim", "no"],
            ["in_bom", "yes" if self.in_bom else "no"],
            ["on_board", "yes" if self.on_board else "no"],
            ["dnp", "no"],
            ["fields_autoplaced", "no"],
            ["uuid", q(self.uuid)],
            *props,
            *pin_entries,
            [
                "instances",
                [
                    "project", q(PROJECT_NAME),
                    [
                        "path", q(inst_path),
                        ["reference", q(self.ref)],
                        ["unit", "1"],
                    ],
                ],
            ],
        ]


class SheetBuilder:
    def __init__(self, filename, title, page_num, is_root=False, sheet_inst_uuid=None):
        self.filename = filename
        self.title = title
        self.page_num = str(page_num)
        self.is_root = is_root
        self.uuid = ROOT_UUID if is_root else make_uuid(f"file-{filename}")
        self.sheet_inst_uuid = sheet_inst_uuid
        self.used_lib_ids = []
        self.symbols = []
        self.wires = []
        self.junctions = []
        self.no_connects = []
        self.labels = []
        self.global_labels = []
        self.texts = []
        self.boxes = []
        self.subsheets = []

    def _use_lib(self, lib_id):
        if lib_id not in self.used_lib_ids:
            self.used_lib_ids.append(lib_id)

    def place(self, lib_id, ref, value, footprint, sx, sy, rot=0, mpn="", lcsc="", datasheet="", in_bom=True, on_board=True, ref_offset=None, val_offset=None, text_justify="left"):
        self._use_lib(lib_id)
        sym = PlacedSymbol(self, lib_id, ref, value, footprint, sx, sy, rot, mpn, lcsc, datasheet, in_bom, on_board, ref_offset, val_offset, text_justify)
        self.symbols.append(sym)
        return sym

    def add_pwr(self, net_name, x, y, rot=0):
        global PWR_Counter
        PWR_Counter += 1
        lib_id = f"YoloUNO:{net_name}"
        ref = f"#PWR{PWR_Counter:04d}"
        return self.place(lib_id, ref, net_name, "", x, y, rot=rot, in_bom=False, on_board=True)

    def add_pwr_flag(self, x, y, rot=0):
        global PWR_Counter
        PWR_Counter += 1
        ref = f"#FLG{PWR_Counter:04d}"
        return self.place("YoloUNO:PWR_FLAG", ref, "PWR_FLAG", "", x, y, rot=rot, in_bom=False, on_board=True)

    def tie_gnd(self, x, y, stub_dy=2.54):
        gy = round(y + stub_dy, 2)
        if abs(stub_dy) > 1e-4:
            self.add_wire(x, y, x, gy)
        self.add_pwr("GND", x, gy, rot=0)

    def tie_rail(self, rail, x, y, stub_dy=-2.54):
        ry = round(y + stub_dy, 2)
        if abs(stub_dy) > 1e-4:
            self.add_wire(x, y, x, ry)
        self.add_pwr(rail, x, ry, rot=0)

    def tie_horiz_pwr(self, net_name, px, py, stub_dx=-6.35):
        ex = round(px + stub_dx, 2)
        self.add_wire(ex, py, px, py)
        rot = 270 if net_name == "GND" else 90
        self.add_pwr(net_name, ex, py, rot=rot)

    def add_wire(self, x1, y1, x2, y2):
        x1, y1, x2, y2 = round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)
        if abs(x1 - x2) < 1e-4 and abs(y1 - y2) < 1e-4:
            return
        self.wires.append((x1, y1, x2, y2))

    def add_junction(self, x, y):
        self.junctions.append((round(x, 2), round(y, 2)))

    def add_nc(self, x, y):
        self.no_connects.append((round(x, 2), round(y, 2)))

    def add_label(self, name, x, y, rot=0):
        just = "left bottom" if rot in (0, 90) else "right bottom"
        self.labels.append((name, round(x, 2), round(y, 2), rot, just))

    def add_glabel(self, name, x, y, rot=0, shape="bidirectional"):
        just = "left" if rot == 0 else "right"
        self.global_labels.append((name, shape, round(x, 2), round(y, 2), rot, just))

    def add_box(self, title, x1, y1, x2, y2):
        self.boxes.append((x1, y1, x2, y2))
        self.texts.append((title, x1 + 2.54, y1 + 4.2, 1.9, True))

    def add_note(self, text, x, y, size=1.4, bold=False):
        self.texts.append((text, x, y, size, bold))

    def save(self):
        lib_syms = ["lib_symbols"] + [SYM_CATALOG[lid]["lib_node"] for lid in self.used_lib_ids]

        rect_nodes = [
            [
                "rectangle",
                ["start", fmt_num(x1), fmt_num(y1)],
                ["end", fmt_num(x2), fmt_num(y2)],
                ["stroke", ["width", "0.2"], ["type", "dash"], ["color", "0", "90", "160", "1"]],
                ["fill", ["type", "none"]],
                ["uuid", q(make_uuid("box"))],
            ]
            for (x1, y1, x2, y2) in self.boxes
        ]

        text_nodes = [
            [
                "text", q(txt),
                ["exclude_from_sim", "no"],
                ["at", fmt_num(x), fmt_num(y), "0"],
                [
                    "effects",
                    ["font", ["size", fmt_num(sz), fmt_num(sz)], *([["bold", "yes"]] if bld else [])],
                    ["justify", "left", "bottom"],
                ],
                ["uuid", q(make_uuid("txt"))],
            ]
            for (txt, x, y, sz, bld) in self.texts
        ]

        wire_nodes = [
            [
                "wire",
                ["pts", ["xy", fmt_num(x1), fmt_num(y1)], ["xy", fmt_num(x2), fmt_num(y2)]],
                ["stroke", ["width", "0"], ["type", "default"]],
                ["uuid", q(make_uuid("wire"))],
            ]
            for (x1, y1, x2, y2) in self.wires
        ]

        junc_nodes = [
            [
                "junction",
                ["at", fmt_num(x), fmt_num(y)],
                ["diameter", "1.016"],
                ["color", "0", "0", "0", "0"],
                ["uuid", q(make_uuid("junc"))],
            ]
            for (x, y) in self.junctions
        ]

        nc_nodes = [
            ["no_connect", ["at", fmt_num(x), fmt_num(y)], ["uuid", q(make_uuid("nc"))]]
            for (x, y) in self.no_connects
        ]

        lbl_nodes = [
            [
                "label", q(name),
                ["at", fmt_num(x), fmt_num(y), fmt_num(rot)],
                ["effects", ["font", ["size", "1.2", "1.2"]], ["justify", *just.split()]],
                ["uuid", q(make_uuid(f"lbl-{name}"))],
            ]
            for (name, x, y, rot, just) in self.labels
        ]

        glbl_nodes = [
            [
                "global_label", q(name),
                ["shape", shape],
                ["at", fmt_num(x), fmt_num(y), fmt_num(rot)],
                ["fields_autoplaced", "yes"],
                ["effects", ["font", ["size", "1.2", "1.2"]], ["justify", just]],
                ["uuid", q(make_uuid(f"glbl-{name}"))],
                [
                    "property", q("Intersheetrefs"), q("${INTERSHEET_REFS}"),
                    ["at", fmt_num(x + 5.08), fmt_num(y), "0"],
                    ["hide", "yes"],
                    ["effects", ["font", ["size", "1.27", "1.27"]], ["justify", "left"]],
                ],
            ]
            for (name, shape, x, y, rot, just) in self.global_labels
        ]

        sym_nodes = [s.to_sexp() for s in self.symbols]

        root_sexp = [
            "kicad_sch",
            ["version", "20250610"],
            ["generator", q("eeschema")],
            ["generator_version", q("10.0")],
            ["uuid", q(self.uuid)],
            ["paper", q("A3")],
            [
                "title_block",
                ["title", q(self.title)],
                ["date", q("2026-11-25")],
                ["rev", q("1.0")],
                ["company", q("HCMUT - CO2037 Electronic Devices & Circuits")],
                ["comment", "1", q("Board: Yolo UNO Redesign (ESP32-S3-WROOM-1-N16R8, 4-Layer IPC-2221)")],
                ["comment", "2", q("12x Grove (3.3V) | QWIIC | 4x Servo GVS | USB-C + 6-12V DC Power-Mux")],
            ],
            lib_syms,
            *rect_nodes,
            *text_nodes,
            *wire_nodes,
            *junc_nodes,
            *nc_nodes,
            *lbl_nodes,
            *glbl_nodes,
            *sym_nodes,
            *self.subsheets,
        ]
        if self.is_root:
            root_sexp.append(["sheet_instances", ["path", q("/"), ["page", q("1")]]])
        root_sexp.append(["embedded_fonts", "no"])

        out_path = os.path.join(HW_DIR, self.filename)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(dump_sexp(root_sexp) + "\n")
        return out_path


# ==============================================================================
# SHEET 1: ROOT HIERARCHY & MECHANICAL / DFM FIDUCIALS
# ==============================================================================
sh_pwr_uuid = make_uuid("inst-pwr")
sh_mcu_uuid = make_uuid("inst-mcu")
sh_usb_uuid = make_uuid("inst-usb")
sh_per_uuid = make_uuid("inst-per")

root = SheetBuilder("YoloUNO.kicad_sch", "Yolo UNO Redesign - System Architecture Overview", 1, is_root=True)
root.add_box("SYSTEM HIERARCHY OVERVIEW (CO2037 PROJECT 1 - YOLO UNO REDESIGN)", 25.4, 25.4, 393.7, 185.42)
root.add_note(
    "Architecture Summary:\n"
    "- Sheet 2 (01_Power_Supply): 6-12V DC Reverse-Polarity MOSFET (AO3407A) + SMBJ15CA -> 5.05V/2A Sync Buck (TPS54202) + TPS2116 Power-Mux -> +5V & AP2114H-3.3 (1A) -> +3V3\n"
    "- Sheet 3 (02_MCU_ESP32S3): ESP32-S3-WROOM-1-N16R8 (16MB Flash, 8MB Octal PSRAM, 3.3V VDD_SPI), Decoupling (22uF+100nF), EN RC Delay (10k/1uF) & BOOT (GPIO0)\n"
    "- Sheet 4 (03_USB_and_LEDs): USB Type-C 16P (5.1k Rd x2) + USBLC6-2SC6 ESD, User LED D13 (GPIO48, 270 Ohm), WS2812B NeoPixel + SN74LV1T34 Level Shifter (GPIO45 + 10k PD)\n"
    "- Sheet 5 (04_Peripherals_and_Headers): Arduino UNO R3 Headers, 12x Grove (4 Analog, 4 Digital, 4 I2C), QWIIC, 1.5k I2C Pull-Ups, A0 0-5V Divider (JP1), 4x Servo GVS + 470uF",
    33.02, 63.5, size=1.5
)

subsheet_specs = [
    ("01_Power_Supply", "01_Power_Supply.kicad_sch", sh_pwr_uuid, "2", 38.1, 96.52, 76.2, 40.64),
    ("02_MCU_ESP32S3", "02_MCU_ESP32S3.kicad_sch", sh_mcu_uuid, "3", 127.0, 96.52, 76.2, 40.64),
    ("03_USB_and_LEDs", "03_USB_and_LEDs.kicad_sch", sh_usb_uuid, "4", 215.9, 96.52, 76.2, 40.64),
    ("04_Peripherals_and_Headers", "04_Peripherals_and_Headers.kicad_sch", sh_per_uuid, "5", 304.8, 96.52, 76.2, 40.64),
]
for sname, sfile, suuid, spage, sx, sy, sw, sh in subsheet_specs:
    root.subsheets.append([
        "sheet",
        ["at", fmt_num(sx), fmt_num(sy)],
        ["size", fmt_num(sw), fmt_num(sh)],
        ["exclude_from_sim", "no"],
        ["in_bom", "yes"],
        ["on_board", "yes"],
        ["dnp", "no"],
        ["fields_autoplaced", "yes"],
        ["stroke", ["width", "0.254"], ["type", "solid"]],
        ["fill", ["color", "240", "248", "255", "1.0"]],
        ["uuid", q(suuid)],
        [
            "property", q("Sheetname"), q(sname),
            ["at", fmt_num(sx), fmt_num(sy - 1.27), "0"],
            ["effects", ["font", ["size", "1.8", "1.8"], ["bold", "yes"]], ["justify", "left", "bottom"]],
        ],
        [
            "property", q("Sheetfile"), q(sfile),
            ["at", fmt_num(sx), fmt_num(sy + sh + 2.54), "0"],
            ["effects", ["font", ["size", "1.3", "1.3"]], ["justify", "left", "top"]],
        ],
        [
            "instances",
            ["project", q(PROJECT_NAME), ["path", q(f"/{ROOT_UUID}"), ["page", q(spage)]]],
        ],
    ])

root.add_box("MECHANICAL MOUNTING HOLES (UNO R3 M3 x4) & OPTICAL DFM FIDUCIALS (x3)", 25.4, 198.12, 284.48, 254.0)
for idx in range(1, 5):
    root.place(
        "YoloUNO:MountingHole_M3", f"H{idx}", "M3_Hole",
        "YoloUNO:MountingHole_3.2mm_M3", 45.72 + (idx - 1) * 35.56, 228.6,
        mpn="M3_NPTH_UNO_R3", lcsc="N/A", in_bom=False, on_board=True,
        ref_offset=(2.54, -1.27), val_offset=(2.54, 1.524)
    )
for idx in range(1, 4):
    root.place(
        "YoloUNO:Fiducial_1mm", f"FID{idx}", "Fiducial",
        "YoloUNO:Fiducial_1mm_Mask2mm", 195.58 + (idx - 1) * 30.48, 228.6,
        mpn="FIDUCIAL_1MM", lcsc="N/A", in_bom=False, on_board=True,
        ref_offset=(2.54, -1.27), val_offset=(2.54, 1.524)
    )


# ==============================================================================
# SHEET 2: 01_Power_Supply.kicad_sch (Blocks 4.1, 4.2, 4.3, 4.4)
# ==============================================================================
s_pwr = SheetBuilder("01_Power_Supply.kicad_sch", "Power Supply: Protection, 5V Buck, Power-Mux & 3.3V LDO", 2, sheet_inst_uuid=sh_pwr_uuid)

# --- Block 4.1: Input Power & Protection (6-12V DC) ---
s_pwr.add_box("4.1 INPUT POWER (DC JACK 6-12V), TVS & P-MOSFET REVERSE-POLARITY PROTECTION", 20.32, 20.32, 203.2, 139.7)

j1 = s_pwr.place("YoloUNO:PJ-002A_BarrelJack", "J1", "PJ-002A (6-12V)", "YoloUNO:BarrelJack_CUI_PJ-102AH_Horizontal",
                 38.1, 58.42, rot=0, mpn="PJ-002A", lcsc="C720477",
                 ref_offset=(-7.62, -6.35), val_offset=(-7.62, 6.35))
j1_p1 = j1.pin_xy("1")
j1_p3 = j1.pin_xy("3")
j1_p2 = j1.pin_xy("2")

s_pwr.add_wire(j1_p3[0], j1_p3[1], 50.8, j1_p3[1])
s_pwr.add_wire(j1_p2[0], j1_p2[1], 50.8, j1_p2[1])
s_pwr.add_wire(50.8, j1_p3[1], 50.8, 66.04)
s_pwr.add_junction(50.8, j1_p2[1])
s_pwr.add_pwr("GND", 50.8, 66.04)

d1 = s_pwr.place("YoloUNO:SMBJ15CA", "D1", "SMBJ15CA", "YoloUNO:D_SMB",
                 68.58, 68.58, rot=90, mpn="SMBJ15CA", lcsc="C123785",
                 ref_offset=(2.54, -1.27), val_offset=(2.54, 1.524))
s_pwr.add_wire(j1_p1[0], j1_p1[1], 68.58, j1_p1[1])
s_pwr.add_label("VIN_RAW", 53.34, j1_p1[1])
s_pwr.add_wire(68.58, j1_p1[1], *d1.pin_xy("2"))
s_pwr.add_junction(68.58, j1_p1[1])
s_pwr.tie_gnd(*d1.pin_xy("1"), 3.81)

q1 = s_pwr.place("YoloUNO:AO3407A", "Q1", "AO3407A", "YoloUNO:SOT-23-3",
                 96.52, 58.42, rot=90, mpn="AO3407A", lcsc="C347475",
                 ref_offset=(-5.08, -9.525), val_offset=(-5.08, -6.985))
q1_d = q1.pin_xy("3")
q1_s = q1.pin_xy("2")
q1_g = q1.pin_xy("1")
s_pwr.add_wire(68.58, j1_p1[1], q1_d[0], q1_d[1])

d2 = s_pwr.place("YoloUNO:BZT52C10", "D2", "BZT52C10 (10V)", "YoloUNO:D_SOD-123",
                 111.76, 68.58, rot=270, mpn="BZT52C10-7-F", lcsc="C81598",
                 ref_offset=(2.54, -1.27), val_offset=(2.54, 1.524))
r1 = s_pwr.place("YoloUNO:R", "R1", "47k", "YoloUNO:R_0603_1608Metric",
                 96.52, 85.09, rot=0, mpn="RC0603FR-0747KL", lcsc="C25819")
s_pwr.add_wire(q1_g[0], q1_g[1], *r1.pin_xy("1"))
s_pwr.add_wire(*d2.pin_xy("2"), 111.76, 76.2)
s_pwr.add_wire(111.76, 76.2, 96.52, 76.2)
s_pwr.add_junction(96.52, 76.2)
s_pwr.tie_gnd(*r1.pin_xy("2"), 3.81)

s_pwr.add_wire(q1_s[0], q1_s[1], 187.96, 55.88)
s_pwr.add_wire(111.76, 55.88, *d2.pin_xy("1"))
s_pwr.add_junction(111.76, 55.88)

s_pwr.add_wire(132.08, 55.88, 132.08, 48.26)
s_pwr.add_junction(132.08, 55.88)
s_pwr.add_pwr_flag(132.08, 48.26, rot=0)

c1 = s_pwr.place("YoloUNO:C_Polarized", "C1", "47uF/25V", "YoloUNO:CP_Elec_6.3x5.4",
                 147.32, 68.58, rot=0, mpn="EEE-FK1E470P", lcsc="C72485")
s_pwr.add_wire(147.32, 55.88, *c1.pin_xy("1"))
s_pwr.add_junction(147.32, 55.88)
s_pwr.tie_gnd(*c1.pin_xy("2"), 3.81)

c2 = s_pwr.place("YoloUNO:C", "C2", "100nF", "YoloUNO:C_0603_1608Metric",
                 170.18, 68.58, rot=0, mpn="CL10B104KB8NNNC", lcsc="C1591")
s_pwr.add_wire(170.18, 55.88, *c2.pin_xy("1"))
s_pwr.add_junction(170.18, 55.88)
s_pwr.tie_gnd(*c2.pin_xy("2"), 3.81)

s_pwr.add_glabel("VIN_PROT", 187.96, 55.88, rot=0, shape="output")

s_pwr.add_pwr("GND", 40.64, 119.38, rot=0)
s_pwr.add_wire(40.64, 119.38, 40.64, 114.3)
s_pwr.add_pwr_flag(40.64, 114.3, rot=0)


# --- Block 4.2: 5V Synchronous Buck Converter (TPS54202DDCR) ---
s_pwr.add_box("4.2 5V SYNCHRONOUS BUCK CONVERTER (TPS54202DDCR, 500kHz, VOUT=5.05V @ 2A)", 213.36, 20.32, 403.86, 139.7)

u1 = s_pwr.place("YoloUNO:TPS54202DDCR", "U1", "TPS54202DDCR", "YoloUNO:SOT-23-6",
                 279.4, 68.58, rot=0, mpn="TPS54202DDCR", lcsc="C128249",
                 ref_offset=(-8.89, -11.43), val_offset=(-8.89, -8.89))
u1_vin = u1.pin_xy("3")
u1_en = u1.pin_xy("5")
u1_gnd = u1.pin_xy("1")
u1_boot = u1.pin_xy("6")
u1_sw = u1.pin_xy("2")
u1_fb = u1.pin_xy("4")

s_pwr.add_glabel("VIN_PROT", 226.06, 53.34, rot=180, shape="input")
s_pwr.add_wire(226.06, 53.34, 261.62, 53.34)
s_pwr.add_wire(261.62, 53.34, 261.62, u1_vin[1])
s_pwr.add_wire(261.62, u1_vin[1], u1_vin[0], u1_vin[1])

c3 = s_pwr.place("YoloUNO:C", "C3", "10uF/25V", "YoloUNO:C_0805_2012Metric",
                 231.14, 68.58, rot=0, mpn="GRM21BR61E106KA73L", lcsc="C15850")
s_pwr.add_wire(231.14, 53.34, *c3.pin_xy("1"))
s_pwr.add_junction(231.14, 53.34)
s_pwr.tie_gnd(*c3.pin_xy("2"), 3.81)

r2 = s_pwr.place("YoloUNO:R", "R2", "100k", "YoloUNO:R_0603_1608Metric",
                 248.92, 62.23, rot=0, mpn="RC0603FR-07100KL", lcsc="C25803")
s_pwr.add_wire(248.92, 53.34, *r2.pin_xy("1"))
s_pwr.add_junction(248.92, 53.34)
s_pwr.add_wire(*r2.pin_xy("2"), 248.92, u1_en[1])
s_pwr.add_wire(248.92, u1_en[1], u1_en[0], u1_en[1])

s_pwr.tie_gnd(u1_gnd[0], u1_gnd[1], 5.08)

c4 = s_pwr.place("YoloUNO:C", "C4", "100nF", "YoloUNO:C_0603_1608Metric",
                 300.99, 55.88, rot=90, mpn="CL10B104KB8NNNC", lcsc="C1591",
                 ref_offset=(-2.54, -6.35), val_offset=(-2.54, -3.81))
s_pwr.add_wire(u1_boot[0], u1_boot[1], 293.37, u1_boot[1])
s_pwr.add_wire(293.37, u1_boot[1], 293.37, 55.88)
s_pwr.add_wire(293.37, 55.88, *c4.pin_xy("1"))

l1 = s_pwr.place("YoloUNO:L", "L1", "15uH (SRN6045)", "YoloUNO:L_Bourns_SRN6045TA",
                 316.23, 68.58, rot=90, mpn="SRN6045TA-150M", lcsc="C169400",
                 ref_offset=(-5.08, -6.35), val_offset=(-5.08, -3.81))
s_pwr.add_wire(u1_sw[0], u1_sw[1], *l1.pin_xy("1"))
s_pwr.add_wire(*c4.pin_xy("2"), 308.61, 55.88)
s_pwr.add_wire(308.61, 55.88, 308.61, 68.58)
s_pwr.add_junction(308.61, 68.58)

s_pwr.add_wire(*l1.pin_xy("2"), 396.24, 68.58)
s_pwr.add_label("5V_BUCK", 396.24, 68.58, rot=180)

s_pwr.add_wire(327.66, 68.58, 327.66, 58.42)
s_pwr.add_junction(327.66, 68.58)
s_pwr.add_pwr_flag(327.66, 58.42, rot=0)

r3 = s_pwr.place("YoloUNO:R", "R3", "68.0k 1%", "YoloUNO:R_0603_1608Metric",
                 335.28, 82.55, rot=0, mpn="RC0603FR-0768KL", lcsc="C23231")
r4 = s_pwr.place("YoloUNO:R", "R4", "9.10k 1%", "YoloUNO:R_0603_1608Metric",
                 335.28, 100.33, rot=0, mpn="RC0603FR-079K1L", lcsc="C23268")
s_pwr.add_wire(335.28, 68.58, *r3.pin_xy("1"))
s_pwr.add_junction(335.28, 68.58)
s_pwr.add_wire(*r3.pin_xy("2"), *r4.pin_xy("1"))
fb_mid_y = round((r3.pin_xy("2")[1] + r4.pin_xy("1")[1]) / 2 / GRID) * GRID
s_pwr.add_wire(u1_fb[0], u1_fb[1], 297.18, u1_fb[1])
s_pwr.add_wire(297.18, u1_fb[1], 297.18, fb_mid_y)
s_pwr.add_wire(297.18, fb_mid_y, 335.28, fb_mid_y)
s_pwr.add_junction(335.28, fb_mid_y)
s_pwr.tie_gnd(*r4.pin_xy("2"), 3.81)

c5 = s_pwr.place("YoloUNO:C", "C5", "22uF/16V", "YoloUNO:C_0805_2012Metric",
                 358.14, 86.36, rot=0, mpn="GRM21BR61C226ME44L", lcsc="C45783")
c6 = s_pwr.place("YoloUNO:C", "C6", "22uF/16V", "YoloUNO:C_0805_2012Metric",
                 381.0, 86.36, rot=0, mpn="GRM21BR61C226ME44L", lcsc="C45783")
for cx, cap in [(358.14, c5), (381.0, c6)]:
    s_pwr.add_wire(cx, 68.58, *cap.pin_xy("1"))
    s_pwr.add_junction(cx, 68.58)
    s_pwr.tie_gnd(*cap.pin_xy("2"), 3.81)


# --- Block 4.3: USB / DC Auto Power-Path Mux (TPS2116DRLR) ---
s_pwr.add_box("4.3 USB / DC AUTO POWER-PATH MUX (TPS2116DRLR, VSW=4.60V, ZERO BACKFEED)", 20.32, 149.86, 203.2, 266.7)

u2 = s_pwr.place("YoloUNO:TPS2116DRLR", "U2", "TPS2116DRLR", "YoloUNO:SOT-583-8",
                 124.46, 203.2, rot=0, mpn="TPS2116DRLR", lcsc="C2875184",
                 ref_offset=(-8.89, -13.97), val_offset=(-8.89, -11.43))
u2_vin1 = u2.pin_xy("3")
u2_pr1 = u2.pin_xy("4")
u2_mode = u2.pin_xy("5")
u2_vin2 = u2.pin_xy("6")
u2_gnd = u2.pin_xy("1")
u2_vout = u2.pin_xy("2")
u2_st = u2.pin_xy("8")

s_pwr.add_wire(38.1, 180.34, 101.6, 180.34)
s_pwr.add_label("5V_BUCK", 38.1, 180.34, rot=0)
s_pwr.add_wire(101.6, 180.34, 101.6, u2_mode[1])
s_pwr.add_wire(101.6, u2_vin1[1], u2_vin1[0], u2_vin1[1])
s_pwr.add_junction(101.6, u2_vin1[1])
s_pwr.add_wire(101.6, u2_mode[1], u2_mode[0], u2_mode[1])

r5 = s_pwr.place("YoloUNO:R", "R5", "36.0k 1%", "YoloUNO:R_0603_1608Metric",
                 63.5, 191.77, rot=0, mpn="RC0603FR-0736KL", lcsc="C23146")
r6 = s_pwr.place("YoloUNO:R", "R6", "10.0k 1%", "YoloUNO:R_0603_1608Metric",
                 63.5, 209.55, rot=0, mpn="RC0603FR-0710KL", lcsc="C25804")
s_pwr.add_wire(63.5, 180.34, *r5.pin_xy("1"))
s_pwr.add_junction(63.5, 180.34)
s_pwr.add_wire(*r5.pin_xy("2"), *r6.pin_xy("1"))
s_pwr.add_wire(63.5, u2_pr1[1], u2_pr1[0], u2_pr1[1])
s_pwr.add_junction(63.5, u2_pr1[1])
s_pwr.tie_gnd(*r6.pin_xy("2"), 3.81)

# VBUS tied horizontally LEFT from VIN2 (y=208.28) so it stays completely below PR1/MODE wires!
s_pwr.tie_horiz_pwr("VBUS", u2_vin2[0], u2_vin2[1], -17.78)

s_pwr.tie_gnd(u2_gnd[0], u2_gnd[1], 5.08)
s_pwr.add_nc(u2_st[0], u2_st[1])

s_pwr.add_wire(u2_vout[0], u2_vout[1], 182.88, u2_vout[1])
s_pwr.tie_rail("+5V", 182.88, u2_vout[1], -5.08)
c7 = s_pwr.place("YoloUNO:C", "C7", "10uF/16V", "YoloUNO:C_0805_2012Metric",
                 160.02, 210.82, rot=0, mpn="CL21A106KOQNNNE", lcsc="C17024")
s_pwr.add_wire(160.02, u2_vout[1], *c7.pin_xy("1"))
s_pwr.add_junction(160.02, u2_vout[1])
s_pwr.tie_gnd(*c7.pin_xy("2"), 3.81)


# --- Block 4.4: 3.3V LDO Regulator (AP2114H-3.3TRG1) & Power Indicator LED ---
s_pwr.add_box("4.4 3.3V LDO REGULATOR (AP2114H-3.3TRG1, 1.0A) & POWER LED INDICATOR", 213.36, 149.86, 403.86, 266.7)

u3 = s_pwr.place("YoloUNO:AP2114H-3.3TRG1", "U3", "AP2114H-3.3TRG1", "YoloUNO:SOT-223-3_TabPin2",
                 289.56, 198.12, rot=0, mpn="AP2114H-3.3TRG1", lcsc="C151275",
                 ref_offset=(-7.62, -10.16), val_offset=(-7.62, -7.62))
u3_vi = u3.pin_xy("3")
u3_gnd = u3.pin_xy("1")
u3_vo = u3.pin_xy("2")

s_pwr.add_wire(236.22, u3_vi[1], u3_vi[0], u3_vi[1])
s_pwr.tie_rail("+5V", 236.22, u3_vi[1], -5.08)
c8 = s_pwr.place("YoloUNO:C", "C8", "10uF/16V", "YoloUNO:C_0805_2012Metric",
                 254.0, 210.82, rot=0, mpn="CL21A106KOQNNNE", lcsc="C17024")
s_pwr.add_wire(254.0, u3_vi[1], *c8.pin_xy("1"))
s_pwr.add_junction(254.0, u3_vi[1])
s_pwr.tie_gnd(*c8.pin_xy("2"), 3.81)

s_pwr.tie_gnd(u3_gnd[0], u3_gnd[1], 5.08)

s_pwr.add_wire(u3_vo[0], u3_vo[1], 378.46, u3_vo[1])
s_pwr.tie_rail("+3V3", 358.14, u3_vo[1], -5.08)
s_pwr.add_junction(358.14, u3_vo[1])

c9 = s_pwr.place("YoloUNO:C", "C9", "22uF/16V", "YoloUNO:C_0805_2012Metric",
                 314.96, 210.82, rot=0, mpn="GRM21BR61C226ME44L", lcsc="C45783")
c10 = s_pwr.place("YoloUNO:C", "C10", "100nF", "YoloUNO:C_0603_1608Metric",
                  337.82, 210.82, rot=0, mpn="CL10B104KB8NNNC", lcsc="C1591")
for cx, cap in [(314.96, c9), (337.82, c10)]:
    s_pwr.add_wire(cx, u3_vo[1], *cap.pin_xy("1"))
    s_pwr.add_junction(cx, u3_vo[1])
    s_pwr.tie_gnd(*cap.pin_xy("2"), 3.81)

r11 = s_pwr.place("YoloUNO:R", "R11", "470R", "YoloUNO:R_0603_1608Metric",
                  378.46, 209.55, rot=0, mpn="RC0603FR-07470RL", lcsc="C23179")
d3 = s_pwr.place("YoloUNO:LED", "D3", "PWR_GREEN", "YoloUNO:LED_0603_1608Metric",
                 378.46, 226.06, rot=90, mpn="19-217/GHC-YR1S2/3T", lcsc="C72043",
                 ref_offset=(3.175, -1.27), val_offset=(3.175, 1.524))
s_pwr.add_wire(378.46, u3_vo[1], *r11.pin_xy("1"))
s_pwr.add_wire(*r11.pin_xy("2"), *d3.pin_xy("2"))
s_pwr.tie_gnd(*d3.pin_xy("1"), 3.81)


# ==============================================================================
# SHEET 3: 02_MCU_ESP32S3.kicad_sch (Block 4.5)
# ==============================================================================
s_mcu = SheetBuilder("02_MCU_ESP32S3.kicad_sch", "MCU Core: ESP32-S3-WROOM-1, Decoupling & Reset/Boot", 3, sheet_inst_uuid=sh_mcu_uuid)
s_mcu.add_box("4.5 ESP32-S3-WROOM-1-N16R8 CORE, DECOUPLING, RESET (EN) & BOOT (GPIO0)", 20.32, 20.32, 403.86, 266.7)

u4 = s_mcu.place("YoloUNO:ESP32-S3-WROOM-1-N16R8", "U4", "ESP32-S3-WROOM-1-N16R8", "YoloUNO:ESP32-S3-WROOM-1",
                 236.22, 139.7, rot=0, mpn="ESP32-S3-WROOM-1-N16R8", lcsc="C2913202",
                 ref_offset=(6.35, -31.75), val_offset=(6.35, -29.21))

s_mcu.tie_rail("+3V3", *u4.pin_xy("2"), -6.35)
s_mcu.tie_gnd(*u4.pin_xy("1"), 6.35)

left_glabels = {
    "3": ("MCU_EN", "input"),
    "27": ("BOOT_IO0", "bidirectional"),
    "39": ("A0_ADC", "input"),
    "38": ("A1", "bidirectional"),
    "15": ("A2", "bidirectional"),
    "4": ("A3", "bidirectional"),
    "5": ("D2", "bidirectional"),
    "6": ("D3", "bidirectional"),
    "7": ("D4", "bidirectional"),
    "12": ("D5", "bidirectional"),
    "17": ("D6", "bidirectional"),
    "18": ("D7", "bidirectional"),
    "19": ("I2C_SDA", "bidirectional"),
    "20": ("I2C_SCL", "bidirectional"),
    "22": ("A6", "bidirectional"),
}
for pnum, (lname, shape) in left_glabels.items():
    px, py = u4.pin_xy(pnum)
    ex = px - 10.16
    s_mcu.add_wire(ex, py, px, py)
    if lname == "BOOT_IO0":
        s_mcu.add_label(lname, ex, py, rot=0)
    else:
        s_mcu.add_glabel(lname, ex, py, rot=180, shape=shape)

for pnum in ["21", "8", "9"]:
    s_mcu.add_nc(*u4.pin_xy(pnum))

right_glabels = {
    "37": ("D1_TX", "output"),
    "36": ("D0_RX", "input"),
    "10": ("D8", "bidirectional"),
    "11": ("D9", "bidirectional"),
    "13": ("USB_DN", "bidirectional"),
    "14": ("USB_DP", "bidirectional"),
    "23": ("D10", "bidirectional"),
    "31": ("D11", "bidirectional"),
    "26": ("NEO_GPIO45", "output"),
    "24": ("D12", "bidirectional"),
    "25": ("D13", "bidirectional"),
}
for pnum, (lname, shape) in right_glabels.items():
    px, py = u4.pin_xy(pnum)
    ex = px + 10.16
    s_mcu.add_wire(px, py, ex, py)
    s_mcu.add_glabel(lname, ex, py, rot=0, shape=shape)

for pnum in ["28", "29", "30", "32", "33", "34", "35", "16"]:
    s_mcu.add_nc(*u4.pin_xy(pnum))

s_mcu.add_note("Note: IO35, IO36, IO37 internally reserved by 8MB Octal PSRAM (N16R8) - MUST remain NC!", 266.7, 138.43, size=1.3, bold=True)

# MCU Decoupling
s_mcu.add_box("MCU 3.3V DECOUPLING", 33.02, 43.18, 127.0, 106.68)
s_mcu.add_wire(55.88, 60.96, 96.52, 60.96)
s_mcu.tie_rail("+3V3", 55.88, 60.96, -5.08)
c11 = s_mcu.place("YoloUNO:C", "C11", "22uF/16V", "YoloUNO:C_0805_2012Metric",
                  71.12, 73.66, rot=0, mpn="GRM21BR61C226ME44L", lcsc="C45783")
c12 = s_mcu.place("YoloUNO:C", "C12", "100nF", "YoloUNO:C_0603_1608Metric",
                  96.52, 73.66, rot=0, mpn="CL10B104KB8NNNC", lcsc="C1591")
for cx, cap in [(71.12, c11), (96.52, c12)]:
    s_mcu.add_wire(cx, 60.96, *cap.pin_xy("1"))
    if cx == 71.12:
        s_mcu.add_junction(cx, 60.96)
    s_mcu.tie_gnd(*cap.pin_xy("2"), 3.81)

# Reset (EN)
s_mcu.add_box("RESET CIRCUIT (EN RC DELAY tau=10ms)", 33.02, 114.3, 147.32, 185.42)
r7 = s_mcu.place("YoloUNO:R", "R7", "10.0k", "YoloUNO:R_0603_1608Metric",
                 58.42, 138.43, rot=0, mpn="RC0603FR-0710KL", lcsc="C25804")
s_mcu.tie_rail("+3V3", *r7.pin_xy("1"), -3.81)
en_y = 149.86
s_mcu.add_wire(*r7.pin_xy("2"), 58.42, en_y)
s_mcu.add_wire(58.42, en_y, 121.92, en_y)
s_mcu.add_glabel("MCU_EN", 121.92, en_y, rot=0, shape="output")

c13 = s_mcu.place("YoloUNO:C", "C13", "1uF/16V", "YoloUNO:C_0603_1608Metric",
                  58.42, 162.56, rot=0, mpn="CL10B105KO8NNNC", lcsc="C15849")
s_mcu.add_wire(58.42, en_y, *c13.pin_xy("1"))
s_mcu.add_junction(58.42, en_y)
s_mcu.tie_gnd(*c13.pin_xy("2"), 3.81)

sw1 = s_mcu.place("YoloUNO:TS-1187A", "SW1", "RESET", "YoloUNO:SW_Push_1P1T_XKB_TS-1187A",
                  93.98, 162.56, rot=90, mpn="TS-1187A-B-A-B", lcsc="C318884",
                  ref_offset=(3.81, -1.27), val_offset=(3.81, 1.524))
s_mcu.add_wire(93.98, en_y, *sw1.pin_xy("2"))
s_mcu.add_junction(93.98, en_y)
s_mcu.tie_gnd(*sw1.pin_xy("1"), 3.81)

# Boot (GPIO0)
s_mcu.add_box("BOOT BUTTON (GPIO0 STRAPPING)", 33.02, 193.04, 147.32, 256.54)
r8 = s_mcu.place("YoloUNO:R", "R8", "10.0k", "YoloUNO:R_0603_1608Metric",
                 58.42, 214.63, rot=0, mpn="RC0603FR-0710KL", lcsc="C25804")
s_mcu.tie_rail("+3V3", *r8.pin_xy("1"), -3.81)
boot_y = 226.06
s_mcu.add_wire(*r8.pin_xy("2"), 58.42, boot_y)
s_mcu.add_wire(58.42, boot_y, 121.92, boot_y)
s_mcu.add_label("BOOT_IO0", 121.92, boot_y, rot=180)

sw2 = s_mcu.place("YoloUNO:TS-1187A", "SW2", "BOOT", "YoloUNO:SW_Push_1P1T_XKB_TS-1187A",
                  88.9, 238.76, rot=90, mpn="TS-1187A-B-A-B", lcsc="C318884",
                  ref_offset=(3.81, -1.27), val_offset=(3.81, 1.524))
s_mcu.add_wire(88.9, boot_y, *sw2.pin_xy("2"))
s_mcu.add_junction(88.9, boot_y)
s_mcu.tie_gnd(*sw2.pin_xy("1"), 3.81)


# ==============================================================================
# SHEET 4: 03_USB_and_LEDs.kicad_sch (Blocks 4.6 & 4.7)
# ==============================================================================
s_usb = SheetBuilder("03_USB_and_LEDs.kicad_sch", "USB Type-C + ESD & Display LEDs (D13, NeoPixel)", 4, sheet_inst_uuid=sh_usb_uuid)

s_usb.add_box("4.6 USB TYPE-C RECEPTACLE (16P, INDEPENDENT 5.1k Rd) & ESD PROTECTION (USBLC6-2SC6)", 20.32, 20.32, 403.86, 142.24)

j2 = s_usb.place("YoloUNO:TYPE-C-31-M-12", "J2", "USB_C_16P", "YoloUNO:USB_C_Receptacle_HRO_TYPE-C-31-M-12",
                 68.58, 78.74, rot=0, mpn="TYPE-C-31-M-12", lcsc="C165948",
                 ref_offset=(-15.24, -25.4), val_offset=(-15.24, -22.86))

s_usb.tie_gnd(*j2.pin_xy("A1"), 6.35)
s_usb.tie_gnd(*j2.pin_xy("SH"), 6.35)
s_usb.add_nc(*j2.pin_xy("A8"))
s_usb.add_nc(*j2.pin_xy("B8"))

cc1_xy = j2.pin_xy("A5")
cc2_xy = j2.pin_xy("B5")
r9 = s_usb.place("YoloUNO:R", "R9", "5.10k 1%", "YoloUNO:R_0603_1608Metric",
                 111.76, 104.14, rot=0, mpn="RC0603FR-075K1L", lcsc="C23186")
r10 = s_usb.place("YoloUNO:R", "R10", "5.10k 1%", "YoloUNO:R_0603_1608Metric",
                  137.16, 104.14, rot=0, mpn="RC0603FR-075K1L", lcsc="C23186")
s_usb.add_wire(cc1_xy[0], cc1_xy[1], 111.76, cc1_xy[1])
s_usb.add_wire(111.76, cc1_xy[1], *r9.pin_xy("1"))
s_usb.tie_gnd(*r9.pin_xy("2"), 3.81)

s_usb.add_wire(cc2_xy[0], cc2_xy[1], 137.16, cc2_xy[1])
s_usb.add_wire(137.16, cc2_xy[1], *r10.pin_xy("1"))
s_usb.tie_gnd(*r10.pin_xy("2"), 3.81)

vbus_xy = j2.pin_xy("A4")
s_usb.add_wire(vbus_xy[0], vbus_xy[1], 160.02, 63.50)
s_usb.add_wire(160.02, 63.50, 160.02, 53.34)
s_usb.add_wire(160.02, 53.34, 248.92, 53.34)

s_usb.tie_rail("VBUS", 177.8, 53.34, -5.08)
s_usb.add_junction(177.8, 53.34)
s_usb.add_wire(195.58, 53.34, 195.58, 45.72)
s_usb.add_junction(195.58, 53.34)
s_usb.add_pwr_flag(195.58, 45.72, rot=0)

c14 = s_usb.place("YoloUNO:C", "C14", "100nF", "YoloUNO:C_0603_1608Metric",
                  215.9, 68.58, rot=0, mpn="CL10B104KB8NNNC", lcsc="C1591")
s_usb.add_wire(215.9, 53.34, *c14.pin_xy("1"))
s_usb.add_junction(215.9, 53.34)
s_usb.tie_gnd(*c14.pin_xy("2"), 3.81)

u5 = s_usb.place("YoloUNO:USBLC6-2SC6", "U5", "USBLC6-2SC6", "YoloUNO:SOT-23-6",
                 248.92, 78.74, rot=0, mpn="USBLC6-2SC6", lcsc="C7519",
                 ref_offset=(3.81, -8.89), val_offset=(3.81, -6.35))
s_usb.add_wire(248.92, 53.34, *u5.pin_xy("5"))
s_usb.tie_gnd(*u5.pin_xy("2"), 5.08)

dn_a = j2.pin_xy("A7")
dn_b = j2.pin_xy("B7")
s_usb.add_wire(dn_a[0], dn_a[1], 172.72, dn_a[1])
s_usb.add_wire(172.72, dn_a[1], 172.72, dn_b[1])
s_usb.add_wire(dn_b[0], dn_b[1], *u5.pin_xy("1"))
s_usb.add_junction(172.72, dn_b[1])

dp_a = j2.pin_xy("A6")
dp_b = j2.pin_xy("B6")
s_usb.add_wire(dp_b[0], dp_b[1], 177.8, dp_b[1])
s_usb.add_wire(177.8, dp_b[1], 177.8, dp_a[1])
s_usb.add_wire(dp_a[0], dp_a[1], *u5.pin_xy("3"))
s_usb.add_junction(177.8, dp_a[1])

s_usb.add_wire(*u5.pin_xy("6"), 274.32, 78.74)
s_usb.add_wire(274.32, 78.74, 274.32, 74.93)
s_usb.add_wire(274.32, 74.93, 304.8, 74.93)
s_usb.add_glabel("USB_DN", 304.8, 74.93, rot=0, shape="bidirectional")

s_usb.add_wire(*u5.pin_xy("4"), 274.32, 81.28)
s_usb.add_wire(274.32, 81.28, 274.32, 85.09)
s_usb.add_wire(274.32, 85.09, 304.8, 85.09)
s_usb.add_glabel("USB_DP", 304.8, 85.09, rot=0, shape="bidirectional")
s_usb.add_note("Route USB_DP / USB_DN as 90 Ohm differential pair (w=0.25mm, s=0.20mm over In1.Cu GND)", 274.32, 101.6, size=1.3)


# --- Block 4.7: User LED D13 & NeoPixel RGB + Level Shifter ---
s_usb.add_box("4.7 USER LED D13 (GPIO48) & NEOPIXEL RGB WS2812B WITH 3.3V->5V BUFFER (SN74LV1T34)", 20.32, 152.4, 403.86, 266.7)

s_usb.add_glabel("D13", 53.34, 200.66, rot=180, shape="input")
r12 = s_usb.place("YoloUNO:R", "R12", "270R 1%", "YoloUNO:R_0603_1608Metric",
                  76.2, 200.66, rot=90, mpn="RC0603FR-07270RL", lcsc="C22966",
                  ref_offset=(-3.81, -5.08), val_offset=(-3.81, -2.54))
s_usb.add_wire(53.34, 200.66, *r12.pin_xy("1"))
d4 = s_usb.place("YoloUNO:LED", "D4", "D13_RED", "YoloUNO:LED_0603_1608Metric",
                 99.06, 212.09, rot=90, mpn="19-217/R6C-AL1M2VY/3T", lcsc="C2286",
                 ref_offset=(3.175, -1.27), val_offset=(3.175, 1.524))
s_usb.add_wire(*r12.pin_xy("2"), 99.06, 200.66)
s_usb.add_wire(99.06, 200.66, *d4.pin_xy("2"))
s_usb.tie_gnd(*d4.pin_xy("1"), 3.81)

s_usb.add_glabel("NEO_GPIO45", 162.56, 203.2, rot=180, shape="input")
r13 = s_usb.place("YoloUNO:R", "R13", "10.0k (Strap PD)", "YoloUNO:R_0603_1608Metric",
                  180.34, 218.44, rot=0, mpn="RC0603FR-0710KL", lcsc="C25804")
u6 = s_usb.place("YoloUNO:SN74LV1T34DBVR", "U6", "SN74LV1T34DBVR", "YoloUNO:SOT-23-5",
                 228.6, 203.2, rot=0, mpn="SN74LV1T34DBVR", lcsc="C100018",
                 ref_offset=(5.08, -10.16), val_offset=(5.08, -7.62))
s_usb.add_wire(162.56, 203.2, *u6.pin_xy("2"))
s_usb.add_wire(180.34, 203.2, *r13.pin_xy("1"))
s_usb.add_junction(180.34, 203.2)
s_usb.tie_gnd(*r13.pin_xy("2"), 3.81)

s_usb.add_wire(*u6.pin_xy("5"), 228.6, 182.88)
s_usb.add_wire(228.6, 182.88, 256.54, 182.88)
s_usb.tie_rail("+5V", 228.6, 182.88, -3.81)
s_usb.add_junction(228.6, 182.88)
c15 = s_usb.place("YoloUNO:C", "C15", "100nF", "YoloUNO:C_0603_1608Metric",
                  256.54, 195.58, rot=0, mpn="CL10B104KB8NNNC", lcsc="C1591")
s_usb.add_wire(256.54, 182.88, *c15.pin_xy("1"))
s_usb.tie_gnd(*c15.pin_xy("2"), 3.81)
s_usb.tie_gnd(*u6.pin_xy("3"), 5.08)

d5 = s_usb.place("YoloUNO:WS2812B-B", "D5", "WS2812B-B", "YoloUNO:LED_WS2812B_PLCC4_5.0x5.0mm_P3.2mm",
                 314.96, 203.2, rot=0, mpn="WS2812B-B/W", lcsc="C114586",
                 ref_offset=(5.08, -10.16), val_offset=(5.08, -7.62))
s_usb.add_wire(*u6.pin_xy("4"), *d5.pin_xy("4"))
s_usb.add_label("NEO_DIN_5V", 274.32, 203.2)
s_usb.add_nc(*d5.pin_xy("2"))
s_usb.tie_gnd(*d5.pin_xy("3"), 5.08)

s_usb.add_wire(*d5.pin_xy("1"), 314.96, 182.88)
s_usb.add_wire(314.96, 182.88, 345.44, 182.88)
s_usb.tie_rail("+5V", 314.96, 182.88, -3.81)
s_usb.add_junction(314.96, 182.88)
c16 = s_usb.place("YoloUNO:C", "C16", "100nF", "YoloUNO:C_0603_1608Metric",
                  345.44, 195.58, rot=0, mpn="CL10B104KB8NNNC", lcsc="C1591")
s_usb.add_wire(345.44, 182.88, *c16.pin_xy("1"))
s_usb.tie_gnd(*c16.pin_xy("2"), 3.81)


# ==============================================================================
# SHEET 5: 04_Peripherals_and_Headers.kicad_sch (Block 4.8)
# ==============================================================================
s_per = SheetBuilder("04_Peripherals_and_Headers.kicad_sch", "Peripherals: UNO R3, 12x Grove, QWIIC, I2C & 4x Servo", 5, sheet_inst_uuid=sh_per_uuid)

# Stagger horizontal power stubs on adjacent pins so "+3V3" and "GND" labels never touch!
def wire_conn_pins_horiz(sheet, sym, pin_spec):
    pwr_idx = 0
    for pnum, action in pin_spec.items():
        px, py = sym.pin_xy(pnum)
        if action == "NC":
            sheet.add_nc(px, py)
        elif action in ("GND", "+3V3", "+5V"):
            dx = -6.35 if (pwr_idx % 2 == 0) else -13.97
            pwr_idx += 1
            sheet.tie_horiz_pwr(action, px, py, dx)
        elif isinstance(action, tuple) and action[0] == "L":
            ex = round(px - 11.43, 2)
            sheet.add_wire(ex, py, px, py)
            sheet.add_label(action[1], ex, py, rot=0)
        elif isinstance(action, tuple) and action[0] == "G":
            ex = round(px - 8.89, 2)
            sheet.add_wire(ex, py, px, py)
            sheet.add_glabel(action[1], ex, py, rot=180, shape=action[2])

# --- Sub-box A: Arduino UNO R3 Shield Headers (J17, J18, J19, J20) ---
s_per.add_box("4.8A ARDUINO UNO R3 HEADERS", 15.24, 17.78, 129.54, 175.26)

j17 = s_per.place("YoloUNO:UNO_Header_1x08", "J17", "UNO_PWR_1x08", "YoloUNO:PinSocket_1x08_P2.54mm_Vertical",
                  58.42, 48.26, rot=0, mpn="FH-254-1x08", lcsc="C49661", ref_offset=(-2.54, -10.16), val_offset=(-2.54, 13.97))
wire_conn_pins_horiz(s_per, j17, {
    "1": "NC",
    "2": "+3V3",
    "3": ("G", "MCU_EN", "bidirectional"),
    "4": "+3V3",
    "5": "+5V",
    "6": "GND",
    "7": "GND",
    "8": ("G", "VIN_PROT", "input"),
})

j18 = s_per.place("YoloUNO:UNO_Header_1x06", "J18", "UNO_ANALOG_1x06", "YoloUNO:PinSocket_1x06_P2.54mm_Vertical",
                  58.42, 104.14, rot=0, mpn="FH-254-1x06", lcsc="C49659", ref_offset=(-2.54, -7.62), val_offset=(-2.54, 11.43))
wire_conn_pins_horiz(s_per, j18, {
    "1": ("L", "A0_RAW"),
    "2": ("G", "A1", "bidirectional"),
    "3": ("G", "A2", "bidirectional"),
    "4": ("G", "A3", "bidirectional"),
    "5": ("G", "I2C_SDA", "bidirectional"),
    "6": ("G", "I2C_SCL", "bidirectional"),
})

j19 = s_per.place("YoloUNO:UNO_Header_1x10", "J19", "UNO_DIGH_1x10", "YoloUNO:PinSocket_1x10_P2.54mm_Vertical",
                  114.3, 53.34, rot=0, mpn="FH-254-1x10", lcsc="C49663", ref_offset=(-2.54, -12.7), val_offset=(-2.54, 16.51))
wire_conn_pins_horiz(s_per, j19, {
    "1": ("G", "D8", "bidirectional"),
    "2": ("G", "D9", "bidirectional"),
    "3": ("G", "D10", "bidirectional"),
    "4": ("G", "D11", "bidirectional"),
    "5": ("G", "D12", "bidirectional"),
    "6": ("G", "D13", "bidirectional"),
    "7": "GND",
    "8": "+3V3",
    "9": ("G", "I2C_SDA", "bidirectional"),
    "10": ("G", "I2C_SCL", "bidirectional"),
})

j20 = s_per.place("YoloUNO:UNO_Header_1x08", "J20", "UNO_DIGL_1x08", "YoloUNO:PinSocket_1x08_P2.54mm_Vertical",
                  114.3, 121.92, rot=0, mpn="FH-254-1x08", lcsc="C49661", ref_offset=(-2.54, -10.16), val_offset=(-2.54, 13.97))
wire_conn_pins_horiz(s_per, j20, {
    "1": ("G", "D0_RX", "bidirectional"),
    "2": ("G", "D1_TX", "bidirectional"),
    "3": ("G", "D2", "bidirectional"),
    "4": ("G", "D3", "bidirectional"),
    "5": ("G", "D4", "bidirectional"),
    "6": ("G", "D5", "bidirectional"),
    "7": ("G", "D6", "bidirectional"),
    "8": ("G", "D7", "bidirectional"),
})


# --- Sub-box B: A0 0-5V Analog Conditioning (Q[10]: JP1 rot=0 so Bridged12 = Direct 3.3V default!) ---
s_per.add_box("4.8B A0 0-5V CONDITIONING (Q[10])", 15.24, 182.88, 129.54, 266.7)

# JP1 at rot=0: Pin 1=(-5.08,0) [LEFT=Direct A0_RAW, Bridged12 default!], Pin 3=(5.08,0) [RIGHT=5V Scaled], Pin 2=(0,-3.81)->(sx, sy+3.81) [BOTTOM=A0_ADC]
jp1 = s_per.place("YoloUNO:SolderJumper_3_Bridged12", "JP1", "A0_3V3/5V", "YoloUNO:SolderJumper-3_P1.3mm_Bridged12_Pad1.0x1.5mm",
                  63.5, 208.28, rot=0, mpn="SJ-3-1.3MM", lcsc="N/A",
                  ref_offset=(-5.08, -6.35), val_offset=(-5.08, -3.81))
# A0_RAW enters at (25.4, 208.28) -> connects straight into JP1 Pin 1 (58.42, 208.28), and branches UP at x=43.18 to R16/R17 on the right!
# Even simpler: branch UP at x=43.18 -> y=195.58 -> x=93.98 -> DOWN through R16 (6.8k) -> midpoint (93.98, 208.28) -> JP1 Pin 3 (68.58, 208.28), and R17 (10k) below!
s_per.add_wire(27.94, 208.28, *jp1.pin_xy("1"))
s_per.add_label("A0_RAW", 27.94, 208.28, rot=0)

s_per.add_wire(43.18, 208.28, 43.18, 194.31)
s_per.add_junction(43.18, 208.28)
s_per.add_wire(43.18, 194.31, 96.52, 194.31)

r16 = s_per.place("YoloUNO:R", "R16", "6.80k 1%", "YoloUNO:R_0603_1608Metric",
                  96.52, 200.66, rot=0, mpn="RC0603FR-076K8L", lcsc="C23212")
r17 = s_per.place("YoloUNO:R", "R17", "10.0k 1%", "YoloUNO:R_0603_1608Metric",
                  96.52, 218.44, rot=0, mpn="RC0603FR-0710KL", lcsc="C25804")
s_per.add_wire(96.52, 194.31, *r16.pin_xy("1"))
s_per.add_wire(*r16.pin_xy("2"), *r17.pin_xy("1"))  # midpoint at y = 209.55 -> wait: 200.66+3.81=204.47, 218.44-3.81=214.63, mid=209.55; let's align midpoint with JP1 Pin 3 y=208.28!
# If R16 is at y=199.39 (pin1=195.58, pin2=203.20) and R17 is at y=217.17 (pin1=213.36, pin2=220.98) -> midpoint is 208.28 EXACTLY!
s_per.symbols.pop()
s_per.symbols.pop()
s_per.wires.pop()
s_per.wires.pop()
s_per.wires.pop()  # pop (43.18, 194.31, 96.52, 194.31)
s_per.wires.pop()  # pop (43.18, 208.28, 43.18, 194.31)

s_per.add_wire(43.18, 208.28, 43.18, 195.58)
s_per.add_wire(43.18, 195.58, 96.52, 195.58)
r16 = s_per.place("YoloUNO:R", "R16", "6.80k 1%", "YoloUNO:R_0603_1608Metric",
                  96.52, 199.39, rot=0, mpn="RC0603FR-076K8L", lcsc="C23212")
r17 = s_per.place("YoloUNO:R", "R17", "10.0k 1%", "YoloUNO:R_0603_1608Metric",
                  96.52, 217.17, rot=0, mpn="RC0603FR-0710KL", lcsc="C25804")
s_per.add_wire(*r16.pin_xy("2"), *r17.pin_xy("1"))
s_per.add_wire(*jp1.pin_xy("3"), 96.52, 208.28)
s_per.add_junction(96.52, 208.28)
s_per.tie_gnd(*r17.pin_xy("2"), 3.81)

# JP1 Pin 2 (63.5, 212.09) -> y=226.06 -> C17 (100nF) + A0_ADC
s_per.add_wire(*jp1.pin_xy("2"), 63.5, 226.06)
s_per.add_wire(63.5, 226.06, 81.28, 226.06)
s_per.add_glabel("A0_ADC", 81.28, 226.06, rot=0, shape="output")
c17 = s_per.place("YoloUNO:C", "C17", "100nF", "YoloUNO:C_0603_1608Metric",
                  63.5, 238.76, rot=0, mpn="CL10B104KB8NNNC", lcsc="C1591")
s_per.add_wire(63.5, 226.06, *c17.pin_xy("1"))
s_per.add_junction(63.5, 226.06)
s_per.tie_gnd(*c17.pin_xy("2"), 3.81)


# --- Sub-box C: 12x Grove 2.0mm Connectors (J3..J14, All VCC=+3V3) ---
s_per.add_box("4.8C 12x GROVE 2.0mm PORTS (4x ANALOG YELLOW, 4x DIGITAL WHITE, 4x I2C RED - VCC=+3V3)", 134.62, 17.78, 406.4, 187.96)

grove_specs = [
    ("J3", "Grove_A6-A3", ("G", "A3", "bidirectional"), ("G", "A6", "bidirectional"), "110990030", "C2906423", 175.26, 48.26),
    ("J4", "Grove_A3-A2", ("G", "A2", "bidirectional"), ("G", "A3", "bidirectional"), "110990030", "C2906423", 241.3, 48.26),
    ("J5", "Grove_A2-A1", ("G", "A1", "bidirectional"), ("G", "A2", "bidirectional"), "110990030", "C2906423", 307.34, 48.26),
    ("J6", "Grove_A1-A0", ("L", "A0_RAW"), ("G", "A1", "bidirectional"), "110990030", "C2906423", 373.38, 48.26),
    ("J7", "Grove_D10-D9", ("G", "D9", "bidirectional"), ("G", "D10", "bidirectional"), "112060001", "C492401", 175.26, 104.14),
    ("J8", "Grove_D8-D7", ("G", "D7", "bidirectional"), ("G", "D8", "bidirectional"), "112060001", "C492401", 241.3, 104.14),
    ("J9", "Grove_D6-D5", ("G", "D5", "bidirectional"), ("G", "D6", "bidirectional"), "112060001", "C492401", 307.34, 104.14),
    ("J10", "Grove_D4-D3", ("G", "D3", "bidirectional"), ("G", "D4", "bidirectional"), "112060001", "C492401", 373.38, 104.14),
    ("J11", "Grove_I2C4", ("G", "I2C_SCL", "bidirectional"), ("G", "I2C_SDA", "bidirectional"), "110990031", "C2906424", 175.26, 160.02),
    ("J12", "Grove_I2C3", ("G", "I2C_SCL", "bidirectional"), ("G", "I2C_SDA", "bidirectional"), "110990031", "C2906424", 241.3, 160.02),
    ("J13", "Grove_I2C2", ("G", "I2C_SCL", "bidirectional"), ("G", "I2C_SDA", "bidirectional"), "110990031", "C2906424", 307.34, 160.02),
    ("J14", "Grove_I2C1", ("G", "I2C_SCL", "bidirectional"), ("G", "I2C_SDA", "bidirectional"), "110990031", "C2906424", 373.38, 160.02),
]

for ref, val, sig1, sig2, mpn, lcsc, gx, gy in grove_specs:
    gsym = s_per.place("YoloUNO:Grove_1x04", ref, val, "YoloUNO:NS-Tech_Grove_1x04_P2mm_Vertical",
                       gx, gy, rot=0, mpn=mpn, lcsc=lcsc, ref_offset=(-2.54, -7.62), val_offset=(-2.54, 8.89))
    wire_conn_pins_horiz(s_per, gsym, {
        "1": sig1,
        "2": sig2,
        "3": "+3V3",
        "4": "GND",
    })


# --- Sub-box D: Shared I2C Pull-Ups (1.5k E12, Q[11]) & QWIIC JST-SH (J15) ---
s_per.add_box("4.8D I2C PULL-UPS (1.5k) & QWIIC", 134.62, 195.58, 251.46, 266.7)

r14 = s_per.place("YoloUNO:R", "R14", "1.50k 1%", "YoloUNO:R_0603_1608Metric",
                  152.4, 223.52, rot=0, mpn="RC0603FR-071K5L", lcsc="C22843")
r15 = s_per.place("YoloUNO:R", "R15", "1.50k 1%", "YoloUNO:R_0603_1608Metric",
                  175.26, 223.52, rot=0, mpn="RC0603FR-071K5L", lcsc="C22843")
s_per.add_wire(152.4, 214.63, 175.26, 214.63)
s_per.add_wire(152.4, 214.63, *r14.pin_xy("1"))
s_per.add_wire(175.26, 214.63, *r15.pin_xy("1"))
s_per.tie_rail("+3V3", 163.83, 214.63, -2.54)
s_per.add_junction(163.83, 214.63)

j15 = s_per.place("YoloUNO:QWIIC_JST_SH_1x04", "J15", "QWIIC_SM04B", "YoloUNO:JST_SH_SM04B-SRSS-TB_1x04-1MP_P1.00mm_Horizontal",
                  231.14, 231.14, rot=0, mpn="SM04B-SRSS-TB", lcsc="C160404",
                  ref_offset=(-2.54, -8.89), val_offset=(-2.54, -6.35))
s_per.tie_horiz_pwr("GND", *j15.pin_xy("1"), -6.35)
s_per.tie_horiz_pwr("+3V3", *j15.pin_xy("2"), -13.97)

p3x, p3y = j15.pin_xy("3")
s_per.add_wire(152.4, r14.pin_xy("2")[1], 152.4, p3y)
s_per.add_wire(152.4, p3y, p3x, p3y)
s_per.add_wire(144.78, p3y, 152.4, p3y)
s_per.add_junction(152.4, p3y)
s_per.add_glabel("I2C_SDA", 144.78, p3y, rot=180, shape="bidirectional")

p4x, p4y = j15.pin_xy("4")
s_per.add_wire(175.26, r15.pin_xy("2")[1], 175.26, p4y)
s_per.add_wire(175.26, p4y, p4x, p4y)
s_per.add_wire(144.78, p4y, 175.26, p4y)
s_per.add_junction(175.26, p4y)
s_per.add_glabel("I2C_SCL", 144.78, p4y, rot=180, shape="bidirectional")

s_per.tie_gnd(*j15.pin_xy("MP"), 3.81)


# --- Sub-box E: 4x Servo GVS Headers (J21..J24) + 470uF Bulk Cap (C18) ---
s_per.add_box("4.8E 4x SERVO GVS HEADERS (+5V) & 470uF BULK CAPACITOR", 256.54, 195.58, 406.4, 266.7)

c18 = s_per.place("YoloUNO:C_Polarized", "C18", "470uF/10V", "YoloUNO:CP_Elec_8x10.5",
                  269.24, 231.14, rot=0, mpn="EEE-FK1A471P", lcsc="C134734")
s_per.tie_rail("+5V", *c18.pin_xy("1"), -5.08)
s_per.tie_gnd(*c18.pin_xy("2"), 5.08)

servo_specs = [
    ("J21", "Servo_D2", "D2", 322.58, 220.98),
    ("J22", "Servo_D13", "D13", 381.0, 220.98),
    ("J23", "Servo_D12", "D12", 322.58, 248.92),
    ("J24", "Servo_D11", "D11", 381.0, 248.92),
]
for sref, sval, snet, sx, sy in servo_specs:
    sv = s_per.place("YoloUNO:Servo_GVS_1x03", sref, sval, "YoloUNO:PinHeader_1x03_P2.54mm_Vertical",
                     sx, sy, rot=0, mpn="X6511WV-1x3", lcsc="C492405", ref_offset=(-2.54, -8.255), val_offset=(-2.54, -5.715))
    wire_conn_pins_horiz(s_per, sv, {
        "1": "GND",
        "2": "+5V",
        "3": ("G", snet, "bidirectional"),
    })


# ---------------- Save All 5 Sheets & Project `.kicad_pro` ----------------
for sh in [root, s_pwr, s_mcu, s_usb, s_per]:
    path = sh.save()
    print("Generated:", path)

pro_data = {
    "board": {
        "3dviewports": [],
        "design_settings": {
            "defaults": {
                "board_outline_line_width": 0.05,
                "copper_line_width": 0.2,
                "courtyard_line_width": 0.05,
                "silk_line_width": 0.12,
                "silk_text_size_h": 1.0,
                "silk_text_size_v": 1.0,
                "silk_text_thickness": 0.15,
                "zones": {
                    "min_clearance": 0.25,
                    "min_thickness": 0.25,
                    "pad_connection": 1,
                    "thermal_relief_gap": 0.25,
                    "thermal_relief_spoke_width": 0.35,
                },
            },
            "diff_pair_dimensions": [{"gap": 0.2, "via_gap": 0.25, "width": 0.25}],
            "drc_exclusions": [],
            "meta": {"version": 2},
            "rules": {
                "max_error": 0.005,
                "min_clearance": 0.15,
                "min_connection": 0.0,
                "min_copper_edge_clearance": 0.3,
                "min_hole_clearance": 0.25,
                "min_hole_to_hole": 0.25,
                "min_microvia_diameter": 0.2,
                "min_microvia_drill": 0.1,
                "min_resolved_spokes": 1,
                "min_silk_clearance": 0.0,
                "min_text_height": 0.8,
                "min_text_thickness": 0.08,
                "min_through_hole_diameter": 0.2,
                "min_track_width": 0.15,
                "min_via_annular_width": 0.1,
                "min_via_diameter": 0.6,
                "min_via_drill": 0.3,
                "solder_mask_to_copper_clearance": 0.0,
            },
        },
    },
    "libraries": {"pinned_footprint_libs": ["YoloUNO"], "pinned_symbol_libs": ["YoloUNO"]},
    "meta": {"filename": "YoloUNO.kicad_pro", "version": 3},
    "net_settings": {
        "classes": [
            {
                "bus_width": 12,
                "clearance": 0.15,
                "diff_pair_gap": 0.20,
                "diff_pair_via_gap": 0.25,
                "diff_pair_width": 0.25,
                "line_style": 0,
                "microvia_diameter": 0.3,
                "microvia_drill": 0.1,
                "name": "Default",
                "pcb_color": "rgba(0, 0, 0, 0.000)",
                "priority": 2147483647,
                "schematic_color": "rgba(0, 0, 0, 0.000)",
                "track_width": 0.25,
                "tuning_profile": "",
                "via_diameter": 0.6,
                "via_drill": 0.3,
                "wire_width": 6,
            }
        ],
        "meta": {"version": 5},
        "net_colors": None,
        "netclass_assignments": None,
        "netclass_patterns": [],
    },
    "schematic": {
        "legacy_lib_dir": "",
        "legacy_lib_list": [],
        "top_level_sheets": [
            {"filename": "YoloUNO.kicad_sch", "name": "YoloUNO", "uuid": ROOT_UUID}
        ],
    },
    "sheets": [
        [ROOT_UUID, "Root"],
        [sh_pwr_uuid, "01_Power_Supply"],
        [sh_mcu_uuid, "02_MCU_ESP32S3"],
        [sh_usb_uuid, "03_USB_and_LEDs"],
        [sh_per_uuid, "04_Peripherals_and_Headers"],
    ],
    "text_variables": {},
}

pro_path = os.path.join(HW_DIR, "YoloUNO.kicad_pro")
with open(pro_path, "w", encoding="utf-8") as f:
    json.dump(pro_data, f, indent=2)
print("Generated:", pro_path)
