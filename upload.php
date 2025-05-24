<?php
$targetDir = "uploads/";
if (!file_exists($targetDir)) {
    mkdir($targetDir, 0777, true); // Create uploads folder if not exists
}

if (isset($_FILES["audio"])) {
    $fileName = basename($_FILES["audio"]["name"]);
    $targetFilePath = $targetDir . $fileName;
    $fileType = pathinfo($targetFilePath, PATHINFO_EXTENSION);

    // Allow only audio files
    $allowTypes = array('mp3', 'wav', 'ogg', 'm4a');
    if (in_array($fileType, $allowTypes)) {
        if (move_uploaded_file($_FILES["audio"]["tmp_name"], $targetFilePath)) {
            echo json_encode(["file_path" => "uploads/" . $fileName]);
        } else {
            echo json_encode(["error" => "File upload failed."]);
        }
    } else {
        echo json_encode(["error" => "Only audio files are allowed."]);
    }
} else {
    echo json_encode(["error" => "No file uploaded."]);
}
?>
