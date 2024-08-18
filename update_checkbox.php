<?php
// send a JSON message to website 
header("Access-Control-Allow-Origin: *");
header("Access-Control-Allow-Methods: POST, GET, OPTIONS");
header("Access-Control-Allow-Headers: Content-Type, Authorization");


header('Content-Type: application/json');// muc dich la de thong bao cho trinh duyet web biet rang file code dc gui duoi dang JSON( dang chuoi data)
//connect
include("config.php");
// read data from database
$sql = "select * from CONTROL";
$result = mysqli_query($conn, $sql);

// send data to website
$data = array();
foreach ($result as $row) {

        $data[]= $row;// se doc tung hang 1 cua result
    }


mysqli_close($conn);

echo json_encode($data);
?>