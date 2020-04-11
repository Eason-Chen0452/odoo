# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.website_portal.controllers.main import website_account, get_records_pager

class website_account(website_account):

    # Personal Material (个人中心物料管理)
    @http.route(['/my/material', '/my/material/page/<int:page>'], type='http', auth="user", website=True)
    def cpo_my_personal_material(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):

        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        get_obj = request.env['personal.center'].sudo()
        get_vlaues = get_obj.get_partner(partner)
        values.update({
            'express_no': None,
            'date': date_begin,
            'quotations': None,
            'page_name': 'my material',
            'pager': None,
            'archive_groups': None,
            'default_url': '/my/material',
            'sortby': sortby,
        })

        return request.render("website_cpo_personal_center.cpo_personal_material_warehouse", values)

# class WebsiteCpoPersonalCenter(http.Controller):
#     @http.route('/website_cpo_personal_center/website_cpo_personal_center/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/website_cpo_personal_center/website_cpo_personal_center/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('website_cpo_personal_center.listing', {
#             'root': '/website_cpo_personal_center/website_cpo_personal_center',
#             'objects': http.request.env['website_cpo_personal_center.website_cpo_personal_center'].search([]),
#         })

#     @http.route('/website_cpo_personal_center/website_cpo_personal_center/objects/<model("website_cpo_personal_center.website_cpo_personal_center"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('website_cpo_personal_center.object', {
#             'object': obj
#         })