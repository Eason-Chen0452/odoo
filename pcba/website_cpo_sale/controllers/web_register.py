# -*- coding: utf-8 -*-
from odoo import http, tools, _
from odoo.http import request
from odoo.addons.website_cpo_seo.controllers.cpo_setting_seo import Website
from odoo.addons.web.controllers.main import ensure_db, Home
from odoo.addons.auth_signup.models.res_users import SignupError
from odoo.addons.auth_signup.models.res_partner import SignupError, now
from odoo.addons.website.models.website import slug,unslug
import werkzeug
import base64
import logging

_logger = logging.getLogger(__name__)

# class cpo_register_WebsiteSale(http.Controller):
#
#     @http.route([
#         '/web/verification',
#     ], type='http', auth="public", website=True)
#     def web_verification(self, **post):
#         values = {}
#         signup = request.env['res.users'].Enrolment(post.get('login'), post.get('name'))
#         # 返回的bool值 False 说明这个账号已创建 或 存在
#         if not signup:
#             pass
#         mail_split = post.get('login').split('@')
#         mail_route = 'www.mail.'+str(mail_split[1])
#         mail_label = '<a href="'+mail_route+'" target="view_window">To verify</a>'
#         values.update({
#             'mail_route': mail_label,
#             'mail_route1': mail_route,
#         })
#         return request.render("website_cpo_sale.cpo_register_mail", values)


    # def ffff(self):
        # portal = self.env.ref('base.group_portal').id
        # subtotal = self.env.ref('sale.group_show_price_subtotal').id
        # address = self.env.ref('sale.group_delivery_invoice_address').id
        # user_data = {
        #     'login': post.get('login'),
        #     'name': post.get('name'),
        #     'email': post.get('login'),
        #     'groups_id': [(6, 0, [portal, subtotal, address])]
        # }

        # res_id = request.env['res.users'].sudo().create(user_data)
        # template = request.env.ref('auth_signup.set_password_email', raise_if_not_found=False)
        # cpo_mail = template.sudo().send_mail(res_id.id, force_send=True, raise_exception=True, email_values=None)