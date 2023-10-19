<?php

function disable_ob() {
    // Turn off output buffering
    ini_set('output_buffering', 'off');
    // Turn off PHP output compression
    ini_set('zlib.output_compression', false);
    // Implicitly flush the buffer(s)
    ini_set('implicit_flush', true);
    ob_implicit_flush(true);
    // Clear, and turn off output buffering
    while (ob_get_level() > 0) {
        // Get the curent level
        $level = ob_get_level();
        // End the buffering
        ob_end_clean();
        // If the current level has not changed, abort
        if (ob_get_level() == $level) break;
    }
    // Disable apache output buffering/compression
    if (function_exists('apache_setenv')) {
        apache_setenv('no-gzip', '1');
        apache_setenv('dont-vary', '1');
    }
}



if (isset($_GET['package_name']) && $_GET['package_name'] != "") {

    $package_name = $_GET['package_name'];

    file_put_contents('userDB/tempPackage.txt', $package_name);

    exec("python ManageBackendScripts.py 2>&1", $output4, $returnCode);

    $country = [];
    $values = [];

    $row = 1;
    if (($handle = fopen("userDB/dataForFrontend.csv", "r")) !== FALSE) {
        while (($data = fgetcsv($handle, 1000, ",")) !== FALSE) {
            $num = count($data);

            if ($row != 1){
                for ($c=0; $c < $num; $c++) {

                    array_push($country, $data[$c]);
                    array_push($values, $data[$c + 1]);
                    $c++;
                }
            }
            $row++;
        }
        fclose($handle);
    }

    if ($country == []){
        echo json_encode("No data for this repository");
    }
    else {
        $return = ["region"=>$country, "contributions"=>$values];
        echo json_encode($return);
    }

}
else {
    echo "package name missing";
}

?>
