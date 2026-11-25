# Case: case_003_lcd_block_routing

## Tiêu đề
Khắc phục 54 lỗi DRC định tuyến khối màn hình LCD qua kỹ thuật East Breakout Highway và trật tự topo Manhattan

## Mô tả kỹ thuật & nguyên nhân
## 1. Bản chất sự cố
Khối hiển thị màn hình LCD (Group F) gồm 9 nets liên kết MCU ESP32-WROOM-32 (U6) ở đỉnh với Header J_LCD ở đáy bờ Tây, cùng mạch kích đèn nền Q2/R_BL_LIM/R_LCD_GATE/R_LCD_PD.
Phiên bản ban đầu phát sinh 54 vi phạm DRC nghiêm trọng do:
- Xung đột giao cắt trực giao: Đoạn dây dọc LCD_BL_PWM chạy trên B.Cu đè ngang qua SPI_MOSI trên B.Cu.
- Va chạm chân linh kiện: Dây LCD_GATE chạy thẳng qua chân nguồn GND của bóng SOT-23 Q2.
- Va chạm vỏ giắc USB Type-C: Đường SPI_MOSI chạy sát mép va vào vùng đệm 4 chân vỏ THT của J_USB.SH.
- Nghẽn mạch thoát chân MCU: 4 chân SPI_SCK, LCD_CS, LCD_RST, LCD_DC đi ngược hướng vào bụng chip ESP32 và chồng lấn kênh Y trên B.Cu.

## 2. Phân tích không gian hình học & Giải pháp kỹ thuật Manhattan
- Tách tầng trực giao nghiêm ngặt: Chuyển toàn bộ các đoạn dây dọc dài sang F.Cu và các đoạn dây ngang sang B.Cu. Dây LCD_BL_PWM chạy dọc trên F.Cu dọc X=88.50mm, lách qua phía trên tại Y=54.50mm trên B.Cu để sang bờ Đông (X=123.80mm), triệt tiêu hoàn toàn giao cắt với SPI_MOSI.
- Tái định tuyến lách chân Q2: Dây LCD_GATE từ Q2.1 rẽ sang phía Tây (X=111.40mm) trước khi hạ độ cao xuống phía Nam, giữ khoảng cách >0.35mm với chân Q2.2 (GND).
- Khai thông hành lang mép Tây: Tịnh tiến đường trục dọc SPI_MOSI ra biên X=74.00mm, cách mép vỏ USB SH >0.75mm (đạt ngưỡng an toàn vượt mức 0.15mm).
- East Breakout Highway & Topological Ordering:
  * 4 chân tín hiệu MCU U6 thoát ra hướng Đông theo thứ tự bậc thang không cắt nhau trên F.Cu: U6.27 (X=110.2), U6.28 (X=110.8), U6.29 (X=111.4), U6.30 (X=112.0).
  * Chuyển tầng qua via so le xuống dải hành lang ngang B.Cu (Y=78.8..81.5mm).
  * Đường LCD_DC đi ngang trên cùng tại Y=78.80mm sang mép Tây X=74.00mm, không chắn các đường phía dưới.
  * 3 đường SCK, RST, CS đi dọc trên B.Cu qua khe thông thoáng X=81.6..82.8mm, rẽ Tây theo thứ tự tăng dần bán kính (Y=96.50, 97.10, 97.70mm) cắm trực tiếp vào pad THT của J_LCD mà không cần via phụ ở bờ Tây.

## 3. Kết quả nghiệm thu
DRC giảm từ 54 lỗi xuống đúng 0 lỗi (100% Pass DRC).

## Số lỗi DRC trước sửa: 54
## Số lỗi DRC sau sửa: 0
