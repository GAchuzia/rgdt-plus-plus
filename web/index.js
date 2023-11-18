function upload_file(){
    var myUploadedFile = document.getElementById("uploadFile").files[0];
    const res = await axios.post('/upload', formData, {
        headers: {
            'Content-Type': 'file'
        }
    });
}
