const nav = document.querySelector(".nav");
const mainContainer = document.querySelector(".main-container");
mainContainer.style.marginLeft = getComputedStyle(nav).width;

$(document).ready(function() {
    $('#captcha_image_refresh_button').click(function() {
        refreshCaptchaImage()
    });
});

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

function refreshCaptchaImage() {
    captcha_image = document.getElementById("captcha_image").src;
    encrypted_captcha_image = encrypt_data(captcha_image)
    $.ajax({
        url: '/cloud/random-captch/',
        type: 'POST',
        async: false,
        headers: {
            "X-CSRFToken": get_csrf_token()
        },
        data: {
            captcha_image: encrypted_captcha_image,
        },
        success: function (response) {

            response = decrypt_data(response)
            response = JSON.parse(response);
            if (response['status'] == 200) {
                host_name = window.location.host;
                host_name = host_name.toString();
                new_captcha_image = response["captcha_image"];
                old_captch_image = document.getElementById("captcha_image");
                old_captch_image.src = new_captcha_image;
            } else {
                M.toast({
                    'html': 'Unable to connect to server. Please try again later.'
                }, 2000);
            }
        },
        error: function (error) {
            console.log("eero",error)
            // M.toast({
            //     'html': 'Unable to connect to server. Please try again later.'
            // }, 2000);
        }
    });
}

function is_valid_email(email) {
    email = String(email).trim() 
    if (email == "" || email.length > 50) {
        return false
    }
    const regex = /^\w+([.-]?\w+)*@\w+([.-]?\w+)*(\.\w{2,3})+$/;
    return regex.test(email);
}


function send_password_reset_mail(event, is_new_user) {
    event.preventDefault();
    let email = $("#password_reset_email").val()
    if (!is_valid_email(email)) {
        console.log("Please enter valid email")
        return
    }

    send_password_reset_mail_api(email, is_new_user) 

}

function send_password_reset_mail_api(email, is_new_user) {
    $.ajax({
        url: '/cloud/reset-password/',
        type: 'POST',
        headers: {
            "X-CSRFToken": get_csrf_token()
        },
        data: {
            'email': email,
            "is_new_user": is_new_user
        },
        success: function() {
            setTimeout(function () {
                window.location = "/cloud/reset_password_sent/";
            }, 100);
           
        },
        error: function(xhr, textStatus, errorThrown) {
            console.log('Error:', errorThrown);
        }
    });
}

function valid_name(name) {
    const regex = /^[a-zA-Z]+$/;
    name = name.trim()
    if (regex.test(name) && name.length < 20){
        return true
    } else {
        return false
    }
}


function sign_up(event) {
    event.preventDefault()
    first_name = document.getElementById("first_name").value;
    last_name = document.getElementById("last_name").value;
    email_id = document.getElementById("email_id").value;
    

    if (!valid_name(first_name)) {
        console.log("invalid firsrname")
        return;
    }
    if (!valid_name(first_name)) {
        console.log("invalid lastrname")
        return;
    }
    if (!is_valid_email(email_id)) {
        console.log("invalid email")
        return;
    }

    var json_string = JSON.stringify({
        'first_name': first_name,
        'last_name': last_name,
        'email_id': email_id,
    })
    encrypted_json_string = encrypt_data(json_string)
    csrf_token = get_csrf_token();
    var response = $.ajax({
        url: '/cloud/signup/',
        type: "POST",
        headers: {
            'X-CSRFToken': csrf_token,
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        async: false,
        data: {
            json_string: encrypted_json_string,
        },
        success: function (response) {
            response = decrypt_data(response)
            response = JSON.parse(response);
            if (response["status"] == 200) {
                console.log(" user created")
                send_password_reset_mail_api(email_id, true)

            } else if (response["status"] == 300) {
                console.log(response["message"])
            }

        },
        error: function (error) {
            console.log(error)
            M.toast({
                'html': 'Unable to connect to server. Please try again later.'
            }, 2000);
        }
    }).responseJSON;

    return response;
}

function login_function(event) {
    event.preventDefault()
    let email = document.getElementById("login_email").value;
    let password = document.getElementById("password_login").value;
    let captcha_image_input = document.getElementById("captcha_image_input").value;

    if (!is_valid_email(email)) {
        alert("Please enter valid email");
        return;
    }

    if (password.value == "") {
        alert("Please enter valid password");
        return;
    }
    
    if (captcha_image_input == "") {
        alert("Please enter valid captcha");
        return;
    }

    captcha_image = document.getElementById("captcha_image").src;

    request_params = {
        email: email,
        password: password,
        captcha_image: captcha_image,
        captcha_image_input: captcha_image_input
    }

    json_string = JSON.stringify(request_params);
    encrypted_data = encrypt_data(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };

    login_btn = document.getElementById('login_btn');
    // login_btn.disabled = true;

    csrf_token = get_csrf_token();
    var response = $.ajax({
        url: '/cloud/userauth/',
        type: "POST",
        headers: {
            'X-CSRFToken': csrf_token,
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        async: false,
        data: encrypted_data,
        success: function (response) {
            response = decrypt_data(response)
            response = JSON.parse(response);
            if (response["status"] == 200) {
                setTimeout(function () {
                    window.location = "/cloud/folder-root-view/";
                }, 500);

                console.log("login success")
            } else if (response["status"] == 300) {
                // login_btn.disabled = false;
                console.log("mes",response["message"])
            } 
        },
        error: function (error) {

            console.log(err)
        }
    }).responseJSON;

    return response;
}