# -*- coding: utf-8 -*-
{
    'name': "Message system",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Charlie Chen",
    'website': "http://www.chinapcbone.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'personal_center', 'cpo_preferential', 'cpo_sale_allocations'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/cpo_message_view.xml',
        'views/template.xml',
    ],
    'auto_install': True,
}