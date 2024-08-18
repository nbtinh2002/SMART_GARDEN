<?php
header("Access-Control-Allow-Origin: *");
header("Access-Control-Allow-Methods: POST, GET, OPTIONS");
header("Access-Control-Allow-Headers: Content-Type, Authorization");

header('Content-Type: application/json');

// Kết nối đến cơ sở dữ liệu
include("config.php");

// Đọc dữ liệu từ cơ sở dữ liệu
$sql = "SELECT * FROM DATA";
$result = mysqli_query($conn, $sql);

// Gửi dữ liệu đến website
$data = array();
foreach ($result as $row) {
    $data[] = $row;
}

mysqli_close($conn);

echo json_encode($data);
?>
