'use strict';

const MAX_OUTPUT_HISTORY_SIZE = 32;
const MAX_HISTORY_SIZE = 256;
const MAX_CHARS = 8192;

class Terminal {
    static isSSH = false;
    static commandOutputHistory = [];
    static SSHOutputHistory = [];

    static commandConsoleHistory = [];
    static SSHConsoleHistory = [];

    static commandCurrentPosition = 0;
    static SSHCurrentPosition = 0;

    static commandCurrentInput = '';
    static SSHCurrenInput = '';

    static isProcessing = false;

    constructor() {
        enableInput();
        enableTabs();

        $('#console-output').text('');

        if (this.consoleHistory.length === 0) {
            $('#console-output').append(this.mainMenu);
        } else {
            this.populateOutput();
        }

        $('#console-input').val(this.currentInput);
        $('#console-input').focus();
    }

    static addtoSSHHistory(input, output) {
        if (Terminal.SSHOutputHistory.length >= MAX_OUTPUT_HISTORY_SIZE) {
            Terminal.SSHOutputHistory.shift();
        }

        Terminal.SSHOutputHistory.push({ input: input, output: output.slice(0, MAX_CHARS) });
    }

    static addtoCommandHistory(input, output) {
        if (Terminal.commandOutputHistory.length >= MAX_OUTPUT_HISTORY_SIZE) {
            Terminal.commandOutputHistory.shift();
        }

        Terminal.commandOutputHistory.push({ input: input, output: output.slice(0, MAX_CHARS) });
    }

    get outputHistory() {
        return Terminal.isSSH ? Terminal.SSHOutputHistory : Terminal.commandOutputHistory;
    }

    get consoleHistory() {
        return Terminal.isSSH ? Terminal.SSHConsoleHistory : Terminal.commandConsoleHistory;
    }

    get currentPosition() {
        return Terminal.isSSH ? Terminal.SSHCurrentPosition : Terminal.commandCurrentPosition;
    }

    set currentPosition(value) {
        if (Terminal.isSSH) {
            Terminal.SSHCurrentPosition = value;
        } else {
            Terminal.commandCurrentPosition = value;
        }
    }

    get isProcessing() {
        return Terminal.isProcessing;
    }

    set isProcessing(value) {
        Terminal.isProcessing = value;
    }

    get currentInput() {
        return Terminal.isSSH ? Terminal.SSHCurrenInput : Terminal.commandCurrentInput;
    }

    set currentInput(value) {
        if (Terminal.isSSH) {
            Terminal.SSHCurrenInput = value;
        } else {
            Terminal.commandCurrentInput = value;
        }
    }

    populateOutput() {
        this.outputHistory.forEach((h) => {
            $('#console-output').append(h['output']);
        });

        this.scroll();
    }

    addtoConsoleHistory(input) {
        if (Terminal.isSSH) {
            if (Terminal.SSHConsoleHistory.length >= MAX_HISTORY_SIZE) {
                Terminal.SSHConsoleHistory.shift();
            }

            Terminal.SSHConsoleHistory.push(input);
        } else {
            if (Terminal.commandConsoleHistory.length >= MAX_HISTORY_SIZE) {
                Terminal.commandConsoleHistory.shift();
            }

            Terminal.commandConsoleHistory.push(input);
        }
    }

    get mainMenu() {
        throw Exception.NotImplemented;
    }

    execute(_cmd) {
        throw Exception.NotImplemented;
    }

    startExe() {
        if (!this.isProcessing) {
            this.isProcessing = true;
            disableInput();
        }
    }

    stopExe(input, output) {
        if (this.isProcessing) {
            enableInput();
            this.isProcessing = false;
        }

        $('#console-input').val('');

        if (input) {
            this.consoleOutput(input, output);
        }
    }

    constructOuput(input, ouput) {
        let p = $('<p>', { class: 'console-output-section' });

        p.append($('<span>', { class: 'console-output-input-cmd' }).text(input));
        p.append($('<span>', { class: 'console-output-output' }).text(ouput));

        return p;
    }

    consoleOutput(input, output) {
        let _output = output;
        output = this.constructOuput(input, output);

        if (_output.trim().length) {
            let histOutput = this.constructOuput(input, _output.slice(0, MAX_CHARS));

            if (Terminal.isSSH) {
                Terminal.addtoSSHHistory(input, histOutput);
            } else {
                Terminal.addtoCommandHistory(input, histOutput);
            }
        }

        $('#console-output').append(output);
        this.scroll();
    }

    scroll() {
        $('.console-display').scrollTop($('.console-display').prop('scrollHeight'));
    }
}

function disableInput() {
    let consoleInput = $('#console-input');
    consoleInput.prop('disabled', true);
    $('.console-input-container').addClass('disabled-console-input');
}

function enableInput() {
    let consoleInput = $('#console-input');
    consoleInput.prop('disabled', false);
    $('.console-input-container').removeClass('disabled-console-input');
    $('#console-input').focus();
}

function disableTabs() {
    $('.console ul.nav li').each((_, e) => {
        $(e).addClass('disabled-tab');
    });
}

function enableTabs() {
    $('.console ul.nav li').each((_, e) => {
        $(e).removeClass('disabled-tab');
    });
}

function disabledTerminalObj() {
    terminalObj = null;
}

function disableConsole() {
    disableInput();
    disableTabs();
    disabledTerminalObj();
}
