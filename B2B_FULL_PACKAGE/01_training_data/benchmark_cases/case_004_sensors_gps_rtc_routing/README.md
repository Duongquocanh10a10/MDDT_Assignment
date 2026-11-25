# Case: case_004_sensors_gps_rtc_routing

## Tiêu đề
Tái định tuyến chuẩn Manhattan 0 lỗi DRC cho Khối cảm biến/GPS/RTC/OneWire (Group G)

## Mô tả kỹ thuật & nguyên nhân
1. Khắc phục 50 lỗi DRC nghiêm trọng trong Khối cảm biến/GPS/RTC/OneWire (Group G):
   - Tuyến I2C_SCL, I2C_SDA, ONEWIRE_TEMP cũ chạy dọc tại X=121..122 đâm xuyên qua hàng chân THT của header J_BOOT (chân 1..6), nút SW_BOOT và lỗ ốc H2.
   - Tuyến GPS_TX và GPS_RX cũ chạy ngang tại Y=77.5..78.5 trên B.Cu đâm xuyên qua các pad SMD 11..14 của chip U_GPS (NEO-M8N) và chéo nhau.
   - Tuyến VBAT_RTC cũ chạy đâm vào pad BT1.2 (GND) và cắt RTC_INT.
2. Giải pháp kỹ thuật Manhattan:
   - Dời trục chính I2C_SCL (X=123.80 B.Cu) và I2C_SDA (X=123.20 B.Cu) ra hành lang bờ Đông ngoài cùng thông suốt, lách qua khoảng trống an toàn Y in [62.0, 68.0] giữa H2 và J_BOOT.
   - Sắp xếp trật tự topo I2C theo nguyên tắc bao ngoài (SCL bao ngoài SDA) loại bỏ giao cắt trên B.Cu và cắm thẳng vào pad SOIC-16 của U7 (DS3231).
   - ONEWIRE_TEMP đi qua hành lang F.Cu X=116.50 né điện trở kéo R_SDA_PU, chuyển tầng B.Cu tại Y=62.50 sang cột X=124.40 cắm thẳng vào chân THT J_TEMP.2 và rẽ nhánh F.Cu vào R_DS_PU.1.
   - GPS_TX và GPS_RX đi vòng qua phía Nam U_GPS tại Y=79.50 và Y=80.20 trên B.Cu theo thứ tự topo song song, cách pad U_GPS > 1.05mm.
   - VBAT_RTC chạy 100% trên B.Cu tại Y=106.50 (0 via), vượt qua đường RTC_INT thông qua via cầu tầng Manhattan tại X=103.00 trên F.Cu.
3. Kết quả: Giảm từ 50 lỗi DRC về 0 lỗi DRC tuyệt đối.

## Số lỗi DRC trước sửa: 50
## Số lỗi DRC sau sửa: 0
