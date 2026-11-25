# PHASE 2 — GIẢI THÍCH SƠ ĐỒ NGUYÊN LÝ (SCHEMATIC) & KIỂM TRA ERC (MỤC 4.1 – 4.9)

**Phần mềm thiết kế:** KiCad E.D.A. `10.0.8` (`D:\KiCad\bin\kicad-cli.exe`)  
**Cấu trúc bản vẽ:** Sơ đồ phân cấp 5 tờ khổ A3 (`YoloUNO.kicad_sch` + 4 tờ chức năng con), nhúng toàn bộ thư viện tự trị `YoloUNO.kicad_sym` & `YoloUNO.pretty`  
**Kết quả kiểm tra ERC (`--severity-all`):** **`0 Errors, 0 Warnings`** ([erc_report.rpt](file:///c:/Users/QUOC%20ANH%20PC/Downloads/MDDT_Assignment/YoloUNO_Project/outputs/erc_report.rpt))

---

## 4.1. Khối nguồn vào và bảo vệ (`01_Power_Supply.kicad_sch` — Khung 4.1)

- **Chức năng từng linh kiện:**
  - `J1` (`PJ-002A`, Jack DC `5.5 × 2.1 mm`): Nhận nguồn adapter ngoài $6–12\text{ V DC}$ (`Pin 1` cực dương `VIN_RAW`, `Pin 2` & `Pin 3` nối `GND`).
  - `D1` (`SMBJ15CA`, TVS hai chiều $15\text{ V}$, công suất đỉnh $600\text{ W}$): Mắc song song ngay sát `J1` để kẹp các xung quá áp đột biến (cắm nóng adapter, sét lan truyền) ở $\pm 24.4\text{ V} < 30\text{ V}$ giới hạn $V_{DS(\text{max})}$ của `Q1`. Việc dùng TVS **hai chiều (`CA`)** thay vì một chiều (`A`) đảm bảo khi người dùng cắm ngược cực $-12\text{ V}$, `D1` không dẫn ngắn mạch gây nổ diode khi chưa có cầu chì.
  - `Q1` (`AO3407A`, P-MOSFET $-30\text{ V}, \pm 20\text{ V } V_{GS}, R_{DS(\text{on})} \le 48\text{ m}\Omega$): Đấu kiểu **Ideal Diode chống ngược cực** với chân **Drain (`Pin 3`)** hướng về phía `VIN_RAW` và **Source (`Pin 2`)** hướng về tải `VIN_PROT`.
    - *Khi cấp đúng cực ($+6\text{ V} \to +12\text{ V}$):* Ban đầu body diode của `Q1` dẫn từ Drain sang Source, kéo Source lên $\approx V_{\text{IN}} - 0.7\text{ V}$; chân Gate được kéo về `GND` qua $R_1 = 47\text{ k}\Omega$ tạo $V_{GS} \ll V_{GS(\text{th})}$ làm kênh P dẫn bão hòa hoàn toàn, sụt áp chỉ $\Delta V \le 48\text{ mV/A}$ (tổn hao nhỏ hơn $>6\times$ so với diode Schottky `SS34`).
    - *Khi cắm ngược cực ($-12\text{ V}$):* Body diode phân cực ngược, cả Source và Gate đều ở $0\text{ V}$ ($V_{GS} = 0\text{ V}$), `Q1` khóa hoàn toàn cách ly mạch tải.
  - `D2` (`BZT52C10`, Zener $10\text{ V}$) & `R1` ($47\text{ k}\Omega$): Ghim điện áp $|V_{GS}| \le 10\text{ V}$ ngay cả khi adapter vọt lên $15–20\text{ V}$, bảo vệ tuyệt đối lớp oxit cực cổng của `Q1`.
  - `C1` ($47\,\mu\text{F} / 25\text{ V}$ tụ hóa SMD) & `C2` ($100\text{ nF}$ tụ gốm X7R): Lọc gợn áp tần số thấp và khử nhiễu cao tần trên đường `VIN_PROT` (đồng thời nối ra chân `VIN` của Header Arduino `J17.8`).

---

## 4.2. Khối hạ áp đồng bộ 5 V (`01_Power_Supply.kicad_sch` — Khung 4.2)

- **Chức năng từng linh kiện:**
  - `U1` (`TPS54202DDCR`, SOT-23-6): IC hạ áp xung đồng bộ (tích hợp sẵn MOSFET High-side và Low-side), $V_{\text{IN}} = 4.5–28\text{ V}$, dòng liên tục $2.0\text{ A}$, tần số đóng cắt $f_{\text{sw}} = 500\text{ kHz}$, điện áp tham chiếu nội $V_{\text{FB}} = 0.596\text{ V}$.
  - `C3` ($10\,\mu\text{F} / 25\text{ V}$ X5R): Tụ gốm ESR thấp đặt sát chân `VIN (Pin 3)` và `GND (Pin 1)` để khép kín vòng dòng xung $di/dt$ lớn.
  - `R2` ($100\text{ k}\Omega$): Kéo chân `EN (Pin 5)` lên `VIN_PROT` để tự động bật nguồn Buck khi có nguồn DC.
  - `C4` ($100\text{ nF}$): Tụ Bootstrap nối giữa `BOOT (Pin 6)` và `SW (Pin 2)` cấp áp kích cực cổng cho MOSFET kênh N phía cao.
  - `L1` (`SRN6045TA-150M`, $15\,\mu\text{H}$ bọc từ chống nhiễu, $I_{\text{sat}} \ge 2.9\text{ A}$): Tích trữ và san phẳng dòng điện ($\Delta I_L = 0.390\text{ A}$ tại $12\text{ V} \to 5.05\text{ V}$, $I_{\text{peak}} = 2.195\text{ A} < 2.9\text{ A}$).
  - `R3` ($68.0\text{ k}\Omega\ 1\%$) & `R4` ($9.10\text{ k}\Omega\ 1\%$): Cầu phân áp hồi tiếp đặt điện áp ngõ ra `5V_BUCK`:
    $$V_{\text{OUT}} = 0.596 \times \left(1 + \frac{68.0}{9.10}\right) = 5.050\text{ V}$$
  - `C5, C6` ($2 \times 22\,\mu\text{F} / 16\text{ V}$ X5R mắc song song): Giảm trở kháng ra và giữ độ gợn sóng điện áp đầu ra $< 20\text{ mV}_{\text{pp}}$.

---

## 4.3. Khối chọn nguồn tự động USB / DC (`01_Power_Supply.kicad_sch` — Khung 4.3)

- **Chức năng từng linh kiện:**
  - `U2` (`TPS2116DRLR`, SOT-583-8): Bộ ghép kênh nguồn ưu tiên $2.5\text{ A}$ ($R_{\text{ON}} = 40\text{ m}\Omega\text{ typ}$) với cấu trúc MOSFET đối lưng chặn dòng ngược hai chiều (*Reverse Current Blocking*).
  - `R5` ($36.0\text{ k}\Omega\ 1\%$) & `R6` ($10.0\text{ k}\Omega\ 1\%$): Chia áp từ `5V_BUCK` vào chân so sánh `PR1 (Pin 4)` (với `MODE (Pin 5)` nối lên `5V_BUCK`), thiết lập ngưỡng chuyển mạch ưu tiên $V_{\text{SW}} = 1.0\text{ V}\times(1 + 36/10) = 4.60\text{ V}$.
  - `C7` ($10\,\mu\text{F} / 16\text{ V}$): Tụ ổn định đường nguồn tổng `+5V` sau khi chuyển mạch.
- **Ba kịch bản vận hành:**
  1. *Chỉ cắm Jack DC:* `5V_BUCK = 5.05 V > 4.60 V` ($V_{\text{PR1}} = 1.10\text{ V} > 1.0\text{ V}$) → `U2` nối `VIN1 (5V_BUCK)` ra `+5V`, ngắt hoàn toàn nhánh `VBUS`.
  2. *Chỉ cắm USB-C:* `5V_BUCK = 0 V` ($V_{\text{MODE}} = 0\text{ V}, V_{\text{PR1}} = 0\text{ V}$) → theo bảng chân trị mục 7.3.1 datasheet `TPS2116`, IC hoạt động ở chế độ Auto-ORing và dẫn `VIN2 (VBUS)` ra `+5V` với sụt áp chỉ $\sim 20–40\text{ mV}$, đồng thời khóa nhánh `VIN1` không cho dòng chảy ngược về IC Buck.
  3. *Cắm đồng thời cả USB-C và Jack DC:* Vì $V_{\text{PR1}} > 1.0\text{ V}$, `U2` **cưỡng bức ưu tiên chọn nguồn DC (`5V_BUCK`)** ngay cả khi `VBUS` máy tính cao hơn nhẹ ($5.1\text{ V}$), giải phóng hoàn toàn tải servo khỏi cổng USB PC và triệt tiêu 100% dòng ngược.

---

## 4.4. Khối ổn áp 3,3 V & LED báo nguồn (`01_Power_Supply.kicad_sch` — Khung 4.4)

- `U3` (`AP2114H-3.3TRG1`, SOT-223): Hạ áp từ `+5V` xuống `+3V3` ($I_{\text{max}} = 1.0\text{ A}$, $V_{\text{DO}} = 450\text{ mV typ}$, $I_Q = 60\,\mu\text{A}$). Chân Tab (`Pin 2`) nối trực tiếp ra `+3V3` giúp truyền nhiệt xuống vùng đồng PCB.
- `C8` ($10\,\mu\text{F}$) lọc đầu vào; `C9` ($22\,\mu\text{F}$) và `C10` ($100\text{ nF}$) lọc đầu ra đáp ứng tức thời xung dòng phát Wi-Fi của ESP32-S3.
- `R11` ($470\,\Omega$) & `D3` (LED xanh lá, $V_F \approx 2.1\text{ V}$): Báo nguồn `+3V3` hoạt động tốt với dòng tiết kiệm $I_{\text{PWR}} = (3.3 - 2.1)/470 = 2.55\text{ mA}$.

---

## 4.5. Khối vi điều khiển ESP32-S3-WROOM-1-N16R8 (`02_MCU_ESP32S3.kicad_sch` — Khung 4.5)

- **Tụ lọc nguồn sát module:** `C11` ($22\,\mu\text{F}$) + `C12` ($100\text{ nF}$) đặt sát chân `3V3 (Pin 2)` cung cấp năng lượng tức thời cho khối khuếch đại RF $2.4\text{ GHz}$.
- **Mạch Reset (`EN`):** `R7` ($10.0\text{ k}\Omega$) + `C13` ($1\,\mu\text{F}$) tạo hằng số thời gian $\tau = 10.0\text{ ms}$ ($t_{0.75V_{DD}} = 13.86\text{ ms} \gg 50\,\mu\text{s}$), kết hợp nút nhấn `SW1` (`RESET`) và kết nối tới chân `RESET` của Header Arduino `J17.3`.
- **Mạch Boot (`GPIO0`):** `SW2` (`BOOT`) kéo `IO0` xuống `GND` để vào chế độ nạp USB-Serial/JTAG, kèm trở kéo lên `R8` ($10.0\text{ k}\Omega$).
- **Xử lý chân đặc biệt:** Các chân `IO35, IO36, IO37` (dùng nội bộ cho 8 MB Octal PSRAM trên `N16R8`) và `IO46` (strapping pull-down nội) được đánh dấu `No-Connect (X)` rõ ràng.

### Bảng ánh xạ chân thực tế trên Schematic (`U4`)

| Chân `U4` | Tên GPIO | Nhãn mạch (Net) | Kết nối ngoại vi trên bo |
| :---: | :--- | :--- | :--- |
| `36, 37` | `GPIO44, GPIO43` | `D0_RX`, `D1_TX` | Header UNO `J20.1 (D0)`, `J20.2 (D1)` (UART0) |
| `5` | `GPIO5 (ADC1_CH4)` | `D2` | Header UNO `J20.3`, Servo `J21.3` |
| `6, 7` | `GPIO6, GPIO7` | `D3`, `D4` | Header UNO `J20.4–5`, Grove Digital `J10 (D4-D3)` |
| `12, 17` | `GPIO8, GPIO9` | `D5`, `D6` | Header UNO `J20.6–7`, Grove Digital `J9 (D6-D5)` |
| `18, 10` | `GPIO10, GPIO17` | `D7`, `D8` | Header UNO `J20.8 / J19.1`, Grove Digital `J8 (D8-D7)` |
| `11, 23` | `GPIO18, GPIO21` | `D9`, `D10` | Header UNO `J19.2–3`, Grove Digital `J7 (D10-D9)` |
| `31, 24` | `GPIO38, GPIO47` | `D11`, `D12` | Header UNO `J19.4–5`, Servo `J24.3 (D11)`, `J23.3 (D12)` |
| `25` | `GPIO48` | `D13` | Header UNO `J19.6`, Servo `J22.3`, LED đỏ `D4` (`R12 = 270 Ω`) |
| `39` | `GPIO1 (ADC1_CH0)` | `A0_ADC` | Cực giữa `JP1.2` + `C17` (`A0_RAW` từ `J18.1` & Grove `J6.1`) |
| `38, 15, 4` | `GPIO2, GPIO3, GPIO4` | `A1`, `A2`, `A3` | Header UNO `J18.2–4`, Grove Analog `J6, J5, J4, J3` |
| `22` | `GPIO14 (ADC2_CH3)` | `A6` | Grove Analog `J3.2 (A6-A3)` |
| `19, 20` | `GPIO11, GPIO12` | `I2C_SDA`, `I2C_SCL` | UNO `J18.5–6`, `J19.9–10`, Grove `J11–J14`, QWIIC `J15`, `R14/R15 (1.5 kΩ)` |
| `13, 14` | `GPIO19, GPIO20` | `USB_DN`, `USB_DP` | Qua ESD `U5 (USBLC6-2SC6)` tới USB Type-C `J2` |
| `26` | `GPIO45` (Strapping) | `NEO_GPIO45` | `R13 (10 kΩ PD)` + Buffer `U6 (SN74LV1T34)` → `D5 (WS2812B)` |

---

## 4.6. Khối USB Type-C & Bảo vệ ESD (`03_USB_and_LEDs.kicad_sch` — Khung 4.6)

- `J2` (`TYPE-C-31-M-12`, USB-C 16 chân): Các chân `VBUS (A4/A9/B4/B9)` nối chung cấp nguồn `VBUS`; vỏ kim loại `SH` và `GND (A1/A12/B1/B12)` nối thẳng xuống mặt phẳng `GND` để thoát xung tĩnh điện ngắn nhất. Hai chân `SBU1/SBU2` để hở (`NC`).
- `R9` & `R10` ($2 \times 5.10\text{ k}\Omega\ 1\%$ độc lập): Kéo riêng từng chân `CC1 (A5)` và `CC2 (B5)` xuống `GND`, định danh thiết bị chuẩn Sink UFP trên mọi cáp USB-C ↔ USB-C có E-Marker.
- `U5` (`USBLC6-2SC6`) & `C14` ($100\text{ nF}$): Kẹp xung ESD $\pm 15\text{ kV}$ trên cả `VBUS` lẫn cặp vi sai `D+/D−` (`A6+B6` và `A7+B7`) với điện dung ký sinh cực nhỏ ($2.5\text{ pF}$) trước khi đưa vào `GPIO20 / GPIO19`.

---

## 4.7. Khối hiển thị LED D13 & NeoPixel (`03_USB_and_LEDs.kicad_sch` — Khung 4.7)

- **LED D13:** `GPIO48 (D13)` lái trực tiếp LED đỏ `D4` qua `R12 = 270 Ω` ($I = 4.81\text{ mA}$, $P_{R12} = 6.26\text{ mW}$).
- **NeoPixel RGB:** Chân strapping `GPIO45` được giữ mức `0` an toàn lúc khởi động nhờ `R13 = 10.0 kΩ` nối `GND`, đồng thời đưa vào ngõ vào `A` của IC đệm dịch mức `U6` (`SN74LV1T34DBVR`, cấp nguồn `+5V`, lọc bởi `C15 = 100 nF`, $V_{\text{IH(min)}} = 2.0\text{ V}$). Ngõ ra `Y` xuất xung chuẩn $5.0\text{ V}$ (`NEO_DIN_5V`) cấp vào `DIN` của `D5` (`WS2812B-B`, lọc nguồn bởi `C16 = 100 nF`).

---

## 4.8. Khối kết nối ngoại vi (`04_Peripherals_and_Headers.kicad_sch` — Khung 4.8A–4.8E)

- **4.8A — Header Arduino UNO R3 (`J17–J20`):** Đúng thứ tự chuẩn UNO R3 (`J17` 8 chân nguồn với `Pin 1 = NC`, `Pin 2 = IOREF = +3V3`; `J18` `A0–A5`; `J19` `D8–D13, GND, AREF=+3V3, SDA, SCL`; `J20` `D0–D7`).
- **4.8B — Giao tiếp Analog `A0` 0–5 V (`R16, R17, JP1, C17`):** Cầu hàn 3 cực `JP1` mặc định nối tắt `1–2` đưa thẳng `A0_RAW` (`0–3.1 V`) vào `A0_ADC (GPIO1)`. Khi cắt cầu `1–2` và hàn `2–3`, tín hiệu đi qua cầu chia `R16 = 6.80 kΩ` / `R17 = 10.0 kΩ` hạ $5.00\text{ V} \to 2.976\text{ V}$ ($R_{\text{out}} = 4.05\text{ k}\Omega$) kèm tụ bù điện tích SAR `C17 = 100 nF`.
- **4.8C — 12 cổng Grove (`J3–J14`):** Bố trí 3 hàng × 4 cổng (`SIG1 – SIG2 – +3V3 – GND`), toàn bộ dùng `VCC = +3V3` bảo vệ an toàn các chân GPIO ESP32-S3.
- **4.8D — Bus I2C dùng chung & QWIIC (`R14, R15, J15`):** Chỉ đặt duy nhất **một cặp điện trở kéo lên** `R14 = R15 = 1.50 kΩ` lên `+3V3` cho toàn bộ bus (`4× Grove I2C + QWIIC J15 + UNO A4/A5 + SDA/SCL`), đảm bảo $t_r = 254\text{ ns} \le 300\text{ ns}$ ở $400\text{ kHz}, C_b = 200\text{ pF}$.
- **4.8E — 4 chân cắm Servo GVS (`J21–J24`) & Tụ Bulk (`C18`):** Cấp nguồn trực tiếp từ ray `+5V` cho `D2, D13, D12, D11`, đi kèm tụ hóa Low-ESR `C18 = 470 µF / 10 V` dập sụt áp khi servo đề-pa.

---

## 4.9. Kết quả kiểm tra ERC (Electrical Rules Check)

Chạy kiểm tra tự động nghiêm ngặt nhất (`--severity-all --exit-code-violations`) bằng KiCad 10 CLI:

```text
ERC report (2026-11-25T09:51:54, Encoding UTF8)
Report includes: Errors, Warnings, Exclusions

***** Sheet /
***** Sheet /01_Power_Supply/
***** Sheet /02_MCU_ESP32S3/
***** Sheet /03_USB_and_LEDs/
***** Sheet /04_Peripherals_and_Headers/

 ** ERC messages: 0  Errors 0  Warnings 0
```

- **Nhận xét:** Toàn bộ 5 trang schematic đạt **0 lỗi (0 Errors) và 0 cảnh báo (0 Warnings)**, mọi đường nguồn (`GND`, `VIN_PROT`, `5V_BUCK`, `VBUS`, `+5V`, `+3V3`) đều được cấp `PWR_FLAG` / `power_out` hợp lệ, không có chân bỏ trống quên gắn cờ `No-Connect`, và 100% linh kiện đã liên kết chặt chẽ với thư viện footprint nội bộ `YoloUNO.pretty`.
