# -*- coding: utf-8 -*-
{
    'name': "Material Management",

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
    'depends': ['base', 'product', 'sale', 'personal_center', 'cpo_offer_base'],

    # always loaded
    'data': [
        'security/security_material.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/inherit_personal_center_views.xml',
        'wizard/wizard_gift_views.xml',
    ],
    # only loaded in demonstration mode
}