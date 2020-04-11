# -*- coding: utf-8 -*-

from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    def _compute_price(self):
        super(AccountInvoiceLine, self)._compute_price()
        for inv_line in self:
            for x_id in inv_line.sale_line_ids:
                inv_line.update({'price_subtotal': x_id.price_subtotal})
                # self.price_subtotal = self.sale_line_ids.price_subtotal
