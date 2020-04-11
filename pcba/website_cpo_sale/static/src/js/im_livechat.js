odoo.define('website_cpo_sale.im_livechat', function (require) {
"use strict";

var im_livechat = require('im_livechat.im_livechat');
var local_storage = require('web.local_storage');
var bus = require('bus.bus').bus;
var config = require('web.config');
var core = require('web.core');
var session = require('web.session');
var time = require('web.time');
var utils = require('web.utils');
var ajax = require("web.ajax");
var ChatWindow = require('mail.ChatWindow');

var _t = core._t;
var QWeb = core.qweb;
// ajax.loadXML('/website_cpo_sale/static/src/xml/cpo_change_livechar_window.xml', QWeb);

im_livechat.LivechatButton = im_livechat.LivechatButton.extend({
    start: function () {
        var self = this;
        var p_super = this._super();
        self.cpo_reparse_im_box(self.$el);
        return p_super;
    },
    cpo_reparse_im_box: function(e){
        $('.open_im_livechar').css('display', 'inherit');
        $('.open_im_livechar').append(e);
        e.html('');
        // ajax.jsonRpc("/get_imchat_box_temp", 'call', {'button_text': this.options.button_text}).then(function (data) {
        //     $('.open_im_livechar').css('display', 'inherit');
        //     $('.open_im_livechar').append(e);
        //     e.html(data.html);
        //     $('.o_livechat_button #cpo_shrink_magnify').on('click', function () {
        //         // event.stopPropagation();
        //         $('.o_livechat_button .cpo_conversation_content').css('display', 'none');
        //         $(this).css('display', 'none');
        //         $('.o_livechat_button .cpo_im_box_p').css({'padding': '0', 'border': '0','background-color': 'rgba(255,255,255,0)'});
        //         return false
        //     });
        // });
    },

});


im_livechat.LivechatButton.include({
    close_chat: function(e){
        this.chat_window.destroy();
        utils.set_cookie('im_livechat_session', "", -1); // remove cookie
        bus.stop_polling();
        var im_livechat = require('im_livechat.im_livechat');
        var button = new im_livechat.LivechatButton(
                           $('body'),
                           window.location.origin,
                           {"channel_id": this.options.channel_id,
                            "default_message": this.options.default_message,
                            "input_placeholder": this.options.input_placeholder,
                            "button_text": this.options.button_text,
                            "channel_name": this.options.channel_name,
                            "default_username": this.options.default_username}
                       );
        button.appendTo($('body'));
        window.livechat_button = button;
    },
})
// im_livechat.LivechatButton.include({
//     // id: "cpo_send_message",
//     // events: {
//     //     "click": "btn_send_message"
//     // },
//     open_chat_window: function (channel) {
//         im_livechat.start()
//         var self = this;
//         var options = {
//             display_stars: false,
//             placeholder: this.options.input_placeholder || "",
//         };
//         var is_folded = (channel.state === 'folded');
//         this.chat_window = new ChatWindow(this, channel.id, channel.name, is_folded, channel.message_unread_counter, options);
//         this.chat_window.appendTo($('body')).then(function () {
//             self.chat_window.$el.css({right: 0, bottom: 0});
//             // self.$el.hide();
//         });
//         this.chat_window.on("close_chat_session", this, function () {
//             var input_disabled = this.chat_window.$(".o_chat_composer input").prop('disabled');
//             var ask_fb = !input_disabled && _.find(this.messages, function (msg) {
//                 return msg.id !== '_welcome';
//             });
//             if (ask_fb) {
//                 this.chat_window.toggle_fold(false);
//                 this.ask_feedback();
//             } else {
//                 this.close_chat();
//             }
//         });
//         this.chat_window.on("post_message", this, function (message) {
//             self.send_message(message).fail(function (error, e) {
//                 e.preventDefault();
//                 return self.send_message(message); // try again just in case
//             });
//         });
//         this.chat_window.on("fold_channel", this, function () {
//             this.channel.state = (this.channel.state === 'open') ? 'folded' : 'open';
//             utils.set_cookie('im_livechat_session', JSON.stringify(this.channel), 60*60);
//         });
//         this.chat_window.thread.$el.on("scroll", null, _.debounce(function () {
//             if (self.chat_window.thread.is_at_bottom()) {
//                 self.chat_window.update_unread(0);
//             }
//         }, 100));
//     },
// });

// ChatWindow.include({
//     id: "cpo_send_message",
//     events: {
//         "click": "btn_send_message"
//     },
//     btn_send_message: function () {
//         this.il = new im_livechat.LivechatButton()
//         this.il.send_message(this.il.message);
//     }
// })

})
