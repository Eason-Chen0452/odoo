odoo.define("website_cpo_sale.ele_index_content", function(require) {
    "use strict";

    var base = require('web_editor.base');
    var ajax = require("web.ajax");
    var core = require('web.core');
    var config = require("web.config");

    $('#index-coupon').load("/cpo/index-coupon", function(responseTxt, statusTxt, xhr){
        if(statusTxt=="success"){
            $('.cpo-material-box').css('display', 'block');
        }
        // if(statusTxt=="error"){
        //     $('.cpo-material-box').css('display', 'none');
        // }
    });
    // 大banner
    // $(document).ready(function(){
    // $('.slider-area').load('/banner/test');
    if($('.slider-area').length > 0){
        ajax.jsonRpc('/banner/record', 'call', {
            'number': 1,
        }).then(function (data) {
            if(data){-
                $('.slider-area .slider-active').empty().html(data.cpo_banner_image_temp);
            }
            $('.slider-active').owlCarousel({
                loop: true,
                nav: true,
                dots: true,
                // pagination: true,
                // paginationNumbers: true,
                navText: ['<i class="fa fa-angle-left"></i>', '<i class="fa fa-angle-right"></i>'],
                items: 2,
                mouseDrag: false,
                touchDrag: false,
                responsive: {
                    0: {
                        items: 1
                    },
                    768: {
                        items: 1
                    },
                    1000: {
                        items: 1
                    }
                }
            });
            // 首页按钮颜色改变
            bannerFirstLoadPage() // 页面加载时改变颜色

            $('.slider-area').on('click', '.owl-prev', function(){
                bannerBTNColor(); // 设置按钮背景颜色
                bannerBGSVG() // 解决SVG背景重叠
            });
            $('.slider-area').on('click', '.owl-next', function(){
                bannerBTNColor(); // 设置按钮背景颜色
                bannerBGSVG() // 解决SVG背景重叠
            });
            $('.slider-area').on('click', '.owl-dots .owl-dot', function () {
                bannerBTNColor(); // 设置按钮背景颜色
                if($(this).hasClass('active')){
                    bannerBGSVG(); // 解决SVG背景重叠
                }
            });

        });
    }
    // 页面加载时改变颜色
    function bannerFirstLoadPage(){
        var slider_bg = $('.slider-area .active .single-slider').css('background-color');
        if(slider_bg){
            slider_bg = slider_bg;
        }else{
            slider_bg = '4a93fd';
        }
        $('.slider-area .slider-content .btn').css({'background-color': slider_bg, 'border-color': slider_bg});
        $('.slider-area .owl-dots .active').css({'background-color': slider_bg});
        $('.slider-area .cpo-quo-tt .quo-tt-active').css({'background-color': slider_bg, 'border-color': slider_bg});
    }
    // 幻灯片切换时改变颜色
    function bannerBTNColor() {
        var slider_bg = $('.slider-area .active .single-slider').css('background-color');
        $('.slider-area .owl-nav .owl-prev').css({'background-color': slider_bg, 'border-color': slider_bg});
        $('.slider-area .owl-nav .owl-next').css({'background-color': slider_bg, 'border-color': slider_bg});
        $('.slider-area .slider-content .btn').css({'background-color': slider_bg, 'border-color': slider_bg});
        $('.slider-area .cpo-quo-tt .quo-tt-active').css({'background-color': slider_bg, 'border-color': slider_bg});
        $('.slider-area .owl-dots .active').css({'background-color': slider_bg}).siblings().css({'background-color': '#ffffff'});
    }
    // 插件SVG图片会重叠，将不展示的隐藏
    function bannerBGSVG(){
        $('.slider-area .owl-stage .owl-item').each(function () {
            if($(this).hasClass('active')){
                // $(this).find('div.cpo_bg_svg').css({'display': 'block'});
                // $(this).css({'display':'block'});
                $(this).children().children('div.cpo_bg_svg').show();
                $(this).children().children('div.cpo_bg_svg').children('svg').css({'visibility':'visible'});
            }else{
                // $(this).find('div.cpo_bg_svg').css({'display': 'none'});
                // $(this).css({'display':'none'});
                $(this).children().children('div.cpo_bg_svg').hide();
                $(this).children().children('div.cpo_bg_svg').children('svg').css({'visibility':'hidden'});
            }
        });
    }

    ajax.jsonRpc('/page/natification', 'call', {
        'number': 1,
    }).then(function (data) {
        if(data){
            if($(".cpo-notification").length > 0){
                $(".cpo-notification").addClass('cpo-block');
                $(".cpo-notification").html(data.page_natification_temp);
                var d_len = $('.cpo-notification .natifi-cont');
                if(d_len.length > 2){
                    $(".cpo-notification .natifi-all").Scroll({
                        line: 1,
                        speed: 500,
                        timer: 10000
                    });
                }
            }
        }else{
            $(".cpo-notification").removeClass('cpo-none');
        }
    });

    // 展示优惠
    // if($('#index-coupon').length > 0){
    //     $('#index-coupon').empty();
    //     ajax.jsonRpc('/cpo/index-coupon', 'call').then(function (data) {
    //         if(data){
    //             // console.log(data)
    //             // $('.cpo-material-box').css('display', 'block');
    //             // $('#index-coupon').append(data.cpo_index_coupon);
    //         }else{
    //             $('.slider-area .owl-dots').css('bottom', '50px');
    //             $('.cpo-material-box').css('display', 'none');
    //         }
    //     });
    // }

	// });

    //
    ajax.jsonRpc('/get/cookie', 'call').then(function (data) {
        if(data){
            $('#cpo_cookie_time input').val(data);
        }else{
            $('#cpo_cookie_time input').val('');
        }
    })

    // PCBA 菜单
    if($('.cpo_choose_pcba').length > 0){
        ajax.jsonRpc('/pcba-condition', 'call').then(function (data) {
            if(data){
                $('.cpo_choose_pcba').html(data.pcba_condition);
            }
        })
    }

    // 电子物料展示
    // if($('.mat-content').length > 0){
    //     ajax.jsonRpc('/show/material', 'call').then(function (data) {
    //         if(data){
    //             $('.mat-content').css('display', 'block');
    //             $('.mat-content').empty().append(data.cpo_get_material_temp);
    //             $("#material-scroll").Scroll({
    //                 line: 1,
    //                 speed: 500,
    //                 timer: 10000
    //             });
    //         }else{
    //             $('.mat-content').empty();
    //             $('.mat-content').css('display', 'none');
    //         }
    //     })
    //
    // }

    // 新闻列表
    // $(document).ready(function(){
    //     ajax.jsonRpc('/cpo_new_list', 'call', {
    //         'number': 2,
    //     }).then(function (data) {
    //         $('.news_right').html(data.cpo_new_list_link);
    //     });
    // });

    // // 视频链接
    // $('.vjs-big-play-button').on('click', function () {
    //     ajax.jsonRpc('/cpo_video', 'call', {
    //         'number': 2,
    //     }).then(function (data) {
    //         var iframe_video = '<iframe id="facebook_video_link" src="'+data.cpo_company_video+'"\n' +
    //             'width="560" height="315" style="border:none;overflow:hidden" scrolling="no" frameborder="0" allowTransparency="true"\n' +
    //             'allowFullScreen="true"></iframe>'
    //         $('.cpo_video_bg').html(iframe_video)
    //     });
    // })
    // $(document).ready(function(){
     //    ajax.jsonRpc('/cpo_video', 'call', {
     //        'number': 2,
     //    }).then(function (data) {
     //        // $('.cpo_video_bg').html(data.cpo_company_video);
     //        var a = '<iframe class="facebook_video" src="https://www.facebook.com/plugins/video.php?href=https%3A%2F%2Fwww.facebook.com%2Fchinapcbone%2Fvideos%2F421556251938499%2F&amp;show_text=0&amp;width=560"\n' +
     //                'width="589" height="319" style="border:none;overflow:hidden" scrolling="no" frameborder="0"\n' +
     //                'allowTransparency="true" allowFullScreen="true"></iframe>'
     //        $('.cpo_video_bg').append(data.cpo_company_video);
     //    });
	// });

    //
    // $(document).ready(function(){
    //     ajax.jsonRpc('/cpo_pcb_online_sales', 'call', {
    //         'number': 1,
    //     }).then(function (data) {
    //         $('.multilayer_board').html("");
    //         $('.multilayer_board').html(data.cpo_pcb_online_content);
    //     });
    // });

    // Index 优惠券
    // $(document).ready(function(){
    //     ajax.jsonRpc('/cpo_coupon_list', 'call').then(function (data) {
    //         var coupon_content = $.trim(data.cpo_coupon_list);
    //         if(coupon_content != ''){
    //             $('.cpo-right').html(data.cpo_coupon_list);
    //         }
    //     });
    // });

    // 加载流程视频
    // $(document).ready(function(){
    //     ajax.jsonRpc('/load_cpo_video', 'call').then(function (data) {
    //         if(data){
    //             // $('.process_load_video').remove();
    //             $('#process_video').attr("src", data);
    //             var iframe = document.getElementById("process_video");
    //             if (iframe.attachEvent) {
    //                 iframe.attachEvent("onload", function() {
    //                 $("#order_tutorial .video_load").addClass("cpo-none");
    //                 alert("Video loading failed, please refresh and try again!");
    //                 });
    //             } else {
    //                 iframe.onload = function() {
    //                     $("#order_tutorial .video_load").addClass("cpo-none");
    //                 }
    //             };
    //         }
    //     });
    // });

    // 展示国家列表
    $(document).ready(function(){
        var country_content_val = $('.cpo_country_list .country_select');
        if(country_content_val.length > 0){
            ajax.jsonRpc('/cpo_country_list', 'call').then(function (data) {
                $('.cpo_country_list .country_select').html(data.cpo_country_list_temp);
                $('.cpo_country_list select.country_select').comboSelect();
                $(".cpo_country_list .country_select option").each(function () {
                    var result = $.trim($(this).html());
                    $(this).html(result)
                });
            });
        }
        // 报价AD
        if($('a.order-page-content').length > 0){
            ajax.jsonRpc('/advertising/order/page/', 'call').then(function (data) {
                $('a.order-page-content').html(data.order_page_ad_content)
            })
        }
	});


    // 展示产品介绍（轮播图）
    // $(document).ready(function(){
    //     ajax.jsonRpc('/cpo_board_list', 'call').then(function (data) {
    //         var cpo_board_description_link1 = $.trim(data.cpo_board_description_link);
    //         if(cpo_board_description_link1 != ''){
    //             $('.product_left_content .content_lb .cpo_click_lb').html(data.cpo_board_description_link);
    //         }
    //     });
    //
    //     ajax.jsonRpc('/cpo_board_right_list', 'call').then(function (data) {
    //         var cpo_board_description_link2 = $.trim(data.cpo_board_right_link);
    //         if(cpo_board_description_link2 != ''){
    //             $('.product_right_content .content_lb .cpo_click_lb').html(data.cpo_board_right_link);
    //         }
    //     });
    // });


    // Banner轮播
    // var margin_ll = 0;
    // var timers = setInterval(funcMar, 3000);
    // function funcMar(value){
    //     var lb_list_height = $('.cpo_lb li').height();
    //     var lb_list_length = $('.cpo_lb li').length;
    //     var lb_index = $('.lb_btn li');
    //     if(value == undefined){
    //         margin_ll += -lb_list_height;
    //     }else{
    //         margin_ll = -value;
    //     }
    //     $(".cpo_lb").css("margin-top",margin_ll+'px');
    //     lb_index.eq(Math.abs(Math.abs(margin_ll/lb_list_height))).addClass('li_ac').siblings().removeClass('li_ac');
    //     if(margin_ll == -lb_list_height*(lb_list_length-1)){
    //         margin_ll = lb_list_height;
    //     }
    // }
    // //Banner轮播点击跳转
    // // $('#cpo_price_compar_com table').on('change', 'input.cpo_quantity_val', function (e) {
    //
    // $('.cpo_lb_content').on('click', '.lb_btn li',function (){
    //     var lb_list_height = $('.cpo_lb li').height();
    //     var lb_list_length = $('.cpo_lb li').length;
    //     var margin_l = -lb_list_height;
    //     var _index = $(this).index();
    //     var margin_value = margin_l*_index;
    //     $(".cpo_lb").css("margin-top",margin_value+'px');
    //     $(this).addClass('li_ac').siblings().removeClass('li_ac');
    //     var time_out = setTimeout(funcMar(Math.abs(margin_value)),3000);
    //     clearInterval(time_out);
    // });

    // $('.o_chat_window .o_chat_header .o_chat_window_close').on('click', function(){
    //     alert(123);
    //     $('.o_livechat_button').css('display','block!important');
    // })



})