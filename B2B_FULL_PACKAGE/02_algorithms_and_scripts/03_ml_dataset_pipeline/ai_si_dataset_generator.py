"""
Bộ sinh dữ liệu huấn luyện AI: Trích xuất hình học PCB & Mô phỏng SI (scikit-rf)
Dự án: Industrial Water Quality Monitoring System (IoT)
"""

import math
import os
import h5py
import numpy as np
import pcbnew
import skrf as rf
from skrf.media import MLine

PCB_PATH = "KiCad_Project/WaterSensor.kicad_pcb"
OUTPUT_H5 = "ai_si_dataset_sample.h5"

# Thông số Stackup 4 lớp chuẩn IPC-2221
# F.Cu -> In1.Cu: H = 0.20 mm, er = 4.5, Cu thickness = 0.035 mm (1 oz)
H_MM = 0.20
EPSILON_R = 4.5
COPPER_THICKNESS_MM = 0.035


def calc_microstrip_ipc(w_mm, h_mm=H_MM, er=EPSILON_R, t_mm=COPPER_THICKNESS_MM):
    """Tính trở kháng vi dải theo công thức IPC-2141 / Wheeler."""
    # Bù độ dày đồng: Weff
    if t_mm > 0:
        weff = w_mm + (t_mm / math.pi) * (1 + math.log(4 * math.pi * w_mm / t_mm))
    else:
        weff = w_mm

    w_over_h = weff / h_mm
    # Hằng số điện môi hiệu dụng
    eeff = (er + 1) / 2 + ((er - 1) / 2) * (1 / math.sqrt(1 + 12 / w_over_h))

    # Trở kháng đặc tính Z0
    if w_over_h <= 1.0:
        z0 = (60 / math.sqrt(eeff)) * math.log(8 / w_over_h + 0.25 * w_over_h)
    else:
        z0 = (120 * math.pi) / (
            math.sqrt(eeff) * (w_over_h + 1.393 + 0.667 * math.log(w_over_h + 1.444))
        )

    # Vận tốc lan truyền và điện dung/điện cảm ký sinh
    v_c = 3e8  # m/s
    v_prop = v_c / math.sqrt(eeff)
    t_pd_ns_per_m = 1e9 / v_prop
    c_per_m = math.sqrt(eeff) / (v_c * z0)
    l_per_m = z0 * math.sqrt(eeff) / v_c

    return {
        "z0_ohm": z0,
        "eeff": eeff,
        "t_pd_ns_per_m": t_pd_ns_per_m,
        "c_pf_per_mm": c_per_m * 1e9,
        "l_nh_per_mm": l_per_m * 1e6,
    }


def extract_traces_and_simulate(pcb_file=PCB_PATH):
    print(f"[*] Đang nạp bo mạch từ: {pcb_file}")
    board = pcbnew.LoadBoard(pcb_file)

    tracks = board.GetTracks()
    print(f"[*] Tổng số đoạn mạch (tracks & vias): {len(tracks)}")

    # Gom nhóm theo Net
    net_tracks = {}
    for t in tracks:
        if t.GetClass() == "PCB_TRACK":
            netname = t.GetNetname()
            if not netname:
                continue
            if netname not in net_tracks:
                net_tracks[netname] = []
            length_mm = t.GetLength() / 1e6
            width_mm = t.GetWidth() / 1e6
            layer = t.GetLayerName()
            net_tracks[netname].append(
                {"length_mm": length_mm, "width_mm": width_mm, "layer": layer}
            )

    print(f"[*] Số đường mạng có track: {len(net_tracks)}")

    # Dải tần số mô phỏng cho dataset: 100 MHz đến 5 GHz
    freq = rf.Frequency(0.1, 5.0, 101, unit="ghz")

    dataset_records = []

    for netname, segs in net_tracks.items():
        total_len = sum(s["length_mm"] for s in segs)
        if total_len < 0.1:  # Bỏ qua net siêu ngắn
            continue
        avg_width = sum(s["width_mm"] * s["length_mm"] for s in segs) / total_len

        # Tính toán đặc tính SI
        si_props = calc_microstrip_ipc(avg_width)

        # Mô phỏng S-Parameters với scikit-rf
        try:
            ms_media = MLine(
                frequency=freq,
                w=avg_width * 1e-3,
                h=H_MM * 1e-3,
                t=COPPER_THICKNESS_MM * 1e-3,
                ep_r=EPSILON_R,
                z0_port=50.0,
            )
            # Đường truyền dài total_len (mm)
            line_ntwk = ms_media.line(total_len * 1e-3, unit="m", name=netname)
            s21_mag_db = line_ntwk.s_db[:, 1, 0]  # Suy hao truyền dẫn
            s11_mag_db = line_ntwk.s_db[:, 0, 0]  # Độ phản xạ
            avg_s21_loss = float(np.mean(s21_mag_db))
            worst_s11_refl = float(np.max(s11_mag_db))
        except Exception as e:
            avg_s21_loss = 0.0
            worst_s11_refl = -99.0
            s21_mag_db = np.zeros(len(freq))
            s11_mag_db = np.zeros(len(freq))

        rec = {
            "netname": netname,
            "length_mm": total_len,
            "width_mm": avg_width,
            "z0_ohm": si_props["z0_ohm"],
            "eeff": si_props["eeff"],
            "t_pd_ns_per_m": si_props["t_pd_ns_per_m"],
            "c_pf_per_mm": si_props["c_pf_per_mm"],
            "l_nh_per_mm": si_props["l_nh_per_mm"],
            "total_delay_ps": si_props["t_pd_ns_per_m"] * total_len,
            "avg_s21_loss_db": avg_s21_loss,
            "worst_s11_db": worst_s11_refl,
            "s21_vector": s21_mag_db,
            "s11_vector": s11_mag_db,
        }
        dataset_records.append(rec)

    # Lưu thành file HDF5 chuẩn training AI
    with h5py.File(OUTPUT_H5, "w") as hf:
        # Features (Hình học): Length, Width
        geo_data = np.array(
            [[r["length_mm"], r["width_mm"]] for r in dataset_records], dtype=np.float32
        )
        # Labels (SI ground-truth): Z0, Delay, Loss, S11
        si_labels = np.array(
            [
                [
                    r["z0_ohm"],
                    r["total_delay_ps"],
                    r["avg_s21_loss_db"],
                    r["worst_s11_db"],
                ]
                for r in dataset_records
            ],
            dtype=np.float32,
        )
        s21_curves = np.array([r["s21_vector"] for r in dataset_records], dtype=np.float32)

        hf.create_dataset("features_geometry", data=geo_data)
        hf.create_dataset("labels_si_metrics", data=si_labels)
        hf.create_dataset("s21_frequency_response", data=s21_curves)
        hf.attrs["freq_start_ghz"] = 0.1
        hf.attrs["freq_stop_ghz"] = 5.0
        hf.attrs["n_points"] = len(freq)

    print(f"\n[+] ĐÃ HOÀN TẤT TRÍCH XUẤT VÀ TÍNH TOÁN {len(dataset_records)} MẪU NET!")
    print(f"[+] File dataset HDF5 đã lưu tại: {OUTPUT_H5} (Size: {os.path.getsize(OUTPUT_H5)} bytes)")

    # In kết quả tiêu biểu của các tuyến quan trọng
    targets = ["GPS_ANT", "USB_D+", "USB_D-", "SPI_SCK", "SPI_MOSI", "LCD_DC"]
    print("\n--- BẢNG THÔNG SỐ SI TRÍCH XUẤT TIÊU BIỂU ---")
    print(
        f"{'Net':<12} | {'Width (mm)':<10} | {'Len (mm)':<8} | {'Z0 (Ohm)':<8} | {'Delay (ps)':<10} | {'Loss S21 (dB)':<13}"
    )
    print("-" * 75)
    for r in dataset_records:
        if any(t in r["netname"] for t in targets):
            print(
                f"{r['netname']:<12} | {r['width_mm']:<10.3f} | {r['length_mm']:<8.2f} | {r['z0_ohm']:<8.1f} | {r['total_delay_ps']:<10.1f} | {r['avg_s21_loss_db']:<13.3f}"
            )


if __name__ == "__main__":
    extract_traces_and_simulate()
