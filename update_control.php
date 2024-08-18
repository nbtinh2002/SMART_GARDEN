<?php
// Thêm tiêu đề CORS
header("Access-Control-Allow-Origin: *"); // Cho phép tất cả các nguồn. Thay đổi "*" thành nguồn cụ thể nếu cần.
header("Access-Control-Allow-Methods: POST, GET, OPTIONS"); // Các phương thức HTTP được phép
header("Access-Control-Allow-Headers: Content-Type"); // Các tiêu đề được phép

// Kiểm tra xem có dữ liệu được gửi từ phía client hay không
if (isset($_POST['column']) && isset($_POST['value'])) {
    // Kết nối tới cơ sở dữ liệu
    include("config.php");

    // Kiểm tra kết nối
    if ($conn->connect_error) {
        die('Kết nối tới cơ sở dữ liệu thất bại: ' . $conn->connect_error);
    }

    // Lấy dữ liệu gửi từ phía client
    $column = $conn->real_escape_string($_POST['column']);
    $value = $conn->real_escape_string($_POST['value']);

    // Cập nhật giá trị trong cơ sở dữ liệu
    $sql = "UPDATE CONTROL SET $column = $value";

    if ($conn->query($sql) === TRUE) {
        echo 'Cập nhật thành công';
    } else {
        echo 'Lỗi khi cập nhật: ' . $conn->error;
    }

    $conn->close();
} else {
    echo 'Thiếu dữ liệu gửi từ client';
}
?>
