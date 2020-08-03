'use strict';

const UP_CODE = 38;
const DOWN_CODE = 40;
const ENTER_CODE = 13;

$(document).ready(function () {
    setServerStatusInactive();
});

$('.console-display').mouseup(() => {
    if (getSelectedText().length === 0) {
        $('#console-input').focus();
    }
});

function getSelectedText() {
    if (window.getSelection) {
        return window.getSelection().toString();
    } else if (document.selection) {
        return document.selection.createRange().text;
    }
    return '';
}

$('#console-input').keydown((e) => {
    if (terminalObj === null || terminalObj.processingCommand) {
        return;
    }

    let consoleHistory = terminalObj.consoleHistory;

    let keyCode = e.keyCode;
    let consoleInput = $('#console-input');

    if (keyCode === UP_CODE || keyCode === DOWN_CODE || keyCode == ENTER_CODE) {
        e.preventDefault();
    }

    if (e.keyCode === UP_CODE) {
        // Up

        if (terminalObj.currentPosition > 0) {
            terminalObj.currentPosition -= 1;
            consoleInput.val(consoleHistory[terminalObj.currentPosition]);
        }
    } else if (e.keyCode === DOWN_CODE) {
        // Down

        if (terminalObj.currentPosition < consoleHistory.length) {
            terminalObj.currentPosition += 1;
            consoleInput.val(consoleHistory[terminalObj.currentPosition]);
        }
    } else if (e.keyCode === ENTER_CODE) {
        let currentValue = consoleInput.val();

        if (currentValue.trim().length == 0) {
            return;
        }

        updateHistory(currentValue);
        execute(currentValue);
    }
});

$('#console-input').keyup(() => {
    terminalObj.currentInput = $('#console-input').val();
});

function execute(cmd) {
    if (cmd.toLowerCase() === 'cls') {
        $('#console-output').text('');
        $('#console-input').val('');
        terminalObj.scroll();
        return;
    }

    terminalObj.execute(cmd);
    terminalObj.currentInput = '';
}

function updateHistory(currentValue) {
    let historySize = terminalObj.consoleHistory.length;

    if (historySize >= MAX_HISTORY_SIZE) {
        historySize = historySize - 1;
    }

    if (historySize === 0) {
        terminalObj.addtoConsoleHistory(currentValue);
        historySize += 1;
    } else if (historySize !== 0) {
        if (terminalObj.consoleHistory[terminalObj.consoleHistory.length - 1] !== currentValue) {
            terminalObj.addtoConsoleHistory(currentValue);
            historySize += 1;
        }
    }

    terminalObj.currentPosition = historySize;
}
