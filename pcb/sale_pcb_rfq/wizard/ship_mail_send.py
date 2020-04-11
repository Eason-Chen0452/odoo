# -*- coding: utf-8 -*-

from odoo import api, models


class ShipMailSend(models.TransientModel):
    _inherit = 'mail.compose.message'

    @api.multi
    def send_mail(self, auto_commit=False):
        if self._context.get('default_model') == 'sale.order' and self._context.get('default_res_id') and self._context.get('mark_so_as_sent'):
            order = self.env['sale.order'].browse([self._context['default_res_id']])
            if order.state == 'wait_delivery':
                order.state = 'wait_receipt'
            self = self.with_context(mail_post_autofollow=True)
        return super(ShipMailSend, self).send_mail(auto_commit=auto_commit)
