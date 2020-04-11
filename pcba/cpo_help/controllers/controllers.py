# -*- coding: utf-8 -*-
from odoo import http

# class CpoHelp(http.Controller):
#     @http.route('/cpo_help/cpo_help/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cpo_help/cpo_help/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('cpo_help.listing', {
#             'root': '/cpo_help/cpo_help',
#             'objects': http.request.env['cpo_help.cpo_help'].search([]),
#         })

#     @http.route('/cpo_help/cpo_help/objects/<model("cpo_help.cpo_help"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cpo_help.object', {
#             'object': obj
#         })