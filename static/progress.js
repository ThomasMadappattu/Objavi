


function objavi_show_progress(task){
    var e =$("#" + task);
    e.css("color", "black");
    e.next().css("color", "red");

    if (task == 'finished' || task == 'publish_pdf'){
        $(".oncomplete").css("display", "block");
    }
}

