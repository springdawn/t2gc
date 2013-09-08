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
//    $.get('http://localhost:8000', {'selectionText': ''});
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
    $('#date').datepicker({dateFormat: 'yy-mm-dd'});
    $('#start_time').timepicker({stepMinute: 5, hourGrid:3, minuteGrid:15});
    $('#end_time').timepicker({stepMinute: 5, hourGrid:3, minuteGrid:15});
    $('#submit').prop('disabled', true);
    $('#date').change(function(){
        if($('#date').val()) {
            $('#submit').prop('disabled', false);
        } else {
            $('#submit').prop('disabled', true);
        }
    });
    $('#submit').click(submit);
//    $('#date').datepicker('setDate', '2013-09-01');
    //$('#date').datepicker();
});

function submit(e) {
    console.log("submit")
    var summary = encodeURI($('#summary').val()) || '';
    var dateval = $('#date').val();
    var date = validate('date', dateval)? dateval: '';
    var start_timeval = $('#start_time').val();
    var start_time = validate('time', start_timeval)? start_timeval: '';
    var end_timeval = $('#end_time').val();
    var end_time = validate('time', end_timeval)? end_timeval: '';
    var location = encodeURI($('#location').val()) || '';
    if(!date || (!start_time && end_time)) {
        console.log("invalid data");
        $("#status").html("invalid data");
        return;
    }
    $.get('http://localhost:8000',
          {title: summary, date: date, start: start_time, end: end_time, location: location},
          function(data){
              console.log(data)
          });
}

function validate(type, val) {
    if (!val) return false;
    if(type == 'date') {
        try {
            $.datepicker.parseDate($.datepicker.W3C, val);
            return true;
        } catch(e) {
            return false;
        }
    } else if(type == 'time') {
        var reg = /^(?:[01]\d|2[0-3]):[0-5]\d$/;
        return reg.test(val);
    }
}
