# -*- coding: utf-8 -*-
{
    'name': "website_cpo_index",

    'summary': """
        Website feature settings, generating data from the background to the front end rendering!""",

    'description': """
        Website feature settings
    """,

    'author': "Charlie Chen",
    'website': "https://www.icloudfactory.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Website',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sales_team', 'personal_center'],

    # always loaded
    'data': [
        'security/cpo_operation_authority.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/cpo_package_price_view.xml',
        'views/cpo_new_list_view.xml',
        'views/cpo_new_list_template.xml',
        'views/cpo_banner_image_view.xml',
        'views/cpo_country_list_template.xml',
        'views/cpo_click_select_big_category.xml',
        'views/cpo_form_click_select_to_category.xml',
        'views/cpo_form_click_select_to_detailed.xml',
        'views/cpo_coupon_list_temp.xml',
        'views/cpo_annex_file_upload.xml',
        'views/cpo_coupon_centen_template.xml',
        'views/cpo_board_description_view.xml',
        'views/cpo_video_view.xml',
        'views/cpo_board_description_template.xml',
        'views/cpo_quotation_record.xml',
        'views/cpo_quotation_record_all.xml',
        'views/cpo_quotation_record_all_chart.xml',
        'views/cpo_advertage_products_view.xml',
        'views/cpo_pcba_condition_view.xml',
        'views/cpo_website_show_all_material.xml',
        'views/cpo_setting_cookie_duration_view.xml',
        'views/cpo_login_and_register_view.xml',
        'views/cpo_website_source_view.xml',
        'views/cpo_website_source_set_view.xml',
        # 'views/cpo_inherit_routing_parameter_view.xml',
        'demo/cpo_form_click_to_data.xml',
        'demo/cpo_board_description_data.xml',
        'data/cpo_pcba_package_data.xml',
        'data/cpo_page_data.xml',
    ],
    # only loaded in demonstration mode
    # 'images': ['static/src/images/layerimg/layer_1_2.jpg'],
    'demo': [
        'demo/demo.xml',
        # 'demo/cpo_pcb_online_data.xml',
        'demo/cpo_website_news_demo.xml',
    ],
}