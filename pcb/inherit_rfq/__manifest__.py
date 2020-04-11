# -*- coding: utf-8 -*-
{
    'name': "Inherit RFQ",

    'summary': """
            Play some friendly functions
        """,

    'description': """
        Play some friendly functions
    """,

    'author': "Eason Chen",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sales_team', 'sale', 'sale_pcb_rfq', 'payment_paypal', 'payment'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/inherit_website_payment_templates.xml',
        'data/TimerActionData.xml',
    ],
    'auto_install': True,
}