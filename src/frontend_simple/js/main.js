// API URL
axios.defaults.baseURL = '/api';

// file input
var input_file = document.getElementById("input_file");
var input_file_view = document.getElementById('input_file_view');

function upload_file() {
    // Clear
    //prediction_label.innerHTML = "";
    input_file_view.src = null;

    input_file.click();
}

function input_file_onchange() {
    // Read the uploaded file and display it
    var file_to_upload = input_file.files[0];
    input_file_view.src = URL.createObjectURL(file_to_upload);
    //prediction_label.innerHTML = "";

    // Post the video to the /predict API
    var formData = new FormData();
    formData.append("file", input_file.files[0]);
    axios.post('/predict', formData, {
        headers: {
            'Content-Type': 'multipart/form-data'
        }
    }).then(function (response) {
        console.log(response.data);
        // Assuming response includes a video ID or some status message
        alert("Your video is being processed. You will be notified when it's ready.");
        checkStatus();
        }).catch(function (error) {
        console.error("Error during file upload:", error);
        alert("There was an error uploading your video.");
    });
}

// Attach an onchange event
input_file.onchange = input_file_onchange;

function startDummyProgressBar() {
    var progress = 0;
    var progressBar = document.getElementById('progressBar');
    var downloadButton = document.getElementById('downloadButton');
    progressBar.style.width = progress + '%';

    var interval = setInterval(function() {
        progress += 5; // increment the progress
        progressBar.style.width = progress + '%';

        if (progress >= 100) {
            clearInterval(interval);
            downloadButton.style.display = 'block'; // show the download button
        }
    }, 1000); //update progress every 1 second
}

function checkStatus() {
    axios.get('/status').then(response => {
        console.log('im inside checkStatus')
        console.log(response)
        if (response.data.status === 'completed') {
            console.log('completed')
            // When processing is complete
            showDownloadButton();
        } else {
            // If still processing, check again after some time
            setTimeout(checkStatus, 5000);
        }
    }).catch(error => console.error("Error checking status:", error));
}

function showDownloadButton() {
    console.log('inside showDownload')
    var downloadButton = document.getElementById('downloadButton');
    downloadButton.style.display = 'block'; // Show the download button
}

function downloadVideo() {
    // Request the processed video from the backend
    console.log('inside download')
    axios.get('/get_video', {
        responseType: 'blob'  // Important to handle binary data
    }).then(response => {
        // Create a URL for the blob
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', 'test.mp4'); // Specify the download file name
        document.body.appendChild(link);
        link.click();
        
        // Clean up and revoke the URL
        link.parentNode.removeChild(link);
        window.URL.revokeObjectURL(url);
    }).catch(error => console.error("Error getting video:", error));
}

