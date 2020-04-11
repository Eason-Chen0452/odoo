odoo.define('website_cpo_pages.website_pcb_package_price', function (require) {
    "use strict";

    var widgets = require('web_editor.widget');
    var Widget = require('web.Widget');
    var base = require('web_editor.base');
    var ajax = require("web.ajax");
    var core = require('web.core');
    var config = require("web.config");

    //------------Package Price a标签点击----------------------------------------------------------------------
    // $('#cpo_pcb_package_pirce a').on('click', function () {
    //     if(!$(this).hasClass('cpo_back_color')){
    //         $(this).addClass('cpo_input_active').siblings('a').removeClass('cpo_input_active');
    //     }
    // });
    // $('#cpo_pcb_package_pirce .cpo_surface_treatment a').on('click', function () {
    //     if(!$(this).hasClass('cpo_back_color')){
    //         $('#cpo_pcb_package_pirce .cpo_surface_treatment a').each(function () {
    //             $(this).removeClass('cpo_input_active');
    //         })
    //         if($(this).children('span').html() == 'Immersion gold'){
    //             $('.cpo_immersion_gold_request').css('display', 'block');
    //         }else{
    //             $('.cpo_immersion_gold_request').css('display', 'none');
    //         }
    //         $(this).addClass('cpo_input_active').siblings('a').removeClass('cpo_input_active');
    //     }
    // });
    //---------------------------------------------------------------------------------------

    // 特殊工艺选择
    // $('#cpo_proce_and_mater li').on('click', function () {
    //     var all_page = $('#all_pages_content_list li.pages_content');
    //     var all_caclula = $('#pages_calcula_title_list li.pages_title');
    //     $(this).addClass('cpo_input_active').siblings('li').removeClass('cpo_input_active');
    //     all_page.eq($(this).index()).addClass('pages-active').siblings('li').removeClass('pages-active');
    //     all_caclula.eq($(this).index()).addClass('pages-title-ac').siblings('li').removeClass('pages-title-ac');
    // });

    // 特殊工艺
    // $('.cpo_material_list li').on('click', function () {
    //     var $li_value = $(this).children().html();
    //     var $select = $('.cpo_input_needpcb_group .cpo_material_select');
    //     var $values = $('.cpo_material_values .cpo_input_needpcb_group');
    //     $(this).addClass('cpo_input_active').siblings('li').removeClass('cpo_input_active');
    //     $select.eq($(this).index()).addClass('cpo-select-active').siblings('select').removeClass('cpo-select-active');
    //     $values.eq($(this).index()).removeClass('cpo-none').addClass('cpo-block');
    //     $values.eq($(this).index()).siblings().removeClass('cpo-block').addClass('cpo-none');
    //     if($li_value == 'Rogers'){
    //         $('.cpo_rogers_special').each(function () {
    //             $(this).removeClass('cpo-none').addClass('cpo-block');
    //         });
    //     }else{
    //         $('.cpo_rogers_special').each(function () {
    //             $(this).removeClass('cpo-block').addClass('cpo-none');
    //         });
    //     }
    // });

    // 打包价选择颜色
    $('.cpo-sm-sc .cpo-box-select').on('change', function () {
        var $sl_val = $(this).val();
        if($sl_val == 'No'){
            $(this).siblings('span').css('background-color', "");
            $(this).siblings('span').html('No');
        }else{
            $(this).siblings('span').css('background-color', $sl_val);
            $(this).siblings('span').html('');
        }
    });
    // 层数选择
    // $('.cpo_package_meterial_layer .cpo_layers').on('change', function () {
    // $('.quo-active .cpo_meterial_layer .cpo_layers').on('change', function () {
    //     var $this_val = $(this).val();
    //     pcbSelectLayer($this_val)
    //     // var cpo_inner_outer = $('.quo-active .cpo_inner_outer');
    //     // var cpo_heavy_copper = $('.quo-active .cpo_heavy_copper .outer_copper');
    //     // var $select_val = $(this).val();
    //     // if($select_val > 2){
    //     //     $('.quo-active .cpo-box .inner_copper').val('0.5');
    //     //     if(cpo_heavy_copper.length > 0){
    //     //         cpo_heavy_copper.empty();
    //     //         cpo_heavy_copper.append('\n'+
    //     //             '<option value="1">1</option>\n' +
    //     //             '<option value="2">2</option>\n' +
    //     //             '<option value="3">3</option>\n' +
    //     //             '<option value="4">4</option>\n' +
    //     //             '<option value="5">5</option>')
    //     //     }
    //     // }else{
    //     //     $('.quo-active .cpo-box .inner_copper').val('0');
    //     //     if(cpo_heavy_copper.length > 0){
    //     //         cpo_heavy_copper.empty();
    //     //         cpo_heavy_copper.append('\n'+
    //     //             '<option value="1">1</option>\n' +
    //     //             '<option value="2">2</option>\n' +
    //     //             '<option value="3">3</option>\n' +
    //     //             '<option value="4">4</option>\n' +
    //     //             '<option value="5">5</option>\n' +
    //     //             '<option value="6">6</option>\n' +
    //     //             '<option value="7">7</option>\n' +
    //     //             '<option value="8">8</option>\n' +
    //     //             '<option value="9">9</option>\n' +
    //     //             '<option value="10">10</option>\n' +
    //     //             '<option value="11">11</option>\n' +
    //     //             '<option value="12">12</option>\n' +
    //     //             '<option value="13">13</option>\n' +
    //     //             '<option value="14">14</option>\n' +
    //     //             '<option value="15">15</option>\n' +
    //     //             '<option value="16">16</option>\n' +
    //     //             '<option value="17">17</option>\n' +
    //     //             '<option value="18">17</option>\n' +
    //     //             '<option value="19">19</option>\n' +
    //     //             '<option value="20">20</option>');
    //     //     }
    //     //     // $('.quo-active .cpo-box .inner_copper').val('0.5');
    //     // }
    // });
    // function pcbSelectLayer(value){
    //     var cpo_heavy_copper = $('.quo-active .cpo_heavy_copper .outer_copper');
    //     var $select_val = value;
    //     if($select_val > 2){
    //         $('.quo-active .cpo-box .inner_copper').val('0.5');
    //         if(cpo_heavy_copper.length > 0){
    //             cpo_heavy_copper.empty();
    //             cpo_heavy_copper.append('\n'+
    //                 '<option value="1">1</option>\n' +
    //                 '<option value="2">2</option>\n' +
    //                 '<option value="3">3</option>\n' +
    //                 '<option value="4">4</option>\n' +
    //                 '<option value="5">5</option>')
    //         }
    //     }else{
    //         $('.quo-active .cpo-box .inner_copper').val('0');
    //         if(cpo_heavy_copper.length > 0){
    //             cpo_heavy_copper.empty();
    //             cpo_heavy_copper.append('\n'+
    //                 '<option value="1">1</option>\n' +
    //                 '<option value="2">2</option>\n' +
    //                 '<option value="3">3</option>\n' +
    //                 '<option value="4">4</option>\n' +
    //                 '<option value="5">5</option>\n' +
    //                 '<option value="6">6</option>\n' +
    //                 '<option value="7">7</option>\n' +
    //                 '<option value="8">8</option>\n' +
    //                 '<option value="9">9</option>\n' +
    //                 '<option value="10">10</option>\n' +
    //                 '<option value="11">11</option>\n' +
    //                 '<option value="12">12</option>\n' +
    //                 '<option value="13">13</option>\n' +
    //                 '<option value="14">14</option>\n' +
    //                 '<option value="15">15</option>\n' +
    //                 '<option value="16">16</option>\n' +
    //                 '<option value="17">17</option>\n' +
    //                 '<option value="18">17</option>\n' +
    //                 '<option value="19">19</option>\n' +
    //                 '<option value="20">20</option>');
    //         }
    //         // $('.quo-active .cpo-box .inner_copper').val('0.5');
    //     }
    // }

    // 基材选择
    // $('.quo-active .material_select .cpo_material').on('change', function () {
    //     var $val = $(this).val();
    //     cpoCopperSelect($val);
    // });
    // // 常规板选择
    // function cpoCopperSelect(data){
    //     var cpo_heavy_copper = $('.quo-active .cpo_heavy_copper .outer_copper');
    //     if(data == 'Rogers'){
    //         if(cpo_heavy_copper.length > 0){
    //             cpo_heavy_copper.empty();
    //             cpo_heavy_copper.append('\n'+
    //                 '<option value="1">1</option>\n' +
    //                 '<option value="2">2</option>\n' +
    //                 '<option value="3">3</option>\n' +
    //                 '<option value="4">4</option>\n' +
    //                 '<option value="5">5</option>')
    //         }
    //     }else{
    //         if(cpo_heavy_copper.length > 0){
    //             cpo_heavy_copper.empty();
    //             cpo_heavy_copper.append('\n'+
    //                 '<option value="1">1</option>\n' +
    //                 '<option value="2">2</option>\n' +
    //                 '<option value="3">3</option>\n' +
    //                 '<option value="4">4</option>\n' +
    //                 '<option value="5">5</option>\n' +
    //                 '<option value="6">6</option>\n' +
    //                 '<option value="7">7</option>\n' +
    //                 '<option value="8">8</option>\n' +
    //                 '<option value="9">9</option>\n' +
    //                 '<option value="10">10</option>\n' +
    //                 '<option value="11">11</option>\n' +
    //                 '<option value="12">12</option>\n' +
    //                 '<option value="13">13</option>\n' +
    //                 '<option value="14">14</option>\n' +
    //                 '<option value="15">15</option>\n' +
    //                 '<option value="16">16</option>\n' +
    //                 '<option value="17">17</option>\n' +
    //                 '<option value="18">17</option>\n' +
    //                 '<option value="19">19</option>\n' +
    //                 '<option value="20">20</option>');
    //         }
    //     }
    // }

    // 打包价选择内铜厚时，根据层数校正
    $('.cpo_pcbpackage_quotation .layer_inner_copper .inner_copper').on('change', function () {
        var $th_val = $(this).val();
        var $select_val = $('.cpo_pcbpackage_quotation .cpo_meterial_layer select.cpo_layers').val();
        if($select_val > 2){
            if($th_val <= 0){
                $(this).val('0.5');
            }else{
                $(this).val($th_val);
            }
        }else{
            $(this).val('0');
        }
    });
    // 打包价选择层数，对应内铜厚跟着改变
    $('.cpo_pcbpackage_quotation .cpo_meterial_layer select.cpo_layers').on('change', function () {
        var $this_val = $(this).val();
        var inner_copper = $('.cpo_pcbpackage_quotation .layer_inner_copper .inner_copper');
        if($this_val > 2){
            inner_copper.val('0.5');
        }else{
            inner_copper.val('0');
        }
    });

    // 打包价表面处理
    $('.cpo_pcbpackage_quotation .surface_value').on('change', function () {
        var $val = $(this).val();
        var immersion_gold = 'Immersion gold';
        if($val.indexOf(immersion_gold) != -1){
            $('.cpo_pcbpackage_quotation .cpo-tips-content').addClass('cpo-block').removeClass('cpo-none');
        }else {
            $('.cpo_pcbpackage_quotation .cpo-tips-content').addClass('cpo-none').removeClass('cpo-block');
        }
    });
    



})