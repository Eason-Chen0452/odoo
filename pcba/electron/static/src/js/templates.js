odoo.define("electron.electron", function(require) {
    "use strict";
    var base = require('web_editor.base');
    var ajax = require("web.ajax");
    var core = require('web.core');
    var config = require("web.config");
    var _t = core._t;
//$(document).ready(function () {
    //$("#table2").freezeHeader({ 'height': '100%' });
    //$("#table2").freezeHeader({offset : '0px'});
    $(".pv_pcba").change(function(e){
        var brands = $('option:selected');
        var selected = [];
        var search_count = $(".searh_count");
        var cpo_ids = $("form.to_filter_args");
        $(brands).each(function(index, brand){
            var ab={};
            ab[this.id]=$(this).val();
            selected.push(ab);
        });
        ajax.jsonRpc("/electron/get_product_len", 'call', {'category':this.dataset.category,'title':this.name,"filter":selected})
        .then(function (data){
            search_count.text(data.count);
            cpo_ids.find("input[name='cpo_ids']").val(data.ids)
            //_.each(data, function (e){
                //var self = this;
            //});

        });
        //console.log(selected);
        //alert(selected);
    });

    $('#cpo_header_selection table button').click(function () {
        $(this).parent().prev().children().attr('selected', false);
        $(this.parentElement.parentElement).find(".pv_pcba").trigger('change');
    })

    var navH = $("#ele_cpo_all").offset().top;
    $(window).scroll(function () {
        var scroH = $(this).scrollTop();
        // console.log(scroH)
        if (scroH >= navH) {
            $("#ele_cpo_all").css({
                "position": "fixed",
                "top": 0,
                'width': '299px',
                'background-color': '#ffffff'
            });
            $("#all_cpo_ele_right").css('margin-left','299px');
        } else if (scroH < navH) {
            $("#ele_cpo_all").css({"position": "static"});
            $("#all_cpo_ele_right").css('margin-left','0');
        }
    });





})

$(document).ready(function() {
    $('#table2xx').DataTable( {
        lengthChange: false,
        searching : false,
        "bInfo" : false,
        "bJQueryUI" : true,
        "scrollCollapse": true,
        "paging": false,
        "bAutoWidth": false,
        // "scrollX": true
    } );


} );
//On top

$(document).ready(function() {
    $('#category_cpo_ele li a').click(function () {
        // $(this).children('a').attr('id')
        var id_value = $(this).attr('id');
        console.log(id_value)
        var t = $('#all_cpo_ele_con'+' '+'#'+id_value).offset().top;
        console.log(t)
        $(window).scrollTop(t-20)
    });

});

