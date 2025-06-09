#!/bin/bash

# Hàm để dọn dẹp tiến trình server chạy nền
cleanup() {
    echo "---"
    echo "Đang dừng server (PID: $SERVER_PID)..."
    # Lệnh kill có thể thất bại nếu tiến trình đã tự kết thúc, nên ta ẩn lỗi đi
    kill $SERVER_PID 2>/dev/null
    echo "Dọn dẹp hoàn tất."
}

# Đặt một "bẫy" để chạy hàm cleanup khi script kết thúc hoặc bị ngắt (Ctrl+C)
trap cleanup EXIT

echo "--- DEMO: Tấn Công Giả Mạo Chữ Ký ECDSA do Lỗ Hổng Không Băm Dữ Liệu ---"
echo

# 1. Khởi động server ở chế độ nền
echo "1. Đang khởi động server có lỗ hổng ở chế độ nền..."
python3 server.py &
SERVER_PID=$!
# Cho server một chút thời gian để khởi động
sleep 2
echo "   Server đang chạy với PID: $SERVER_PID"
echo

# 2. Chạy client hợp pháp để lấy một chữ ký hợp lệ
echo "2. Đang chạy client hợp pháp để tạo chữ ký cho một tin nhắn hợp lệ."
echo "   Chữ ký này sẽ bị 'đánh cắp' để phục vụ cho cuộc tấn công."
echo "---"
python3 client.py
echo "---"
echo

# 3. Hướng dẫn người dùng và chạy script của kẻ tấn công
echo "3. Bây giờ, chúng ta sẽ thực hiện cuộc tấn công."
echo "   Kẻ tấn công sẽ yêu cầu nhập 'Stolen Signature' (Chữ ký bị đánh cắp)."
echo "   HÀNH ĐỘNG: Vui lòng SAO CHÉP giá trị 'Signature' từ kết quả ở trên và DÁN vào lời nhắc bên dưới."
echo "---"
python3 attacker.py
echo "---"
echo

echo "Demo kết thúc."
# "Bẫy" đã đặt ở trên sẽ tự động xử lý việc dọn dẹp