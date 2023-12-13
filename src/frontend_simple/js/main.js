// API URL
axios.defaults.baseURL = '/api';

// File input elements
var input_file = document.getElementById("input_file");
var input_file_view = document.getElementById('input_file_view');
var downloadButton = document.getElementById('downloadButton');
var processingFilename = ''; // To store the filename of the processing video

function upload_file() {
    input_file_view.src = null;
    input_file.click();
}

function input_file_onchange() {
    var file_to_upload = input_file.files[0];
    input_file_view.src = URL.createObjectURL(file_to_upload);

    var formData = new FormData();
    formData.append("file", file_to_upload);
    axios.post('/predict', formData, {
        headers: {
            'Content-Type': 'multipart/form-data'
        }
    }).then(function (response) {
        console.log(response.data);
        processingFilename = response.data.filename; // Store the filename for status checking
        alert("Your video is being processed. Please keep the page open.");
        checkStatus();
    }).catch(function (error) {
        console.error("Error during file upload:", error);
        alert("There was an error uploading your video.");
    });
}

input_file.onchange = input_file_onchange;

function checkStatus() {
    if (!processingFilename) {
        console.error("No processing filename available for status check.");
        return;
    }

    axios.get(`/status/${processingFilename}`).then(response => {
        console.log('Status:', response.data.status);
        if (response.data.status === 'completed') {
            showDownloadButton();
        } else if (response.data.status === 'error') {
            alert("An error occurred during video processing.");
        } else {
            // If still processing, check again after some time
            setTimeout(checkStatus, 5000);
        }
    }).catch(error => console.error("Error checking status:", error));
}

function showDownloadButton() {
    downloadButton.style.display = 'block';
    downloadButton.addEventListener('click', downloadVideo);
}

function downloadVideo() {
    axios.get(`/get_video/${processingFilename}`, {
        responseType: 'blob'
    }).then(response => {
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', processingFilename); // Use the processing filename for download
        document.body.appendChild(link);
        link.click();
        link.parentNode.removeChild(link);
        window.URL.revokeObjectURL(url);
    }).catch(error => console.error("Error getting video:", error));
}

