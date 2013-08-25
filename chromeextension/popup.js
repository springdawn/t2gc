console.log('popup');
chrome.runtime.getBackgroundPage(function(background) {
    background.getSelect(function(data){
        console.log(data);
        document.getElementById('data').innerHTML = data;
        $.get('http://localhost:8000', {'selectionText': ''});
    });
});
