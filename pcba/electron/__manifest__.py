# -*- coding: utf-8 -*-
{
    'name': "electron",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','website', 'product', 'stock'],

    # always loaded
    'data': [
        'security/security_view.xml',
        'security/ir.model.access.csv',
        'data/electron_type_code_rel.xml',
        'data/auto_check.xml',
        'views/views.xml',
        #'views/style_view.xml',
        'views/templates.xml',
        'views/electronic_view.xml',
        'views/electronic_base_view.xml',
        # 'views/electronic_resistance_view.xml',
        'views/electronic_relation.xml',
        'wizard/update_electron_update_field_sequence.xml',
        'views/product.xml',
        'views/res_partner.xml',
        #'views/electron_semi_conductor_view.xml',
        #'views/electronic_capacitor_view.xml',
        #'views/electronic_potentiometer_view.xml',
        #'views/electronic_filters_view.xml',
        ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
