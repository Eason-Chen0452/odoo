# -*- coding: utf-8 -*-
{
    'name': "Sale RFQ Bom",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Eason Chen",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'cpo_offer_base', 'sale'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'data/bom_dashboard_data.xml',
    ],
}