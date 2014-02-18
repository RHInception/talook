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
    // Execute it at the start
    load_from_hash();
});

CURRENT_ENV = null;
EXTRANOTES = "{{- extranotes -}}";
var hosts = {};

// Get the host list from the hosts local endpoint
$.ajax({
    url: 'hosts.json',
    async: false,
    success: function(data) {
        $.each(data, function(key, value) {
            hosts[key] = value;
        });
}});

var envs = ['All'];
add_topnav_env('All');
// Get the envs list from the envs local endpoint
$.getJSON('envs.json', function(data) {
    $.each(data, function(index, value) {
        // only add an env name if it isn't already in the list
        if (envs.indexOf(value) == -1) {
            envs.push(value);
            add_topnav_env(value);
        }
    });
});

function add_topnav_env(env) {
    $( '#topnav' ).append( $( "<li id='env-" + env + "'>" ).append(
        '<a href="#" onClick="load_hosts(\''+env+'\')">'+env+'</a>'));
}

function load_hosts(env) {
    CURRENT_ENV = env;
    $("li[id^='env-']").removeClass('active');
    $("#env-" + env).addClass('active');
    $("#sidenav").empty();
    var $env_hosts = [];
    $.each(hosts, function(host, hostenv) {
        if (hostenv == env || env == 'All') {
            $env_hosts.push(host);
        };
    });
    $env_hosts.sort();
    var $host_filter = new RegExp(get_host_filter());
    $.each($env_hosts, function(i, host) {
        if ($host_filter.test(host)) {
            $("#sidenav").append( '<li id="statsloader-' + host.replace(/\./g, '') + '" ><a href="#" onClick="load_stats(\''+host+'\')">'+host+'</a></li>');
        }
    });
    var num_hosts = $('#sidenav li').length;
    $("#sidenav").prepend( $('<li class="nav-header">Hosts (' + num_hosts + ')</li>'));
};

// Read the current filter from the filter input
function get_host_filter() {
    if ($('#hostfilter').val()) {
        return $('#hostfilter').val();
    } else {
        return ".*"
    }
}

// Host filter callback for the input form event handler
function filter_hosts() {
    load_hosts(CURRENT_ENV);
}

// Filter the hosts while typing in the filter input
$("#hostfilter").on("input", null, null, filter_hosts);

function loading_screen(host) {
    $("#loadinganimation").show();
    $("#loading").html("<h4>Loading stats for " + host + "</h4>");
    $("#loading").show();
}

function extranotes_link(host) {
    if ( EXTRANOTES != "") {
        var en_url = EXTRANOTES.replace(/%s/, host)
        return " [<a href='" + en_url + "' target=_blank>extra notes</a>]"
    } else {
        return ""
    }
}

function load_stats(host) {
    $("li[id^='statsloader-']").removeClass('active');
    $("#statsloader-" + host.replace(/\./g, '')).addClass('active');
    var host_endpoint = 'host/' + host + '.json';
    loading_screen(host);
    $("#content").empty().hide();
    $("#anchors").empty().hide();
    $("#anchors").append('<h4>Stats for '+host+' [<a href="'+host_endpoint+'">json</a>]' + extranotes_link(host) + '[<a href="/#!/host/'+host+'/">bookmark</a>]</h4>');
    $.getJSON(host_endpoint, function(data) {
        // each, WHERE: key = fact title string, value = fact hash
        $.each(data, function(key, value) {
            $( '#content' ).append('<a id="'+key+'"></a><h2>'+key+'</h2>');
            $( '#anchors' ).append('<a href="#'+key+'">'+key+'</a>&nbsp;');
            $( '#content' ).append( $( '<ul id="stat_'+key+'"></ul>' ) );
            var fact_keys = Object.keys(value).sort();
            $.each(fact_keys, function(i, fact_key) {
                $( '#stat_'+key ).append('<li><b>'+fact_key+'</b>: '+value[fact_key]+'</li>');
            });
        });
        $("#loading").hide();
        $("#loadinganimation").hide();
        $("#anchors").show();
        $("#content").show();
    });
};

function load_from_hash() {
    var parts = document.location.hash.split('/');
    if (parts[1] == 'host') {
        if (hosts.hasOwnProperty(parts[2])) {
            load_stats(parts[2]);
        } else {
            alert('Unknown host.');
        }
    }
};

// Hash router
$(window).on('hashchange', function(e) {
    load_from_hash();
});
