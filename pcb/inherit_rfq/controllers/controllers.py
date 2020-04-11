# -*- coding: utf-8 -*-
from odoo import http, _
from odoo.http import request
from odoo.addons.website_payment.controllers.main import WebsitePayment as Payment
from odoo.addons.sale_pcb_rfq.controllers.main import AdditionalCost


class InheritPayment(Payment):

    @http.route()
    def confirm(self, **kw):
        tx_id = request.env['payment.transaction'].sudo().browse(request.session.get('website_payment_tx_id') or False)
        if tx_id.state == 'done' and not request.env['sale.order'].sudo().GetReview():
            x_str = tx_id.reference.encode('utf-8')
            x_str = x_str if 'x' not in x_str else x_str[:x_str.index('x')]
            x_id = request.env['account.invoice'].sudo().search([('number', '=', x_str)])
            request.env['account.payment'].sudo()._create_register_payment(x_id)
        return super(InheritPayment, self).confirm(**kw)

    # 直接付款
    def get_website_payment(self, order_id):
        if len(order_id) > 1:
            return False
        order = request.env['sale.order'].sudo().browse(order_id)
        if order.ProductName() and not order.GetReview():
            country_id = str(request.env.user.country_id.id)
            amount = float(order.invoice_ids.amount_total)
            currency_id = str(order.currency_id.id)
            reference = order.invoice_ids.number
            x_str = 'reference=' + reference + '&amount=' + str(amount) + '&currency_id=' + currency_id + '&country_id=' + country_id
            return request.redirect('/website_payment/pay?%s' % x_str)
        return False

    @http.route(['/website_payment/pay'], type='http', auth='public', website=True)
    def pay(self, reference='', amount=False, currency_id=None, acquirer_id=None, **kw):
        env = request.env
        user = env.user.sudo()
        currency_id = currency_id and int(currency_id) or user.company_id.currency_id.id
        currency = env['res.currency'].browse(currency_id)
        # Try default one then fallback on first
        acquirer_id = acquirer_id and int(acquirer_id) or env['ir.values'].get_default('payment.transaction', 'acquirer_id', company_id=user.company_id.id) or \
                      env['payment.acquirer'].search([('website_published', '=', True), ('company_id', '=', user.company_id.id)])[0].id
        acquirer = env['payment.acquirer'].with_context(submit_class='btn btn-primary pull-right', submit_txt=_('Pay Now')).browse(acquirer_id)
        # auto-increment reference with a number suffix if the reference already exists
        discount = self.search_sale_order(reference)
        reference = request.env['payment.transaction'].get_next_reference(reference)
        partner_id = user.partner_id.id if user.partner_id.id != request.website.partner_id.id else False
        payment_form = acquirer.sudo().render(reference, float(amount), currency.id, values={'return_url': '/website_payment/confirm', 'partner_id': partner_id})
        values = {
            'reference': reference,
            'acquirer': acquirer,
            'currency': currency,
            'amount': float(amount),
            'payment_form': payment_form,
            'discount': discount,
        }
        return request.render('website_payment.pay', values)

    def search_sale_order(self, reference):
        account = request.env['account.invoice'].search([('number', '=', reference)])
        return account.sale_order_id.discount_total


class InheritAdditionalCost(AdditionalCost):

    def create_email_notice(self, order, inv):
        request.env['automatically.send.order'].sudo().create({'order_id': order.id, 'invoice_id': inv.id})
        return super(InheritAdditionalCost, self).create_email_notice(order, inv)
