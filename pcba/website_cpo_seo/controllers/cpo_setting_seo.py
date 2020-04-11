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
from odoo import http, api
from odoo import fields
from odoo.http import request
from odoo.osv.orm import browse_record
from odoo.exceptions import AccessError

from odoo.addons.website.models.website import slug
from odoo.addons.web.controllers.main import WebClient, Binary, Home

logger = logging.getLogger(__name__)

class Website(Home):


    @http.route('/page/<page:page>', type='http', auth="public", website=True, cache=300)
    def page(self, page, **opt):
        values = {
            'path': page,
            'deletable': True,  # used to add 'delete this page' in content menu
        }
        # /page/website.XXX --> /page/XXX
        if page.startswith('website.'):
            return request.redirect('/page/%s?%s' % (page[8:], request.httprequest.query_string), code=301)
        elif '.' not in page:
            page = 'website.%s' % page

        try:
            request.website.get_template(page)
        except ValueError as e:
            # page not found
            if request.website.is_publisher():
                values.pop('deletable')
                page = 'website.page_404'
            else:
                return request.env['ir.http']._handle_exception(e, 404)
        values = self.get_seo_data(values)

        return request.render(page, values)

    @api.multi
    def get_seo_data(self, values):
        # set_seo_data = request.env['cpo_set_website_seo'].sudo().search([])
        try:
            get_all_data = request.env['cpo.sitemap.url'].sudo().search([])
            page = values.get('path')
            if 'homepage' == page:
                page = '/'
            elif 'contactus' == page:
                page = '/page/contactus'

            for res in get_all_data:
                # if res.url in page:
                if page == res.url:
                    values['title'] = res.title
                    values['website_meta_keywords'] = res.keywords
                    values['website_meta_description'] = res.description
        except Exception, e:
            request.redirect('website.404')

        return values

