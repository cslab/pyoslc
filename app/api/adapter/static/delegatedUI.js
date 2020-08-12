function search(baseUrl) {
    var ie = window.navigator.userAgent.indexOf("MSIE");
    list = document.getElementById("results");
    list.options.length = 0;
    var searchMessage = document.getElementById('searchMessage');
    var loadingMessage = document.getElementById('loadingMessage');
    xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange = function () {
        if (xmlhttp.readyState == 4 && xmlhttp.status == 200) {
            // populate results
            txt = xmlhttp.responseText;
            resp = JSON.parse(txt);
            for (var i = 0; i < resp["oslc:results"].length; i = i + 1) {
                var item = new Option(resp["oslc:results"][i]["oslc:label"], resp["oslc:results"][i]["rdf:resource"], false, false);
                if (ie > 0) {
                    list.add(item);
                } else {
                    list.add(item, null);
                }
            }
            searchMessage.style.display = 'block';
            loadingMessage.style.display = 'none';
        }
    };
    stream = "data";
    xmlhttp.open("GET", baseUrl + "&stream=" + encodeURIComponent(stream), true);
    searchMessage.style.display = 'none';
    loadingMessage.style.display = 'block';
    xmlhttp.send();
}

function create(baseUrl) {
    var form = document.getElementById("Create");
    xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange = function () {
        if (xmlhttp.readyState == 4 && (xmlhttp.status == 201)) {
            var raw_response = xmlhttp.responseText;
            var json_response = JSON.parse(raw_response);
            // Send response to listener
            sendRawResponse(json_response);
        }
    };
    var postData = "";

    var formElements = form.elements;
    for (var i = 0; i < formElements.length; i++) {
        var el = formElements[i];
        var el_type = el.type;
        if (el && el.getAttribute("name")) {
            postData += '&' + el.getAttribute("name") + '=' + encodeURIComponent(el.value);
        }
    }

    xmlhttp.open("POST", baseUrl, true);
    xmlhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xmlhttp.setRequestHeader("Content-length", postData.length);
    xmlhttp.send(postData);
}

function select() {
    var list = document.getElementById("results");
    if (list.length > 0 && list.selectedIndex >= 0) { // something is selected
        var oslcResponse = 'oslc-response:{ "oslc:results": ['
        for (var item = 0; item < list.options.length; item++) {
            var option = list.options[item];
            if (option.selected) {
                oslcResponse += '{"oslc:label": "' + option.text + '", "rdf:resource": "' + option.value + '"}, '
            }
        }
        oslcResponse = oslcResponse.substr(0, oslcResponse.length - 2) + ']}'
        sendResponse(oslcResponse);
    }
}


function sendResponse(oslcResponse) {
    if (window.location.hash == '#oslc-core-windowName-1.0') {
        // Window Name protocol in use
        respondWithWindowName(oslcResponse);
    } else if (window.location.hash == '#oslc-core-postMessage-1.0') {
        // Post Message protocol in use
        respondWithPostMessage(oslcResponse);
    }
}

function sendRawResponse(jsonObj) {
    var oslcResponse = "oslc-response:" + JSON.stringify(jsonObj, null, 2);

    if (window.location.hash == '#oslc-core-windowName-1.0') {
        // Window Name protocol in use
        respondWithWindowName(oslcResponse);
    } else if (window.location.hash == '#oslc-core-postMessage-1.0') {
        // Post Message protocol in use
        respondWithPostMessage(oslcResponse);
    }
}

function sendCancelResponse() {
    var oslcResponse = 'oslc-response:{ "oslc:results": [ ]}';

    if (window.location.hash == '#oslc-core-windowName-1.0') {
        // Window Name protocol in use
        respondWithWindowName(oslcResponse);
    } else if (window.location.hash == '#oslc-core-postMessage-1.0') {
        // Post Message protocol in use
        respondWithPostMessage(oslcResponse);
    }
}


function respondWithWindowName(/*string*/ response) {
    var returnURL = window.name;
    window.name = response;
    window.location.href = returnURL;

}

function respondWithPostMessage(/*string*/ response) {
    if (window.parent != null) {
        window.parent.postMessage(response, "*");
    } else {
        window.postMessage(response, "*");
    }
}

function cancel() {
    sendCancelResponse();
}
