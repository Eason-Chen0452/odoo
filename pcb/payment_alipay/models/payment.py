# coding: utf-8

import logging, urlparse, func, json
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from ..controllers.main import AlipayController
from datetime import datetime

_logger = logging.getLogger(__name__)


class AcquirerAlipay(models.Model):
    _inherit = 'payment.acquirer'

    provider = fields.Selection(selection_add=[('alipay', 'Alipay')])
    alipay_partner = fields.Char('Alipay Partner ID', required_if_provider="alipay", groups='base.group_user')
    alipay_seller_id = fields.Char('Alipay Seller ID', groups='base.group_user')
    alipay_private_key = fields.Text('Alipay Private KEY', groups='base.group_user')
    alipay_public_key = fields.Text('Alipay Public KEY', groups='base.group_user')
    alipay_sign_type = fields.Selection([('RSA', 'RSA'), ('RSA2', 'RSA2')], string='Sign Type', default='RSA2', groups='base.group_user')
    alipay_transport = fields.Selection([('https', 'HTTPS'), ('http', 'HTTP')], groups='base.group_user')
    # alipay_service = fields.Char('Service', required_if_provider="alipay", groups='base.group_user', default='create_direct_pay_by_user')
    # alipay_payment_type = fields.Char('Payment Type', groups='base.group_user', default='1')

    @api.model
    def _get_alipay_urls(self, environment):
        if environment == 'prod':
            return {
                'alipay_form_url': 'https://openapi.alipay.com/gateway.do?',
            }
        else:
            return {
                'alipay_form_url': 'https://openapi.alipaydev.com/gateway.do?',
            }

    @api.multi
    # 是否加收手续费
    def alipay_compute_fees(self, amount, currency_id, country_id):
        if not self.fees_active:
            return 0.0
        country = self.env['res.country'].browse(country_id)
        if country and self.company_id.country_id.id == country.id:
            percentage = self.fees_dom_var
            fixed = self.fees_dom_fixed
        else:
            percentage = self.fees_int_var
            fixed = self.fees_int_fixed
        fees = (percentage / 100.0 * amount + fixed) / (1 - percentage / 100.0)
        return fees

    @api.multi
    def alipay_form_generate_values(self, values):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        biz_content = {
            'subject': '%s:%s' % (str(self.company_id.name), str(values['reference'])),
            'out_trade_no': str(values['reference']),
            'total_amount': values['amount'],
            'product_code': 'FAST_INSTANT_TRADE_PAY'
        }
        tx_values = {
            "method": "alipay.trade.page.pay",
            "return_url": '%s' % urlparse.urljoin(base_url, AlipayController._return_url),
            "notify_url": '%s' % urlparse.urljoin(base_url, AlipayController._notify_url),
            "app_id": self.alipay_seller_id,
            "charset": "UTF-8",
            "sign_type": self.alipay_sign_type,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "version": "1.0",
            "biz_content": biz_content,
        }
        sign = func.sign_data(tx_values, self.alipay_private_key, self.alipay_sign_type)
        tx_values.update({'sign': sign, 'biz_content': json.dumps(biz_content, separators=(',', ':'))})
        return dict(values, **tx_values)

    @api.multi
    def alipay_get_form_action_url(self):
        return self._get_alipay_urls(self.environment)['alipay_form_url']


class TxAlipay(models.Model):
    _inherit = 'payment.transaction'

    alipay_txn_type = fields.Char('Transaction type')

    # --------------------------------------------------
    # FORM RELATED METHODS
    # --------------------------------------------------

    @api.model
    def _alipay_form_get_tx_from_data(self, data):
        reference, txn_id = data.get('out_trade_no'), data.get('trade_no')
        if not reference or not txn_id:
            error_msg = _('Alipay: received data with missing reference (%s) or txn_id (%s)') % (reference, txn_id)
            _logger.info(error_msg)
            raise ValidationError(error_msg)

        # find tx -> @TDENOTE use txn_id ?
        txs = self.env['payment.transaction'].search([('reference', '=', reference)])
        if not txs or len(txs) > 1:
            error_msg = 'Alipay: received data for reference %s' % (reference)
            if not txs:
                error_msg += '; no order found'
            else:
                error_msg += '; multiple order found'
            _logger.info(error_msg)
            raise ValidationError(error_msg)
        return txs[0]

    @api.multi
    def _alipay_form_get_invalid_parameters(self, data):
        invalid_parameters = []
        _logger.info('Receive payment information notification from Alipay: %s', data.get('trade_status'))
        # TODO: txn_id: shoudl be false at draft, set afterwards, and verified with txn details
        pass
        return invalid_parameters

    @api.multi
    def _alipay_form_validate(self, data):
        status = data.get('trade_status')
        res = {
            # 'acquirer_reference': data.get('out_trade_no'),
            'alipay_txn_type': data.get('payment_type'),
            'acquirer_reference':data.get('trade_no'),
            'partner_reference': data.get('buyer_id')
        }
        if status in ['TRADE_FINISHED', 'TRADE_SUCCESS']:
            _logger.info('Validated alipay payment for tx %s: set as done' % (self.reference))
            res.update(state='done', date_validate=data.get('gmt_payment', fields.datetime.now()))
            return self.write(res)
        else:
            error = 'Received unrecognized status for Alipay payment %s: %s, set as error' % (self.reference, status)
            _logger.info(error)
            res.update(state='error', state_message=error)
            return self.write(res)
