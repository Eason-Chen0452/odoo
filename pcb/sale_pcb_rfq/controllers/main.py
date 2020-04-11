# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
import logging
from base64 import b64decode as d64

_logger = logging.getLogger(__name__)


# 此路由用于加收费触发的
class AdditionalCost(http.Controller):

    @http.route('/email/additional', type='http', auth='public', website=True)
    def email_markup(self, **kw):
        if kw.get('token'):
            order_id = kw.get('token')[4:-4]
            order = int(d64(order_id))
            order = request.env['sale.order'].sudo().browse(order)
            # 如果有已支付 或 已验证 的发票直接跳 个人中心
            inv = order.invoice_ids.filtered(lambda x: x.state in ['paid', 'open'])
            if inv:
                return request.redirect('/my/home')
            if order.state != 'sale':
                order.write({'state': 'sale'})
            inv = order.invoice_ids.filtered(lambda x: x.state != 'cancel')
            # 如果没有发票进行 创建
            if not inv:
                inv = order.action_invoice_create()  # 创建发票
                inv = request.env['account.invoice'].sudo().browse(inv)
                inv.write({'user_id': order.user_id.id})
            self.create_email_notice(order, inv)
            inv.action_invoice_open()  # 验证发票
            _logger.info('Client %s agree to increase cost' % order.name)
        return request.redirect('/my/home')

    # 用于别处地方函数的重写 - 不得删除
    def create_email_notice(self, order, inv):
        return False


