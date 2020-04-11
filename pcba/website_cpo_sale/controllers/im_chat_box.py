# -*- coding: utf-8 -*-
from odoo import http,fields
from odoo.http import request
from odoo.addons.website_form.controllers.main import WebsiteForm

class WebsiteSale_CPO_imchat_box(WebsiteForm):
    @http.route('/get_imchat_box_temp', type='json', auth='public', website=True)
    def get_imchat_box_temp(self, **kw):
        return {'html': request.env['ir.ui.view'].render_template('website_cpo_sale.imchat_box',{
            'button_text':kw.get('button_text')
        })}
