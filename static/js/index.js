'use strict';

$('#form').submit(e => {
    e.preventDefault();

    let username = $('#username').val();
    let password = $('#password').val();

    if (username.length == 0 || password.length == 0) {
        return;
    }

    $.ajax({
        type: 'POST',
        url: '/login',
        data: { username: username, password: password },
        beforeSend: request => {
            request.setRequestHeader('X-CSRFToken', $('#csrf_token').val());
        }
    })
        .done(resp => {
            if (!resp['is_authenticated']) {
                $('#password').val('');
                displayErrorMsg(resp['msg']);
            } else {
                window.location.href = '/';
            }
        })
        .fail(() => {
            window.location.href = '/';
        });
});

function displayErrorMsg(msg) {
    let alert = $('<div class="alert alert-danger alert-dismissible fade show" role="alert"></div>');
    let btn = $(
        '<button type="button" class="close" data-dismiss="alert" aria-label="Close"></button>'
    ).append('<span aria-hidden="true">&times;</span>');

    alert.append('<strong>Error:</strong> ' + msg).append(btn);

    let alertContainer = $('#alert-container');

    alertContainer.empty();
    alertContainer.append(alert);
}
