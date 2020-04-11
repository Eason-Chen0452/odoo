{
    'name': "cpo_offer_base",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "ChinaPCBOne & Eason Chan",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'product', 'electron', 'mail', 'sale', 'sales_team', 'cam'],

    # always loaded
    'data': [
        'security/bom_security.xml',
        'security/ir.model.access.csv',
        'views/product_data.xml',
        'wizard/cpo_bom_table_head_views.xml',
        'wizard/cpo_bom_wizard_views.xml',
        'wizard/cpo_search_data_view.xml',
        'views/cpo_offer_bom_line_views.xml',
        'views/cpo_offer_bom_views.xml',
        'views/cpo_inherit_sale_order_views.xml',
        'views/cpo_smt_price_views.xml',
        'views/smt_package_views.xml',
        'views/smt_data.xml',
        'views/res_currency_view.xml',
        'views/templates.xml',
    ],

}
# -*- coding: utf-8 -*-
