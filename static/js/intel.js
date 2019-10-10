'use strict';

$(document).ready(function() {
    intelSystemSrc();
});

function intelSystemSrc() {
    $.ajax({
        type: 'GET',
        url: '/intel/system/src'
    }).done(function(data) {
        let display = document.getElementById('display');
        let html = data['resp'];
        if (html) {
            display.innerHTML = html;
            intelSystemData();
        }
    });
}

function intelNetworkSrc() {
    $.ajax({
        type: 'GET',
        url: '/intel/network/src'
    }).done(function(data) {
        let display = document.getElementById('display');
        let html = data['resp'];
        if (html) {
            display.innerHTML = html;
            intelNetworkData();
        }
    });
}

function intelGeoSrc() {
    $.ajax({
        type: 'GET',
        url: '/intel/geo/src'
    }).done(function(data) {
        let display = document.getElementById('display');
        let html = data['resp'];
        if (html) {
            display.innerHTML = html;
            intelGeoData();
        }
    });
}

function intelSystemData() {
    $.ajax({
        type: 'GET',
        url: '/intel/system/data'
    }).done(function(data) {
        let displayArea = document.getElementById('display-area');
        console.log(data);
        let html = data['resp'];
        if (html) {
            displayArea.innerHTML = html;
        }
    });
}

function intelNetworkData() {
    $.ajax({
        type: 'GET',
        url: '/intel/network/data'
    }).done(function(data) {
        let displayArea = document.getElementById('display-area');
        console.log(data);
        let html = data['resp'];
        if (html) {
            displayArea.innerHTML = html;
        }
    });
}

function intelGeoData() {
    $.ajax({
        type: 'GET',
        url: '/intel/geo/data'
    }).done(function(data) {
        let displayArea = document.getElementById('display-area');
        console.log(data);
        let html = data['resp'];
        if (html) {
            displayArea.innerHTML = html;
        }
    });
}
