odoo.define("website_cpo_sale.pcba_quotation", function(require) {
    "use strict";

    var Widget = require('web.Widget');
    var base = require('web_editor.base');
    var ajax = require("web.ajax");
    var core = require('web.core');
    var config = require("web.config");
    var utils = require('web.utils');
    //
    var log = console.log.bind(console)

    $(".terms_conditions_btn").on("click", function () {
        var timer_con = $(".terms_conditions");
        var get_set_time = parseFloat($('#cpo_cookie_time input').val());
        var calculate_tatol = $('.calculate_tatol');
        var times = 24;
        if(get_set_time){
            times = get_set_time;
        }
        cpoDoNotShow(timer_con, times);
        if(calculate_tatol.length > 0){
            calculate_tatol.css('bottom', '0')
        }
        ajax.jsonRpc('/service/protocol', 'call').then(function () {

        })
    })
    // $('#top_menu li a').on('click', function () {
    //     var self = $(this);
    //     var my_href = $(this).attr('href');
    //     if(my_href){
    //         $(this).removeAttr("href");
    //         window.location.href = my_href;
    //     }else{
    //         return false;
    //     }
    //     //设置5S后执行添加a标签点击事件
    //     setTimeout(function(){ self.attr('href', my_href); }, 5000);
    // })

    //问号提示语
    $(function () { $("[data-toggle='tooltip']").tooltip(); });
    // 判断用户输入，长宽数量（面积大于3㎡则加收测试费）
    // PCB
    $('.quo-active select').on('change', function () {
        checkCustomerData();
    })
    $('.quo-active input[type="text"]').on('change', function () {
        checkCustomerData();
        if(this.name == "pcb_quantity"){
            getAreaBoard();
        }else if(this.name == "pcb_length"){
            getAreaBoard();
        }else if(this.name == "pcb_breadth"){
            getAreaBoard();
        }
    });
    $('.quo-active .cpo_e_test').on('change', function () {
        getAreaBoard();
    });
    // PCBA + PCB (test fee)
    $('.cpo_pcba_need_pcb .cpo_e_test').on('change', function () {
        getAreaBoard();
    });

    // 检查check数据（及时提示客户，避免客户输入无用数据）
    $('.cpo_pcb_special select').on('change', function () {
        checkCustomerData();
    })
    $('.cpo_pcb_special input[type="text"]').on('change', function () {
        checkCustomerData();
    })
    // 打包价check
    $('.cpo_pcbpackage_quotation input[type="text"]').on('change', function () {
        checkPCBPriceCustomerData()
    })
    // $('.cpo_pcbpackage_quotation select').on('change', function () {
    //     checkCustomerData();
    // })
    function checkCustomerData() {
        var showVal;
        var form_data = pcbGetFormData();
        var pcb_special = form_data.pcb_special_requirements;
        var warnning = $('.cpo-warning');
        if(form_data.quality_standard == '3'){
            showVal = 'IPC Class III is unable to quote automatically , if you are interested, please turn to personal support.';
        }else if(parseFloat(form_data.pcb_length) >= 600.00){
            showVal = 'Length ≥600mm is unable to quote automatically , if you are interested, please turn to personal support.';
        }else if(parseFloat(form_data.pcb_breadth) >= 600.00){
            showVal = 'Width ≥600mm is unable to quote automatically , if you are interested, please turn to personal support.';
        }else if(pcb_special.Laser_drilling == 'Yes'){
            // $('.generate_special_documents').css('display', 'block');
            // showVal =  'Laser drilling is unable to quote automatically , if you are interested, please turn to personal support.';
        }else if(pcb_special.Depth_control_routing == 'Yes'){
            // $('.generate_special_documents').css('display', 'block');
            // showVal = 'Depth milling unable to quote automatically , if you are interested, please turn to personal support.';
        }else if(pcb_special.The_space_for_drop_V_cut == 'Yes'){
            // $('.generate_special_documents').css('display', 'block');
            // showVal = 'Jumping v-cut is unable to quote automatically , if you are interested, please turn to personal support.';
        }else if(pcb_special.Number_back_drilling == 'Yes'){
            // $('.generate_special_documents').css('display', 'block');
            // showVal = "Back drilling is unable to quote automatically , if you are interested, please turn to personal support.";
        }else if(!pcb_special.Countersunk_deep_holes){
            // $('.generate_special_documents').css('display', 'block');
            // showVal = 'Countersunk/depth control hole is unable to quote automatically , if you are interested, please turn to personal support.';
        }else if(!pcb_special.Blind_hole_structure){
            // $('.generate_special_documents').css('display', 'block');
            // showVal = "Blind&Buried via is unable to quote automatically , if you are interested, please turn to personal support.";
        }else if(!pcb_special.Blind_and_buried_hole){
            // $('.generate_special_documents').css('display', 'block');
            // showVal = "Blind&Buried via is unable to quote automatically , if you are interested, please turn to personal support.";
        }else{
            // $('.generate_special_documents').css('display', 'none');
            showVal = null;
        }
        // console.log(showVal)
        var w_con = '<div class="alert alert-warning">\n' +
            '<a href="#" class="close" data-dismiss="alert">\n' +
            '<i class="fa fa-close"></i></a><strong>Prompt : </strong>'+showVal+'\n' +
            '<a></a>'+'\n' +
            '</div>';
        if(showVal == null){
            warnning.html('');
        }else{
            warnning.html(w_con);
            $('body,html').animate({scrollTop: 150}, 500);
        }
    }

    function getAreaBoard(){
        var area, pcb_quantity,pcb_length,pcb_breadth;
        var pcba_need_pcb = $('.cpo_pcba_need_pcb');
        if(pcba_need_pcb.length > 0){
            pcb_quantity = $('.cpo_pcba_need_pcb input[name="pcb_quantity"]').val();
            pcb_length = $('.cpo_pcba_need_pcb input[name="pcb_length"]').val();
            pcb_breadth = $('.cpo_pcba_need_pcb input[name="pcb_breadth"]').val();
        }else{
            pcb_quantity = $('.quo-active input[name="pcb_quantity"]').val();
            pcb_length = $('.quo-active input[name="pcb_length"]').val();
            pcb_breadth = $('.quo-active input[name="pcb_breadth"]').val();
        }
        area = parseFloat(pcb_length) * parseFloat(pcb_breadth) * parseFloat(pcb_quantity) / 1000000;
        if(area >= 3){
            if(pcba_need_pcb.length > 0){
                $('.cpo_pcba_need_pcb .cpo_e_test').val('E-test fixture');
            }else{
                $('.quo-active .cpo_e_test').val('E-test fixture')
            }
        }else{
            if(pcba_need_pcb.length > 0){
                $('.cpo_pcba_need_pcb .cpo_e_test').val('Free Flying Probe');
            }
            $('.quo-active .cpo_e_test').val('Free Flying Probe');
        }
    }

// 工艺选项（普通，HDI，软硬结合）--------------------------------------------------------------------
//     $('.process-box .process-item').on('click', function () {
//         var $index = $(this).index();
//         $(this).addClass('process-active').siblings().removeClass('process-active');
//         $(this).children('span').addClass('process-icon');
//         $(this).siblings().children('span').removeClass('process-icon');
//         $('.quo-content-ul .quo-li').eq($index).addClass('quo-active').siblings().removeClass('quo-active');
        // PCB 表面处理选择
        $('.quo-active .surface_treatment select.surface_value').on('change', function () {
            var $value = $(this).val();
            if($value == 'Immersion gold (2 u″)' || $value == 'Immersion gold (2 u″)'){
                $('.quo-active .cpo-tips-content').addClass('cpo-block').removeClass('cpo-none');
            }else{
                $('.quo-active .cpo-tips-content').addClass('cpo-none').removeClass('cpo-block');
            }
            // sufaceTreatment($value);
        });
        $('.quo-active .surface_combination').on('change', function () {
            var $value = $(this).val();
            sufaceTr($value);
            // if($value == 'Yes'){
            //     $('.quo-active .cpo-finger-box').addClass('cpo-block').removeClass('cpo-none');
            // }else{
            //     $('.quo-active .cpo-finger-box').addClass('cpo-none').removeClass('cpo-block');
            // }
            // optionalCom($value);
        });
    // 表面处理选择
    function sufaceTr(value) {
        if(value == 'No'){
            $('.quo-active .cpo-finger-box').addClass('cpo-none').removeClass('cpo-block');
        }else{
            $('.quo-active .cpo-finger-box').addClass('cpo-block').removeClass('cpo-none');
        }
    }

        // 层数选择
        $('.quo-active .cpo_meterial_layer .cpo_layers').on('change', function () {
            var $this_val = $(this).val();
            pcbSelectLayer($this_val)
        });
        // 内铜厚
        $('.quo-active .cpo-box .inner_copper').on('change', function () {
        var $this = $(this);
            innerCopper($this)
        });
        // PCB
        $('.quo-active input[type="text"]').on('change', function () {
            if(this.name == "pcb_quantity"){
                getAreaBoard();
            }else if(this.name == "pcb_length"){
                getAreaBoard();
            }else if(this.name == "pcb_breadth"){
                getAreaBoard();
            }
        });
        $('.quo-active .cpo_e_test').on('change', function () {
            getAreaBoard();
        });

    // 文件上传 0.5 开始
    $('#select_file_form').on('change', '.select_file_05', function () {
        $(this).prev().val($(this).val());
    });
    // 确认上传
    $('#upload_05').on('click', function () {
        var fileObf = $('#select_file_form').find('input#upload')[0];
        var fileType = $('#select_file_form').find('input[name="file_type"]').val();
        if(!fileObf.files[0]){
            webAlert("Please select a file !", null, false);
            // alert('Please select a file!');
            return false;
        }
        // 文件格式
        var file_format = fileFormat05(fileObf, fileType);
        if(!file_format){
            fileObf.value = '';
            webAlert("The upload format is incorrect, please upload again !", null, false);
            // alert('The upload format is incorrect, please upload again!');
            return false;
        }
        // 文件大小
        var file_size = allFileSize05(fileObf);
        if(!file_size){
            fileObf.value = '';
            webAlert('The file size cannot exceed 20M!', null, false);
            // alert('The file size cannot exceed 20M!');
            return false;
        }
        $('#my_upload_05').modal('hide');
        $('.svg_loading').addClass('cpo-block').removeClass('cpo-none');
        cpoOrderUploadFile05(fileObf, fileType);
    })
    function cpoOrderUploadFile05(fileObf, fileType) {
        var order_type = $('.order-nav-list .order-nav-active').children('a').html();
        var file_type = "Gerber File";
        var file = fileObf.files[0]; // 文件模型
        if(fileType == "bom_file"){
            file_type = "BOM File";
        }else if(fileType == "smt_file"){
            file_type = "SMT File";
        }
        //读取本地文件，以gbk编码方式输出
        var reader = new FileReader();
        reader.readAsDataURL(file);
        var file_name = file.name; // 文件名
        reader.onload = function () {
            var datas = reader.result.substring(reader.result.indexOf(",")+1);
            var values = {
                'datas': datas,
                'name': file_name,
                'order_type': order_type,
                'file_type': file_type,
                'tag_name': fileType
            }
            ajax.jsonRpc("/upload/file/json", 'call', values).then(function (data) {
                if(!data.error){
                    $.each(data, function (k, v) {
                        if(k == 'atta_id' || k == 'file_id' || k == 'file_name'){
                            var type = data.file_type.split(' ')[0].toLowerCase()+'_' + k;
                            var $document = $('.cpo_file_ids input[name="'+type+'"]');
                            if($document.length > 0){
                                $document.remove();
                            }
                            var $input = '<input type="text" name="'+type+'" value="'+v+'"/>';
                            $('.cpo_file_ids').append($input);
                        }
                    })
                    successfullyUpload05($('.cpo_file_line .file_status'), file_name, fileType, '100%')
                }else{
                    errorUpload05($('.cpo_file_line .file_status'), file_name, fileType, 'Upload failed');
                    webAlert(data.error, null, false);
                    // alert(data.error);
                }
                fileObf.value = '';
                $('.svg_loading').addClass('cpo-none').removeClass('cpo-block');
            })
        }
    }
    // 上传成功
    function successfullyUpload05(obj, file_name, fileType, error) {
        obj.find('p.tips_box').html('');
        if(fileType == 'gerber_file'){
            obj.find('div.gerber_file_box').empty().append('<p><i class="fa fa-check-circle green mr5"></i>' + file_name + ' (' +error + ' )</p>');
        }else if(fileType == 'bom_file'){
            obj.find('div.bom_file_box').empty().append('<p><i class="fa fa-check-circle green mr5"></i>' + file_name + ' (' +error + ' )</p>');
        }else if(fileType == 'smt_file'){
            obj.find('div.smt_file_box').empty().append('<p><i class="fa fa-check-circle green mr5"></i>' + file_name + ' (' +error + ' )</p>');
        }
    }
    // 错误提示
    function errorUpload05(obj, file_name, fileType, error) {
        obj.find('p.tips_box').html('');
        if(fileType == 'gerber_file'){
            obj.find('div.gerber_file_box').empty().append('<p style="color: red;">' + file_name + ' (' +error + ' )</p>');
        }else if(fileType == 'bom_file'){
            obj.find('div.bom_file_box').empty().append('<p style="color: red;">' + file_name + ' (' +error + ' )</p>');
        }else if(fileType == 'smt_file'){
            obj.find('div.smt_file_box').empty().append('<p style="color: red;">' + file_name + ' (' +error + ' )</p>');
        }
    }
    // 文件格式判断
    function fileFormat05(obj, fileType) {
        var files = obj.files[0];
        var fl_format = files.name.split('.').pop();
        if(fileType == 'gerber_file' || fileType == 'smt_file'){
            if(fl_format == 'rar' || fl_format == 'zip'){
                return true;
            }
        }else if(fileType == 'bom_file'){
            if(fl_format == 'xls' || fl_format == 'xlsx'){
                return true;
            }
        }else {
            return false;
        }
        return false;
    }
    // 文件大小判断
    function allFileSize05(obj) {
        var files = obj.files[0];
        if(files.size/(1024*1024) > 20){
            return false;
        }
        return true;
    }
    // 文件上传 0.5 结束

    // 进度条执行
    var set_interval;
    var cpo_process = function (progress_obj, number_obj, $format, iSpeed=12){
        if(!$format){
            progress_obj.style.width = '0%';
            number_obj.innerHTML = '0%';
            number_obj.style.right = '';
            return false;
        }
        if(set_interval){
           clearInterval(set_interval);
        }
        progress_obj.style.width = '0%';
        number_obj.innerHTML = '0%';
        set_interval =setInterval(function(){
            iSpeed += 1;
            if(iSpeed >= 100){    // 设置达到多少进度后停止
                progress_obj.parentElement.nextElementSibling.innerHTML += ' <span >'+iSpeed+'%</span>'
                stopInterval();
                return false;
            }
            progress_obj.style.width = iSpeed+'%';
            number_obj.innerHTML = iSpeed+'%';
            number_obj.style.right = '10px';
        }, 20);
        return true;
    }
    // 暂停进度条
    function stopInterval() {
        clearInterval(set_interval);
    }
    // 继续进度条
    function continueInterval(progress_obj, number_obj) {
        var iSpeed = parseInt(progress_obj.style.width)
        set_interval = setInterval(function(){
            iSpeed++;
            if(iSpeed >= 100){
                progress_obj.style.width = iSpeed+'%';
                number_obj.innerHTML = iSpeed+'%';
                progress_obj.parentElement.nextElementSibling.innerHTML += ' <span>'+iSpeed+'%</span>'
                stopInterval();
                return true;
            }
            progress_obj.style.width = iSpeed+'%';
            number_obj.innerHTML = iSpeed+'%';
            number_obj.style.right = '10px';
        }, 20);
    }
    // 上传错误提示
    function errorUpload(progress_obj, number_obj) {
        progress_obj.parentElement.nextElementSibling.innerHTML = "Upload failed, please upload again!"
    }
    // 文件格式判断
    function fileFormat(obj) {
        var files = obj.files[0];
        var fl_format = files.name.split('.').pop();
        if(obj.name == 'gerber_file' || obj.name == 'smt_file'){
            if(fl_format == 'rar' || fl_format == 'zip'){
                return true;
            }
        }else if(obj.name == 'bom_file'){
            if(fl_format == 'xls' || fl_format == 'xlsx'){
                return true;
            }
        }else {
            return false;
        }
        return false;
    }
    // 文件大小判断
    function allFileSize(obj) {
        var files = obj.files[0];
        if(files.size/(1024*1024) > 20){
            return false;
        }
        return true;
    }
    // 设置进度条
    function setProgress(){
        var progress_obj = document.getElementById('bar');
        var number_obj = document.getElementById('text-progress')
        cpo_process(progress_obj, number_obj);
    }
    // 展示模态框，显示上传进度
    function showModal(modalObj){
        modalObj.modal({
             show: true,
             backdrop: true
        });
    }
    // 2019-11-26 上传文件
    $('.pg-box .pg-name input[type="file"]').on('change', function () {
        var show_d = $(this).parent().next().next();
        var pg_obj = this.parentNode.nextElementSibling.firstElementChild;
        var nb_obj = this.parentNode.nextElementSibling.firstElementChild.firstElementChild;
        // 判断文件格式
        var $format = fileFormat(this);
        if(!$format){
            this.value = "";
            show_d.html('<span style="color: red">Upload failed, please upload the correct file format!</span>');
        }
        // 判断文件大小
        var $size = allFileSize(this);
        if(!$size){
            show_d.html('<span style="color: red">The file size cannot exceed 20M!</span>');
        }
        // 调整进度条
        var pg_bool = $format && $size;
        var progress = cpo_process(pg_obj, nb_obj, pg_bool)
        if(!progress){
            return false;
        }
        show_d.html('');
        if(!this.files[0]){
            return false;
        }
        var fileName = this.files[0].name +'('+ Math.round(this.files[0].size/1024) +'KB)';
        cpoOrderUploadFile(this);
        show_d.html(fileName);
    });
    function cpoOrderUploadFile(fileObf) {
        checkUploadInvalid(); // 其他上传按钮不可点击
        var file_type = "Gerber File";
        var order_type = $('.order-nav-list .order-nav-active').children('a').html();
        var file = fileObf.files[0]; // 文件模型
        var tag_name = fileObf.name; // 类型 input的name
        if(tag_name == "bom_file"){
            file_type = "BOM File";
        }else if(tag_name == "smt_file"){
            file_type = "SMT File";
        }
        //读取本地文件，以gbk编码方式输出
        var reader = new FileReader();
        reader.readAsDataURL(file);
        var file_name = file.name; // 文件名
        reader.onload = function () {
            var datas = reader.result.substring(reader.result.indexOf(",")+1);
            var values = {
                'datas': datas,
                'name': file_name,
                'order_type': order_type,
                'file_type': file_type,
                'tag_name': tag_name
            }
            ajax.jsonRpc("/upload/file/json", 'call', values).then(function (data) {
                var pg_obj = fileObf.parentNode.nextElementSibling.firstElementChild;
                var nb_obj = fileObf.parentNode.nextElementSibling.firstElementChild.firstElementChild;
                stopInterval(); // 进度条暂停
                if(!data.error){
                    $.each(data, function (k, v) {
                        if(k == 'atta_id' || k == 'file_id' || k == 'file_name'){
                            var type = data.file_type.split(' ')[0].toLowerCase()+'_' + k;
                            var $document = $('.cpo_file_ids input[name="'+type+'"]');
                            if($document.length > 0){
                                $document.remove();
                            }
                            var $input = '<input type="text" name="'+type+'" value="'+v+'"/>';
                            $('.cpo_file_ids').append($input);
                            // console.log(type + k + ' = ' + v);
                        }
                    })
                    continueInterval(pg_obj, nb_obj) // 继续进度条
                    // console.log(data);
                }else{
                    errorUpload(pg_obj, nb_obj);
                    webAlert(data.error, null, false);
                    // alert(data.error);
                }
                checkUploadActive(); // 其他按钮可以点击
            })
        }
    }
    // 确认上传文件
    $('#pcb_file_upload .file_comfirm').on('click', function () {
        $('.cpo_file_line .file_status').empty();
        $('.pg-box .pg-status').each(function(){
            if(this.firstElementChild && this.firstElementChild.innerHTML == '100%'){
                $('.cpo_file_line .file_status').append('<p>'+this.innerText+'</p>')
            }
        })
        if($('.cpo_file_line .file_status').html() == ""){
            $('.cpo_file_line .file_status').html("<p>Haven't you uploaded the file yet?</p>");
        }
        $('.pg-box input[type="file"]').each(function () {
            var tag_list = ['atta_id', 'file_id', 'file_name'];
            if(this.value == ""){
                for(var i=0;i<tag_list.length;i++){
                    var type = this.id+ '_' + tag_list[i];
                    $('.cpo_file_ids input[name="'+type+'"]').remove();
                }
            }

        })

    })
    // 上传文件中让按钮失效
    function checkUploadInvalid(){
        $('.pg-box input[type="file"]').each(function () {
            $(this).attr('disabled', 'disabled');
        })
    }
    // 上传文件中让按钮失效
    function checkUploadActive(){
        $('.pg-box input[type="file"]').each(function () {
            $(this).removeAttr('disabled');
        })
    }

    //上传文件
    $(".quo-active .cpo_file_line .cpo_file").on("change","input[type='file']",function(){
        $(this).parent().next().next().html('Gerber file.zar');
        var fileObj=$(this);
        if(cpoFilePath(fileObj) == false){
            return false;
        }
        changeUploadFile(this);
        showModal($('#pcb_file_upload'));
        setProgress();
    })
    // });
    function optionalCom(value) {
        var $pcba_nedd_pcb = $('.cpo_pcba_need_pcb');
        var surface_value;
        var immersion_gold = 'Immersion gold';
        var gold_finger = 'Gold finger';
        var cpo_click_value = value;
        if($pcba_nedd_pcb.length > 0){
            surface_value = $('.surface_treatment select.surface_value').val();
            if(cpo_click_value.indexOf(immersion_gold) != -1){
                $('.cpo-tips-content').addClass('cpo-block').removeClass('cpo-none');
            }else {
                if(surface_value.indexOf(immersion_gold) != -1){
                    $('.cpo-tips-content').addClass('cpo-block').removeClass('cpo-none');
                }else{
                    $('.cpo-tips-content').addClass('cpo-none').removeClass('cpo-block');
                }
                // $('.cpo-tips-content').addClass('cpo-none').removeClass('cpo-block');
            }
            if(cpo_click_value.indexOf(gold_finger) != -1){
                $('.cpo-finger-box').addClass('cpo-block').removeClass('cpo-none');
            }else{
                if(surface_value.indexOf(gold_finger) != -1){
                    $('.cpo-finger-box').addClass('cpo-block').removeClass('cpo-none');
                }else{
                    $('.cpo-finger-box').addClass('cpo-none').removeClass('cpo-block');
                }
                // $('.cpo-finger-box').addClass('cpo-none').removeClass('cpo-block');
            }
        }else{
            surface_value = $('.quo-active .surface_treatment select.surface_value').val();
            if(cpo_click_value.indexOf(immersion_gold) != -1){
                $('.quo-active .cpo-tips-content').addClass('cpo-block').removeClass('cpo-none');
            }else {
                if(surface_value.indexOf(immersion_gold) != -1){
                    $('.quo-active .cpo-tips-content').addClass('cpo-block').removeClass('cpo-none');
                }else{
                    $('.quo-active .cpo-tips-content').addClass('cpo-none').removeClass('cpo-block');
                }
                // $('.quo-active .cpo-tips-content').addClass('cpo-none').removeClass('cpo-block');
            }
            if(cpo_click_value.indexOf(gold_finger) != -1){
                $('.quo-active .cpo-finger-box').addClass('cpo-block').removeClass('cpo-none');
            }else{
                if(surface_value.indexOf(gold_finger) != -1){
                    $('.quo-active .cpo-finger-box').addClass('cpo-block').removeClass('cpo-none');
                }else{
                    $('.quo-active .cpo-finger-box').addClass('cpo-none').removeClass('cpo-block');
                }
                // $('.quo-active .cpo-finger-box').addClass('cpo-none').removeClass('cpo-block');
            }
        }
    }
//-PCB 报价 Begin Version-0.3 -----------------------------------------------------------------------------------------------------------------

    // PCS 和 Panel 切换
    $('.quo-active .cpo-ps-rl').on('click', function () {
        var need_pcb = $('.cpo_pcba_need_pcb');
        var $val = $(this).children('span').html();
        if(need_pcb.length > 0){
            webAlert('The current order does not provide imposition !', null, false);
            // alert('The current order does not provide imposition !');
        }else {
            if ($val == 'PCS') {
                $('.quo-active .cpo-box input[name="pcb_panel_pcs"]').val('');
                $('.quo-active .cpo-box input[name="pcb_panel_item"]').val('');
                $('.quo-active .cpo-box-panel').css('display', 'none');
                $(this).children('i').addClass('cpo-radio-select')
                $(this).siblings('span').children('i').removeClass('cpo-radio-select');
            } else {
                $(this).children('i').addClass('cpo-radio-select')
                $(this).siblings('span').children('i').removeClass('cpo-radio-select');
                $('.quo-active .cpo-box-panel').css('display', 'block');
            }
        }
    });
    //
    // PCB 基材选择
    $('.quo-active .material_select .cpo_material').on('change', function () {
        var $material = $(this).val();
        cpoReplaceSelect($material);
    });

    function cpoReplaceSelect(value){
        if(value == 'FR4'){
            $('.quo-active .cpo_rogers_data').addClass('cpo-none').removeClass('cpo-block');
            $('.quo-active .cpo-board-thickness').addClass('cpo-block').removeClass('cpo-none');
            $('.quo-active .cpo_material_value .cpo-box-title').html('TG Value');
            $('.quo-active .cpo_material_value .cpo-box-content').empty();
            $('.quo-active .cpo_material_value .cpo-box-content').append('\n'+
                '<select class="cpo-box-select material_value">\n' +
                    '<option value="Tg135">135</option>\n' +
                    '<option value="Tg150">150</option>\n' +
                    '<option value="Tg170">170</option>\n' +
                '</select>');
            $('.quo-active .cpo_meterial_layer .cpo-box-content').empty().append('\n'+
                '<select class="cpo-box-select cpo_layers">\n' +
                    '<option value="2">2 Layer</option>\n' +
                    '<option value="4">4 Layer</option>\n' +
                    '<option value="6">6 Layer</option>\n' +
                    '<option value="8">8 Layer</option>\n' +
                    '<option value="10">10 Layer</option>\n' +
                    '<option value="12">12 Layer</option>\n' +
                    '<option value="14">14 Layer</option>\n' +
                    '<option value="16">16 Layer</option>\n' +
                    '<option value="18">18 Layer</option>\n' +
                    '<option value="20">20 Layer</option>\n' +
                '</select>');
            $('.quo-active .cpo_heavy_copper .cpo-box-content').empty();
            $('.quo-active .cpo_heavy_copper .cpo-box-content').append('\n'+'' +
                    '<select class="cpo-box-select outer_copper">\n' +
                    '<option value="1">1</option>\n' +
                    '<option value="1.5">1.5</option>\n' +
                    '<option value="2">2</option>\n' +
                    '<option value="3">3</option>\n' +
                    '<option value="4">4</option>\n' +
                    '<option value="5">5</option>\n' +
                    '<option value="6">6</option>\n' +
                    '<option value="7">7</option>\n' +
                    '<option value="8">8</option>\n' +
                    '<option value="9">9</option>\n' +
                    '<option value="10">10</option>\n' +
                    '<option value="11">11</option>\n' +
                    '<option value="12">12</option>\n' +
                    '<option value="13">13</option>\n' +
                    '<option value="14">14</option>\n' +
                    '<option value="15">15</option>\n' +
                    '<option value="16">16</option>\n' +
                    '<option value="17">17</option>\n' +
                    '<option value="18">18</option>\n' +
                    '<option value="19">19</option>\n' +
                    '<option value="20">20</option>\n' +
                    '</select>\n' +
                    '<span class="cpo-box-unit"> OZ</span>');
            $('.quo-active .layer_inner_copper .inner_copper').val('0');
            $('.quo-active .layer_inner_copper .inner_copper').removeAttr('disabled');
            $('.quo-active .cpo-board-thickness input[name="cpo_thickness"]').removeAttr('disabled');
            $('.quo-active .cpo-board-thickness input[name="cpo_thickness"]').val('1.6');
            $('.quo-active .cpo-board-thickness .thick-unit').html('MM (±10%)');
        }else{
            $('.quo-active .cpo_rogers_data').addClass('cpo-block').removeClass('cpo-none');
            $('.quo-active .cpo-board-thickness').addClass('cpo-none').removeClass('cpo-block');
            $('.quo-active .cpo_material_value .cpo-box-title').html('Rogers');
            $('.quo-active .cpo_material_value .cpo-box-content').empty();
            $('.quo-active .cpo_material_value .cpo-box-content').append('\n'+
                '<select class="cpo-box-select material_value">\n' +
                    '<option value="4003C">4003C</option>\n' +
                    '<option value="4350B">4350B</option>\n' +
                '</select>');
            $('.quo-active .cpo_meterial_layer .cpo-box-content').empty().append('\n'+
                '<select class="cpo-box-select cpo_layers">\n' +
                    '<option value="1">1 Layer</option>\n' +
                    '<option value="2">2 Layer</option>\n' +
                '</select>');
            $('.quo-active .cpo_heavy_copper .cpo-box-content').empty();
            $('.quo-active .cpo_heavy_copper .cpo-box-content').append('\n'+'' +
                    '<select class="cpo-box-select outer_copper">\n' +
                        '<option value="1">1</option>\n' +
                        '<option value="2">2</option>\n' +
                    '</select>\n' +
                    '<span class="cpo-box-unit"> OZ</span>')
            $('.quo-active .layer_inner_copper .inner_copper').val('0');
            $('.quo-active .layer_inner_copper .inner_copper').attr('disabled', 'disabled');
            $('.quo-active .cpo-board-thickness input[name="cpo_thickness"]').val('0.3');
            $('.quo-active .cpo-board-thickness .thick-unit').html('MM (±0.1MM)');
            $('.quo-active .cpo-board-thickness input[name="cpo_thickness"]').attr('disabled', 'disabled');
        }
    }
    // PCBA 基材
    $('.cpo_pcba_need_pcb .material_select .cpo_material').on('change', function () {
        var $material = $(this).val();
        cpoPCBAReplaceSelect($material);
    });
    function cpoPCBAReplaceSelect(value){
        if(value == 'FR4'){
            $('.cpo_pcba_need_pcb .cpo_rogers_data').addClass('cpo-none').removeClass('cpo-block');
            $('.cpo_pcba_need_pcb .cpo_material_value .cpo-box-title').html('TG Value');
            $('.cpo_pcba_need_pcb .cpo_material_value .cpo-box-content').empty();
            $('.cpo_pcba_need_pcb .cpo_material_value .cpo-box-content').append('\n'+
                '<select class="cpo-box-select material_value">\n' +
                    '<option value="Tg135">135</option>\n' +
                    '<option value="Tg150">150</option>\n' +
                    '<option value="Tg170">170</option>\n' +
                '</select>');
            $('.cpo_pcba_need_pcb .cpo_meterial_layer .cpo-box-content').empty().append('\n'+
                '<select class="cpo-box-select cpo_layers">\n' +
                    '<option value="2">2 Layer</option>\n' +
                    '<option value="4">4 Layer</option>\n' +
                    '<option value="6">6 Layer</option>\n' +
                    '<option value="8">8 Layer</option>\n' +
                    '<option value="10">10 Layer</option>\n' +
                    '<option value="12">12 Layer</option>\n' +
                    '<option value="14">14 Layer</option>\n' +
                    '<option value="16">16 Layer</option>\n' +
                    '<option value="18">18 Layer</option>\n' +
                    '<option value="20">20 Layer</option>\n' +
                '</select>');
        }else{
            $('.cpo_pcba_need_pcb .cpo_rogers_data').addClass('cpo-block').removeClass('cpo-none');
            $('.cpo_pcba_need_pcb .cpo_material_value .cpo-box-title').html('Rogers');
            $('.cpo_pcba_need_pcb .cpo_material_value .cpo-box-content').empty();
            $('.cpo_pcba_need_pcb .cpo_material_value .cpo-box-content').append('\n'+
                '<select class="cpo-box-select material_value">\n' +
                    '<option value="4003C">4003C</option>\n' +
                    '<option value="4350B">4350B</option>\n' +
                '</select>');
            $('.cpo_pcba_need_pcb .cpo_meterial_layer .cpo-box-content').empty().append('\n'+
                '<select class="cpo-box-select cpo_layers">\n' +
                    '<option value="1">1 Layer</option>\n' +
                    '<option value="2">2 Layer</option>\n' +
                '</select>');
        }
    }
    // Rogers 芯板选择
    $('.quo-active .cpo_core_board').on('change', function () {
        var thick = $('.quo-active .cpo-board-thickness input[name="cpo_thickness"]');
        var thick_unit = $('.quo-active .cpo-board-thickness .thick-unit');
        var $this = $(this).val();
        if($this == '10'){
            thick.val('0.3');
            thick_unit.html('MM (±0.1MM)');
        }else if($this == '20'){
            thick.val('0.5');
            thick_unit.html('MM (±0.1MM)');
        }else if($this == '30'){
            thick.val('0.8');
            thick_unit.html('MM (±0.1MM)');
        }else{
            thick.val('1.6');
            thick_unit.html('MM (±10%)');
        }
    });

    // Rogers 选择时，显示对应的芯板厚度
    $('.quo-active .cpo_material_value').on('change', '.material_value', function () {
        var $this_val = $(this).val();
        if($this_val == '4003C'){
            $('.quo-active .cpo_core_board').empty();
            $('.quo-active .cpo_core_board').append('\n'+
                    '<option value="12">12 mil</option>\n' +
                    '<option value="16">16 mil</option>\n' +
                    '<option value="20">20 mil</option>\n' +
                    '<option value="32">32 mil</option>\n' +
                    '<option value="60">60 mil</option>');
        }else{
            $('.quo-active .cpo_core_board').empty();
            $('.quo-active .cpo_core_board').append('\n'+
                    '<option value="10">10 mil</option>\n' +
                    '<option value="13.3">13.3 mil</option>\n' +
                    '<option value="16.6">16.6 mil</option>\n' +
                    '<option value="20">20 mil</option>\n' +
                    '<option value="30">30 mil</option>\n' +
                    '<option value="60">60 mil</option>');
        }
    });

    // 层数选择
    $('.quo-active .cpo_meterial_layer .cpo_layers').on('change', function () {
        var $this_val = $(this).val();
        pcbSelectLayer($this_val)
    });
    function pcbSelectLayer(value){
        var cpo_heavy_copper = $('.quo-active .cpo_heavy_copper .outer_copper');
        var cpo_inner_copper = $('.quo-active .cpo-box .inner_copper');
        var $select_val = value;
        if($select_val > 2){
            cpo_inner_copper.val('0.5');
            if(cpo_heavy_copper.length > 0){
                cpo_heavy_copper.empty();
                cpo_heavy_copper.append('\n'+
                    '<option value="1">1</option>\n' +
                    '<option value="2">2</option>\n' +
                    '<option value="3">3</option>\n' +
                    '<option value="4">4</option>\n' +
                    '<option value="5">5</option>')
            }
        }else{
            cpo_inner_copper.val('0');
            if(cpo_heavy_copper.length > 0){
                cpo_heavy_copper.empty();
                cpo_heavy_copper.append('\n'+
                    '<option value="1">1</option>\n' +
                    '<option value="2">2</option>\n' +
                    '<option value="3">3</option>\n' +
                    '<option value="4">4</option>\n' +
                    '<option value="5">5</option>\n' +
                    '<option value="6">6</option>\n' +
                    '<option value="7">7</option>\n' +
                    '<option value="8">8</option>\n' +
                    '<option value="9">9</option>\n' +
                    '<option value="10">10</option>\n' +
                    '<option value="11">11</option>\n' +
                    '<option value="12">12</option>\n' +
                    '<option value="13">13</option>\n' +
                    '<option value="14">14</option>\n' +
                    '<option value="15">15</option>\n' +
                    '<option value="16">16</option>\n' +
                    '<option value="17">17</option>\n' +
                    '<option value="18">17</option>\n' +
                    '<option value="19">19</option>\n' +
                    '<option value="20">20</option>');
            }
        }
    }
    // 页面选择内铜厚，要考虑层数问题
    $('.quo-active .cpo-box .inner_copper').on('change', function () {
        var $this = $(this);
        innerCopper($this)
    });
    $('.cpo_pcba_need_pcb .cpo-box .inner_copper').on('change', function () {
        var $this = $(this);
        innerCopper($this)
    });
    function innerCopper(value){
        var $this = value;
        var $pcba_nedd_pcb = $('.cpo_pcba_need_pcb');
        if($pcba_nedd_pcb.length > 0){
            var layer_val = $('.cpo_pcba_need_pcb .cpo_meterial_layer .cpo_layers').val();
        }else{
            var layer_val = $('.quo-active .cpo_meterial_layer .cpo_layers').val();
        }
        if(layer_val > 2){
            if($this.val() <= 0){
                $this.val('0.5')
            }else{
                $this.val($this.val());
            }
        }else{
            $this.val('0');
        }
    }
    // 颜色选择
    $('.cpo-color-sl .cpo_mask_color').on('change', function () {
        var mask_color = { 'Green': 'Green','Yellow': 'Yellow','Red': 'Red','Blue': 'Blue','White': 'White','Black': 'Black','Purple': 'Purple',
                   'Matt Blue': '#0d4a83','Matt green': '#66cc99','Matt black': '#4d433c','Transparent': 'rgba(204,204,204,0.2)','No': '' }

        var $sl_val = $(this).val();
        var $this = $(this);
        $.each(mask_color, function (key, val) {
            if($sl_val == 'No'){
                // $this.siblings('span').css('background-color', '');
                // $this.siblings('span').html('No');
                if ($sl_val == key) {
                    $this.siblings('span').css('background-color', '#fff');
                    $this.siblings('span').html('No');
                }
            }else {
                if ($sl_val == key) {
                    $this.siblings('span').css('background-color', val);
                    $this.siblings('span').html('');
                }
            }
        });
    });
    $('.cpo-color-sl .cpo_silkscreen_color').on('change', function () {
        var silkscreen = { 'White': 'White','Black': 'Black','Red': 'Red','Blue': 'Blue','Yellow': 'Yellow','No': '' }
        var $sl_val = $(this).val();
        var $this = $(this);
        $.each(silkscreen, function (key, val) {
            if($sl_val == 'No'){
                $this.siblings('span').css('background-color', val);
                $this.siblings('span').html('No');
            }else {
                if ($sl_val == key) {
                    $this.siblings('span').css('background-color', val);
                    $this.siblings('span').html('');
                }
            }
        });
    });
    // 面积计算
    // function areaClacu(w, h, qty) {
    //     var area = parseInt(qty) * parseFloat(w) * parseFloat(h) / 1000000;
    //     var e_test = $('.quo-active .cpo_pcb_quotation .cpo_e_test');
    //     if(area >= 3){
    //         e_test.val('E-test fixture');
    //     }else{
    //         e_test.val('Free Flying Probe');
    //     }
    // }
    // PCB From 数据提取
    function pcbGetFormData(){
        var pcb_value_dict;
        var pcb_qty_unit = $('.cpo-ps-rl i.cpo-radio-select').siblings('span').html();
        var pcb_pcs_size = '';
        var pcb_item_size = '';

        var quality_standard = $('.quo-active .cpo_pcb_quotation .quality_standard').val();
        var quantity = $('.quo-active .cpo_pcb_quotation input[name="pcb_quantity"]').val();
        var pcb_quantity = parseInt(quantity);
        if(pcb_qty_unit == 'Panel'){
            pcb_pcs_size = $('.quo-active .cpo_pcb_quotation input[name="pcb_panel_pcs"]').val();
            pcb_item_size = $('.quo-active .cpo_pcb_quotation input[name="pcb_panel_item"]').val();
        }
        var pcb_length = $('.quo-active .cpo_pcb_quotation input[name="pcb_length"]').val();
        var pcb_breadth = $('.quo-active .cpo_pcb_quotation input[name="pcb_breadth"]').val();
        var cpo_layers = $('.quo-active .cpo_pcb_quotation .cpo_layers').val();
        //areaClacu(pcb_breadth, pcb_length, quantity) // 面积判断
        // 基材
        var rogers_number = 1;
        var cpo_raw_material;
        var pcb_rogers = null;
        var cpo_material = $('.quo-active .cpo_pcb_quotation .cpo_material').val();
        var material_value = $('.quo-active .cpo_pcb_quotation .material_value').val();
        var core_thick = $('.quo-active .cpo_pcb_quotation .cpo_core_board').val();
        // var rogers_number = $('.quo-active .cpo_pcb_quotation input[name="cpo_rogers_number"]').val();
        if(cpo_material == 'FR4'){
            cpo_raw_material = cpo_material+'-'+material_value;
        }else{
            cpo_raw_material = cpo_material+' '+material_value;
            pcb_rogers = {
                'core_thick': core_thick,
                'rogers_number': rogers_number
            }
        }

        var cpo_thickness = $('.quo-active .cpo_pcb_quotation input[name="cpo_thickness"]').val();
        var cpo_inner_copper;
        var inner_copper = $('.quo-active .cpo_pcb_quotation .inner_copper').val();
        if(inner_copper == '0'){
            cpo_inner_copper = '';
        }else{
            cpo_inner_copper = inner_copper;
        }
        var cpo_outer_copper = $('.quo-active .cpo_pcb_quotation .outer_copper').val();
        var cpo_mask_color = $('.quo-active .cpo_pcb_quotation .cpo_mask_color').val();
        var cpo_silkscreen_color = $('.quo-active .cpo_pcb_quotation .cpo_silkscreen_color').val();

        var surface_conventional = $('.quo-active .cpo_pcb_quotation .surface_value').val();
        var surface_combination = $('.quo-active .cpo_pcb_quotation .surface_combination').val();
        // 表面处理值
        var cpo_surface_treatment = {};
        if(surface_conventional == 'Gold finger' || surface_combination == 'Gold finger'){
            cpo_surface_treatment.gold_finger_thickness = $('.quo-active .cpo_pcb_quotation .gold_finger_thickness').val();
            cpo_surface_treatment.gold_finger_length = '';
            cpo_surface_treatment.gold_finger_width = '';
            cpo_surface_treatment.gold_finger_qty = '';
        }
        if(surface_conventional){
            if(surface_conventional.indexOf("Immersion gold") != -1){
                cpo_surface_treatment.nickel_thickness = '120';
                cpo_surface_treatment.coated_area = '30';
            }
        }
        if(surface_combination == 'No'){
            cpo_surface_treatment.surface_value = surface_conventional;
        }else{
            cpo_surface_treatment.surface_value = surface_conventional+' + '+surface_combination;
        }
        var cpo_vias = $('.quo-active .cpo_pcb_quotation .cpo_vias').val();
        var cpo_e_test = $('.quo-active .cpo_pcb_quotation .cpo_e_test').val();
        var pcb_special_requirements = pcbQuotationSpecialForm();
        pcb_value_dict = {
            'quality_standard': quality_standard,
            'cpo_quantity': pcb_quantity,
            'pcb_qty_unit': pcb_qty_unit,
            'pcb_length': pcb_length,
            'pcb_breadth': pcb_breadth,
            'pcb_pcs_size':pcb_pcs_size,
            'pcb_item_size':pcb_item_size,
            'pcb_rogers': pcb_rogers,
            'pcb_layer': cpo_layers,
            'pcb_type': cpo_raw_material,
            'pcb_thickness': cpo_thickness,
            'pcb_inner_copper': cpo_inner_copper,
            'pcb_outer_copper': cpo_outer_copper,
            'pcb_solder_mask': cpo_mask_color,
            'pcb_silkscreen_color': cpo_silkscreen_color,
            'pcb_surfaces': cpo_surface_treatment,
            'pcb_vias': cpo_vias,
            'pcb_test': cpo_e_test,
            'pcb_special_requirements': pcb_special_requirements,

        }
        return pcb_value_dict
    }
    // 检查PCB数据是否完整填写
    function checkPCBData03() {
        var flag = true;
        var $pcb_data_input = $('.quo-active .cpo_pcb_quotation input[type="text"]');
        var $i_ac = $('.quo-active .cpo-ps-rl').children('i.cpo-radio-select').siblings('span').html()
        var $cpo_material = $('.quo-active .cpo_material').val();
        $pcb_data_input.each(function () {
            var $val = $(this).val();
            if(!$val){
                if(this.name == 'pcb_panel_pcs' || this.name == 'pcb_panel_item'){
                    if($i_ac != 'PCS'){
                        $(this).css('border', '1px solid red');
                        $(this).focus();
                        flag = false;
                        return flag;
                    }
                }else{
                    $(this).css('border', '1px solid red');
                    $(this).focus();
                    flag = false;
                    return flag;
                }
                // else if(this.name == 'cpo_rogers_number'){
                //     if($cpo_material != 'FR4'){
                //         $(this).css('border', '1px solid red');
                //         $(this).focus();
                //         flag = false;
                //         return flag;
                //     }
                // }
            }else{
                $(this).css('border', '1px solid #dddddd');
            }
        });
        return flag;
    }
    // PCB 特殊数据
    function pcbQuotationSpecialForm(){
        var pcb_special_value;
        var Semi_hole = $('.quo-active form.special_form select.special_semi_hole').val();
        var Edge_plating = $('.quo-active form.special_form select.special_edge_plating').val();
        var Impedance = $('.quo-active form.special_form select.special_impedance').val();
        var Press_fit = $('.quo-active form.special_form select.special_press_fit').val();
        var Peelable_mask = $('.quo-active form.special_form select.special_peelable_mask').val();
        var Carbon_oil = $('.quo-active form.special_form select.pcb_carbon_ink').val();
        var Min_line_width = $('.quo-active form.special_form input.min_line_width').val();
        var Min_line_space = $('.quo-active form.special_form input.special_line_space').val();
        var Min_aperture = $('.quo-active form.special_form input.special_minimum_aperture').val();
        var Total_holes = $('.quo-active form.special_form input.special_total_number').val();
        var Copper_weight_wall = $('.quo-active form.special_form input.special_copper_hall').val();
        var Number_core = $('.quo-active form.special_form input.special_number_core').val();
        var PP_number = $('.quo-active form.special_form input.special_pp_number').val();
        // var Acceptable_stanadard = $('form.special_form select.special_acceptable').val('2');
        var Total_test_points = $('.quo-active form.special_form input.special_total_test').val();
        var Blind_and_buried_hole = $('.quo-active form.special_form .blind_and_buried_hole').val();
        var Blind_hole_structure = $('.quo-active form.special_form .blind_hole_structure').val();
        var Depth_control_routing = $('form.special_form select.special_depth_control').val();
        var Number_back_drilling = $('.quo-active form.special_form select.special_back_drilling').val();
        var Countersunk_deep_holes = $('.quo-active form.special_form .countersunk_deep_holes').val();
        var Laser_drilling = $('.quo-active form.special_form select.special_laser_drilling').val();
        var The_space_for_drop_V_cut = $('.quo-active form.special_form select.special_v_cut_space').val();
        var Inner_hole_line = $('.quo-active form.special_form input.special_inner_hole_line').val();

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

    //---PCB 特殊数据按钮 Begin Version-0.3 -------------------------------------------------------------------------------------------------
    //     var process_special_click = $('.quo-active .pcb_need_special_btn');
    $('.pcb_need_special_btn').on('click', function () {
        var pcba_need_pcb = $('.cpo_pcba_need_pcb');
        var special_i = $(this).find('i');
        if(special_i.hasClass('pcb_need_btn_plus')){
            special_i.removeClass('pcb_need_btn_plus').addClass('pcb_need_btn_less');
            if(pcba_need_pcb.length > 0){
                $('.cpo_pcba_need_pcb .cpo_pcb_special').toggle();
            }else {
                $('.quo-active .cpo_pcb_special').toggle();
            }
        }else{
            special_i.addClass('pcb_need_btn_plus').removeClass('pcb_need_btn_less');
            if(pcba_need_pcb.length > 0){
                $('.cpo_pcba_need_pcb .cpo_pcb_special').toggle();
            }else {
                $('.quo-active .cpo_pcb_special').toggle();
            }
        }
        pcbSpecialForm();
    });

    //---PCB 特殊数据按钮 End Version-0.3 ---------------------------------------------------------------------------------------------------

    // 点击PCB报价计算
    var pcb_click = $('.cpo_pcb_calcula_content .cpo_calculation');
    pcb_click.on('click', function () {
        $('.generate_special_documents').css('display', 'none');
        var checkpcbdata = checkPCBData03();
        if(!checkpcbdata){
            return false;
        }
        cpoPCBQuotationCalculation();
    });
    function cpoPCBQuotationCalculation(){
        var cpo_country = $('.quo-active .cpo_country_list select').val();
        var cpo_express = $('.quo-active .cpo_order_express_message select').val();
        var cpo_source = $('.cpo_source_cp input[name="cpo_source"]').val();
        // var country_val = checkCountry();
        // if(!country_val){
        //     return false;
        // }
        var pcb_from = pcbGetFormData();
        var pcb_special_requirements = pcbQuotationSpecialForm();
        var stair_price = {
            'pcb_value': pcb_from,
            'cpo_country': cpo_country,
            'cpo_express': cpo_express,
            'pcb_special_requirements': pcb_special_requirements,
        }
        $('#step_next').css('display', 'inline-block');
        ajax.jsonRpc("/cpo_pcb_quotation", 'call', {
            'cpo_source': cpo_source,
            'pcb_value': pcb_from,
            'cpo_country': cpo_country,
            'cpo_express': cpo_express,
            'pcb_special_requirements': pcb_special_requirements,
        }).then(function (data) {
            pcbAllData(data);
            cpoPcbQuoStairPrice(stair_price); // 获取阶梯价
        });
    }
    // 错误提示
    function showWarning(showKey, showVal, waring_str) {
        var $doc = $('.cpo-warning');
        $doc.empty();
        var warn_cont = '<div class="alert alert-warning">\n' +
            '<a href="#" class="close" data-dismiss="alert">\n' +
            '<i class="fa fa-close"></i></a><strong>Prompt : </strong>'+showVal+'\n' +
            '</div>';
        if($doc.length > 0){
            $('.generate_special_documents').css('display', 'block');
            $doc.append(warn_cont);
            $('body,html').animate({scrollTop: 150}, 500);
        }else{
            if (showVal != null) {
                waring_str += showVal + '\n';
            }
            return waring_str
        }
    };

    // PBC 返回 Data,前端渲染
    function pcbAllData(data) {
        var order_name = 'PCB';
        var record = setQuotationData(data, order_name);
        if(data){
            if(data.error){
                // $('.quo-active .calculation_content').addClass('cpo-none').removeClass('cpo-block');
                $('.calculation_content>div.cpo_cost_fee').addClass('cpo-none').removeClass('cpo-block');
                $('.quo-active #step_next').css('display', 'none');

                var waring_str = '';
                var waring_num = 1;
                if(data.error.e){
                    webAlert('Please check if the data is filled in correctly !', null, false);
                    // alert('Please check if the data is filled in correctly !');
                    return false;
                }else {
                    $.each(data.error, function (war_key, war_value) {
                        waring_str = showWarning(war_key, war_value, waring_str, waring_num);
                        // waring_str = showWarn(war_key, war_value, waring_str);

                    });
                    if(waring_str){
                        webAlert(waring_str, null, false);
                        // alert(waring_str);
                    }
                }

            }else if(data.login){
                getLoginData(data);
            }
            else{
                $('.cpo-warning').empty();
                //加急
                $('.order_page_ad').addClass('cpo-none');
                $('.calculation_content>div.cpo_cost_fee').addClass('cpo-block').removeClass('cpo-none');
                $('.cpo_try_expedited_list .cpo_quantity_content').empty();
                if(data.pcb_value.pcb_rogers){
                    $('.cpo_try_expedited_list').addClass('cpo-none').removeClass('cpo-block');
                    $.each(data.pcb_value.pcb_rogers, function (rog_key, rog_val) {
                        $('#cpo_pcb_result .pcb_result').append('<input type="hidden" name="'+ rog_key +'" value="'+ rog_val + '"/>')
                    });
                }else {
                    var expedited_list = data.cpo_expedited_list;
                    if (data['PCB Area'] < '3' && expedited_list.length) {
                        $('.cpo_try_expedited_list').addClass('cpo-block').removeClass('cpo-none');
                        $.each(expedited_list, function (day_key, day_val) {
                            var day_vals = day_val + ' Day'
                            if (day_vals == data['Delivery Period']) {
                                $('.cpo_try_expedited_list .cpo_quantity_content').append('\n' +
                                    '<div class="cpo_quantiry_line cpo_quantity_select">\n' +
                                    '<div class="cpo_try_icon cpo_try_select_icon"></div>\n' +
                                    '<p class="cpo_try_quantity">\n' +
                                    '<span>' + day_val + '</span>\n' +
                                    '<span>Day</span>\n' +
                                    '</p>\n' +
                                    '</div>')
                            } else {
                                $('.cpo_try_expedited_list .cpo_quantity_content').append('\n' +
                                    '<div class="cpo_quantiry_line">\n' +
                                    '<div class="cpo_try_icon"></div>\n' +
                                    '<p class="cpo_try_quantity">\n' +
                                    '<span>' + day_val + '</span>\n' +
                                    '<span>Day</span>\n' +
                                    '</p>\n' +
                                    '</div>')
                            }
                        });
                    } else {
                        $('.cpo_try_expedited_list').addClass('cpo-none').removeClass('cpo-block');
                    }
                }

                // 点击计算价格前清空（避免数据重复）
                $('#cpo_pcb_result .pcb_result').empty();
                $('#cpo_pcb_result .pcb_special_requirements').empty();
                $('#cpo_pcb_result .pcb_surface').empty();
                $('.cpo_pcb_all_fee .pcb_fee_ul').empty(); //清空所有价格（避免重复）
                var pcb_price_detailed = data.pcb_price_detailed;
                var pcb_area = data['PCB Area'];
                if(pcb_area >= 3.0){
                    $('.cpo_e_test').val('E-test fixture');
                    data.pcb_value.pcb_test = 'E-test fixture';
                }else{
                    $('.cpo_e_test').val('Free Flying Probe');
                    data.pcb_value.pcb_test = 'Free Flying Probe';
                }
                $.each(pcb_price_detailed, function (pcb_fee_key, pcb_fee_value) {
                    if(pcb_fee_key == 'Cost By'){
                        $('.cpo_pcb_all_fee .pcb_fee_ul').append('<li>\n'+
                                '<span class="ul_span">Cost By ㎡</span>\n'+
                                '<span class="ul_span_cost">\n'+
                                    '<i>$</i>\n'+
                                    '<input type="text" name="'+pcb_fee_key+'" value="'+pcb_fee_value+'" readonly="readonly"/>\n'+
                                '</span></li>')
                    }else{
                        $('.cpo_pcb_all_fee .pcb_fee_ul').append('<li>\n'+
                                '<span class="ul_span">'+ pcb_fee_key +'</span>\n'+
                                '<span class="ul_span_cost">\n'+
                                    '<i>$</i>\n'+
                                    '<input type="text" name="'+pcb_fee_key+'" value="'+pcb_fee_value+'" readonly="readonly"/>\n'+
                                '</span></li>')
                    }
                });

                var pcb_special_list = data.pcb_special_requirements; //特殊数据
                var pcb_value_list = data.pcb_value;
                $.each(pcb_value_list, function (pcb_key, pcb_value) {
                    if(pcb_key == 'pcb_surfaces'){
                        $.each(pcb_value_list.pcb_surfaces, function (pcb_sur_key, pcb_sur_value) {
                            $('#cpo_pcb_result .pcb_surface').append('<input type="hidden" name="'+ pcb_sur_key +'" value="'+ pcb_sur_value + '"/>');
                        })
                    }else{
                        $('#cpo_pcb_result .pcb_result').append('<input type="hidden" name="'+ pcb_key +'" value="'+ pcb_value + '"/>');
                    }
                });

                if(data.pcb_value.pcb_rogers){
                    $.each(data.pcb_value.pcb_rogers, function (rog_key, rog_val) {
                        $('#cpo_pcb_result .pcb_result').append('<input type="hidden" name="'+ rog_key +'" value="'+ rog_val + '"/>')
                    });
                }

                $.each(pcb_special_list, function (pcb_res_key, pcb_res_value) {
                    $('#cpo_pcb_result .pcb_special_requirements').append('<input type="hidden" name="'+ pcb_res_key +'" value="'+ pcb_res_value + '"/>');
                })
                var area = data['PCB Area'] + ' ㎡';
                $('.cpo_cost_fee input[name="cpo_flat_area"]').val(area);
                if(data['Shipping Cost'] <= 0){
                    var first_i = $('.quo-active .cpo_freifth_box').children().first('i');
                    if(first_i.html() == '\n'){
                        first_i.remove();
                    }
                    $('.quo-active .cpo_freifth_box').prepend('<i class="fa fa-info-circle" data-toggle="tooltip" data-placement="bottom"\n' +
                        'title="The current address cannot automatically calculate the shipping cost, and the final cost is settled"\n'+
                        'style="color: #2e8bc3;">\n' +
                        '</i>')
                }else{
                    var first_i = $('.cpo_freifth_box').children().first('i');
                    if(first_i.html() == '\n'){
                        first_i.remove();
                    }
                }
                if(data['E-test Fixture Cost'] > 0){
                    $('.quo-active .pcb_e_test_cost').addClass('cpo-block').removeClass('cpo-none');
                    $('.quo-active .pcb_e_test_cost .e_test_cost').val(data['E-test Fixture Cost']);
                }else{
                    $('.quo-active .pcb_e_test_cost').addClass('cpo-none').removeClass('cpo-block');
                }
                if(data['Stencil Cost'] > 0){
                    $('.quo-active .pcb_stencil_cost').addClass('cpo-block').removeClass('cpo-none');
                    $('.quo-active .pcb_stencil_cost .stencil_cost').val(data['Stencil Cost']);
                }else{
                    $('.quo-active .pcb_stencil_cost').addClass('cpo-none').removeClass('cpo-block');
                }
                if(data['Film Cost'] > 0){
                    $('.quo-active .pcb_film_cost').addClass('cpo-block').removeClass('cpo-none');
                    $('.quo-active .pcb_film_cost .film_cost').val(data['Film Cost']);
                }else{
                    $('.pcb_film_cost').addClass('cpo-none').removeClass('cpo-block');
                }
                if(data['Process Cost'] > 0){
                    $('.quo-active .pcb_process_cost').addClass('cpo-block').removeClass('cpo-none');
                    $('.quo-active .pcb_process_cost .process_cost').val(data['Process Cost']);
                }else{
                    $('.quo-active .pcb_process_cost').addClass('cpo-none').removeClass('cpo-block');
                }
                log(pcb_price_detailed);
                if(pcb_price_detailed['Original Price'] > 0){
                    $('.quo-active .cpo_original_price').addClass('cpo-block').removeClass('cpo-none');
                    $('.quo-active .cpo_original_price .discount_price').val(pcb_price_detailed['Original Price'].toFixed(2));
                    $('.quo-active .cpo_pcb_total_change').text('After discount');
                }else{
                    $('.quo-active .cpo_original_price').addClass('cpo-none').removeClass('cpo-block');
                    $('.quo-active .cpo_pcb_total_change').text('Total');
                }

                $('.quo-active .cpo_cost_fee input[name="cpo_pcb_quantity"]').val(data.pcb_value.cpo_quantity +' '+data.pcb_value.pcb_qty_unit);
                $('.quo-active .cpo_cost_fee input[name="cpo_freight"]').val(data['Shipping Cost']);
                $('.quo-active .cpo_cost_fee input[name="cpo_delivery"]').val(data['Delivery Period']);
                $('.quo-active .cpo_cost_fee input[name="part_fee"]').val(data['Board Price Cost']);
                $('.quo-active .cpo_cost_fee input[name="cpo_engineering_fee"]').val(data['Set Up Cost']);
                $('.quo-active .cpo_cost_fee input[name="all_fee"]').val(data['Total Cost'].toFixed(2));
                $.each(pcb_price_detailed, function (pcb_afee_key, pcb_afee_value) {
                    $('#cpo_pcb_result .pcb_result').append('<input type="hidden" name="'+ pcb_afee_key +'" value="'+ pcb_afee_value + '"/>');
                });
                $('.pcb_calculation_results .calculation_content').addClass('cpo-block').removeClass('cpo-none');
                pcbSpecialCallBack(data.pcb_special_requirements);
                var get_order_id = $('#cpo_pcb_result .pcb_fixed_data .order_id').val();
                var get_pcb_fee = $('.pcba_order_fee .all_fee').val();
                var get_pcba_fee = $('.pcba_order_fee .total_cost').val();
                if(get_order_id){
                    var pcb_pcba_fee = parseFloat(get_pcb_fee) + parseFloat(get_pcba_fee);
                    $('.pcba_order_fee .pcb_pcba_all_fee').val(pcb_pcba_fee.toFixed(2));
                }
            }
        }
    }
    // 报价记录保存
    function setQuotationData(data, order_name) {
        var gerber_file_id, gerber_atta_id,gerber_file_name;
        var bom_file_id,bom_atta_id,bom_file_name;
        var smt_file_id,smt_atta_id,smt_file_name;
        var file_name;
        var record_data;
        // var cpo_pcba_need_pcb = $('.cpo_pcba_need_pcb');
        // var cpo_pcba_need_pcb = $('#cpo_pcba_online_content');
        // if(cpo_pcba_need_pcb.length > 0){
        gerber_file_id = $('.cpo_file_ids input[name="gerber_file_id"]').val();
        gerber_atta_id = $('.cpo_file_ids input[name="gerber_atta_id"]').val();
        gerber_file_name = $('.cpo_file_ids input[name="gerber_file_name"]').val();
        bom_file_id = $('.cpo_file_ids input[name="bom_file_id"]').val();
        bom_atta_id = $('.cpo_file_ids input[name="bom_atta_id"]').val();
        bom_file_name = $('.cpo_file_ids input[name="bom_file_name"]').val();
        smt_file_id = $('.cpo_file_ids input[name="smt_file_id"]').val();
        smt_atta_id = $('.cpo_file_ids input[name="smt_atta_id"]').val();
        smt_file_name = $('.cpo_file_ids input[name="smt_file_name"]').val();
        file_name = {
            'gerber_file_id': gerber_file_id,
            'gerber_atta_id': gerber_atta_id,
            'gerber_file_name': gerber_file_name,
            'bom_file_id': bom_file_id,
            'bom_atta_id': bom_atta_id,
            'bom_file_name': bom_file_name,
            'smt_file_id': smt_file_id,
            'smt_atta_id': smt_atta_id,
            'smt_file_name': smt_file_name,
        }
        // }else{
        //     gerber_file_id = $('.quo-active .gerber_box .gerber_file_id').val();
        //     gerber_atta_id = $('.quo-active .gerber_box .gerber_atta_id').val();
        //     gerber_file_name = $('.quo-active .gerber_box .gerber_file_name').val();
        //     file_name = {
        //         'gerber_file_id': gerber_file_id,
        //         'gerber_atta_id': gerber_atta_id,
        //         'gerber_file_name': gerber_file_name
        //     }
        // }
         ajax.jsonRpc('/set_quotation_reacord', 'call',{
            'data': data,
            'order_name': order_name,
            'file_data': file_name,
            'record_data': order_name,
        }).then(function (data) {
            var record = data;
            if(record){
                var SIGNUP_COOKIE_HISTORY = 'quote_signup_history';
                var getQuote = utils.get_cookie('quote_signup_history');
                if(getQuote){
                    var url_history = JSON.parse(getQuote);
                    url_history.quote_id = record;
                    utils.set_cookie(SIGNUP_COOKIE_HISTORY, JSON.stringify(url_history), 60*60*24); // 1 day cookie
                }else {
                    var url_history = {
                        'quote_id': record,
                    };
                    utils.set_cookie(SIGNUP_COOKIE_HISTORY, JSON.stringify(url_history), 60*60*24); // 1 day cookie
                }
            }
            return record;
        });
        // var record = cpoQuotationRecord(record_data, data, file_name, order_name);
        // return record
    }
    // PCB 特殊数据数据返回
    function pcbSpecialCallBack(list) {
        // $('.quo-active form.special_form input[name="min_line_width"]').val(list.Min_line_width);
        // $('.quo-active form.special_form input[name="special_line_space"]').val(list.Min_line_space);
        // $('.quo-active form.special_form input[name="special_minimum_aperture"]').val(list.Min_aperture);
        // $('.quo-active form.special_form input[name="special_total_number"]').val(list.Total_holes);
        // $('.quo-active form.special_form input[name="special_copper_hall"]').val(list.Copper_weight_wall);
        // $('.quo-active form.special_form input[name="special_number_core"]').val(list.Number_core);
        // $('.quo-active form.special_form input[name="special_pp_number"]').val(list.PP_number);
        // $('.quo-active form.special_form input[name="special_total_test"]').val(list.Total_test_points);
        // $('.quo-active form.special_form input[name="blind_and_buried_hole"]').val(list.Blind_and_buried_hole);
        // $('.quo-active form.special_form input[name="blind_hole_structure"]').val(list.Blind_hole_structure);
        // $('.quo-active form.special_form input[name="countersunk_deep_holes"]').val(list.Countersunk_deep_holes);
        // $('.quo-active form.special_form input[name="special_inner_hole_line"]').val(list.Inner_hole_line);
    }
    // PCB 阶梯价
    function cpoPcbQuoStairPrice(stair_price) {
        ajax.jsonRpc("/get_pcb_stair_price", 'call', {
            'pcb_value': stair_price.pcb_value,
            'cpo_country': stair_price.cpo_country,
            'cpo_express': stair_price.cpo_express,
            'pcb_special_requirements': stair_price.pcb_special_requirements,
        }).then(function (data) {
            if(data){
                if(data.warning){
                    $('.pcb_calculation_results .calculation_content').removeClass('cpo-block').addClass('cpo-none');
                    webAlert(data.warning, null, false);
                    // alert(data.warning);
                }else{
                    $('.cpo_pcb_calcula_content .pcb_try_quantity .cpo_quantity_content').empty();
                    if(data.price_list.length){
                        $('.cpo_pcb_calcula_content .pcb_try_quantity').addClass('cpo-block').removeClass('cpo-none');
                        $.each(data.price_list, function (price_key, price_val) {
                            if(price_key == 0){
                                $.each(price_val, function (key_p, key_l) {
                                    if(key_l != ''){
                                        $('.pcb_try_quantity .cpo_quantity_content').append('\n'+
                                        '<div class="cpo_quantiry_line cpo_quantity_select">\n' +
                                        '<div class="cpo_try_icon cpo_try_select_icon"></div>\n' +
                                        '<p class="cpo_try_quantity">\n' +
                                        '<span>'+key_p+'</span>\n' +
                                        '<span>$ '+ key_l.toFixed(2) +' </span>\n' +
                                        '</p>\n' +
                                        '</div>');
                                    }
                                })
                            }else{
                                $.each(price_val, function (key_p, key_l) {
                                    if(key_l != ''){
                                        $('.pcb_try_quantity .cpo_quantity_content').append('\n'+
                                        '<div class="cpo_quantiry_line">\n' +
                                        '<div class="cpo_try_icon"></div>\n' +
                                        '<p class="cpo_try_quantity">\n' +
                                        '<span>'+key_p+'</span>\n' +
                                        '<span>$ '+ key_l.toFixed(2) +' </span>\n' +
                                        '</p>\n' +
                                        '</div>');
                                    }
                                })
                            }
                        })
                    }else{
                        $('.cpo_pcb_calcula_content .pcb_try_quantity').addClass('cpo-none').removeClass('cpo-block');
                    }
                }
            }
        })
    }
    // 点击Try PCB 数量
    $('.cpo_pcb_calcula_content  .pcb_try_quantity .cpo_quantity_content').on('click', '.cpo_quantiry_line', function () {
        $(this).find('div').addClass('cpo_try_select_icon');
        $(this).siblings().find('div').removeClass('cpo_try_select_icon');
        $(this).addClass('cpo_quantity_select').siblings().removeClass('cpo_quantity_select');

        var cpo_country = $('.cpo_country_list select').val();
        var cpo_express = $('.cpo_order_express_message select').val();
        var pcb_from = pcbGetFormData();
        var pcb_special_requirements = pcbQuotationSpecialForm();
        if($(this).find('div').hasClass('cpo_try_select_icon')){
           var this_val = $(this).find('span:first').html();
           ajax.jsonRpc("/get_pcb_try_qty", 'call', {
                'pcb_value': pcb_from,
                'cpo_country': cpo_country,
                'cpo_express': cpo_express,
                'pcb_special_requirements': pcb_special_requirements,
                'this_val': this_val
           }).then(function (data) {
               $('#cpo_pcb_result .pcb_fixed_data .expedited_days').val("");
               pcbAllData(data);
               $('.quo-active .cpo_pcb_quotation input[name="pcb_quantity"]').val(data.pcb_value.cpo_quantity)
           })
        }
    })
    // 加急天数循环
    $('.cpo_pcb_calcula_content .cpo_try_expedited_list').on('click', '.cpo_quantiry_line', function () {
        $(this).find('div').toggleClass('cpo_try_select_icon');
        $(this).siblings().find('div').removeClass('cpo_try_select_icon');
        $(this).toggleClass('cpo_quantity_select').siblings().removeClass('cpo_quantity_select');
        var cpo_delivery = $('.cpo_assembly_cost input[name="cpo_delivery"]').val().replace(/[^0-9]/ig,"");
        var this_val = $(this).find('span:first').html();
        if($(this).find('div').hasClass('cpo_try_select_icon')){
            if(this_val == cpo_delivery){
                $('#cpo_pcb_result .pcb_fixed_data .expedited_days').val("");
            }else{
                $('#cpo_pcb_result .pcb_fixed_data .expedited_days').val(this_val);
            }
        }else{
            $('#cpo_pcb_result .pcb_fixed_data .expedited_days').val("");
        }
        var cpo_country = $('.cpo_country_list select').val();
        var cpo_express = $('.cpo_order_express_message select').val();
        var expedited_days = $('#cpo_pcb_result .expedited_days').val();
        var pcb_from = pcbGetFormData();
        var pcb_special_requirements = pcbQuotationSpecialForm();
        $('#step_next').css('display', 'inline-block');
        ajax.jsonRpc("/shop_pcb_confirm_urgent_service", 'call', {
            'pcb_value': pcb_from,
            'cpo_country': cpo_country,
            'cpo_express': cpo_express,
            'pcb_special_requirements': pcb_special_requirements,
            'expedited_days': expedited_days,
        }).then(function (data) {
            pcbAllData(data);
        })

    });


//---PCB 报价 End Version-0.3 -----------------------------------------------------------------------------------------------------------

//---HDI 报价 Begin Version-0.3----------------------------------------------------------------------------------------------------------

    //HDI 值
    var cpoHdi = function () {
        // var inputAll = $('form.cpo_hdi_quotation input[type="text"]');
        var number_of_step = $('.quo-active .cpo_hdi_quotation .number_of_step').val();
        var valAll = {
            'number_of_step': number_of_step
        }
        return valAll;
    }
    // 点击HDI报价计算
    // var hdi_click = $('.quo-active .cpo_hdi_calcula_content .cpo_calculation');
    var hdi_click = $('.cpo_hdi_calcula_content .cpo_calculation');

    hdi_click.on('click', function () {
        // var country_val = checkCountry();
        // if(!country_val){
        //     return false;
        // }
        var pcbcheckdata = checkPCBData03();

        if(!pcbcheckdata){
            return false;
        }
        var cpo_country = $('.quo-active .cpo_country_list select').val();
        var cpo_express = $('.quo-active .cpo_order_express_message select').val();
        var cpo_source = $('.cpo_source_cp input[name="cpo_source"]').val();
        var pcb_from = pcbGetFormData();
        var pcb_special_requirements = pcbQuotationSpecialForm();
        var cpohdi = cpoHdi();
        pcb_from.pcb_hdi = cpohdi;

        ajax.jsonRpc('/get/hdi', 'call', {
            'cpo_country': cpo_country,
            'cpo_express': cpo_express,
            'cpo_source': cpo_source,
            'pcb_value': pcb_from,
            'pcb_special_requirements': pcb_special_requirements,
        }).then(function (data) {
            var order_name = 'HDI';
            setQuotationData(data, order_name)
            if(data.error){
                $('.calculation_content').addClass('cpo-none').removeClass('cpo-block');
                $('#cpo_hdi_result_form #step_next').css('display','none');
                $('.calculation_content>div.cpo_cost_fee').addClass('cpo-none').removeClass('cpo-block');
                var waring_str = '';
                var waring_num = 1;
                if(data.error.e){
                    webAlert('1. Data cannot be empty !\n2.Please check if the data type is correct!', null, false);
                    // alert('1. Data cannot be empty !\n2.Please check if the data type is correct!');
                    return false;
                }else{
                    $.each(data.error, function (war_key, war_value) {
                        waring_str = showWarning(war_key, war_value, waring_str, waring_num)

                    });
                    if(waring_str){
                        webAlert(waring_str, null, false);
                        // alert(waring_str);
                    }
                }

            }else if(data.login){
                getLoginData(data);
            }else{
                $('.cpo-warning').empty();
                // var order_name = 'HDI';
                // setQuotationData(data, order_name)
                $('.calculation_content').addClass('cpo-block').removeClass('cpo-none');
                $('.calculation_content>div.cpo_cost_fee').addClass('cpo-block').removeClass('cpo-none');
                $('#cpo_hdi_result_form #step_next').css('display', 'block');
                $('#cpo_hdi_result_form .cpo_pcb_all_fee .pcb_fee_ul').empty(); //清空所有价格（避免重复）
                var pcb_price_detailed = data.pcb_price_detailed;
                $.each(pcb_price_detailed, function (pf_key, pf_value) {
                    if(pf_key == 'Cost By'){
                        $('#cpo_hdi_result_form .cpo_pcb_all_fee .pcb_fee_ul').append('<li>\n'+
                                '<span class="ul_span">Cost By ㎡</span>\n'+
                                '<span class="ul_span_cost">\n'+
                                    '<i>$</i>\n'+
                                    '<input type="text" name="'+pf_key+'" value="'+pf_value+'" readonly="readonly"/>\n'+
                                '</span></li>')
                    }else{
                        $('#cpo_hdi_result_form .cpo_pcb_all_fee .pcb_fee_ul').append('<li>\n'+
                                    '<span class="ul_span">'+ pf_key +'</span>\n'+
                                    '<span class="ul_span_cost">\n'+
                                        '<i>$</i>\n'+
                                        '<input type="text" name="'+pf_key+'" value="'+pf_value+'" readonly="readonly"/>\n'+
                                    '</span></li>')
                    }
                });
                var calculate_return = data.hdi_quotation.value; // 计算返回的数据
                $('#cpo_hdi_result_form .cpo_cost_fee input[name="cpo_pcb_quantity"]').val(data.pcb_value.cpo_quantity +' '+data.pcb_value.pcb_qty_unit);
                $('#cpo_hdi_result_form .cpo_cost_fee input[name="cpo_freight"]').val(data.hdi_quotation['Shipping Cost']);
                $('#cpo_hdi_result_form .cpo_cost_fee input[name="cpo_delivery"]').val(calculate_return['Delivery Period']);
                $('#cpo_hdi_result_form .cpo_cost_fee input[name="cpo_flat_area"]').val(calculate_return['PCB Area']+' '+'㎡');
                $('#cpo_hdi_result_form .cpo_cost_fee input[name="part_fee"]').val(calculate_return['Board Price Cost']);
                $('#cpo_hdi_result_form .cpo_cost_fee input[name="cpo_engineering_fee"]').val(calculate_return['Set Up Cost']);
                var e_test_fee = calculate_return['E-test Fixture Cost'];
                var film_fee = calculate_return['Film Cost'];
                if(e_test_fee){
                    $('.quo-active .pcb_e_test_cost').addClass('cpo-block').removeClass('cpo-none');
                    $('.quo-active .pcb_e_test_cost input.e_test_cost').val(e_test_fee);
                }else{
                    $('.quo-active .pcb_e_test_cost').addClass('cpo-none').removeClass('cpo-block');
                }
                if(film_fee){
                    $('.quo-active .pcb_film_cost').addClass('cpo-block').removeClass('cpo-none');
                    $('.quo-active .pcb_film_cost input.film_cost').val(film_fee);
                }else{
                    $('.quo-active .pcb_film_cost').addClass('cpo-none').removeClass('cpo-block');
                }
                var all_fee = parseFloat(calculate_return['Total Cost']) + parseFloat(data.hdi_quotation["Shipping Cost"]);
                $('#cpo_hdi_result_form .cpo_cost_fee input[name="all_fee"]').val(all_fee.toFixed(2));
                $.each(pcb_price_detailed, function (paf_key, paf_value) {
                    $('#cpo_hdi_result_form #cpo_pcb_result .pcb_result').append('<input type="hidden" name="'+ paf_key +'" value="'+ paf_value + '"/>');
                });
                // 列出所有数据传递下一个页面
                $('#cpo_hdi_result_form #cpo_pcb_result .pcb_surface').empty();
                $('#cpo_hdi_result_form #cpo_pcb_result .pcb_result').empty();
                var pcb_value_list = data.pcb_value;
                $.each(pcb_value_list, function (pcb_key, pcb_value) {
                    if(pcb_key == 'pcb_surfaces'){
                        $.each(pcb_value_list.pcb_surfaces, function (pcb_sur_key, pcb_sur_value) {
                            $('#cpo_hdi_result_form #cpo_pcb_result .pcb_surface').append('<input type="hidden" name="'+ pcb_sur_key +'" value="'+ pcb_sur_value + '"/>');
                        })
                    }else{
                        $('#cpo_hdi_result_form #cpo_pcb_result .pcb_result').append('<input type="hidden" name="'+ pcb_key +'" value="'+ pcb_value + '"/>');
                    }
                });
                // HDI data
                if(data.pcb_value.pcb_hdi){
                    $.each(data.pcb_value.pcb_hdi, function (hdi_key, hdi_val) {
                        $('#cpo_hdi_result_form #cpo_pcb_result .pcb_result').append('<input type="hidden" name="'+ hdi_key +'" value="'+ hdi_val + '"/>')
                    });
                }
                // 特殊数据
                var pcb_special_list = data.pcb_special_requirements; //特殊数据
                $('#cpo_hdi_result_form .pcb_special_requirements')
                $.each(pcb_special_list, function (pcb_res_key, pcb_res_value) {
                    $('#cpo_hdi_result_form .pcb_special_requirements').append('<input type="hidden" name="'+ pcb_res_key +'" value="'+ pcb_res_value + '"/>');
                })

                pcbSpecialCallBack(pcb_special_list);
            }
        });

    });
//---HDI 报价 End Version-0.3----------------------------------------------------------------------------------------------------------

//---Flex-Rigid 报价 Begin Version-0.3 --------------------------------------------------------------------------------------------------------------
    function cpoFlexRigidForm(){
        var pcb_soft_hard;
        var cpo_inner_outer = $('.quo-active .flex_form .cpo_inner_outer').val();
        var cpo_flex_open = $('.quo-active .flex_form .cpo_flex_open').val();
        var cpo_flex_number = $('.quo-active .flex_form .cpo_flex_number').val();
        pcb_soft_hard = {
            'cpo_inner_outer': cpo_inner_outer,
            'cpo_flex_open': cpo_flex_open,
            'cpo_flex_number': cpo_flex_number,
        }
        return pcb_soft_hard;
    }
    function flexFormCheck(){
        var flag = true;
        $('.quo-active .flex_form input[type="text"]').each(function () {
            if($(this).val() == ''){
                flag = false;
                $(this).css('border', '1px solid red');
                $(this).focus();
                return flag;
            }else{
                return flag;
            }
        });
    }

    $('.cpo_flex_rigid_calcula_content .cpo_calculation').on('click', function () {
        // var country_val = checkCountry();
        // if(!country_val){
        //     return false;
        // }
        var pcbcheckdata = checkPCBData03();
        var flexform = flexFormCheck();
        if(!pcbcheckdata){
            return false;
        }
        if(flexform){
            return false;
        }
        var cpo_country = $('.quo-active .cpo_country_list select').val();
        var cpo_express = $('.quo-active .cpo_order_express_message select').val();
        var cpo_source = $('.cpo_source_cp input[name="cpo_source"]').val();
        var pcb_from = pcbGetFormData();
        var pcb_special_requirements = pcbQuotationSpecialForm();
        var soft_hard = cpoFlexRigidForm();

        pcb_from.pcb_soft_hard = soft_hard;
        ajax.jsonRpc('/flex-rigid', 'call', {
            'cpo_country': cpo_country,
            'cpo_express': cpo_express,
            'cpo_source': cpo_source,
            'pcb_value': pcb_from,
            'pcb_special_requirements': pcb_special_requirements,
            'pcb_soft_hard': soft_hard,
        }).then(function (data) {
            var order_name = 'Rigid-FLex';
            setQuotationData(data, order_name)
            if(data.error){
                $('.flexrigid_calculation_results .calculation_content').addClass('cpo-none').removeClass('cpo-block');
                var waring_str = '';
                var waring_num = 1;
                if(data.error.e){
                    webAlert('Please check the data !', null, false);
                    // alert('Please check the data !');
                    return false;
                }else {
                    $.each(data.error, function (war_key, war_value) {
                        waring_str = showWarning(war_key, war_value, waring_str, waring_num)

                    });
                    if(waring_str){
                        webAlert(waring_str, null, false);
                        // alert(waring_str);
                    }
                    $('#cpo_flexrigid_result_form #step_next').css('display','block');
                    $('.calculation_content>div.cpo_cost_fee').addClass('cpo-none').removeClass('cpo-block');
                }
            }else if(data.login){
                getLoginData(data);
            }else {

                $('.cpo-warning').empty();
                // var order_name = 'Rigid-FLex';
                // setQuotationData(data, order_name)
                $('#cpo_flexrigid_result_form #step_next').css('display','block');
                $('.calculation_content').addClass('cpo-block').removeClass('cpo-none');
                $('.calculation_content>div.cpo_cost_fee').addClass('cpo-block').removeClass('cpo-none');
                var flex_rigid_return_val = data.value.value;
                var flex_rigid_val = data.pcb_value.pcb_soft_hard;
                var pcb_value = data.pcb_value;
                $('#cpo_flexrigid_result_form input[name="cpo_pcb_quantity"]').val(pcb_value.cpo_quantity+' '+'PCS'); // 硬板
                $('#cpo_flexrigid_result_form input[name="cpo_flex_quantity"]').val(data.flex_layers+' '+'L'); // 软板
                $('#cpo_flexrigid_result_form input[name="cpo_flat_area"]').val(flex_rigid_return_val['PCB Area']+' '+'㎡'); //

                $('.cpo_flex_rigid_calcula_content .calculation_content').addClass('cpo-block').removeClass('cpo-none'); // 展示数据
                $('#cpo_flexrigid_result_form input[name="cpo_delivery"]').val(flex_rigid_return_val['Delivery Period']); //
                $('#cpo_flexrigid_result_form input[name="part_fee"]').val(flex_rigid_return_val['Board Price Cost']); //
                $('#cpo_flexrigid_result_form input[name="cpo_freight"]').val(data.value['Shipping Cost']); //
                if(data.value.value['E-test Fixture Cost'] > 0){
                    $('#cpo_flexrigid_result_form .cpo_e_test_box').addClass('cpo-block').removeClass('cpo-none');
                    $('#cpo_flexrigid_result_form input[name="e_test_cost"]').val(data.value.value['E-test Fixture Cost']); //
                }else{
                    $('#cpo_flexrigid_result_form .cpo_e_test_box').addClass('cpo-none').removeClass('cpo-block');
                    $('#cpo_flexrigid_result_form input[name="e_test_cost"]').val(0);
                }
                $('#cpo_flexrigid_result_form input[name="cpo_engineering_fee"]').val(data.value.value['Set Up Cost']); //
                var all_fee = parseFloat(data.value.value['Total Cost']) + parseFloat(data.value['Shipping Cost']);
                $('#cpo_flexrigid_result_form input[name="all_fee"]').val(all_fee.toFixed(2)); //
                var pcb_price_detailed = data.pcb_price_detailed;
                $('#cpo_flexrigid_result_form .cpo_pcb_all_fee .pcb_fee_ul').empty();
                $.each(pcb_price_detailed, function (pf_key, pf_value) {
                    if(pf_key == 'Cost By'){
                        $('#cpo_flexrigid_result_form .cpo_pcb_all_fee .pcb_fee_ul').append('<li>\n'+
                                '<span class="ul_span">Cost By ㎡</span>\n'+
                                '<span class="ul_span_cost">\n'+
                                    '<i>$</i>\n'+
                                    '<input type="text" name="'+pf_key+'" value="'+pf_value+'" readonly="readonly"/>\n'+
                                '</span></li>')
                    }else{
                        $('#cpo_flexrigid_result_form .cpo_pcb_all_fee .pcb_fee_ul').append('<li>\n'+
                                    '<span class="ul_span">'+ pf_key +'</span>\n'+
                                    '<span class="ul_span_cost">\n'+
                                        '<i>$</i>\n'+
                                        '<input type="text" name="'+pf_key+'" value="'+pf_value+'" readonly="readonly"/>\n'+
                                    '</span></li>')
                    }
                });
                // Rigid data
                $('#cpo_flexrigid_result_form #cpo_pcb_result .pcb_result').empty();
                $.each(pcb_value, function (pkey, pvalue) {
                    $('#cpo_flexrigid_result_form #cpo_pcb_result .pcb_result').append('<input type="hidden" name="' + pkey + '" value="' + pvalue + '"/>');
                });
                $.each(pcb_value.pcb_surfaces, function (pcb_sur_key, pcb_sur_value) {
                    $('#cpo_flexrigid_result_form #cpo_pcb_result .pcb_surface').append('<input type="hidden" name="' + pcb_sur_key + '" value="' + pcb_sur_value + '"/>');
                })
                $.each(pcb_value.pcb_soft_hard, function (sh_key, sh_value) {
                    $('#cpo_flexrigid_result_form #cpo_pcb_result .pcb_soft_hard').append('<input type="hidden" name="' + sh_key + '" value="' + sh_value + '"/>');
                })
                $.each(data.pcb_special_requirements, function (sp_key, sp_value) {
                    $('#cpo_flexrigid_result_form #cpo_pcb_result .pcb_special_requirements').append('<input type="hidden" name="' + sp_key + '" value="' + sp_value + '"/>');
                })
                pcbSpecialCallBack(data.pcb_special_requirements);
                // $.each(pcb_value, function (pkey, pvalue) {
                //     if (pkey == 'pcb_surfaces') {
                //         $.each(pcb_value.pcb_surfaces, function (pcb_sur_key, pcb_sur_value) {
                //             $('#cpo_flexrigid_result_form #cpo_pcb_result .pcb_surface').append('<input type="hidden" name="' + pcb_sur_key + '" value="' + pcb_sur_value + '"/>');
                //         })
                //     } else {
                //         $('#cpo_flexrigid_result_form #cpo_pcb_result .pcb_result').append('<input type="hidden" name="' + pkey + '" value="' + pvalue + '"/>');
                //     }
                // });
            }
        });
    });

//---Flex-Rigid 报价 End Version-0.3 --------------------------------------------------------------------------------------------------------------

//---PCBA 报价 Begin Version-0.3 --------------------------------------------------------------------------------------------------------------
    // 选择PCB板材的供应方式
    $('#pcba_data_quotation .cpo_input_pcb_supply').on('change', function () {
        if($(this).val()=='chinapcbone'){
            $('#cpo_pcba_online_content .cpo_pcba_need_pcb').addClass('cpo-block').removeClass('cpo-none');
        }else{
            $('#cpo_pcba_online_content .cpo_pcba_need_pcb').addClass('cpo-none').removeClass('cpo-block');
        }
    });
    // 是否有其它特殊需求
    $('#pcba_data_quotation .cpo_select_value').on('change', function () {
        if($(this).val() == 'Other'){
            $('#pcba_data_quotation .pcba_special_request_other').addClass('cpo-block').removeClass('cpo-none');
        }else{
            $('#pcba_data_quotation .pcba_special_request_other').addClass('cpo-none').removeClass('cpo-block');
        }
    })
    //PCBA form取值
    function pcbaGetForm() {
        var pcba_value_dict;
        var cpo_quantity = $('#pcba_data_quotation input[name="cpo_input_quantity"]').val();
        var cpo_width = $('#pcba_data_quotation input[name="cpo_input_width"]').val();
        var cpo_length = $('#pcba_data_quotation input[name="cpo_input_lenght"]').val();
        var cpo_dip_qty = $('#pcba_data_quotation input[name="cpo_input_dip"]').val();
        var cpo_smt_qty = $('#pcba_data_quotation input[name="cpo_input_smt"]').val();
        var cpo_side = $('#pcba_data_quotation select.pcba_smt_side').val();
        var pcb_thickness = $('#pcba_data_quotation input[name="cpo_input_copper"]').val();
        var cpo_components_supply = $('#pcba_data_quotation .cpo_components_supply').val();
        var cpo_pcb_supply = $('#pcba_data_quotation select.cpo_input_pcb_supply').val();
        var cpo_select_value;
        var special_request = $('#pcba_data_quotation select.cpo_select_value').val();
        var pcba_other_request = $('#pcba_data_quotation .pcba_other_request').val();
        if(special_request == 'Other'){
            cpo_select_value = pcba_other_request;
        }else{
            cpo_select_value = special_request;
        }

        pcba_value_dict = {
            'cpo_quantity': cpo_quantity,
            'cpo_width': cpo_width,
            'cpo_length': cpo_length,
            'cpo_dip_qty': cpo_dip_qty,
            'cpo_smt_qty': cpo_smt_qty,
            'cpo_side': cpo_side,
            'pcb_thickness': pcb_thickness,
            'cpo_components_supply': cpo_components_supply,
            'cpo_pcb_supply': cpo_pcb_supply,
            'cpo_select_value': cpo_select_value,
        }
        return pcba_value_dict
    }
        // PCB From 数据提取
    function pcbaGetPCBFormData(){
        var pcb_value_dict;
        var pcb_qty_unit = $('.cpo_pcba_need_pcb .cpo-ps-rl i.cpo-radio-select').siblings('span').html();
        var pcb_pcs_size = '';
        var pcb_item_size = '';

        var quality_standard = $('.cpo_pcba_need_pcb .cpo_pcb_quotation .quality_standard').val();
        var pcb_quantity = $('.cpo_pcba_need_pcb .cpo_pcb_quotation input[name="pcb_quantity"]').val();
        if(pcb_qty_unit == 'Panel'){
            pcb_pcs_size = $('.cpo_pcba_need_pcb .cpo_pcb_quotation input[name="pcb_panel_pcs"]').val();
            pcb_item_size = $('.cpo_pcba_need_pcb .cpo_pcb_quotation input[name="pcb_panel_item"]').val();
        }
        var pcb_length = $('.cpo_pcba_need_pcb .cpo_pcb_quotation input[name="pcb_length"]').val();
        var pcb_breadth = $('.cpo_pcba_need_pcb .cpo_pcb_quotation input[name="pcb_breadth"]').val();
        var cpo_layers = $('.cpo_pcba_need_pcb .cpo_pcb_quotation .cpo_layers').val();

        // 基材
        var rogers_number = 1;
        var cpo_raw_material;
        var pcb_rogers = null;
        var cpo_material = $('.cpo_pcba_need_pcb .cpo_pcb_quotation .cpo_material').val();
        var material_value = $('.cpo_pcba_need_pcb .cpo_pcb_quotation .material_value').val();
        var core_thick = $('.cpo_pcba_need_pcb .cpo_pcb_quotation .cpo_core_board').val();
        // var rogers_number = $('.cpo_pcba_need_pcb .cpo_pcb_quotation input[name="cpo_rogers_number"]').val();
        if(cpo_material == 'FR4'){
            cpo_raw_material = cpo_material+'-'+material_value;
        }else{
            cpo_raw_material = cpo_material+' '+material_value;
            pcb_rogers = {
                'core_thick': core_thick,
                'rogers_number': rogers_number
            }
        }

        var cpo_thickness = $('.cpo_pcba_need_pcb .cpo_pcb_quotation input[name="cpo_thickness"]').val();
        var cpo_inner_copper;
        var inner_copper = $('.cpo_pcba_need_pcb .cpo_pcb_quotation .inner_copper').val();
        if(inner_copper == '0'){
            cpo_inner_copper = '';
        }else{
            cpo_inner_copper = inner_copper;
        }
        var cpo_outer_copper = $('.cpo_pcba_need_pcb .cpo_pcb_quotation .outer_copper').val();
        var cpo_mask_color = $('.cpo_pcba_need_pcb .cpo_pcb_quotation .cpo_mask_color').val();
        var cpo_silkscreen_color = $('.cpo_pcba_need_pcb .cpo_pcb_quotation .cpo_silkscreen_color').val();

        var surface_conventional = $('.cpo_pcba_need_pcb .cpo_pcb_quotation .surface_value').val();
        var surface_combination = $('.cpo_pcba_need_pcb .cpo_pcb_quotation .surface_combination').val();
        //表面处理值
        var cpo_surface_treatment = {};
        if(surface_conventional == 'Gold finger' || surface_combination == 'Gold finger'){
            cpo_surface_treatment.gold_finger_thickness = $('.cpo_pcb_quotation .gold_finger_thickness').val();
            cpo_surface_treatment.gold_finger_length = '';
            cpo_surface_treatment.gold_finger_width = '';
            cpo_surface_treatment.gold_finger_qty = '';
        }
        if(surface_conventional.indexOf("Immersion gold") != -1){
            cpo_surface_treatment.nickel_thickness = '120';
            cpo_surface_treatment.coated_area = '30';
        }
        if(surface_combination == 'No'){
            cpo_surface_treatment.surface_value = surface_conventional;
        }else{
            cpo_surface_treatment.surface_value = surface_conventional+' '+surface_combination;
        }
        var cpo_vias = $('.cpo_pcba_need_pcb .cpo_pcb_quotation .cpo_vias').val();
        var cpo_e_test = $('.cpo_pcba_need_pcb .cpo_pcb_quotation .cpo_e_test').val();
        var pcb_special_requirements = pcbaNeedPCBSpecialForm();
        pcb_value_dict = {
            'quality_standard': quality_standard,
            'cpo_quantity': pcb_quantity,
            'pcb_qty_unit': pcb_qty_unit,
            'pcb_length': pcb_length,
            'pcb_breadth': pcb_breadth,
            'pcb_pcs_size':pcb_pcs_size,
            'pcb_item_size':pcb_item_size,
            'pcb_rogers': pcb_rogers,
            'pcb_layer': cpo_layers,
            'pcb_type': cpo_raw_material,
            'pcb_thickness': cpo_thickness,
            'pcb_inner_copper': cpo_inner_copper,
            'pcb_outer_copper': cpo_outer_copper,
            'pcb_solder_mask': cpo_mask_color,
            'pcb_silkscreen_color': cpo_silkscreen_color,
            'pcb_surfaces': cpo_surface_treatment,
            'pcb_vias': cpo_vias,
            'pcb_test': cpo_e_test,
            'pcb_special_requirements': pcb_special_requirements,

        }
        return pcb_value_dict
    }
    // PCB 特殊数据
    function pcbaNeedPCBSpecialForm(){
        var pcb_special_value;
        var Semi_hole = $('.cpo_pcba_need_pcb form.special_form select.special_semi_hole').val();
        var Edge_plating = $('.cpo_pcba_need_pcb form.special_form select.special_edge_plating').val();
        var Impedance = $('.cpo_pcba_need_pcb form.special_form select.special_impedance').val();
        var Press_fit = $('.cpo_pcba_need_pcb form.special_form select.special_press_fit').val();
        var Peelable_mask = $('.cpo_pcba_need_pcb form.special_form select.special_peelable_mask').val();
        var Carbon_oil = $('.cpo_pcba_need_pcb form.special_form select.pcb_carbon_ink').val();
        var Min_line_width = $('.cpo_pcba_need_pcb form.special_form input.min_line_width').val();
        var Min_line_space = $('.cpo_pcba_need_pcb form.special_form input.special_line_space').val();
        var Min_aperture = $('.cpo_pcba_need_pcb form.special_form input.special_minimum_aperture').val();
        var Total_holes = $('.cpo_pcba_need_pcb form.special_form input.special_total_number').val();
        var Copper_weight_wall = $('.cpo_pcba_need_pcb form.special_form input.special_copper_hall').val();
        var Number_core = $('.cpo_pcba_need_pcb form.special_form input.special_number_core').val();
        var PP_number = $('.cpo_pcba_need_pcb form.special_form input.special_pp_number').val();
        var Total_test_points = $('.cpo_pcba_need_pcb form.special_form input.special_total_test').val();
        var Blind_and_buried_hole = $('.cpo_pcba_need_pcb form.special_form input.blind_and_buried_hole').val();
        var Blind_hole_structure = $('.cpo_pcba_need_pcb form.special_form input.blind_hole_structure').val();
        var Depth_control_routing = $('.cpo_pcba_need_pcb form.special_form select.special_depth_control').val();
        var Number_back_drilling = $('.cpo_pcba_need_pcb form.special_form select.special_back_drilling').val();
        var Countersunk_deep_holes = $('.cpo_pcba_need_pcb form.special_form input.countersunk_deep_holes').val();
        var Laser_drilling = $('.cpo_pcba_need_pcb form.special_form select.special_laser_drilling').val();
        var The_space_for_drop_V_cut = $('.cpo_pcba_need_pcb form.special_form select.special_v_cut_space').val();
        var Inner_hole_line = $('.cpo_pcba_need_pcb form.special_form input.special_inner_hole_line').val();

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
    function cpoGetfileData(){
        var file_data = {}
        $('#pcba_need_pcb_form input').each(function () {
            var name = this.name;
            file_data.name = $(this).val();
        });
        return file_data
    }
    //PCBA 统一PCB的数量、长宽
    $('#pcba_data_quotation').on('change', 'input', function () {
        if($(this).attr('name') == 'cpo_input_quantity'){
            $('.cpo_pcba_need_pcb .cpo_pcb_quotation input[name="pcb_quantity"]').val($(this).val());
            getAreaBoard();
        }else if($(this).attr('name') == 'cpo_input_lenght'){
            $('.cpo_pcba_need_pcb .cpo_pcb_quotation input[name="pcb_length"]').val($(this).val());
            getAreaBoard();
        }else if($(this).attr('name') == 'cpo_input_width'){
            $('.cpo_pcba_need_pcb .cpo_pcb_quotation input[name="pcb_breadth"]').val($(this).val());
            getAreaBoard();
        }else if($(this).attr('name') == 'cpo_input_copper'){
            $('.cpo_pcba_need_pcb .cpo_pcb_quotation input[name="cpo_thickness"]').val($(this).val());
        }
    })

    $('.cpo_pcba_need_pcb .cpo_pcb_quotation').on('change', 'input', function () {
        if($(this).attr('name') == 'pcb_quantity'){
            $('#pcba_data_quotation input[name="cpo_input_quantity"]').val($(this).val());
            getAreaBoard();
        }else if($(this).attr('name') == 'pcb_length'){
            $('#pcba_data_quotation input[name="cpo_input_lenght"]').val($(this).val());
            getAreaBoard();
        }else if($(this).attr('name') == 'pcb_breadth'){
            $('#pcba_data_quotation input[name="cpo_input_width"]').val($(this).val());
            getAreaBoard();
        }else if($(this).attr('name') == 'cpo_thickness'){ //这个是PCB板厚
            $('#pcba_data_quotation input[name="cpo_input_copper"]').val($(this).val());
        }
    })
    //点击PCBA计算
    var cpo_calculation = $('.pcba_calculation_results .cpo_calculation');
    cpo_calculation.on('click', function () {
        cpoPCBAResultCalculation(); // 调用计算函数
    });
    // PCBA 点击下一步
    $('#cpo_pcba_shop_product #step_next').on('click', function () {
        var edit_id = $('#cpo_pcba_shop_product .pcb_edit input[name="edit_id"]');
        if(edit_id.length > 0){
            $('#cpo_pcba_shop_product').submit();
            return
        }else{
            $('#cpo_need_pcb_modal').modal('show');
        }
    });
    // 不需要PCB板，直接创建订单
    $('#not_pcb_order_btn').on('click', function () {
        $('#cpo_pcba_shop_product').submit();
    });
    // 需要PCB板，跳转到PCB下单
    $('#need_pcb_order_btn').on('click', function () {
        var pcba_value = pcbaGetForm();
        var file_data = cpoGetfileData();
        var edit_id = $('#cpo_pcba_shop_product .pcb_edit input[name="edit_id"]');
        if(edit_id.length > 0){
            $('#pcba_need_pcb_form').submit();
        }else{
            $('#cpo_pcba_shop_product').submit();
        }
    });
    
    // PCBA 价格计算 Function
    function cpoPCBAResultCalculation(){

        var cpo_country = $('.pcba_calculation_results .cpo_country_list select').val();
        var cpo_express = $('.pcba_calculation_results .cpo_order_express_message select').val();
        var cpo_source = $('.cpo_source_cp input[name="cpo_source"]').val();
        // var pcb_from = pcbGetFormData();
        // var pcb_special_requirements = pcbQuotationSpecialForm();
        // 判断数据是否没填写
        var checkpcbadata = checkPCBAData();
        if(!checkpcbadata){
            return false;
        }
        var cpo_select_pcb = false;
        var pcba_value = pcbaGetForm(); // PCBA Value
        var pcb_value = null; // PCB Value
        if(pcba_value.cpo_pcb_supply == 'chinapcbone'){
            pcb_value = pcbaGetPCBFormData();
            cpo_select_pcb = true;
        }

        var cpo_area = (pcba_value.cpo_width * pcba_value.cpo_length) * pcba_value.cpo_quantity / (Math.pow(10,6))
        if(cpo_select_pcb){
            if(cpo_area >= 10){
                // cpo_need_pcb_select_click(pcb_select);
                webAlert('The total area cannot exceed 10 ㎡ !', null, false);
                // alert('The total area cannot exceed 10 ㎡ !')
                return false;
            }
        }
        // 阶梯价所需数据
        var stair_price = {
            'pcba_value': pcba_value,
            'cpo_select_pcb': cpo_select_pcb,
            'cpo_country': cpo_country,
            'cpo_express': cpo_express,
            'pcb_value': pcb_value,
        }
        $('#step_next').css('display', 'block');
        ajax.jsonRpc("/get_pcba_price", 'call', {
            'pcba_value': pcba_value,
            'cpo_source': cpo_source, // 优惠券码
            'cpo_select_pcb': cpo_select_pcb,
            'cpo_country': cpo_country,
            'cpo_express': cpo_express,
            'pcb_value': pcb_value,
        }).then(function (data) {

            pcbaReturnResultData(data);
            //阶梯价对比
            cpoPCBAStairPrice(stair_price);
            // // 报价记录
            // var order_name = 'PCBA';
            // setQuotationData(data, order_name);

        });
    }
    // PCBA Data渲染
    function pcbaReturnResultData(data){
        // 报价记录
        var order_name = 'PCBA';
        setQuotationData(data, order_name);
        if(data){
            if(data.waring){
                var waring_str = '';
                var waring_num = 1;
                $.each(data.waring, function (war_key, war_value) {
                    waring_str = showWarning(war_key, war_value, waring_str, waring_num);
                });
                if(waring_str){
                    webAlert(waring_str, null, false);
                    // alert(waring_str);
                }
                // $.each(data.waring, function (war_key, war_value) {
                //     if(war_value != null){
                //         waring_str += waring_num +' : '+ war_value + '\n';
                //         waring_num++;
                //     }
                // });
                $('#step_next').css('display','none');
                $('.calculation_content>div.cpo_cost_fee').addClass('cpo-none').removeClass('cpo-block');
                // alert(waring_str);
            }else if(data.login){
                getLoginData(data);
            }else{
                $('.order_page_ad').addClass('cpo-none');
                $('.calculation_content>div.cpo_cost_fee').addClass('cpo-block').removeClass('cpo-none');
                var cpo_price_list = data.cpo_price_list;
                // PCBA 数据
                $('#cpo_pcba_result').empty();
                $('#pcba_need_pcb_form .need_form_content').empty();
                $.each(data.pcba_value, function (need_pk, need_pl) {
                    $('#pcba_need_pcb_form .need_form_content').append('<input type="hidden" name="'+ need_pk +'" value="'+ need_pl + '"/>');
                });
                $.each(data.pcba_value, function (pcba_key, pcba_value) {
                    $('#cpo_pcba_result').append('<input type="hidden" name="'+ pcba_key +'" value="'+ pcba_value + '"/>');
                });
                // PCB 数据
                if(data.cpo_select_pcb){
                    $('.cpo_pcb_fee_box').css('display', 'block');
                    var pcb_price_list = data.cpo_price_list.pcb_fee.x_fee;
                    var pcb_value_list = data.cpo_price_list.pcb_fee.x_value;
                    $.each(data.pcb_value, function (pcb_key, pcb_value) {
                        if(pcb_key == 'pcb_special_requirements'){
                            $('#cpo_pcb_result .pcb_special_requirements').empty();
                            $.each(data.pcb_value.pcb_special_requirements, function (pcb_res_key, pcb_res_value) {
                                $('#cpo_pcb_result .pcb_special_requirements').append('<input type="hidden" name="'+ pcb_res_key +'" value="'+ pcb_res_value + '"/>');
                            })
                        }else if(pcb_key == 'pcb_surfaces'){
                            $('#cpo_pcb_result .pcb_surface').empty();
                            $.each(data.pcb_value.pcb_surfaces, function (pcb_sur_key, pcb_sur_value) {
                                $('#cpo_pcb_result .pcb_surface').append('<input type="hidden" name="'+ pcb_sur_key +'" value="'+ pcb_sur_value + '"/>');
                            })
                        }else{
                            $('#cpo_pcb_result').append('<input type="hidden" name="'+ pcb_key +'" value="'+ pcb_value + '"/>');
                        }
                    });

                    if(pcb_price_list){
                        $('.cpo_cost_fee input[name="all_fee"]').val(pcb_price_list['Total Cost']);
                        $('.cpo_pcb_all_fee .pcb_fee_ul').empty();
                        $.each(pcb_price_list, function (pcb_fee_key, pcb_fee_value) {
                            if(pcb_fee_key != 'Total Cost' && pcb_fee_key != 'Cost By' && pcb_fee_key != 'Surface Cost'){
                                if(pcb_fee_key == 'Cost By'){
                                    $('.cpo_pcb_all_fee .pcb_fee_ul').append('<li>\n'+
                                            '<span class="ul_span">Cost By ㎡</span>\n'+
                                            '<span class="ul_span_cost">\n'+
                                                '<i>$</i>\n'+
                                                '<input type="text" name="'+pcb_fee_key+'" value="'+pcb_fee_value+'" readonly="readonly"/>\n'+
                                            '</span></li>')
                                }else{
                                    $('.cpo_pcb_all_fee .pcb_fee_ul').append('<li>\n'+
                                                '<span class="ul_span">'+ pcb_fee_key +'</span>\n'+
                                                '<span class="ul_span_cost">\n'+
                                                    '<i>$</i>\n'+
                                                    '<input type="text" name="'+pcb_fee_key+'" value="'+pcb_fee_value+'" readonly="readonly"/>\n'+
                                                '</span></li>')
                                }
                            }
                        });
                    }
                    // PCB 需求
                    $('#cpo_pcb_result').append('<input type="hidden" name="cpo_select_pcb" value="'+ data.cpo_select_pcb + '"/>');
                    // 交期
                    var delivery_period = pcb_value_list.cpo_delivery;
                    if(delivery_period){
                        $('.cpo_delivery_period').css('display', 'block');
                        $('.cpo_cost_fee input[name="delivery_period"]').val(delivery_period);
                    }else{
                        $('.cpo_delivery_period').css('display', 'none');
                    }
                    pcbaSpecialCallBack(data.pcb_value.pcb_special_requirements);
                }else{
                    $('.cpo_pcb_fee_box').css('display', 'none');
                }
                if(cpo_price_list.freigth_fee <= 0){
                    var first_i = $('.cpo_pcba_freigth .cpo_cost_fee').children().first('i');
                    if(first_i.html() == '\n'){
                        first_i.remove();
                    }
                    $('.cpo_pcba_freigth .cpo_cost_fee').prepend('<i class="fa fa-info-circle" data-toggle="tooltip" data-placement="bottom"\n' +
                        'title="The current address cannot automatically calculate the shipping cost, and the final cost is settled"\n'+
                        'style="color: #2e8bc3;">\n' +
                        '</i>')
                }else{
                    var first_i = $('.cpo_pcba_freigth .cpo_cost_fee').children().first('i');
                    if(first_i.html() == '\n'){
                        first_i.remove();
                    }
                }
                $('.cpo_cost_fee input[name="cpo_freight"]').val(cpo_price_list.freigth_fee);

                // 国家
                $('#cpo_pcb_result').append('<input type="hidden" name="cpo_country" value="'+ data.cpo_country + '"/>');

                $('.cpo_cost_fee input[name="smt_assembly_cost"]').val(cpo_price_list.smt_assembly_fee);
                $('.cpo_cost_fee input[name="stencil_cost"]').val(cpo_price_list.stencil_fee);
                if(cpo_price_list.jig_tool_fee > 0){
                    $('.cpo_jig_cost_box').css('display', 'block');
                    $('.cpo_cost_fee input[name="jig_cost"]').val(cpo_price_list.jig_tool_fee);
                }else{
                    $('.cpo_jig_cost_box').css('display', 'none');
                }

                if(cpo_price_list.test_tool_fee){
                    $('.cpo_special_cost_box').css('display', 'block');
                    $('.cpo_cost_fee input[name="e_test"]').val(cpo_price_list.test_tool_fee);
                }else{
                    $('.cpo_special_cost_box').css('display', 'none');
                }
                $('.cpo_cost_fee input[name="cpo_pcba_quantity"]').val(data.pcba_value.cpo_quantity + ' PCS');
                $('.cpo_cost_fee input[name="total_cost"]').val(cpo_price_list.ele_tatol.toFixed(2));
                $('.pcba_calculation_results .calculation_content').addClass('cpo-block').removeClass('cpo-none');
            }
        }
    }
    // PCBA 特殊数据返回
    function pcbaSpecialCallBack(list) {
        $('.cpo_pcba_need_pcb form.special_form input[name="special_minimum_line"]').val(list.Min_line_width);
        $('.cpo_pcba_need_pcb form.special_form input[name="special_line_space"]').val(list.Min_line_space);
        $('.cpo_pcba_need_pcb form.special_form input[name="special_minimum_aperture"]').val(list.Min_aperture);
        $('.cpo_pcba_need_pcb form.special_form input[name="special_total_number"]').val(list.Total_holes);
        $('.cpo_pcba_need_pcb form.special_form input[name="special_copper_hall"]').val(list.Copper_weight_wall);
        $('.cpo_pcba_need_pcb form.special_form input[name="special_number_core"]').val(list.Number_core);
        $('.cpo_pcba_need_pcb form.special_form input[name="special_pp_number"]').val(list.PP_number);
        $('.cpo_pcba_need_pcb form.special_form input[name="special_total_test"]').val(list.Total_test_points);
        $('.cpo_pcba_need_pcb form.special_form input[name="special_blind_hole"]').val(list.Blind_and_buried_hole);
        $('.cpo_pcba_need_pcb form.special_form input[name="special_blind_struture"]').val(list.Blind_hole_structure);
        $('.cpo_pcba_need_pcb form.special_form input[name="special_countersunk"]').val(list.Countersunk_deep_holes);
        $('.cpo_pcba_need_pcb form.special_form input[name="special_inner_hole_line"]').val(list.Inner_hole_line);
    }
    // PCBA 阶梯价
    function cpoPCBAStairPrice(stair_price) {

        ajax.jsonRpc("/get_stair_price", 'call', {
            'pcba_value': stair_price.pcba_value,
            'cpo_select_pcb': stair_price.cpo_select_pcb,
            'cpo_country': stair_price.cpo_country,
            'cpo_express': stair_price.cpo_express,
            'pcb_value': stair_price.pcb_value,
        }).then(function (data) {
            if(data){
                if(data.warning){
                    webAlert(data.warning, null, false);
                    // alert(data.warning)
                }else{
                    $('.pcba_try_quantity .cpo_quantity_content').empty();
                    if(data.price_list.length){
                        $('.pcba_try_quantity').addClass('cpo-block').removeClass('cpo-none');
                        $.each(data.price_list, function (price_key, price_val) {
                            if(price_key == 0){
                                $.each(price_val, function (key_p, key_l) {
                                    if(key_l != ''){
                                        $('.pcba_try_quantity .cpo_quantity_content').append('\n'+
                                            '<div class="cpo_quantiry_line cpo_quantity_select">\n' +
                                            '<div class="cpo_try_icon cpo_try_select_icon"></div>\n' +
                                            '<p class="cpo_try_quantity">\n' +
                                            '<span>'+key_p+'</span>\n' +
                                            '<span>$ '+ key_l.toFixed(2) +' </span>\n' +
                                            '</p>\n' +
                                            '</div>');
                                    }
                                })
                            }else{
                                $.each(price_val, function (key_p, key_l) {
                                    if(key_l != ''){
                                        $('.pcba_try_quantity .cpo_quantity_content').append('\n'+
                                            '<div class="cpo_quantiry_line">\n' +
                                            '<div class="cpo_try_icon"></div>\n' +
                                            '<p class="cpo_try_quantity">\n' +
                                            '<span>'+key_p+'</span>\n' +
                                            '<span>$ '+ key_l.toFixed(2) +' </span>\n' +
                                            '</p>\n' +
                                            '</div>');
                                    }
                                })
                            }
                        })
                    }else{
                        $('.pcba_try_quantity').addClass('cpo-none').removeClass('cpo-block');
                    }
                }
            }
        })
    }
    // 点击Try PCBA 数量
    $('.pcba_try_quantity .cpo_quantity_content').on('click', '.cpo_quantiry_line', function () {
        $(this).find('div').addClass('cpo_try_select_icon');
        $(this).siblings().find('div').removeClass('cpo_try_select_icon');
        $(this).addClass('cpo_quantity_select').siblings().removeClass('cpo_quantity_select');

        var cpo_country = $('.pcba_calculation_results .cpo_country_list select').val();
        var cpo_express = $('.pcba_calculation_results .cpo_order_express_message select').val();
        var cpo_source = $('.cpo_source_cp input[name="cpo_source"]').val();
        var cpo_select_pcb = false;
        var pcba_value = pcbaGetForm(); // PCBA Value
        var pcb_value = null; // PCB Value
        if(pcba_value.cpo_pcb_supply == 'chinapcbone'){
            pcb_value = pcbaGetPCBFormData();
            cpo_select_pcb = true;
        }

        var cpo_area = (pcba_value.cpo_width * pcba_value.cpo_length) * pcba_value.cpo_quantity / (Math.pow(10,6))
        if(cpo_select_pcb){
            if(cpo_area >= 10){
                webAlert('The total area cannot exceed 10 ㎡ !', null, false);
                // alert('The total area cannot exceed 10 ㎡ !')
                return false;
            }
        }
        if($(this).find('div').hasClass('cpo_try_select_icon')){
           var this_val = $(this).find('span:first').html();
           ajax.jsonRpc("/get_try_qty", 'call', {
               'pcba_value': pcba_value,
               'cpo_select_pcb': cpo_select_pcb,
               'cpo_country': cpo_country,
               'cpo_express': cpo_express,
               'pcb_value': pcb_value,
               'select_qty': this_val,
               'cpo_source': cpo_source,
           }).then(function (data) {
                pcbaReturnResultData(data);
                $('#pcba_data_quotation input[name="cpo_input_quantity"]').val(data.pcba_value.cpo_quantity);
                if(cpo_select_pcb){
                    $('.cpo_pcba_need_pcb .cpo_pcb_quotation input[name="pcb_quantity"]').val(data.pcba_value.cpo_quantity)
                }
           })
        }
    })
    // 检查数据，如果有没填写的，给出提示
    function checkPCBAData(){
        var flag = true;
        var $pcba_data_input = $('#pcba_data_quotation input[type="text"]');
        $pcba_data_input.each(function () {
            if(!$(this).val()){
                $(this).css('border', '1px solid red');
                $(this).focus();
                flag = false;
                return flag;
            }else{
                $(this).css('border', '1px solid #dddddd');
            }
        });
        return flag;
    }

//---PCBA 报价 End Version-0.3 --------------------------------------------------------------------------------------------------------------

//---报价记录------------------------------------------------------------------------------------------------------------------------------
    function cpoQuotationRecord(record_data, datas, file_data, order_name){
         ajax.jsonRpc('/set_quotation_reacord', 'call',{
            'data': datas,
            'order_name': order_name,
            'file_data': file_data,
            'record_data': record_data,
        }).then(function (data) {
            var record = data;
            return record;
        });
    }
    function ajaxCpoQuotationRecord(record_data, datas, file_data, order_name) {
        ajax.jsonRpc('/set_quotation_reacord', 'call',{
            'data': datas,
            'order_name': order_name,
            'file_data': file_data,
            'record_data': record_data,
        }).then(function (data) {
            var record = data;
            return record;
        });
    }
//------------------------------------------

//----PCBA 打包价 Begin----------------------------------------------------------------------------------------------------------------------
    //PCBA 打包价 form
    function pcbaPackagePriceForm(){
        var pcba_package_qty = $('#pcba_package_data_quotation input[name="cpo_input_quantity"]').val();
        var pcba_package_width = $('#pcba_package_data_quotation input[name="cpo_input_width"]').val();
        var pcba_package_length = $('#pcba_package_data_quotation input[name="cpo_input_lenght"]').val();
        var pcba_package_dip = $('#pcba_package_data_quotation input[name="cpo_input_dip"]').val();
        var pcba_material_type = $('#pcba_package_data_quotation input[name="cpo_material_type"]').val();
        var pcba_package_smt = $('#pcba_package_data_quotation input[name="cpo_input_smt"]').val();
        var pcba_package_smt_side = $('#pcba_package_data_quotation .pcba_smt_side').val();
        var pcba_package_thick = $('#pcba_package_data_quotation input[name="cpo_input_thick"]').val();
        var pcba_package_surface = $('#pcba_package_data_quotation .surface_value').val();
        // var pcba_package_included = $('#pcba_package_data_quotation .pcba_package_included').val();

        var pcba_package_dict = {
            'pcba_package_qty': pcba_package_qty,
            'pcba_package_width': pcba_package_width,
            'pcba_package_length': pcba_package_length,
            'pcba_package_dip': pcba_package_dip,
            'pcba_material_type': pcba_material_type,
            'pcba_package_smt': pcba_package_smt,
            'pcba_package_smt_side': pcba_package_smt_side,
            'pcba_package_thick': pcba_package_thick,
            'pcba_package_surface': pcba_package_surface,
            'pcba_package_included': ''
        };
        return pcba_package_dict;
    }
    // 不含物料
    $('.pcba_nomaterial_package_calculation_results .cpo_calculation').on('click', function () {
        var package_form = pcbaPackagePriceForm();
        package_form.pcba_package_included = 'no';
        ajax.jsonRpc('/pcba-package-price', 'call', {
            'package_form': package_form
        }).then(function (data) {
            // 报价记录
            var order_name = 'PCBA Package Price';
            setQuotationData(data, order_name);
            if(data){
                if(data.warning){
                    var waring_str = '';
                    var waring_num = 1;
                    $.each(data.warning, function (war_key, war_value) {
                        waring_str = showWarning(war_key, war_value, waring_str, waring_num);
                    });
                    if(waring_str){
                        webAlert(waring_str, null, false);
                        // alert(waring_str);
                    }
                    $('#step_next').css('display','none');
                    $('.calculation_content').addClass('cpo-none').removeClass('cpo-block');
                }else if(data.login){
                    getLoginData(data);
                }else {
                    $('.cpo-warning').html('');
                    // var order_name = 'PCBA Package Price';
                    // setQuotationData(data, order_name);
                    var form_data = data.package_form;
                    var data_box = $('#cpo_pcba_result');
                    data_box.empty();
                    $('.pcba_nomaterial_package_calculation_results #step_next').css('display', 'block');
                    $('.pcba_nomaterial_package_calculation_results .calculation_content').addClass('cpo-block').removeClass('cpo-none');
                    $('#cpo_pcba_package_no_material .cpo_pcba_quantity').val(form_data.pcba_package_qty + ' PCS');
                    $('#cpo_pcba_package_no_material .cpo_quantity').val(form_data.pcba_package_qty);
                    $('#cpo_pcba_package_no_material .total_cost').val(data.pcba_package['Total Price']);
                    $.each(form_data, function (pk_key, pk_val) {
                        var $doc_input = '<input type="hidden" name="' + pk_key + '" value="' + pk_val + '" class="' + pk_key + '"/>';
                        data_box.append($doc_input);
                    });
                    $('.calculation_content').addClass('cpo-block').removeClass('cpo-none');
                }
            }
        });
    });
    // 含物料
    $('.pcba_material_package_calculation_results .cpo_calculation').on('click', function () {
        var package_form = pcbaPackagePriceForm();
        package_form.pcba_package_included = 'yes';
        ajax.jsonRpc('/pcba-package-price', 'call', {
            'package_form': package_form
        }).then(function (data) {
            // 报价记录
            var order_name = 'PCBA Package Price';
            setQuotationData(data, order_name);
            if(data.warning){
                var waring_str = '';
                var waring_num = 1;
                $.each(data.warning, function (war_key, war_value) {
                    waring_str = showWarning(war_key, war_value, waring_str, waring_num);
                });
                if(waring_str){
                    webAlert(waring_str, null, false);
                    // alert(waring_str);
                }
                $('#step_next').css('display','none');
                $('.calculation_content').addClass('cpo-none').removeClass('cpo-block');
            }else if(data.login){
                getLoginData(data);
            }else {
                // // 报价记录
                // var order_name = 'PCBA Package Price';
                // setQuotationData(data, order_name);
                var form_data = data.package_form;
                var data_box = $('#cpo_pcba_result');
                data_box.empty();
                $('.pcba_material_package_calculation_results #step_next').css('display', 'block');
                $('.pcba_material_package_calculation_results .calculation_content').addClass('cpo-block').removeClass('cpo-none');
                $('#cpo_pcba_package_material .cpo_pcba_quantity').val(form_data.pcba_package_qty + ' PCS');
                $('#cpo_pcba_package_material .cpo_quantity').val(form_data.pcba_package_qty);
                $('#cpo_pcba_package_material .total_cost').val(data.pcba_package['Total Price']);
                $.each(form_data, function (pk_key, pk_val) {
                    var $doc_input = '<input type="hidden" name="' + pk_key + '" value="' + pk_val + '" class="' + pk_key + '"/>';
                    data_box.append($doc_input);
                });
            }
        });
    });
    // 自动触发检查数据
    $('#cpo_pcba_online_content input[type="text"]').on('change', function () {
        checkPCBApackprice();
    })
    function checkPCBApackprice(){
        var material_pack = $('.pcba_material_package_calculation_results');
        var nomaterial_pack = $('.pcba_nomaterial_package_calculation_results');
        var form_data = pcbaPackagePriceForm();
        // var pcba = $('.pcba_calculation_results');
        var warnning = $('.cpo-warning');
        var smt_dip_total = parseInt(form_data.pcba_package_dip)+parseInt(form_data.pcba_package_smt);
        var setVal = null;
        if(nomaterial_pack.length > 0){
            if(parseInt(form_data.pcba_package_qty) > 20){
                setVal = "The number cannot exceed 20pcs";
            }else if(parseFloat(form_data.pcba_package_width) > 100.00){
                setVal = "Dimensions, length and width should not exceed 100mm";
            }else if(parseFloat(form_data.pcba_package_length) > 100.00){
                setVal = "Dimensions, length and width should not exceed 100mm";
            }else if(parseInt(smt_dip_total) > 50){
                setVal = "The total number of DIP and SMT cannot exceed 50";
            }
        }else if(material_pack.length > 0){
            if(parseInt(form_data.pcba_package_qty) > 5){
                setVal = "The number cannot exceed 5pcs";
            }else if(parseFloat(form_data.pcba_package_width) > 100.00){
                setVal = "Dimensions, length and width should not exceed 100mm";
            }else if(parseFloat(form_data.pcba_package_length) > 100.00){
                setVal = "Dimensions, length and width should not exceed 100mm";
            }else if(parseInt(form_data.pcba_package_smt) > 50){
                setVal = "The total number of SMT cannot exceed 50";
            }
        }else{

        }
        var w_con = '<div class="alert alert-warning">\n' +
            '<a href="#" class="close" data-dismiss="alert">\n' +
            '<i class="fa fa-close"></i></a><strong>Prompt : </strong>'+setVal+'\n' +
            '<a></a>'+'\n' +
            '</div>';
        if(setVal == null){
            warnning.html('');
        }else{
            warnning.html(w_con);
            $('body,html').animate({scrollTop: 150}, 500);
        }
    }

//----PCBA 打包价 End----------------------------------------------------------------------------------------------------------------------

    //

    //点击选择Try quantity
    $('.cpo_try_order_quantity .cpo_quantiry_line').on('click', function () {
        $(this).find('div').removeClass('cpo_try_icon').addClass('cpo_try_select_icon');
        $(this).siblings().find('div').removeClass('cpo_try_select_icon').addClass('cpo_try_icon');
        $(this).addClass('cpo_quantity_select').siblings().removeClass('cpo_quantity_select');
    });

    // PCB 特殊数据 按钮
    var special_click = $('#pcb_need');
    special_click.on('click', function () {
        var special_i = $(this).find('i');
        if(special_i.hasClass('pcb_need_btn_plus')){
            special_i.removeClass('pcb_need_btn_plus').addClass('pcb_need_btn_less');
            $('.cpo_pcb_special').toggle();
        }else{
            special_i.addClass('pcb_need_btn_plus').removeClass('pcb_need_btn_less');
            $('.cpo_pcb_special').toggle();
        }
        pcbSpecialForm();
    });

    // PCBA 价格明细
    // $('.pcba_order_fee').mouseover(function () {
    //     var $all_fee1 = $(this).find('div.cpo_pcba_all_fee');
    //     var $height = '-'+$all_fee1.height()+'px';
    //     $all_fee1.css({'display': 'block', 'top': $height});
    // }).mouseout(function () {
    //     var $all_fee2 = $(this).find('div.cpo_pcba_all_fee');
    //     var $height2 = '-'+$all_fee2.height()+'px';
    //     $all_fee2.css({'display': 'none', 'top': $height2});
    // });
    // PCB 价格明细
    // $('.board_price').mouseover(function () {
    //     $('.cpo_pcb_all_fee').css('display', 'block');
    // }).mouseout(function () {
    //     $('.cpo_pcb_all_fee').css('display', 'none');
    // });
    // PCB 价格移动
    // $('.cpo_pcb_all_fee').on("mouseover mouseout",'ul.pcb_fee_ul li',function(event){
    //     if(event.type == "mouseover"){
    //         $(this).css('background-color', '#cccccc');
    //         $(this).find('input').css('background-color', '#cccccc');
    //     }else if(event.type == "mouseout"){
    //         $(this).css('background-color', '#FFFFFF');
    //         $(this).find('input').css('background-color', '#FFFFFF');
    //     }
    // })
    // $('.cpo_pcb_all_fee').on("click",'ul.pcb_fee_ul li',function(event){
    //     $('.cpo_pcb_all_fee').css('display', 'none');
    // })

    // 必须选择国家才能报价，检查是否选择国家
    function checkCountry() {
        // var cpo_pcba_need_pcb = $('.cpo_pcba_need_pcb');
        var stencil = $('#cpo_stencil_online_content');
        var country_val = $('.cpo_country_list .country_select').val();
        if(country_val == ""){
            webAlert('Please select a country !', null, false);
            // alert('Please select a country !');
            return false;
        }else{
            return true;
        }
    }

    // 自动触发计算cpo_pcba_online_content
    $('.cpo_col_pcba_md8 a').click(function () {
        // cpoPCBACalculation();
        $('#step_next').css('display', 'none');
        $('.calculation_content>div.cpo_cost_fee').addClass('cpo-none').removeClass('cpo-block');
    });
    $('.cpo_col_pcba_md8 input[type="text"]').change(function () {
        // cpoPCBACalculation();
        getAreaBoard();
        $('#step_next').css('display', 'none');
        $('.calculation_content>div.cpo_cost_fee').addClass('cpo-none').removeClass('cpo-block');
    });
    $('.cpo_col_pcba_md8 input[type="text"]').blur(function () {
        // cpoPCBACalculation();
        $('#step_next').css('display', 'none');
        $('.calculation_content>div.cpo_cost_fee').addClass('cpo-none').removeClass('cpo-block');
    });
    $('.cpo_col_pcba_md8 select').change(function () {
        // cpoPCBACalculation();
        $('#step_next').css('display', 'none');
        $('.calculation_content>div.cpo_cost_fee').addClass('cpo-none').removeClass('cpo-block');
    });

    // 打包价PCB 特殊数据获取

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


    // PCB 层数影响铜厚
    $('.cpo_select_layers').on('change', function () {
        var hdi_page = $('.cpo_hdi_quotation');
        var layer = $(this).val();
        if(layer >= 4){
            $('.cpo_inner_copper_weight a').each(function () {
                $(this).addClass('cpo_input_active');
            });
        }else{
            $('.cpo_inner_copper_weight .inner_copper_weight').removeClass('cpo_input_active');
        }
        // hdi 判断
        if(hdi_page.length > 0){
            hdi_page.addClass('cpo-block').removeClass('cpo-none');
        }else{
            hdi_page.addClass('cpo-none').removeClass('cpo-block');
        }

    });


//----打包价 开始-------------------------------------------------------------------------------------------------------
    function checkPCBPriceCustomerData() {
        var showVal;
        var form_data;
        form_data = pcbpackage_form();
        var pcb_special = form_data.pcb_special_requirements;
        var pack_price_area = parseFloat(form_data.cpo_quantity) * (parseFloat(form_data.pcb_breadth) * 0.001) * (parseFloat(form_data.pcb_length) * 0.001) ;
        var warnning = $('.cpo-warning');
        if(parseFloat(form_data.pcb_length) > 100.00){
            showVal = 'Length must be ≤100mm !';
        }else if(parseFloat(form_data.pcb_breadth) > 100.00){
            showVal = 'Width must be ≤100mm !';
        }else if(pack_price_area > 1){
            showVal = 'Area must be ≤ 1㎡ !';
        }else if(pcb_special.Laser_drilling == 'Yes'){
            showVal =  'Laser drilling is unable to quote automatically , if you are interested, please turn to personal support.';
        }else if(pcb_special.Depth_control_routing == 'Yes'){
            showVal = 'Depth milling unable to quote automatically , if you are interested, please turn to personal support.';
        }else if(pcb_special.The_space_for_drop_V_cut == 'Yes'){
            showVal = 'Jumping v-cut is unable to quote automatically , if you are interested, please turn to personal support.';
        }else if(pcb_special.Number_back_drilling == 'Yes'){
            showVal = "Back drilling is unable to quote automatically , if you are interested, please turn to personal support.";
        }else if(!pcb_special.Countersunk_deep_holes){
            showVal = 'Countersunk/depth control hole is unable to quote automatically , if you are interested, please turn to personal support.';
        }else if(!pcb_special.Blind_hole_structure){
            showVal = "Blind&Buried via is unable to quote automatically , if you are interested, please turn to personal support.";
        }else if(!pcb_special.Blind_and_buried_hole){
            showVal = "Blind&Buried via is unable to quote automatically , if you are interested, please turn to personal support.";
        }else{
            showVal = null;
        }
        var w_con = '<div class="alert alert-warning">\n' +
            '<a href="#" class="close" data-dismiss="alert">\n' +
            '<i class="fa fa-close"></i></a><strong>Prompt : </strong>'+showVal+'\n' +
            '<a></a>'+'\n' +
            '</div>';
        if(showVal == null){
            warnning.html('');
        }else{
            warnning.html(w_con);
            $('body,html').animate({scrollTop: 150}, 500);
        }
    }

    function getAreaBoard(){
        var area, pcb_quantity,pcb_length,pcb_breadth;
        var pcba_need_pcb = $('.cpo_pcba_need_pcb');
        if(pcba_need_pcb.length > 0){
            pcb_quantity = $('.cpo_pcba_need_pcb input[name="pcb_quantity"]').val();
            pcb_length = $('.cpo_pcba_need_pcb input[name="pcb_length"]').val();
            pcb_breadth = $('.cpo_pcba_need_pcb input[name="pcb_breadth"]').val();
        }else{
            pcb_quantity = $('.quo-active input[name="pcb_quantity"]').val();
            pcb_length = $('.quo-active input[name="pcb_length"]').val();
            pcb_breadth = $('.quo-active input[name="pcb_breadth"]').val();
        }
        area = parseFloat(pcb_length) * parseFloat(pcb_breadth) * parseFloat(pcb_quantity) / 1000000;
        if(area >= 3){
            if(pcba_need_pcb.length > 0){
                $('.cpo_pcba_need_pcb .cpo_e_test').val('E-test fixture');
            }else{
                $('.quo-active .cpo_e_test').val('E-test fixture')
            }
        }else{
            if(pcba_need_pcb.length > 0){
                $('.cpo_pcba_need_pcb .cpo_e_test').val('Free Flying Probe');
            }
            $('.quo-active .cpo_e_test').val('Free Flying Probe');
        }
    }

    function eTestCheckData(showVal) {
        var warnning = $('.cpo-warning');
        var w_con = '<div class="alert alert-warning">\n' +
            '<a href="#" class="close" data-dismiss="alert">\n' +
            '<i class="fa fa-close"></i></a><strong>Prompt : </strong>Area of 3 square meters or more, E-test fixture must be used\n' +
            '<a></a>'+'\n' +
            '</div>';
        if(showVal == 'Free Flying Probe'){
            warnning.html('');
        }else{
            warnning.html(w_con);
            $('body,html').animate({scrollTop: 150}, 500);
        }
    }

    // PCB package form取值
    var pcbpackage_form = function() {
        var pcb_value_dict;
        var pcb_qty_unit;
        var pcb_pcs_size = '';
        var pcb_item_size = '';

        var quality_standard = $('.cpo_pcbpackage_quotation .quality_standard').val();
        var pcb_quantity = $('.cpo_pcbpackage_quotation input[name="pcb_quantity"]').val();
        var pcb_length = $('.cpo_pcbpackage_quotation input[name="pcb_length"]').val();
        var pcb_breadth = $('.cpo_pcbpackage_quotation input[name="pcb_breadth"]').val();
        var cpo_layers = $('.cpo_pcbpackage_quotation .cpo_layers').val();
        var cpo_raw_material = $('.cpo_pcbpackage_quotation .cpo_raw_material').val();
        var cpo_thickness = $('.cpo_pcbpackage_quotation input[name="cpo_thickness"]').val();
        var cpo_inner_copper = $('.cpo_pcbpackage_quotation .inner_copper').val();
        var cpo_outer_copper = $('.cpo_pcbpackage_quotation .outer_copper').val();
        var cpo_mask_color = $('.cpo_pcbpackage_quotation .cpo_mask_color').val();
        var cpo_silkscreen_color = $('.cpo_pcbpackage_quotation .cpo_silkscreen_color').val();
        var surface_value = $('.cpo_pcbpackage_quotation .surface_value').val();
        //表面处理值
        var cpo_surface_treatment = {
            surface_value: surface_value
        };
        var cpo_vias = $('.cpo_pcbpackage_quotation .cpo_vias').val();
        var cpo_e_test = $('.cpo_pcbpackage_quotation .cpo_e_test').val();
        var pcb_special_requirements = pcbPackageSpecialForm();
        pcb_value_dict = {
            'quality_standard': quality_standard,
            'cpo_quantity': pcb_quantity,
            'pcb_qty_unit': "PCS",
            'pcb_length': pcb_length,
            'pcb_breadth': pcb_breadth,
            // 'pcb_pcs_size':pcb_pcs_size,
            // 'pcb_item_size':pcb_item_size,
            'pcb_layer': cpo_layers,
            'pcb_type': cpo_raw_material,
            'pcb_thickness': cpo_thickness,
            'pcb_inner_copper': cpo_inner_copper,
            'pcb_outer_copper': cpo_outer_copper,
            'pcb_solder_mask': cpo_mask_color,
            'pcb_silkscreen_color': cpo_silkscreen_color,
            'pcb_surfaces': cpo_surface_treatment,
            'pcb_vias': cpo_vias,
            'pcb_test': cpo_e_test,
            'pcb_special_requirements': pcb_special_requirements,

        }
        return pcb_value_dict
    }
    function pcbPackageSpecialForm(){
        var pcb_special_value;
        var Semi_hole = $('form.special_form select.special_semi_hole').val();
        var Edge_plating = $('form.special_form select.special_edge_plating').val();
        var Impedance = $('form.special_form select.special_impedance').val();
        var Press_fit = $('form.special_form select.special_press_fit').val();
        var Peelable_mask = $('form.special_form select.special_peelable_mask').val();
        var Carbon_oil = $('form.special_form select.pcb_carbon_ink').val();
        var Min_line_width = $('form.special_form input.min_line_width').val();
        var Min_line_space = $('form.special_form input.special_line_space').val();
        var Min_aperture = $('form.special_form input.special_minimum_aperture').val();
        var Total_holes = $('form.special_form input.special_total_number').val();
        var Copper_weight_wall = $('form.special_form input.special_copper_hall').val();
        var Number_core = $('form.special_form input.special_number_core').val();
        var PP_number = $('form.special_form input.special_pp_number').val();
        // var Acceptable_stanadard = $('form.special_form select.special_acceptable').val();
        var Total_test_points = $('form.special_form input.special_total_test').val();
        var Blind_and_buried_hole = $('form.special_form .blind_and_buried_hole').val();
        var Blind_hole_structure = $('form.special_form .blind_hole_structure').val();
        var Depth_control_routing = $('form.special_form select.special_depth_control').val();
        var Number_back_drilling = $('form.special_form select.special_back_drilling').val();
        var Countersunk_deep_holes = $('form.special_form .countersunk_deep_holes').val();
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
    // 打包价数据传递
    function cpoPCBPackageCalculation(){
        var cpo_country = $('.cpo_country_list select').val();
        var cpo_express = $('.cpo_order_express_message select').val();
        var cpo_source = $('.cpo_source_cp input[name="cpo_source"]').val();
        var check_pcb_input = checkPCBPackage(); //检测是否输入数据
        if(!check_pcb_input){
            return false;
        }
        var pcb_from = pcbpackage_form();
        var pcb_special_requirements = pcbPackageSpecialForm();
        // var stair_price = {
        //     'pcb_value': pcb_from,
        //     'cpo_country': cpo_country,
        //     'cpo_express': cpo_express,
        //     'pcb_special_requirements': pcb_special_requirements,
        // }
        $('#step_next').css('display', 'inline-block');
        ajax.jsonRpc("/cpo_pcbpackage_quotation", 'call', {
            'cpo_source': cpo_source,
            'pcb_value': pcb_from,
            'cpo_country': cpo_country,
            'cpo_express': cpo_express,
            'pcb_special_requirements': pcb_special_requirements,
        }).then(function (data) {
            pcbPackageAllData(data);
        });
    }
    // 点击打包价报价计算
    var pcb_click = $('.pcbpackage_calculation_results .cpo_calculation');
    pcb_click.on('click', function () {
        // var country_val = checkCountry();
        // if(!country_val){
        //     return false;
        // }
        cpoPCBPackageCalculation();
    });
    // 打包价数据渲染
    function pcbPackageAllData(data){
        var order_name = 'PCB Package';
        setQuotationData(data, order_name)
        if(data.error){
            var waring_str = '';
            var waring_num = 1;
            // $.each(data.error, function (war_key, war_value) {
            //     // if(war_value != null){
            //     //     waring_str += waring_num +' : '+ war_value + '\n';
            //     //     waring_num++;
            //     // }
            $.each(data.error, function (war_key, war_value) {
                waring_str = showWarning(war_key, war_value, waring_str, waring_num)

            });
            if(waring_str){
                webAlert(waring_str, null, false);
                // alert(waring_str);
            }
            // });
            $('#step_next').css('display','none');
        }else if(data.login){
            getLoginData(data);
        }
        else {
            $('.cpo-warning').empty();
            // var order_name = 'PCB Package';
            // setQuotationData(data, order_name)
            $('.pcbpackage_calculation_results .calculation_content').addClass('cpo-block').removeClass('cpo-none');
            var back_return = data.pcb_package.value;
            var return_special = data.pcb_package.value.pcb_special;
            pcbSpecialCallBack(return_special);
            var enter_data = data.pcb_value;
            var pcb_result = $('.pcbpackage_calculation_results .pcb_result') // PCB 数据
            var pcb_surface = $('.pcbpackage_calculation_results .pcb_surface') // 表面处理 数据
            var pcb_special_requirements = $('.pcbpackage_calculation_results .pcb_special_requirements') // 特殊 数据
            $('.pcbpackage_calculation_results input[name="cpo_pcb_quantity"]').val(enter_data.cpo_quantity+" "+enter_data.pcb_qty_unit);
            $('.pcbpackage_calculation_results input[name="cpo_pcb_package"]').val(data.package);
            $('.pcbpackage_calculation_results input[name="cpo_flat_area"]').val(back_return['PCB Area']+' m²');
            $('.pcbpackage_calculation_results input[name="cpo_delivery"]').val(back_return['Delivery Period']);
            $('.pcbpackage_calculation_results input[name="cpo_freight"]').val(data.pcb_package['Shipping Cost']);
            $('.pcbpackage_calculation_results input[name="cpo_package_cost"]').val(back_return['Package Cost']);
            $('.pcbpackage_calculation_results input[name="all_fee"]').val(back_return['Total Cost']);

            pcb_result.empty();
            pcb_surface.empty();
            pcb_special_requirements.empty();
            $.each(enter_data, function (key, val) {
                if (key == 'pcb_special_requirements' || key == 'pcb_surfaces') {
                    if (key == 'pcb_special_requirements') {
                        $.each(data.pcb_special_requirements, function (sp_key, sp_val) {
                            var $sp_tag = '<input type="hidden" name="' + sp_key + '" value="' + sp_val + '">';
                            pcb_special_requirements.append($sp_tag);
                        });
                    } else {
                        $.each(enter_data.pcb_surfaces, function (ps_key, ps_val) {
                            var $ps_tag = '<input type="hidden" name="' + ps_key + '" value="' + ps_val + '">';
                            pcb_surface.append($ps_tag);
                        });
                    }
                } else {
                    var $tag = '<input type="hidden" name="' + key + '" value="' + val + '">';
                    pcb_result.append($tag);
                }
            })
        }
    }
//---打包价 结束----------------------------------------------------------------------------

    // 钢网计算
    var stencil_calculation = $('.stencil_calculation_results .cpo_calculation');
    var stencil_confrim = $('#cpo_stencil_result #step_next');
    stencil_calculation.click(function () {
        // var country_val = checkCountry();
        // if(!country_val){
        //     return false;
        // }
        cpoStencilData();
    });
    // 钢网数据传递和渲染
    function cpoStencilData() {
        if(!checkStencilData()){
            return false;
        }
        var country = checkCountry();
        if(!country){
            return false;
        }
        stencil_confrim.css('display', 'block')
        var cpo_country = $('.cpo_country_list select').val();
        var cpo_express = $('.cpo_order_express_message select').val();
        var cpo_source = $('.cpo_source_cp input[name="cpo_source"]').val();
        var stencil_data = stencilDate();
        ajax.jsonRpc('/stencil_order', 'call',{
            'cpo_source': cpo_source,
            'stencil_data': stencil_data,
            'cpo_country': cpo_country,
            'cpo_express': cpo_express,
        }).then(function (data) {
            if(data){
                if(data.error){
                    webAlert(data.error, null, false);
                    // alert(data.error)
                }else{
                    $('.order_page_ad').addClass('cpo-none');
                    var stencil_return = data.stencil_value;
                    $('.stencil_calculation_results .cpo_delivery').val(stencil_return['Stencil Delivery']+' Days');
                    $('.stencil_calculation_results .stencil_freigth').val(stencil_return['Stencil Freight']);
                    $('.stencil_calculation_results .stencil_cost').val(stencil_return['Stencil Cost']);
                    $('.stencil_calculation_results .total_cost').val(stencil_return['Stencil Total']);
                    $('#cpo_stencil_other .cpo_country').val(data.cpo_country);
                    $('#cpo_stencil_other .cpo_express').val(data.cpo_express);
                    $('#cpo_stencil_other .stencil_special').val(data.stencil_data.stencil_special);
                    $('#cpo_stencil_result').empty();
                    $.each(data.stencil_data, function (st_key, st_val) {
                        $('#cpo_stencil_result').append('<input type="hidden" class="cpo_express" name="'+st_key+'" value="'+ st_val +'"  readonly="readonly"/>');
                    })
                    $('#step_next').css('display', 'block');
                    $('.stencil_calculation_results .stencil_content_cost').addClass('cpo-block').removeClass('cpo-none');
                }
            }else{
                webAlert('A small accident has occurred, please refresh and try again !', null, false);
                // alert('A small accident has occurred, please refresh and try again !')
            }
        });
    }
    function checkStencilData() {
        var stencil_vale = $('#submit_stencil_quotation input[name="cpo_stencil_quantity"]');
        var flag = true;
        if(stencil_vale.val() == ''){
            stencil_vale.focus();
            stencil_vale.css('border', '1px solid #FF0000')
            flag = false;
        }else{
            stencil_vale.css('border', '1px solid #ccc')
            flag = true;
        }
        return flag;
    }
    // 钢网数据
    function stencilDate(){
        var stencil_qty = $('#submit_stencil_quotation input[name="cpo_stencil_quantity"]').val();
        // var stencil_type = $('#submit_stencil_quotation .cpo_stencil_type a.cpo_input_active').children('span').html();
        var stencil_size = $('#submit_stencil_quotation .cpo_stencil_size').val();
        // var stencil_side = $('#submit_stencil_quotation .cpo_stencil_side a.cpo_input_active').children('span').html();
        var stencil_thickness = $('#submit_stencil_quotation .cpo_stencil_thickness').val();
        // var stencil_existing = $('#submit_stencil_quotation .cpo_stencil_existing a.cpo_input_active').children('span').html();
        // var stencil_electropo = $('#submit_stencil_quotation .cpo_stencil_Electropo a.cpo_input_active').children('span').html();
        var stencil_special = $('#submit_stencil_quotation .cpo_stencil_special .stencil_special_re').val();

        var stencil_dict = {
            'stencil_qty': stencil_qty,
            // 'stencil_type': stencil_type,
            'stencil_size': stencil_size,
            // 'stencil_side': stencil_side,
            'stencil_thickness': stencil_thickness,
            // 'stencil_existing': stencil_existing,
            // 'stencil_electropo': stencil_electropo,
            'stencil_special': stencil_special,
        }

        return stencil_dict
    }

    // 右侧价格显示，菜单固定
    $(function(){
        var calculaH = $("#cpo_calcula_title");
        if(calculaH.length > 0){ //判断当前元素是否存在（避免下面代码报错）
            var cpoCalculaH = calculaH.offset().top; //获取要定位元素距离浏览器顶部的距离
            //滚动条事件
            var window_height = $(window).height();
            if(window_height > 740){
                $(window).scroll(function(){
                    var scroH = $(this).scrollTop(); //获取滚动条的滑动距离
                    //滚动条的滑动距离大于等于定位元素距离浏览器顶部的距离，就固定，反之就不固定
                    if(scroH>cpoCalculaH){
                        calculaH.addClass('cpo_calcula_title');
                    }else{
                        calculaH.removeClass('cpo_calcula_title');
                    }
                })
            }
        }

    })
    // 确认页面PCB信息隐藏显示
    $('.show_pcb_info').on('click', function () {
        if($('.show_pcb_info a').hasClass('cpo-plus')){
            $('.show_pcb_info a').removeClass('cpo-plus').addClass('cpo-less');
        }else{
            $('.show_pcb_info a').addClass('cpo-plus').removeClass('cpo-less');
        }
        $('.pcb_information_content').toggle();
    })
    $('.show_pcb_special').on('click', function () {
        if($('.show_pcb_special a').hasClass('cpo-plus')){
            $('.show_pcb_special a').removeClass('cpo-plus').addClass('cpo-less');
        }else{
            $('.show_pcb_special a').addClass('cpo-plus').removeClass('cpo-less');
        }
        $('.pcb_special_request_content').toggle();
    })
    // PCB price 确认数据页面
    // $('.cpo_pcb_fee_line').mouseover(function () {
    //     $('.pcb_other_fee').addClass('cpo-block').removeClass('cpo-none');
    // }).mouseout(function () {
    //     $('.pcb_other_fee').addClass('cpo-none').removeClass('cpo-block');
    // });
    // 检查PCBA数据输入
    // function checkPCBAInput() {
    //     var pcba_flag = true;
    //     $('#cpo_pcba_online_content input[type="text"]').each(function () {
    //         if($(this).val() == ''){
    //             $(this).addClass('cpo-border-red');
    //             $(this).focus();
    //             pcba_flag = false;
    //             return pcba_flag;
    //         }else{
    //             $(this).removeClass('cpo-border-red');
    //         }
    //     });
    //     return pcba_flag
    // }
    // 不拼版、非金手指等为空数据
    // function emptyData() {
    //     var pcs_set = $('.cpo_pcb_online_all_need .set_contetn');
    //     var finger_res = $('.cpo_gold_finger_request');
    //     if(pcs_set.css('display') == 'none'){
    //         pcs_set.find('input').val('');
    //     }
    //     if(finger_res.css('display') == 'none'){
    //         finger_res.find('input').val('');
    //     }
    //
    // }
    // 检查PCB数据输入
    function checkPCBinput(){
        emptyData();
        var pcb_flag = true;
        var list_value = ['gold_finger_thickness','gold_finger_length', 'gold_finger_width', 'gold_finger_qty']
        var span_val = $('.pages-active .cpo_input_quantity span.cpo_input_active').html();
        var finger_gold = $('.pages-active .cpo_input_surface_duoxuan a.cpo_input_active').find('span').html();
        $('.pages-active .cpo_pcb_quotation input[type="text"]').each(function () {
            if($(this).attr('name') == 'cpo_input_set_qty' || $(this).attr('name') == 'cpo_input_item_qty'){
                if(span_val == 'Set'){
                    if($(this).val() == ''){
                        $(this).addClass('cpo-border-red');
                        $(this).focus();
                        pcb_flag = false;
                        return pcb_flag;
                    }else{
                        $(this).removeClass('cpo-border-red');
                    }
                }else{
                    $(this).removeClass('cpo-border-red');
                }
            }else{
                if(finger_gold == 'Gold finger'){
                    if($(this).val() == ''){
                        $(this).addClass('cpo-border-red');
                        $(this).focus();
                        pcb_flag = false;
                        return pcb_flag;
                    }else{
                        $(this).removeClass('cpo-border-red');
                    }
                }else{
                    if($.inArray($(this).attr('name'), list_value) >= 0){
                        $(this).removeClass('cpo-border-red');
                    }else{
                        if($(this).val() == ''){
                            $(this).addClass('cpo-border-red');
                            $(this).focus();
                            pcb_flag = false;
                            return pcb_flag;
                        }else{
                            $(this).removeClass('cpo-border-red');
                        }
                    }
                }
            }

        });
        return pcb_flag

    }
    // 打包价输入检查
    function checkPCBPackage(){
        var pcb_flag = true;
        var $array = [
            'cpo_input_set_qty',
            'cpo_input_item_qty',
            'gold_finger_thickness',
            'gold_finger_length',
            'gold_finger_width',
            'gold_finger_qty'
        ];
        $('.cpo_pcbpackage_quotation input[type="text"]').each(function () {
            var value = $(this).attr('name');
            if($(this).val() == ""){
                if($.inArray(value, $array) >= 0){
                }else {
                    $(this).addClass('cpo-border-red');
                    $(this).focus();
                    pcb_flag = false;
                    return pcb_flag;
                }
            }else{
                $(this).removeClass('cpo-border-red');
            }
        })
        return pcb_flag;
    }

    // 钢网数量限制
    $('#submit_stencil_quotation input[name="cpo_stencil_quantity"]').on('change', function () {
        var qty = $(this).val();
        var side_list = ['Top', 'Bottom']
        var stencil_active = $('.cpo_stencil_side a.cpo_input_active').children('span').html();
        if(stencil_active == 'Top &amp; Bottom(On Separate Stencil)'){
            $(this).val(2);
        }else if(stencil_active == 'Top+Bottom(On Single Stencil)'){
            $(this).val(1);
        }
    });

    $('.cpo_stencil_existing a').on('click', function () {
        $(this).addClass('cpo_input_active').siblings('a').removeClass('cpo_input_active');
    });


    // 关闭广告
    $('div.page-close-btn').on('click', function () {
        $(this).parent().addClass('cpo-none');
    })
    // 判断文件大小
    function fileSize(ts){
        var flag = true;
        var file_size = 30*1024*1024;
        var this_size = ts.files[0].size;
        if(this_size >= file_size){
            flag = false;
        }else{
            flag = true;
        }
        return flag;
    }

    //上传文件
    $(".quo-active .cpo_file_line .cpo_file").on("change","input[type='file']",function(){
        if(fileSize(this) == false){
            $(this).parent().parent().find('div.cpoFileName').html('');
            webAlert('file size length must less than 30M.', null, false);
            // alert('file size length must less than 30M.')
            return false;
        }
        var fileObj=$(this);
        if(cpoFilePath(fileObj) == false){
            return false;
        }
        cpoFilePath(fileObj)
        changeUploadFile(this);
    })
    //上传文件
    $(".pcba_upload_file .cpo_file_line .cpo_file").on("change","input[type='file']",function(){
        if(fileSize(this) == false){
            $(this).parent().parent().find('div.cpoFileName').html('');
            webAlert('file size length must less than 30M.', null, false);
            // alert('file size length must less than 30M.')
            return false;
        }
        var fileObj=$(this);
        // var fileNameList = ['zip', 'rar']
        if(cpoFilePath(fileObj) == false){
            return false;
        }
        cpoFilePath(fileObj)
        changeUploadFile(this);
    })

    document.addEventListener("drop",function(e){  //拖离   
        e.preventDefault();      
    })  
    document.addEventListener("dragleave",function(e){  //拖后放   
        e.preventDefault();      
    })  
    document.addEventListener("dragenter",function(e){  //拖进  
        e.preventDefault();      
    })  
    document.addEventListener("dragover",function(e){  //拖来拖去    
        e.preventDefault();      
    }) 
    // 拖拽
    $(".quo-active .cpo_update_file").on("drop",".cpo_file_line", function(e){
        var attrName = $(this).find('input.cpo_files').attr('name');
        var files_file = $(this).find('input.cpo_files');
        if(fileSize(files_file[0]) == false){
            $(this).parent().parent().find('div.cpoFileName').html('');
            webAlert('file size length must less than 30M.', null, false);
            // alert('file size length must less than 30M.')
            return false;
        }
        var fileList = e.originalEvent.dataTransfer.files; //获取文件对象    
        var fileObf = e.originalEvent.dataTransfer; //获取文件对象  
        if(fileList.length == 0){                
            return false;            
        }else{
            cpoDropFilePath(fileObf, files_file, attrName)
            changeUploadFile(fileObf, attrName);
        }    
    });
    $(".pcba_upload_file").on("drop",".cpo_file_line",function(e){
        var attrName = $(this).find('input.cpo_files').attr('name')
        var files_file = $(this).find('input.cpo_files');
        if(fileSize(files_file[0]) == false){
            $(this).parent().parent().find('div.cpoFileName').html('');
            webAlert('file size length must less than 30M.', null, false);
            // alert('file size length must less than 30M.')
            return false;
        }
        var fileList = e.originalEvent.dataTransfer.files; //获取文件对象    
        var fileObf = e.originalEvent.dataTransfer; //获取文件对象    
        if(fileList.length == 0){                
            return false;            
        }else{
            cpoDropFilePath(fileObf, files_file, attrName);
            changeUploadFile(fileObf, attrName);
        }    
    });
    // 拖拽添加文件名
    function cpoDropFilePath(fileObf, files_file, attrName){
        var filePath = fileObf.files[0].name;
        var flag = true;
        if(filePath.indexOf("zip")!=-1 || filePath.indexOf("rar")!=-1){
            files_file.parent().parent().find('div.cpoFileError').html("").hide();
            files_file.parent().parent().find('div.cpoFileName').html(filePath).show()
            if(attrName == 'gerber_file'){
                $('#product_details form input[name="gerber_file"]').val(filePath);
            }
        }else if(filePath.indexOf("xls")!=-1 || filePath.indexOf("xlsx")!=-1){
            files_file.parent().parent().find('div.cpoFileError').html("").hide();
            files_file.parent().parent().find('div.cpoFileName').html(filePath).show()
            if(attrName == 'gerber_file'){
                $('#product_details form input[name="gerber_file"]').val(filePath);
            }
        }else{
            flag = false;
            files_file.parent().parent().find('div.cpoFileName').html("");
            files_file.parent().parent().find('div.cpoFileError').html("Please upload the correct file format !").show();
            webAlert("Please upload the correct file format !", null, false);
            // alert("Please upload the correct file format !");
        }
        return flag
    }
    // 添加文件名
    function cpoFilePath(fileObj){
        var filePath = fileObj.val();
        var flag = true;
        if(filePath.indexOf("zip")!=-1 || filePath.indexOf("rar")!=-1){
            fileObj.parent().parent().find('div.cpoFileError').html("").hide();
            var arr=filePath.split('\\');
            var fileName=arr[arr.length-1];
            fileObj.parent().parent().find('div.cpoFileName').html(fileName).show()
            if(fileObj.get(0).id == 'gerber_file'){
                $('#product_details form input[name="gerber_file"]').val(filePath);
            }
        }else if(filePath.indexOf("xls")!=-1 || filePath.indexOf("xlsx")!=-1){
            fileObj.parent().parent().find('div.cpoFileError').html("").hide();
            var arr=filePath.split('\\');
            var fileName=arr[arr.length-1];
            fileObj.parent().parent().find('div.cpoFileName').html(fileName).show()
            if(fileObj.get(0).id == 'gerber_file'){
                $('#product_details form input[name="gerber_file"]').val(filePath);
            }
        }else{
            flag = false;
            fileObj.parent().parent().find('div.cpoFileName').html("");
            fileObj.parent().parent().find('div.cpoFileError').html("Please upload the correct file format !").show();
            webAlert("Please upload the correct file format !", null, false);
            // alert("Please upload the correct file format !");
        }
        return flag
    }
    // 传入后台
    function changeUploadFile(fileObf, attrName) {
        var order_type = null;
        if($('.quo-content-ul .quo-active').length > 0){
            order_type = $('.order-nav-list .order-nav-active').children('a').html();
        }else{
            order_type = 'PCBA'
        }
        var file = fileObf.files[0];
        var tag_name;
        //读取本地文件，以gbk编码方式输出
        var reader = new FileReader();
        reader.readAsDataURL(file);
        var file_name = file.name;
        if(attrName){
            tag_name = attrName;
        }else{
            tag_name = fileObf.name;
        }
        reader.onload = function () {
            var datas = reader.result.substring(reader.result.indexOf(",")+1);
            var values = {
                'datas': datas,
                'name': file_name,
                'order_type': order_type,
                'file_type': 'Gerber File',
                'tag_name': tag_name
            }
            ajax.jsonRpc("/upload/file/json", 'call', values).then(function (data) {
                if(!data.error){
                    var pcba_need_pcb = $('.quo-active');
                    if(pcba_need_pcb.length <= 0){
                        if(data.tag_name == 'gerber_file'){
                            $('.file_ids .gerber_file_id').each(function () {
                                $(this).val(data.file_id);
                            });
                            $('.file_ids .gerber_atta_id').each(function () {
                                $(this).val(data.atta_id);
                            });
                            $('.file_ids .gerber_file_name').each(function () {
                                $(this).val(data.file_name);
                            });
                        }else if(data.tag_name == 'bom_file'){
                            $('.file_ids .bom_file_id').each(function () {
                                $(this).val(data.file_id);
                            });
                            $('.file_ids .bom_atta_id').each(function () {
                                $(this).val(data.atta_id);
                            });
                            $('.file_ids .bom_file_name').each(function () {
                                $(this).val(data.file_name);
                            });
                        }else{
                            $('.file_ids .smt_file_id').each(function () {
                                $(this).val(data.file_id);
                            });
                            $('.file_ids .smt_atta_id').each(function () {
                                $(this).val(data.atta_id);
                            });
                            $('.file_ids .smt_file_name').each(function () {
                                $(this).val(data.file_name);
                            });
                            // $('.pcba_calculation_results .file_ids .smt_file_id').val(data.file_id);
                            // $('.pcba_calculation_results .file_ids .smt_atta_id').val(data.atta_id);
                            // $('.pcba_calculation_results .file_ids .smt_file_name').val(data.file_name);
                        }
                    }else{
                        if(data.tag_name == 'gerber_file'){
                            $('.quo-active .file_ids .gerber_file_id').val(data.file_id);
                            $('.quo-active .file_ids .gerber_atta_id').val(data.atta_id);
                            $('.quo-active .file_ids .gerber_file_name').val(data.file_name);
                        }else if(data.tag_name == 'bom_file'){
                            $('.quo-active .file_ids .bom_file_id').val(data.file_id);
                            $('.quo-active .file_ids .bom_atta_id').val(data.atta_id);
                            $('.quo-active .file_ids .bom_file_name').val(data.file_name);
                        }else{
                            $('.quo-active .file_ids .smt_file_id').val(data.file_id);
                            $('.quo-active .file_ids .smt_atta_id').val(data.atta_id);
                            $('.quo-active .file_ids .smt_file_name').val(data.file_name);
                        }
                    }

                }else{
                    webAlert(data.error, null, false);
                    // alert(data.error);
                }

            })
        }
    }
    function getLoginData(data){
        /*
        * 判断登录状态
        * */
        // alert(data.login);
        // window.location.href = data.url;
        // $('#pcb_login_signup .oe_login_form').find('in
        //
        // put[name="src"]').val(data.src)
        // $('#pcb_login_signup .oe_login_form').find('input[name="type"]').val(data.type)
        // $('#pcb_login_signup .oe_login_form').attr('action', data.url);
        var SIGNUP_COOKIE_HISTORY = 'quote_signup_history';
        var getQuote = utils.get_cookie('quote_signup_history');
        if(getQuote){
            var url_history = JSON.parse(getQuote);
            url_history.src = data.src;
            url_history.type = data.type;
        }else{
            var url_history = {
                'src': data.src,
                'type': data.type,
                'quote_id': data.quote_id,
            }
        }
        utils.set_cookie(SIGNUP_COOKIE_HISTORY, JSON.stringify(url_history), 60*60*24); // 1 day cookie
        let url = '/quote/login?' + data.url;
        $('#pcb_login_signup .cpo_minilogin_iframe').attr('src', url);
        $('#pcb_login_signup').modal('show');
    }
    //小导航
    $('.cpo-small-nav li a').click(function () {
        if($(this).hasClass('cpo-stencil-a')){
            $(this).parent().parent().removeClass('cpo-nav-fixed');
        }
    });
    $('.cpo-small-nav .cpo-close').click(function () {
        $(this).parent().removeClass('cpo-nav-fixed');
        $(this).addClass('cpo-none');
    })

    $(document).on('click', function () {
        var small_nav = $('.cpo-small-nav');
        if(small_nav.length){
            small_nav.removeClass('cpo-nav-fixed');
        }
    });

    //选择收货地址 刷新页面
    $('.oe_cart .panel').on('click', function(){
        $(this).siblings('form').submit();
    })

    //
    // 订单详情
    $('.cpo_cart_line_detail').on('click', '.cart_show_hide_detail', function () {
        $(this).toggleClass('put-away');
        $(this).next().toggle();
        return false;
    })

    // ------------------------------------------------------- //
    // Sidebar Functionality
    // ------------------------------------------------------ //
    $('.ac-page').on('click', '#toggle-btn', function (e) {
        e.preventDefault();
        $(this).toggleClass('active');

        $('.ac-page .side-navbar').toggleClass('shrinked');
        $('.ac-page .content-inner').toggleClass('active');
        $(document).trigger('sidebarChanged');

        if ($(window).outerWidth() > 1183) {
            if ($('#toggle-btn').hasClass('active')) {
                $('.ac-page .brand-small').hide();
                $('.ac-page .brand-big').show();
            } else {
                $('.ac-page .brand-small').show();
                $('.ac-page .brand-big').hide();
            }
        }

        if ($(window).outerWidth() < 1183) {
            $('.ac-page .brand-small').show();
        }
    });
    // Help 鼠标操作

    $('.help-content a').mouseover(function () {
        $(this).find('div.tips-content').css('display', 'block');
        // $(this).find('div.help-tips').stop(true,true).show('slow');
    }).mouseout(function () {
        var self = this;
        $(self).find('div.tips-content').css('display', 'none');
    })
    // $('.help-content a').mouseout(function () {
    //     var self = this;
    //     // $(self).find('div.help-tips').stop(true,true).hide(2000);
    //     self.find('div.help-tips').css('display', 'none');
    //     return false;
    //     // set_mouesout = setInterval(function () {
    //     //     $this.find('div.help-tips').css('display', 'none');
    //     //     console.log(123)
    //     //     log(123)
    //     // }, 100);
    //     log(123);
    //     // setTimeout(function() {
    //     //     $(self).find('div.help-tips').stop(true,true).hide(2000);
    //     // }, 3000);
    // });
    //
    // 状态选择
    $('#cpo_order_state').on('click', '.dashboard-counts .item', function () {
        // var state = $(this).find('input[name="state"]').val();
        var number = $(this).find('div.number').text();
        // if(number == 0){
        //     return false;
        // }
        // $(this).addClass('ni-active').siblings().removeClass('ni-active');
        // var values = {
        //     'state': state
        // };
        // ajax.jsonRpc('/order/state', 'call', values).then(function (data) {
        //     $('#cpo_order_state').empty();
        //     $('#cpo_order_state').html(data.order_select);
        // });
    })
    // 删除收货地址
    $('.ac-page .my_account_addres').on('click', 'input.delete-btn', function () {
        $('.svg_loading').addClass('cpo-block').removeClass('cpo-none');
        ajax.jsonRpc('/delete/address', 'call', {
            'pid': this.id
        }).then(function (data) {
            if(data.error){
                webAlert(data.error, null, false);
                // alert(data.error);
            }else{
                webAlert('Successfully deleted!', function (f) {
                    if(f){
                        window.location.href = data.url;
                    }
                }, false);
                // alert('Successfully deleted!');
                // window.location.href = data.url;
                $('.svg_loading').addClass('cpo-none').removeClass('cpo-block');
            }
        })
    });
    // 添加PO号
    $('#cpo_website_ele_cart_order .cpo_po_number').on('click', 'a.check_po_number', function () {
        var this_val = $(this).parent().find('input[name="po_number"]').val();
        var this_id = $(this).parent().find('input[name="order_id"]').val();
        $('#edit_cpo_po_number .po_number_form').find('input[name="po_number"]').val(this_val);
        $('#edit_cpo_po_number .po_number_form').find('input[name="order_id"]').val(this_id);
        $('#edit_cpo_po_number').modal('show');
    });
    //  添加PO号
    $('#edit_cpo_po_number .po_number_form').on('click', '.confirm_btn', function () {
        svgBlockNone($('.svg_loading'), 'block');
        var values = {}
        $('#edit_cpo_po_number .po_number_form input').each(function () {
            values[this.name] = this.value;
        })
        ajax.jsonRpc('/po/number', 'call', {
            'vals': values,
        }).then(function (data) {
            $('#edit_cpo_po_number').modal('hide');
            if(data.error){
                svgBlockNone($('.svg_loading'), 'none');
                webAlert(data.error, null, false);
                // alert(data.error);
            }else{
                webAlert('Added successfully!', function (f) {
                    if(f){
                        window.location.href = '/shop/cart';
                    }
                }, false);
                // alert('Added successfully!');
                // window.location.href = '/shop/cart';
            }
        })

    });
    // 添加Part No.
    $('#cpo_website_ele_cart_order .cpo_po_number').on('click', 'a.check_part_no', function () {
        var this_val = $(this).parent().find('input[name="part_no"]').val();
        var this_id = $(this).parent().find('input[name="order_id"]').val();
        $('#edit_cpo_part_number .part_number_form').find('input[name="part_no"]').val(this_val);
        $('#edit_cpo_part_number .part_number_form').find('input[name="order_id"]').val(this_id);
        $('#edit_cpo_part_number').modal('show');
    });
    //  添加Part No.
    $('#edit_cpo_part_number .part_number_form').on('click', '.confirm_btn', function () {
        svgBlockNone($('.svg_loading'), 'block');
        var values = {}
        $('#edit_cpo_part_number .part_number_form input').each(function () {
            values[this.name] = this.value;
        })
        ajax.jsonRpc('/part/number', 'call', {
            'vals': values,
        }).then(function (data) {
            $('#edit_cpo_part_number').modal('hide');
            if(data.error){
                // alert(data.error);
                webAlert(data.error, null, false);
                svgBlockNone($('.svg_loading'), 'none');
            }else{
                webAlert('Added successfully!', function (f) {
                    if(f){
                        window.location.href = '/shop/cart';
                    }
                }, false);
                // alert('Added successfully!');
            }
        })
    });

    // 搜索功能
    $('.ac-page').on('click', '#my_account_search .search', function () {
        var get_data = {}
        $('#my_account_search input[type="text"]').each(function () {
            get_data[this.name] = this.value
        });
        ajax.jsonRpc('/order/search', 'call', get_data).then(function (data) {
            if(data.error){
                webAlert(data.error, null, false);
                // alert(data.error)
            }else{
                $('#all_order_status_return').empty();
                $('#all_order_status_return').html(data.order_search);
            }
        })
    });
    // 编辑数据 (购物车数据更改)
    $('#testest').on('click', '.edit_order_form a.edit-btn', function () {
        var values = {};
        var $data = $(this).parent().find('input');
        $data.each(function () {
            values[this.name] = this.value;
        });
        if(values.order_type == 'PCBA' && values.quotation_line == 'true'){
            var $select = $('#cpo_select_pcb_or_pcba .input_content');
            $select.empty();
            $.each(values, function (k, v) {
                var $in = '<input type="hidden" name="'+ k +'" value="'+ v +'"/>';
                $select.append($in);
            })
            $('#cpo_select_pcb_or_pcba').modal('show');
            return false;
        }
        ajax.jsonRpc('/edit/order', 'call', values).then(function (data) {
            window.location.href = data.url;
        })
    });
    $('#cpo_select_pcb_or_pcba .select_order_box').on('click', 'button', function () {
        var values = {};
        var $select = $('#cpo_select_pcb_or_pcba .input_content');
        $select.append('<input type="hidden" name="select_type" value="'+ $(this).text() +'"/>');
        var $input = $('#cpo_select_pcb_or_pcba .cpo_select_pcb_or_pcba_edit input');
        $input.each(function () {
            values[this.name] = this.value;
        })
        ajax.jsonRpc('/edit/order', 'call', values).then(function (data) {
            window.location.href = data.url;
        })
    })
    // 支付退款状态选择
    // 状态选择
    $('#cpo_paid_box').on('click', '.dashboard-paid .item', function () {
        // var state = $(this).find('input[name="state"]').val();
        var number = $(this).find('div.number').text();
        // if(number == 0){
        //     return false;
        // }
        // $(this).addClass('ni-active').siblings().removeClass('ni-active');
        // var values = {
        //     'state': state
        // };
        // ajax.jsonRpc('/paid/status', 'call', values).then(function (data) {
        //     $('#cpo_paid_box').empty();
        //     $('#cpo_paid_box').html(data.paid_select);
        // });
    })
    // 增加侧边联系方式最小化
    $('.cpo_help .help-close').on('click', function () {
        $(this).addClass('cpo-none').removeClass('cpo-block');
        $(this).parent().find('div.help-show').addClass('cpo-block').removeClass('cpo-none');
        $(this).parent().addClass('cpo_help_hide');
    });
    $('.cpo_help .help-show').on('click', function () {
        $(this).addClass('cpo-none').removeClass('cpo-block');
        $(this).parent().find('div.help-close').addClass('cpo-block').removeClass('cpo-none');
        $(this).parent().removeClass('cpo_help_hide');
    })
    //
    $('#cpo_refund_form_data .refund_textarea').on('change', function () {
        $(this).parent().find('input[type="hidden"]').val($(this).val());
        // log($(this).parent().find('input[type="hidden"]').val());
    });
    // 发起退款申请
    $('.cpo-od-ul .od-dt-content form .request-refund').on('click', function () {
        var value = {};
        $(this).parent().find('input').each(function () {
            value[this.name] = this.value;
        });
        ajax.jsonRpc('/refund/submit', 'call', value).then(function (data) {
            if(data.error){
                webAlert(data.error, null, false);
                // alContent(data.error);
                // alert(data.error);
            }else {
                window.location.href = data.url
            }
        });
    });
    // 提交申请退款
    $('#cpo_refund_form_data').on('click', 'a.btn', function () {
        svgBlockNone($('.svg_loading'), 'block');
        var value = {};
        $('#cpo_refund_form_data input').each(function () {
            value[this.name] = this.value;
        })
        ajax.jsonRpc('/refund/send', 'call', value).then(function (data) {
            if(data.error){
                webAlert(data.error, null, false);
                // alert(data.error);
            }else{
                webAlert(data.success, function (f) {
                    if(f){
                        window.location.href = data.url;
                    }
                }, false);
                // alert(data.success);

            }
            svgBlockNone($('.svg_loading'), 'none');
        });
    })
    // 发起取消申请
    $('.cpo-od-ul .od-dt-content form .cancel-refund').on('click', function () {
        svgBlockNone($('.svg_loading'), 'block');
        var value = {};
        $(this).parent().find('input').each(function () {
            value[this.name] = this.value;
        });
        ajax.jsonRpc('/cancel/refund', 'call', value).then(function (data) {
            if(data.error){
                 webAlert(data.error, null, false);
                // alContent(data.error);
            }else {
                webAlert(data.success, function (f) {
                    if(f){
                        window.location.href = data.url;
                    }
                }, false);
                // alert(data.success);
                // window.location.href = data.url;
            }
        });
        svgBlockNone($('.svg_loading'), 'none');
    });
    /*
    * Message 详情
    * 1、监听输入框
    * 2、发送消息
    * */
    // 1 监听输入框
    $('#cpo_message_form .message_content').bind("input propertychange", function(event){
        var self = $(this);
        var message = self.text();
        var message_content = self.html();
        var img = self.find('img').length;
        var btn = self.parent().parent().find('input[type="button"]');
        var msg_c = self.parent().find('input[name="message"]');
        if(message || img > 0){
            btn.removeAttr('disabled');
            msg_c.val('');
            msg_c.val(message_content);
        }else {
            self.parent().find('input[name="message"]').val('');
            btn.attr('disabled', 'disabled');
        }
    });
    // 输入框添加图片
    // 上传文件
    $('#msg_upload_file').on('change', function(){
        var imgFiles = $(this)[0].files;
        var reply_content = $('#cpo_message_form .message_content');
        if(imgFiles[0].size / 1024 / 1024 > 3){
            $(this).val('');
            webAlert('The file size cannot exceed 3M!', null, false);
            // alert('The file size cannot exceed 3M!');
            return false
        }
        var fileFormat = imgFiles[0].name.split('.')[1].toLowerCase()
        if(!fileFormat.match(/png|jpg|jpeg/) ) {
            webAlert('Upload failed, file format must be: png/jpg/jpeg !', null, false);
            // alert('Upload failed, file format must be: png/jpg/jpeg !');
            return
        }
        var reader = new FileReader();
        reader.readAsDataURL(this.files[0]);
        reader.onload = function (e) {
            var img_content = '<div class="img-reply"><img src="'+reader.result+'"/></div><br/>'
            reply_content.append(img_content);
            checkMsgContent(reply_content);
        };
    })
    function checkMsgContent(ele){
        var img = ele.find('img').length;
        var text = ele.text();
        var btn = ele.parent().parent().find('input[type="button"]');
        if(img > 0 || text){
            btn.removeAttr('disabled');
            ele.parent().find('input[name="message"]').val(ele.html());
        }
    }
    // 重置
    $('#cpo_message_form .eq-reset').on("click", function(){
        $('#cpo_message_form .message_content').html('').focus();
        $('#cpo_message_form input[name="message"]').val('');
    })
    // 2 发送消息
    $('#cpo_message_form').on('click', 'input[type="button"]', function () {
        svgBlockNone($('.svg_loading'), 'block');  // 开打遮罩层（加载）
        var value = {}, self = $(this), $parent = self.parent().parent().find('input');
        $parent.each(function () {
            value[this.name] = this.value;
        });
        ajax.jsonRpc('/send/message', 'call', value).then(function (data) {
            if(data.error){
                webAlert(data.error, null, false);
                // alert(data.error);
            }else{
                window.location.href = data.url;
            }
            svgBlockNone($('.svg_loading'), 'none');  // 关闭遮罩层
        });
    });
    /*
    * 增加查看订单详情
    * */
    $('.ac-page').on('click', '.cpo-od-ul .cpo-od-li .home-order-details', function () {
        svgBlockNone($('.svg_loading'), 'block');  // 开打遮罩层（加载）
        var self = $(this), $modal = $('#home_order_details_Modal'), $content = $('#home_order_details_Modal .modal-body');
        var $oid = self.parent().find('input[name="oid"]').val();
        ajax.jsonRpc('/show/order-details', 'call', {
            'oid': $oid,
        }).then(function (data) {
            if(data.error){
                webAlert(data.error, null, false);
                // alert(data.error)
            }else{
                $content.empty().html(data.show_order_details);
                $modal.modal('show');
            }
        });
        svgBlockNone($('.svg_loading'), 'none');  // 关闭遮罩层
    })
    /*
    * 支付和退款的查询
    * */
    // 搜索功能
    $('.ac-page').on('click', '.cpo-paid-search .search', function () {
        var get_data = {}
        $('.cpo-paid-search input[type="text"]').each(function () {
            get_data[this.name] = this.value
        });
        ajax.jsonRpc('/paid/search', 'call', get_data).then(function (data) {
            if(data.error){
                webAlert(data.error, null, false);
                // alert(data.error)
            }else{
                $('#cpo_paid_box').empty();
                $('#cpo_paid_box').html(data.paid_search);
            }
        })
    });

    /*
    * 工程问题（问客）
    * */
    $('.ac-page').on('click', '.cpo-od-ul .cpo-od-li .home-order-eq', function () {
        svgBlockNone($('.svg_loading'), 'block');  // 开打遮罩层（加载）
        var self = $(this), $modal = $('#home_order_qe_Modal'), $content = $('#home_order_qe_Modal .modal-body');
        var $oid = self.parent().parent().find('input[name="oid"]').val();
        ajax.jsonRpc('/show/eq-details', 'call', {
            'oid': $oid,
        }).then(function (data) {
            if(data.error){
                webAlert(data.error, null, false);
                // alert(data.error)
            }else{
                $content.empty().html(data.show_eq_details);
                $modal.modal('show');
            }
        });
        svgBlockNone($('.svg_loading'), 'none');  // 关闭遮罩层
    })
    changeContentHeight('.user_reply_content', 150);
    function changeContentHeight(cls, minHeight){
		var idArr = $(cls); // 获取传进来的class或者id
		$.each(idArr, function(k, v) { // 循环遍历 为每一个添加它自己的scrollHeight
			$(v).css({
				'min-height': v.scrollHeight+'px',
				'overflow': 'auto',
				// 'height':  v.scrollHeight+'px',
				// 'overflow': 'auto'
				})    // 其实这里换成overflow hidden效果更好 没滚动条
		});
		$(cls).on('input prototychange', function(){ // 监听的事件 可以换成keyup等等 可以自行封装
			var that = $(this);
			var reply = that.html();
			var reply_text = that.text();
			var img = that.find('img').length;
            var btn = that.parent().parent().find('input[type="button"]');
            var eq_content = that.parent().find('input[name="user_reply_content"]');
            if(reply_text || img > 0){
                btn.removeAttr('disabled');
                eq_content.val('');
                eq_content.val(reply);
            }else {
                btn.attr('disabled', 'disabled');
                eq_content.val('');
            }
			// that.css('height', '0') // 避免每次改变的时候高度都会增加的问题
			if(that.val().length<=0){ // 如果输入框内容空了  回到最小的高度
				that.css({'min-height': minHeight+'px'})
			}else{ // 不是空的话 设置高度
                that.css('height', that[0].scrollHeight+'px') // 这里也可以把最小高度一起改变
                // console.log(that[0].scrollHeight)
			}
		})
	}
    // 重置
    $('#cpo_eq_form_data .eq-reset').on("click", function(){
        $('#cpo_eq_form_data .user_reply_content').html('').focus();
        $('#cpo_eq_form_data input[name="user_reply_content"]').val('');
    })
    // 输入框添加图片
    // 上传文件
    $('#reply_upload_file').on('change', function(){
        var imgFiles = $(this)[0].files;
        var reply_content = $('#cpo_eq_form_data .user_reply_content');
        if(imgFiles[0].size / 1024 / 1024 > 3){
            $(this).val('');
            webAlert('The file size cannot exceed 3M!', null, false);
            // alert('The file size cannot exceed 3M!');
            return false;
        }
        var fileFormat = imgFiles[0].name.split('.')[1].toLowerCase()
        if(!fileFormat.match(/png|jpg|jpeg/) ) {
            webAlert('Upload failed, file format must be: png/jpg/jpeg !', null, false);
            // alert('Upload failed, file format must be: png/jpg/jpeg !');
            return false;
        }
        var reader = new FileReader();
        reader.readAsDataURL(this.files[0]);
        reader.onload = function (e) {
            // console.log(datas);
            var img_content = '<div class="img-reply"><img src="'+reader.result+'"/></div><br/>'
            reply_content.append(img_content);
            checkEQContent(reply_content);
        };
    })
    // 上传文件
    $('#reply_upload_file2').on('change', function(){
        var imgFiles = $(this)[0].files;
        var reply_content = $('#cpo_eq_form_data .user_reply_content');
        if(imgFiles[0].size / 1024 / 1024 > 24){
            $(this).val('');
            webAlert('The file size cannot exceed 24M!', null, false);
            // alert('The file size cannot exceed 24M!');
            return false;
        }
        var fileFormat = imgFiles[0].name.split('.')[1].toLowerCase()
        // if(!fileFormat.match(/png|jpg|jpeg/) ) {
        //     alert('Upload failed, file format must be: png/jpg/jpeg !');
        //     return false;
        // }
        //读取本地文件，以gbk编码方式输出
        var file_desc = $('#cpo_paid_box .h4').text().trim()
        var name = imgFiles[0].name;
        var type = imgFiles[0].type;
        var reader = new FileReader();
        reader.readAsDataURL(this.files[0]);
        reader.onload = function (e) {
            // console.log(datas);
            var datas = reader.result.substring(reader.result.indexOf(",")+1);
            ajax.jsonRpc('/ask/file', 'call', {
                'name': name,
                'datas': datas,
                'file_desc': file_desc,
            }).then(function (data) {
                if(data.error){
                    webAlert(data.error, null, false);
                    // alert(data.error)
                }else{
                    var img_content = '<div class="img-reply"><a class="o_image" href="/down/file?attaId='+data.atta_id+'" data-mimetype="'+type+'"></a></div><br>'
                    reply_content.append(img_content);
                    checkEQContent(reply_content);
                }
            });
        };
    })
    function checkEQContent(ele){
        var img = ele.find('img').length;
        var a_l = ele.find('a.o_image').length;
        var text = ele.text();
        var btn = ele.parent().parent().find('input[type="button"]');
        if(img > 0 || text){
            btn.removeAttr('disabled');
            ele.parent().find('input[name="user_reply_content"]').val(ele.html());
        }
        if(a_l > 0 || text){
            btn.removeAttr('disabled');
            ele.parent().find('input[name="user_reply_content"]').val(ele.html());
        }
    }

    $('#cpo_eq_form_data input.btn').on('click', function () {
        svgBlockNone($('.svg_loading'), 'block');  // 打开遮罩层
        var values = {};
        var $input = $(this).parent().parent().find('input');
        var img = $('.user_reply_content img').length;
        var aL = $('.user_reply_content a.o_image').length;
        var text = $(this).parent().parent().find('div.user_reply_content').text();
        $input.each(function () {
            values[this.name] = this.value;
        });
        // var ct = values.user_reply_content.trim();
        if((!text && img <= 0) && (!text && aL <= 0)){
            webAlert('Please fill in the content first!', null, false);
            // alert('Please fill in the content first!');
            return false;
        }
        ajax.jsonRpc('/ask/reply', 'call', values).then(function (data) {
            if(data.error){
                webAlert(data.error, null, false);
                // alert(data.error);
            }else{
                window.location.href = data.url;
            }
        })
        svgBlockNone($('.svg_loading'), 'none');  // 关闭遮罩层
    })
    // 上传文件
    // $('#reply_upload_file').on('change', function(){
    //     var imgFiles = $(this)[0].files;
    //     for (var i=0;i<imgFiles.length;i++){
    //         const filePath = imgFiles[i].name;
    //         const fileFormat = filePath.split('.')[1].toLowerCase();
    //         const src = window.URL.createObjectURL(imgFiles[i]);
    //         if(!fileFormat.match(/png|jpg|jpeg/) ) {
    //             alert('Upload failed, file format must be: png/jpg/jpeg !');
    //             return false
    //         }
    //         if(imgFiles[i].size / 1024 / 1024 > 3){
    //             alert('The file size cannot exceed 3M!');
    //             return false
    //         }
    //         //读取文件过程方法
    //         var reader = new FileReader();
    //         reader.readAsDataURL(imgFiles[i]);
    //          reader.onload = function (e) {
    //             // console.log(datas);
    //             files_reply.push(reader.result);
    //         }
    //         var preview = $('#cpo_eq_form_data .reply_img');
    //         var img = '<img src="'+ src +'" width="200" height="200"/>';
    //         preview.append(img)
    //     }
    //     if($('.reply_img img').length > 3){
    //         alert('Upload up to 3 pictures!');
    //         $('.reply_img img').slice(-1).remove();
    //         files_reply.slice(-1).pop();
    //         return false;
    //     }
    // })
    $("#cpo_eq_form_data").on('click', 'img', function(){
        var _this = $(this);//将当前的pimg元素作为_this传入函数
        imgShow("#outerdiv", "#innerdiv", "#bigimg", _this);
    });
    $(".cpo_message_section").on('click', 'img', function(){
        var _this = $(this);//将当前的pimg元素作为_this传入函数
        imgShow("#outerdiv", "#innerdiv", "#bigimg", _this);
    });
    $('.select-route-active').on('change', function () {
        var select_val = $(this).val();
        var a_text = $(this).next('input[name="route_oid"]').val();
        var url = '/show/eq-details/' + a_text + '/' + select_val;
        window.location.href = url;
    });
    // 生产制造的路径
    $('.select-route-mft-active').on('change', function () {
        var select_val = $(this).val();
        var url = '/manufacturing/state?oid=' + select_val;
        window.location.href = url;
    });
    /*
    * 内容过长滚动
    * */
    $(function () {
        $("body .card-body .table-responsive").scroll(function () {
            var scrollTop = this.scrollTop;
            $(this).find("li.od-li-title").attr("style", "transform: translateY(" + scrollTop + "px);")
        });
    })
    /*
    * 登录和注册页面的更改！
    * */
    var materialInputs = $('.login-page input.input-material');
    // activate labels for prefilled values
    materialInputs.filter(function() { return $(this).val() !== ""; }).siblings('.label-material').addClass('active');
    // move label on focus
    materialInputs.on('focus', function () {
        $(this).siblings('.label-material').addClass('active');
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
    // 登录注册的更改结束！
    // 分页显示
    $(".cpo_eq_list_tabel").dataTable({
        "bPaginate": true,
        "bJQueryUI" : true, //是否使用 jQury的UI theme
        "bLengthChange": false, // 左上角的show行数
        "iDisplayLength": 3,
        "bProcessing" : true,
        "bInfo" : false, // 是否显示页脚信息，DataTables插件左下角显示记录数
        "sProcessing" : "正在获取数据，请稍后...",
    });
    $(".cpo_message_tabel").dataTable({
        "bPaginate": true,
        "bJQueryUI" : true, //是否使用 jQury的UI theme
        "bLengthChange": false, // 左上角的show行数
        "iDisplayLength": 8,
        "bProcessing" : true,
        "bInfo" : false, // 是否显示页脚信息，DataTables插件左下角显示记录数
    });
    //
    // $('#cpo_eq_form_data .reply_content .content-box').on('DOMNodeInserted',function(){
    //     $('#cpo_eq_form_data .reply_content .content-box').each(function(){
    //         if($(this).children().height() > 120){
    //             $(this).parent().append('<a class="btn reply-dt">show details</a>');
    //         }
    //     });
    // })
    $('.card-body .content-box').each(function(){
        if($(this).children().height() > 120){
            $(this).parent().append('<a class="btn reply-dt">Open</a>');
        }
    });
    $('.reply-content').on('click', 'a.btn', function () {
        var c_height = $(this).prev('div.content-box').height();
        if(c_height > 120){
            $(this).prev('div.content-box').animate({'max-height': '120px'}, 500)
            $(this).text('Open');
        }else{
            $(this).prev('div.content-box').animate({'max-height': '100%'}, 500)
            $(this).text('Close');
        }
    });
    // 消息的折叠
    $('.message-content').on('click', 'a.btn', function () {
        var c_height = $(this).prev('div.content-box').height();
        if(c_height > 120){
            $(this).prev('div.content-box').animate({'max-height': '120px'}, 500)
            $(this).text('Open');
        }else{
            $(this).prev('div.content-box').animate({'max-height': '100%'}, 500)
            $(this).text('Close');
        }
    });
    
    // 修改头像
    $('#upload_avatar').on('change', function () {
        var imgFiles = $(this)[0].files;
        for (var i=0;i<imgFiles.length;i++){
            const filePath = imgFiles[i].name;
            const fileFormat = filePath.split('.')[1].toLowerCase();
            if(!fileFormat.match(/png|jpg|jpeg/) ) {
                webAlert('Upload failed, file format must be: png/jpg/jpeg !', null, false);
                // alert('Upload failed, file format must be: png/jpg/jpeg !');
                return false;
            }
            if(imgFiles[i].size / 1024 / 1024 > 3){
                webAlert('The file size cannot exceed 3M!', null, false);
                // alert('The file size cannot exceed 3M!');
                return false;
            }
            var reader = new FileReader();
            reader.readAsDataURL(imgFiles[i]);
             reader.onload = function (e) {
                ajax.jsonRpc('/change/avatar', 'call', {
                    'datas': reader.result,
                }).then(function (data) {
                    if(data.error){
                         webAlert(data.error, null, false)
                        // alert(data.error);
                    }else{
                        webAlert(data.success, function (f) {
                            if(f){
                                window.location.href = '/my/home';
                            }
                        }, false);
                        // alert(data.success);

                    }
                })
            }
        }
    })
    // 更改时区
    $('.cpo-timezones').on('change', function () {
        svgBlockNone($('.svg_loading'), 'block');  // 打开遮罩层
        let self = $(this);
        let tz = self.val();
        ajax.jsonRpc('/cpo/change/tz', 'call', {
            'tz': tz,
        }).then(function (data) {
            if(data.error){
                webAlert(data.error, null, false);
                // alert(data.error);
            }else{
                // alert(data.success);
                var tips = 'Current Timezone Changed to: '+tz;
                webAlert(tips, function (f) {
                    if(f){
                        location.reload();
                    }
                }, false);
                // alert('Current Timezone Changed to: '+tz);
            }
            svgBlockNone($('.svg_loading'), 'none');  // 打开遮罩层
            // location.reload();
        })
    })
    // 邮箱验证
    $('.ac-page input[type="email"]').on('change', function () {
        var value = $(this).val();
        var check = utils.is_email(value, false);
        if(!check){
            $(this).val('');
            $(this).focus();
            webAlert("Please enter a valid email ! eg: sales@chinapcbone.com", null, false);
            // alert("Please enter a valid email ! eg: sales@chinapcbone.com");
        }
    })
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

    $('.cpo_email_registered input#login').on('change', function () {
        var value = $(this).val();
        var check = utils.is_email(value, false);
        if(!check){
            $(this).val('');
            $(this).focus();
            webAlert("Please enter a valid email ! eg: sales@chinapcbone.com", null, false);
            // alert("Please enter a valid email ! eg: sales@chinapcbone.com");
        }
    })
    // 发送邮件的倒计时
    var setTime;
    function daojishi(ele, value, textSpan){
        var time = parseInt(value);
        setTime=setInterval(function(){
            if(time<=0){
                clearInterval(setTime);
                ele.removeAttr('disabled');
                textSpan.css('display', 'none');
                textSpan.text(5);
                return;
            }
            time--;
            textSpan.text(time);
        },1000);
    }
    $('#sendEmail').on('click', function(){
        $(this).attr('disabled', 'disabled');
        var textSpan = $(this).parent().find('span.textspan');
        var ele = $(this), value = textSpan.text();
        textSpan.css('display', 'inline-block');
        daojishi(ele, value, textSpan);
    })
    // 创建特殊订单（需要人工联系的订单）
    $('.cpo_create_special_order').on('click', function () {
        var check = specialCheckFile();
        if(!check){
            return false;
        }
        $('#create_special_order_modal').modal('show')
    })
    
    function specialCheckFile() {
        var gerber_file = $('.file_boxs .gerber_file_box p').length;
        if(gerber_file <= 0){
            $('.generate_special_documents .gsd_tips').css('display', 'block');
            $('.generate_special_documents .gsd_tips').text('Please upload "Gerber File" first');
            return false;
        }else{
            $('.generate_special_documents .gsd_tips').css('display', 'none');
        }
        return true;
    }
    $('#create_special_btn').on('click', function () {
        var pcb_from = pcbGetFormData();
        var pcb_special_requirements = pcbQuotationSpecialForm();
        var cpohdi = cpoHdi();
        var soft_hard = cpoFlexRigidForm();
        var file_names = specialGetFiles();
        ajax.jsonRpc('/create/special/order', 'call', {
            'pcb_value': pcb_from,
            'pcb_special_requirements': pcb_special_requirements,
            'cpohdi': cpohdi,
            'soft_hard': soft_hard,
            'file_names': file_names,
        }).then(function (data) {
            if(data.error){
                $('#create_special_order_modal .special-error').css('display', 'block');
                $('#create_special_order_modal .special-error').text(data.error);
            }else{
                $('#create_special_order_modal .special-error').css('display', 'none');
                $('#create_special_order_modal .special-success').css('display', 'block');
                $('#create_special_order_modal .special-success').text(data.success);
                window.location.href = data.url;
            }
        })
    })
    function specialGetFiles() {
        var gerber_file_id, gerber_atta_id,gerber_file_name;
        var bom_file_id,bom_atta_id,bom_file_name;
        var smt_file_id,smt_atta_id,smt_file_name;
        var file_name;
        gerber_file_id = $('.cpo_file_ids input[name="gerber_file_id"]').val();
        gerber_atta_id = $('.cpo_file_ids input[name="gerber_atta_id"]').val();
        gerber_file_name = $('.cpo_file_ids input[name="gerber_file_name"]').val();
        bom_file_id = $('.cpo_file_ids input[name="bom_file_id"]').val();
        bom_atta_id = $('.cpo_file_ids input[name="bom_atta_id"]').val();
        bom_file_name = $('.cpo_file_ids input[name="bom_file_name"]').val();
        smt_file_id = $('.cpo_file_ids input[name="smt_file_id"]').val();
        smt_atta_id = $('.cpo_file_ids input[name="smt_atta_id"]').val();
        smt_file_name = $('.cpo_file_ids input[name="smt_file_name"]').val();
        file_name = {
            'gerber_file_id': gerber_file_id,
            'gerber_atta_id': gerber_atta_id,
            'gerber_file_name': gerber_file_name,
            'bom_file_id': bom_file_id,
            'bom_atta_id': bom_atta_id,
            'bom_file_name': bom_file_name,
            'smt_file_id': smt_file_id,
            'smt_atta_id': smt_atta_id,
            'smt_file_name': smt_file_name,
        }
        return file_name;
    }
    // Contact us
    /*
    * 联系我们
    * */
    var contactus_page = $('.contactus-page input.input-material');
    // activate labels for prefilled values
    contactus_page.filter(function() { return $(this).val() !== ""; }).siblings('.label-material').addClass('active');
    // move label on focus
    contactus_page.on('focus', function () {
        $(this).siblings('.label-material').addClass('active');
    });
    contactus_page.bind("input propertychange",function(event){
        $(this).siblings('.label-material').addClass('active');
    });
    // remove/keep label on blur
    contactus_page.on('blur', function () {
        $(this).siblings('.label-material').removeClass('active');

        if ($(this).val() !== '') {
            $(this).siblings('.label-material').addClass('active');
        } else {
            $(this).siblings('.label-material').removeClass('active');
        }
    });
    $('.support_type_group select.form-control').on('change', function () {
        $('.support_type_group #cu_support_type').val($(this).val());
    })
    $('.cu_we_help #cu_content').on('change', function () {
        $('.cu_we_help #cu_content_inuput').val($(this).val());
    })
    $('#cu_submit').on('click', function () {
        var cu_data = {};
        $('.cu_customer_information .cu_form input').each(function () {
            cu_data[this.name] = this.value;
        })
        ajax.jsonRpc('/contactus/message', 'call', {
            'cu_data': cu_data,
        }).then(function (data) {
            if(data.error){
                webAlert(data.error, null, false);
            }else{
                var url = data.url;
                webAlert(data.success, function (f) {
                    if(f){
                        window.location.href = url;
                    }
                }, false);
            }
        })
    })
})


