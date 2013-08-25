chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
    console.log(request)
    if(request.request == true) {
        console.log(request);
        sendResponse({response:true, select:window.getSelection().toString()});
    } else {
        sendResponse({response:false});
    }
});
