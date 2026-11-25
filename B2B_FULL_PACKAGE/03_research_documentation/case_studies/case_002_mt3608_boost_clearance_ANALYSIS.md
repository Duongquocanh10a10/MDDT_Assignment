# Case: case_002_mt3608_boost_clearance

## Tiêu đề
MT3608 SW_NODE and BST_FB Clearance Tuning

## Mô tả kỹ thuật & nguyên nhân
Khối MT3608 có đường SW_NODE dòng lớn (width 0.40mm) quá sát pad U4.6 (khoảng cách 0.150mm) và via GND cản trở đường hồi tiếp BST_FB. Sửa đổi: Dời nhánh ngang SW_NODE xuống Y=107.30mm và dời via GND lên Y=103.60mm đạt đúng 0 lỗi DRC.

## Số lỗi DRC trước sửa: 2
## Số lỗi DRC sau sửa: 0
