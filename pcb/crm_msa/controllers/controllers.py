# -*- coding: utf-8 -*-

import logging, urllib, werkzeug
from base64 import b64decode as d64
from odoo import http, fields
from odoo.http import request
from odoo.addons.personal_center.controllers.controllers import ActivateAccount

_logger = logging.getLogger(__name__)


class MailTrack(http.Controller):

    @http.route('/crm/ordinary', type='http', auth='public', website=True)
    def OrdinaryConnection(self, **kw):
        value = urllib.unquote(kw.get('value'))
        value = d64(value[:17] + value[22:]).split('&')
        # 第一个值是网站, 第二个是mail.customer_email id
        url = urllib.unquote(value[0])
        if value[1] != 'False':
            line = request.env['mass_sales.mail.line'].sudo().browse(int(value[1]))
            click_ids = line.click_ids
            if line.read_bool:
                click_ids.create({'click_name': url, 'click_time': fields.datetime.now(), 'line_id': int(value[1])})
            else:
                mail = line.mail_id
                mail.write({'open_mail': mail.open_mail + 1})
                line.write({'receive_bool': True, 'state': 'Sent', 'read_bool': True})
                click_ids.create({'click_name': url, 'click_time': fields.datetime.now(), 'line_id': int(value[1])})
        if url in ['sales@chinapcbone.com', 'www.icloudfactory.com']:
            url = 'https://' + url
        elif url == 'http://113.116.72.54:8069/web#':
            url = 'https://www.icloudfactory.com'
        return werkzeug.utils.redirect(url)


# 客户注册后自动发送第一封营销邮件
class SignupEmail(ActivateAccount):

    @http.route()
    def web_email_verifictaion(self, *args, **kw):
        res = super(SignupEmail, self).web_email_verifictaion(*args, **kw)
        # view = request.env.ref('crm_msa.custom_text_1').sudo()
        # cen_id = request.env['personal.center'].sudo().search([('user_id', '=', request._uid)]).ids
        # request.env['mass_sales.mail'].sudo().create({
        #     'name': 'Welcome To Quoting On Our Online ICloudFactory',
        #     'email_type': 'Registered',
        #     'personal_ids': [(6, 0, cen_id)],
        #     'select_template': view.id,
        #     'state': 'Sending',
        #     'mail_content': view.message_text
        # })
        return res
