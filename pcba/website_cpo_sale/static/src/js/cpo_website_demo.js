odoo.define("website_cpo_sale.cpo_website_demo", function(require) {
    "use strict";

    var Widget = require('web.Widget');
    var base = require('web_editor.base');
    var ajax = require("web.ajax");
    var core = require('web.core');
    var config = require("web.config");
        
    ajax.jsonRpc("/website/cpo_demo/json", 'call', {
        '123':123,
    })
    .then(function (data) {
        _.each(data, function(e){
            var demo_content = $("div"+e.class);
            var demo_content_bigbox = $("#cpo_content_prompt_big");
            demo_content.parent().removeClass("hide");
            demo_content.html(e.content);
            demo_content.append('<span style="" id="demo_content_close"><i class="fa fa-close fa-2x"></i></span>')
            // demo_content.parent().on('click',function () {
            //     demo_content.removeClass("hidden");
            //     demo_content.addClass("show");
            // });
            demo_content.click(function () {
                return false
            });
            $('#cpo_open_demo').on('click',function () {
                demo_content_bigbox.removeClass("hidden");
                demo_content_bigbox.addClass("show");
                $(document.body).css({
                   "overflow-x":"hidden",
                   "overflow-y":"hidden"
                 });
            });
            demo_content_bigbox.on('click',function () {
                demo_content_bigbox.removeClass("show");
                demo_content_bigbox.addClass("hidden");
                $(document.body).css({
                   "overflow-x":"auto",
                   "overflow-y":"auto"
                });

                return false
            });
            $('#demo_content_close').on('click',function () {
                demo_content_bigbox.removeClass("show");
                demo_content_bigbox.addClass("hidden");
                $(document.body).css({
                   "overflow-x":"auto",
                   "overflow-y":"auto"
                });
                return false
            });

        })
    });

})
