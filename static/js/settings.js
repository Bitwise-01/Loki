"use strict";

var dynamicTabsSet = false;
var sidebarItems = new Array();
var subtabsItems = new Array();

$(document).ready(function(){
	accountManagement();
	for(let n=0; n<5; n++) {
		usernameUpdateSource();
	}
	setEventListenerOnTabs();
});

function checkUsername() {
	let input = document.getElementById("new_username");
	let output = document.getElementById("username_status");
	displayMsg("", document.getElementById("form-status"), "");

	if(!input.value) {
		if(!input.classList.contains("invalid")) {
			input.classList.add("invalid");
		} else {

		}
		output.innerHTML = "";
	} else {
		$.ajax({
			data: { "username": input.value },
			type: "POST",
			url: "/check_username"
		}).done(function(data) {
			let db_resp = data["resp"];
			let submit = document.getElementById("submit");
			
			if (db_resp != "valid") {
				output.innerHTML = db_resp;
				submit.style.display = "none";

				if(!input.classList.contains("invalid")) {
					input.classList.add("invalid");
				}
			} else {
				if(input.classList.contains("invalid")) {
					input.classList.remove("invalid");
				}
				output.innerHTML = "";
				submit.style.display = "block";
			}			
		});
	}
}

function checkPassword() {
	let input = document.getElementById("new_password");
	let output = document.getElementById("password_status");
	
	if(!input.value) {
		if(!input.classList.contains("invalid")) {
			input.classList.add("invalid");
		} else {

		}
		output.innerHTML = "";
	} else {
		$.ajax({
			data: { "password": input.value },
			type: "POST",
			url: "/check_password"
		}).done(function(data) {
			let db_resp = data["resp"];
			let confirm = document.getElementById("confirm");

			displayMsg(input, output, db_resp);

			if(db_resp == "valid") {
				confirm.removeAttribute("disabled");
			} else {
				confirm.setAttribute("disabled", "disabled");
			}
		});
	}
}

function displayMsg(input, output, msg) {	
	if(msg != "valid") {
		if(input) { 
			if(!input.classList.contains("invalid")) {
				input.classList.add("invalid");
			}
		}
		output.innerHTML = msg;
	} else {
		if(input) {

			if(input.classList.contains("invalid")) {
				input.classList.remove("invalid");
			}
		}
		output.innerHTML = "";
	}	
}

function showHide(e) {
	let show = (e.innerHTML.toLowerCase() == "show") ? false : true;
	let inputs = document.getElementById("display-area").getElementsByTagName("input");

	for(let n=0; n<inputs.length; n++) {
		inputs[n].type = (show) ? "password" : "text";
	}
	
	e.innerHTML = (show) ? "Show" : "Hide";
}

function checkCurrentPassword(id) {
	let input = document.getElementById(id);
	let output = document.getElementById("current_password_status");

    if(!input.value) {
		displayMsg(input, output, "");
    } else {
    	let password = input.value;

    	$.ajax({
			data: { "password": password },
			type: "POST",
			url: "/current_password_check"
		}).done(function(data) {
			let db_resp = data["resp"];
			displayMsg(input, output, db_resp);
		});
    }
}

function confirmPassword(e) {
	let confirm = e.value;
	let submit = document.getElementById("submit");
	let password = document.getElementById("new_password");
	let output = document.getElementById("password_status");

	if(!password.value) {
		displayMsg(password, output, "");
		displayMsg(e, output, "");	
	} else {
		if(confirm != password.value) {
			displayMsg(e, output, "");
			submit.style.display = "none";
			statusReport();
			return "";
		} else {
			displayMsg(e, output, "valid");
			statusReport();
			return "valid"
		}
	}
}

function statusReport() {
	let submit = document.getElementById("submit");
	let confirm_password = document.getElementById("confirm");
	let new_password = document.getElementById("new_password");
	let current_password = document.getElementById("current_password");

	if(all([current_password.value, new_password.value, confirm_password.value])) {
		$.ajax({
			data: { "current": current_password.value, "new": new_password.value, "confirm": confirm_password.value },
			type: "POST",
			url: "/password_change_check"
		}).done(function(data) {
			if(data["resp"] == "valid") {
				displayMsg("", document.getElementById("form-status"), data["resp"]);
				submit.style.display = "block";
			} else {
				displayMsg("", document.getElementById("form-status"), data["resp"]);
				submit.style.display = "none";
			}
		});
    }
}

function all(items) {
	for(let n=0; n<items.length; n++) {
		if(!items[n]) {
			return false;
		}
	}
	return true;
}

function any(items) {
	for(let n=0; n<items.length; n++) {
		if(items[n]) {
			return true;
		}
	}
	return false;
}

function accountManagement() {
	$.ajax({
		type: "POST",
		url: "/account_management"
	}).done(function(data) {
		let display = document.getElementById("display");
		let html = data["resp"];
		if(html) {
			display.innerHTML = html;		
			setEventListenerOnTabs();
		}
	});
}

function passwordUpdateSource() {
	$.ajax({
		type: "POST",
		url: "/password_update_source"
	}).done(function(data) {
		let displayArea = document.getElementById("display-area");
		let html = data["resp"];
		if(html) {
			displayArea.innerHTML = html;			
		}
	});
}

function updatePassword() {
	let current = document.getElementById("current_password");
	let _new = document.getElementById("new_password");
	let confirm = document.getElementById("confirm");
	let submit = document.getElementById("submit");
	let load = document.getElementById("load");

	load.style.display = "block";
	submit.style.display = "none";

	if(all([current, _new, confirm])) {
		$.ajax({
			data: { "current": current.value, "new": _new.value, "confirm": confirm.value },
			type: "POST",
			url: "/update_password"
		}).done(function(data) {
			submit.style.display = "none";
			if(data["resp"]) {
				let notice = document.getElementById("notice");
				if(notice && "status" in data) {
					notice.innerHTML = data["status"];
				}
				if("status" in data) {
					load.style.display = "none";
					current.value = "";
					confirm.value = "";
					_new.value = "";
				}
				displayMsg("", document.getElementById("form-status"), data["resp"]);
			} 
		});
	}
}

function usernameUpdateSource() {
	$.ajax({
		type: "POST",
		url: "/username_update_source"
	}).done(function(data) {
		let displayArea = document.getElementById("display-area");
		let html = data["resp"];
		if(html) {
			try { 
				displayArea.innerHTML = html;	
			} catch(e) {

			}		
		}
	});
}

function updateUsername() {
	let username = document.getElementById("new_username");
	let submit = document.getElementById("submit");
	let load = document.getElementById("load");

	load.style.display = "block";
	submit.style.display = "none";

	if(username) {
		$.ajax({
			data: { "username": username.value },
			type: "POST",
			url: "/update_username"
		}).done(function(data) {
			submit.style.display = "none";
			if(data["resp"]) {
				let notice = document.getElementById("notice");
				if(notice && "status" in data) {
					notice.innerHTML = data["status"];
				}
				if("status" in data) {
					load.style.display = "none";
					username.value = "";
				}
				displayMsg("", document.getElementById("form-status"), data["resp"]);
			} 
		});
	}
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
				console.log(data);
				if("mode" in data) {
					if(data["mode"] == "Start Server") {

						if("failed" in data) {
							if(!data["failed"]) {
								ip.disabled = false;
								port.disabled = false;							
							} else {
								invalidate("ip");
								invalidate("port");
							}							
						}
						if("ipFailed" in data && "portFailed" in data) {
							if(!data["ipFailed"] && !data["portFailed"]) {
								ip.disabled = false;
								port.disabled = false;
							} else if(data["ipFailed"] && data["portFailed"]) {
								invalidate("ip");
								invalidate("port");
							} else if(data["ipFailed"]) {
								invalidate("ip");
							} else if(data["portFailed"]) {
								invalidate("port");
							}							
						}
					} else {
						ip.disabled = true;
						port.disabled = true;
					}

					btn.innerHTML = data["mode"];
				}
				btn.style.display = "block";
				load.style.display = "none";
		});
	}
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
				if(ip.value) {
					ip.disabled = true;
					port.disabled = true;
				} 
			}		
		}
	});	
}