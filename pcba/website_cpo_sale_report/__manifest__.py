# -*- coding: utf-8 -*-
{
    'name': "website_cpo_sale_report",

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
    'depends': ['base', 'account', 'sale'],

    # always loaded
    'data': [
        #'report/inherit_stock_report_deliveryslip.xml',
        'report/inherit_sale_report.xml',
        'report/inherit_account_report_invoice.xml',
        'report/cpo_sale_pcb_and_pcba_order_report.xml',
        # 'report/cpo_stencil_report.xml',
        # 'report/cpo_inherit_account_new_invoice_template.xml',
        # 'report/cpo_account_invoice_report.xml',
        # 'report/cpo_test_report.xml',
        # 'security/ir.model.access.csv',
        #'views/views.xml',
        #'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        #'demo/demo.xml',
    ],
}
