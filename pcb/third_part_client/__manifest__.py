# -*- coding: utf-8 -*-
{
    'name': "Client Data Show",

    'summary': """
        This module deals with customer-related data issues in multiple models, 
        because there is no direct relationship between the modules themselves, 
        but for many reasons, this module is required to contact
    """,

    'description': """
        This module deals with customer-related data issues in multiple models, 
        because there is no direct relationship between the modules themselves, 
        but for many reasons, this module is required to contact
    """,

    'author': "Eason Chen",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['cpo_preferential', 'personal_center', 'website_sale_rfq'],
    'auto_install': True,
}