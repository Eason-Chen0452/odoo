# -*- coding: utf-8 -*-

from odoo import models, fields, api


class InheritSaleConfigSettings(models.TransientModel):
    _inherit = 'sale.config.settings'

    @api.model
    def _default_sale_review(self):
        x_id = self.search([])
        if not x_id:
            return True
        return x_id[-1].review_bool

    review_bool = fields.Boolean('Whether to review', default=_default_sale_review)


class InheritSaleOrderRFQ(models.Model):
    _inherit = 'sale.order'

    def GetReview(self):
        x_id = self.env['sale.config.settings'].search([])
        if not x_id:  # 没有 就默认审核
            return True
        return x_id[-1].review_bool

    def ProductName(self):
        if self.product_type == 'PCBA':
            return False
        return True

    @api.one
    @api.multi
    def write(self, vals):
        res = super(InheritSaleOrderRFQ, self).write(vals)
        # PCBA 一定审核
        if vals.get('state') == 'wait_confirm' and self.ProductName() and not self.GetReview():
            self.action_confirm()  # 确认订单
            invoice_list = self.action_invoice_create()  # 创建发票
            self.env['account.invoice'].browse(invoice_list).action_invoice_open()  # 验证发票
            self.write({'calculate_bool': True})  # 打开发送邮件按钮
            self.env['automatically.send.order'].create({'order_id': self.id, 'invoice_id': invoice_list[0]})
        return res


class InheritAccountPayment(models.Model):
    _inherit = 'account.payment'

    def _create_register_payment(self, x_id, writeoff_acc=None):
        payment_type = x_id.type in ('out_invoice', 'in_refund') and 'inbound' or 'outbound'
        if payment_type == 'inbound':
            payment_method = self.env.ref('account.account_payment_method_manual_in')
        else:
            payment_method = self.env.ref('account.account_payment_method_manual_out')
        value = {
            'invoice_ids': [(6, 0, [x_id.id])],
            'amount': x_id.amount_total,
            'communication': x_id.number,
            'currency_id': x_id.currency_id.id,
            'journal_id': x_id.journal_id.id,
            'partner_id': x_id.partner_id.id,
            'partner_type': x_id.type in ('out_invoice', 'out_refund') and 'customer' or 'supplier',
            'payment_date': fields.Date.context_today(self),
            'payment_difference_handling': writeoff_acc and 'reconcile' or 'open',
            'payment_method_id': payment_method.id,
            'payment_token_id': False,
            'payment_type': payment_type,
            'writeoff_account_id': writeoff_acc and writeoff_acc.id or False,
            'writeoff_label': 'Write-Off'
        }
        payment = self.create(value)
        payment.post()

        return True


class SaleOrderAutomaticallySendMail(models.Model):
    _name = 'automatically.send.order'
    _description = 'Automatically Send Quotation Order'
    _order = 'id desc'

    order_id = fields.Many2one('sale.order', 'Sale Order')
    invoice_id = fields.Many2one('account.invoice', 'Invoice')
    state = fields.Selection([('Yes', 'Yes'), ('No', 'No')], default='No', string='Status', index=True)

    @api.model
    def SendQuotationOrInvoice(self):
        data = self.search([('state', '=', 'No')], limit=10)
        quotation = self.env.ref('sale.email_template_edi_sale')
        invoice = self.env.ref('account.email_template_edi_invoice')
        assert quotation._name == 'mail.template'
        assert invoice._name == 'mail.template'
        for x_id in data:
            order_id = x_id.order_id.id
            invoice_id = x_id.invoice_id.id
            quotation.with_context(lang=self._context.get('lang')).send_mail(order_id, force_send=True, raise_exception=True)
            invoice.with_context(lang=self._context.get('lang')).send_mail(invoice_id, force_send=True, raise_exception=True)
        if data:
            data.write({'state': 'Yes'})
        return True

    @api.model
    def DeleteOutgoingMail(self):
        data = self.search([('state', '=', 'Yes')])
        if data:
            data.unlink()
        return True




