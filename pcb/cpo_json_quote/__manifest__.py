# -*- coding: utf-8 -*-
{
    'name': "Json Api Quote PCB&PCBA",

    'summary': """
        Json Api Quote PCB&PCBA""",

    'description': """
        Json Api Quote PCB&PCBA
    """,

    'author': "Eason Chen",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale_pcb_rfq', 'cpo_offer_base'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
    ],
}