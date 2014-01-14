$(document).ready(function(){
    $('#talook-info').click(function() {
	$('#myModal').modal('show');
    });


    $("[rel=tooltip]").tooltip({placement: 'bottom'});
    $("[rel=tooltip_search]").tooltip({placement: 'right'});

    $("#clearfilter").click(function(event) {
        $("#hostfilter").val("");
        load_hosts(CURRENT_ENV);
    });
});
