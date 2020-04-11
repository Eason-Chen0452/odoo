# -*- coding: utf-8 -*-
{
    'name': "ProductFlow",

    'summary': """Feedback Product Flow""",

    'description': """
        Feedback Product Flow
    """,

    'author': "Eason Chen",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'sale_pcb_rfq', 'mail', 'personal_center'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'data/product_flow_email_data.xml',
        'views/views.xml',
        'wizard/product_flow_message_wizard.xml',
    ],
}