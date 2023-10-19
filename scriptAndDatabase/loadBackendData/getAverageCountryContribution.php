<?php

$return = array();

$row = 1;
if (($handle = fopen("backendStats.csv", "r")) !== FALSE) {
    while (($data = fgetcsv($handle, 1000, ",")) !== FALSE) {
        $num = count($data);
        // echo "<p> $num fields in line $row: <br /></p>\n";

        if ($row != 1){
            for ($c=0; $c < $num; $c++) {

                $return[$data[$c]] = floatval($data[$c + 1]);

                // array_push($countryFront, $data[$c]);
                // array_push($countryback, $data[$c + 1]);
                // echo $data[$c] . "<br />\n";
                $c++;
            }
        }
        $row++;
    }
    fclose($handle);
}

// print_r($country) ;
// print_r($region) ;

echo json_encode($return);
?>