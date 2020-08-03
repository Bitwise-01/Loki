'use strict';

const MIN_USERNAME_LENGTH = 4;
const MAX_USERNAME_LENGTH = 16;

const MIN_PASSWORD_LENGTH = 12;
const MAX_PASSWORD_LENGTH = 256;

let isProcessing = false;

function isValidUsername(username) {
    username = username.trim();
    let resp = { status: 0, msg: '' };

    if (username.length === 0) {
        return resp;
    }

    if (username.length < MIN_USERNAME_LENGTH) {
        resp['msg'] = 'Username must contain at least ' + MIN_USERNAME_LENGTH + ' characters';
        return resp;
    } else if (username.length > MAX_USERNAME_LENGTH) {
        resp['msg'] = 'Username must contain at most ' + MAX_USERNAME_LENGTH + ' characters';
        return resp;
    }

    if (username.match(/\W/i)) {
        resp['msg'] = 'Username must not contain a special or space character';
        return resp;
    }

    resp['status'] = 1;
    return resp;
}

function isValidPassword(password) {
    let _password = password;
    password = password.trim();

    let resp = { status: 0, msg: '' };

    if (password.length === 0) {
        return resp;
    }

    // Length

    if (password.length < MIN_PASSWORD_LENGTH) {
        resp['msg'] = 'Password must contain at least ' + MIN_PASSWORD_LENGTH + ' characters';
        return resp;
    } else if (password.length > MAX_PASSWORD_LENGTH) {
        resp['msg'] = 'Password must contain at most ' + MAX_PASSWORD_LENGTH + ' characters';
        return resp;
    }

    // Diversity
    if (password.match(/^\d+\d$/gm)) {
        resp['msg'] = 'Password must not only consist of numbers';
        return resp;
    }

    if (!password.match(/\d/gm)) {
        resp['msg'] = 'Password must contain a digit';
        return resp;
    }

    if (!password.match(/\w/)) {
        resp['msg'] = 'Password must contain a letter';
        return resp;
    }

    // Spaces
    if (_password.match(/^\s|\s$/gm)) {
        resp['msg'] = 'Password must not start or end with a space';
        return resp;
    }

    if (!password.match(/\s/gm)) {
        resp['msg'] = 'Password must contain a space';
        return resp;
    }

    if (password.match(/\s{2,}/gm)) {
        resp['msg'] = 'Password must not have consecutive space';
        return resp;
    }

    resp['status'] = 1;
    return resp;
}

function setInvalid(field, feedback) {
    field.removeClass('is-valid');
    feedback.removeClass('valid-feedback');

    field.addClass('is-invalid');
    feedback.addClass('invalid-feedback');
}

function setValid(field, feedback) {
    field.removeClass('is-invalid');
    feedback.removeClass('invalid-feedback');

    field.addClass('is-valid');
    feedback.addClass('valid-feedback');
}

function setClear(field, feedback) {
    field.removeClass('is-invalid');
    field.removeClass('is-valid');

    feedback.removeClass('invalid-feedback');
    feedback.removeClass('valid-feedback');

    feedback.text('');
}

$('#new-username').keyup(() => {
    let resp = isValidUsername($('#new-username').val());
    let feedback = $('#new-username-resp');
    let field = $('#new-username');

    if (resp['status'] === 0 && resp['msg'].length !== 0) {
        setInvalid(field, feedback);
        feedback.text(resp['msg']);
    } else if (resp['status'] === 0 && resp['msg'].length === 0) {
        setClear(field, feedback);
    }

    if (resp['status'] === 1) {
        setValid(field, feedback);
        feedback.text('');
    }
});

$('#new-password').keyup(() => {
    checkPassword();
    checkConfirmPassword();
});

$('#confirm-password').keyup(() => {
    checkConfirmPassword();
});

function checkPassword() {
    let resp = isValidPassword($('#new-password').val());
    let feedback = $('#new-password-resp');
    let field = $('#new-password');

    if (resp['status'] === 0 && resp['msg'].length !== 0) {
        setInvalid(field, feedback);
        feedback.text(resp['msg']);
    } else if (resp['status'] === 0 && resp['msg'].length === 0) {
        setClear(field, feedback);
    }

    if (resp['status'] === 1) {
        setValid(field, feedback);
        feedback.text('');
    }
}

function checkConfirmPassword() {
    let feedback = $('#confirm-password-resp');
    let field = $('#confirm-password');

    if ($('#new-password').val().length === 0 || field.val().length === 0) {
        setClear(field, feedback);
        return;
    }

    if ($('#new-password').val() !== field.val()) {
        setInvalid(field, feedback);
        feedback.text('Passwords do not match');
    } else {
        if ($('#new-password').val().length >= MIN_PASSWORD_LENGTH) {
            setValid(field, feedback);
            feedback.text('');
        }
    }
}

$('#btn-update-username-password').click(() => {
    let newUsername = $('#new-username');

    let currentPassword = $('#current-password');
    let newPassword = $('#new-password');
    let confirmPassword = $('#confirm-password');

    if (currentPassword.val().length === 0 && newUsername.val().length === 0) {
        return;
    }

    let newPasswordResp = isValidPassword(newPassword.val());
    let newUsernameResp = isValidUsername(newUsername.val());

    if (
        (newPasswordResp['status'] === 1 && newPassword.val() === $('#confirm-password').val()) ||
        newUsernameResp['status'] === 1
    ) {
        updateUsernamePassword();
    }
});

function updateUsernamePassword() {
    if (isProcessing) {
        return;
    } else {
        enableLoader();
        isProcessing = true;
    }

    $.ajax({
        type: 'POST',
        url: '/update-username-password',
        data: {
            newUsername: $('#new-username').val(),
            currentPassword: $('#current-password').val(),
            newPassword: $('#new-password').val(),
            confirmPassword: $('#confirm-password').val(),
        },
        beforeSend: (request) => {
            request.setRequestHeader('X-CSRFToken', $('#csrf_token').val());
        },
    })
        .done((resp) => {
            for (let i in resp) {
                if (resp[i]['status'] && resp[i]['msg']) {
                    setValid($('#' + i), $('#' + i + '-resp'));
                    $('#' + i + '-resp').text(resp[i]['msg']);
                }

                if (resp[i]['status'] === 0 && resp[i]['msg']) {
                    setInvalid($('#' + i), $('#' + i + '-resp'));
                    $('#' + i + '-resp').text(resp[i]['msg']);
                }
            }

            if (resp['new-username'].status === 1) {
                $('#new-username').attr('placeholder', $('#new-username').val());
                $('#new-username').val('');
            }

            if (resp['new-password'].status === 1) {
                $('#current-password').val('');
                $('#new-password').val('');
                $('#confirm-password').val('');

                setClear($('#current-password'), $('#current-password'));
            }

            disableLoader();
            setAccountStatus();
            isProcessing = false;
        })
        .fail(() => {
            disableLoader();
            isProcessing = false;
        });
}

function enableLoader() {
    $('#update-username-password-loader').removeClass('d-none');
    $('#update-username-password-loader').addClass('d-block');
    $('#btn-update-username-password').addClass('d-none');
}

function disableLoader() {
    $('#update-username-password-loader').addClass('d-none');
    $('#update-username-password-loader').removeClass('d-block');
    $('#btn-update-username-password').removeClass('d-none');
}

function setAccountStatus() {
    $.ajax({
        type: 'GET',
        url: '/get-account-status',
        beforeSend: (request) => {
            request.setRequestHeader('X-CSRFToken', $('#csrf_token').val());
        },
    }).done((resp) => {
        if (resp['msg']) {
            $('#notice').text(resp['msg']);
            $('#account-status-msg').removeClass('d-none');
        } else {
            $('#account-status-msg').addClass('d-none');
        }
    });
}
