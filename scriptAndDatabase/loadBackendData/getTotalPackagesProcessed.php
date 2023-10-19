<?php
    $fp = file('../userDB/DecisionDatabase.csv');
    echo json_encode(count($fp));
?>