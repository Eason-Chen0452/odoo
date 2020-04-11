# -*- coding: utf-8 -*-
{
    'name': "Order Scatter Process 10",

    'summary': """Distribute ICloudFactory sales orders; this is the version of odoo10""",

    'description': """
        Distribute ICloudFactory sales orders; this is the version of odoo10
    """,

    'author': "Eason Chen",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale_pcb_rfq', 'cpo_sale_allocations'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/receive_send_process.xml',
        'views/orders_process.xml',
        'data/process_rule_timer.xml',
    ],
}