#!/bin/bash

# Dừng các tiến trình cũ có thể đang chạy từ lần demo trước
pkill -f "sage server.py"

echo "====================================================="
echo "      Pohlig-Hellman ECDLP Attack Demo"
echo "====================================================="
echo "Kịch bản này sẽ minh họa một cuộc tấn công vào một hệ thống"
echo "mật mã đường cong Elliptic, nơi bậc của điểm sinh G là"
echo "một 'số trơn' (chỉ có các thừa số nguyên tố nhỏ)."
echo
echo "1. Server sẽ khởi động, tạo một khóa bí mật, và mã hóa cờ."
echo "2. Client sẽ kết nối, nhận các tham số công khai."
echo "3. Client sẽ sử dụng thuật toán Pohlig-Hellman để giải"
echo "   bài toán ECDLP một cách hiệu quả và khôi phục khóa bí mật."
echo "4. Client sẽ dùng khóa bí mật khôi phục được để giải mã"
echo "   cờ và gửi lại cho server để xác minh."
echo "====================================================="
echo

# 1. Kiểm tra xem SageMath đã được cài đặt chưa
echo "[*] Đang kiểm tra cài đặt SageMath..."
if ! command -v sage &> /dev/null
then
    echo "[!] LỖI: Lệnh 'sage' không được tìm thấy."
    echo "    Demo này yêu cầu SageMath. Vui lòng cài đặt và đảm bảo"
    echo "    lệnh 'sage' có trong PATH của hệ thống."
    echo "    Hướng dẫn cài đặt: https://www.sagemath.org/download.html"
    exit 1
fi
echo "[+] Đã tìm thấy SageMath!"
echo

# 2. Khởi động server ở chế độ nền
echo "[*] Đang khởi động server ở chế độ nền..."
# Chạy server với sage và chuyển hướng output vào file log
sage server.py > server.log 2>&1 &
SERVER_PID=$!

# Chờ một chút để server khởi động hoàn toàn
sleep 2

# Kiểm tra xem server có khởi động thành công không
if ! ps -p $SERVER_PID > /dev/null; then
    echo "[!] LỖI: Server không thể khởi động. Vui lòng kiểm tra server.log để biết lỗi."
    exit 1
fi
echo "[+] Server đã khởi động với PID: $SERVER_PID. Xem server.log để biết chi tiết."
echo "--- BẮT ĐẦU OUTPUT SERVER (từ server.log) ---"
head -n 11 server.log
echo "..."
echo "--- KẾT THÚC OUTPUT SERVER ---"
echo

# 3. Chạy client
echo "[*] Đang chạy client để thực hiện cuộc tấn công..."
echo "--- BẮT ĐẦU OUTPUT CLIENT ---"
sage client.py
echo "--- KẾT THÚC OUTPUT CLIENT ---"
echo

# 4. Dọn dẹp: Dừng server
echo "[*] Dọn dẹp: Đang dừng server (PID: $SERVER_PID)..."
kill $SERVER_PID
sleep 1 # Chờ tiến trình kết thúc
echo "[+] Server đã dừng."
echo
echo "====================================================="
echo " Demo kết thúc."
echo "====================================================="