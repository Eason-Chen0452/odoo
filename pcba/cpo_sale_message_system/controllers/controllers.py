# -*- coding: utf-8 -*-
from odoo import http
from odoo.addons.website_cpo_sale.controllers.main import CPOwebsite_account
import pytz
import werkzeug
import urlparse
from odoo import http, tools, _
from odoo.http import request


class WebsiteCpoDependent(CPOwebsite_account):

    def _get_web_message_list(self, uid=0, msg_id=False, reply=False):
        """
        继承函数修改，如果message没有安装，不会报错
        :param uid:
        :return:
        """
        msg_pool = request.env['message.center'].sudo()
        msg_unread_qty = msg_pool.GetWebMessage(uid, msg_id=msg_id, reply=reply)
        return msg_unread_qty
