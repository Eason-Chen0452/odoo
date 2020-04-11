# -*- coding: utf-8 -*-
from odoo import http

# class RedisClient(http.Controller):
#     @http.route('/redis_client/redis_client/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/redis_client/redis_client/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('redis_client.listing', {
#             'root': '/redis_client/redis_client',
#             'objects': http.request.env['redis_client.redis_client'].search([]),
#         })

#     @http.route('/redis_client/redis_client/objects/<model("redis_client.redis_client"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('redis_client.object', {
#             'object': obj
#         })