axios.defaults.baseURL = '/api';

var input_file = document.getElementById("input_file");
var input_file_view = document.getElementById('input_file_view');

function upload_file() {
    input_file_view.src = null;
    input_file.click();
}

function input_file_onchange() {
    var file_to_upload = input_file.files[0];
    input_file_view.src = URL.createObjectURL(file_to_upload);

    var formData = new FormData();
    formData.append("file", input_file.files[0]);
    axios.post('/predict', formData, {
        headers: {
            'Content-Type': 'multipart/form-data'
        }
    }).then(function (response) {
        alert("Your video is being processed. You will be notified when it's ready.");
        checkStatus();
    }).catch(function (error) {
        console.error("Error during file upload:", error);
        alert("There was an error uploading your video.");
    });
}

input_file.onchange = input_file_onchange;

function checkStatus() {
    axios.get('/status').then(response => {
        const status = response.data.status;
        let progress = 0;
        const labels = document.getElementsByClassName('label');

        // Reset all labels to default style
        for (let i = 0; i < labels.length; i++) {
            labels[i].classList.remove('visible-label');
        }

        // Update progress and highlight the current label
        switch(status) {
            case 'processing':
                progress = 0;
                labels[0].classList.add('visible-label');
                break;
            case 'preprocessing_done':
                progress = 30;
                labels[1].classList.add('visible-label');
                break;
            case 'feature_extraction_done':
                progress = 65;
                labels[2].classList.add('visible-label');
                break;
            case 'completed':
                progress = 100;
                labels[3].classList.add('visible-label');
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
}

function downloadVideo() {
    axios.get('/get_video', { responseType: 'blob' }).then(response => {
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', 'test.mp4');
        document.body.appendChild(link);
        link.click();

        link.parentNode.removeChild(link);
        window.URL.revokeObjectURL(url);
    }).catch(error => console.error("Error getting video:", error));
}
