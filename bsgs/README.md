# Baby-Step Giant-Step Attack Demo
Demo đơn giản của thuật toán Baby-Step Giant-Step (BSGS) trên đường cong Elliptic secp256k1.
Đây là phần demo đơn giản với không giản key nhỏ, trong project thực tế không gian key sẽ nhỏ nhưng vừa đủ lớn, sát với thực tế hơn.
## Nguyên lý
BSGS là thuật toán tìm kiếm logarit rời rạc với độ phức tạp O(√N), sử dụng phương pháp meet-in-the-middle:
1. Với không gian tìm kiếm N, chọn m = ⌈√N⌉
2. Baby steps: Tính và lưu G, 2G, 3G, ..., (m-1)G
3. Giant steps: Tính Q - iG và kiểm tra xem có trong bảng baby steps không
4. Nếu tìm thấy Q - iG = jG, thì private key = im + j
## Lổ hổng và bối cảnh tấn công
Không gian khóa (số lượng khả năng của $x$) nhỏ, thường thấy trong các:
- Mật khẩu ngắn dùng làm khóa riêng,
- ECDSA/ECDH sử dụng các đường cong với bậc nhỏ (không đủ lớn).
## Cấu trúc code
- `ecc_helper.py`: Thư viện hỗ trợ tính toán trên đường cong elliptic
- `bsgs_attack_demo.py`: Cài đặt thuật toán BSGS và demo
- `README.md`: Tài liệu hướng dẫn


## Yêu cầu
```bash
pip install gmpy2
```
## Sử dụng

```bash
python bsgs_attack_demo.py
```

Demo sẽ:
1. Tạo cặp khóa với private key 
2. Thực hiện tấn công BSGS để tìm lại private key
3. Hiển thị kết quả và thời gian chạy
## Lưu ý
- Demo này chỉ hoạt động với private key nhỏ (để demo)
- Với private key lớn (thực tế), cần:
  - Nhiều bộ nhớ hơn cho bảng baby steps
  - Tối ưu việc lưu trữ và tìm kiếm
  - Sử dụng kỹ thuật song song hóa 