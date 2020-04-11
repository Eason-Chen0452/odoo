# -*- coding: utf-8 -*-
from odoo import http

# class ModuleVersionManagement(http.Controller):
#     @http.route('/module_version_management/module_version_management/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/module_version_management/module_version_management/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('module_version_management.listing', {
#             'root': '/module_version_management/module_version_management',
#             'objects': http.request.env['module_version_management.module_version_management'].search([]),
#         })

#     @http.route('/module_version_management/module_version_management/objects/<model("module_version_management.module_version_management"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('module_version_management.object', {
#             'object': obj
#         })