<?php

    //ket noi voi database
    $server = "localhost";
    $user = "tuan";
    $password = "100902"; /* set me first */
    $dbname = "SIC_IOT_FINAL";
    $conn = mysqli_connect($server,$user,$password,$dbname);

    // Tạo kết nối
    // $conn = mysqli_connect($servername, $username, $password, $database);

    // Kiểm tra kết nối
    // if (!$conn) {
    //     die("Connection failed: " . mysqli_connect_error());
    // }
    // echo "Connected successfully";
?>