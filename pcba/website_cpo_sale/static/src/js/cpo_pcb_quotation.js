odoo.define("website_cpo_sale.pcb_queto_online", function(require) {
    "use strict";

    var Widget = require('web.Widget');
    var base = require('web_editor.base');
    var ajax = require("web.ajax");
    var core = require('web.core');
    var config = require("web.config");



    // PCB 价格明细
    // $('.board_price').mouseover(function () {
    //     $('.cpo_pcb_all_fee').css('display', 'block');
    // }).mouseout(function () {
    //     $('.cpo_pcb_all_fee').css('display', 'none');
    // });

    //点击进入下一步确认订单
    $('#pcb_details_btn').click(function () {
        var $form = $('form[id="cpo_pcb_result"]');
        $form.submit();
    });


        // PCB 特殊数据获取
    var pcb_special_form = $('form.special_form');
    function pcbSpecialForm(){
        var pcb_special_value;
        var Semi_hole = $('form.special_form select.special_semi_hole').val();
        var Edge_plating = $('form.special_form select.special_edge_plating').val();
        var Impedance = $('form.special_form select.special_impedance').val();
        var Press_fit = $('form.special_form select.special_press_fit').val();
        var Peelable_mask = $('form.special_form select.special_peelable_mask').val();
        var Carbon_oil = $('form.special_form select.pcb_carbon_ink').val();
        var Min_line_width = $('form.special_form input.special_minimum_line').val();
        var Min_line_space = $('form.special_form input.special_line_space').val();
        var Min_aperture = $('form.special_form input.special_minimum_aperture').val();
        var Total_holes = $('form.special_form input.special_total_number').val();
        var Copper_weight_wall = $('form.special_form input.special_copper_hall').val();
        var Number_core = $('form.special_form input.special_number_core').val();
        var PP_number = $('form.special_form input.special_pp_number').val();
        var Acceptable_stanadard = $('form.special_form select.special_acceptable').val();
        var Total_test_points = $('form.special_form input.special_total_test').val();
        var Blind_and_buried_hole = $('form.special_form input.special_blind_hole').val();
        var Blind_hole_structure = $('form.special_form input.special_blind_struture').val();
        var Depth_control_routing = $('form.special_form select.special_depth_control').val();
        var Number_back_drilling = $('form.special_form select.special_back_drilling').val();
        var Countersunk_deep_holes = $('form.special_form input.special_countersunk').val();
        var Laser_drilling = $('form.special_form select.special_laser_drilling').val();
        var The_space_for_drop_V_cut = $('form.special_form select.special_v_cut_space').val();
        var Inner_hole_line = $('form.special_form input.special_inner_hole_line').val();

        pcb_special_value = {
            'Semi_hole': Semi_hole,
            'Edge_plating': Edge_plating,
            'Impedance': Impedance,
            'Press_fit': Press_fit,
            'Peelable_mask': Peelable_mask,
            'Carbon_oil': Carbon_oil,
            'Min_line_width': Min_line_width,
            'Min_line_space': Min_line_space,
            'Min_aperture': Min_aperture,
            'Total_holes': Total_holes,
            'Copper_weight_wall': Copper_weight_wall,
            'Number_core': Number_core,
            'PP_number': PP_number,
            'Acceptable_stanadard': Acceptable_stanadard,
            'Total_test_points': Total_test_points,
            'Blind_and_buried_hole': Blind_and_buried_hole,
            'Blind_hole_structure': Blind_hole_structure,
            'Depth_control_routing': Depth_control_routing,
            'Number_back_drilling': Number_back_drilling,
            'Countersunk_deep_holes': Countersunk_deep_holes,
            'Laser_drilling': Laser_drilling,
            'Inner_hole_line': Inner_hole_line,
            'The_space_for_drop_V_cut': The_space_for_drop_V_cut,
        }
        return pcb_special_value
    }


    //验证客户输入是否为空
    function detection_enter(){
        var pcb_qty = $('#cpo_pcb_quotation .cpo_pcb_qty_parent .cpo_pcb_qty');
        var pcb_panel_size = $('#cpo_pcb_quotation .cpo_pcb_parent input[type=text]');
        var pcb_layer = $('#cpo_pcb_quotation .cpo_pcb_layer_number .cpo_pcb_layer');
        var pcb_thickness = $('#cpo_pcb_quotation .cpo_pcb_thickness input');
        var pcb_gold_finger_val = $('#pcb_gold_finger_table input');
        var pcb_surface_more = $('#cpo_pcb_quotation .pcb_surface .cpo_pcb_surface_more.pcb_active').children('span').html();
        var pcb_imm = $('.pcb_immersion_gold_select .cpo_pcb_fold_finger');
        var pcb_imm_sele = $('.pcb_multiple_choice a.pcb_active').children('span').html();
        if(pcb_qty.val()){
            pcb_qty.parent().css('border', '1px solid #cccccc');
            pcb_qty.val(parseInt(pcb_qty.val()));
        }else{
            pcb_qty.parent().css('border', '1px solid #ff0000');
            pcb_qty.focus();
            return false
        }
        for(var i=0;i<pcb_panel_size.length;i++){
            if(pcb_panel_size[i].value){
                if(pcb_panel_size[i].nextElementSibling.innerHTML == 'Item'){
                    if(pcb_panel_size[i].value){
                        pcb_panel_size[i].parentElement.style.border = 'none';
                        pcb_panel_size[i].parentElement.style.borderBottom = '1px solid #cccccc';
                        pcb_panel_size[i].value = parseInt(pcb_panel_size[i].value);
                    }else{
                        pcb_panel_size[i].parentElement.style.border = '1px solid #ff0000';
                        pcb_panel_size[i].focus();
                    }
                }else if(pcb_panel_size[i].nextElementSibling.innerHTML == 'PCS'){
                    if(pcb_panel_size[i].value){
                        pcb_panel_size[i].parentElement.style.border = '1px solid #cccccc';
                        pcb_panel_size[i].value = parseInt(pcb_panel_size[i].value);
                    }else{
                        pcb_panel_size[i].parentElement.style.border = '1px solid #ff0000';
                        pcb_panel_size[i].focus();
                    }
                }else{
                    pcb_panel_size[i].parentElement.style.border = '1px solid #cccccc';
                    pcb_panel_size[i].value = parseFloat(pcb_panel_size[i].value).toFixed(2);
                }
            }else{
                pcb_panel_size[i].parentElement.style.border = '1px solid #ff0000';
                pcb_panel_size[i].focus();
                return false
            }

        }
        if(pcb_layer.val()){
            pcb_layer.parent().css('border', '1px solid #cccccc');
            pcb_layer.val(parseInt(pcb_layer.val()));
            if(pcb_layer.val() < 3){
                $('#cpo_pcb_quotation #inner_copper').removeClass('pcb_active');
            }else{
                $('#cpo_pcb_quotation #inner_copper').addClass('pcb_active');
            }
        }else{
            pcb_layer.parent().css('border', '1px solid #ff0000');
            pcb_layer.focus();
            return false
        }
        if(pcb_thickness.val()){
            pcb_thickness.parent().css('border', '1px solid #cccccc');
            pcb_thickness.val(parseFloat(pcb_thickness.val()));
        }else{
            pcb_thickness.parent().css('border', '1px solid #ff0000');
            pcb_thickness.focus();
            return false
        }
        if(pcb_imm_sele == "Immersion gold"){
            for(var j=0;j<pcb_imm.length;j++){
                if(pcb_imm[j].value == ""){
                    pcb_imm[j].style.border = '1px solid #ff0000';
                    return false
                }else if(pcb_imm[j].value == 0){
                    pcb_imm[j].style.border = '1px solid #ff0000';
                    pcb_imm[j].value = "";
                    return false
                }else{
                    pcb_imm[j].style.border = '1px solid #ddd';
                }
            }
        }

        if(pcb_surface_more == 'Gold finger'){
            for(var i=0;i<pcb_gold_finger_val.length;i++){
                if(pcb_gold_finger_val[i].value){
                    pcb_gold_finger_val[i].style.border = '1px solid #cccccc';
                    if(i==3){
                        pcb_gold_finger_val[i].value = parseInt(pcb_gold_finger_val[i].value);
                    }else{
                        pcb_gold_finger_val[i].value = parseFloat(pcb_gold_finger_val[i].value).toFixed(2);
                    }
                }else {
                     pcb_gold_finger_val[i].style.border = '1px solid #ff0000';
                     // pcb_gold_finger_val[i].focus();
                    return false
                }
            }
        }else{
            return true
        }
        return true
    }
    //自动检测输入框是否为空
    $('#cpo_pcb_quotation .form-group input').change(function () {
        detection_enter();
        $('#pcb_details_btn').css('display', 'none');
    });
    //面积判断，是否大于3平方米
    function judgePcbArea() {
        var cpo_quantity = $('.cpo_input_quantity input[name="cpo_input_quantity"]').val();
        var cpo_length = $('.cpo_input_quantity input[name="cpo_input_lenght"]').val();
        var cpo_width = $('.cpo_input_quantity input[name="cpo_input_width"]').val();
        var cpo_area = cpo_quantity * cpo_length * cpo_width;
    }
    function cpo_pcb_area_size(){
        var pcb_length = $('#cpo_pcb_quotation .cpo_pcb_panel_size .cpo_pcb_lenght').val();
        var pcb_width = $('#cpo_pcb_quotation .cpo_pcb_panel_size .cpo_pcb_width').val();

        if(pcb_length){
            $('#cpo_pcb_quotation .cpo_pcb_panel_size .cpo_pcb_lenght').val();
        }else{
            $('#cpo_pcb_quotation .cpo_pcb_panel_size .cpo_pcb_lenght').val("");
        }
        if(pcb_width){
            $('#cpo_pcb_quotation .cpo_pcb_panel_size .cpo_pcb_width').val();
        }else{
            $('#cpo_pcb_quotation .cpo_pcb_panel_size .cpo_pcb_width').val("");
        }
        var pcb_qty = $('#cpo_pcb_quotation .cpo_pcb_qty').val();
        var pcb_e_test = $('#cpo_pcb_quotation .pcb_flying_probe .pcb_e_test_ficture');
        var e_test_fee = $('#cpo_pcb_quotation .pcb_flying_probe a.pcb_active').html();

        var pcb_area_size = pcb_width * pcb_length * pcb_qty;
        if(pcb_area_size >= 3000000){
            pcb_e_test.addClass('pcb_active').siblings('a').removeClass('pcb_active');
            $('#pcb_test_fee').css('display', 'block');
            return true
        }else if(pcb_area_size < 3000000 && e_test_fee == 'E-test fixture'){
            $('#pcb_test_fee').css('display', 'block');
            // pcb_e_test.removeClass('pcb_active').siblings('a').addClass('pcb_active');
            return true
        }else{
            $('#pcb_test_fee').css('display', 'none');
            // pcb_e_test.removeClass('pcb_active').siblings('a').addClass('pcb_active');
        }
    }
    //自动检测客户输入面积的大小
    $('#cpo_pcb_quotation .cpo_pcb_parent .cpo_pcb_width').change(function () {
        cpo_pcb_area_size();
    });
    $('#cpo_pcb_quotation .cpo_pcb_panel_size .cpo_pcb_lenght').change(function () {
        cpo_pcb_area_size();
    });
    $('#cpo_pcb_quotation .cpo_pcb_qty').change(function () {
        cpo_pcb_area_size();
    });

    //判断拼版款数
    function pcb_unit_sku(){
        var cpo_pcs_val = $('#cpo_pcb_quotation .cpo_pcb_pcs_parent input.pcb_panel_pcs');
        var cpo_sku_val = $('#cpo_pcb_quotation .pcb_unit_sku input.cpo_pcb_sku');
        if(cpo_sku_val.val() > 5){
            alert('Puzzle mobile number, No more than 5!');
            cpo_sku_val.val('');
            return false
        }
        if(cpo_pcs_val.val() <= cpo_sku_val.val()){
            alert('The number of PCB must be less than or equal to the number of PCS!')
            return false
        }
    }
    //change 拼版款数
    $('#cpo_pcb_quotation .pcb_unit_sku input.cpo_pcb_sku').change(function () {
        pcb_unit_sku();
    });

    //PCS 和 Panel 选择
    $('#cpo_pcb_quotation .cpo_pcb_qty_total a.cpo_pcb_qty_unit').click(function () {
        var this_val = $(this).html();
        var pcb_xiegan = $('#cpo_pcb_quotation .cpo_pcb_area .pcb_xiegan');
        var pcb_pcb_pcs = $('#cpo_pcb_quotation .cpo_pcb_area .cpo_pcb_pcs_parent');
        var pcb_unit_sku = $('#cpo_pcb_quotation .cpo_pcb_area .pcb_unit_sku');
        if(this_val == 'Set'){
            if(pcb_xiegan.length >= 1 || pcb_pcb_pcs.length >= 1 || pcb_unit_sku.length >= 1){
                return true
            }else{
                $('#cpo_pcb_quotation .cpo_pcb_area').append(
                "<span class=\"pcb_xiegan\">/</span>\n" +
                "<a class=\"form-control cpo_pcb_parent cpo_pcb_pcs_parent\">\n" +
                "<input type=\"text\" name=\"abc\" class=\"pcb_panel_pcs\"\n" +
                "maxlength=\"7\" onKeyUp=\"value=value.replace(/\\D/g,'')\" onchange=\"value=value.replace(/\\D/g,'')\"/>\n" +
                "<i class=\"cpo_pcb_unit\">PCS</i>\n" +
                "</a>\n" +
                "<a class=\"form-control cpo_pcb_parent pcb_unit_sku\">\n" +
                "(<input type=\"text\" name=\"abc\" class=\"unit_sku cpo_pcb_sku\"\n" +
                "maxlength=\"7\" onKeyUp=\"value=value.replace(/\\D/g,'')\" onchange=\"value=value.replace(/\\D/g,'')\"/>\n" +
                "<i class=\"pcb_unit\">Item</i>)\n" +
                "</a>");
            }
            $('#cpo_pcb_quotation .cpo_pcb_panel_size label').html('Set Size');
        }else{

            $('#cpo_pcb_quotation .cpo_pcb_area .pcb_xiegan').remove();
            $('#cpo_pcb_quotation .cpo_pcb_area .cpo_pcb_pcs_parent').remove();
            $('#cpo_pcb_quotation .cpo_pcb_area .pcb_unit_sku').remove();
            $('#cpo_pcb_quotation .cpo_pcb_panel_size label').html('PCS Size');
        }
    });

    //判断面积，选择收费
    $('#cpo_pcb_quotation .pcb_flying_probe a').click(function () {
        $(this).addClass('pcb_active');
        if($(this).html() == 'Free Flying Probe'){
            if(cpo_pcb_area_size()){
                alert('The current area is greater than or equal to 3 square meters, need to charge the test fee!');
                return false
            }else{
                $(this).siblings('a').removeClass('pcb_active');
                $('#pcb_test_fee').css('display', 'none');
            }
        }else{
            $(this).siblings('a').removeClass('pcb_active');
            $('#pcb_test_fee').css('display', 'block');
            // $(this).toggleClass('.pcb_active')
        }
    });

    //表面处理的组合
    function pcb_results_match() {
        var pcb_osp = [
            'Immersion gold(1 u″) + Electroless nickel gold',
            'Immersion gold(2 u″) + Electroless nickel gold',
            'Immersion gold(3 u″) + Electroless nickel gold',
            'Immersion gold(1 u″) + Complete gold plating',
            'Immersion gold(2 u″) + Complete gold plating',
            'Immersion gold(3 u″) + Complete gold plating',
            'Immersion gold(1 u″) + Gold plating',
            'Immersion gold(2 u″) + Gold plating',
            'Immersion gold(3 u″) + Gold plating',
            'Immersion gold + Complete gold plating',
            'Immersion gold + Gold plating',
            'Immersion gold(1 u″) + OSP',
            'Immersion gold(2 u″) + OSP',
            'Immersion gold(3 u″) + OSP',
            'Immersion gold + OSP',
            'Immersion gold(1 u″) + Gold finger',
            'Immersion gold(2 u″) + Gold finger',
            'Immersion gold(3 u″) + Gold finger',
            'Immersion gold + Gold finger',
            'OSP + Electroless nickel gold',
            'Leaded HASL + Gold finger',
            'Lead Free HASL + Gold finger',
            'Immersion Tin + Gold finger',
            'Immersion Silver + Gold finger',
            'Nickel palladium gold + Gold finger',
            'OSP + Gold finger',
            'Gold finger + Electroless nickel gold'
        ]
        return pcb_osp
    }
    //不选择金手指时，金手指参数清空
    function clear_glof_finger() {
        var fg_gold_thickness = $('#pcb_gold_finger_table .gold_thickness');
        var fg_gold_size_width = $('#pcb_gold_finger_table .numbers_gold_size_width');
        var fg_gold_size_height = $('#pcb_gold_finger_table .numbers_gold_size_height');
        var fg_size = $('#pcb_gold_finger_table .gold_finger_size');

        // var pcb_finger_data = {
        //     'fg_gold_thickness':fg_gold_thickness,
        //     'fg_gold_size_width':fg_gold_size_width,
        //     'fg_gold_size_height':fg_gold_size_height,
        //     'fg_size':fg_size,
        // }
        fg_gold_thickness.val("");
        fg_gold_size_width.val("");
        fg_gold_size_height.val("");
        fg_size.val("");

        return true
    }
    // 金手指所有搭配的可能性（提供客户选择）
    function cpo_pcb_gold_figer() {

        var pcb_osp = pcb_results_match();

        var pcb_surface_result = '';
        var pcb_surface_content = '';
        var pcb_radio = $('#cpo_pcb_quotation .pcb_multiple_choice .pcb_active');
        var pcb_surface_unit = $('#cpo_pcb_quotation .pcb_multiple_choice .pcb_active').children('.pcb_immersion_gold').val();
        var pcb_surface_title = $('#cpo_pcb_quotation .pcb_multiple_choice .pcb_active').children('.pcb_immersion_title').html();
        var pcb_surface_special = $('#cpo_pcb_quotation .pcb_gold_finger_select .pcb_active').children();
        var pcb_fg_gold_thickness = $('#pcb_gold_finger_table .gold_thickness').val();
        var pcb_fg_gold_size_width = $('#pcb_gold_finger_table .numbers_gold_size_width').val();
        var pcb_fg_gold_size_height = $('#pcb_gold_finger_table .numbers_gold_size_height').val();
        var pcb_fg_size = $('#pcb_gold_finger_table .gold_finger_size').val();
        var pcb_nickel_thickness = $('#pcb_immersion_gold_table .nickel_thickness').val();
        var pcb_coated_area = $('#pcb_immersion_gold_table .coated_area').val();
        //沉金取值
        if(pcb_surface_title && pcb_surface_unit){
            pcb_surface_result = pcb_surface_title+'('+pcb_surface_unit+')';
            $('#cpo_pcb_quotation .pcb_immersion_gold_select').css('display', 'block');
        }else if(pcb_surface_title){
            pcb_surface_result = pcb_surface_title;
            $('#cpo_pcb_quotation .pcb_immersion_gold_select').css('display', 'none');
        }else if(pcb_surface_special.length){
            pcb_surface_result = pcb_surface_special.html();
            $('#cpo_pcb_quotation .pcb_immersion_gold_select').css('display', 'none');
        }else{
            pcb_surface_result = $('#cpo_pcb_quotation .pcb_surface .pcb_none_select a').children('span').html();
            $('#cpo_pcb_quotation .pcb_immersion_gold_select').css('display', 'none');
            return pcb_surface_result
        }

        //判断表处理的组合能不能通过
        if(pcb_radio.length && pcb_surface_special.length){
            if(pcb_surface_special.html() == 'Gold finger'){
                var pcb_gold_finger  = pcb_surface_result +' + '+ pcb_surface_special.html()
                if(jQuery.inArray(pcb_gold_finger, pcb_osp) > -1){
                    $('#cpo_pcb_quotation .pcb_gold_finger').css('display','block');
                    if(pcb_surface_title == 'Immersion gold'){
                        pcb_surface_content = {
                            'pcb_fg_gold_thickness': pcb_fg_gold_thickness,
                            'pcb_fg_gold_size_width': pcb_fg_gold_size_width,
                            'pcb_fg_gold_size_height': pcb_fg_gold_size_height,
                            'pcb_fg_size': pcb_fg_size,
                            'pcb_nickel_thickness': pcb_nickel_thickness,
                            'pcb_coated_area': pcb_coated_area,
                            'pcb_surface': pcb_surface_result +' + '+ pcb_surface_special.html(),
                        }
                    }else{
                        pcb_surface_content = {
                            'pcb_fg_gold_thickness': pcb_fg_gold_thickness,
                            'pcb_fg_gold_size_width': pcb_fg_gold_size_width,
                            'pcb_fg_gold_size_height': pcb_fg_gold_size_height,
                            'pcb_fg_size': pcb_fg_size,
                            'pcb_surface': pcb_surface_result +' + '+ pcb_surface_special.html(),
                        }
                    }

                    return pcb_surface_content
                }else{
                    return false
                }

            }else{
                var pcb_surface = pcb_surface_result +' + '+ pcb_surface_special.html();
                clear_glof_finger()
                if(jQuery.inArray(pcb_surface, pcb_osp) > -1){
                    // clear_glof_finger();
                    pcb_surface_content = {
                        'pcb_fg_gold_thickness': "",
                        'pcb_fg_gold_size_width': "",
                        'pcb_fg_gold_size_height': "",
                        'pcb_fg_size': "",
                        'pcb_nickel_thickness': pcb_nickel_thickness,
                        'pcb_coated_area': pcb_coated_area,
                        'pcb_surface': pcb_surface
                    }
                    return pcb_surface_content
                }else{
                    // alert('Current match cannot complete auto quote!')
                    return false
                }
            }
        }else if(pcb_radio.length){
            if(pcb_surface_title == 'Immersion gold'){
                pcb_surface_content = {
                    'pcb_surface': pcb_surface_result,
                    'pcb_nickel_thickness': pcb_nickel_thickness,
                    'pcb_coated_area': pcb_coated_area,
                }
                return pcb_surface_content
            }else {
                pcb_surface_content = {
                    'pcb_surface': pcb_surface_result,
                    'pcb_nickel_thickness': "",
                    'pcb_coated_area': "",
                }
                return pcb_surface_content
            }


        }else{
            if(pcb_surface_special.length > 1){
                if(pcb_surface_special[1].innerHTML == 'Gold finger'){
                    $('#cpo_pcb_quotation .pcb_gold_finger').css('display','block');
                    var pcb_surface = pcb_surface_special[0].innerHTML +' + '+ pcb_surface_special[1].innerHTML;
                    if(jQuery.inArray(pcb_surface, pcb_osp) > -1){
                        // clear_glof_finger();
                        pcb_surface_content = {
                            'pcb_fg_gold_thickness': pcb_fg_gold_thickness,
                            'pcb_fg_gold_size_width': pcb_fg_gold_size_width,
                            'pcb_fg_gold_size_height': pcb_fg_gold_size_height,
                            'pcb_fg_size': pcb_fg_size,
                            'pcb_surface': pcb_surface,
                        }
                        return pcb_surface_content
                    }else{
                        // alert('Current match cannot complete auto quote!')
                        return false
                    }
                }else if(pcb_surface_special[0].innerHTML == 'Gold finger'){
                    var pcb_surface = pcb_surface_special[0].innerHTML +' + '+ pcb_surface_special[1].innerHTML;
                    $('#cpo_pcb_quotation .pcb_gold_finger').css('display','block');
                    if(jQuery.inArray(pcb_surface, pcb_osp) > -1){
                        pcb_surface_content = {
                            'pcb_fg_gold_thickness': pcb_fg_gold_thickness,
                            'pcb_fg_gold_size_width': pcb_fg_gold_size_width,
                            'pcb_fg_gold_size_height': pcb_fg_gold_size_height,
                            'pcb_fg_size': pcb_fg_size,
                            'pcb_surface': pcb_surface,
                        }
                        return pcb_surface_content
                    }else{
                        // alert('Current match cannot complete auto quote!')
                        return false
                    }
                }else{
                    var pcb_surface = pcb_surface_special[0].innerHTML +' + '+ pcb_surface_special[1].innerHTML;
                    if(jQuery.inArray(pcb_surface, pcb_osp) > -1){
                        if(pcb_surface_title == 'Immersion gold'){
                            pcb_surface_content = {
                                'pcb_surface': pcb_surface_result,
                                'pcb_fg_gold_thickness': "",
                                'pcb_fg_gold_size_width': "",
                                'pcb_fg_gold_size_height': "",
                                'pcb_fg_size': "",
                                'pcb_nickel_thickness': pcb_nickel_thickness,
                                'pcb_coated_area': pcb_coated_area,
                            }
                            alert(pcb_surface_content)
                            return pcb_surface_content
                        }else {
                            pcb_surface_content = {
                                'pcb_surface': pcb_surface_result,
                                'pcb_nickel_thickness': "",
                                'pcb_coated_area': "",
                            }
                            return pcb_surface_content
                        }
                        // pcb_surface_content = {
                        //     'pcb_surface': pcb_surface,
                        // }

                    }else{
                        // alert('Current match cannot complete auto quote!')
                        return false
                    }
                }
            }else {
                pcb_surface_content = {
                    'pcb_surface': pcb_surface_result,
                }
                return pcb_surface_content
            }
        }



    }

    //获取特殊要求数据
    function special_form() {
        var pcb_tg_value = $('#pcb_col_md_8 .table .pcb_tg_value');//TG 值
        var pcb_semi_hole = $('#pcb_col_md_8 .table .pcb_semi_hole');//Semi-hole
        var pcb_edge_plating = $('#pcb_col_md_8 .table .pcb_edge_plating');//Edge plating
        var pcb_impedance = $('#pcb_col_md_8 .table .pcb_impedance');//Impedance
        // var pcb_impedance_contous = $('#pcb_col_md_8 .table .pcb_impedance_contous');//Impedance contous
        var pcb_blind_hole = $('#pcb_col_md_8 .table .pcb_blind_hole');//The drill layer for blind &amp; buried hole
        var pcb_blind_struture = $('#pcb_col_md_8 .table .pcb_blind_struture');//Blind hole structure
        // var pcb_laminating_times = $('#pcb_col_md_8 .table .pcb_laminating_times');
        var pcb_press_fit = $('#pcb_col_md_8 .table .pcb_press_fit');
        var pcb_carbon_oil = $('#pcb_col_md_8 .table .pcb_carbon_oil');
        // var pcb_plugging_hole = $('#pcb_col_md_8 .table .pcb_plugging_hole');
        var pcb_peelable_mask = $('#pcb_col_md_8 .table .pcb_peelable_mask');
        var pcb_coil_plate = $('#pcb_col_md_8 .table .pcb_coil_plate');
        var pcb_back_drilling = $('#pcb_col_md_8 .table .pcb_back_drilling');
        var pcb_depth_control = $('#pcb_col_md_8 .table .pcb_depth_control');
        var pcb_countersunk = $('#pcb_col_md_8 .table .pcb_countersunk');
        // var pcb_control_deep = $('#pcb_col_md_8 .table .pcb_control_deep');
        var pcb_laser_drilling = $('#pcb_col_md_8 .table .pcb_laser_drilling');
        // var pcb_v_cut_knives = $('#pcb_col_md_8 .table .pcb_v_cut_knives');
        // var pcb_v_cut_drop = $('#pcb_col_md_8 .table .pcb_v_cut_drop');
        var pcb_v_cut_space = $('#pcb_col_md_8 .table .pcb_v_cut_space');
        var pcb_minimum_line = $('#pcb_col_md_8 .table .pcb_minimum_line');
        var pcb_minimun_line_space = $('#pcb_col_md_8 .table .pcb_minimun_line_space');
        var pcb_minimum_aperture = $('#pcb_col_md_8 .table .pcb_minimum_aperture');
        var pcb_inner_hole_line = $('#pcb_col_md_8 .table .pcb_inner_hole_line');
        var pcb_bga_center = $('#pcb_col_md_8 .table .pcb_bga_center');
        var pcb_thickness_diameter = $('#pcb_col_md_8 .table .pcb_thickness_diameter');
        var pcb_total_number = $('#pcb_col_md_8 .table .pcb_total_number');
        // var pcb_hole_density = $('#pcb_col_md_8 .table .pcb_hole_density');
        var pcb_copper_hall = $('#pcb_col_md_8 .table .pcb_copper_hall');
        var pcb_number_core = $('#pcb_col_md_8 .table .pcb_number_core');
        var pcb_pp_number = $('#pcb_col_md_8 .table .pcb_pp_number');
        var pcb_acceptable = $('#pcb_col_md_8 .table .pcb_acceptable');
        var pcb_total_test = $('#pcb_col_md_8 .table .pcb_total_test');

        var pcb_special_require = {
            'TG_values':pcb_tg_value,
            'Semi_hole':pcb_semi_hole,
            'Edge_plating':pcb_edge_plating,
            'Impedance':pcb_impedance,
            'Blind_and_buried_hole':pcb_blind_hole,
            // 'Impedance_contous':pcb_impedance_contous,
            'Countersunk_deep_holes':pcb_countersunk,
            'Blind_hole_structure':pcb_blind_struture,
            // 'Laminating_times':pcb_laminating_times,
            'Press_fit':pcb_press_fit,
            'Carbon_oil':pcb_carbon_oil,
            // 'Plugging_resin_times':pcb_plugging_hole,
            'Peelable_mask':pcb_peelable_mask,
            'Coil_plate':pcb_coil_plate,
            'Number_back_drilling':pcb_back_drilling,
            'Depth_control_routing':pcb_depth_control,
            // 'Control_deep_gong':pcb_control_deep,
            'Laser_drilling':pcb_laser_drilling,
            // 'Number_V_CUT_knives': pcb_v_cut_knives,
            // 'Number_of_drop_V_CUT':pcb_v_cut_drop,
            'The_space_for_drop_V_cut':pcb_v_cut_space,
            'Min_line_width':pcb_minimum_line,
            'Min_line_space':pcb_minimun_line_space,
            'Min_aperture':pcb_minimum_aperture,
            'Inner_hole_line':pcb_inner_hole_line,
            'BGA_center': pcb_bga_center,
            'Thickness_ratio':pcb_thickness_diameter,
            'Total_holes':pcb_total_number,
            // 'Hole_density':pcb_hole_density,
            'Copper_weight_wall':pcb_copper_hall,
            'Number_core':pcb_number_core,
            'PP_number':pcb_pp_number,
            'Acceptable_stanadard': pcb_acceptable,
            'Total_test_points':pcb_total_test,
        }
        var pcb_special_requirements = {
            'TG_values':pcb_tg_value.val(),
            'Semi_hole':pcb_semi_hole.val(),
            'Edge_plating':pcb_edge_plating.val(),
            'Impedance':pcb_impedance.val(),
            'Blind_and_buried_hole':pcb_blind_hole.val(),
            // 'Impedance_contous':pcb_impedance_contous.val(),
            'Countersunk_deep_holes':pcb_countersunk.val(),
            'Blind_hole_structure':pcb_blind_struture.val(),
            // 'Laminating_times':pcb_laminating_times.val(),
            'Press_fit':pcb_press_fit.val(),
            'Carbon_oil':pcb_carbon_oil.val(),
            // 'Plugging_resin_times':pcb_plugging_hole.val(),
            'Peelable_mask':pcb_peelable_mask.val(),
            'Coil_plate':pcb_coil_plate.val(),
            'Number_back_drilling':pcb_back_drilling.val(),
            'Depth_control_routing':pcb_depth_control.val(),
            // 'Control_deep_gong':pcb_control_deep.val(),
            'Laser_drilling':pcb_laser_drilling.val(),
            // 'Number_V_CUT_knives': pcb_v_cut_knives.val(),
            // 'Number_of_drop_V_CUT':pcb_v_cut_drop.val(),
            'The_space_for_drop_V_cut':pcb_v_cut_space.val(),
            'Min_line_width':pcb_minimum_line.val(),
            'Min_line_space':pcb_minimun_line_space.val(),
            'Min_aperture':pcb_minimum_aperture.val(),
            'Inner_hole_line':pcb_inner_hole_line.val(),
            'BGA_center': pcb_bga_center.val(),
            'Thickness_ratio':pcb_thickness_diameter.val(),
            'Total_holes':pcb_total_number.val(),
            // 'Hole_density':pcb_hole_density.val(),
            'Copper_weight_wall':pcb_copper_hall.val(),
            'Number_core':pcb_number_core.val(),
            'PP_number':pcb_pp_number.val(),
            'Acceptable_stanadard': pcb_acceptable.val(),
            'Total_test_points':pcb_total_test.val(),
            'pcb_special_require': pcb_special_require
        }
        var special_requirements = {
            'pcb_special_require': pcb_special_require,
            'pcb_special_requirements': pcb_special_requirements,
        }
        return special_requirements
    }

    //获取数据
    function acquire(){
        // var pcb_surface_result = null;
        var copper_inner_content = null;
        var copper_outer_content = null;
        var pcb_qty_calculate = null;
        var pcb_qty_unit = null;
        var pcb_solder_mask = null;
        var pcb_silkscreen_color = null;
        var pcb_panel_pcs = null;
        var pcs_size = null;
        var item_size = null;

        var qty = $('#cpo_pcb_quotation .cpo_pcb_qty_total .cpo_pcb_qty').val();
        var qty_unit = $('#cpo_pcb_quotation .cpo_pcb_qty_total .pcb_active').html();
        pcb_qty_calculate = qty
        var pcb_qty_calculate_unit = qty_unit

        var pcb_pcs_size_val = $('#cpo_pcb_quotation .cpo_pcb_area .cpo_pcb_pcs_parent input.pcb_panel_pcs');
        var pcb_item_size_val = $('#cpo_pcb_quotation .cpo_pcb_area .pcb_unit_sku input.unit_sku');

            if(pcb_pcs_size_val.val() || pcb_item_size_val.val()){
                pcs_size = pcb_pcs_size_val.val() + ' PCS';
                item_size = pcb_item_size_val.val() + ' Item';
            }else{
                pcs_size = null;
                item_size = null;
            }



        var pcb_surface_content = cpo_pcb_gold_figer();
        var copper_inner_title = $('#cpo_pcb_quotation .cpo_pcb_copper_weight #inner_copper.pcb_active').children('.pcb_inner_copper_title').html();
        var copper_inner_unit = $('#cpo_pcb_quotation .cpo_pcb_copper_weight #inner_copper.pcb_active').children('.inner_copper_value').val();
        var pcb_copper_unit = $('#cpo_pcb_quotation .cpo_pcb_copper_weight #inner_copper.pcb_active').children('.pcb_copper_unit').html();
        if(copper_inner_title && copper_inner_unit){
            copper_inner_content = copper_inner_title+'('+copper_inner_unit+' '+'OZ)';
        }else if(copper_inner_title){
            copper_inner_content = copper_inner_title
        }

        var copper_outer_title = $('#cpo_pcb_quotation .cpo_pcb_copper_weight #outer_copper.pcb_active').children('.pcb_outer_copper_title').html();
        var copper_outer_unit = $('#cpo_pcb_quotation .cpo_pcb_copper_weight #outer_copper.pcb_active').children('.outer_copper_value').val();
        if(copper_outer_title && copper_outer_unit){
            copper_outer_content = copper_outer_title+'('+copper_outer_unit+' '+'OZ)';
        }else if(copper_outer_title){
            copper_outer_content = copper_outer_title
        }

        var pcb_qty = pcb_qty_calculate;
        var pcb_qty_unit = pcb_qty_calculate_unit;
        var pcb_pcs_size = pcs_size;
        var pcb_item_size = item_size;
        var pcb_length = $('#cpo_pcb_quotation .cpo_pcb_panel_size .cpo_pcb_lenght').val();
        var pcb_width = $('#cpo_pcb_quotation .cpo_pcb_panel_size .cpo_pcb_width').val();
        var pcb_layer = $('#cpo_pcb_quotation .cpo_pcb_layer_number .cpo_pcb_layer').val();
        var pcb_type = $('#cpo_pcb_quotation .pcb_order .pcb_active input').val();
        var pcb_thickness = $('#cpo_pcb_quotation .pcb_thickness .cpo_pcb_thickness input').val();
        var pcb_inner_copper = copper_inner_content;
        var pcb_outer_copper = copper_outer_content;
        var pcb_solder_mask_color = $('#cpo_pcb_quotation .pcb_solder_mask .pcb_active').html();
        var pcb_silkscreen_select_color = $('#cpo_pcb_quotation .pcb_text_color .pcb_active').html();
        var pcb_surface = pcb_surface_content;
        var pcb_vias = $('#cpo_pcb_quotation .pcb_vias .pcb_active').html();
        var pcb_frame = $('#cpo_pcb_quotation .pcb_stencil_select a.pcb_active').html();
        var pcb_test = $('#cpo_pcb_quotation .pcb_flying .pcb_active').html();

        if(pcb_solder_mask_color){
            pcb_solder_mask = pcb_solder_mask_color;
        }else{
            pcb_solder_mask = '';
        }

        if(pcb_silkscreen_select_color){
            pcb_silkscreen_color = pcb_silkscreen_select_color;
        }else{
            pcb_silkscreen_color = '';
        }
        var ac_obj = {
                'pcb_qty':pcb_qty,
                'pcb_qty_unit':pcb_qty_unit,
                'pcb_length':pcb_length,
                'pcb_width':pcb_width,
                'pcb_pcs_size':pcb_pcs_size,
                'pcb_item_size':pcb_item_size,
                'pcb_layer':pcb_layer,
                'pcb_type':pcb_type,
                'pcb_thickness':pcb_thickness,
                'pcb_inner_copper':pcb_inner_copper,
                'pcb_outer_copper':pcb_outer_copper,
                'pcb_solder_mask':pcb_solder_mask,
                'pcb_silkscreen_color':pcb_silkscreen_color,
                'pcb_surface':pcb_surface,
                'pcb_vias':pcb_vias,
                'pcb_frame':pcb_frame,
                'pcb_test':pcb_test
        }
        return ac_obj
    }
    //渲染特殊要求数据
    function special_form_rendering() {
        var pcb_tg_value = $('#pcb_special_requirements_val .pcb_tg_value');//TG 值
        var pcb_semi_hole = $('#pcb_special_requirements_val .pcb_semi_hole');//Semi-hole
        var pcb_edge_plating = $('#pcb_special_requirements_val .pcb_edge_plating');//Edge plating
        var pcb_impedance = $('#pcb_special_requirements_val .pcb_impedance');//Impedance
        // var pcb_impedance_contous = $('#pcb_special_requirements_val .pcb_impedance_contous');//Impedance contous
        var pcb_blind_hole = $('#pcb_special_requirements_val .pcb_blind_hole');//The drill layer for blind &amp; buried hole
        var pcb_blind_struture = $('#pcb_special_requirements_val .pcb_blind_struture');//Blind hole structure
        // var pcb_laminating_times = $('#pcb_special_requirements_val .pcb_laminating_times');
        var pcb_press_fit = $('#pcb_special_requirements_val .pcb_press_fit');
        var pcb_carbon_oil = $('#pcb_special_requirements_val .pcb_carbon_oil');
        // var pcb_plugging_hole = $('#pcb_special_requirements_val .pcb_plugging_hole');
        var pcb_peelable_mask = $('#pcb_special_requirements_val .pcb_peelable_mask');
        var pcb_coil_plate = $('#pcb_special_requirements_val .pcb_coil_plate');
        var pcb_back_drilling = $('#pcb_special_requirements_val .pcb_back_drilling');
        var pcb_depth_control = $('#pcb_special_requirements_val .pcb_depth_control');
        var pcb_countersunk = $('#pcb_special_requirements_val .pcb_countersunk');
        // var pcb_control_deep = $('#pcb_special_requirements_val .pcb_control_deep');
        var pcb_laser_drilling = $('#pcb_special_requirements_val .pcb_laser_drilling');
        // var pcb_v_cut_knives = $('#pcb_special_requirements_val .pcb_v_cut_knives');
        // var pcb_v_cut_drop = $('#pcb_special_requirements_val .pcb_v_cut_drop');
        var pcb_v_cut_space = $('#pcb_special_requirements_val .pcb_v_cut_space');
        var pcb_minimum_line = $('#pcb_special_requirements_val .pcb_minimum_line');
        var pcb_minimun_line_space = $('#pcb_special_requirements_val .pcb_minimun_line_space');
        var pcb_minimum_aperture = $('#pcb_special_requirements_val .pcb_minimum_aperture');
        var pcb_inner_hole_line = $('#pcb_special_requirements_val .pcb_inner_hole_line');
        var pcb_bga_center = $('#pcb_special_requirements_val .pcb_bga_center');
        var pcb_thickness_diameter = $('#pcb_special_requirements_val .pcb_thickness_diameter');
        var pcb_total_number = $('#pcb_special_requirements_val .pcb_total_number');
        // var pcb_hole_density = $('#pcb_special_requirements_val .pcb_hole_density');
        var pcb_copper_hall = $('#pcb_special_requirements_val .pcb_copper_hall');
        var pcb_number_core = $('#pcb_special_requirements_val .pcb_number_core');
        var pcb_pp_number = $('#pcb_special_requirements_val .pcb_pp_number');
        var pcb_acceptable = $('#pcb_special_requirements_val .pcb_acceptable');
        var pcb_total_test = $('#pcb_special_requirements_val .pcb_total_test');

        var pcb_special_require_reader = {
            'TG_values':pcb_tg_value,
            'Semi_hole':pcb_semi_hole,
            'Edge_plating':pcb_edge_plating,
            'Impedance':pcb_impedance,
            'Blind_and_buried_hole':pcb_blind_hole,
            // 'Impedance_contous':pcb_impedance_contous,
            'Countersunk_deep_holes':pcb_countersunk,
            'Blind_hole_structure':pcb_blind_struture,
            // 'Laminating_times':pcb_laminating_times,
            'Press_fit':pcb_press_fit,
            'Carbon_oil':pcb_carbon_oil,
            // 'Plugging_resin_times':pcb_plugging_hole,
            'Peelable_mask':pcb_peelable_mask,
            'Coil_plate':pcb_coil_plate,
            'Number_back_drilling':pcb_back_drilling,
            'Depth_control_routing':pcb_depth_control,
            // 'Control_deep_gong':pcb_control_deep,
            'Laser_drilling':pcb_laser_drilling,
            // 'Number_V_CUT_knives': pcb_v_cut_knives,
            // 'Number_of_drop_V_CUT':pcb_v_cut_drop,
            'The_space_for_drop_V_cut':pcb_v_cut_space,
            'Min_line_width':pcb_minimum_line,
            'Min_line_space':pcb_minimun_line_space,
            'Min_aperture':pcb_minimum_aperture,
            'Inner_hole_line':pcb_inner_hole_line,
            'BGA_center': pcb_bga_center,
            'Thickness_ratio':pcb_thickness_diameter,
            'Total_holes':pcb_total_number,
            // 'Hole_density':pcb_hole_density,
            'Copper_weight_wall':pcb_copper_hall,
            'Number_core':pcb_number_core,
            'PP_number':pcb_pp_number,
            'Acceptable_stanadard': pcb_acceptable,
            'Total_test_points':pcb_total_test,
        }

        return pcb_special_require_reader
    }
    //渲染数据
    function pcb_calculate(){
        var pcb_qty = $('#pcb_select_result .pcb_qty');
        var pcb_size_width = $('#pcb_select_result .pcb_size_width');
        var pcb_size_length = $('#pcb_select_result .pcb_size_length');
        var pcb_area = $('#pcb_select_result .pcb_area');
        var pcb_layer = $('#pcb_select_result .pcb_layer');
        var pcb_type = $('#pcb_select_result .pcb_type');
        var pcb_thickness = $('#pcb_select_result .pcb_thickness');
        var pcb_inner_copper = $('#pcb_select_result .pcb_inner_copper');
        var pcb_outer_copper = $('#pcb_select_result .pcb_outer_copper');
        var pcb_solder_mask = $('#pcb_select_result .pcb_solder_mask');
        var pcb_text_color = $('#pcb_select_result .pcb_text_color');
        var pcb_surface = $('#pcb_select_result .pcb_surface');
        var pcb_vias = $('#pcb_select_result .pcb_vias');
        var cpo_pcb_frame = $('#pcb_select_result .cpo_pcb_frame');
        var pcb_test = $('#pcb_select_result .pcb_test');
        var pcb_delivery_period = $('#pcb_select_result .pcb_delivery_period');
        var pcb_special_require = $('#pcb_select_result .pcb_special_require');
        var pcb_acceptable = $('#pcb_select_result .pcb_acceptable');   //验证标准
        var pcb_total = $('#pcb_price_calculate .pcb_all_total_fee');
        var pcb_panel_pcs = $('#pcb_special_requirements_val .pcb_panel_pcs');
        var cpo_pcb_sku = $('#pcb_special_requirements_val .cpo_pcb_sku');
        var gold_thickness = $('#pcb_special_requirements_val .gold_thickness');
        var numbers_gold_size_width = $('#pcb_special_requirements_val .numbers_gold_size_width');
        var numbers_gold_size_height = $('#pcb_special_requirements_val .numbers_gold_size_height');
        var gold_finger_size = $('#pcb_special_requirements_val .gold_finger_size');
        var pcb_quantity = $('#pcb_special_requirements_val .pcb_quantity');
        var pcb_qty_unit = $('#pcb_special_requirements_val .pcb_qty_unit');
        var pcb_nickel_thickness = $('#pcb_special_requirements_val .nickel_thickness');
        var pcb_coated_area = $('#pcb_special_requirements_val .coated_area');

        //费用
        var pcb_board_fee = $('#pcb_fee_table .pcb_board_fee');
        var pcb_set_up_cost = $('#pcb_fee_table .pcb_set_up_cost');
        var pcb_e_test = $('#pcb_fee_table .pcb_e_test');
        var pcb_process_fee = $('#pcb_fee_table .pcb_process_fee');
        var cpo_benchmark_fee = $('#pcb_fee_table .cpo_benchmark_fee');
        // var cpo_item_fee = $('#pcb_fee_table .cpo_item_fee');
        var cpo_thickness_fee = $('#pcb_fee_table .cpo_thickness_fee');
        var cpo_copper_fee = $('#pcb_fee_table .cpo_copper_fee');
        var cpo_sprocess_fee = $('#pcb_fee_table .cpo_sprocess_fee');
        var cpo_material_fee = $('#pcb_fee_table .cpo_material_fee');
        var cpo_film_all_fee = $('#pcb_fee_table .cpo_film_all_fee');
        var cpo_pcb_frame_fee = $('#pcb_fee_table .cpo_pcb_frame_fee');
        var cpo_text_color_fee = $('#pcb_fee_table .cpo_text_color_fee');
        var cpo_silkscreen_color_fee = $('#pcb_fee_table .cpo_silkscreen_color_fee');
        var cpo_surface_fee = $('#pcb_fee_table .cpo_surface_fee');
        var cpo_smaterial_fee = $('#pcb_fee_table .cpo_smaterial_fee');
        var cpo_heart_pp_fee = $('#pcb_fee_table .cpo_heart_pp_fee');
        var cpo_other_all_fee = $('#pcb_fee_table .cpo_other_all_fee');
        var cpo_gold_finger_fee = $('#pcb_fee_table .cpo_gold_finger_fee');

        var pcb_obj_result = {
            'pcb_qty':pcb_qty,
            'pcb_quantity':pcb_quantity,
            'pcb_qty_unit':pcb_qty_unit,
            'pcb_size_width':pcb_size_width,
            'pcb_size_length':pcb_size_length,
            'pcb_area':pcb_area,
            'pcb_layer':pcb_layer,
            'pcb_type':pcb_type,
            'pcb_thickness':pcb_thickness,
            'pcb_inner_copper':pcb_inner_copper,
            'pcb_outer_copper':pcb_outer_copper,
            'pcb_solder_mask':pcb_solder_mask,
            'pcb_text_color':pcb_text_color,
            'pcb_surface':pcb_surface,
            'pcb_vias':pcb_vias,
            'cpo_pcb_frame':cpo_pcb_frame,
            'pcb_test':pcb_test,
            'pcb_process_fee':pcb_process_fee,
            'pcb_delivery_period':pcb_delivery_period,
            'pcb_board_fee':pcb_board_fee,
            'pcb_set_up_cost':pcb_set_up_cost,
            'pcb_e_test':pcb_e_test,
            'pcb_special_require':pcb_special_require,
            'pcb_total':pcb_total,
            'pcb_acceptable':pcb_acceptable,

            'pcb_pcs_size':pcb_panel_pcs,
            'pcb_item_size':cpo_pcb_sku,
            'gold_thickness':gold_thickness,
            'numbers_gold_size_width':numbers_gold_size_width,
            'numbers_gold_size_height':numbers_gold_size_height,
            'gold_finger_size':gold_finger_size,
            'pcb_nickel_thickness':pcb_nickel_thickness,
            'pcb_coated_area':pcb_coated_area,

            'cpo_benchmark_fee':cpo_benchmark_fee,
            // 'cpo_item_fee':cpo_item_fee,
            'cpo_thickness_fee':cpo_thickness_fee,
            'cpo_copper_fee':cpo_copper_fee,
            'cpo_sprocess_fee':cpo_sprocess_fee,
            'cpo_material_fee':cpo_material_fee,
            'cpo_film_all_fee':cpo_film_all_fee,
            'cpo_pcb_frame_fee':cpo_pcb_frame_fee,
            'cpo_text_color_fee':cpo_text_color_fee,
            'cpo_silkscreen_color_fee':cpo_silkscreen_color_fee,
            'cpo_surface_fee':cpo_surface_fee,
            'cpo_smaterial_fee':cpo_smaterial_fee,
            'cpo_heart_pp_fee':cpo_heart_pp_fee,
            'cpo_other_all_fee':cpo_other_all_fee,
            'cpo_gold_finger_fee':cpo_gold_finger_fee,

        };

        return pcb_obj_result
    }
    //工程费计入测试费时
    $('#pcb_test_fee').mouseover(function () {
        $('#pcb_test_fee .pcb_construction_cost').css('display', 'block');
    }).mouseout(function () {
        $('#pcb_test_fee .pcb_construction_cost').css('display', 'none');
    });
    //鼠标移动到 set cost fee

    //点击选中
    $('#cpo_pcb_quotation .cpo_pcb_qty_total a.cpo_pcb_qty_unit').click(function () {
        $(this).addClass('pcb_active').siblings('a').removeClass('pcb_active');
    });
    $('#cpo_pcb_quotation .pcb_order a').click(function () {
        $(this).addClass('pcb_active').siblings('a').removeClass('pcb_active');
    });
    $('#cpo_pcb_quotation .pcb_raw_material a').click(function () {
        $(this).addClass('pcb_active').siblings('a').removeClass('pcb_active');
    });
    $('#cpo_pcb_quotation .pcb_solder_mask a').click(function () {
        $(this).addClass('pcb_active').siblings('a').removeClass('pcb_active');
    });
    $('#cpo_pcb_quotation .pcb_text_color a').click(function () {
        $(this).addClass('pcb_active').siblings('a').removeClass('pcb_active');
    });
    $('#cpo_pcb_quotation .pcb_stencil_select a').click(function () {
        $(this).addClass('pcb_active').siblings('a').removeClass('pcb_active');
        if($(this).html()!= 'No'){
            $('#cpo_pcb_stencil_fee').css('display', 'block');
        }else{
            $('#cpo_pcb_stencil_fee').css('display', 'none');
        }
    });

    //材料选择a
    $('#cpo_pcb_quotation .pcb_order a').click(function () {
        var pcb_type = $(this).children().val();
        if(pcb_type == 'Other'){
            $('#cpo_pcb_quotation .pcb_raw_material_select').css('display', 'block');
        }else{
            $('#cpo_pcb_quotation .pcb_raw_material_select').css('display', 'none');
        }
    });
    //沉金
    $('#pcb_immersion_gold_table .cpo_pcb_fold_finger').change(function () {
        $('#pcb_details_btn').css('display', 'none');
    });
    //表面处理(选择与反选)
    $('#cpo_pcb_quotation .pcb_surface .pcb_multiple_choice a.cpo_pcb_surface').click(function () {


        var pcb_select_osp = pcb_results_match();
        var pcb_finger_select = $('#cpo_pcb_quotation .pcb_surface .pcb_gold_finger_select a.cpo_pcb_surface_more').children('span');
        var pcb_finger_active = $('#cpo_pcb_quotation .pcb_surface .pcb_gold_finger_select a.pcb_active').children('span');

        if(pcb_finger_active.html()){
            for(var i=0;i<pcb_finger_active.length;i++){
                var pcb_val_this = $(this).children('span').html() +' + '+ pcb_finger_active[i].innerHTML;
                if(pcb_finger_active.length >= 2){
                    alert('You can only choose two at most!');
                    return false
                }else{
                    if($.inArray(pcb_val_this, pcb_select_osp) > -1){
                        $(this).toggleClass('pcb_active').siblings('a').removeClass('pcb_active');
                        $('#cpo_pcb_quotation .pcb_surface .pcb_none_select a').removeClass('pcb_active');
                    }else{
                        return false
                    }
                }
            }

        }else{
            $(this).toggleClass('pcb_active').siblings('a').removeClass('pcb_active');
            $('#cpo_pcb_quotation .pcb_surface .pcb_none_select a').removeClass('pcb_active');
            if($(this).hasClass('pcb_active')){
                for(var i=0;i<pcb_finger_select.length;i++){
                    var pcb_this_val = $(this).children('span').html() +' + '+ pcb_finger_select[i].innerHTML
                    if(pcb_select_osp.indexOf(pcb_this_val) == -1){
                        pcb_finger_select[i].parentElement.style.backgroundColor = '#b9b7b7';
                        pcb_finger_select[i].style.backgroundColor = '#b9b7b7';
                        pcb_finger_select[i].style.cursor = 'text';
                        pcb_finger_select[i].parentElement.style.cursor = 'text';
                    }else{
                        pcb_finger_select[i].parentElement.style.backgroundColor = '#FFFFFF';
                        pcb_finger_select[i].style.backgroundColor = '#FFFFFF';
                        pcb_finger_select[i].style.cursor = 'pointer';
                        pcb_finger_select[i].parentElement.style.cursor = 'pointer';
                    }
                }
            }else{
                pcb_finger_select.css('background-color', '#FFFFFF');
                pcb_finger_select.parent().css('cursor', 'pointer');
                pcb_finger_select.parent().css('background-color', '#FFFFFF');
            }
        }
        var pcb_active_result = $('#cpo_pcb_quotation .pcb_surface .pcb_active').length;
        if($(this).hasClass('pcb_active')){
            if(pcb_active_result > 2){
                alert('You can only choose two at most!')
                $(this).toggleClass('pcb_active').siblings('a').removeClass('pcb_active');
                return false
            }else if(cpo_pcb_gold_figer() == false){
                for(var i=0;i<pcb_finger_select.length;i++){
                    var pcb_this_val = $(this).children('span').html() +' + '+ pcb_finger_select[i].innerHTML
                    if(pcb_select_osp.indexOf(pcb_this_val) == -1){
                        if(pcb_finger_select[i].parentElement.classList.contains('pcb_active')==true){
                            $(this).toggleClass('pcb_active').siblings('a').removeClass('pcb_active');
                            if($(this).children('span').html() == 'Immersion gold'){
                                $('#cpo_pcb_quotation .pcb_immersion_gold_select').css('display', 'block');
                            }else{
                                $('#cpo_pcb_quotation .pcb_immersion_gold_select').css('display', 'none');
                            }
                        }else{
                            pcb_finger_select[i].parentElement.style.backgroundColor = '#FFFFFF';
                            pcb_finger_select[i].style.backgroundColor = '#FFFFFF';
                            pcb_finger_select[i].parentElement.style.cursor = 'pointer';
                        }
                    }else{
                        pcb_finger_select[i].parentElement.style.backgroundColor = '#FFFFFF';
                        pcb_finger_select[i].style.backgroundColor = '#FFFFFF';
                        pcb_finger_select[i].parentElement.style.cursor = 'pointer';
                        // $(this).toggleClass('pcb_active').siblings('a').removeClass('pcb_active');
                    }
                }
            }else{
                for(var i=0;i<pcb_finger_select.length;i++){
                    var pcb_this_val = $(this).children('span').html() +' + '+ pcb_finger_select[i].innerHTML
                    if(pcb_select_osp.indexOf(pcb_this_val) == -1){
                        if(pcb_finger_select[i].parentElement.classList.contains('pcb_active')==true){
                            $(this).toggleClass('pcb_active').siblings('a').removeClass('pcb_active');
                            if($(this).children('span').html() == 'Immersion gold'){
                                $('#cpo_pcb_quotation .pcb_immersion_gold_select').css('display', 'block');
                            }else{
                                $('#cpo_pcb_quotation .pcb_immersion_gold_select').css('display', 'none');
                            }
                        }else{
                            pcb_finger_select[i].parentElement.style.backgroundColor = '#b9b7b7';
                            pcb_finger_select[i].style.backgroundColor = '#b9b7b7';
                            pcb_finger_select[i].parentElement.style.cursor = 'text';
                        }
                    }else{
                        pcb_finger_select[i].parentElement.style.backgroundColor = '#FFFFFF';
                        pcb_finger_select[i].style.backgroundColor = '#FFFFFF';
                        pcb_finger_select[i].parentElement.style.cursor = 'pointer';
                        // $(this).toggleClass('pcb_active').siblings('a').removeClass('pcb_active');
                    }
                }
            }
        }else{
            pcb_finger_select.parent().css('background-color', '#fff');
            pcb_finger_select.css('background-color', '#fff');
            pcb_finger_select.css('cursor', 'pointer');
            if($('#cpo_pcb_quotation .pcb_gold_finger_select a.pcb_active').length){
                $('#cpo_pcb_quotation .pcb_surface .pcb_none_select a').removeClass('pcb_active');
            }else{
                $('#cpo_pcb_quotation .pcb_surface .pcb_none_select a').addClass('pcb_active');
                $('#cpo_pcb_quotation .pcb_immersion_gold_select').css('display', 'none');
            }

        }



    });
    $('#cpo_pcb_quotation .pcb_surface .pcb_gold_finger_select a.cpo_pcb_surface_more').click(function () {
        $(this).toggleClass('pcb_active');
        $('#cpo_pcb_quotation .pcb_surface .pcb_none_select a').removeClass('pcb_active');
        var pcb_active_result = $('#cpo_pcb_quotation .pcb_surface .pcb_active').length;
        var pcb_select_osp = pcb_results_match();
        var pcb_radio_select = $('#cpo_pcb_quotation .pcb_surface .pcb_multiple_choice a.cpo_pcb_surface').children('span');
        if(pcb_active_result > 2){
            $(this).toggleClass('pcb_active');
            alert('You can only choose two at most!')
            return false
        }else if(cpo_pcb_gold_figer() == false){
            $(this).toggleClass('pcb_active').siblings('a').removeClass('pcb_active');
        }else{
            if($(this).index() == 1){
                if($(this).hasClass('pcb_active')){
                    $('#cpo_pcb_quotation .pcb_gold_finger').css('display', 'block');
                }else{
                    $('#cpo_pcb_quotation .pcb_gold_finger').css('display', 'none');
                }
            }
        }
        var all_pcb_select = $('#cpo_pcb_quotation .pcb_surface .pcb_gold_finger_select a.pcb_active');
        var all_pcb_radio_select = $('#cpo_pcb_quotation .pcb_surface .pcb_multiple_choice a.pcb_active').children('span').html();
        if($(this).hasClass('pcb_active')){
            for(var i=0;i<pcb_radio_select.length;i++){
                var pcb_this_val = pcb_radio_select[i].innerHTML +' + '+$(this).children('span').html();
                if(pcb_radio_select[i].nextElementSibling){
                    if(pcb_select_osp.indexOf(pcb_this_val) == -1){
                        pcb_radio_select[i].parentElement.style.backgroundColor = '#b9b7b7';
                        pcb_radio_select[i].style.backgroundColor = '#b9b7b7';
                        pcb_radio_select[i].nextElementSibling.style.backgroundColor = '#b9b7b7';
                        pcb_radio_select[i].parentElement.style.cursor = 'text';
                    }else{
                        pcb_radio_select[i].parentElement.style.backgroundColor = '#FFFFFF';
                        pcb_radio_select[i].style.backgroundColor = '#FFFFFF';
                        pcb_radio_select[i].nextElementSibling.style.backgroundColor = '#FFFFFF';
                        pcb_radio_select[i].parentElement.style.cursor = 'pointer';
                    }
                }else{
                    if(pcb_select_osp.indexOf(pcb_this_val) == -1){
                        pcb_radio_select[i].parentElement.style.backgroundColor = '#b9b7b7';
                        pcb_radio_select[i].parentElement.style.cursor = 'text';
                        pcb_radio_select[i].style.backgroundColor = '#b9b7b7';
                    }else{
                        pcb_radio_select[i].parentElement.style.backgroundColor = '#FFFFFF';
                        pcb_radio_select[i].parentElement.style.cursor = 'pointer';
                        pcb_radio_select[i].style.backgroundColor = '#FFFFFF';
                    }
                }
            }
        }else if(all_pcb_radio_select){
            for(var i=0;i<pcb_radio_select.length;i++){
                    var pcb_this_val = pcb_radio_select[i].innerHTML +' + '+$(this).children('span').html();
                    if(pcb_radio_select[i].nextElementSibling){
                            pcb_radio_select[i].parentElement.style.backgroundColor = '#FFFFFF';
                            pcb_radio_select[i].parentElement.style.cursor = 'pointer';
                            pcb_radio_select[i].style.backgroundColor = '#FFFFFF';
                            pcb_radio_select[i].nextElementSibling.style.backgroundColor = '#FFFFFF';

                    }else{
                            pcb_radio_select[i].parentElement.style.backgroundColor = '#FFFFFF';
                            pcb_radio_select[i].parentElement.style.cursor = 'pointer';
                            pcb_radio_select[i].style.backgroundColor = '#FFFFFF';
                    }


            }
        }else if(all_pcb_select.children('span').html()){
             for(var i=0;i<pcb_radio_select.length;i++){
                var pcb_this_val = pcb_radio_select[i].innerHTML +' + '+all_pcb_select.children('span').html();
                if(pcb_radio_select[i].nextElementSibling){
                    if(pcb_select_osp.indexOf(pcb_this_val) == -1){
                        pcb_radio_select[i].parentElement.style.backgroundColor = '#b9b7b7';
                        pcb_radio_select[i].style.backgroundColor = '#b9b7b7';
                        pcb_radio_select[i].nextElementSibling.style.backgroundColor = '#b9b7b7';
                        pcb_radio_select[i].parentElement.style.cursor = 'text';
                    }else{
                        pcb_radio_select[i].parentElement.style.backgroundColor = '#FFFFFF';
                        pcb_radio_select[i].style.backgroundColor = '#FFFFFF';
                        pcb_radio_select[i].nextElementSibling.style.backgroundColor = '#FFFFFF';
                        pcb_radio_select[i].parentElement.style.cursor = 'pointer';
                    }
                }else{
                    if(pcb_select_osp.indexOf(pcb_this_val) == -1){
                        pcb_radio_select[i].parentElement.style.backgroundColor = '#b9b7b7';
                        pcb_radio_select[i].style.backgroundColor = '#b9b7b7';
                        pcb_radio_select[i].parentElement.style.cursor = 'text';
                    }else{
                        pcb_radio_select[i].parentElement.style.backgroundColor = '#FFFFFF';
                        pcb_radio_select[i].style.backgroundColor = '#FFFFFF';
                        pcb_radio_select[i].parentElement.style.cursor = 'pointer';
                    }
                }
            }

        }else{
            pcb_radio_select.css('background-color', '#FFFFFF');
            pcb_radio_select.parent().css('background-color', '#FFFFFF');
            pcb_radio_select.parent().css('cursor', 'pointer');
            pcb_radio_select.siblings().css('background-color', '#FFFFFF');
            $(this).siblings().css('background-color', '#FFFFFF');
            $(this).siblings().css('cursor', 'pointer');
            $(this).siblings().children().css('background-color', '#FFFFFF');
            $('#cpo_pcb_quotation .pcb_surface .pcb_none_select a').addClass('pcb_active');
        }
    });
    //选择表面处理为空时
    $('#cpo_pcb_quotation .pcb_surface .pcb_none_select a').click(function () {
        if($(this).hasClass('pcb_active')){
            // $(this).toggleClass('pcb_active');
            var pcb_radio_select = $('#cpo_pcb_quotation .pcb_surface .pcb_multiple_choice a.cpo_pcb_surface').children('span');
            var pcb_finger_select = $('#cpo_pcb_quotation .pcb_surface .pcb_gold_finger_select a.cpo_pcb_surface_more').children('span');
            pcb_radio_select.css('background-color', '#FFFFFF');
            pcb_radio_select.parent().css('background-color', '#FFFFFF');
            pcb_radio_select.parent().css('cursor', 'pointer');
            pcb_radio_select.siblings().css('background-color', '#FFFFFF');
            pcb_radio_select.parent().removeClass('pcb_active');
            pcb_finger_select.parent().css('background-color', '#fff');
            pcb_finger_select.parent().removeClass('pcb_active');
            pcb_finger_select.css('background-color', '#fff');
            pcb_finger_select.css('cursor', 'pointer');
        }else{
            $(this).addClass('pcb_active');
            var pcb_radio_select = $('#cpo_pcb_quotation .pcb_surface .pcb_multiple_choice a.cpo_pcb_surface').children('span');
            var pcb_finger_select = $('#cpo_pcb_quotation .pcb_surface .pcb_gold_finger_select a.cpo_pcb_surface_more').children('span');
            pcb_radio_select.css('background-color', '#FFFFFF');
            pcb_radio_select.parent().css('background-color', '#FFFFFF');
            pcb_radio_select.parent().css('cursor', 'pointer');
            pcb_radio_select.siblings().css('background-color', '#FFFFFF');
            pcb_radio_select.parent().removeClass('pcb_active');
            pcb_finger_select.parent().css('background-color', '#fff');
            pcb_finger_select.parent().removeClass('pcb_active');
            pcb_finger_select.css('background-color', '#fff');
            pcb_finger_select.css('cursor', 'pointer');
        }

    });

    //选中金手指必须填写相应的数据
    function pcb_gold_finger_input(){
        var pcb_gold_finger_val = $('#pcb_gold_finger_table input');
        for(var i=0;i<pcb_gold_finger_val.length;i++){
            if(pcb_gold_finger_val[i].value){

            }else {
                return false
            }
        }
    }

    $('#cpo_pcb_quotation .pcb_hole a').click(function () {
        $(this).addClass('pcb_active').siblings('a').removeClass('pcb_active');
    });
    $('#cpo_pcb_quotation .cpo_pcb_copper_weight a').click(function () {
        $(this).toggleClass('pcb_active');
    });
    //阻止select冒泡
    $('#cpo_pcb_quotation .cpo_pcb_copper_weight .cpo_pcb_cppper select').click(function () {
        $('#pcb_details_btn').css('display', 'none');
        return false;
    });
    $('#cpo_pcb_quotation .pcb_multiple_choice .pcb_immersion_gold').click(function () {
        return false;
    });
    // $('#cpo_pcb_quotation .pcb_flying a').click(function () {
    //     $(this).addClass('pcb_active').siblings('a').removeClass('pcb_active');
    // });
    $('#cpo_pcb_quotation .pcb_cppper input').click(function () {
        event.stopPropagation();
    });
    $('#cpo_pcb_quotation .cpo_pcb_cppper .pcb_inner_copper').change(function () {
        // event.stopPropagation();
        var inner_select = $('#cpo_pcb_quotation .cpo_pcb_cppper .inner_copper_value');
        inner_select.val($(this).val());
        inner_select.focus();
    });
    $('#cpo_pcb_quotation .cpo_pcb_cppper .pcb_outer_copper').change(function () {
        // event.stopPropagation();
        var outer_select = $('#cpo_pcb_quotation .cpo_pcb_cppper .outer_copper_value');
        outer_select.val($(this).val());
        outer_select.focus();
    });
    //PCB 层数不能超过20
    var pcb_item = $('#cpo_pcb_quotation .cpo_pcb_layer_parent input.cpo_pcb_layer')
    pcb_item.change(function () {
        if($(this).val() > 20){
            alert('Sorry! Currently only support 20 layers or less orders!');
            $(this).val('');
            $(this).focus();
        }
    });
    $('#cpo_pcb_quotation .form-group a').click(function () {
        if(detection_enter()) {
            $('#pcb_col_md_8').css('display', 'none');
            $('#pcb_details_btn').css('display', 'none');
            $('#pcb_col_md_1').css('display', 'block');
            $('.row_padding_value').css('display', 'block');
            $('#cpo_pcb_quotation .cpo_btn_requirement .btn i').removeClass('pcb_special_subtract').addClass('pcb_special_plus');
        }
    });
    $('#cpo_pcb_quotation .cpo_btn_requirement .btn').click(function () {
        if(detection_enter()) {
            $('#pcb_col_md_8').toggle();
            $('#pcb_col_md_1').toggle();
            $('.row_padding_value').toggle();
            var obj = $('#cpo_pcb_quotation .cpo_btn_requirement .btn i');
            if (obj.hasClass('pcb_special_plus')) {
                obj.removeClass('pcb_special_plus').addClass('pcb_special_subtract');
                $('#pcb_details_btn').css('display', 'none');
                //如果是加号则执行，否则不执行
                var pcb_acquire_data = acquire();
                var pcb_special = special_form();
                ajax.jsonRpc("/cpo_pcb_quotation", 'call', {
                    'pcb_quantity':pcb_acquire_data.pcb_qty,
                    'pcb_qty_unit':pcb_acquire_data.pcb_qty_unit,
                    'pcb_length':pcb_acquire_data.pcb_length,
                    'pcb_breadth':pcb_acquire_data.pcb_width,
                    'pcb_pcs_size':pcb_acquire_data.pcb_pcs_size,
                    'pcb_item_size':pcb_acquire_data.pcb_item_size,
                    'pcb_layer':pcb_acquire_data.pcb_layer,
                    'pcb_type':pcb_acquire_data.pcb_type,
                    'pcb_thickness':pcb_acquire_data.pcb_thickness,
                    'pcb_inner_copper':pcb_acquire_data.pcb_inner_copper,
                    'pcb_outer_copper':pcb_acquire_data.pcb_outer_copper,
                    'pcb_solder_mask':pcb_acquire_data.pcb_solder_mask,
                    'pcb_silkscreen_color':pcb_acquire_data.pcb_silkscreen_color,
                    'pcb_surfaces':pcb_acquire_data.pcb_surface,
                    'pcb_vias':pcb_acquire_data.pcb_vias,
                    'cpo_pcb_frame':pcb_acquire_data.pcb_frame,
                    'pcb_test':pcb_acquire_data.pcb_test,
                    'pcb_special':pcb_special.pcb_special_requirements
                })
                .then(function (data) {
                    // pcb_data_special(data.pcb_special);
                    pcb_special.pcb_special_require.TG_values.val(data.pcb_special.TG_values);
                    pcb_special.pcb_special_require.Semi_hole.val(data.pcb_special.Semi_hole);
                    pcb_special.pcb_special_require.Edge_plating.val(data.pcb_special.Edge_plating);
                    pcb_special.pcb_special_require.Impedance.val(data.pcb_special.Impedance);
                    pcb_special.pcb_special_require.Blind_and_buried_hole.val(data.pcb_special.Blind_and_buried_hole);
                    // pcb_special.pcb_special_require.Impedance_contous.val(data.pcb_special.Impedance_contous);
                    pcb_special.pcb_special_require.Countersunk_deep_holes.val(data.pcb_special.Countersunk_deep_holes);
                    pcb_special.pcb_special_require.Blind_hole_structure.val(data.pcb_special.Blind_hole_structure);
                    pcb_special.pcb_special_require.Press_fit.val(data.pcb_special.Press_fit);
                    pcb_special.pcb_special_require.Carbon_oil.val(data.pcb_special.Carbon_oil);
                    pcb_special.pcb_special_require.Peelable_mask.val(data.pcb_special.Peelable_mask);
                    pcb_special.pcb_special_require.Coil_plate.val(data.pcb_special.Coil_plate);
                    pcb_special.pcb_special_require.Number_back_drilling.val(data.pcb_special.Number_back_drilling);
                    pcb_special.pcb_special_require.Depth_control_routing.val(data.pcb_special.Depth_control_routing);
                    pcb_special.pcb_special_require.Laser_drilling.val(data.pcb_special.Laser_drilling);
                    pcb_special.pcb_special_require.The_space_for_drop_V_cut.val(data.pcb_special.The_space_for_drop_V_cut);
                    pcb_special.pcb_special_require.Min_line_width.val(data.pcb_special.Min_line_width);
                    pcb_special.pcb_special_require.Min_line_space.val(data.pcb_special.Min_line_space);
                    pcb_special.pcb_special_require.Min_aperture.val(data.pcb_special.Min_aperture);
                    pcb_special.pcb_special_require.Inner_hole_line.val(data.pcb_special.Inner_hole_line);
                    pcb_special.pcb_special_require.Thickness_ratio.val(data.pcb_special.Thickness_ratio);
                    pcb_special.pcb_special_require.Total_holes.val(data.pcb_special.Total_holes);
                    pcb_special.pcb_special_require.Copper_weight_wall.val(data.pcb_special.Copper_weight_wall);
                    pcb_special.pcb_special_require.Number_core.val(data.pcb_special.Number_core);
                    pcb_special.pcb_special_require.PP_number.val(data.pcb_special.PP_number);
                    pcb_special.pcb_special_require.Acceptable_stanadard.val(data.pcb_special.Acceptable_stanadard);
                    pcb_special.pcb_special_require.Total_test_points.val(data.pcb_special.Total_test_points);
                });
            } else {
                obj.removeClass('pcb_special_subtract').addClass('pcb_special_plus');
            }
        }
    });
    $('#pcb_col_md_8 #pcb_put_away').click(function () {
        $('#pcb_col_md_8').toggle();
        $('#pcb_col_md_1').toggle();
        $('.row_padding_value').toggle();
        $('#cpo_pcb_quotation .cpo_btn_requirement .btn i').addClass('pcb_special_plus').removeClass('pcb_special_subtract');
    });
    $('#pcb_board_all_fee').mouseover(function () {
        $('#pcb_price_calculate .pcb_all_fee_details').css('display', 'block');
    }).mouseout(function () {
        $('#pcb_price_calculate .pcb_all_fee_details').css('display', 'none');
    });


    //传递数据
    $('#cpo_pcb_calculate').click(function () {
        pcb_data();
    });
    function pcb_data() {
        var pcb_acquire_data = acquire();
        var pcb_set_data = pcb_calculate();
        var pcb_special = special_form();
        detection_enter();
        cpo_pcb_area_size();
        pcb_unit_sku();
        // pcb_gold_finger_input()
        if(detection_enter()==false){
            return false
        }else{
            $('#pcb_details_btn').css('display', 'inline-block');
            ajax.jsonRpc("/cpo_pcb_quotation", 'call', {
                    'pcb_quantity':pcb_acquire_data.pcb_qty,
                    'pcb_qty_unit':pcb_acquire_data.pcb_qty_unit,
                    'pcb_length':pcb_acquire_data.pcb_length,
                    'pcb_breadth':pcb_acquire_data.pcb_width,
                    'pcb_pcs_size':pcb_acquire_data.pcb_pcs_size,
                    'pcb_item_size':pcb_acquire_data.pcb_item_size,
                    'pcb_layer':pcb_acquire_data.pcb_layer,
                    'pcb_type':pcb_acquire_data.pcb_type,
                    'pcb_thickness':pcb_acquire_data.pcb_thickness,
                    'pcb_inner_copper':pcb_acquire_data.pcb_inner_copper,
                    'pcb_outer_copper':pcb_acquire_data.pcb_outer_copper,
                    'pcb_solder_mask':pcb_acquire_data.pcb_solder_mask,
                    'pcb_silkscreen_color':pcb_acquire_data.pcb_silkscreen_color,
                    'pcb_surfaces':pcb_acquire_data.pcb_surface,
                    'pcb_vias':pcb_acquire_data.pcb_vias,
                    'cpo_pcb_frame':pcb_acquire_data.pcb_frame,
                    'pcb_test':pcb_acquire_data.pcb_test,
                    'pcb_special':pcb_special.pcb_special_requirements
                })
                .then(function (data) {
                    if(data.error){
                        // var a = data.error+'\n'+'<a href="www.baidu.com">Emial</a>';
                        alert(data.error);
                        $('#pcb_details_btn').css('display', 'none');
                        return
                    }else{
                        pcb_data_special(data.pcb_special)
                        var pcb_quantity_and_unit = data.pcb_quantity + ' ' +data.pcb_qty_unit;
                        pcb_set_data.pcb_qty.val(pcb_quantity_and_unit);
                        pcb_set_data.pcb_quantity.val(data.pcb_quantity);
                        pcb_set_data.pcb_qty_unit.val(data.pcb_qty_unit);
                        pcb_set_data.pcb_size_length.val(data.pcb_length);
                        pcb_set_data.pcb_size_width.val(data.pcb_breadth);
                        pcb_set_data.pcb_pcs_size.val(data.pcb_pcs_size);
                        pcb_set_data.pcb_item_size.val(data.pcb_item_size);
                        pcb_set_data.pcb_area.val(data.cpo_flat_area);
                        pcb_set_data.pcb_layer.val(data.pcb_layer);
                        pcb_set_data.pcb_type.val(data.pcb_type);
                        pcb_set_data.pcb_thickness.val(data.pcb_thickness);
                        pcb_set_data.pcb_inner_copper.val(data.pcb_inner_copper);
                        pcb_set_data.pcb_outer_copper.val(data.pcb_outer_copper);
                        pcb_set_data.pcb_solder_mask.val(data.pcb_solder_mask);
                        pcb_set_data.pcb_text_color.val(data.pcb_silkscreen_color);
                        if(data.pcb_surfaces == 'No'){
                            pcb_set_data.pcb_surface.val(data.pcb_surfaces);
                        }else{
                            pcb_set_data.pcb_surface.val(data.pcb_surfaces.pcb_surface);
                            pcb_set_data.gold_thickness.val(data.pcb_surfaces.pcb_fg_gold_thickness);
                            pcb_set_data.numbers_gold_size_width.val(data.pcb_surfaces.pcb_fg_gold_size_width);
                            pcb_set_data.numbers_gold_size_height.val(data.pcb_surfaces.pcb_fg_gold_size_height);
                            pcb_set_data.gold_finger_size.val(data.pcb_surfaces.pcb_fg_size);
                            pcb_set_data.pcb_nickel_thickness.val(data.pcb_surfaces.pcb_nickel_thickness);
                            pcb_set_data.pcb_coated_area.val(data.pcb_surfaces.pcb_coated_area);
                        }
                        pcb_set_data.pcb_vias.val(data.pcb_vias);
                        // if(data.cpo_test_fee){
                        //     $('#cpo_pcb_stencil_fee').css('display', 'block');
                        //     pcb_set_data.cpo_pcb_frame.val(data.cpo_pcb_frame);
                        // }
                        pcb_set_data.cpo_pcb_frame.val(data.cpo_pcb_frame);
                        pcb_set_data.pcb_test.val(data.pcb_test);
                        pcb_set_data.pcb_delivery_period.val(data.cpo_delivery);
                        pcb_set_data.pcb_special_require.val(data.pcb_special);
                        pcb_set_data.pcb_total.val(data.all_fee);
                        pcb_set_data.pcb_board_fee.val(data.part_fee);
                        pcb_set_data.pcb_set_up_cost.val(data.cpo_engineering_fee);
                        if(data.cpo_test_fee){
                            pcb_set_data.pcb_e_test.val(data.cpo_test_fee);
                            $('#pcb_test_fee').css('display', 'block');
                        }else{
                            pcb_set_data.pcb_e_test.val(0);
                        }
                        pcb_set_data.cpo_benchmark_fee.val(data.cpo_benchmark_fee);
                        // pcb_set_data.cpo_item_fee.val(data.cpo_item_fee);
                        pcb_set_data.cpo_thickness_fee.val(data.cpo_thickness_fee);
                        pcb_set_data.cpo_copper_fee.val(data.cpo_copper_fee);
                        pcb_set_data.cpo_sprocess_fee.val(data.cpo_sprocess_fee);
                        pcb_set_data.cpo_material_fee.val(data.cpo_material_fee);
                        pcb_set_data.cpo_pcb_frame_fee.val(data.cpo_pcb_frame_fee);
                        if(data.cpo_film_all_fee){
                            $('#pcb_fee_table .cpo_pcb_film_fee').css('display', 'block');
                            pcb_set_data.cpo_film_all_fee.val(data.cpo_film_all_fee);
                        }else{
                            $('#pcb_fee_table .cpo_pcb_film_fee').css('display', 'none');
                            pcb_set_data.cpo_film_all_fee.val(0);
                        }

                        if(data.pcb_process_fee){
                            $('#pcb_fee_table .cpo_pcb_process_fee').css('display', 'block');
                            pcb_set_data.pcb_process_fee.val(data.pcb_process_fee);
                        }else{
                            $('#pcb_fee_table .cpo_pcb_process_fee').css('display', 'none');
                            pcb_set_data.pcb_process_fee.val(0);
                        }
                        // pcb_acceptable
                        if(data.pcb_special.Acceptable_stanadard == "2"){
                            pcb_set_data.pcb_acceptable.val("IPC Class Ⅱ");
                        }else if(data.pcb_special.Acceptable_stanadard == "3"){
                            pcb_set_data.pcb_acceptable.val("IPC Class Ⅲ");
                        }

                        pcb_set_data.cpo_text_color_fee.val(data.cpo_text_color_fee);
                        pcb_set_data.cpo_silkscreen_color_fee.val(data.cpo_silkscreen_color_fee);
                        pcb_set_data.cpo_surface_fee.val(data.cpo_surface_fee);
                        pcb_set_data.cpo_smaterial_fee.val(data.cpo_smaterial_fee);
                        pcb_set_data.cpo_heart_pp_fee.val(data.cpo_heart_pp_fee);
                        pcb_set_data.cpo_other_all_fee.val(data.cpo_other_all_fee);
                        pcb_set_data.cpo_gold_finger_fee.val(data.cpo_gold_finger_fee);
                    }

                });
            }
    }
    //数据传递隐藏
    function pcb_data_special(data_obj) {
        var special_form_obj = special_form_rendering();
        special_form_obj.TG_values.val(data_obj.TG_values);
        special_form_obj.Semi_hole.val(data_obj.Semi_hole);
        special_form_obj.Edge_plating.val(data_obj.Edge_plating);
        special_form_obj.Impedance.val(data_obj.Impedance);
        special_form_obj.Blind_and_buried_hole.val(data_obj.Blind_and_buried_hole);
        // special_form_obj.Impedance_contous.val(data_obj.Impedance_contous);
        special_form_obj.Countersunk_deep_holes.val(data_obj.Countersunk_deep_holes);
        special_form_obj.Blind_hole_structure.val(data_obj.Blind_hole_structure);
        // special_form_obj.Laminating_times.val(data_obj.Laminating_times);
        special_form_obj.Press_fit.val(data_obj.Press_fit);
        special_form_obj.Carbon_oil.val(data_obj.Carbon_oil);
        // special_form_obj.Plugging_resin_times.val(data_obj.Plugging_resin_times);
        special_form_obj.Peelable_mask.val(data_obj.Peelable_mask);
        special_form_obj.Coil_plate.val(data_obj.Coil_plate);
        special_form_obj.Number_back_drilling.val(data_obj.Number_back_drilling);
        special_form_obj.Depth_control_routing.val(data_obj.Depth_control_routing);
        // special_form_obj.Control_deep_gong.val(data_obj.Control_deep_gong);
        special_form_obj.Laser_drilling.val(data_obj.Laser_drilling);
        // special_form_obj.Number_V_CUT_knives.val(data_obj.Number_V_CUT_knives);
        // special_form_obj.Number_of_drop_V_CUT.val(data_obj.Number_of_drop_V_CUT);
        special_form_obj.The_space_for_drop_V_cut.val(data_obj.The_space_for_drop_V_cut);
        special_form_obj.Min_line_width.val(data_obj.Min_line_width);
        special_form_obj.Min_line_space.val(data_obj.Min_line_space);
        special_form_obj.Min_aperture.val(data_obj.Min_aperture);
        special_form_obj.Inner_hole_line.val(data_obj.Inner_hole_line);
        special_form_obj.BGA_center.val(data_obj.BGA_center);
        special_form_obj.Thickness_ratio.val(data_obj.Thickness_ratio);
        special_form_obj.Total_holes.val(data_obj.Total_holes);
        // special_form_obj.Hole_density.val(data_obj.Hole_density);
        special_form_obj.Copper_weight_wall.val(data_obj.Copper_weight_wall);
        special_form_obj.Number_core.val(data_obj.Number_core);
        special_form_obj.PP_number.val(data_obj.PP_number);
        special_form_obj.Acceptable_stanadard.val(data_obj.Acceptable_stanadard);
        special_form_obj.Total_test_points.val(data_obj.Total_test_points);

    }

    //创建订单
    // $('#add_to_cart').click(function () {
    //     $('#pcb_order_load_content').css('display', 'block');
    // });

    //改变数量
    $('#cpo_change_quantity').change(function () {
        var pcba_src_order_id = $('#pcba_src_order_id');
        var pcb_old_qty = parseInt($('#pcb_quo .pcb_qty').html());
        if(pcba_src_order_id.val()){
            $('#cpo_change_quantity').val(pcb_old_qty);
            alert("The current quantity is the number of PCBA orders and cannot be changed !");
            return false
        }else {
            $('#shop_pcb_confirm_urgent .pcb_new_qty').val($(this).val());
            $('#cpo_pcb_expedited_select').css('display', 'none');
            $('#cpo_pcb_detail_peice .cpo_pcb_select_td_parent').css('display', 'none');
            var pcb_value = pcb_confirm_form_value();
            var pcb_urgent = "Normal leading time";
            ajax.jsonRpc("/shop_pcb_confirm_urgent_service", 'call', {
                'pcb_quantity': $(this).val(),
                'pcb_length': pcb_value.pcb_length,
                'pcb_breadth': pcb_value.pcb_breadth,
                'pcb_pcs_size': pcb_value.pcb_pcs_size,
                'pcb_item_size': pcb_value.pcb_item_size,
                'pcb_layer': pcb_value.pcb_layer,
                'pcb_type': pcb_value.pcb_type,
                'pcb_thickness': pcb_value.pcb_thickness,
                'pcb_inner_copper': pcb_value.pcb_inner_copper,
                'pcb_outer_copper': pcb_value.pcb_outer_copper,
                'pcb_solder_mask': pcb_value.pcb_solder_mask,
                'pcb_silkscreen_color': pcb_value.pcb_silkscreen_color,
                'pcb_surfaces': pcb_value.pcb_surface,
                'pcb_vias': pcb_value.pcb_vias,
                'cpo_pcb_frame':pcb_value.cpo_pcb_frame,
                'pcb_test': pcb_value.pcb_test,
                'pcb_qty_unit': pcb_value.pcb_qty_unit,
                'pcb_special': pcb_value.pcb_special_requirements,
                'pcb_urgent': pcb_urgent
            }).then(function (data) {
                var pcb_quantity_all = data.pcb_quantity + " " + data.pcb_qty_unit;
                if (data.error) {
                    $('#pcb_myModal').modal('hide');
                    $('#cpo_change_quantity').val(pcb_old_qty);
                    alert(data.error);
                    return
                } else {
                    // $('#pcb_quo .pcb_expedited_prent').css('display', 'none');
                    $('#cpo_pcb_detail_peice .cpo_pcb_span_delivery_period').html(data.cpo_delivery);
                    $('#pcb_quo .pcb_qty').html(pcb_quantity_all);
                    $('#pcb_quo .pcb_area').html(data.cpo_flat_area);
                    $('#cpo_pcb_detail_peice .smt_price_total').html(data.all_fee);
                    $('#cpo_pcb_detail_peice .pcb_board_prive').html(data.part_fee);
                    $('#pcb_quo .pcb_expedited_days').html("");
                    $('#pcb_expedited_days').val("");
                    $('#product_details .js_add_cart_variants .pcb_urgent_select_result').val($('#pcb_quo a.pcb_active').html())
                }
            })
        }
    });

    //点击加急处理
    $('#pcb_quo .pcb_urgent').click(function () {

        $(this).addClass('pcb_active').siblings().removeClass('pcb_active');
        var pcb_value = pcb_confirm_form_value();
        var pcb_urgent_select_btn = $('#pcb_quo a.pcb_active').html();
        if(pcb_urgent_select_btn == 'Expedited'){
            var pcb_old_qty = parseInt($('#pcb_quo .pcb_qty').html());
            var pcb_urgent = $(this).html();
            ajax.jsonRpc("/shop_pcb_confirm_urgent_service", 'call',{
                'pcb_quantity':pcb_value.pcb_new_quantity,
                'pcb_length':pcb_value.pcb_length,
                'pcb_breadth':pcb_value.pcb_breadth,
                'pcb_pcs_size':pcb_value.pcb_pcs_size,
                'pcb_item_size':pcb_value.pcb_item_size,
                'pcb_layer':pcb_value.pcb_layer,
                'pcb_type':pcb_value.pcb_type,
                'pcb_thickness':pcb_value.pcb_thickness,
                'pcb_inner_copper':pcb_value.pcb_inner_copper,
                'pcb_outer_copper':pcb_value.pcb_outer_copper,
                'pcb_solder_mask':pcb_value.pcb_solder_mask,
                'pcb_silkscreen_color':pcb_value.pcb_silkscreen_color,
                'pcb_surfaces':pcb_value.pcb_surface,
                'pcb_vias':pcb_value.pcb_vias,
                'cpo_pcb_frame':pcb_value.cpo_pcb_frame,
                'pcb_test':pcb_value.pcb_test,
                'pcb_qty_unit':pcb_value.pcb_qty_unit,
                'pcb_special':pcb_value.pcb_special_requirements,
                'pcb_old_qty': pcb_old_qty,
                'pcb_urgent': pcb_urgent
            }).then(function (data) {
                if(data.error){
                    $('#pcb_myModal').modal('hide');
                    $('#pcb_quo .pcb_urgent_service').removeClass('pcb_active').siblings('a').addClass('pcb_active');
                    $('#cpo_change_quantity').val(data.pcb_quantity);
                    $('#product_details .js_add_cart_variants .pcb_urgent_select_result').val("Normal leading time")
                    alert(data.error);
                    $('#cpo_pcb_detail_peice .cpo_pcb_select_td_parent').css('display', 'none');
                    return
                }else{
                    $('#pcb_myModal').modal('show');
                    $('#pcb_myModal .pcb_confirm_qty').val(data.pcb_quantity);
                    $('#pcb_myModal .pcb_confirm_area').val(data.cpo_flat_area);
                    var time_list = data.cpo_quick_time_list;
                    for(var i=1;i<=time_list.length;i++){
                        if(i == 1){
                            $('#pcb_myModal .radio').append("<a class=\"form-control pcb_urgent_day pcb_active\">"+ i +" Day</a>");
                        }else{
                            $('#pcb_myModal .radio').append("<a class=\"form-control pcb_urgent_day\">"+ i +" Day</a>");
                        }
                    }
                    $('#cpo_pcb_detail_peice .cpo_pcb_select_td_parent').css('display', 'table-row');
                }
            })
        }else{
            var pcb_old_qty = $('#cpo_change_quantity').val();
            var pcb_urgent = $(this).html();
            ajax.jsonRpc("/shop_pcb_confirm_urgent_service", 'call',{
                'pcb_quantity':pcb_old_qty,
                'pcb_length':pcb_value.pcb_length,
                'pcb_breadth':pcb_value.pcb_breadth,
                'pcb_pcs_size':pcb_value.pcb_pcs_size,
                'pcb_item_size':pcb_value.pcb_item_size,
                'pcb_layer':pcb_value.pcb_layer,
                'pcb_type':pcb_value.pcb_type,
                'pcb_thickness':pcb_value.pcb_thickness,
                'pcb_inner_copper':pcb_value.pcb_inner_copper,
                'pcb_outer_copper':pcb_value.pcb_outer_copper,
                'pcb_solder_mask':pcb_value.pcb_solder_mask,
                'pcb_silkscreen_color':pcb_value.pcb_silkscreen_color,
                'pcb_surfaces':pcb_value.pcb_surface,
                'pcb_vias':pcb_value.pcb_vias,
                'cpo_pcb_frame':pcb_value.cpo_pcb_frame,
                'pcb_test':pcb_value.pcb_test,
                'pcb_qty_unit':pcb_value.pcb_qty_unit,
                'pcb_special':pcb_value.pcb_special_requirements,
                'pcb_urgent': pcb_urgent
            }).then(function (data) {
                var pcb_quantity_all = data.pcb_quantity +" "+data.pcb_qty_unit;
                if(data.error){
                    $('#pcb_myModal').modal('hide');
                    $('#product_details .js_add_cart_variants .pcb_urgent_select_result').val("Normal leading time")
                    alert(data.error);
                    return
                }else{
                    $('#pcb_myModal').modal('show');
                    // $('#pcb_quo .pcb_expedited_prent').css('display', 'none');
                    $('#pcb_quo .pcb_span_delivery_period').html(data.cpo_delivery);
                    $('#pcb_quo .pcb_qty').html(pcb_quantity_all);
                    $('#pcb_quo .pcb_area').html(data.cpo_flat_area);
                    $('#cpo_pcb_detail_peice .smt_price_total').html(data.all_fee);
                    $('#pcb_quo .pcb_expedited_days').html("");
                    $('#pcb_expedited_days').val("");
                    $('#product_details .js_add_cart_variants .pcb_urgent_select_result').val($('#pcb_quo a.pcb_active').html())
                }
            })
        }

    });
    //选择加急天数
    $('#pcb_myModal .radio').delegate('a.pcb_urgent_day','click',function(){
        $(this).addClass('pcb_active').siblings('a').removeClass('pcb_active');
        return false;
    });
    //选中加急天数，返回加急后的价格
    $('#pcb_comfirm_btn').click(function () {
        var pcb_old_qty = parseInt($('#pcb_quo .pcb_qty').html());
        var pcb_value = pcb_confirm_form_value();
        var pcb_expedited_days = $('#pcb_myModal .pcb_confirm_radio a.pcb_active').html();
        if(pcb_expedited_days){
            ajax.jsonRpc("/shop_pcb_confirm_urgent_service", 'call',{
                'pcb_quantity':pcb_value.pcb_new_quantity,
                'pcb_length':pcb_value.pcb_length,
                'pcb_breadth':pcb_value.pcb_breadth,
                'pcb_pcs_size':pcb_value.pcb_pcs_size,
                'pcb_item_size':pcb_value.pcb_item_size,
                'pcb_layer':pcb_value.pcb_layer,
                'pcb_type':pcb_value.pcb_type,
                'pcb_thickness':pcb_value.pcb_thickness,
                'pcb_inner_copper':pcb_value.pcb_inner_copper,
                'pcb_outer_copper':pcb_value.pcb_outer_copper,
                'pcb_solder_mask':pcb_value.pcb_solder_mask,
                'pcb_silkscreen_color':pcb_value.pcb_silkscreen_color,
                'pcb_surfaces':pcb_value.pcb_surface,
                'pcb_vias':pcb_value.pcb_vias,
                'cpo_pcb_frame':pcb_value.cpo_pcb_frame,
                'pcb_test':pcb_value.pcb_test,
                'pcb_qty_unit':pcb_value.pcb_qty_unit,
                'pcb_special':pcb_value.pcb_special_requirements,
                'pcb_old_qty': pcb_old_qty,
                'pcb_expedited_days':pcb_expedited_days
            }).then(function (data) {
                $('#cpo_pcb_expedited_select').css('display', 'table');
                var pcb_quantity_all = data.pcb_quantity +" "+data.pcb_qty_unit;
                $('#pcb_myModal').modal('hide');
                $('#pcb_myModal .radio').empty();
                // $('#pcb_quo .pcb_expedited_prent').css('display', 'table-row');
                $('#pcb_quo .pcb_expedited_days').html(data.pcb_expedited_days);
                $('#pcb_quo .pcb_span_delivery_period').html(data.cpo_delivery);
                $('#pcb_quo .pcb_qty').html(pcb_quantity_all);
                $('#pcb_quo .pcb_area').html(data.cpo_flat_area);
                $('#cpo_pcb_expedited_select .pcb_board_prive').html(data.part_fee);
                $('#cpo_pcb_expedited_select .pcb_stencil_cost').html(data.cpo_engineering_fee);
                $('#cpo_pcb_expedited_select .pcb_process_fee').html(data.pcb_process_fee);
                $('#cpo_pcb_expedited_select .cpo_film_all_fee').html(data.cpo_film_all_fee);
                $('#cpo_pcb_expedited_select .pcb_e_test_fixture').html(data.cpo_test_fee);
                $('#cpo_pcb_expedited_select .smt_price_total').html(data.all_fee);
                $('#pcb_expedited_days').val(data.pcb_expedited_days);
                $('#product_details .js_add_cart_variants .pcb_urgent_select_result').val($('#pcb_quo a.pcb_active').html());
            })
        }else{
            $('#pcb_myModal').modal('hide');
            $('#pcb_myModal .radio').empty();
            $('#pcb_quo .pcb_expedited_days').css('display', 'none');
            $('#product_details .js_add_cart_variants .pcb_urgent_select_result').val("Normal leading time");
            alert('Sorry! The number you choose cannot be expedited!');
        }

    });
    $('#pcb_comfirm_cancel').click(function () {
        var cpo_pcb_jiaji = $('#pcb_quo .pcb_expedited_days').html();
        $('#pcb_myModal .radio').empty();
        if(cpo_pcb_jiaji){

        }else{
            $('#pcb_quo a.pcb_active').removeClass('pcb_active').siblings('a').addClass('pcb_active');
            $('#product_details .js_add_cart_variants .pcb_urgent_select_result').val("Normal leading time");
            $('#cpo_change_quantity').val(parseInt($('#pcb_quo .pcb_qty').html()));
            $('#cpo_pcb_expedited_select').css('display', 'none');
            $('#cpo_pcb_detail_peice .cpo_pcb_select_td_parent').css('display', 'none');
        }
    });
    //鼠标悬停添加样式
    $('#cpo_pcb_detail_peice').mouseover(function () {
        if($('#cpo_pcb_expedited_select').css('display') == 'table'){
            $(this).css({'border': '2px solid #337ab7', 'cursor': 'pointer'});
        }else{
            $(this).css('cursor', 'default');
        }
    }).mouseout(function () {
        if($('#cpo_pcb_detail_peice .cpo_pcb_select_delivery_period').hasClass('pcb_active')){
            // $(this).css({'border': '2px solid #ddd','cursor': 'pointer'});
        }else{
            $(this).css({'border': 'none', 'border-top': '1px solid #ddd'});
        }

    });
    $('#cpo_pcb_expedited_select').mouseover(function () {
        $(this).css({'border': '2px solid #337ab7', 'cursor': 'pointer'});
    }).mouseout(function () {
        if($('#cpo_pcb_expedited_select .cpo_pcb_select_delivery_period').hasClass('pcb_active')){

        }else{
            $(this).css({'border': 'none', 'border-top': '1px solid #ddd'});
        }
        // $(this).css('border-top', '1px solid #ddd');
    });
    //最终选择加急或者不加急
    $('#cpo_pcb_detail_peice').click(function () {
        var cpo_pcb_expedited = $('#cpo_pcb_expedited_select .cpo_pcb_select_delivery_period');
        var cpo_delivery = $('#cpo_pcb_detail_peice .cpo_pcb_span_delivery_period').html();
        if(cpo_pcb_expedited.hasClass('pcb_active')){
            cpo_pcb_expedited.removeClass('pcb_active');
            if($('#cpo_pcb_expedited_select').css('display') == "table"){
                $('#cpo_pcb_detail_peice .cpo_pcb_select_delivery_period').addClass('pcb_active');
                // $(this).css('border', 'aliceblue');
                $(this).css('border', '2px solid #337ab7');
                cpo_pcb_expedited.parents('table').css('border', 'aliceblue');
                cpo_pcb_expedited.parents('table').css('border-top', '1px solid #ddd');
                $('#cpo_delivery').val(cpo_delivery);
                $('#pcb_expedited_days').val("");
            }else{
                $(this).css({'border': 'none', 'border-top': '1px solid #ddd'});
            }
        }else{
            if($('#cpo_pcb_expedited_select').css('display') == "table"){
                $('#cpo_pcb_detail_peice .cpo_pcb_select_delivery_period').addClass('pcb_active');
                // $(this).css('border', 'aliceblue');
                $(this).css('border', '2px solid #337ab7');
                cpo_pcb_expedited.parents('table').css('border', 'aliceblue');
                cpo_pcb_expedited.parents('table').css('border-top', '1px solid #ddd');
                $('#cpo_delivery').val(cpo_delivery);
                $('#pcb_expedited_days').val("");
            }else{
                $(this).css({'border': 'none', 'border-top': '1px solid #ddd'});
            }
        }
    });

    $('#cpo_pcb_expedited_select').click(function () {
        var cpo_delivery = $('#cpo_pcb_expedited_select .pcb_span_delivery_period').html();
        var cpo_expedited_days = $('#cpo_pcb_expedited_select .pcb_expedited_days').html();
        var cpo_pcb_normal = $('#cpo_pcb_detail_peice .cpo_pcb_select_delivery_period');
        if(cpo_pcb_normal.hasClass('pcb_active')){
            cpo_pcb_normal.removeClass('pcb_active');
            $('#cpo_pcb_expedited_select .cpo_pcb_select_delivery_period').addClass('pcb_active');
            // $(this).css('border', 'aliceblue');
            $(this).css('border', '2px solid #337ab7');
            cpo_pcb_normal.parents('table').css('border', 'aliceblue');
            cpo_pcb_normal.parents('table').css('border-top', '1px solid #ddd');
            $('#cpo_delivery').val(cpo_delivery);
            $('#pcb_expedited_days').val(cpo_expedited_days);
        }else{
            cpo_pcb_normal.removeClass('pcb_active');
            $('#cpo_pcb_expedited_select .cpo_pcb_select_delivery_period').addClass('pcb_active');
            // $(this).css('border', 'aliceblue');
            $(this).css('border', '2px solid #337ab7');
            cpo_pcb_normal.parents('table').css('border', 'aliceblue');
            cpo_pcb_normal.parents('table').css('border-top', '1px solid #ddd');
            $('#cpo_delivery').val(cpo_delivery);
            $('#pcb_expedited_days').val(cpo_expedited_days);
        }
    });

    //Form 值
    function pcb_confirm_form_value() {
        var pcb_new_quantity = $('#shop_pcb_confirm_urgent input[name="pcb_quantity"]').val();
        var pcb_length = $('#shop_pcb_confirm_urgent input[name="pcb_length"]').val();
        var pcb_breadth = $('#shop_pcb_confirm_urgent input[name="pcb_breadth"]').val();
        var pcb_pcs_size = $('#shop_pcb_confirm_urgent input[name="pcb_pcs_size"]').val();
        var pcb_item_size = $('#shop_pcb_confirm_urgent input[name="pcb_item_size"]').val();
        var pcb_fg_gold_thickness = $('#shop_pcb_confirm_urgent input[name="pcb_fg_gold_thickness"]').val();
        var pcb_fg_gold_size_width = $('#shop_pcb_confirm_urgent input[name="pcb_fg_gold_size_width"]').val();
        var pcb_fg_gold_size_height = $('#shop_pcb_confirm_urgent input[name="pcb_fg_gold_size_height"]').val();
        var pcb_fg_size = $('#shop_pcb_confirm_urgent input[name="pcb_fg_size"]').val();
        var pcb_layer = $('#shop_pcb_confirm_urgent input[name="pcb_layer"]').val();
        var pcb_type = $('#shop_pcb_confirm_urgent input[name="pcb_type"]').val();
        var pcb_thickness = $('#shop_pcb_confirm_urgent input[name="pcb_thickness"]').val();
        var pcb_inner_copper = $('#shop_pcb_confirm_urgent input[name="pcb_inner_copper"]').val();
        var pcb_outer_copper = $('#shop_pcb_confirm_urgent input[name="pcb_outer_copper"]').val();
        var pcb_solder_mask = $('#shop_pcb_confirm_urgent input[name="pcb_solder_mask"]').val();
        var pcb_silkscreen_color = $('#shop_pcb_confirm_urgent input[name="pcb_silkscreen_color"]').val();
        var pcb_surface = $('#shop_pcb_confirm_urgent input[name="pcb_surface"]').val();
        var pcb_vias = $('#shop_pcb_confirm_urgent input[name="pcb_vias"]').val();
        var cpo_pcb_frame = $('#shop_pcb_confirm_urgent input[name="cpo_pcb_frame"]').val();
        var pcb_test = $('#shop_pcb_confirm_urgent input[name="pcb_test"]').val();
        var pcb_qty_unit = $('#shop_pcb_confirm_urgent input[name="pcb_qty_unit"]').val();
        var pcb_coated_area = $('#shop_pcb_confirm_urgent input[name="pcb_coated_area"]').val();
        var pcb_nickel_thickness = $('#shop_pcb_confirm_urgent input[name="pcb_nickel_thickness"]').val();

        var TG_values = $('#shop_pcb_confirm_urgent input[name="TG_values"]').val();
        var Semi_hole = $('#shop_pcb_confirm_urgent input[name="Semi_hole"]').val();
        var Edge_plating = $('#shop_pcb_confirm_urgent input[name="Edge_plating"]').val();
        var Impedance = $('#shop_pcb_confirm_urgent input[name="Impedance"]').val();
        var Blind_and_buried_hole = $('#shop_pcb_confirm_urgent input[name="Blind_and_buried_hole"]').val();
        // var Impedance_contous = $('#shop_pcb_confirm_urgent input[name="Impedance_contous"]').val();
        var Countersunk_deep_holes = $('#shop_pcb_confirm_urgent input[name="Countersunk_deep_holes"]').val();
        var Blind_hole_structure = $('#shop_pcb_confirm_urgent input[name="Blind_hole_structure"]').val();
        // var Laminating_times = $('#shop_pcb_confirm_urgent input[name="Laminating_times"]').val();
        var Press_fit = $('#shop_pcb_confirm_urgent input[name="Press_fit"]').val();
        var Carbon_oil = $('#shop_pcb_confirm_urgent input[name="Carbon_oil"]').val();
        var Peelable_mask = $('#shop_pcb_confirm_urgent input[name="Peelable_mask"]').val();
        var Number_back_drilling = $('#shop_pcb_confirm_urgent input[name="Number_back_drilling"]').val();
        var Depth_control_routing = $('#shop_pcb_confirm_urgent input[name="Depth_control_routing"]').val();
        var Laser_drilling = $('#shop_pcb_confirm_urgent input[name="Laser_drilling"]').val();
        var The_space_for_drop_V_cut = $('#shop_pcb_confirm_urgent input[name="The_space_for_drop_V_cut"]').val();
        var Min_line_width = $('#shop_pcb_confirm_urgent input[name="Min_line_width"]').val();
        var Min_line_space = $('#shop_pcb_confirm_urgent input[name="Min_line_space"]').val();
        var Min_aperture = $('#shop_pcb_confirm_urgent input[name="Min_aperture"]').val();
        var Inner_hole_line = $('#shop_pcb_confirm_urgent input[name="Inner_hole_line"]').val();
        var Total_holes = $('#shop_pcb_confirm_urgent input[name="Total_holes"]').val();
        var Copper_weight_wall = $('#shop_pcb_confirm_urgent input[name="Copper_weight_wall"]').val();
        var Number_core = $('#shop_pcb_confirm_urgent input[name="Number_core"]').val();
        var PP_number = $('#shop_pcb_confirm_urgent input[name="PP_number"]').val();
        var Acceptable_stanadard = $('#shop_pcb_confirm_urgent input[name="Acceptable_stanadard"]').val();
        var Total_test_points = $('#shop_pcb_confirm_urgent input[name="Total_test_points"]').val();

        var confirm_value = {
            'pcb_new_quantity': pcb_new_quantity,
            'pcb_length': pcb_length,
            'pcb_breadth': pcb_breadth,
            'pcb_pcs_size': pcb_pcs_size,
            'pcb_item_size': pcb_item_size,
            'pcb_layer': pcb_layer,
            'pcb_type': pcb_type,
            'pcb_thickness': pcb_thickness,
            'pcb_inner_copper': pcb_inner_copper,
            'pcb_outer_copper': pcb_outer_copper,
            'pcb_solder_mask': pcb_solder_mask,
            'pcb_silkscreen_color': pcb_silkscreen_color,
            'pcb_surface': {
                'pcb_surface': pcb_surface,
                'pcb_fg_gold_thickness': pcb_fg_gold_thickness,
                'pcb_fg_gold_size_width': pcb_fg_gold_size_width,
                'pcb_fg_gold_size_height': pcb_fg_gold_size_height,
                'pcb_fg_size': pcb_fg_size,
                'pcb_coated_area': pcb_coated_area,
                'pcb_nickel_thickness': pcb_nickel_thickness
            },
            'pcb_vias': pcb_vias,
            'cpo_pcb_frame': cpo_pcb_frame,
            'pcb_test': pcb_test,
            'pcb_qty_unit': pcb_qty_unit,
            'pcb_special_requirements': {
                'TG_values': TG_values,
                'Semi_hole': Semi_hole,
                'Edge_plating':Edge_plating,
                'Impedance':Impedance,
                'Blind_and_buried_hole':Blind_and_buried_hole,
                // 'Impedance_contous':Impedance_contous,
                'Countersunk_deep_holes':Countersunk_deep_holes,
                'Blind_hole_structure':Blind_hole_structure,
                // 'Laminating_times':Laminating_times,
                'Press_fit':Press_fit,
                'Carbon_oil':Carbon_oil,
                'Peelable_mask':Peelable_mask,
                'Number_back_drilling':Number_back_drilling,
                'Depth_control_routing':Depth_control_routing,
                'Laser_drilling':Laser_drilling,
                'The_space_for_drop_V_cut':The_space_for_drop_V_cut,
                'Min_line_width':Min_line_width,
                'Min_line_space':Min_line_space,
                'Min_aperture':Min_aperture,
                'Inner_hole_line':Inner_hole_line,
                'Total_holes':Total_holes,
                'Copper_weight_wall':Copper_weight_wall,
                'Number_core':Number_core,
                'PP_number':PP_number,
                'Acceptable_stanadard':Acceptable_stanadard,
                'Total_test_points':Total_test_points,
            }

        }
        return confirm_value
    }
    $()
    $('#cpo_ele_cart_att #cpo_down_excel').click(function (e) {
        //var $form = $(this).next('form');
        //var $form = $('form[id="cpo_sale_order_merger"]');
        var $form = $(e.currentTarget.parentElement).find('form[id="cpo_sale_order_merger"]');
        $form.submit();
        ajax.jsonRpc("/cpo_merger_order", 'call',{
            // 'cpo_sale_order_name': cpo_sale_order_name
        }).then(function (data) {
            if(data.pcb_supply){
                window.location.href ="/pcb";
                var $form = $('form[id="cpo_sale_order_merger"]');
                $form.submit();
            }
        })

    });

    //确认订单前检查所有的数据
   //  $('#pcb_quo .check_all_data_btn').click(function () {
   //      if(!$(this).hasClass('check_data_active')){
   //          $(this).addClass('check_data_active');
   //          $(this).parents('table').css('border','1px solid #ddd');
   //      }else{
   //          $(this).removeClass('check_data_active');
   //      }
   //      return false
   //  });
   //  $('#pcb_quo .pcb_details_all_data').click(function () {
   //
   //  });
   //   $('#pcb_quo .pcb_details_all_data').click(function () {
   //      var check_click_table = $('#pcb_quo .check_all_data_btn');
   //      // check_click_table.toggleClass('check_data_active');
   //      if(!check_click_table.hasClass('check_data_active')){
   //          check_click_table.addClass('check_data_active');
   //          $(this).css('border','1px solid #ddd');
   //      }else{
   //          check_click_table.removeClass('check_data_active');
   //      }
   //  });
   // $('#pcb_quo .pcb_details_all_data').mouseover(function () {
   //      $(this).css('cursor', 'pointer');
   //  }).mouseout(function () {
   //      $(this).css('cursor', 'default');
   //  });


});
