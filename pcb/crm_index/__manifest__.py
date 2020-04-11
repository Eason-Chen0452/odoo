# -*- coding: utf-8 -*-
{
    'name': "CRM Index",

    'summary': """
        Organize website trial price records, traffic sources, session""",

    'description': """
        Organize website trial price records, traffic sources, session
    """,

    'author': "Eason Chen",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'website_cpo_index', 'crm_msa', 'personal_center'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        # 'views/views.xml',
        'views/inherit_index.xml',
        # 'data/AutomaticProcessFunction.xml',
    ],

}