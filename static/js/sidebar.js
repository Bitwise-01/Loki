"use strict";

var _isClicked = 0;
var sidebar = null;
var menuLines = null;
var isClicked = false;

$(document).ready(function(){
	sidebar = document.getElementById("sidebar");
	menuLines = document.getElementById("menu-lines");
	addListeners();
});

function addListeners() {
	menuLines.addEventListener("click", toggleSideBar);
	document.addEventListener("click", function(e) {
		if(_isClicked == 1) {	
			sidebar.style.display = "none";
			isClicked = false;
			_isClicked = 0;
		} else {
			if(isClicked) {
				_isClicked += 1;
			}
		}
	});		
}

function toggleSideBar() {
	if(!isClicked) {
		sidebar.style.display = "block";
	} else {
		sidebar.style.display = "none";
	}
	isClicked = !isClicked;
}