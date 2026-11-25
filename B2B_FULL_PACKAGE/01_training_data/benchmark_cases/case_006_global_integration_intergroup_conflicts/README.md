# Case: case_01_global_integration_intergroup_conflicts

## Tiêu đề
Xung đột liên nhóm khi tích hợp toàn bộ Groups A-H trên bo mạch thu nhỏ 52x75mm

## Mô tả kỹ thuật & nguyên nhân

Khi ghép nối tất cả 8 nhóm định tuyến độc lập (A-H), xuất hiện 230 vi phạm DRC liên nhóm:
1. Xung đột sườn Tây F.Cu: PH_ADC, VBAT_SW, CHIP_PU và SPI_MOSI cùng chia sẻ hành lang X=73.8..74.0mm.
2. Xung đột đại lộ ngang B.Cu: Các đường bus tín hiệu LCD (SPI_SCK, LCD_RST, LCD_CS) chạy dọc B.Cu cắt ngang qua các đại lộ nguồn VBAT_RAW (Y=97.0), VBUS (Y=91.5) và +3V3 (Y=104.04).
3. Xung đột khối giao tiếp USB-UART: CP_VDD, USB_D-, USB_D+ cấn đường VBUS và RTC_INT.
4. Xung đột cụm chân MCU Đông: TX0, RX0, IO0 cắt chéo qua các đường I2C, OneWire và LCD Control.
Khắc phục: Xem mô tả kỹ thuật trong diff.patch.


## Số lỗi DRC trước sửa: 230
## Số lỗi DRC sau sửa: 0
