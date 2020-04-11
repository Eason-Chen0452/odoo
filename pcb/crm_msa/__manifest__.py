# -*- coding: utf-8 -*-
{
    'name': "CRM Marketing Strategy Analysis",

    'summary': """CRM Marketing Strategy Analysis""",

    'description': """CRM Marketing Strategy Analysis""",

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
        'mail',
        # 'crm',
        # 'utm',
        # 'calendar',
        # 'sales_team',
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        # 'views/views.xml',
        'views/mass_sales_mail_views.xml',
        'views/crm_views.xml',
        # 'views/templates.xml',
        'data/mass_sales_email.xml',
        'data/custom_message_text_data.xml',
        # 'wizard/mass_sales_email_wizard.xml',

    ],

}