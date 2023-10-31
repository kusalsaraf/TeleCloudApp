function uploadFiles() {
    var files = $('#file-input')[0].files;
    var folder_path = $("#folder-path").text();
    var currentIndex = 0;
    var uploadLimit = 4;
    var delay = 60000 / (20 / uploadLimit); // Delay per batch in milliseconds

    function uploadBatch() {
        var formData = new FormData();
        var endIndex = Math.min(currentIndex + uploadLimit, files.length);
        
        for (var i = currentIndex; i < endIndex; i++) {
            formData.append('files', files[i]);
        }
        
        formData.append('folder_path', folder_path);
        
        $.ajax({
            url: '/cloud/file/upload/',
            type: 'POST',
            headers: {
                "X-CSRFToken": get_csrf_token()
            },
            data: formData,
            contentType: false,
            processData: false,
            xhr: function() {
                var xhr = new window.XMLHttpRequest();
                
                xhr.upload.addEventListener('progress', function(evt) {
                    if (evt.lengthComputable) {
                        var percentComplete = (evt.loaded / evt.total) * 100;
                        console.log(percentComplete);
                    }
                }, false);
                
                return xhr;
            },
            success: function(response) {
                // Handle the success response
                response = JSON.parse(response);
                console.log(response)
                if (response["status"] == 200) {
                    render_files(response["files_data"]);
                    
                    currentIndex += uploadLimit; 

                    if (currentIndex < files.length) {
                        setTimeout(uploadBatch, delay);
                    }
                } else {
                    toast("Error", response["message"], "red")
                }
            },
            error: function(xhr, status, error) {
                // Handle the error
                console.log(error);
                
                currentIndex += uploadLimit; 
                
                if (currentIndex < files.length) {
                    setTimeout(uploadBatch, delay);
                }
            }
        });
    }

    uploadBatch();
}

function convert_bytes_to_megabytes(bytes) {
    let megabytes = bytes / (1024 * 1024);
    return megabytes.toFixed(2);
}


function render_files(files_data){
    files_data.forEach(file => {
        if (file.is_deleted) {
            return;
        }
        if (file.is_favorite) {
            favorite_src = "/static/TeleCloudApp/icons/icon-star.svg"
        } else {
            favorite_src = "/static/TeleCloudApp/icons/icon-star-empty.svg"
        }
        let image_src = ""
        let media_html = ""
        let video_src = ""
        if (file.type == "image") {
            image_src = file.file_url
            media_html = `  <div class="file-square-img-wrapper" id="file-img-div-${file.file_pk}">	
                                <img class="file-square-img" id="file-url-${file.file_pk}" src="${image_src}" alt="">	
                            </div>
                            <div class="file-square-icons">
                                <img class="file-square-icon-type" src="/static/TeleCloudApp/icons/icon-image.svg" alt="">
                                <div>
                                    <img id="file-options-icon-${file.file_pk}" class="file-options-icon" src="/static/TeleCloudApp/icons/icon-option-dots.svg" alt="">
                                    <img id="file-favorite-icon-${file.file_pk}" class="file-favorite-icon" src=${favorite_src} alt="">
                                </div>
                            </div>`
            }
        else if (file.type == "video") {
            video_src = file.file_url
            media_html = `<video width="320" height="240" controls>
                                <source id="file-url-${file.file_pk}" src="${video_src}" type="video/mp4">
                                </video>`
        }
        else {
            document_src = file.file_url
            media_html = `  <div class="file-square-icons">
                                <img class="file-square-icon-type" src="/static/TeleCloudApp/icons/icon-image.svg" alt="">
                                <div>
                                    <img class="file-options-icon" src="/static/TeleCloudApp/icons/icon-option-dots.svg" alt="">
                                    <img src="/static/TeleCloudApp/icons/icon-star.svg" alt="">
                                </div>
                            </div>`
        }

        const file_html = `
            <div class="file-square-wrapper" id="file-${file.file_pk}">
                <div class="file-square">
                    ${media_html}
                    <div class="file-square-details">
                        <div class="file-square-name" id="file-name-${file.file_pk}">
                            ${file.name}
                        </div>
                        <div class="file-square-size" id="file-sie-${file.file_pk}">
                            ${convert_bytes_to_megabytes(file.size)} Mb
                        </div>
                    </div>
                </div>
                <div id="file-options-list-${file.file_pk}" class="file-options-list-wrapper">
                    <div class="file-options-list">
                    <div id="file-option-rename-${file.file_pk}" class="option option-file-rename">
                        Rename
                    </div>
                    <div id="file-option-delete-${file.file_pk}" class="option option-file-delete">
                        Delete
                    </div>
                    </div>
                </div>
            </div>
        `
        $(file_html).appendTo("#all-files");
    });
}

$('#upload-form').on('change', function() {
    uploadFiles();
});

$(document).on("click", ".file-options-icon", function(event) {
    event.stopPropagation();
    console.log("file option clicked")
    let file_option_id = (this.id).split('-')[3];
    $("#file-options-list-" + file_option_id).toggle();
});


$(document).on("click", ".option-file-rename", function(event) {
    event.preventDefault();
    console.log("rename option clicked file")
    let file_rename_id = (this.id).split('-')[3];
    let file_root_div = $("#file-" + file_rename_id);
    const file_name = file_root_div.find(".file-name");
    const rename_html = $("<div>")
        .addClass("form-file-rename-wrapper")
        .html(`
            <form action="" class="form-file-rename">
                <input class="rename" id="rename" type="text">
            </form>
        `);
    
    file_root_div.append(rename_html);
    
    const file_name_div = file_root_div.find('.file-square-name');
    file_name_div.toggleClass('color-transparent');
    
    const file_input_rename = rename_html.find("#rename");
    file_input_rename.val(file_name.text().replace(/\s/g, ''));
    file_input_rename.select();
    let rename_value = ""
    rename_html.find(".form-file-rename").on('submit', (event) => {
        event.preventDefault();
        rename_value = file_input_rename.val()
        if (rename_value !== "" && rename_value != file_name_div.text().trim()){
            console.log("renamfile1");
            rename_file(rename_value, file_rename_id)
        }
        
        $("#file-name-" + file_rename_id).removeClass('color-transparent');
        rename_html.remove();
    });

    
    $(document).mouseup((e) => {
        if (!rename_html.is(e.target) && rename_html.has(e.target).length === 0 && !$(e.target).hasClass("option option-file-rename") && !$(e.target).hasClass("rename")) {
            let new_file_name = file_input_rename.val().trim();
            if (new_file_name !== "" && new_file_name != file_name_div.text().trim()) {
                console.log("renamfile2");
                rename_file(new_file_name, file_rename_id)
                
            }
            console.log("targetttt",e.target)

            $("#file-name-" + file_rename_id).removeClass('color-transparent');
            console.log("remove2")
            rename_html.remove();
        }
    });
});


function rename_file(new_file_name, file_pk) {

    new_file_name = new_file_name.trim()

    $.ajax({
        url: '/cloud/file-rename/',
        type: 'POST',
        async: false,
        headers: {
            "X-CSRFToken": get_csrf_token()
        },
        data: {
            new_file_name: new_file_name,
            file_pk: file_pk,
        },
        success: function (response) {

            // response = decrypt_data(response)
            //response = JSON.parse(response);
            // if (response['status'] == 200) {
                
                response = JSON.parse(response)
                console.log("response",response)
                $("#file-name-" + file_pk).text(new_file_name);
            //}
        },
        error: function (error) {
            console.log("eero",error)
            // M.toast({
            //     'html': 'Unable to connect to server. Please try again later.'
            // }, 2000);
        }
    });

}


$(document).on("click", ".option-file-delete", function(event) {
    event.preventDefault();
    let file_delete_pk = (this.id).split('-')[3];

    $.ajax({
        url: '/cloud/file-temp-delete/',
        type: 'POST',
        async: false,
        headers: {
            "X-CSRFToken": get_csrf_token()
        },
        data: {
            file_delete_pk: file_delete_pk,
        },
        success: function (response) {

            // response = decrypt_data(response)
            //response = JSON.parse(response);
            // if (response['status'] == 200) {
                
                response = JSON.parse(response)
                console.log("response",response)
                $('#file-' + file_delete_pk).remove();
            //}
        },
        error: function (error) {
            console.log("eero",error)
            // M.toast({
            //     'html': 'Unable to connect to server. Please try again later.'
            // }, 2000);
        }
    });

})

function get_csrf_token() {
    const CSRF_TOKEN = $('input[name="csrfmiddlewaretoken"]').val();
    return CSRF_TOKEN;
}

$(document).on("click", ".file-favorite-icon", function(event) {
    event.preventDefault();
    let file_favorite_pk = (this.id).split('-')[3];

    $.ajax({
        url: '/cloud/favorite-toggle/',
        type: 'POST',
        async: false,
        headers: {
            "X-CSRFToken": get_csrf_token()
        },
        data: {
            file_favorite_pk: file_favorite_pk,
        },
        success: function (response) {

            // response = decrypt_data(response)
            //response = JSON.parse(response);
            // if (response['status'] == 200) {
                
                response = JSON.parse(response)
                console.log("response",response)
                if (response['is_favorite']) {
                    $("#file-favorite-icon-" + file_favorite_pk).attr("src", "/static/TeleCloudApp/icons/icon-star.svg");
                } else {
                    $("#file-favorite-icon-" + file_favorite_pk).attr("src", "/static/TeleCloudApp/icons/icon-star-empty.svg");
                }
                let current_window_url = window.location.href;
                let favorite_url_pattern = "favorites/";

                if (current_window_url.indexOf(favorite_url_pattern) !== -1) {
                    $('#file-' + file_favorite_pk).remove();
                
                } 
                
            //}
        },
        error: function (error) {
            console.log("eero",error)
            // M.toast({
            //     'html': 'Unable to connect to server. Please try again later.'
            // }, 2000);
        }
    });

})