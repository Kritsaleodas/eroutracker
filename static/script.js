var page = 'none';

function changehtml(page, id) {
   var jqXHR = $.ajax({
        url: page,
        method: "GET",
    });
    jqXHR.always(function() {
        $('#board').text("");
    })
    jqXHR.done(function(html) {
        //clear underlined buttons on navbar and underline the current page's button
        $('.display-4').css('text-decoration', 'none')
        $('#'+id).css('text-decoration','underline solid 7%')
        //changehtml of empty division
        $('#add_task_div').append(html);
        //call partready to add drag and drop effects now that the partial html has been loaded
        partready();
    })
}

function partready() {
    $('.card').each(function(obj) {
        var tst = 
    })
    //attach drag n drop effects to all card elements
}

function remove(element) {
    var id = element.parentNode.parentNode.id;
    var where = ''
    if (page == '/week') {
        where = 'Week';
    }
    if (page == '/today') {
        where = 'Today';
    }
    if (page == '/done') {
        where = 'Done';
    }

    $.post("/", {'id': id, 'where': 'delete'}).done(function(data) {
            wherez(where);
    })
}

function wherez(where) {
    if (where == 'Week') {
        changehtml('/week','weekbutton');
    }
    else if (where == 'Today') {
        changehtml('/today','todaybutton');
    }
    else if (where == 'Done') {
        changehtml('/done','donebutton');
    }
    else if (where == 'Stats') {
        changehtml('/stats', 'statsbutton');
    }
}

function fail(element) {
    var id = element.parentNode.parentNode.id;
    var action = $(element).text();
    if (action == 'Fail') {
        $.post("/", {'id': id, 'where': 'fail'}).done(function(data) {
            wherez('Done');
        });
    }

    else if (action == 'Unfail') {
        $.post("/", {'id': id, 'where': 'unfail'}).done(function(data) {
            wherez('Done');
        });
    }
}

function endweek() {
    if (confirm('All tasks will be erased. Are you sure you want to end week?') == true) {
        if (confirm('Do you want tasks to be added into the stats?') == true)
        {
            $.post("/stats").done(function(data) {
                wherez('Stats');
            });
        }
    }
}


//drag n drop stuff
$(document).ready(function() {
    $('#testtest').click(function() {
        alert('f');
    })
})