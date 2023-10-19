<?php

$country = [];
$region = [];

$row = 1;
if (($handle = fopen("../database/countryToRegion.csv", "r")) !== FALSE) {
    while (($data = fgetcsv($handle, 1000, ";")) !== FALSE) {
        $num = count($data);
        // echo "<p> $num fields in line $row: <br /></p>\n";

        if ($row != 1){
            for ($c=0; $c < $num; $c++) {

                array_push($country, $data[$c]);
                array_push($region, $data[$c + 1]);
                $c++;
                // echo $data[$c] . "<br />\n";
            }
        }
        $row++;
    }
    fclose($handle);
}

// print_r($country) ;
// print_r($region) ;

$return = ["country"=>$country, "regions"=>$region];
echo json_encode($return);
?>