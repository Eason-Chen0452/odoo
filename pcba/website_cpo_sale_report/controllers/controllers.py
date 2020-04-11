# -*- coding: utf-8 -*-
from odoo import http

# class WebsiteCpoSaleReport(http.Controller):
#     @http.route('/website_cpo_sale_report/website_cpo_sale_report/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/website_cpo_sale_report/website_cpo_sale_report/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('website_cpo_sale_report.listing', {
#             'root': '/website_cpo_sale_report/website_cpo_sale_report',
#             'objects': http.request.env['website_cpo_sale_report.website_cpo_sale_report'].search([]),
#         })

#     @http.route('/website_cpo_sale_report/website_cpo_sale_report/objects/<model("website_cpo_sale_report.website_cpo_sale_report"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('website_cpo_sale_report.object', {
#             'object': obj
#         })