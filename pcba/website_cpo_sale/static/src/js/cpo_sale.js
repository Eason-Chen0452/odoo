odoo.define('website_cpo_sale.test_shop', function (require) {
    "use strict";

//    var widgets = require('web_editor.widget');
    var Widget = require('web.Widget');
    var base = require('web_editor.base');
    var ajax = require("web.ajax");
    var core = require('web.core');
    var config = require("web.config");
    var _t = core._t;
    var qweb = core.qweb;
ajax.loadXML('/website_cpo_sale/static/src/xml/cpo_electron_upload.xml', qweb);

var cpo_ELE_Dialog = Widget.extend({
    template: 'website.cpo.sale.upload',
    events: {
        'hidden.bs.modal': 'destroy',
        'click button.save': 'save',
        'click button[data-dismiss="modal"]': 'cancel',
        'change input#upload': 'file_upload',
        //'change input#url': 'slide_url',
        'click .list-group-item': function (ev) {
            this.$('.list-group-item').removeClass('active');
            $(ev.target).closest('li').addClass('active');
        }
    },
    init: function (el, order_id, product_type) {
        this._super(el, order_id, product_type);
        this.order_id = parseInt(order_id, 10);
        this.file = {};
        this.product_type = product_type;
        this.index_content = "";
        this.file_types = ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet','application/pdf'];
    },
    start: function () {
        this.$el.modal({
            backdrop: 'static'
        });
        $('.modal-title').text('Upload Files Wizard');
        //this.set_category_id();
        this.set_tag_ids();
    },

    file_upload: function (ev) {
        var self = this,
            file = ev.target.files[0],
            is_image = /^image\/.*/.test(file.type),
            loaded = false;
        this.file.name = file.name;
        this.file.type = file.type;
        var index_type = $.inArray(file.type, this.file_types)
        if (index_type < 0 && 1==2) {
            this.display_alert(_t("Invalid file type. Please select excel file"));
            this.reset_file();
            return;
        }
        if (file.size / 1024 / 1024 > 25) {
            this.display_alert(_t("File is too big. File size cannot exceed 25MB"));
            this.reset_file();
            return;
        }
        this.$('.alert-warning').remove();
        var BinaryReader = new FileReader();
        // file read as DataURL
        BinaryReader.readAsDataURL(file);
        BinaryReader.onloadend = function (upload) {
            var buffer = upload.target.result;
            if (is_image) {
                self.$("#slide-image").attr("src", buffer);
            }
            buffer = buffer.split(',')[1];
            self.file.data = buffer;
        };
        if ( index_type >= 0 || 1==1) {
            var ArrayReader = new FileReader();
            this.$('.save').button('loading');
            // file read as ArrayBuffer for PDFJS get_Document API
            ArrayReader.readAsArrayBuffer(file);
            ArrayReader.onload = function (evt) {
                var buffer = evt.target.result;
                self.$('.save').button('reset');
                var passwordNeeded = function () {
                    self.display_alert(_t("You can not upload password protected file."));
                    self.reset_file();
                    self.$('.save').button('reset');
                };
            };
        }

        var input = file.name;
        var input_val = input.substr(0, input.lastIndexOf('.')) || input;
        self.$('#name').val(input_val);
    },
    reset_file: function () {
        var control = this.$('#upload');
        control.replaceWith(control = control.clone(true));
        this.file.name = false;
    },
    display_alert: function (message) {
        this.$('.alert-warning').remove();
        $('<div class="alert alert-warning" role="alert">' + message + '</div>').insertBefore(this.$('form'));
    },
    // Tags management from select2
    set_tag_ids: function () {
        var self = this;
        //var data = [{ id: 0, text: 'BOM File' }, { id: 1, text: 'SMT FILE' }, { id: 2, text: 'Gerber File' }];
        var tag_ids = $("#cpo_ele_tag_ids");
        if ($('.oe_electron_js_upload')[0].attributes.file_type){
            tag_ids.select2({
                data: [{'id':1, 'text':$('.oe_electron_js_upload')[0].getAttribute('file_type')}],
                width: '100%',
                placeholder:'请选择',
                allowClear:true
            })
        } else {
            ajax.jsonRpc("/get_electron_type", 'call',
                {'product_type': this.product_type}).then(function (data) {
                tag_ids.select2({
                    data: data,
                    width: '100%',
                    placeholder:'请选择',
                    allowClear:true
                })
            });
        }
    },
    get_tag_ids: function () {
        var res = [];
        _.each($('#cpo_ele_tag_ids').select2('data'),
            function (val) {
                if (val.create) {
                    res.push([0, 0, {'name': val.text}]);
                } else {
                    res.push([4, val.id]);
                }
            });
        return res;
    },
    get_value: function () {
        var file_type_name = $(".select2-chosen").text();//this.$('#cpo_ele_tag_ids').val();
        var name = this.file.name;
        var values = {
            'order_id': this.order_id || '',
            'name': name,
            'url': this.$('#url').val(),
            'tag_ids': file_type_name,
        };
        if ($.inArray(this.file.type, this.file_types) >= 0 || 1==1) {
            _.extend(values, {
                'mime_type': this.file.type,
                'datas': this.file.data
            });
        }
        return values;
    },
    validate: function () {
        this.$('.form-group').removeClass('has-error');
        if (!this.$('#upload').val()) {
            this.$('#upload').closest('.form-group').addClass('has-error');
            return false;
        }
        if (!this.$('#cpo_ele_tag_ids').val()) {
            this.$('#cpo_ele_tag_ids').closest('.form-group').addClass('has-error');
            return false;
        }
        return true;
    },
    save: function (ev) {
        var self = this;
        if (this.validate()) {
            var values = this.get_value();
            if ($(ev.target).data('published')) {
                values.website_published = true;
            }
            // this.$('.oe_slides_upload_loading').show();
            // this.$('.modal-footer, .modal-body').hide();
            $('.svg_loading').addClass('cpo-block').removeClass('cpo-none');
            this.$el.hide();
            ajax.jsonRpc("/pcb_electron/upload_file", 'call', values).then(function (data) {
                if (data.error) {
                    self.display_alert(data.error);
                    self.$('.oe_slides_upload_loading').hide();
                    self.$('.modal-footer, .modal-body').show();
                } else {
                    if (data.is_bom){
                        var $form = $('form[id="cpo_bom_check_ref_form_act"]');
                        $form[0].atta_id.value = data.atta_id;
                        $form.submit();
                    } else {
                        window.location = data.url;
                    }
                }
            });
        }
    },
    cancel: function () {
        this.trigger("cancel");
    }
});



//订单上上传文件
//    $('.generated_order_upload')
$('#testest').on('change', 'input.order_upload_file', function () {
    var file_types = ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet','application/pdf']
    var values;
    var file = this.files[0];
    var order_id = this.parentNode.getAttribute('order_id');
    var tag_name_num = this.getAttribute('id');
    var is_image = /^image\/.*/.test(file.type)
    if(is_image){
        webAlert('The file format is incorrect, please re-upload !', null, false);
        // alert("The file format is incorrect, please re-upload !");
        return ;
    }
    var index_type = $.inArray(file.type, this.file_types)
    if (index_type < 0 && 1==2) {
        this.display_alert(_t("Invalid file type. Please select excel file"));
        this.reset_file();
        return;
    }
    if (file.size / 1024 / 1024 > 25) {
        this.display_alert(_t("File is too big. File size cannot exceed 25MB"));
        this.reset_file();
        return;
    }
    var BinaryReader = new FileReader();
    BinaryReader.readAsDataURL(file);
    BinaryReader.onloadend = function (upload) {
        var buffer = upload.target.result;
        var datas = buffer.split(',')[1];
        var mime_type = buffer.split(',')[0];
        ///pcb_electron/upload_file
        values = {
            'datas': datas,
            'name': file.name,
            'order_id': order_id,
            'tag_ids': tag_name_num,
            'mime_type': mime_type,
        }
        ajax.jsonRpc("/pcb_electron/upload_file", 'call', values).then(function (data) {
            if (data.error) {
                // alert(data.error);
                webAlert(data.error, null, false);
            } else {
                if (data.is_bom){
                    var $form = $('form[id="cpo_bom_check_ref_form_act"]');
                    $form[0].atta_id.value = data.atta_id;
                    $form.submit();
                } else {
                    window.location = data.url;
                }
            }
        })

    };
});

// 订单待确认状态时，如果订单出错，客户可以重新上传
$('.cpo_confirmed_order .generated_order_upload').on('change', 'input.order_upload_file', function () {
    var file_types = ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet','application/pdf']
    var values;
    var file = this.files[0];
    var order_id = this.parentNode.getAttribute('order_id');
    var tag_name_num = this.getAttribute('id');
    var is_image = /^image\/.*/.test(file.type)
    if(is_image){
        webAlert("The file format is incorrect, please re-upload !", null, false);
        // alert("The file format is incorrect, please re-upload !");
    }
    var index_type = $.inArray(file.type, this.file_types)
    if (index_type < 0 && 1==2) {
        this.display_alert(_t("Invalid file type. Please select excel file"));
        this.reset_file();
        return;
    }
    if (file.size / 1024 / 1024 > 25) {
        this.display_alert(_t("File is too big. File size cannot exceed 25MB"));
        this.reset_file();
        return;
    }
    var BinaryReader = new FileReader();
    BinaryReader.readAsDataURL(file);
    BinaryReader.onloadend = function (upload) {
        var buffer = upload.target.result;
        var datas = buffer.split(',')[1];
        var mime_type = buffer.split(',')[0];
        values = {
            'datas': datas,
            'name': file.name,
            'order_id': order_id,
            'tag_ids': tag_name_num,
            'mime_type': mime_type,
        }
        ajax.jsonRpc("/confirm/order/upload_file", 'call', values).then(function (data) {
            if (data.error) {
                webAlert(data.error, null, false);
                // alert(data.error);
            } else {
                if (data.is_bom){
                    var $form = $('form[id="cpo_bom_check_ref_form_act"]');
                    $form[0].atta_id.value = data.atta_id;
                    $form.submit();
                } else {
                    window.location = "/my/waitconf";
                }
            }
        })

    };
});

//领取优惠券
$(document).ready(function(){
    $('body').on('click', '.cpo-receive', function () {
        var div_sib = $(this).next();
        var div_this = $(this);
        var coupon_id = $(this).attr('id');
        ajax.jsonRpc('/confrim_coupon', 'call',{
            'coupon_id': coupon_id
        }).then(function (data) {
            if(data.tips){
                // alert(data.tips);
                webAlert(data.tips, null, false);
                window.open(data.url, '_self');
            }else if(data.verification){
                // div_sib.addClass('cpo-block').removeClass('cpo-none');
                // div_this.parent().parent().parent().addClass('cash-coupon-box-received');
                // div_this.parent().parent().next('div.cpo-coupon-receive').addClass('cpo-block').removeClass('cpo-none');
                // div_this.parent().addClass('cpo-none').removeClass('cpo-block');
                // alert(data.value);
                div_this.text('Received')
                div_this.css('background', '#61b9ef');
                webAlert(data.value, null, false);
                // alert(data.value);
            }else{
                webAlert(data.warning, null, false);
                // alert(data.warning)
            }
        })
    });
    // $('.cpo-index-coupon').on('click', '.cpo-coupon-btn', function () {
    //     var div_sib = $(this).parent().find('.cpo-coupon-receive');
    //     var coupon_id = $(this).attr('id');
    //     ajax.jsonRpc('/confrim_coupon', 'call',{
    //         'coupon_id': coupon_id
    //     }).then(function (data) {
    //         if(data.tips){
    //             alert(data.tips);
    //             window.open(data.url, '_self');
    //         }else if(data.verification){
    //             div_sib.addClass('cpo-block').removeClass('cpo-none');
    //             alert(data.value);
    //         }else{
    //             alert(data.warning)
    //         }
    //     })
    // });
    // url: /coupon
    $('#cpo_receive_coupon').on('click', '.cpo-cash-btn', function () {
        var div_sib = $(this).next();
        var div_this = $(this);
        var coupon_id = $(this).attr('id');
        ajax.jsonRpc('confrim_coupon', 'call',{
            'coupon_id': coupon_id
        }).then(function (data) {
            if(data.tips){
                // alert(data.tips);
                webAlert(data.tips, function (f) {
                    if(f){
                        window.open(data.url, '_blank');
                    }
                }, false);
                // window.open(data.url, '_blank');
            }else if(data.verification){
                div_sib.addClass('cpo-block').removeClass('cpo-none');
                div_this.parent().parent().parent().addClass('cash-coupon-box-received');
                div_this.parent().parent().next('div.cpo-coupon-receive').addClass('cpo-block').removeClass('cpo-none');
                div_this.parent().addClass('cpo-none').removeClass('cpo-block');
                // alert(data.value);
                webAlert(data.value, null, false);
            }else{
                webAlert(data.warning, null, false);
                // alert(data.warning)
            }
        })
    });

});

 //使用优惠券
$('#cpo_coupon_use_page').on('click', '.cpo-circle-btn', function (){
    // $('form#coupon_form_order').submit();
     var express = $('#cpo_delivery_methods .methods_select .cpo-select');
     var cpo_supply_method = null;
     if(express.length > 0){
         cpo_supply_method = express.siblings('span').html().trim();
     }
    $(this).toggleClass('cpo-select');
    var res = [];
    var checked_coupon_use ;
    if($(this).hasClass('cpo-select')){
        checked_coupon_use = true;
    }else{
        checked_coupon_use = false;
    }
    $('#cart_products td.td-order_name span').each(function () {
        res.push($(this).attr('data-id'));
    })

    ajax.jsonRpc("/shop/cpo_coupon_form", 'call', {
        'checked_coupon_use': checked_coupon_use,
        'order_names': res,
        'cpo_supply_method': cpo_supply_method,
        'coupon_id': $(this).prev().val(),
        'order_use_id': $(this).parents('tr').attr('id'),
    }).then(function (data) {
        $('#cpo_coupon_use_page').html(data.cpo_coupon_list_content);
    })

});

//导航栏的下拉（个人中心）
// var cpo_clienWith = document.body.clientWidth;
// if(cpo_clienWith > 500){
//     $('#top_menu .dropdown').on("mouseover", function () {
//         if(cpo_clienWith > 500){
//             $(this).addClass('open');
//         }else {
//             $(this).addClass('open');
//         }
//     });
//     $('#top_menu .dropdown').on("mouseout", function () {
//         $(this).removeClass('open');
//     });
// }

// $('.cpo-go-home').click(function () {
//     // window.location = '/my/home';
//     window.open('/my/home', '_blank');
// })

$('.oe_electron_js_upload').on('click', function () {
    var order_id = $(this).attr('order_id');
    var product_type = $(this).attr('product_type');
    new cpo_ELE_Dialog(this, order_id, product_type).appendTo(document.body);
});

$('a[href*="/shop"]').parents("li:first").remove();
$("button.filepicker").click(function(e) {
    var filepicker = $('input[type=file]');
    if (!_.isEmpty(filepicker)) {
        filepicker[0].click();
    }
});



//创建订单前确认所有数据
$('.check_data .check_all_data_btn').click(function () {
    if($(this).hasClass('check_data_active')){
        $(this).removeClass('check_data_active');
        $(this).parent().addClass('cpo-confirm')
    }else{
        $(this).addClass('check_data_active');
        $(this).parent().removeClass('cpo-confirm')
    }
    return false
});

$('#pcb_details .pcba_details_data').mouseover(function () {
    $(this).css('cursor', 'pointer');
}).mouseout(function () {
    $(this).css('cursor', 'default');
});
//$('a[href*="/shop/checkout"]').click();

$('.oe_website_sale #product_details .js_add_cart_variants #add_to_cart').off('click').on('click', function (event) {
    //判断是否加急
    var cpo_pcb_normal = $('#cpo_pcb_detail_peice .cpo_pcb_select_delivery_period');
    var cpo_pcb_expedited = $('#cpo_pcb_expedited_select .cpo_pcb_select_delivery_period');
    var expedited = true
    if($('#cpo_pcb_expedited_select').css('display')== 'table'){
        if(cpo_pcb_expedited.hasClass('pcb_active') || cpo_pcb_normal.hasClass('pcb_active')){
            expedited = true
        }else{
            $('#cpo_pcb_detail_peice').css('border', '2px solid #ff0000');
            $('#cpo_pcb_expedited_select').css('border', '2px solid #ff0000');
            webAlert("Please choose one of them !", null, false);
            // alert("Please choose one of them !")
            return false
        }
        // return expedited
    }
    //判断是否确认数据
    var cpo_check_data = $('.check_data .check_all_data_btn');
    // var cpo_pcb_check_data = $('#pcb_quo .pcb_details_all_data .check_all_data_btn');
    if(cpo_check_data.length){
        if(!cpo_check_data.hasClass('check_data_active')){
            cpo_check_data.parent('div.check_data').addClass('cpo-confirm');
            $('body,html').animate({scrollTop: 300}, 500);
            // alert("Please check all the above information !");
            webAlert('Please check all the above information !', null, false);
            return false
        }
    }

    if (!event.isDefaultPrevented() && !$(this).is(".disabled")) {
        event.preventDefault();
        $(".js_add_cart_variants input[name='text_val']").attr("value",$("#xiangqing textarea").val());
        $(this).closest('form').submit();
    }

    $('#pcb_order_load_content').css('display', 'block');
})
$('.website_my_bom_form .js_add_cart_variantsx #bom_to_get_pcba_price').off('click').on('click', function (event) {
    if (!event.isDefaultPrevented() && !$(this).is(".disabled")) {
        event.preventDefault();
        //$(".js_add_cart_variants input[name='text_val']").attr("value",$("#xiangqing textarea").val());
        $(this).closest('form').submit();
    }
    })
$('.ele_confirm_sale_order').on('click', '.ele_confirm_cart_form', function() {
    var self = this;
    var order_ids = [];
    var order_id = null;
    var ele_cart_obj = $(".ele_cart_checke_input");

    self.check_atta = true;
    self.has_checked_input = false;
    var has_file_type_obj = {};
    _.each(ele_cart_obj, function(e, index){
        if (e.checked){

            self.has_checked_input = true;
            // 这是旧样式的代码，恢复旧样式使用
            // var td_list = $(e.parentElement.parentElement.children).find("#cpo_ele_cart_att table tbody tr");
            var td_list = $(e.parentElement.parentElement.children).find('.cart_file_type');
            self.file_list = [];
            _.each(td_list, function(e, index){
                // var file_name = $(e).find("td span").text();
                var file_name = $(e).find("span").text();
                if (file_name) {
                    self.file_list.push(file_name);
                };
            }, self);
            // if ($($(e.parentElement.parentElement.children).find("#cpo_ele_cart_att table tbody tr")).length < 3){
            //     self.check_atta = false;
            //     return
            // }
            order_ids.push(e.id);
            has_file_type_obj[e.id] = self.file_list;
            //order_id = e.id;
            // check_upload_file(order_id, self.file_list);

        }
    }, self);
    //ajax.jsonRpc("/pcb_order/cpo_pcb_type", 'call', {
                //'order_ids': order_ids,
                //'has_file_type_obj': has_file_type_obj
            //}).then(function (data) {
                 //_.each(data, function(e, order_name){
                     //alert("Order: " + order_name + ", To upload:" + e + "!");
                     //return
                 //})
            //});
    if (!self.has_checked_input){
        webAlert("Please select the order !", null, false);
        // alert("Please select the order!");
        return
    }

    //check bom
    if (self.check_atta){
        ajax.jsonRpc("/pcb_electron/cpo_pcba_data_check", 'call', {
            'order_ids': order_ids,
            'has_file_type_obj': has_file_type_obj
        }).then(function (data) {
            if (data.error.length > 0){
                _.each(data.error, function(e, order_name){
                    if (e.bom_check_state) {
                        if (e.bom_check_state == 'check_off') {
                            // alert(e.bom_check_state +"Order: " + e.order_name + ", Please first analyze the BOM file of order !");
                            webAlert("Order: " + e.order_name + ", Please first analyze the BOM file of order !", null, false);
                            // alert("Order: " + e.order_name + ", Please first analyze the BOM file of order !");
                        }
                        return
                    }else{
                        webAlert("Order: " + e.order_name + ", To upload:" + e.upload_error + "!", null, false)
                        // alert("Order: " + e.order_name + ", To upload:" + e.upload_error + "!");
                        return
                    }
                })
                //alert("Please first analyze the BOM file of order !");
                return
            }
            if(data.pcb_supply_method.length > 0){
                _.each(data.pcb_supply_method, function(e, order_name){
                    if (e.pcb_order_name) {
                        webAlert("Order: " + e.pcb_order_name + ", PCB Supply method: "+ e.pcb_supply+ " , " + e.pcb_supply_message + " !", null, false)
                       // alert("Order: " + e.pcb_order_name + ", PCB Supply method: "+ e.pcb_supply+ " , " + e.pcb_supply_message + " !");
                       return
                    }
                })
                return
            }
            //if(data.check_state == 'check_on'){
            $('.ele_confirm_sale_order input[id="ele_cart_order_ids"]').val(order_ids);
            //window.alert( "order:"+order_ids);
            //$(this).parent('form.ele_confirm_sale_order').attr('action', '/shop/checkout').submit();
            $('form.ele_confirm_sale_order').attr('action', '/shop/checkout').submit();
            //}

        });
    }

});

//首页钢网数据跳转下一页
$("#cpo_stencil_action .index_stencil_thickness").on("change", function () {
    $("#cpo_stencil_action input[name='cpo_stencil_thick']").val($(this).val());
});
$("#cpo_stencil_action .index_stencil_size").on("change", function () {
    $("#cpo_stencil_action input[name='cpo_stencil_size']").val($(this).val());
});



//check upload file
// function check_upload_file(order_id, file_list) {
//     ajax.jsonRpc("/pcb_order/cpo_pcb_type", 'call', {
//         'order_id': order_id,
//     }).then(function (data) {
//         var order_type_list = data.order_type_list;
//         var this_list = file_list;
//         if(this_list.length){
//             for(var i=0;i<this_list.length;i++){
//                 if($.inArray(this_list[i], order_type_list) > -1){
//                     order_type_list.splice($.inArray(this_list[i], order_type_list),1);
//                 }
//             }
//             if(order_type_list.length){
//                 alert("Please upload "+ order_type_list + " !");
//                 return
//             }
//         }else{
//             alert("Please upload the documents required by PCB or PCBA!");
//             return
//         }
//     });
// }


    $('.oe_cart').on('click', '.js_cpo_delete_product', function(e) {
        e.preventDefault();
        // $(this).closest('li').find('.cpo_js_quantity').val(0).trigger('change');
        $(this).parent().parent().parent().find('.cpo_js_quantity').val(0).trigger('change');
    });

    var clickwatch = (function(){
            var timer = 0;
            return function(callback, ms){
            clearTimeout(timer);
            timer = setTimeout(callback, ms);
            };
    })();
    
    var shopping_cart_link = $('ul#top_menu li a[href$="/shop/cart"]');
    var shopping_cart_link_counter;
    shopping_cart_link.popover({
        trigger: 'manual',
        animation: true,
        html: true,
        title: function () {
            return _t("My Cart");
        },
        container: 'body',
        placement: 'auto',
        template: '<div class="popover mycart-popover" role="tooltip"><div class="arrow"></div><h3 class="popover-title"></h3><div class="popover-content"></div></div>'

    });

    $(".oe_website_sale").off("change").on("change", ".oe_cart input.cpo_js_quantity[data-product-id]", function (e) {
        var $input = $(this);
        if ($input.data('update_change')) {
            return;
        }
        var value = parseInt($input.val() || 0, 10);
        if (isNaN(value)) {
            value = 1;
        }
        //var $dom = $(this).closest('tr');
        var $dom = $(this).closest('#cpo_website_ele_cart_order');
        //var default_price = parseFloat($dom.find('.text-danger > span.oe_currency_value').text());
        var $dom_optional = $dom.nextUntil(':not(.optional_product.info)');
        var line_id = parseInt($input.data('line-id'),10);
        var product_ids = [parseInt($input.data('product-id'),10)];
        clickwatch(function(){
        $dom_optional.each(function(){
            $(this).find('.cpo_js_quantity').text(value);
            product_ids.push($(this).find('span[data-product-id]').data('product-id'));
        });
        $input.data('update_change', true);
        var cpo_ELE_upload = cpo_ELE_Dialog;
        ajax.jsonRpc("/shop/cart/update_json", 'call', {
            'line_id': line_id,
            'product_id': parseInt($input.data('product-id'), 10),
            'set_qty': value
        }).then(function (data) {
            $input.data('update_change', false);
            var check_value = parseInt($input.val() || 0, 10);
            if (isNaN(check_value)) {
                check_value = 1;
            }
            if (value !== check_value) {
                $input.trigger('change');
                return;
            }

            $input.val(data.quantity);
            $('.cpo_js_quantity[data-line-id='+line_id+']').val(data.quantity).html(data.quantity);
            $('.oe_website_sale .js_cart_lines #cart_total').html(data['website_sale.total']);

            $('.cpo_js_quantity[data-line-id='+line_id+']').parents("#cpo_website_ele_cart_order:first").parent().html(data['website_sale.cart_lines']);

            $('.oe_electron_js_upload').on('click', function () {
                var order_id = $(this).attr('order_id');
                new cpo_ELE_upload(this, order_id).appendTo(document.body);
            });

        });
        }, 500);
    });

    $('#pcba_note').blur(function () {
        $('#cpo_pcb_note').val($(this).val());
    });

     $("#cpo_ele_excel_table_content input:checkbox").change(function () {
        if($(this).is(':checked')){
            $(this).attr('value','customer')
            // alert($(this).val())
        }else{
            $(this).attr('value','chinapcbone')
        }
    });

        // Go to top
     $(function () {
        $(window).scroll(function(){
            if ($(window).scrollTop()>100){
                $("#cpo_go_top").fadeIn(1000);
            }
            else
            {
                $("#cpo_go_top").fadeOut(1000);
            }
        });

        $("#cpo_go_top").click(function(){
            //$('body,html').animate({scrollTop:0},1000);
        if ($('html').scrollTop()) {
                $('html').animate({ scrollTop: 0 }, 500);
                return false;
            }
            $('body').animate({ scrollTop: 0 }, 500);
                 return false;
       });
     });

    //Express Number
    $('#cpo_express_no .express_btn').on('click', function () {
        var order_number = $('#modal_express .order_number').html();
        var express_company = $('#modal_express .express_company').val();
        var express_number = $('#modal_express .express_number').val();
        if(express_company == '' || express_number == ''){
            $('#express_form .express_company').css('border', '1px solid #db0700');
            $('#express_form .express_number').css('border', '1px solid #db0700');
            return
        }else{
            ajax.jsonRpc("/pcb_user_expressage", 'call', {
                'order_number': order_number,
                'express_company': express_company,
                'express_number': express_number,
            }).then(function (data) {
                if (data.error){
                    webAlert('Found repeat express number!', null, false);
                    // alert('Found repeat express number!');
                    return
                }
               location.reload();
            });
        }
    });
    // 分页器（个人中心）
    $(document).ready( function () {
        $('.get_express_table').DataTable({
            lengthChange: false, //
            "aaSorting": [[ 0, "desc" ]],
            searching : false, //去掉搜索
            "bProcessing" : true, //显示加载进度
            "bInfo" : false, //去掉底部文字
            "iDisplayLength" : 10, //每一页显示10条
            "bStateSave" : false, //
            "bJQueryUI" : true,
            "ordering": false,
            "bAutoWidth" : false,
        });
    });

    $('.cpo_address_order_title').on('click', function () {
        if($(this).hasClass('fa-plus')){
            $(this).addClass('fa-minus').removeClass('fa-plus');
            $(this).siblings('div.cpo_address_order_detail').addClass('cpo-block').removeClass('cpo-none');
        }else{
            $(this).addClass('fa-plus').removeClass('fa-minus');
            $(this).siblings('div.cpo_address_order_detail').addClass('cpo-none').removeClass('cpo-block');
        }
    });
    // $('#express_btn').click(function () {
    //     var order_number = $('#express_order_detail .order_number').html()
    //     var express_company = $('#express_order_detail .express_company').val()
    //     var express_number = $('#express_order_detail .express_number').val()
    //
    //     if(express_company == '' || express_number == ''){
    //         $('#express_form .express_company').css('border', '1px solid #db0700');
    //         $('#express_form .express_number').css('border', '1px solid #db0700');
    //         return
    //     }else{
    //         ajax.jsonRpc("/pcb_user_expressage", 'call', {
    //             'order_number': order_number,
    //             'express_company': express_company,
    //             'express_number': express_number,
    //         }).then(function (data) {
    //             if (data.error){
    //                 alert('Found repeat express number!');
    //                 return
    //             }
    //            location.reload();
    //         });
    //     }
    //
    // });
    // set order number
    $('.get_express_table .get_order_num').click(function () {
        $('#modal_express .order_number').html($(this).attr('id'));
    });
    //show delete button
    $('.express_ul li').mouseover(function () {
        $(this).children('a').css('visibility','visible')
    }).mouseout(function () {
        $(this).children('a').css('visibility','hidden')
    });
    // delete express
    $('.express_ul a.express_delect').click(function () {
        var express_no = $(this).prev().children('span').html()

        ajax.jsonRpc("/user_delete_express", 'call',{
            'express_no': express_no
        }).then(function (data) {
            $(this).parent().remove()
            location.reload()
        });

    });


    $('.cpo_bom_fields_ref').on("click", function(e){
        $(this).removeClass("cpo_check_red_error")
    });
    $('.oe_website_check_excel_file').on('click', '#cpo_update_bom_supply', function() {
        var self = $(this);
        self.vals = [];
        self.mfr_index = -1;
        self.mfr_title = $(".cpo_check_excel_set select.cpo_bom_mfr_pn").val();
        self.express_provider = $("#cpo_express_provider select[class='cpo_express_provider']").val();
        self.express_number = $("#cpo_express_number input[name='cpo_express_number']").val();
        self.bom_fields = []
        self.check_field_checked = false
        var fields_selction = $(".cpo_bom_fields_ref");
        _.each(fields_selction, function(e, index){
            if ($(e).val()){
                self.bom_fields.push({'src_title': $(e).val(), 'cpo_title': e.getAttribute('data-field_id')});
            }else if ($.inArray( e.id, [ 'cpo_bom_field_qty'] ) >= 0){
                $(e).addClass("cpo_check_red_error")
                self.check_field_checked = e.parentElement.innerText;
                return 
            }
        }, self);
        if (self.check_field_checked) {
            //alert("Manufacturer P/N and Quantityqty need select!");
            webAlert(self.check_field_checked + "need select!", null, false);
            // alert(self.check_field_checked + "need select!");
            return
        };
        var tb_head = $("#cpo_ele_excel_table_content").children("tbody").children("tr:first").find("td");
        _.each(tb_head, function(e, index){
            if (this.mfr_title == e.innerText){
                this.mfr_index = index;
            }
        }, self);
        var ele_supply = $(".cpo_pcba_ele_supply_select");
        _.each(ele_supply, function(e, index){
            if($(e).val() != 'chinapcbone' && this.mfr_index >= 0){
                var value = {};
                value.mfr = e.parentElement.parentElement.children[this.mfr_index].innerText;
                value.supply = $(e).val();
                if (value.mfr){
                    this.vals.push(value);
                }
            }
        }, self);
        ajax.jsonRpc("/pcb_electron/update_ele_supply", 'call', {
            'ref': self.vals,
            'field_ref': self.bom_fields,
            'atta_id': this.getAttribute('data-atta-id'),
            'express_provider': self.express_provider,
            'express_number': self.express_number,
        }).then(function (data) {
            this;
            self;
            if (self[0].getAttribute('data-return_url')){
               window.open(self[0].getAttribute('data-return_url'),"_self");
            }else{
               //window.open('/shop/cart',"_blank");
               window.open('/shop/cart',"_self");
            }
        });
    });
    /*
    * 订单支付
    * 1、全选
    * 2、支付按钮
    */
    // 全选
    $('#checkall_invoice').on('change', function () {
        $('.cpo_invoice_load').removeClass('cpo-none').addClass('cpo-block');
        if(this.checked == true){
            $('#cpo_get_invoice_ids input[type="checkbox"]').each2(function () {
                this.checked = true;
            })
            $("form#cpo_get_invoice_ids").submit();
        }else{
            $('#cpo_get_invoice_ids input[type="checkbox"]').each2(function () {
                this.checked = false;
            })
            $("form#cpo_get_invoice_ids").submit();
        }
    });

    $("form#cpo_get_invoice_ids").submit(function(e){
        var invoices = [];
        $("form#cpo_get_invoice_ids input[type='checkbox']:checked").each(function(e){
            invoices.push(this.name);
        });
        ajax.jsonRpc("/get_invoices", 'call', {
            'invoices': invoices
        }).then(function(data){
            if(data.error != ''){
                $('#invoice_total .price-currency').html(data.currency);
                $('#invoice_total .price-amount').html(data.total_amount);
                $('#get_invoice_pay .invoices_name_ids').empty();
                $.each(data.invoices,function (inKey, inVal) {
                    $('#get_invoice_pay .invoices_name_ids').append('<input type="hidden" name="'+inKey+'" value="'+inVal+'"/>');
                })
                $('.cpo_invoice_load').removeClass('cpo-block').addClass('cpo-none');
            }
        });
    });
    $("form#cpo_get_invoice_ids input[type='checkbox']").on('change',function () {
        $('.cpo_invoice_load').removeClass('cpo-none').addClass('cpo-block');
        $("form#cpo_get_invoice_ids").submit();
    });
    $('#cpo_invoice_pay').on('click', function () {
        $('#get_invoice_pay').submit();
    });
    //---------------------------------------------------------
    $('#cpo_ele_cart_att .cpo_down_file').on('click',function () {
        var atta_id = $(this).siblings('form').find('input[name="atta_id"]').val();
        $(this).parent().submit();
        // ajax.jsonRpc('/down/file', 'call',{
        //     'atta_id': atta_id
        // }).then(function (data) {
        //     window.open('/down/file/download?attachment_id='+data,'_blank');
        // });
    });
    // $("form#down_file_form").submit(function(e){
    //     var files = [];
    //     var attachment_id = $(this).siblings('form').find('input[name="atta_id"]').val();
    //
    //     ajax.jsonRpc("/down/file", 'call', {
    //         'attachment_id':attachment_id,
    //     }).then(function (data){
    //         window.open('/shop/cart/download?attachment_id='+data,'_blank');
    //     })
    //     e;
    // });

    //
    $(document).ready(function () {
        // 当小于等于10条数据时不显示分页
        var badge = $("#cpo_my_home_account .badge");
        for(var i=0;i<badge.length;i++){
            if(i <= badge.length-1){
                var badge_val = badge[i].innerHTML;
                var badge_select = badge[i].parentElement.parentElement.parentElement.nextElementSibling.querySelector(".dataTables_paginate");
                if(badge_val <= 10 && badge_select){
                    badge_select.style.display = "none";
                }
            }
        }
    });
    // 选择地址时，让客户确认是否选择到付
    $('#shop_confirm_order').on('click', function () {
        var select = $("#cpo_delivery_methods .methods_chinapcbone").find(".cpo-select");
        var tracking_number = $("#tracking_number .tracking_number");
        if(select.length < 1){
            webAlert("Please choose the express way !", null, false);
            // alert("Please choose the express way !");
            $('body,html').animate({scrollTop: $('#cpo_delivery_methods').offset().top}, 500);
            return false;
        }else if(!tracking_number.val()){
            var select_val = $("#cpo_delivery_methods .methods_chinapcbone").find(".cpo-select").next().text();
            if(select_val.trim() == "By customer's account"){
                // alert("Please fill in the account information !");
                webAlert("Please fill in the account information !", null, false);
                tracking_number.focus();
                $('body,html').animate({scrollTop: $('#cpo_delivery_methods').offset().top}, 500);
                return false;
            }
        }
    });

    // 选择地址时，确认收货方式：到付，在线支付
    $('#cpo_delivery_methods .methods_select .cpo-circle-btn').on('click', function () {
        svgBlockNone($('.svg_loading'), 'block');
        $(this).addClass('cpo-select');
        $(this).parent('p').siblings('p').find('span.cpo-circle-btn').removeClass('cpo-select');
        var sele_val = $(this).siblings('span').html();
        var express_sele = $('#express_select');
        var tracking_number = $('#tracking_number');
        var supply_method = 'no';
        var express_number = tracking_number.find('input').val();
        if(sele_val == "By customer's account"){
            // express_sele.addClass('cpo-block').removeClass('cpo-none');
            tracking_number.css('display', 'inline-block');
            supply_method = 'yes';
        }else{
            tracking_number.find('input').val('');
            tracking_number.css('display', 'none');
            express_number = '';
        }
        var express_select = express_sele.find('select').val();
        ajax.jsonRpc("/customer/select/express", "call", {
            'cpo_supply_method': supply_method,
            'cpo_express_select': express_select,
            'express_number': express_number,
        }).then(function (data) {
            $('#cpo_coupon_use_page').html(data.cpo_checke_express);
        })
        svgBlockNone($('.svg_loading'), 'none');
    });
    // 选择快递方式（收货地址）
    $('#express_select .methods_exepress').on('change', function () {
        svgBlockNone($('.svg_loading'), 'block');
        var supply_method = 'no';
        var supply_method_val = $('#cpo_delivery_methods .methods_select .cpo-select').siblings('span').html();
        if(supply_method_val == "By customer's account"){
            supply_method = 'yes';
        }
        var cpo_express_select = $(this).val();
        var express_number = $('#tracking_number').find('input').val();
        ajax.jsonRpc("/customer/select/express", "call", {
            'cpo_supply_method': supply_method,
            'cpo_express_select': cpo_express_select,
            'express_number': express_number,
        }).then(function (data) {

        })
        svgBlockNone($('.svg_loading'), 'none');
    });
    // 填写快递单号（收货地址）
    $('#tracking_number .tracking_number').on('blur', function () {
        svgBlockNone($('.svg_loading'), 'block');
        var supply_method = 'no';
        var supply_method_val = $('#cpo_delivery_methods .methods_select .cpo-select').siblings('span').html();
        if(supply_method_val == "By customer's account"){
            supply_method = 'yes';
        }
        var express_sele = $('#express_select').find('select').val();
        var express_number = $(this).val();
        ajax.jsonRpc("/customer/select/express", "call", {
            'cpo_supply_method': supply_method,
            'cpo_express_select': express_sele,
            'express_number': express_number,
        }).then(function (data) {

        })
        svgBlockNone($('.svg_loading'), 'none');
    });

    /*
    * 个人中心，点击展开列表，变成减号，反之加号
    *
    */
    $('#cpo_my_home_account .panel-heading').on('click', function () {
        if($(this).hasClass('collapsed')){
            $(this).find('h4.panel-title').children('i').removeClass('fa-plus').addClass('fa-minus');
            $(this).parent().siblings().find('h4.panel-title').children('i').removeClass('fa-minus').addClass('fa-plus');
        }else{
            $(this).find('h4.panel-title').children('i').removeClass('fa-minus').addClass('fa-plus');
        }
    });
    $('#cpo_express_no .panel-heading').on('click', function () {
        if($(this).hasClass('collapsed')){
            $(this).find('h4.panel-title').children('i').removeClass('fa-plus').addClass('fa-minus');
            $(this).parent().siblings().find('h4.panel-title').children('i').removeClass('fa-minus').addClass('fa-plus');
        }else{
            $(this).find('h4.panel-title').children('i').removeClass('fa-minus').addClass('fa-plus');
        }
    });

    /*
    * 快递信息分类
    * 快递信息填写
    * 快递信息查看
    * */
    $('.cpo_express_title .cpo_express_li').on('click', function () {
        $(this).addClass('cpo_express_active').siblings('li').removeClass('cpo_express_active');

        $('.cpo_express_content li.cpo_express_cont').eq($(this).index()).addClass('cpo-block').removeClass('cpo-none');
        $('.cpo_express_content li.cpo_express_cont').eq($(this).index()).siblings('li').addClass('cpo-none').removeClass('cpo-block');
        // var express_ac = $(this).hasClass('cpo_express_active');
        // if(express_ac){

        //     $(this).removeClass('cpo_express_active').siblings('li').addClass('cpo_express_active');
        // }
    })



    //index button On top
    // var cpo_btnH = $('#panel_btn').offset().top;
    // $(window).scroll(function(){
    //     var scroH = $(this).scrollTop();
    //     if(scroH>cpo_btnH){
    //         $('#panel_btn').css({"position":"fixed","top":'0', 'left': '50%','background-color': '#ffffff','z-index':'999','width':'1170px','margin-left':'-585px'});
    //     }else{
    //         $('#panel_btn').css({"position":"static","margin": "auto auto",'z-index':'0'})
    //     }
    // });

    // 弹窗函数
    function webAlert(str, click, useCancel){
        var $hidder=null;
        var clickHandler=click||$.noop;
        var myClickHandler=function(){
            $hidder.remove();
            clickHandler($(this).html()=="Confirm");
        };
        var init=function(){
            $hidder = $("<div class='web-alert'></div>");
            var $myalert = $("<div class='web-box'>"+
                "<div class='web-tips'>Tips</div></div>")
                .appendTo($hidder);
            $("<div class='web-content'>"+str+"</div>").appendTo($myalert);
            var $myalert_btn_div = $("<div style='padding-top:10px;'></div>").appendTo($myalert);

            var $okBtn = $("<div class='bluebg1 web-btn-cf'>Confirm</div>").appendTo($myalert_btn_div).click(myClickHandler);

            if(useCancel){
                $("<div class='web-btn-cc'>Cancel</div>").appendTo($myalert_btn_div).click(myClickHandler);
            }
            $("body").append($hidder);
        };
        init();
    }


})
odoo.define('website_sale.cart', function (require) {
    "use strict";

    var base = require('web_editor.base');
    var core = require('web.core');
    var _t = core._t;

    var shopping_cart_link = $('ul#top_menu li a[href$="/shop/cart"]');
    var shopping_show = $('ul#top_menu li:last-child ul.dropdown-menu');
    var shopping_cart_link_counter;
    if(shopping_show.length > 0){
        shopping_cart_link.popover({
            trigger: 'manual',
            // animation: true,
            html: true,
            title: function () {
                return _t("My Cart");
            },
            container: 'body',
            placement: 'auto',
            template: '<div class="popover mycart-popover" role="tooltip"><div class="arrow"></div><h3 class="popover-title"></h3><div class="popover-content"></div></div>'
        }).on("mouseenter",function () {
            var self = this;
            clearTimeout(shopping_cart_link_counter);
            shopping_cart_link.not(self).popover('hide');
            shopping_cart_link_counter = setTimeout(function(){
                if($(self).is(':hover') && !$(".mycart-popover:visible").length)
                {
                    $.get("/shop/cart", {'type': 'popover'})
                        .then(function (data) {
                            $(self).data("bs.popover").options.content =  data;
                            $(self).popover("show");
                            $(".popover").on("mouseleave", function () {
                                $(self).trigger('mouseleave');
                            });
                        });
                }
            }, 300);
        }).on("mouseleave", function () {
            var self = this;
            setTimeout(function () {
                if (!$(".popover:hover").length) {
                    if(!$(self).is(':hover')) {
                       $(self).popover('hide');
                    }
                }
            }, 100);
        });
    }else {
        shopping_cart_link.popover({
            trigger: 'manual',
            // animation: true,
            html: true,
            title: function () {
                return _t("My Cart");
            },
            container: 'body',
            placement: 'auto',
            template: '<div class="popover mycart-popover" role="tooltip"><div class="arrow"></div><h3 class="popover-title"></h3><div class="popover-content"></div></div>'
        }).on("mouseenter",function () {
            var self = this;
            clearTimeout(shopping_cart_link_counter);
        }).on("mouseleave", function () {
            var self = this;
            setTimeout(function () {
                if (!$(".popover:hover").length) {
                    if(!$(self).is(':hover')) {
                       $(self).popover('hide');
                    }
                }
            }, 100);
        });
    }
});
odoo.define('website_cpo_sale.cpo_login', function (require) {
    "use strict";

    var base = require('web_editor.base');
    var core = require('web.core');
    var _t = core._t;

    var shopping_cart_link = $('ul#top_menu li:last-child a');
    var shopping_show = $('ul#top_menu li:last-child ul.dropdown-menu');
    var shopping_cart_link_counter;
    shopping_cart_link.popover({
        trigger: 'manual',
        // animation: true,
        html: true,
        title: function () {
            return _t("Welcome to Chinapcbone");
        },
        container: 'body',
        placement: 'auto',
        template: '<div class="popover cpoLogin-popover" role="tooltip" data-placement="bottom"><div class="arrow"></div><h3 class="popover-title"></h3><div class="popover-content"></div></div>'
    }).on("mouseenter",function () {
        var self = this;
        clearTimeout(shopping_cart_link_counter);
        shopping_cart_link.not(self).popover('hide');
        if(shopping_show.length <= 0){
            shopping_cart_link_counter = setTimeout(function(){
                if($(self).is(':hover') && !$(".mycart-popover:visible").length)
                {
                    $(self).data("bs.popover").options.content =  '<div class="signin_signup hidden-xs">\n' +
                        '                <a class="btn btn-primary" style="padding: 5px 15px;margin: 5px 0;" href="/web/login">Sign in</a><br>\n' +
                        '                <span>\n' +
                        '                    New Customer?\n' +
                        '                    <a class="" href="/web/signup">Start Here</a>\n' +
                        '                </span>\n' +
                        '            </div>';
                    $(self).popover("show");
                    $(".popover").on("mouseleave", function () {
                        $(self).trigger('mouseleave');
                    });
                }
            }, 300);
        }
    }).on("mouseleave", function () {
        var self = this;
        setTimeout(function () {
            if (!$(".popover:hover").length) {
                if(!$(self).is(':hover')) {
                   $(self).popover('hide');
                }
            }
        }, 100);
    });
});
