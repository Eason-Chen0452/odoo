/*global $, _, ELEuploadfileJS */
odoo.define('website_cpo_sale.upload', function (require) {
"use strict";

var ajax = require('web.ajax');
var core = require('web.core');
var Widget = require('web.Widget');
var base = require('web_editor.base');
var website = require('website.website');

var qweb = core.qweb;
var _t = core._t;

if(!$('.oe_electron_js_upload').length) {
    return $.Deferred().reject("DOM doesn't contain '.oe_electron_js_upload'");
}

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
    init: function (el, order_id) {
        this._super(el, order_id);
        this.order_id = parseInt(order_id, 10);
        this.file = {};
        this.index_content = "";
        this.file_types = ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet','application/pdf'];
    },
    start: function () {
        this.$el.modal({
            backdrop: 'static'
        });
        //this.set_category_id();
        this.set_tag_ids();
    },
    //check_unique_slide: function (file_name) {
    //    var self = this;
    //    return ajax.jsonRpc('/web/dataset/call_kw', 'call', {
    //        model: 'slide.slide',
    //        method: 'search_count',
    //        args: [[['channel_id', '=', self.channel_id], ['name', '=', file_name]]],
    //        kwargs: {}
    //    });
    //},
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
        //var data = [{ id: 0, text: 'BOM File' }, { id: 1, text: 'SMT FILE' }, { id: 2, text: 'Gerber File' }];
        var tag_ids = $("#cpo_ele_tag_ids");
        ajax.jsonRpc("/get_electron_type", 'call', {}).then(function (data) {
            tag_ids.select2({
                data: data,
                width: '100%',
                placeholder:'请选择',
                allowClear:true
            })
        });
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
            this.$('.oe_slides_upload_loading').show();
            this.$('.modal-footer, .modal-body').hide();
            ajax.jsonRpc("/pcb_electron/upload_file", 'call', values).then(function (data) {
                if (data.error) {
                    self.display_alert(data.error);
                    self.$('.oe_slides_upload_loading').hide();
                    self.$('.modal-footer, .modal-body').show();
                } else {
                    window.location = data.url;
                }
            });
        }
    },
    cancel: function () {
        this.trigger("cancel");
    }
});

    // bind the event to the button
    $('.oe_electron_js_upload').on('click', function () {
        var order_id = $(this).attr('order_id');
        new cpo_ELE_Dialog(this, order_id).appendTo(document.body);
    });

    return {
        Websitecpo_ELE_Dialog: cpo_ELE_Dialog,
    }
});
