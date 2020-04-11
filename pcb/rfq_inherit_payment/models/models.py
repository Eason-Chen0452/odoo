# -*- encoding: utf-8 -*-

from odoo import api, fields, models, _
from paypalrestsdk import Sale, Api


class InheritPaymentPalPay(models.Model):
    _inherit = 'payment.acquirer'

    paypal_api_client_id = fields.Char('Client ID', groups='base.group_user')
    paypal_api_client_secret = fields.Char('Client Secret', groups='base.group_user')
    bank_company_name = fields.Char('Company Name', group='base.group', default='Chinapcbone Technology Limited')
    bank_name = fields.Char('Bank Name', group='base.group', default='HSBC Hong Kong')
    bank_account_no = fields.Char('Account No', group='base.group', default='509 728275 838')
    bank_swift = fields.Char('SWIFT', group='base.group', default='HSBCHKHHHKH')
    bank_address = fields.Text('Bank Address', group='base.group')
    bank_company_address = fields.Text('Bank Name', group='base.group')
    provider = fields.Selection(selection_add=[('bank', 'Bank')])

    # 退款时调用 PayPal的退款接口
    @api.multi
    def paypal_api_refund(self, order, refund_amount=False):
        # 搜索出发票 支付过的一般来说 应该就只有一条
        invoice = order.invoice_ids.filtered(lambda x: x.state == 'paid')
        assert len(invoice) == 1, _('The inspection found that there were at least two paid invoices or the invoices were not paid for the order. The system could not identify which invoice was refunded.')
        txn = self.env['payment.transaction'].search([('reference', 'like', invoice.number)])
        txn = txn.filtered(lambda x: x.state == 'done')
        assert len(txn) == 1, _('Invoice number: "%s" Detected that payment has been made many times or has not been paid, the system cannot determine the serial number' % invoice.number)
        x_str = 'mode' if txn.acquirer_id.environment == 'prod' else 'sandbox'
        api = Api(mode=x_str, client_id=txn.acquirer_id.paypal_api_client_id, client_secret=txn.acquirer_id.paypal_api_client_secret)
        sale = Sale.find(txn.acquirer_reference, api=api)
        sale.refund({
            "amount": {
                "total": refund_amount if refund_amount else txn.amount,
                "currency": txn.currency_id.name
            }
        })
        return txn.acquirer_reference



