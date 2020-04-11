{
    'name': "website_cpo_advertising",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'cpo_offer_base'],

    # always loaded
    'data': [
        'security/advertising_security.xml',
        'security/ir.model.access.csv',
        # 'views/views.xml',
        'views/templates.xml',
        'views/cpo_advertising_view.xml',
        'views/cpo_page_advertising_view.xml',
        'views/cpo_notification_view.xml',
        # 'views/cpo_product_release_view.xml',
        # 'views/cpo_new_list_view.xml',
        # 'views/cpo_new_list_template.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
        # 'demo/cpo_pcb_online_data.xml',
        # 'demo/cpo_website_news_demo.xml',
    ],
}
# -*- coding: utf-8 -*-
