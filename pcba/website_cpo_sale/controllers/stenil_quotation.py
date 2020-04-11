# -*- coding: utf-8 -*-
from odoo import http, tools, _
from odoo.http import request
from odoo.addons.website_cpo_seo.controllers.cpo_setting_seo import Website
from odoo.addons.website_cpo_index.controllers.cpo_quotation_record_code import CpoQuotationRecordCode
import logging

_logger = logging.getLogger(__name__)

class cpo_electron_WebsiteSale(http.Controller):

    @http.route([
        '/stencil',
        '/stencil?source=<val>'
    ], type='http', auth="public", website=True)
    def stencil(self, source=None, **post):
        try:
            product_tmp_id = request.env.ref("cam.cpo_product_template_Stencil").sudo().product_tmpl_id
            if not product_tmp_id.website_published:
                product_tmp_id.write({'website_published': True})
            values = {
                'source': source,
                'path': '/stencil',
                'product_id': product_tmp_id,
                'cpo_login': False
            }
            # 检查是否需要注册/登录才能报价
            try:
                CpoQuotationRecordCode().get_website_source()
                client_user_name = request.env.user.name
                login_regist = request.env['cpo_login_and_register'].get_login_and_register_ingo()
                if login_regist:
                    for lr in login_regist:
                        lr_boolean = lr.cpo_boolean
                        if lr_boolean and client_user_name == 'Public user':
                            values.update({
                                'cpo_login': True
                            })
                        break
                if values.get('cpo_login'):
                    return request.redirect("/web/login")
            except Exception, e:
                _logger.error("website_sale postprocess: %s value has been dropped (empty or not writable)" % e)
            if 'pcb_quantity' in post.keys():
                values.update({
                    'stencil_thickness': post.get('stencil_thickness'),
                    'cpo_stencil_size': post.get('cpo_stencil_size'),
                    'pcb_quantity': post.get('pcb_quantity'),
                })
            values = Website().get_seo_data(values)
            return request.render("website_cpo_sale.stencil_quotaion", values)
        except Exception, e:
            _logger.error("website_sale postprocess: %s value has been dropped (empty or not writable)" % e)
            return False


# class StentcilWebsiteSale(cpo_electron_WebsiteSale):
#
#     @http.route()
#     def stencil(self, source=None, **post):
#         try:
#             CpoQuotationRecordCode().get_website_source()
#         except Exception, e:
#             _logger.error("Error message: %s (empty or not writable)" % e)
#         return super(StentcilWebsiteSale, self).stencil(source=None, **post)




    # def get_seo_data(self, values):
    #     set_seo_data = request.env['cpo.sitemap.url'].sudo().search([])
    #     page = values.get('path')
    #     for res in set_seo_data:
    #         if res.cpo_page_name in page:
    #             values['title'] = res.cpo_title
    #             values['website_meta_keywords'] = res.cpo_keyworks
    #             values['website_meta_description'] = res.cpo_description
    #
    #     return values