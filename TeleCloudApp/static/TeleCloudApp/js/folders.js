global_parent_folder_pk = -1

function get_csrf_token() {
    const CSRF_TOKEN = $('input[name="csrfmiddlewaretoken"]').val();
    return CSRF_TOKEN;
}


function encrypt_data(plaintext) {
    const encryption = new window.Encryption();
    return encryption.encrypt(plaintext);
}

function decrypt_data(plaintext) {
    const encryption = new window.Encryption();
    return encryption.decrypt(plaintext);
}

$(document).on("click", ".folder-options", function(event) {
    event.stopPropagation();
    let folder_option_id = (this.id).split('-')[3];
    $("#folder-options-list-" + folder_option_id).toggle();
});

//Striping html code from string
function sanitize_html(html_string) {
    html_string = html_string.trim()
    return html_string.replace(/(<([^>]+)[><])/ig, ' ');
}

//Check is alphanumeric
function sanitize_input(text) {
    var regex = /^[ A-Za-z0-9_]*$/
    if (text != "" && regex.test(text)) {
        return true
    } else {
        return false
    }
}

//Check is numeric
function sanitize_input_numeric(text) {
    var regex = /^[0-9]*$/
    if (text != "" && regex.test(text)) {
        return true
    } else {
        return false
    }
}


$(document).on('click', function(event) {
    let close_menu = $(event.target);
    if ( !close_menu.hasClass('folder-options') && !close_menu.hasClass('folder-option-icon')) {
        $('.folder-options-list-wrapper').hide();
        $('.file-options-list-wrapper').hide();
    }
});

$(document).on("click", ".option-rename", function(event) {
    event.preventDefault();
    let folder_rename_id = (this.id).split('-')[3];
    let fldr = $("#folder-" + folder_rename_id);
    const folderName = fldr.find(".folder-name");

    const renameForm = $("<div>")
      .addClass("form-folder-rename-wrapper")
      .html(`
        <form action="" class="form-folder-rename">
          <input id="rename" type="text">
        </form>
      `);

    fldr.append(renameForm);

    const inputFieldRename = renameForm.find("#rename");
    inputFieldRename.css("backgroundColor", fldr.find(".folder").css("backgroundColor"));

    inputFieldRename.val(folderName.text().replace(/\s/g, ''));
    inputFieldRename.select();
    let new_folder_name = ""
    renameForm.find(".form-folder-rename").on('submit', (event) => {
        event.preventDefault();
        new_folder_name = inputFieldRename.val()
        if (new_folder_name !== "") {
            rename_folder(new_folder_name, folder_rename_id)
        }
        inputFieldRename.val("")
        renameForm.remove();
    });

    $(document).mouseup((e) => {
        if (!renameForm.is(e.target) && renameForm.has(e.target).length === 0) {
            new_folder_name = inputFieldRename.val()
            if (new_folder_name !== "") {
                rename_folder(new_folder_name, folder_rename_id)            
            }
            renameForm.remove();
        }
        inputFieldRename.val("")
        e.stopPropagation();
        
      });
});

function generate_newfolder_name(counter) {
    return "New Folder " + counter
}

$(document).on("click", ".icon-add-folder", function(event) {
    let counter = 1;
    let folder_name = generate_newfolder_name(counter)
    let folder_name_list = []
    $('.folder-title').each(function() {
        folder_name_list.push($(this).text().trim());
    });
    
    while(folder_name_list.includes(folder_name)) {
        counter++
        folder_name = generate_newfolder_name(counter)
    }
    
    let folder_path = $("#folder-path").text()

    let json_string = JSON.stringify({
        "folder_name": folder_name,
        "folder_path": folder_path,
        "parent_folder_pk": global_parent_folder_pk
    });

    json_string = encrypt_data(json_string);

    $.ajax({
        url: '/cloud/folder-add/',
        type: 'POST',
        async: false,
        headers: {
            "X-CSRFToken": get_csrf_token()
        },
        data: {
            json_string: json_string
        },
        success: function (response) {

            response = decrypt_data(response)
            response = JSON.parse(response);
            if (response['status'] == 200) {
                toast("Success", response["message"], "green")
                render_sub_folder_view(response["new_folder_data"])
            } else if (response['status'] == 300) {
                toast("Error", response["message"], "red")
            } else {
                toast("Error", response["message"], "red")
            }
        },
        error: function (error) {
            toast("Error", "Internal server error. Please report!", "red")
        }
    });
});


$(document).on("click", ".folder", function(event) {
    let folder_menu = $(event.target);
    if (!folder_menu.hasClass('folder-options') && !folder_menu.hasClass('folder-option-icon')) {
        let folder_id = $(this).attr("id");
        let folder_pk = folder_id.split("-")[2]
        let folder_name = $("#folder-name-" + folder_pk).text().trim()
        let folder_path = $("#folder-path").text()

        let json_string = JSON.stringify({
            "folder_pk": folder_pk
        });

        json_string = encrypt_data(json_string);

        $.ajax({
            url: '/cloud/folder-sub-view/',
            type: 'POST',
            async: false,
            headers: {
                "X-CSRFToken": get_csrf_token()
            },
            data: {
                json_string: json_string,
            },
            success: function (response) {
                response = decrypt_data(response)
                response = JSON.parse(response);
                if (response['status'] == 200) {
                    $('#all-folder').empty();
                    $('#all-files').empty();
                    $("#folder-path").text(folder_path + "/" + folder_name)
                    $("#folder-icon-back").show()
                    global_parent_folder_pk = folder_pk
                    render_sub_folder_view(response["folder_data"])
                    render_files(response["file_data"])
                } else {
                    toast("Error", response["message"], "red")
                }
            },
            error: function (error) {
                toast("Error", "Internal server error. Please report!", "red")
            }
        });
    }
});


function render_sub_folder_view(folder_data) {
    folder_data.forEach(folder => {
        if (folder.is_deleted) {
            return;
        }
        const folder_html = `<div class="folder-wrapper" id="folder-${folder.folder_pk}">
                <div class="folder bg-clr-accent-310" id="folder-main-${folder.folder_pk}">
                    <div class="folder-content">
                        <div class="folder-icon">
                            <img src="/static/TeleCloudApp/icons/icon-folder.svg" alt="">
                        </div>
                        <div class="folder-info">
                            <div id="folder-name-${folder.folder_pk}" class="folder-title">
                                ${folder.name}
                            </div>
                            <div class="folder-details">
                                <span id="folder-file-number-${folder.folder_pk}" class="details-files-number">${folder.file_count}</span> Files, <span id="folder-contain-number-${folder.folder_pk}" class="details-folder-number">${folder.numchild}</span> Folders
                            </div>
                        </div>
                    </div>
                    <div id="folder-options-icon-${folder.folder_pk}" class="folder-options">
                        <img src="/static/TeleCloudApp/icons/icon-option-dots.svg" alt="">
                    </div>
                </div>
                <div id="folder-options-list-${folder.folder_pk}" class="folder-options-list-wrapper">
                    <div class="folder-options-list">
                        <div id="folder-option-rename-${folder.folder_pk}" class="option option-rename">
                            Rename
                        </div>
                        <div id="folder-option-delete-${folder.folder_pk}" class="option option-delete">
                            Delete
                        </div>
                    </div>
                </div>
            </div>
        `;

        $(folder_html).appendTo("#all-folder");
    
    });

}

function rename_folder(new_folder_name, folder_pk) {

    new_folder_name = sanitize_html(new_folder_name);

    if (!sanitize_input(new_folder_name)){
        toast("Error", "Folder name cannot contain special character except _", "red")
        return
    }

    let folder_name_list = []
    $('.folder-title').each(function() {
        folder_name_list.push($(this).text().trim());
    });
    
    if (folder_name_list.includes(new_folder_name)) {
        console.log("chckdubname")
        toast("Error", "Dublicate folder name found!", "red")
        return
    }
    
    if (!sanitize_input_numeric(folder_pk)) {
        toast("Error", "Invalid folder pk!", "red")
    }
    new_folder_name = new_folder_name.trim()

    let json_string = JSON.stringify({
        "new_folder_name": new_folder_name,
        "folder_pk": folder_pk,
    });

    json_string = encrypt_data(json_string);

    $.ajax({
        url: '/cloud/folder-rename/',
        type: 'POST',
        async: false,
        headers: {
            "X-CSRFToken": get_csrf_token()
        },
        data: {
            json_string: json_string
        },
        success: function (response) {

            response = decrypt_data(response)
            response = JSON.parse(response);
            if (response['status'] == 200) {
                toast("Success", response["message"], "green")
                $("#folder-name-" + folder_pk).text(new_folder_name);
            } else if (response['status'] == 300) {
                toast("Error", response["message"], "red")
            } else {
                toast("Error", response["message"], "red")
            }
        },
        error: function (error) {
            toast("Error", "Internal server error. Please report!", "red")
        }
    });

}


$(document).on("click", ".option-delete", function(event) {
    event.preventDefault();
    let folder_delete_pk = (this.id).split('-')[3];

    let json_string = JSON.stringify({
        "folder_delete_pk": folder_delete_pk
    });

    json_string = encrypt_data(json_string);

    $.ajax({
        url: '/cloud/folder-temp-delete/',
        type: 'POST',
        async: false,
        headers: {
            "X-CSRFToken": get_csrf_token()
        },
        data: {
            json_string: json_string,
        },
        success: function (response) {

            response = decrypt_data(response)
            response = JSON.parse(response);
            if (response['status'] == 200) {
                toast("Success", response["message"], "green")
                $('#folder-' + folder_delete_pk).remove();
            } else {
                toast("Error", "Internal server error. Please report!", "red")
            }
        },
        error: function (error) {
            toast("Error", "Internal server error. Please report!", "red")
        }
    });

})

$(document).on("click", "#folder-icon-back", function(event) {  
    let folder_path = $("#folder-path").text()

    let json_string = JSON.stringify({
        "parent_folder_pk": global_parent_folder_pk
    });

    json_string = encrypt_data(json_string);

    $.ajax({
        url: '/cloud/folder-back-view/',
        type: 'POST',
        async: false,
        headers: {
            "X-CSRFToken": get_csrf_token()
        },
        data: {
            json_string: json_string,
        },
        success: function (response) {

            response = decrypt_data(response)
            response = JSON.parse(response);
            if (response['status'] == 200) {
                $('#all-folder').empty();
                $('#all-files').empty();
                let modified_path = folder_path.substring(0, folder_path.lastIndexOf("/"));
                $("#folder-path").text(modified_path)
                global_parent_folder_pk = response["parent_folder_pk"]
                if (global_parent_folder_pk == -1) {
                    $("#folder-icon-back").hide()
                }
                render_sub_folder_view(response["folder_data"])
                render_files(response["file_data"])
                
            } else {
                toast("Error", "Internal server error. Please report!", "red")
            }
        },
        error: function (error) {
            toast("Error", "Internal server error. Please report!", "red")
        }
    });

});
