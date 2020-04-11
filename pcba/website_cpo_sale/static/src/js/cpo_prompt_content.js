odoo.define("website_cpo_prompt.website_help_document", function(require) {
    "use strict";

    var Widget = require('web.Widget');
    var base = require('web_editor.base');
    var ajax = require("web.ajax");
    var core = require('web.core');
    var config = require("web.config");

    $().ready(function(){
        var website_help_pcb = $('#website_help_pcb');
        ajax.jsonRpc("/web/help", 'call')
        .then(function (data) {

        })
    })

})
 $().ready(function(){
    ajax.jsonRpc("/web/help", 'call')
    .then(function (data) {
        alert("aaa");
    })
});