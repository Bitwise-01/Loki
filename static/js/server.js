"use strict";

var dynamicTabsSet = false;
var sidebarItems = new Array();
var subtabsItems = new Array();

$(document).ready(function() {
	serverManagement();
	for(let n=0; n<2; n++) {
		serverServiceSource();		
	}
	setEventListenerOnTabs();		
});

function all(items) {
	for(let n=0; n<items.length; n++) {
		if(!items[n]) {
			return false;
		}
	}
	return true;
}

// -------- Tabs -------- //

document.addEventListener("click", function(){
	if(!dynamicTabsSet) {
		dynamicTabsSet = true;
		setEventListenerOnTabs();
	}
 });

function setEvents(items, tagType, array) {
	for(let t=0; t<items.length; t++) {
		let tags = items[t].getElementsByTagName(tagType);
		for(let n=0; n<tags.length; n++) {
			let tag = tags[n];
			tag.addEventListener("click", selectTab);
			array.push(tag);
		}		
	}
}

function setEventListenerOnTabs() {
	let tabs = document.getElementsByClassName("tabs");
	let subtabs = document.getElementsByClassName("sub-tabs");

	setEvents(subtabs, "li", subtabsItems);
	setEvents(tabs, "div", sidebarItems);
}

function isIn(obj, array) {
	let _isIn = false;

	for(let n=0; n<array.length; n++) {
		if(array[n] == obj) {
			_isIn = true;
			break;
		}
	}
	return _isIn;
}

function unSelect(items) {
	for(let n=0; n<items.length; n++) {
		let item = items[n];

		if(item.classList.contains("selected")) {
			item.classList.remove("selected");
		}
	}
}

function removeSelected(obj) {
	if(isIn(obj, sidebarItems)) {
		unSelect(subtabsItems);
		unSelect(sidebarItems);
	} else {
		unSelect(subtabsItems);
	}
}

function selectTab() {
	removeSelected(this);	
	this.classList.add("selected");
}

// -------- Server -------- //

function validateIp(ip) {
	let ipInput = document.getElementById("ip");

	if(!/^(?!0)(?!.*\.$)((1?\d?\d|25[0-5]|2[0-4]\d)(\.|$)){4}$/.test(ip)) {
		if(!ipInput.classList.contains("invalid")) {
			ipInput.classList.add("invalid");
		}
		return false;
	} else {
		if(ipInput.classList.contains("invalid")) {
			ipInput.classList.remove("invalid");
		}
		return true;
	}
}

function testPort(port) {
	let _port = port.toString().trim();	
	
	if(!_port.length) {
		return false;
	} else {

		// check if number
		for(let n=0; n<_port.length; n++) {
			if(isNaN(_port[n])) {
				return false;
			}
		}

		// check if number starts with a zero
		if(parseInt(_port[0]) == 0) {
			return false;
		}

		// check if number is larger than 65535
		if(parseInt(_port) > 65535) {
			return false;
		}

		return true;
	}
}

function validatePort(port) {
	let portInput = document.getElementById("port");

	if(!testPort(port)) {
		if(!portInput.classList.contains("invalid")) {
			portInput.classList.add("invalid");
		}
		return false;
	} else {
		if(portInput.classList.contains("invalid")) {
			portInput.classList.remove("invalid");
		}
		return true;
	}
}

function invalidate(id) {
	let element = document.getElementById(id);

	if(!element.classList.contains("invalid")) {
		element.classList.add("invalid");
	}
}

function serverService() {
	let ip = document.getElementById("ip");
	let port = document.getElementById("port");
	let btn = document.getElementById("server-address-btn");
	let load = document.getElementById("server-service-load");

	if(all([validateIp(ip.value), validatePort(port.value)])) {
		btn.style.display = "none";
		load.style.display = "block";
		$.ajax({
			type: "POST",
			data: {"ip": ip.value, "port": port.value},
			url: "/server_service"
			}).done(function(data) {
				if("mode" in data) {
					if(data["mode"] == "Start Server") {
						if(!data["failed"]) {
							ip.value = "";
							port.value = "";							
						} else {
							invalidate("ip");
							invalidate("port");
						}
					}

					if(data["failed"]) {
						invalidate("ip");
						invalidate("port");
					}

					btn.innerHTML = data["mode"];
				}
				btn.style.display = "block";
				load.style.display = "none";
		});
	}
}

function serverManagement() {
	$.ajax({
		type: "POST",
		url: "/server_management"
	}).done(function(data) {
		let display = document.getElementById("display");
		let html = data["resp"];
		if(html) {
			display.innerHTML = html;		
			setEventListenerOnTabs();
		}
	});
}

function serverServiceSource() {
	$.ajax({
		type: "POST",
		url: "/server_service_source"
	}).done(function(data) {
		let displayArea = document.getElementById("display-area");
		let html = data["resp"];

		if(html) {
			displayArea.innerHTML = html;
			let ip = document.getElementById("ip");
			let port = document.getElementById("port");
			let btn = document.getElementById("server-address-btn");

			if(all([data["ip"], data["port"]])) {
				ip.value = data["ip"];
				port.value = data["port"];
				btn.innerHTML = data["mode"];
			}		
		}
	});	
}