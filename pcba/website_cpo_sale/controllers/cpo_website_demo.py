# -*- coding: utf-8 -*-
from odoo import http, tools, _
from odoo.http import request

class cpo_website_demo_WebsiteSale(http.Controller):

    @http.route(['/website/cpo_demo/json'], type='json', auth='public', website=True)
    def cpo_website_demo_get_json(self, **kw):
        res = []
        data = request.env['cpo.website.demo'].sudo().search([])
        for row in data:
            res.append({
                'class':row.class_code,
                'content':row.body_html
            })
        return res
