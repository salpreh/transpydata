<?php

/////////////////////////
/////// FUNCTIONS ///////
/////////////////////////


/////////////////////////
/////// MAIN SRV ////////
/////////////////////////

$rawJson = file_get_contents('php://input');
$data = json_decode($rawJson, true);

if (is_null($data)) {
    http_response_code(400);
    $res = [
        'error_msg' => 'No incoming data'
    ];
    die(json_encode($res));
}

$data['id'] = uniqid();

http_response_code(201);
die(json_encode($data));
