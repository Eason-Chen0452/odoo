# -*- coding: utf-8 -*-
{
    'name': "website_sale_rfq",

    'summary': """Link sale_pcb_rfq and website_cpo_sale""",

    'description': """
        Link sale_pcb_rfq and website_cpo_sale
    """,

    'author': "Eason Chen",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['website_cpo_sale', 'sale_pcb_rfq', 'sales_team'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/template.xml',
    ],
    'auto_install': True,
}