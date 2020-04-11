# -*- coding: utf-8 -*-
{
    'name': "Sale Staff Assignments",

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
    'depends': ['base', 'sale', 'personal_center'],

    # always loaded
    'data': [
        'security/cpo_sale_allocations_security.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
    ],
    'auto_install': True,
}