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

    // Post the image to the /predict API
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
        // Optionally, save the video ID or other reference in local storage or display it to the user
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

function downloadVideo() {
    // the URL to the video file
    var videoUrl = 'persistent-folder/test.mp4';

    // create a temporary anchor tag to trigger the download
    var a = document.createElement('a');
    a.href = videoUrl;
    a.download = 'processed_video.mp4';  // the name we want to save the file as
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
}

