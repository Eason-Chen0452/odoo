# -*- coding: utf-8 -*-

import logging
from odoo import models, fields, api, _
from urlparse import urljoin

_logger = logging.getLogger(__name__)


class SellerEmail(models.Model):
    _name = 'seller.email'
    _description = 'Seller Email'
    _order = 'id desc'

    name = fields.Char('Name')
    email = fields.Char('Email')
    user_id = fields.Many2one('res.users', 'Seller')
    commonly_used = fields.Boolean('Commonly Used')

    @api.onchange('user_id')
    def _onchange_users(self):
        if self.user_id:
            self.update({'name': self.user_id.name, 'email': self.user_id.email})


# 异步处理客户下单之后 进行邮件通知销售人员 - 往后要可以直接联系到销售员
class OrderNotice(models.Model):
    _name = 'order.notice'
    _description = 'Order Notice'
    _order = 'id desc'

    name = fields.Char('Client Name',readonly=True)
    order_number = fields.Char('Order Number', readonly=True)
    order_time = fields.Datetime('Order Time', readonly=True)
    product = fields.Char('Product Name', readonly=True)
    state = fields.Selection([('Has Been Sent', 'Has Been Sent'),
                              ('Not Sent Yet', 'Not Sent Yet')], index=True, readonly=True, string='Stats', default='Not Sent Yet')
    seller_ids = fields.Many2many('seller.email', string='Seller')

    # 创建通知
    def CreateNotice(self, data):
        seller = self.env['seller.email'].search([])
        user_ids = [x.user_id.id for x in seller]
        seller_ids = seller.filtered(lambda x: x.commonly_used is True).ids
        public_id = self.env.ref('base.user_root').id
        for x_id in data:
            value = {
                'name': x_id.partner_id.name,
                'order_number': x_id.name,
                'order_time': x_id.date_order,
                'product': x_id.product_name,
                'seller_ids': [(6, 0, seller_ids)]
            }
            if x_id.user_id.id != public_id and x_id.user_id.id in user_ids:
                seller_ids = seller.filtered(lambda x: x.commonly_used is True or x.user_id.id == x_id.user_id.id).ids
                value.update({'seller_ids': [(6, 0, seller_ids)]})
            self.create(value)
        return True

    # 执行邮件通知
    def ExecutiveNotice(self):
        data = self.search([('state', '=', 'Not Sent Yet')])
        if data:
            template = self.env.ref('sale_pcb_rfq.notice_sales_template')
            assert template._name == 'mail.template'
            for x_id in data:
                for user in x_id.seller_ids:
                    template.update({'email_to': user.email})
                    template.with_context(lang=self._context.get('lang')).send_mail(x_id.id, force_send=True, raise_exception=True)
                    _logger.info("Message has been sent to <%s>", user.email)
            data.write({'state': 'Has Been Sent'})
        return True

    def ExecutiveDelete(self):
        data = self.search([('state', '=', 'Has Been Sent')])
        if data:
            _logger.info("Delete data <%s>", data)
            data.unlink()
        return True


