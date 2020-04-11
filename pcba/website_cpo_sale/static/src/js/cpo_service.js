// odoo.define("website_cpo_sale.cpo_web_service", function(require) {
//     "use strict";
//
//     var Widget = require('web.Widget');
//     var base = require('web_editor.base');
//     var ajax = require("web.ajax");
//     var core = require('web.core');
//     var config = require("web.config");
//
//     $('#cpo_accept_temrs_conditions').click(function () {
//         $('#cpo_terms_and_conditions').css({'display': 'none'});
//     });
// })
$(function () {
    $.fn.textScroll=function(){
        var p = $(this),  c = p.children(), speed=3000; //值越大速度越小
        var cw = c.width(),pw=p.width();
        var t = (cw / 100) * speed;
        var f = null, t1 = 0;
        function ani(tm) {
            counttime();
            c.animate({ left: -cw }, tm, "linear", function () {  c.css({ left: pw });  clearInterval(f);  t1 = 0;  t=((cw+pw)/100)*speed;  ani(t);
            });
        }
        function counttime() {
            f = setInterval(function () {
                t1 += 10;  }, 10);
        }
        p.on({  mouseenter: function () {
            c.stop(false, false);
            clearInterval(f);
            console.log(t1);
        },  mouseleave: function () {
            ani(t - t1);
            console.log(t1);
        }  });
        ani(t);
    }

    // 文字滚动
    $("#cpo-text-cont").textScroll();
})

