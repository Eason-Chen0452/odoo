# -*- coding: utf-8 -*-
{
    'name': 'Website Sitemap Filter',
	'summary': 'Remove unwanted URL from sitemap.xml',
    'version': '10.0',
    'author': 'Charles Chen',
	'website': 'https://chinapcbone.com',
	'support': 'charles.chen@chinapcbone.com.cn',
    'license': 'AGPL-3',
    'category': 'website',
    'depends': ['website'],
    "description": """
        Website SiteMap serve.
    """,
    'data': [
        'security/cpo_sitemap_filter.xml',
        'security/ir.model.access.csv',
        'views/res_config.xml',
        'views/sitemap.xml',
    ],
    'images': ['static/website_sitemap_filter.png'],
    'qweb': [],
    'installable': True,
    'auto_install': False,
}
