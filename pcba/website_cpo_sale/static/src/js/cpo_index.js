odoo.define("website_cpo_sale.website_product_description", function(require) {
    "use strict";

    var base = require('web_editor.base');
    var ajax = require("web.ajax");
    var core = require('web.core');
    var config = require("web.config");

    // $('.js-preloader').preloadinator({
    //    minTime: 0
    //  });

    // 关闭放假通知
    $('.cpo-notification').on('click', 'a.natifi-close', function () {
        $('.cpo-notification').addClass('cpo-none').removeClass('cpo-block');
    });
    // 产品描述
    $(document).ready(function () {

        // 工艺介绍

        // 工艺介绍
        if($('.cpo-apfc-area .cpo-process').length > 0){
            ajax.jsonRpc('/advertage/products', 'call', {
                'number': 1,
            }).then(function (data) {
                if(data){
                    $('.cpo-apfc-area .cpo-process').empty().html(data.cpo_advertage_products_temp);
                }
            });
        }
        // 打包价
        // if($('.popular-package .package-package').length > 0){
        //     ajax.jsonRpc('/package/price', 'call', {
        //         'number': 1,
        //     }).then(function (data) {
        //         if(data){
        //             $('.popular-package .package-package').empty().html(data.cpo_get_package_price_list);
        //         }
        //     });
        // }


        ajax.jsonRpc('/product/description', 'call', {
            'number': 1,
        }).then(function (data) {
            if(data){
                getProductDesc(data);
            }
            $('.testimonial-image-slider').slick({
                slidesToShow: 3,
                slidesToScroll: 1,
                asNavFor: '.testimonial-text-slider',
                dots: false,
                arrows: true,
                centerMode: true,
                focusOnSelect: true,
                centerPadding: '0px',
                // accessibility: true,
                responsive: [{
                        breakpoint: 767,
                        settings: {
                            dots: false,
                            slidesToShow: 1,
                        }
                    },
                    {
                        breakpoint: 420,
                        settings: {
                            autoplay: true,
                            dots: false,
                            slidesToShow: 1,
                            centerMode: false,
                        }
                    }
                ]
            });
        });
        function getProductDesc(data) {
            $('#product_content .testimonial-image-slider').append(data.cpo_product_description);
        }
        ajax.jsonRpc('/product/img', 'call', {
            'number': 1,
        }).then(function (data) {
            if(data){
                getProductIMG(data);
            }
            $('.testimonial-text-slider').slick({
                slidesToShow: 1,
                slidesToScroll: 1,
                arrows: false,
                draggable: false,
                fade: true,
                asNavFor: '.slider-nav',
            });
        });
        function getProductIMG(data) {
            $('#product_content .testimonial-text-slider').append(data.cpo_product_img_title);
        }
    });

    $(document).ready(function(){
        // 视频链接
        $('#movie_process_btn').on('click', function () {
            var $iframe = $('iframe#movie_process_video');
            if(!$iframe.attr('src')){
                ajax.jsonRpc('/process/video', 'call', {
                    'dicription': 'process',
                }).then(function (data) {
                    $iframe.attr('src', data);
                })
            }

        });
        $('#movie_company_btn').on('click', function () {
            var $iframe = $('iframe#movie_company_video');
            if(!$iframe.attr('src')){
                ajax.jsonRpc('/company/video', 'call', {
                    'dicription': 'index',
                }).then(function (data) {
                    $iframe.attr('src', data);
                })
            }
        })
        $('#movie_company .close').on('click', function () {
             $('iframe#movie_company_video').removeAttr('src');
        });
        $('#movie_company').on('click', function () {
            $('iframe#movie_company_video').removeAttr('src');
        })
        $('#movie_process .close').on('click', function () {
             $('iframe#movie_process_video').removeAttr('src');
        });
        $('#movie_process').on('click', function () {
            $('iframe#movie_process_video').removeAttr('src');
        })


    });

    //PCB和PCBA轮播图
        /*--
    Menu Stick
    -----------------------------------*/
    var header = $('#wrapwrap>header');
    var win = $(window);

    win.on('scroll', function() {
        var scroll = win.scrollTop();
        var win_width = $(window).width();
        var ac_page = $('.ac-page');
        if(ac_page.length > 0){
            ac_page.css('margin-top', '0');
            $('header>div.navbar').css('position', 'static');
            return true;
        }else {
            if(win_width <= 767){
                header.removeClass('stick');
            }else{
                if (scroll <= 80) {
                    header.removeClass('stick');
                } else {
                    header.addClass('stick');
                }
            }
        }
    });



    $(document).ready(function () {
        new WOW().init();
        // $("#material-scroll").Scroll({
        //     line: 1,
        //     speed: 500,
        //     timer: 5000
        // });
        
        $('.cpo-product-an ul li').on('click', function () {
            $(this).addClass('pd-an-active').siblings().removeClass('pd-an-active');
            $(this).find('span').remove()
            $(this).append('<span class="cpo-select-up"></span>');
            $(this).siblings().find('span').remove();
            var t_index = $(this).index();
            $('.cpo-product-lb .cpo-product-item').eq(t_index).addClass('slideInRight').siblings().removeClass('slideInRight');
            $('.cpo-product-lb .cpo-product-item').eq(t_index).addClass('cpo-block').siblings().removeClass('cpo-block');
            $('.cpo-product-lb .cpo-product-item').eq(t_index).css('visibility', 'inherit');
            scrollBody();
        })

        function scrollBody() {
            $('body,html').animate({
                scrollTop: $(window).scrollTop() + 1
            }, 0);
            $('body,html').animate({
                scrollTop: $(window).scrollTop() - 1
            }, 0);
        }
    });




    /* Slider active */
    // $('.slider-active').owlCarousel({
    //     loop: true,
    //     nav: true,
    //     // autoplay: true,
    //     // autoplayTimeout: 6000,
    //     navText: ['<i class="fa fa-angle-left"></i>', '<i class="fa fa-angle-right"></i>'],
    //     item: 1,
    //     responsive: {
    //         0: {
    //             items: 1
    //         },
    //         768: {
    //             items: 1
    //         },
    //         1000: {
    //             items: 1
    //         }
    //     }
    // })

        /* Brand logo active */
    // $('.brand-logo-active').owlCarousel({
    //     loop: true,
    //     nav: false,
    //     autoplay: false,
    //     autoplayTimeout: 5000,
    //     items: 4,
    //     margin: 50,
    //     responsive: false
    // })

    $('.cpo-banner-ul .cpo-banner-li select').on('change', function () {
        $(this).next().val($(this).val());
    });



    // $('.slider-area').on('mouseover', '.cpo-quo-tt .quo-tt-ls', function () {
    // $('.slider-area').on('mouseover', '.cpo-quo-tt .quo-tt-ls', function () {
    //     $(this).addClass('quo-tt-active').siblings().removeClass('quo-tt-active');
    //     var slider_bg = $('.slider-area .active .single-slider').css('background-color');
    //     $(this).css('background', slider_bg).siblings().css('background','rgb(255, 255, 255, 0)');
    //     var banner_li = $('.cpo-banner-ul .cpo-banner-li');
    //     var $index = $(this).index();
    //     banner_li.eq($index).addClass('cpo-block').removeClass('cpo-none')
    //     banner_li.eq($index).siblings().removeClass('cpo-block').addClass('cpo-none');
    // })
    $('.slider-area').on('click', '.cpo-quo-tt .quo-tt-ls', function () {
        $(this).addClass('quo-tt-active').siblings().removeClass('quo-tt-active');
        var slider_bg = $('.slider-area .active .single-slider').css('background-color');
        $(this).css('background', slider_bg).siblings().css('background','rgb(255, 255, 255, 0)');
        var banner_li = $('.cpo-banner-ul .cpo-banner-li');
        var $index = $(this).index();
        banner_li.eq($index).addClass('cpo-block').removeClass('cpo-none')
        banner_li.eq($index).siblings().removeClass('cpo-block').addClass('cpo-none');
    })
    $('.slider-area').on('mouseover', '.cpo-quo-tt .quo-tt-ls', function () {
        $(this).addClass('quo-tt-active').siblings().removeClass('quo-tt-active');
        var slider_bg = $('.slider-area .active .single-slider').css('background-color');
        $(this).css('background-color', slider_bg);
        $(this).siblings().css('background-color','rgb(255, 255, 255, 0)');
        var banner_li = $('.cpo-banner-ul .cpo-banner-li');
        var $index = $(this).index();
        banner_li.eq($index).addClass('cpo-block').removeClass('cpo-none')
        banner_li.eq($index).siblings().removeClass('cpo-block').addClass('cpo-none');
    })
    // $('.slider-area').on('mouseout', '.cpo-quo-tt .quo-tt-ls', function (){
    //      var slider_bg = $('.slider-area .active .single-slider').css('background-color');
    //     $(this).css('background', slider_bg).siblings().css('background','rgb(255, 255, 255, 0)');
    // })

    //报价切换（banner报价选项）
    $('.cpo_selete_quote>li').click(function () {
        var quo_li_index = $(this).index();
        $('.cpo_selete_quote_cont>li').eq(quo_li_index).addClass('cpo_li_active').siblings().removeClass('cpo_li_active')
        $(this).addClass("cpo_li_title_active").siblings().removeClass("cpo_li_title_active");
    });

    // 点击跳转到PCB下单
    $('.pcb_now_quote .btn').click(function () {
        $('form#cpo_pcb_action').submit();
    });
    // PCBA跳转
    $('.pcba_now_quote .btn').click(function (e) {
        $('form#create_pcba_order').submit();
    })
    // 钢网跳转
    $('.stencil_now_quote .btn').click(function (e) {
        $('form#cpo_stencil_action').submit();
    })
    $('form#cpo_stencil_action .stencil_thickness').on('change', function () {
        $('form#cpo_stencil_action input[name="stencil_thickness"]').val($(this).val());
    });
    $('form#cpo_stencil_action .cpo_stencil_size').on('change', function () {
        $('form#cpo_stencil_action input[name="cpo_stencil_size"]').val($(this).val());
    });
    // 电子物料
    $('.bom_now_quote .btn').click(function () {
        $('form#cpo_bom_action').submit();
    });


    var doscroll = function(){
         var cpo_news_ul = $('.news_right ul');
         var cpo_newul_first = cpo_news_ul.find('li:first');
         var height = cpo_newul_first.height();
         cpo_newul_first.animate({
             marginTop: -height + 'px'
             }, 500, function() {
             cpo_newul_first.css('marginTop', 0).appendTo(cpo_news_ul);
         });
    };
    var new_timer = setInterval(function(){doscroll()}, 5000);

     $('.cpo_selete_quote li').mouseover(function(){
        var quo_li_index = $(this).index();
        $('.cpo_selete_quote_cont>li').eq(quo_li_index).addClass('cpo_li_active').siblings().removeClass('cpo_li_active')
        $(this).addClass("cpo_li_title_active").siblings().removeClass("cpo_li_title_active");
        if($(this).hasClass('cpo_li_title_active')){
            $(this).removeClass('ac_hover');
        }else{
            $(this).addClass('ac_hover');
        }

     }).mouseout(function(){
        $(this).removeClass('ac_hover');
     });

    // Help 页面的图片放大功能
    $(".help-content").on('click', 'img.img', function(){
        var _this = $(this);//将当前的pimg元素作为_this传入函数
        imgShow("#outerdiv", "#innerdiv", "#bigimg", _this);
    });
    //
    $('.help_form a.help_search').on('click', function () {
        var search_data = $(this).parent().find('input[name="help_search"]').val();
        if(!search_data){
            alContent('The content can not be blank!');
            return false;
        }
        ajax.jsonRpc('/help/search', 'call', {
            'search': search_data,
        }).then(function (data) {
            if(data.error){
                alContent('No related content!');
                return false;
            }else{
                window.location.href = data.url;
            }
        })
    })

});
