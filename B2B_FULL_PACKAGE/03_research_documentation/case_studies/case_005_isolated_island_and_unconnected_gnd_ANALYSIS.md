# Case: case_005_isolated_island_and_unconnected_gnd

## Tiêu đề
Giải quyết 3 lỗi vi phạm khoảng cách lỗ khoan (DRC) và 3 chân hở kết nối (Unconnected Pads) do hiện tượng cô lập đảo đồng và thiếu via fanout

## Mô tả kỹ thuật & nguyên nhân
1. **Lỗi lỗ khoan co-located và quá gần PTH:**
   - Trùng via tại (119.60, 67.10) do chạy trùng lặp hai lần câu via GND.
   - Via tại (121.50, 72.00) cách chân xuyên lỗ PTH pad 2 J_BOOT chỉ 0.00mm < 0.25mm.
   - Sửa đổi: Xóa via trùng tại (119.6, 67.1) và via thừa tại (121.5, 72.0) vì pad J_BOOT.2 đã cắm thẳng xuống plane In1.Cu.

2. **Hiện tượng cô lập đảo đồng B.Cu (Isolated Zone Island) tại R_FB2.2:**
   - Pad R_FB2.2 (GND) nằm trên B.Cu bị kẹt trong một vùng đồng nhỏ bị bao bọc bởi BST_FB (Y=106.5) và đường +5V chạy ngang 5mm tại Y=108.5, phía trên F.Cu lại bị chắn bởi SW_NODE.
   - Sửa đổi: Đặt via +5V tại (86.825, 108.0) cắm thẳng lên track +5V của F.Cu, xóa bỏ hoàn toàn đường track ngang B.Cu từ (91.775, 108.5) đến (86.825, 108.5). Hành lang B.Cu rộng 2.2mm được mở thông, cho phép mặt phẳng đồng B.Cu GND tràn vào nối thẳng pad R_FB2.2.

3. **Thiếu via fanout GND cho U6.15 và R_PROG.2:**
   - Pad U6.15 (F.Cu) nối via GND tại (93.69, 75.71) bằng track 0.25mm.
   - Pad R_PROG.2 (B.Cu) nối via GND tại (82.40, 99.15) bằng track 0.25mm.

## Kết quả nghiệm thu
- Trước sửa: 3 DRC violations, 3 unconnected pads.
- Sau sửa: 0 DRC violations, 0 unconnected pads, 0 footprint errors.
