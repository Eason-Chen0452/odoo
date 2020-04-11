odoo.define("cpo_login.login_quotation", function(require) {
    "use strict";

    var Widget = require('web.Widget');
    var base = require('web_editor.base');
    var ajax = require("web.ajax");
    var core = require('web.core');
    var config = require("web.config");
    //
    var log = console.log.bind(console)

    function svgBlockNone(ele, status){
        /*
        * ele是JQ对象
        * status：block，none 类型String
        * */
        if(status == 'none'){
            ele.addClass('cpo-none').removeClass('cpo-block');
        }else{
            ele.addClass('cpo-block').removeClass('cpo-none');
        }
    }

    /*
    * 登录和注册页面的更改！
    * */
    var materialInputs = $('.login-page input.input-material');
    var materialLabel = $('.login-page label.input-material');
    // activate labels for prefilled values
    materialInputs.filter(function() { return $(this).val() !== ""; }).siblings('.label-material').addClass('active');
    // move label on focus
    materialInputs.on('focus', function () {
        $(this).siblings('.label-material').addClass('active');
    });
    materialLabel.on('click', function () {
        $(this).addClass('active');
        $(this).siblings('input.label-material').focus();
    });
    materialInputs.bind("input propertychange",function(event){
        $(this).siblings('.label-material').addClass('active');
    });
    // remove/keep label on blur
    materialInputs.on('blur', function () {
        $(this).siblings('.label-material').removeClass('active');

        if ($(this).val() !== '') {
            $(this).siblings('.label-material').addClass('active');
        } else {
            $(this).siblings('.label-material').removeClass('active');
        }
    });

    $('.oe_login_form a.cpo_login_btn').on('click', function () {
        svgBlockNone($('.svg_loading'), 'block');
        var values = {};
        $('.oe_login_form input').each(function () {
            values[this.name] = this.value;
        });
        ajax.jsonRpc("/check/login", 'call', values).then(function (data) {
            if(data.error){
                $('.oe_login_form').empty().html(data.error);
                svgBlockNone($('.svg_loading'), 'none');
            }else{
                $('.oe_login_form').submit();
            }
        });
    })
    $(document).keydown(function(event) {
        if (event.keyCode == 13) {
            $(".oe_login_form a.cpo_login_btn").click();
        }
    })

})