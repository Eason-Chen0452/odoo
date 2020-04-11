# -*- coding: utf-8 -*-

{
    'name': 'AliPay Payment Acquirer',
    'author': 'Reference Jarvis & Esaon Chen',
    'category': 'Accounting',
    'summary': 'Payment Acquirer: AliPay Implementation',
    'website':'http://www.yourcompany.com',
    'version': '1.0',
    'description': """
        AliPay Payment Acquirer Independent module to search documents and other people's code
    """,
    'depends': ['payment'],
    'external_dependencies': {
        'python': ['Crypto'],
        'bin': [],
    },
    'data': [
        'views/AliPayViews.xml',
        'views/AliPayTemplates.xml',
        # 'views/account_config_settings_views.xml',
        'data/AliPayData.xml',
    ],
    # 'installable': True,
}
