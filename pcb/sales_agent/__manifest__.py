# -*- coding: utf-8 -*-
{
    'name': "Regional Sales Agent",

    'summary': """Regional Sales Agent Module""",

    'description': """This module specializes in handling regional sales agent permissions issues""",

    'author': "Eason Chen",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'personal_center',
        'electron',
        'website_cpo_index',
        'cam',
        'sale_pcb_rfq',
        'sales_team',
        'sale',
        'product',
        'website_cpo_sale',
        'cpo_offer_base',
        'cpo_sale_allocations',
    ],

    # always loaded
    'data': [
        'security/sales_agent_security.xml',
        'security/ir.model.access.csv',
        'views/templates.xml',
        'views/views.xml',
        'views/sale_dashboard_crm_team.xml',
        # 'data/sale_dashboard_crm_team_data.xml',
    ],
}