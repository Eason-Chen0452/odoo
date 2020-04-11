# -*- coding: utf-8 -*-
from odoo import http

# class WebsiteCpoData(http.Controller):
#     @http.route('/website_cpo_data/website_cpo_data/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/website_cpo_data/website_cpo_data/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('website_cpo_data.listing', {
#             'root': '/website_cpo_data/website_cpo_data',
#             'objects': http.request.env['website_cpo_data.website_cpo_data'].search([]),
#         })

#     @http.route('/website_cpo_data/website_cpo_data/objects/<model("website_cpo_data.website_cpo_data"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('website_cpo_data.object', {
#             'object': obj
#         })