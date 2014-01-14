$(document).ready(function(){
    $('#talook-info').click(function() {
	$('#myModal').modal('show');
    });


    $("[rel=tooltip]").tooltip({placement: 'bottom'});
    $("[rel=tooltip_search]").tooltip({placement: 'right'});
});
