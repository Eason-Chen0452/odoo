odoo.define("website_cpo_sale.tour.website_cpo_ele_index", function (require) {
    "use strict";

    var core = require("web.core");
    var tour = require("web_tour.tour");
    var base = require("web_editor.base");

    var _t = core._t;

    tour.register("website_cpo_ele_index", {
        url: "/",
        wait_for: base.ready(),
    }, [
    //tour.STEPS.WEBSITE_NEW_PAGE,
    {
        trigger: "a[class=cpo_panel_btn]",
        content: _t("Click <b>PCBA Button</b> to get a pcba Quotation."),
        position: "bottom",
    }]);

});

odoo.define("website_cpo_sale.tour.website_cpo_ele_pcba", function (require) {
    "use strict";

    var core = require("web.core");
    var tour = require("web_tour.tour");
    var base = require("web_editor.base");

    var _t = core._t;

    tour.register("website_cpo_ele_pcba", {
        url: "/pcba",
        wait_for: base.ready(),
    }, [{
        trigger: "input[class='form-control shuliang']",
        content: _t("Input <b>Product Quantity</b>."),
        position: "bottom",
    },{
        trigger: "input[class='form-control wel_com']",
        content: _t("Input <b>DIP through hole quantity</b>."),
        position: "bottom",
    
    },{
        trigger: "input[class='form-control smt_num']",
        content: _t("Input <b>SMT parts quantity</b>."),
        position: "bottom",
    
    }
    ]);
});
odoo.define("website_cpo_sale.tour.cpo_shop_product", function (require) {
    "use strict";

    var core = require("web.core");
    var tour = require("web_tour.tour");
    var base = require("web_editor.base");

    var _t = core._t;

    tour.register("cpo_shop_product", {
        url: "/shop/product/pcba-*",
        wait_for: base.ready(),
    }, [{
        trigger: "a[id=add_to_cart]",
        content: _t("Click <b>Add to Cart</b> Button."),
        position: "bottom",
    }]);
});
odoo.define("website_cpo_sale.tour.cpo_shop_cart", function (require) {
    "use strict";

    var core = require("web.core");
    var tour = require("web_tour.tour");
    var base = require("web_editor.base");

    var _t = core._t;

    tour.register("cpo_shop_cart", {
        url: "/shop/cart",
        wait_for: base.ready(),
    }, [{
        trigger: "a[class='btn btn-primary oe_electron_js_upload upload_btn']",
        content: _t("Click <b>Upload</b> Button to Upload attachment file."),
        position: "bottom",
    },{
        trigger: "button[id=check_file_atta]",
        content: _t("Click <b>Check</b> Button to Setup Bom File Header ref."),
        position: "bottom",
    
    },{
        trigger: "input[class='ele_cart_checke_input check_style']",
        content: _t("Click <b>Checkbox</b> select and confirm order."),
        position: "bottom",
    
    },{
        trigger: "a[id=process_checkout]",
        content: _t("Click <b>Process Checkout</b> Confim order of carts."),
        position: "bottom",
    
    }
    ]);
});
odoo.define("website_cpo_sale.tour.cpo_shop_checkout", function (require) {
    "use strict";

    var core = require("web.core");
    var tour = require("web_tour.tour");
    var base = require("web_editor.base");

    var _t = core._t;

    tour.register("cpo_shop_checkout", {
        url: "/shop/checkout",
        wait_for: base.ready(),
    }, [{
        trigger: "a[href='/shop/confirm_order']",
        content: _t("Click <b>Confirm</b> Button to finish order."),
        position: "bottom",
    }]);
});
