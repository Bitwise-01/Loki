"use strict";

$(document).ready(function() {
	intelSystemSrc();	
});

function intelSystemSrc() {
    $.ajax({
        type: "POST",
        url: "/intel/system/src"
    }).done(function(data) {
        let display = document.getElementById("display");
        let html = data["resp"];
        if(html) {
            display.innerHTML = html;     
            intelSystemData(); 
        }
    });
}

function intelNetworkSrc() {
    $.ajax({
        type: "POST",
        url: "/intel/network/src"
    }).done(function(data) {
        let display = document.getElementById("display");
        let html = data["resp"];
        if(html) {
            display.innerHTML = html;     
            intelNetworkData(); 
        }
    });
}

function intelGeoSrc() {
    $.ajax({
        type: "POST",
        url: "/intel/geo/src"
    }).done(function(data) {
        let display = document.getElementById("display");
        let html = data["resp"];
        if(html) {
            display.innerHTML = html;     
            intelGeoData(); 
        }
    });
}

function intelSystemData() {
	 $.ajax({
        type: "POST",
        url: "/intel/system/data"
    }).done(function(data) {
        let displayArea = document.getElementById("display-area");
        console.log(data);
        let html = data["resp"];
        if(html) {
            displayArea.innerHTML = html;      
        }
    });
}

function intelNetworkData() {
	 $.ajax({
        type: "POST",
        url: "/intel/network/data"
    }).done(function(data) {
        let displayArea = document.getElementById("display-area");
        console.log(data);
        let html = data["resp"];
        if(html) {
            displayArea.innerHTML = html;      
        }
    });
}

function intelGeoData() {
	 $.ajax({
        type: "POST",
        url: "/intel/geo/data"
    }).done(function(data) {
        let displayArea = document.getElementById("display-area");
        console.log(data);
        let html = data["resp"];
        if(html) {
            displayArea.innerHTML = html;      
        }
    });
}

