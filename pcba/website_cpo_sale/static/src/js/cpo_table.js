odoo.define("website_cpo_sale.electron_first_table", function(require) {
    "use strict";

    new WOW().init();
    // $(function () { $("#jisuan_click[data-toggle='tooltip']").tooltip(); });


    var base = require('web_editor.base');
    var ajax = require("web.ajax");
    var core = require('web.core');
    var config = require("web.config");
    var _t = core._t;
    $('#sele_btn input').click(function(){
        $(this).addClass('in_active').siblings('input').removeClass('in_active')
    
    });
    $(function(){
        $("img.img").lazyload({
            skip_invisible : false
        });
    })

    $(".oe_pcb_upload_smt_file input[type='file']").change(function(e){
        var self = this,
            file = e.target.files[0],
            is_image = /^image\/.*/.test(file.type),
            loaded = false;
        var file_name = file.name;
        var file_type = file.type;
        //var shuliang = $('#xiangqing .shuliang').val()
            //var reader = new FileReader();
            //reader.readAsText(e.target.files[0], "UTF-8");//读取文件 
            //reader.onload = function(evt){ //读取完文件之后会回来这里
                //var fileString = evt.target.result;
                ////form.vm.value = fileString; //设置隐藏input的内容
            //}

        var BinaryReader = new FileReader();
        // file read as DataURL
        BinaryReader.readAsDataURL(e.target.files[0]);
        BinaryReader.onloadend = function (upload) {
            var buffer = upload.target.result;
            if ('is_image') {
                $("#slide-image").attr("src", buffer);
            }
            buffer = buffer.split(',')[1];

        ajax.jsonRpc("/pcb_electron/upload_file", 'call', {
            //'file': e.target.files[0].valueOf(),
            'file': buffer,
            })
       .then(function (data){
            sl.html(data.shuliang);
        });
            //self.file.data = buffer;
        };

    });
    // calculate SMT
    var add_detail = $('#click_details')
    var xiangqing_input = $('#xiangqing input');
    xiangqing_input.change(function () {
        $('#click_details').css('display', 'none');
    });
    xiangqing_input.blur(function () {
        var cpo_pd_smt = $(this).parent().siblings('label').text();
        if(cpo_pd_smt == "*SMT parts quantity" && ($(this).val()==0 || $(this).val() == '')){
            $(this).css('border', '1px solid #ccc');
        }else if($(this).val()== 0 || $(this).val()== '' ){
            $(this).css('border', '1px solid red');
            $(this).val("");
        }else{
            $(this).css('border', '1px solid #ccc');
        }
    });
    //regular
    $('#xiangqing .re_change').change(function () {
        var val_change = $(this).val();
        var trans_val = parseFloat(val_change);
        if (isNaN(trans_val)){
            trans_val = ''
        }
        $(this).val(trans_val)

    });


    var check_input_func = function(all_input){
        //if (1==1){return false}
        var check=true;
        xiangqing_input.each(function(e){
            var cpo_pd_smt = $(this).parent().siblings('label').text();
            if(this.type == 'hidden'){
            }else if(cpo_pd_smt == "*SMT parts quantity" && ($(this).val()==0 || $(this).val() == '')){
                $(this).css('border', '1px solid #ccc');
            }else if($(this).val()== '' || $(this).val() == 0 ){
                $(this).val("");
                $(this).css({'border':'1px solid red'});
                check = false;
            }
        });
        return check
    };

    $('#xiangqing .ele_pcb_wh input').change(function () {
        var pcb_length = $('#xiangqing .pcb_length').val();
        var pcb_breadth = $('#xiangqing .pcb_breadth').val();
        if($(this).val() <= 50){
            $('#ele_result #jig_fee_tatol').removeClass('jig_fee_class');
            $('#cpo_detail_result #detail_jig_fee').css("display", "block");
            $('#xiangqing #hint_lenght').css("display", "block");
        }else if($(this).val() > 1100){
            $('#ele_result #jig_fee_tatol').addClass('jig_fee_class');
            $('#cpo_detail_result #detail_jig_fee').css("display", "none");
            $('#xiangqing #hint_lenght_max').css("display", "block");
        }else if($(this).val() > 410){
            $('#ele_result #jig_fee_tatol').addClass('jig_fee_class');
            $('#cpo_detail_result #detail_jig_fee').css("display", "none");
            $('#xiangqing #hint_lenght_max').css("display", "block");
        }else if($(this).val()==0){
            // $('#ele_result #jig_fee_tatol').addClass('jig_fee_class');
            $(this).css({'border':'1px solid red'});
            $(this).val("");
            $('#cpo_detail_result #detail_jig_fee').css("display", "none");
            $('#xiangqing #hint_lenght').css("display", "none");
        }else if($(this).val()==''){
            // $('#ele_result #jig_fee_tatol').addClass('jig_fee_class');
            $(this).css({'border':'1px solid red'});
            $(this).val("");
            $('#cpo_detail_result #detail_jig_fee').css("display", "none");
            $('#xiangqing #hint_lenght').css("display", "none");
        }else{
            $('#cpo_detail_result #detail_jig_fee').css("display", "none");
            $('#xiangqing #hint_lenght').css("display", "none");
            $('#xiangqing #hint_lenght_max').css("display", "block");
        }
    });

    //btn bgc
    $('#cpo_position_top a').mouseover(function () {
        $(this).css({'background': 'none','background-color': '#1C86EE'});
    }).mouseout(function () {
        if($(this).html() == 'PCBA'){
            $(this).css({'background':'url("/website_cpo_sale/static/src/images/pcba_bg1.png")','background-color': 'none'});
        }else if($(this).html() == 'Electronic Parts'){
            $(this).css({'background':'url("/website_cpo_sale/static/src/images/ele_bg2.png")','background-color': 'none'});
        }else if($(this).html() == 'PCB'){
            $(this).css({'background':'url("/website_cpo_sale/static/src/images/pcb_bg1.png")','background-color': 'none'});
        }
    });


    var inputs_list = $('#jisuan_click');
    inputs_list.click(function(){
        var shuliang = $('#xiangqing .shuliang').val();
        var bom_num = $('#xiangqing .bom_type').val();
        var wel_com = $('#xiangqing .wel_com').val();
        var smt_num = $('#xiangqing .smt_num').val();
        // var ic_num = $('#xiangqing .ic_num').val();
        // var bw_num = $('#xiangqing .bw_num').val();
        var mian_one = $('#xiangqing .mian_one').val();
        var in_active1 = $('#xiangqing .pcb_sele_one').val();
        var in_active2 = $('#xiangqing .pcb_sele_two').val();
        var pcb_length = $('#xiangqing .pcb_length').val();
        var pcb_breadth = $('#xiangqing .pcb_breadth').val();
        var pcb_thickness = $('#xiangqing .pcb_thickness').val();
        var pcb_copper = $('#xiangqing .pcb_copper').val();
        var cpo_select_value = $('#xiangqing #cpo_select_value').val();

        // var res = check_input_func(inputs_list);
        if(check_input_func(inputs_list) == false){
            add_detail.css('display', 'none')
            return false
        }
        else {

            add_detail.css('display', 'block')

            var sl = $('#jisuan_one .shuliang')
            var bom = $('#jisuan_one .bom_type')
            var wel = $('#jisuan_one .wel_com')
            var smt = $('#jisuan_one .smt_num')
            // var ic = $('#jisuan_one .ic_num')
            // var bw = $('#jisuan_one .bw_num')
            var mian = $('#jisuan_one .mian_one')
            var active1 = $('#jisuan_one .pcb_pro')
            var active2 = $('#jisuan_one .ms_supply')
            var pcb_len = $('#jisuan_one .pcb_len')
            var pcb_bread = $('#jisuan_one .pcb_bread')
            var thickness = $('#jisuan_one .pcb_thickness')
            var copper = $('#jisuan_one .pcb_copper')
            var pcb_special = $('#jisuan_one .pcb_special')
            var result_pcs = $('#ele_result .result_pcs')
            var price_val = $('#ele_result .price_one')
            var tatol = $('#ele_result .result_1')
            var tatol2 = $('#ele_result .result_2')
            var stencil = $('#ele_result .stencil_result')
            var jig = $('#ele_result .jig_result')
            var e_test = $('#ele_result .e_test_result')


            ajax.jsonRpc("/get_pcba_price", 'call', {
                'ele_shuliang': shuliang,
                'ele_bom_sl': bom_num,
                'ele_wel_com': wel_com,
                'ele_smt_num': smt_num,
                // 'ele_ic_num': ic_num,
                // 'ele_bw_num': bw_num,
                'ele_mian_one': mian_one,
                'ele_in_active1': in_active1,
                'ele_in_active2': in_active2,
                'ele_pcb_length': pcb_length,
                'ele_pcb_breadth': pcb_breadth,
                'ele_pcb_thickness': pcb_thickness,
                'ele_pcb_copper': pcb_copper,
                'cpo_select_value': cpo_select_value,
            })
            .then(function (data) {
                sl.val(data.ele_shuliang);
                sl.siblings("a:first").text(data.ele_shuliang);
                bom.val(data.ele_bom_sl);
                bom.siblings("a:first").text(data.ele_bom_sl);
                wel.val(data.ele_wel_com);
                wel.siblings("a:first").text(data.ele_wel_com);
                smt.val(data.ele_smt_num);
                smt.siblings("a:first").text(data.ele_smt_num);
                // ic.val(data.ele_ic_num);
                // ic.siblings("a:first").text(data.ele_ic_num);
                // bw.val(data.ele_bw_num);
                // bw.siblings("a:first").text(data.ele_bw_num);
                mian.val(data.ele_mian_one);
                mian.siblings("a:first").text(data.ele_mian_one);
                active1.val(data.ele_in_active1);
                active1.siblings("a:first").text(data.ele_in_active1);
                active2.val(data.ele_in_active2);
                active2.siblings("a:first").text(data.ele_in_active2);
                result_pcs.val(data.ele_shuliang);
                result_pcs.siblings("a:first").text(data.ele_shuliang);
                tatol.val(data.smt_assembly_fee);
                tatol.siblings("a:first").text(data.smt_assembly_fee);
                // e_test.val(data.test_tool_fee);
                // e_test.siblings("a:first").text(data.test_tool_fee);
                tatol2.val(data.ele_tatol);
                tatol2.siblings("a:first").text(data.ele_tatol);
                price_val.val(data.process_price);
                price_val.siblings("a:first").text(data.process_price);
                pcb_len.val(data.ele_pcb_length);
                pcb_len.siblings("a:first").text(data.ele_pcb_length);
                pcb_bread.val(data.ele_pcb_breadth);
                pcb_bread.siblings("a:first").text(data.ele_pcb_breadth);
                thickness.val(data.ele_pcb_thickness);
                thickness.siblings("a:first").text(data.ele_pcb_thickness);
                copper.val(data.ele_pcb_copper);
                copper.siblings("a:first").text(data.ele_pcb_copper);
                pcb_special.val(data.cpo_select_value);
                pcb_special.siblings("a:first").text(data.cpo_select_value);

                stencil.val(data.stencil_fee);
                stencil.siblings("a:first").text(data.stencil_fee);
                jig.val(data.jig_tool_fee);
                jig.siblings("a:first").text(data.jig_tool_fee);

            });
        };
    });


    $("#cpo_fixed #cpo_all_check").on('click', function() {
        $("#testest input:checkbox").prop("checked", $(this).prop('checked'));
        var order_id_ls = []
        $('#testest input[type=checkbox]:checked').each(function () {
            order_id_ls.push($(this).attr('id'));
        })
        if($(this).is(':checked')){
            var lineID = [];
            var input_order_select = $("#testest input:checkbox");
            for(var i=0;i<input_order_select.length;i++){
                lineID.push(input_order_select[i].id);
            }
            ajax.jsonRpc('/shop/cart/cpo_checked', 'call', {
                'checked': 'true',
                'cpo_lineID': lineID,
                'order_id_ls': order_id_ls,
            }).then(function (data) {
                $('#order_total').html(data.order_total_temp)
            });
        }else{
            var lineID = [];
            var input_order_select = $("#testest input:checkbox");
            for(var i=0;i<input_order_select.length;i++){
                lineID.push(input_order_select[i].id);
            }
            ajax.jsonRpc('/shop/cart/cpo_checked', 'call', {
                'checked': 'false',
                'cpo_lineID': lineID,
                'order_id_ls': order_id_ls,
            }).then(function (data) {
                 $('#order_total').html(data.order_total_temp)
            });
        }
    })

    $("#testest input:checkbox").on('click', function() {
        if($("#testest input:checkbox").length === $("#testest input:checked").length) {
            $("#cpo_all_check").prop("checked", true);
        } else {
            $("#cpo_all_check").prop("checked", false);
        }
        var order_id_ls = []
        $('#testest input[type=checkbox]:checked').each(function () {
            order_id_ls.push(this.id);
        })
        $(this).each(function () {
            var cpo_lineID = $(this).context.id
            if($(this).prop('checked')) {
                ajax.jsonRpc('/shop/cart/cpo_checked', 'call', {
                    'checked': 'true',
                    'cpo_lineID': cpo_lineID,
                    'order_id_ls': order_id_ls,
                }).then(function (data) {
                    if(data.checked == 'checked'){
                        $(this).attr('checked',true)
                    }
                    $('#order_total').html(data.order_total_temp)
                });
            }else{
                ajax.jsonRpc('/shop/cart/cpo_checked', 'call', {
                    'checked': 'false',
                    'cpo_lineID': cpo_lineID,
                    'order_id_ls': order_id_ls,
                }).then(function (data) {
                    if(data.checked == 'checked'){
                        $(this).attr('checked',false)
                    }
                    $('#order_total').html(data.order_total_temp)
                });
            }
        });

    })


    $('#cpo_go_right p a').mouseover(function () {
        $(this).addClass('cpo_a_btn_hover')
    }).mouseout(function () {
        $(this).removeClass('cpo_a_btn_hover')
    });

    //On bottom
    $(document).ready(function() {
        var browserH = $(document.body).height();
        var footH = -1;
        if ($("#cpo_calculate_tatol").offset()){
            var footH = $("#cpo_calculate_tatol").offset().top;
            if( footH > browserH){
                $("#cpo_calculate_tatol").addClass('calculate_tatol');
                $("#cpo_calculate_tatol #cpo_fixed").removeClass('col-md-12').addClass('col-md-12')
                $("#cpo_calculate_tatol #cpo_col_width").addClass('col-md-1')
                getConditionsContent()
            }
            $(window).scroll(function(){
                var scroH = $(this).scrollTop();
                if((scroH+browserH) < footH){
                    $("#cpo_calculate_tatol").addClass('calculate_tatol');
                    $("#cpo_calculate_tatol #cpo_fixed").removeClass('col-md-12').addClass('col-md-12')
                    $("#cpo_calculate_tatol #cpo_col_width").addClass('col-md-1')
                }
                else if((scroH+footH) >= footH){
                    $("#cpo_calculate_tatol").css({"position":"static"}).removeClass('calculate_tatol');
                    $("#cpo_calculate_tatol #cpo_col_width").removeClass('col-md-1')
                    $("#cpo_calculate_tatol #cpo_fixed").addClass('col-md-12').removeClass('col-md-12')
                }
                getConditionsContent()
            })


        }

    });
    // 协议点击和订单选择一起存在时，避免重叠
    function getConditionsContent(){
        var terms_conditions = $('.terms_conditions');
        var calculate_tatol = $('.calculate_tatol');
        var t_display = terms_conditions.css('display');
        if(terms_conditions.length > 0){
            if(t_display == 'block'){
                calculate_tatol.css('bottom', terms_conditions.height());
            }else{
                calculate_tatol.css('bottom', '0');
            }
        }
    }

    ajax.jsonRpc('/advertising/billboard/', 'call', {
        'number': 1,
    }).then(function (data) {
        var cpo_time
        $("#cpo_advertising_con").html(data.ad_content)
        $('#cpo_close_btn').click(function () {
            $(this).parent().css('display', 'none')
        });
    });

    $('#create_price_compar').click(function (e) {
        // event.stopPropagation();
        e.stopPropagation();
        if($('#cpo_price_compar_com').css('display')=='block'){
            $('#cpo_price_compar_com').css('display', 'none');
            $('#cpo_price_compar_com table tr.cpo_try_content').remove();
        }else{
            $('#cpo_price_compar_com').css('display', 'block');
            var first_tr = $('#cpo_price_compar_com table input.cpo_quantity_val').first();
            if(first_tr.length <= 0){
                $('#cpo_price_compar_com table').append("<tr>\n" +
                "<td><input type=\"radio\" class=\"cpo_choose\" name=\"item\"/></td>\n" +
                "<td><input type=\"text\" class=\"cpo_quantity_val\"/></td>\n" +
                "<td><i>$</i><span class=\"price_total\"></span></td>\n" +
                "<td><a class=\"delete_price_compar\"><i class=\"fa fa-trash\"></i></a></td>\n"+
                "</tr>");
            }else{
                if(!$('#cpo_price_compar_com table input').first().attr('checked')=='checked'){
                    $('#cpo_price_compar_com table input').first().attr("checked", 'checked');
                }

            }
            $('#cpo_price_compar_com table input.cpo_quantity_val').first().val($('#pcb_details .shuliang').html());
            $('#cpo_price_compar_com table span.price_total').first().html($('#cpo_detail_result .smt_price_total').html());
        }

    });
   $('#cpo_create_compar').click(function () {
       var first_tr = $('#cpo_price_compar_com table input.cpo_quantity_val').first();
        if(first_tr.length > 0){
            $('#cpo_price_compar_com table').append("<tr class=\"cpo_try_content\">\n" +
            "<td><input type=\"radio\" class=\"cpo_choose\" name=\"item\"/></td>\n" +
            "<td><input type=\"text\" class=\"cpo_quantity_val\"/></td>\n" +
            "<td><i>$</i><span class=\"price_total\"></span></td>\n" +
            "<td><a class=\"delete_price_compar\"><i class=\"fa fa-trash\"></i></a></td>\n"+
            "</tr>");
            $("#cpo_price_compar_com table tr:last input").focus();
        }else{
            $('#cpo_price_compar_com table').append("<tr>\n" +
            "<td><input type=\"radio\" class=\"cpo_choose\" name=\"item\"/></td>\n" +
            "<td><input type=\"text\" class=\"cpo_quantity_val\"/></td>\n" +
            "<td><i>$</i><span class=\"price_total\"></span></td>\n" +
            "<td><a class=\"delete_price_compar\"><i class=\"fa fa-trash\"></i></a></td>\n"+
            "</tr>");
            $("#cpo_price_compar_com table tr:last input").focus();
        }

   });
   $('#cpo_close_compar').click(function () {
       $('#cpo_price_compar_com table tr.cpo_try_content').remove();
       $('#cpo_price_compar_com').css('display', 'none');
   });

    $('#cpo_price_compar_com table').on('click', 'a.delete_price_compar', function (e) {
        e.stopPropagation();
        $(this).parent('td').parent('tr').remove();
    });
    $('#cpo_price_compar_com table').on('change', 'input.cpo_quantity_val', function (e) {
        // event.preventDefault();
        e.stopPropagation();
        var e = e||event;
        $(document).keyup(function(event){
            if(e.handled !== true){
                if(event.keyCode ==13){
                    $('#cpo_price_compar_com table').append("<tr class=\"cpo_try_content\">\n" +
                        "<td><input type=\"radio\" class=\"cpo_choose\" name=\"item\"/></td>\n" +
                        "<td><input type=\"text\" class=\"cpo_quantity_val\"/></td>\n" +
                        "<td><i>$</i><span class=\"price_total\"></span></td>\n" +
                        "<td><a class=\"delete_price_compar\"><i class=\"fa fa-trash\"></i></a></td>\n"+
                        "</tr>");
                    $("#cpo_price_compar_com table tr:last input").focus();
                }
                e.handled = true;
            }

        });

        var shuliang = $(this).val();
        var wel_com = $('#pcb_details .dip_gs').html();
        var smt_num = $('#pcb_details .smt_geshu').html();
        var mian_one = $('#pcb_details .cengshu').html();
        var pcb_length = $('#pcb_details .ic_geshu').html();
        var pcb_breadth = $('#pcb_details .houhan_gs').html();
        var cpo_special = $('#pcb_details .teshuxuqiu').html();
        var price_total = $(this).parent().siblings().children('span.price_total');
        var price_smt = $(this).parent().siblings().children('input.cpo_smt_val');

        ajax.jsonRpc("/get_pcba_price", 'call', {
                'ele_shuliang': shuliang,
                'ele_wel_com': wel_com,
                'ele_smt_num': smt_num,
                'ele_mian_one': mian_one,
                'ele_pcb_length': pcb_length,
                'ele_pcb_breadth': pcb_breadth,
                'cpo_select_value': cpo_special,
        }).then(function (data) {
            price_total.html(data.ele_tatol);
        });


    });

     $('#cpo_price_compar_com table').on('click', 'input:radio', function () {

        var shuliang = $(this).parent().siblings().children('input.cpo_quantity_val').val();
        var wel_com = $('#pcb_details .dip_gs').html();
        var smt_num = $('#pcb_details .smt_geshu').html();
        var mian_one = $('#pcb_details .cengshu').html();
        var pcb_length = $('#pcb_details .ic_geshu').html();
        var pcb_breadth = $('#pcb_details .houhan_gs').html();
        var cpo_special = $('#pcb_details .teshuxuqiu').html();
        // $(this).attr('checked', 'checked').siblings('input[type=radio]').removeAttr('checked');
        if(shuliang){
             ajax.jsonRpc("/get_pcba_price", 'call', {
                'ele_shuliang': shuliang,
                'ele_wel_com': wel_com,
                'ele_smt_num': smt_num,
                'ele_mian_one': mian_one,
                'ele_pcb_length': pcb_length,
                'ele_pcb_breadth': pcb_breadth,
                'cpo_select_value': cpo_special,
            }).then(function (data) {

                $('#pcb_details .shuliang').html(data.ele_shuliang);
                $('#cpo_detail_result .smt_price_cost').html(data.smt_assembly_fee);
                $('#cpo_detail_result .smt_price_total').html(data.ele_tatol);
                $('#cpo_change_quantity').val(data.ele_shuliang);
            });
        }else{

        }


    });

    //图片预加载
    $('.o_chat_window_close').on(function () {
        $('body .openerp').attr('')
    });





} );

