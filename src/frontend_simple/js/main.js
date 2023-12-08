axios.defaults.baseURL = '/api';

var input_file = document.getElementById("input_file");
var input_file_view = document.getElementById('input_file_view');
var videoId = "";  // Store the video ID

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
        alert("Your video is being processed. You will be notified when it's ready.");
        videoId = response.data.video_id;  // Save the video ID
        checkStatus();
    }).catch(function (error) {
        console.error("Error during file upload:", error);
        alert("There was an error uploading your video.");
    });
}

input_file.onchange = input_file_onchange;

function checkStatus() {
    if (!videoId) return;  // Check if videoId is set

    axios.get('/status/' + videoId).then(response => {
        const status = response.data.status;
        let progress = 0;

        switch(status) {
            case 'preprocessing':
                progress = 25;
                break;
            case 'feature extracting':
                progress = 50;
                break;
            case 'inferencing':
                progress = 75;
                break;
            case 'completed':
                progress = 100;
                showDownloadButton();
                break;
            default:
                progress = 0;
        }

        var progressBar = document.getElementById('progressBar');
        progressBar.style.width = progress + '%';

        if (status !== 'completed') {
            setTimeout(checkStatus, 5000); // Poll every 5 seconds
        }
    }).catch(error => console.error("Error checking status:", error));
}

function showDownloadButton() {
    var downloadButton = document.getElementById('downloadButton');
    downloadButton.style.display = 'block';
    downloadButton.onclick = function() { downloadVideo(videoId); };  // Update download function
}

function downloadVideo(videoId) {
    axios.get('/get_video/' + videoId, { responseType: 'blob' }).then(response => {
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', `${videoId}.mp4`);
        document.body.appendChild(link);
        link.click();

        link.parentNode.removeChild(link);
        window.URL.revokeObjectURL(url);
    }).catch(error => console.error("Error getting video:", error));
}
