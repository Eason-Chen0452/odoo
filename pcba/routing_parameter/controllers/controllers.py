# -*- coding: utf-8 -*-
from odoo import http

# class RoutingParameter(http.Controller):
#     @http.route('/routing_parameter/routing_parameter/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/routing_parameter/routing_parameter/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('routing_parameter.listing', {
#             'root': '/routing_parameter/routing_parameter',
#             'objects': http.request.env['routing_parameter.routing_parameter'].search([]),
#         })

#     @http.route('/routing_parameter/routing_parameter/objects/<model("routing_parameter.routing_parameter"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('routing_parameter.object', {
#             'object': obj
#         })