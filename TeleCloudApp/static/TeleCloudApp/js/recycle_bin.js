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


$(document).on("click", ".folder-restore-icon", function(event) {
    console.log("flag");
    let folder_id = $(this).attr("id");
    let folder_restore_pk = folder_id.split("-")[3]

    let json_string = JSON.stringify({
        "folder_restore_pk": folder_restore_pk
    });

    json_string = encrypt_data(json_string);

    $.ajax({
        url: '/cloud/folder-restore/',
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
                $('#folder-' + folder_restore_pk).remove();
                
            } else {
                toast("Error", "Internal server error. Please report!", "red")
            }
        },
        error: function (error) {
            toast("Error", "Internal server error. Please report!", "red")
        }
    });
});



$(document).on("click", ".file-options-restore", function(event) {
    console.log("flag");
    let file_id = $(this).attr("id");
    let file_restore_pk = file_id.split("-")[3]

    $.ajax({
        url: '/cloud/file-restore/',
        type: 'POST',
        async: false,
        headers: {
            "X-CSRFToken": get_csrf_token()
        },
        data: {
            file_restore_pk: file_restore_pk,
        },
        success: function (response) {

            response = decrypt_data(response)
            response = JSON.parse(response);
            if (response['status'] == 200) {
                $('#file-' + file_restore_pk).remove();
                
            } else {
                toast("Error", "Internal server error. Please report!", "red")
            }
        },
        error: function (error) {
            toast("Error", "Internal server error. Please report!", "red")
        }
    });
});


$(document).on("click", "#empty-recycle-bin-icon", function(event) {
    event.preventDefault();
    console.log("Are you sure you want to delete this")
    $.ajax({
        url: '/cloud/empty-recycle-bin/',
        type: 'POST',
        async: false,
        headers: {
            "X-CSRFToken": get_csrf_token()
        },
        success: function (response) {

            // response = decrypt_data(response)
            //response = JSON.parse(response);
            // if (response['status'] == 200) {
                
                console.log("success",response)
                $('#all-folder').empty();
                $('#all-files').empty();                
            //}
        },
        error: function (error) {
            console.log("eero",error)
            // M.toast({
            //     'html': 'Unable to connect to server. Please try again later.'
            // }, 2000);
        }
    });
});
