# -*- coding: utf-8 -*-
from odoo import http

# class CpoFunctionSetting(http.Controller):
#     @http.route('/cpo_function_setting/cpo_function_setting/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cpo_function_setting/cpo_function_setting/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('cpo_function_setting.listing', {
#             'root': '/cpo_function_setting/cpo_function_setting',
#             'objects': http.request.env['cpo_function_setting.cpo_function_setting'].search([]),
#         })

#     @http.route('/cpo_function_setting/cpo_function_setting/objects/<model("cpo_function_setting.cpo_function_setting"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cpo_function_setting.object', {
#             'object': obj
#         })