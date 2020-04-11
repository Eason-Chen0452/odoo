{
    'name': 'PCB Computer Aided Manage',
    'version': '1.0',
    'sequence': 20,
    'category': 'CAM',
    'summary': 'Ink Color, Copper Base Type, Cam Check',
    'description': """
Manage CAM Check and other setup item about CAM
=================================================
The PCB Cam Managementsystem enables a group of people to intelligently and efficiently manage
cam, MI, Manufacture Process etc.
It manages key tasks such as communication, identification, prioritization,
assignment, resolution and notification.
""",
    'website': 'http://www.chinapcbone.com',
    'depends': [
        'product',
    ],
    'data': [
        'wizard/create_layer_size_price.xml',
        'wizard/create_ink_size_price.xml',
        'wizard/create_surface_process_size_price.xml',
        'wizard/create_special_material_size_price.xml',
        'wizard/create_special_process_size_price.xml',
        'data/ir_sequence_data.xml',
        'data/product_data.xml',
        'data/cam_data.xml',
        'data/cam_gold_finger_data.xml',
        'security/cam_security.xml',
        'security/ir.model.access.csv',
        'views/cam_view.xml',
        'views/product_view.xml',
        'views/increase_cam_views.xml',
        ],

    'css': ['static/src/css/cam.css'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

