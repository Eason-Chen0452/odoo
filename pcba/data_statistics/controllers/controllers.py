# -*- coding: utf-8 -*-
from odoo import http

# class DataStatistics(http.Controller):
#     @http.route('/data_statistics/data_statistics/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/data_statistics/data_statistics/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('data_statistics.listing', {
#             'root': '/data_statistics/data_statistics',
#             'objects': http.request.env['data_statistics.data_statistics'].search([]),
#         })

#     @http.route('/data_statistics/data_statistics/objects/<model("data_statistics.data_statistics"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('data_statistics.object', {
#             'object': obj
#         })