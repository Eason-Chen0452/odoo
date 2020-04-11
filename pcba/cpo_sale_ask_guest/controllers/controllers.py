# -*- coding: utf-8 -*-
from odoo import http
from odoo.addons.website_cpo_sale.controllers.main import CPOwebsite_account
import pytz
import werkzeug
import urlparse
from odoo import http, tools, _
from odoo.http import request


class CpoSaleAskGuest(CPOwebsite_account):

    def _get_web_eq_list(self, client_id, order_id=False, reply=False, ask_id=False, images=False):
        """
        继承函数修改，如果问客没有安装，不会报错
        :param uid:
        :return:
        """
        ask_pool = request.env['ask.guest'].sudo()
        ask_obj = ask_pool.GetAskGuestShow(client_id, order_id=order_id, reply=reply, ask_id=ask_id, images=images)
        return ask_obj
