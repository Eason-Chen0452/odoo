# -*- coding: utf-8 -*-
{
    'name': "PCB Price List",

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
    'depends': [
        'cam',
        'account',
        'sales_team'
    ],

    # always loaded
    'data': [
        # 'security/cpo_it_pcb_security.xml',
        'security/ir.model.access.csv',
        'views/cpo_it_pcb_main_table.xml',
        'views/views.xml',
        'views/increase_views.xml',
        'views/package_price_pcb_views.xml',
        'data/layer_class_data.xml',
        'data/craft_class_data.xml',
        'data/package_price_data.xml',
    ],

}