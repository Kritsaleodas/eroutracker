var current_page;

function changehtml(word, id) {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
        document.getElementById("board").innerHTML = this.responseText;
        current_page = word;
    }
    };

    const titles = document.querySelectorAll('.display-4');

    titles.forEach(title => {
        title.style.textDecoration = 'none';
    });

    document.getElementById(id).style.textDecoration = 'underline solid 3px';

    xhttp.open("GET", word, true);
    xhttp.send();
}

function delete_task(task_name) {
    //make a post request to the delete task controller
    //function(reponse) runs when req was successful
    $.post("/delete_task", {'task_name': task_name, 'current_page': current_page}, function(response) {
            $('#board').html(response);
    })
}

function drag(ev) {
    ev.dataTransfer.setData("text", ev.target.id);
    setTimeout(() => {
        $(ev.target).addClass('hide');
    }, 0);
    $('.navls').each(function() {
        $(this).addClass('dragstart');
    })
}

function dragend(ev) {
    $('.navls').each(function() {
        $(this).removeClass('dragstart');
    })
    $(ev.target).removeClass('hide');
}

function allowDrop(ev) {
    ev.preventDefault();
}

function on(ev) {
    $(ev.target).removeClass('display-4').addClass('dragover');
}

function out(ev) {
    $(ev.target).removeClass('dragover').addClass('display-4');
}


function drop(ev) {
    ev.preventDefault();
    var id = ev.dataTransfer.getData("text");
    var where = $(event.target).text();
    $.post("/", {'id': id, 'where': where}).done(function(data) {
        wherez(where);
    });
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


