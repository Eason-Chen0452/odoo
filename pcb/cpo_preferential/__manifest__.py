# -*- coding: utf-8 -*-
{
    'name': "Sale Preferential",

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
    'depends': ['base', 'cam', 'sale'],

    # always loaded
    'data': [
        'security/preferential_security.xml',
        'security/ir.model.access.csv',
        'views/preferential_customer_contact_views.xml',
        'views/preferential_time_and_money_views.xml',
        # 'views/cash_coupons_views.xml',
        'views/inherit_sale_order.xml',
        # 'views/preferential_time_and_money_workflow_views.xml',
        # 'wizard/wizard_data_analysis.xml',
    ],
    'auto_install': True,
}
