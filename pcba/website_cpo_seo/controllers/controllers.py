# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import datetime
from itertools import islice
import json
import xml.etree.ElementTree as ET
import logging
import re
import urllib2
import werkzeug.utils
import werkzeug.wrappers

import odoo
from odoo import http
from odoo import fields
from odoo.http import request
from odoo.osv.orm import browse_record
from odoo.exceptions import AccessError

from odoo.addons.website.models.website import slug
from odoo.addons.web.controllers.main import WebClient, Binary, Home

# class WebsiteCpoSeo(http.Controller):
#
#     @http.route('/getapi', type='json', auth='public', csrf=False, website=True)
#     def cpo_get_api(self, **kw):
#         a = "Success"
#         print a
#         return a












#     @http.route('/website_cpo_seo/website_cpo_seo/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/website_cpo_seo/website_cpo_seo/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('website_cpo_seo.listing', {
#             'root': '/website_cpo_seo/website_cpo_seo',
#             'objects': http.request.env['website_cpo_seo.website_cpo_seo'].search([]),
#         })

#     @http.route('/website_cpo_seo/website_cpo_seo/objects/<model("website_cpo_seo.website_cpo_seo"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('website_cpo_seo.object', {
#             'object': obj
#         })