# -*- coding: utf-8 -*-

import werkzeug, urllib, pprint, logging, json, requests
from odoo import http
from odoo.http import request
from ..models import func
from datetime import datetime

_logger = logging.getLogger(__name__)


class AlipayController(http.Controller):
    _notify_url = '/payment/alipay/ipn/'
    _return_url = '/payment/alipay/dpn/'

    def _get_return_url(self, **post):
        """ Extract the return URL from the data coming from alipay. """
        return_url = post.pop('return_url', '')
        if not return_url:
            custom = json.loads(urllib.unquote_plus(post.pop('custom', False) or post.pop('cm', False) or '{}'))
            # 暂时这么写死
            return_url = custom.get('return_url', '/website_payment/confirm')
        return return_url

    # 将返回的签名进行验证
    def VerificationSign(self, **post):
        ali = request.env['payment.acquirer'].sudo().search([('provider', '=', 'alipay')])
        signature = func.VerifySign(post, post.get('sign'), ali.alipay_public_key, ali.alipay_sign_type)
        return signature

    def getResponse(self, **post):
        ali = request.env['payment.transaction'].search([('reference', '=', str(post.get('out_trade_no')))])
        # 商家UID
        if post.get('seller_id') != ali.acquirer_id.alipay_partner:
            return False
        # 商家APP ID
        elif post.get('auth_app_id') != ali.acquirer_id.alipay_seller_id:
            return False
        value = {
            'app_id': str(post.get('auth_app_id')),
            'method': 'alipay.trade.query',
            'charset': 'utf-8',
            'sign_type': str(post.get('sign_type')),
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'version': str(post.get('version')),
            'biz_content': {
                'out_trade_no': str(post.get('out_trade_no')),
                'trade_no': str(post.get('trade_no')),
            }
        }
        sign = func.sign_data(value, ali.acquirer_id.alipay_private_key, str(post.get('sign_type')), check=True)
        ali_urls = request.env['payment.acquirer']._get_alipay_urls(ali and ali.acquirer_id.environment or 'prod')
        resp = requests.get(ali_urls.get('alipay_form_url') + sign).text
        post = json.loads(resp, encoding='utf-8')
        return dict(post.get('alipay_trade_query_response'))

    # 整理验证以及查询此交易是否成功
    def verify_data(self, **post):
        res = False
        if not post:
            return False
        verification = self.VerificationSign(**post)
        if not verification:
            return False
        value = self.getResponse(**post)
        if value.get('trade_status') == 'TRADE_SUCCESS':
            _logger.info('AliPay: validated data')
            post.pop('sign')
            res = request.env['payment.transaction'].sudo().form_feedback(dict(post, **value), 'alipay')
        elif value.get('trade_status') == 'TRADE_FINISHED':
            pass
        elif value.get('trade_status') == 'TRADE_CLOSED':
            pass
        return res

    @http.route('/payment/alipay/ipn/', type='http', auth="none", methods=['GET', 'POST'], csrf=False)
    def alipay_ipn(self, **post):
        """ Alipay IPN. PayPal在此路由也是404 模仿PayPal"""
        _logger.info('Beginning Alipay IPN form_feedback with post data %s', pprint.pformat(post))  # debug
        if self.verify_data(**post):
            return 'success'
        else:
            return 'fail'

    @http.route('/payment/alipay/dpn', type='http', auth="none", methods=['POST', 'GET'], csrf=False)
    def alipay_dpn(self, **post):
        """支付好后 首先是需要验证"""
        _logger.info('Beginning Alipay DPN form_feedback with post data %s', pprint.pformat(post))  # debug
        # 这里没有返回的设置的URL?!
        return_url = self._get_return_url(**post)
        # 进行验证
        if self.verify_data(**post):
            return werkzeug.utils.redirect(return_url)
        else:
            return "验证失败"

