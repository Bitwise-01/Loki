"use strict";

$(document).ready(function() {
    onlineBotsSource();
    for(let n=0; n<3; n++) {
        fetchBots();
    }
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
            display.innerHTML = html;      
        }
    });
}

function fetchBots() {
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


