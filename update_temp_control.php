<?php
// Kiểm tra xem có dữ liệu được gửi từ phía client hay không
if (isset($_POST['Temperature'])) {
    // Kết nối tới cơ sở dữ liệu
    include("config.php");

    // Kiểm tra kết nối
    if ($conn->connect_error) {
        die('Kết nối tới cơ sở dữ liệu thất bại: ' . $conn->connect_error);
    }

    // Lấy dữ liệu gửi từ phía client
    $temp = $_POST['Temperature'];
    
    // Cập nhật giá trị trong cơ sở dữ liệu
    $sql = "UPDATE control SET Temp = '$temp'";

    if ($conn->query($sql) === TRUE) {
        echo 'Cập nhật thành công';
    } else {
        echo 'Lỗi khi cập nhật: ' . $conn->error;
    }

    $conn->close();
}
?>
