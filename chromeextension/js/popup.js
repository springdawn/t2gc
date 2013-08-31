console.log('popup');
//chrome.runtime.getBackgroundPage(function(background) {
//    background.getSelect(function(data){
//        console.log(data);
//        document.getElementById('data').innerHTML = data;
//        $.get('http://localhost:8000', {'selectionText': ''});
//    });
//});

getSelect(function(data){
    console.log(data);
    document.getElementById('data').innerHTML = data;
    $.get('http://localhost:8000', {'selectionText': ''});
});

//chrome.notifications.create('', {title:'ABC', message:'defg', type:'basic', iconUrl:'../dummy.jpg'}, function(id){console.log('notification id:', id);});

function getSelect(done) {
    popupData = '';
    chrome.tabs.query({active:true}, function(tabs) {
        console.log(tabs[0].url);
        chrome.tabs.sendMessage(tabs[0].id, {request:true}, function(response) {
            console.log(response);
            popupData = response.select || 'none';
            done(popupData);
        });
    });
}

$(function() {
    $('#data').focus();
    $('#date').datepicker({dateFormat: 'yy-mm-dd'});
//    $('#date').datepicker('setDate', '2013-09-01');
    //$('#date').datepicker();
});
