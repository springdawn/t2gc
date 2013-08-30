function onClickedHandler(info, tab) {
    console.log('info', info);
    console.log('tab', tab);
    $.get('http://localhost:8000', {'selectionText': info.selectionText});
}
chrome.runtime.onInstalled.addListener(function() {
    chrome.contextMenus.create({title:'t2gc', 'id':'t2gc', contexts:['selection']});
});
chrome.contextMenus.onClicked.addListener(onClickedHandler);
//function getSelect(done) {
//    popupData = '';
//    chrome.tabs.query({active:true}, function(tabs) {
//        console.log(tabs[0].url);
//        chrome.tabs.sendMessage(tabs[0].id, {request:true}, function(response) {
//            console.log(response);
//            popupData = response.select || 'none';
//            done(popupData);
//        });
//    });
//}
