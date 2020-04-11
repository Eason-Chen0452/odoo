# -*- coding: utf-8 -*-
{
    'name': "Customer Personal Center",

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
    'depends': ['base', 'mail', 'sale'],

    # always loaded
    'data': [
        'security/security_center.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/activation_login_templates.xml',
        'data/mail_activation_template.xml',
    ],
}