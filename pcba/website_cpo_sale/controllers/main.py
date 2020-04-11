# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import json
import logging
import cStringIO
import xlrd,base64
from werkzeug.exceptions import Forbidden
import pytz
import werkzeug
import urlparse
from odoo import http, tools, _
from odoo.http import request
from odoo.addons.base.ir.ir_qweb.fields import nl2br
from odoo.addons.website.models.website import slug,unslug
from odoo.addons.website.controllers.main import QueryURL
from odoo.exceptions import ValidationError,AccessError
from odoo.addons.website_form.controllers.main import WebsiteForm
from odoo.addons.website_sale.controllers.main import WebsiteSale
import re, string, random
from  decimal import Decimal
from  decimal import getcontext
from ..models.sale_order import ELECTRON_FILE_TYPE,PCB_ELECTRON_FILE_TYPE,PCBA_ELECTRON_FILE_TYPE
from odoo.addons.cpo_offer_base.models.cpo_offer_bom import get_digi_data,recheck_bom_file_content
from odoo.addons.website_portal.controllers.main import website_account, get_records_pager
from odoo.addons.cpo_offer_base.models.ir_mail_server import ORDER_TYPE_PCB,ORDER_TYPE_PCBA
from odoo.addons.website_cpo_seo.controllers.cpo_setting_seo import Website
from odoo.addons.website_cpo_index.controllers import cpo_quotation_record_code
from odoo.addons.website_cpo_index.controllers.cpo_quotation_record_code import CpoQuotationRecordCode
from odoo.addons.web.controllers import main
from odoo.addons.inherit_rfq.controllers.controllers import InheritPayment
import math
from odoo.tools import ustr, pycompat

_logger = logging.getLogger(__name__)


def cpo_mark():
    """
    获取随机的五位数
    :return:
    """
    cpo_chr = string.letters + string.digits
    random_str = ''.join(random.choice(cpo_chr) for x in range(5))
    return random_str


class CPOwebsite_account(website_account):


    def _prepare_portal_layout_values(self):
        values = super(CPOwebsite_account, self)._prepare_portal_layout_values()
        partner = request.env.user.partner_id

        SaleOrder = request.env['sale.order']
        Invoice = request.env['account.invoice']
        # quotation_count = SaleOrder.search_count([
        #     ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
        #     ('state', 'in', ['sent', 'cancel'])
        # ])
        quotation_count = False
        order_count = SaleOrder.sudo().search_count([
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('state', 'in', ['sale', 'done'])
        ])
        invoice_count = Invoice.sudo().search_count([
            ('type', 'in', ['out_invoice', 'out_refund']),
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('state', 'in', ['open', 'paid', 'cancel'])
        ])

        wait_count = SaleOrder.sudo().search_count([
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('state', 'in', ['wait_confirm'])
        ])

        values.update({
            'quotation_count': quotation_count,
            'order_count': order_count,
            'wait_count': wait_count,
            'invoice_count': invoice_count,
        })
        return values

    def _my_account_all_data(self):
        values = super(CPOwebsite_account, self)._prepare_portal_layout_values()
        partner = request.env.user.partner_id

        SaleOrder = request.env['sale.order']
        Invoice = request.env['account.invoice']

        order_qty = SaleOrder.sudo().search([
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('state', 'in', ['sale', 'done'])
        ])
        invoice_qty = Invoice.sudo().search([
            ('type', 'in', ['out_invoice', 'out_refund']),
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('state', 'in', ['open', 'paid', 'cancel'])
        ])

        wait_qty = SaleOrder.sudo().search([
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('state', 'in', ['wait_confirm'])
        ])

        values.update({
            'order_qty': order_qty,
            'invoice_qty': invoice_qty,
            'wait_qty': wait_qty,
        })
        return values

    def _tz_get(self):
        # put POSIX 'Etc/*' entries at the end to avoid confusing users - see bug 1086728
        return [(tz, tz) for tz in sorted(pytz.all_timezones, key=lambda tz: tz if not tz.startswith('Etc/') else '_')]

    def _get_web_message_list(self, uid=0, msg_id=False, reply=False):
        return {}

    def get_all_order_status(self, status):
        """
        获取每个状态订单的数量
        :param status:
        :return:
        """
        order_qty = None
        user = request.env.user
        partner = user.partner_id
        get_obj = request.env['personal.center'].sudo()
        # get_obj = get_obj.with_context({'tz': user.tz})
        state = status
        order_qty = get_obj.get_partner(partner, state)
        #msg_pool = request.env['message.center'].sudo()
        #msg_unread_qty = msg_pool.GetWebMessage(user.id)
        msg_unread_qty = self._get_web_message_list(user.id)
        order_qty.get('qty').update({
            'mu_qty': msg_unread_qty.get('number', 0),
        })
        return order_qty

    @http.route('/change/avatar', type='json', auth='user', website=True)
    def cpo_change_avatar(self, **kw):
        """
        功能：在前端用户修改自己的头像
        author：Charlie Chen
        :param kw:
        :return:
        """
        datas = kw.get('datas')
        if not datas:
            kw['error'] = 'Upload failed, please upload again!'
        user_id = request.env.user.id
        personal_obj = request.env['personal.center'].sudo()
        personal = personal_obj.search([('user_id', '=', user_id)])
        if not personal:
            kw['error'] = 'Upload failed, please upload again!'
        personal.write({
            'image': kw.get('datas').split(',')[1],
        })
        kw['success'] = 'Uploaded successfully!'
        return kw

    @http.route('/cpo/change/tz', type='json', auth='user', website=True)
    def cpo_change_tz(self, **kw):
        """
        功能：在前端用户可以修改自己的时区
        author：Charlie Chen
        :param kw:
        :return:
        """
        user = request.env.user
        tz = kw.get('tz')
        if not user.partner_id or not tz:
            kw.update({
                'error': 'Update failed!',
            })
        user.partner_id.update({
            'tz': tz,
        })
        kw.update({
            'success': 'The current time zone has changed !',
        })
        return kw

    # update timezone of context for session
    def update_tz_context(self):
        """
        新增时区设置，切换时区自动更新
        :return:
        """
        new_tz = request.env.user.tz or 'UTC'
        new_context = dict(request.context,tz=new_tz)
        request.session.context.update({'tz':new_tz})
        setattr(request,'context',new_context)

    @http.route(['/my', '/my/home'], type='http', auth="user", website=True)
    def account(self, **kw):
        # update timezone
        self.update_tz_context()
        values = self._prepare_portal_layout_values()
        # partner = request.env.user.partner_id
        get_obj = request.env['personal.center']
        state = 'under_review'
        order_qty = self.get_all_order_status(state)
        pc_id = get_obj.sudo().search([('user_id', '=', request.env.user.id)])
        # order_qty = self._my_account_all_data()
        values.update({
            'link_active': 'my_home',
            'search_state': False,
            'path': '/my/home',
            'quotation_qty': order_qty,
            'page_name': 'my home',
            'user': request.env.user,
            'personal_id': self._cpo_get_user_ID(),
            'advertage': request.env.user.partner_id,
            'process_state': 'under_review',
            'timezones': self._tz_get(),
        })
        try:
            # CpoQuotationRecordCode().get_website_source()
            values = Website().get_seo_data(values)
        except Exception, e:
            _logger.error("website_sale postprocess: %s value has been dropped (empty or not writable)" % e)
        return request.render("website_cpo_sale.cpo_my_account_center", values)
        # return request.render("website_portal.portal_my_home", values)

    @http.route([
        '/my/account/orders',
        '/my/account/orders/page/<int:page>',
    ], type='http', auth='user', website=True)
    def my_account_orders(self, page=1, type=None, **post):
        link_active, attr, mft_obj, all_count = None, None, None, 0
        if type == 'under-review':
            state = 'under_review'
            link_active = 'under_review'
        elif type == 'payment':
            state = 'awaiting_payment'
            link_active = 'awaiting_payment'
        else:
            state = type
            link_active = type
        values = {
            'link_active': link_active,
            'search_state': False,
            'advertage': request.env.user.partner_id,
            'user': request.env.user,
            'process_state': state,
            'personal_id': self._cpo_get_user_ID(),
        }
        url = '/my/account/orders'
        order_qty = self.get_all_order_status(state)
        if order_qty.get('order'):
            all_count = len(order_qty.get('order'))
            attr = request.env['ir.attachment'].sudo().search([
                ('res_model', '=', 'sale.order'),
                ('res_id', 'in', order_qty.get('order').ids),
            ])
            if page == 1:
                order_qty['order'] = order_qty.get('order')[0*page:3*page]
            else:
                order_qty['order'] = order_qty.get('order')[3*(page-1):3*page]
        if type == 'manufacturing':
            personal_center = request.env['personal.center'].sudo()
            mft_obj = personal_center.GetMakeState(request.env.user.partner_id, order_id=False)
        pager = self.cpo_pager(url=url, total=all_count, page=page, step=3, scope=7, url_args=post, c_type=state)
        values.update({
            'quotation_qty': order_qty,
            'attr': attr,
            'mft_obj': mft_obj,
            'pager': pager,
        })
        return request.render("website_cpo_sale.cpo_my_account_order_status", values)

    def cpo_pager(self, url, total, page=1, step=30, scope=5, url_args=None, c_type=None):
        """ Generate a dict with required value to render `website.pager` template. This method compute
            url, page range to display, ... in the pager.
            :param url : base url of the page link
            :param total : number total of item to be splitted into pages
            :param page : current page
            :param step : item per page
            :param scope : number of page to display on pager
            :param url_args : additionnal parameters to add as query params to page url
            :type url_args : dict
            :returns dict
        """
        # Compute Pager
        page_count = int(math.ceil(float(total) / step))

        page = max(1, min(int(page if str(page).isdigit() else 1), page_count))
        scope -= 1

        pmin = max(page - int(math.floor(scope/2)), 1)
        pmax = min(pmin + scope, page_count)

        if pmax - pmin < scope:
            pmin = pmax - scope if pmax - scope > 0 else 1

        def get_url(page):
            if c_type:
                _url = "%s/page/%s?type=%s" % (url, page, c_type) if page > 1 else (url+'?type='+c_type)
            else:
                _url = "%s/page/%s" % (url, page) if page > 1 else url

            if url_args:
                _url = "%s?%s" % (_url, werkzeug.url_encode(url_args))
            return _url

        return {
            "page_count": page_count,
            "offset": (page - 1) * step,
            "page": {
                'url': get_url(page),
                'num': page
            },
            "page_start": {
                'url': get_url(pmin),
                'num': pmin
            },
            "page_previous": {
                'url': get_url(max(pmin, page - 1)),
                'num': max(pmin, page - 1)
            },
            "page_next": {
                'url': get_url(min(pmax, page + 1)),
                'num': min(pmax, page + 1)
            },
            "page_end": {
                'url': get_url(pmax),
                'num': pmax
            },
            "pages": [
                {'url': get_url(page), 'num': page} for page in pycompat.range(pmin, pmax+1)
            ]
        }

    def cpo_pager_func(self, total):
        pages = math.ceil(total/3)
        return pages

    @http.route(['/my/account/address'], type='http', auth='user', website=True)
    def my_account_address(self, **post):
        """
        获取收货地址
        date: 2019-11-28
        :param post:
        :return:
        """
        values = {}
        state = 'under_review'
        order_qty = self.get_all_order_status(state)
        user = request.env.user
        partner_addr = request.env.user.partner_id.child_ids
        values.update({
            'link_active': 'my_account_address',
            'user': user,
            'partner_addr': partner_addr,
            'personal_id': self._cpo_get_user_ID(),
            'quotation_qty': order_qty,
        })
        return request.render("website_cpo_sale.cpo_my_account_address", values)

    @http.route('/order/state', type='json', auth='user', website=True)
    def cpo_get_order_state_date(self, **post):
        """
        通过Ajax获取不同状态订单的信息
        date：2019年11月29日14:52:03
        :param post:
        :return:
        """
        values = {}
        get_obj = request.env['personal.center']
        order_qty = get_obj.get_partner(request.env.user.partner_id, post.get('state'))
        values.update({
            'search_state': False,
            'quotation_qty': order_qty,
            'process_state': post.get('state'),
            'personal_id': self._cpo_get_user_ID(),
        })
        return {
            'order_select': request.env['ir.ui.view'].render_template(
                'website_cpo_sale.account_page_content', values)
        }

    @http.route('/manufacturing/state', type='http', auth="user", website=True)
    def my_manufacturing_state(self, oid=None, **kwargs):
        """
        生产状态更新
        :param oid:
        :param kwargs:
        :return:
        """
        values = {}
        link_active = 'manufacturing'
        state = "manufacturing"
        user = request.env.user
        values = {
            'link_active': link_active,
            'search_state': False,
            'advertage': request.env.user.partner_id,
            'user': user,
            'personal_id': self._cpo_get_user_ID(),
        }
        order_qty = self.get_all_order_status(state)
        if order_qty.get('order'):
            attr = request.env['ir.attachment'].sudo().search([
                ('res_model', '=', 'sale.order'),
                ('res_id', 'in', order_qty.get('order').ids),
            ])
        # personal_center = request.env['personal.center'].sudo()
        personal_center = request.env['personal.center']
        mft_obj = personal_center.GetMakeState(user.partner_id, order_id=oid)
        values.update({
            'quotation_qty': order_qty,
            'attr': attr,
            'mft_obj': mft_obj,
            'oid': int(oid),
        })
        return request.render("website_cpo_sale.cpo_account_manufacturing_state", values)

    @http.route('/order/search', type='json', auth='user', website=True)
    def cpo_order_search(self, **post):
        """
        客户端订单搜索
        时间：2019年12月5日15:04:31
        :param post:
        :return:
        """
        user = request.env.user
        values, sale_orders, invoices, attr = {}, None, None, None
        state = post.get('state')
        order_qty = self.get_all_order_status(state)
        # get_obj = request.env['personal.center'].sudo()
        # order_qty = get_obj.get_partner(request.env.user.partner_id, state)
        if state == 'awaiting_payment':
            invoice = post.get('invoice').strip()
            if not invoice:
                post['error'] = "Search content cannot be empty!"
                return post
            invoices = order_qty.get('invoice_qty')
            if not invoices:
                post['error'] = "Did not find what you want!"
                return post
            invoice_obj = self._search_invoice(invoice, invoices)
            order_qty['invoice_qty'] = invoice_obj
        else:
            if state == 'engineering-question':
                ask_obj = self._get_web_eq_list(user.partner_id)
                order_qty.update({
                    'order': ask_obj,
                })
            order_number = post.get('order').strip()
            po_number = post.get('po_number').strip()
            if not order_number and not po_number:
                post['error'] = "Search content cannot be empty!"
                return post
            sale_orders = order_qty.get('order')
            search_orders = self._search_orders(order_number, po_number, sale_orders)
            if not search_orders:
                post['error'] = "Search content cannot be empty!"
                return post
            order_qty['order'] = search_orders
        partner_addr = request.env.user.partner_id.child_ids
        if order_qty.get('order'):
            attr = request.env['ir.attachment'].sudo().search([
                ('res_model', '=', 'sale.order'),
                ('res_id', 'in', order_qty.get('order').ids),
            ])
        analysis = urlparse.urlsplit(request.httprequest.environ.get('HTTP_REFERER'))
        url = analysis.path + '?' + analysis.query
        values.update({
            'link_active': state,
            'user': request.env.user,
            'search_state': True,
            'quotation_qty': order_qty,
            'process_state': post.get('state'),
            'personal_id': self._cpo_get_user_ID(),
            'partner_addr': partner_addr,
            'attr': attr,
            'url': url,
        })
        return {
            'order_search': request.env['ir.ui.view'].render_template(
                'website_cpo_sale.cpo_all_order_status_return', values)
        }

    def _search_orders(self, order_number, po_number, sale_orders):
        """
        搜索匹配订单
        :param order_number:
        :param po_number:
        :param sale_orders:
        :return:
        """
        order_ls = []
        if order_number:
            for s in sale_orders:
                if order_number in s.name:
                    order_ls.append(s.id)
        if po_number:

            for p in sale_orders:
                if p.po_number:
                    if po_number in p.po_number:
                        order_ls.append(p.id)
        all_list = list(set(order_ls))
        search_orders = request.env['sale.order'].sudo().search([('id', 'in', all_list)])
        return search_orders

    def _search_invoice(self, invoice, orders):
        """
        发票搜索
        :param invoice:
        :param orders:
        :return:
        """
        invoice_ls = []
        for i in orders:
            if invoice in i.number:
                invoice_ls.append(i.id)
        invoices = request.env['account.invoice'].sudo().search([('id', 'in', invoice_ls)])
        return invoices

    @http.route('/delete/address', type='json', auth='user', website=True)
    def cpo_delete_address(self, **post):
        """
        date：2019年12月2日18:50:40
        用户在个人中心删除收货地址
        :param post:
        :return:
        """
        post['url'] = '/my/account/address'
        Partner = request.env['res.partner']
        child_list = []
        partner = Partner.sudo().search([('id', '=', post.get('pid'))])
        partner_child_ids = request.env.user.partner_id.child_ids.ids
        if not partner:
            post['error'] = 'This record has been deleted or is being modified, please refresh and try again!'
            return request.redirect('/my/account/address')
        if partner.id in partner_child_ids:
            partner_child_ids.remove(partner.id)
            child_list = partner_child_ids
        elif partner.id not in partner_child_ids:
            post['error'] = 'The current data is not allowed to be deleted!'
            return post
        vals = {
            'child_ids': [(
                6,
                0,
                child_list
            )]
        }
        pobj = Partner.sudo().search([('id', '=', request.env.user.partner_id.id)])
        pobj.sudo().write(vals)
        return post

    @http.route('/my/paid', type="http", auth="user", website=True)
    def cpo_my_paid(self, type=None, **kwargs):
        """
        新增路由
        功能：提供客户查看已支付订单，待支付订单，申请退款等
        时间：2019年12月4日16:36:53
        :param kwargs:
        :return:
        """
        attr = None
        value = type
        state = 'under_review'
        order_qty = self.get_all_order_status(state)
        refunded = request.env['sales.refund'].sudo()
        client_id = request.env.user.partner_id
        if value == 'payment':
            order_data = refunded.GetShowOrApply(client_id)
            process_state = 'paid_payment'
        else:
            order_data = refunded.GetShowOrApply(client_id, value=True)
            process_state = 'paid_refund'
        # 状态：list = ['payment', 'refund']
        if order_data.get('order_obj'):
            attr = request.env['ir.attachment'].sudo().search([
                ('res_model', '=', 'sale.order'),
                ('res_id', 'in', order_data.get('order_obj').ids),
            ])
        if order_data.get('refund_obj'):
            attr = request.env['ir.attachment'].sudo().search([
                ('res_model', '=', 'sale.order'),
                ('res_id', 'in', order_data.get('refund_obj').ids),
            ])
        values = {
            'process_state': process_state,
            'link_active': 'my_paid',
            'state': value,
            'attr': attr,
            'quotation_qty': order_qty,
            'user': request.env.user,
            'personal_id': self._cpo_get_user_ID(),
            'order_data': order_data,
        }
        return request.render("website_cpo_sale.cpo_paid_and_refunded", values)

    @http.route('/paid/search', type='json', auth='user', website=True)
    def cpo_paid_order_search(self, **kwargs):
        """
        支付和退款的搜索
        :param kwargs:
        :return:
        """
        values, sale_orders, invoices, attr, back_lc = {}, None, None, None, None
        state = kwargs.get('state')
        refunded = request.env['sales.refund'].sudo()
        client_id = request.env.user.partner_id
        if state == 'paid_payment':
            back_lc = 'payment'
            order_number = kwargs.get('order').strip()
            po_number = kwargs.get('po_number').strip()
            if not order_number and not po_number:
                kwargs['error'] = "Search content cannot be empty!"
                return kwargs
            order_data = refunded.GetShowOrApply(client_id)
            sale_orders = order_data.get('order_obj')
            if not sale_orders:
                kwargs['error'] = "Did not find what you want!"
                return kwargs
            search_orders = self._search_orders(order_number, po_number, sale_orders)
            if not search_orders:
                kwargs['error'] = "Search content cannot be empty!"
                return kwargs
            order_data['order_obj'] = search_orders
        else:
            back_lc = 'refund'
            order_number = kwargs.get('order').strip()
            po_number = kwargs.get('po_number').strip()
            if not order_number and not po_number:
                kwargs['error'] = "Search content cannot be empty!"
                return kwargs
            order_data = refunded.GetShowOrApply(client_id, value=True)
            refund_objs = order_data.get('refund_obj')
            order_ids = []
            for i in refund_objs:
                order_ids.append(i.order_id.id)
            sale_orders = request.env['sale.order'].sudo().search([('id', 'in', list(set(order_ids)))])
            if not sale_orders:
                kwargs['error'] = "Did not find what you want!"
                return kwargs
            search_orders = self._search_orders(order_number, po_number, sale_orders)
            if not search_orders:
                kwargs['error'] = "Search content cannot be empty!"
                return kwargs
            refund_sh = refunded.search([('order_id', 'in', search_orders.ids)])
            order_data['refund_obj'] = refund_sh
        values.update({
            'link_active': 'my_paid',
            'user': request.env.user,
            'search_state': True,
            'back_lc': back_lc,
            'state': back_lc,
            'process_state': state,
            'personal_id': self._cpo_get_user_ID(),
            'attr': attr,
            'order_data': order_data,
        })
        return {
            'paid_search': request.env['ir.ui.view'].render_template(
                'website_cpo_sale.cpo_paid_template_data', values)
        }

    @http.route('/my/refund', type="http", auth="user", website=True)
    def cpo_my_refund(self, order_id=None, order_name=None, **kwargs):
        """
        新增路由（退款）
        功能：申请退款
        时间：2019年12月11日19:21:37
        :param kwargs:
        :return:
        """
        attr, o_id, o_name = None, None, None
        value = type
        state = 'under_review'
        order_qty = self.get_all_order_status(state)
        if not order_id and not order_name:
            return request.redirect('/my/paid?type=payment')
        o_id = base64.b64decode(order_id[5:]).decode()
        o_name = order_name
        values = {
            'link_active': 'my_paid',
            'state': value,
            'order_id': o_id,
            'order_name': o_name,
            'quotation_qty': order_qty,
            'user': request.env.user,
            'personal_id': self._cpo_get_user_ID(),
        }
        return request.render("website_cpo_sale.cpo_my_refunded", values)

    @http.route('/refund/submit', type='json', auth='user', website=True)
    def cpo_refund_submit(self, **kwargs):
        """
        发起退款申请，跳转到填写申请页面
        :param kwargs:
        :return:
        """
        order_id = kwargs.get('order_id')
        order_name = kwargs.get('order_name')
        check = request.env['sales.refund'].sudo().CheckApplyRecord(order_id)
        if check:
            kwargs['error'] = check.get('reason')
            return kwargs
        if not order_id and not order_name:
            return kwargs
        enc_str = cpo_mark()
        str_encryption = enc_str + base64.b64encode(order_id)  # 字符串加密
        kwargs['url'] = '/my/refund?order_id='+str_encryption+'&order_name='+order_name
        return kwargs

    @http.route('/cancel/refund', type='json', auth='user', website=True)
    def cpo_cancel_refund(self, **kwargs):
        """
        取消退款申请
        :param kwargs:
        :return:
        """
        refund_id = kwargs.get('refund_id')
        check = request.env['sales.refund'].sudo().GetCancelRefund(refund_id)
        if check:
            kwargs['success'] = "Cancel success!"
            kwargs['url'] = '/my/paid?type=refund'
            return kwargs

    @http.route('/refund/send', type='json', auth='user', website=True)
    def cpo_refund_sead(self, **kwargs):
        """
        发送消息(消息系统)
        :param kwargs:
        :return:
        """
        if not kwargs.get('order_id') and not kwargs.get('refund_instr'):
            kwargs['error'] = 'Application failed, please try again!'
            return kwargs
        order_id = kwargs.get('order_id')
        refund_instr = kwargs.get('refund_instr')
        client_id = request.env.user.partner_id
        refunded = request.env['sales.refund'].sudo()
        value = refunded.GetShowOrApply(client_id, order_id=order_id, reason=refund_instr)
        if not value.get('refund_id'):
            kwargs['error'] = 'Application failed, please try again!'
            return kwargs
        kwargs['success'] = 'Successful application! Please pay attention to the email notification!'
        kwargs['url'] = '/my/paid?type=refund'
        return kwargs

    @http.route('/paid/status', type='json', auth='user', website=True)
    def cpo_paid_status(self, **kwargs):
        """
        支付状态切换
        :param kwargs:
        :return:
        """
        value = kwargs.get('state')
        refunded = request.env['sales.refund'].sudo()
        client_id = request.env.user.partner_id
        if value == 'refund':
            order_data = refunded.GetShowOrApply(client_id, value)
        else:
            order_data = refunded.GetShowOrApply(client_id)
        values = {
            'state': value,
            'user': request.env.user,
            'personal_id': self._cpo_get_user_ID(),
            'order_data': order_data,
        }
        return request.render("website_cpo_sale.cpo_paid_template_data", values)

    @http.route('/message/center', type='http', auth='user', website=True)
    def cpo_message_center(self, **kw):
        """
        消息中心，个人消息通知
        时间：2019年12月12日09:38:15
        author：Charlie
        :param kw:
        :return:
        """
        values, msg_obj = {}, None
        state = 'under_review'
        user = request.env.user
        order_qty = self.get_all_order_status(state)
        # msg_pool = request.env['message.center'].sudo()
        # msg_dict = msg_pool.GetWebMessage(user.id)
        msg_dict = self._get_web_message_list(user.id)
        values = {
            'msg_content': 'list',
            'link_active': 'message',
            'state': state,
            'quotation_qty': order_qty,
            'user': user,
            'msg_obj': msg_dict.get('msg_obj', None),
            'personal_id': self._cpo_get_user_ID(),
        }
        return request.render("website_cpo_sale.cpo_my_message_center", values)

    @http.route('/message/details', type='http', auth='user', website=True)
    def cpo_message_details(self, message=None, **kw):
        """
        消息中心: 个人消息详情
        时间：2019年12月12日11:33:48
        author：Charlie
        :param kw:
        :return:
        """
        values, msg_obj = {}, None
        user = request.env.user
        if message:
            msg_id = int(message)
            msg_obj = self._get_web_message_list(user.id, msg_id=msg_id)
            # msg_obj = msg_obj.get('msg_obj', None)
            # msg_pool = request.env['message.center'].sudo()
            # msg_obj = msg_pool.GetWebMessage(user.id, msg_id=msg_id)
            if not msg_obj:
                return request.render("website_cpo_sale.cpo_website_404", values)
        state = 'under_review'
        order_qty = self.get_all_order_status(state)
        values = {
            'msg_content': 'details',
            'link_active': 'message',
            'state': state,
            'quotation_qty': order_qty,
            'user': request.env.user,
            'personal_id': self._cpo_get_user_ID(),
            'msg_obj': msg_obj,
        }
        return request.render("website_cpo_sale.cpo_my_message_center", values)

    @http.route('/send/message', type='json', auth='user', website=True)
    def cpo_send_message(self, **kwargs):
        """
        个人中心发送留言
        :param kwargs:
        :return:
        """
        user, msg_id = request.env.user, None
        reply = kwargs.get('message')
        msg_id = kwargs.get('msg_line_id')
        if msg_id:
            msg_id = int(msg_id)
        msg_obj = self._get_web_message_list(user.id, msg_id=msg_id, reply=reply)
        # msg_obj = msg_obj.get('msg_obj', None)
        # msg_pool = request.env['message.center'].sudo()
        # msg_obj = msg_pool.GetWebMessage(user.id, msg_id=msg_id, reply=reply)
        if not msg_obj:
            kwargs['error'] = 'Send failed, please resend!'
            return kwargs
        url = '/message/details?message=' + str(msg_obj.id)
        kwargs['url'] = url
        return kwargs

    @http.route('/show/order-details', type='json', auth='user', website=True)
    def cpo_show_order_details(self, **kwargs):
        """
        个人中心展示订单详情
        :param kwargs:
        :return:
        """
        values = {}
        if not kwargs.get('oid'):
            kwargs['error'] = 'Please refresh and try again!'
            return kwargs
        sale_order = request.env['sale.order'].sudo().search([('id', '=', kwargs.get('oid'))])
        if not sale_order:
            kwargs['error'] = 'Please refresh and try again!'
            return kwargs
        # details = self.cpo_get_show_order_details(sale_order)
        values.update({
            'sale_order': sale_order,
        })
        return {
            'show_order_details': request.env['ir.ui.view'].render_template(
                'website_cpo_sale.my_home_order_details', values)
        }

    def _get_web_eq_list(self, client_id, order_id=False, reply=False, ask_id=False, images=False):
        return {}

    @http.route([
        '/my/engineering-question',
        '/my/engineering-question/page/<int:page>',
    ], type='http', auth='user', website=True)
    def cpo_engineering_question(self, eqid=None, page=1, **kwargs):
        """
        工程问客展示
        :param eqid:
        :param kwargs:
        :return:
        """
        values, ask_list, attr, all_count = {}, [], None, 0
        # 如果有ID，说明是查看详情或者回复
        if eqid:
            return self.get_eqid_data(eqid)
        state = 'under_review'
        user = request.env.user
        order_qty = self.get_all_order_status(state)
        # ask_pool = request.env['ask.guest'].sudo()
        # ask_obj = ask_pool.GetAskGuestShow(user.partner_id)
        ask_obj = self._get_web_eq_list(user.partner_id)
        if ask_obj:
            attr = request.env['ir.attachment'].sudo().search([
                ('res_model', '=', 'sale.order'),
                ('res_id', 'in', ask_obj.ids),
            ])
            all_count = len(ask_obj)
            order_qty['order'] = ask_obj[3*(page-1):3*page]
        for ask in ask_obj:
            ask_len = len(ask.ask_ids.filtered(lambda x: x.state == 'wait_reply'))
            ask_list.append([ask_len, ask.id])
        url = '/my/engineering-question'
        pager = self.cpo_pager(url=url, total=all_count, page=page, step=3, scope=7, url_args=kwargs, c_type=eqid)
        values = {
            'eq_state': False,
            'search_state': False,
            'process_state': 'engineering-question',
            'link_active': 'eq_active',
            'quotation_qty': order_qty,
            'user': user,
            'ask_obj': ask_list,
            'attr': attr,
            'pager': pager,
            'personal_id': self._cpo_get_user_ID(),
        }
        return request.render("website_cpo_sale.cpo_engineering_question", values)

    def get_eqid_data(self, eqid):
        """
        问客：
        展示详情或者回复
        :param eqid:
        :return:
        """
        state = 'under_review'
        user = request.env.user
        order_qty = self.get_all_order_status(state)
        # ask_pool = request.env['ask.guest'].sudo()
        # ask_obj_id = ask_pool.search([('id', '=', eqid)])
        # ask_obj_id = self._get_web_eq_list(user.partner_id, oid)
        ask_obj_id = self._get_web_eq_list(user.partner_id, ask_id=eqid)
        values = {
            'eq_state': True,
            'eq_list': True,
            'search_state': False,
            'process_state': 'engineering-question',
            'link_active': 'eq_active',
            'quotation_qty': order_qty,
            'user': user,
            'ask_obj_id': ask_obj_id,
            'personal_id': self._cpo_get_user_ID(),
        }
        return request.render("website_cpo_sale.cpo_engineering_question", values)
        # return request.render("website_cpo_sale.cpo_click_eq_id_show_datails", values)

    @http.route('/show/eq-details', type='json', auth='user', website=True)
    def cpo_show_eq_details(self, **kwargs):
        """
        展示所有的问客问题
        包括已读和未读
        :param kwargs:
        :return:
        """
        values = {
            'ask_obj': None,
        }
        oid = kwargs.get('oid')
        user = request.env.user
        # ask_pool = request.env['ask.guest'].sudo()
        # ask_obj = ask_pool.GetAskGuestShow(user.partner_id, oid)
        ask_obj = self._get_web_eq_list(user.partner_id, oid)
        if ask_obj:
            values.update({
                'ask_obj': ask_obj,
            })
        return {
            'show_eq_details': request.env['ir.ui.view'].render_template(
                'website_cpo_sale.cpo_order_eq_list_datails', values)
        }

    @http.route([
        '/show/eq-details',
        '/show/eq-details/<int:oid>/<int:eqid>',
    ], type='http', auth='user', website=True)
    def cpo_show_eq_details(self, oid=None, eqid=None, **kwargs):
        state, ask_obj_id, eq_list = 'under_review', None, True
        user = request.env.user
        order_qty = self.get_all_order_status(state)
        # ask_pool = request.env['ask.guest'].sudo()
        # ask_obj = ask_pool.GetAskGuestShow(user.partner_id, oid, ask_id=eqid)
        ask_obj = self._get_web_eq_list(user.partner_id, oid, ask_id=eqid)
        if eqid:
            # ask_obj_id = ask_pool.search([('id', '=', eqid)])
            ask_obj_id = ask_obj.filtered(lambda x: x.id == eqid)
            eq_list = False
        values = {
            'eq_state': True,
            'eq_list': eq_list,
            'search_state': False,
            'process_state': 'engineering-question',
            'link_active': 'eq_active',
            'quotation_qty': order_qty,
            'user': user,
            'ask_obj': ask_obj,
            'ask_obj_id': ask_obj_id,
            'oid': oid,
            'personal_id': self._cpo_get_user_ID(),
        }
        return request.render("website_cpo_sale.cpo_engineering_question", values)

    @http.route('/ask/reply', type='json', auth='user', website=True)
    def cpo_ask_reply(self, **kwargs):
        """
        客户回复问客问题！
        :param kwargs:
        :return:
        """
        user = request.env.user
        oid = kwargs.get('oid')
        order_id = False
        ask_id = kwargs.get('ask_id')
        reply = kwargs.get('user_reply_content')
        file_list = []
        # ask_pool = request.env['ask.guest'].sudo()
        # ask_obj = ask_pool.GetAskGuestShow(user.partner_id, order_id, reply, ask_id, file_list)
        ask_obj = self._get_web_eq_list(user.partner_id, order_id, reply, ask_id, file_list)
        if ask_obj:
            kwargs['url'] = '/show/eq-details/%d/%d' % (int(oid), int(ask_id))
            return kwargs
        if not ask_id or not reply:
            kwargs['error'] = 'Please refresh the page and try again!'
            return kwargs

    @http.route('/ask/file', type='json', auth='user', website=True)
    def cpo_ask_file(self, **kwargs):
        """
        问客文件上传
        :param kwargs:
        :return:
        """
        attachment_obj = request.env['ir.attachment'].sudo()
        datas = kwargs.get('datas')
        name = kwargs.get('name')
        file_desc = kwargs.get('file_desc')
        if not datas:
            kwargs.update({
                'error': 'Upload failed, please upload again!'
            })
            return kwargs
        vals = {
            'name': name,
            'description': file_desc,
            'type': 'binary',
            'public': True,
            'datas': datas,
            'datas_fname': name,
        }
        attachment = attachment_obj.create(vals)
        if not attachment:
            kwargs.update({
                'error': 'Upload failed, please upload again!'
            })
            return kwargs
        str_encryption = base64.b64encode(str(attachment.id))  # 字符串加密
        atta_id = cpo_mark() + str_encryption
        kwargs.update({
            'atta_id': atta_id
        })
        return kwargs

    @http.route(['/my/account'], type='http', auth='user', website=True)
    def details(self, redirect=None, **post):
        self.OPTIONAL_BILLING_FIELDS.append('tz')
        values = self._prepare_portal_layout_values()
        orders_qty = self._my_account_all_data()
        partner = request.env.user.partner_id
        values.update({
            'orders_qty': orders_qty
        })
        values.update({
            'error': {},
            'error_message': [],
            'hide_current_user': True,
        })

        if post:
            error, error_message = self.details_form_validate(post)
            values.update({'error': error, 'error_message': error_message})
            values.update(post)
            if not error:
                values = {key: post[key] for key in self.MANDATORY_BILLING_FIELDS}
                values.update({key: post[key] for key in self.OPTIONAL_BILLING_FIELDS if key in post})
                values.update({'zip': values.pop('zipcode', '')})
                partner.sudo().write(values)
                #partner.sudo().user_ids.write({'tz':values.get('tz')})
                if redirect:
                    return request.redirect(redirect)
                return request.redirect('/my/home')

        countries = request.env['res.country'].sudo().search([])
        states = request.env['res.country.state'].sudo().search([])

        values.update({
            'partner': partner,
            'page_name': 'my account',
            'countries': countries,
            'states': states,
            'has_check_vat': hasattr(request.env['res.partner'], 'check_vat'),
            'timezones': self._tz_get(),
            'redirect': redirect,
        })

        response = request.render("website_portal.details", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    def _cpo_get_user_ID(self):
        """
        获取（personal对象）
        :return:
        """
        personal_id = 'CPO001001'
        personal_center = request.env['personal.center'].sudo()
        user_id = request.env.user.id
        if not user_id:
            return personal_id
        return personal_center.search([('user_id', '=', user_id)])

    # 订单状态（进入生产）
    @http.route(['/my/manufacturing'], type='http', auth='user', website=True)
    def my_manufacturing(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        values.update({
            'page_name': 'my manufacturing'
        })
        try:
            partner_id = request.env.user.partner_id.id
            personal_c = request.env['personal.center']
            get_data = personal_c.get_interface_flow(partner_id)
            values.update({
                'default_url': '/my/manufacturing',
                'pcb': get_data.get('PCB'),
                'pcba': get_data.get('PCBA'),
                'all_order': get_data.get('ALL'),
                'pcb_qty': len(get_data.get('PCB')),
                'pcba_qty': len(get_data.get('PCBA')),
                'all_qty': len(get_data.get('ALL')),
            })
        except Exception, e:
            pass
        return request.render("website_cpo_sale.portal_my_manufacturing", values)

    # /my/express
    def _my_all_express_no(self):
        """
        所有的快递单号
        :return:
        """
        values = {}
        partner = request.env.user.partner_id

        SaleOrder = request.env['sale.order']
        Invoice = request.env['account.invoice']
        # quotation_count = SaleOrder.search_count([
        #     ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
        #     ('state', 'in', ['sent', 'cancel'])
        # ])
        express_self_no = SaleOrder.search([
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('state', 'in', ['sale', 'wait_payment', 'manufacturing', 'wait_delivery', 'wait_receipt', 'complete'])
        ])
        express_cpo_no = SaleOrder.search([
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('state', 'in', ['sale', 'wait_payment', 'manufacturing', 'wait_delivery', 'wait_receipt', 'complete']),

        ])
        express_self_count = SaleOrder.search_count([
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('state', 'in', ['sale', 'wait_payment', 'manufacturing', 'wait_delivery', 'wait_receipt', 'complete'])
        ])
        express_cpo_count = SaleOrder.search_count([
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('state', 'in', ['sale', 'wait_payment', 'manufacturing', 'wait_delivery', 'wait_receipt', 'complete']),

        ])

        values.update({
            'express_self_no': express_self_no,
            'express_cpo_no': express_cpo_no,
            'express_self_count': express_self_count,
            'express_cpo_count': express_cpo_count,
        })
        return values

    @http.route(['/my/express', '/my/express/page/<int:page>'], type='http', auth="user", website=True)
    def portal_customer_express(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        """
        客户上传快递信息
        :param page:
        :param date_begin:
        :param date_end:
        :param sortby:
        :param kw:
        :return:
        """
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        SaleOrder = request.env['sale.order']
        express_no = self._my_all_express_no()
        domain = [
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('state', 'in', ['sale'])
        ]

        searchbar_sortings = {
            'date': {'label': _('Order Date'), 'order': 'date_order desc'},
            'name': {'label': _('Reference'), 'order': 'name'},
        }

        # default sortby order
        if not sortby:
            sortby = 'date'
        sort_order = searchbar_sortings[sortby]['order']

        archive_groups = self._get_archive_groups('sale.order', domain)
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # count for pager
        quotation_count = SaleOrder.search_count(domain)
        # make pager
        pager = request.website.pager(
            url="/my/express",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=quotation_count,
            page=page,
            step=self._items_per_page
        )
        # search the count to display, according to the pager data
        quotations = SaleOrder.search(domain, order=sort_order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_quotes_history'] = quotations.ids[:100]

        values.update({
            'express_no': express_no,
            'date': date_begin,
            'quotations': quotations,
            'page_name': 'my express customer',
            'pager': pager,
            'archive_groups': archive_groups,
            'default_url': '/my/express',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        return request.render("website_cpo_sale.portal_my_express", values)

    # /my/express
    @http.route(['/my/express/cpo', '/my/express/cpo/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_express_cpo(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        """
        后台上传快递信息
        :param page:
        :param date_begin:
        :param date_end:
        :param sortby:
        :param kw:
        :return:
        """
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        SaleOrder = request.env['sale.order']

        domain = [
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('state', 'in', ['sale', 'wait_payment', 'manufacturing', 'wait_delivery', 'wait_receipt', 'complete'])
        ]

        searchbar_sortings = {
            'date': {'label': _('Order Date'), 'order': 'date_order desc'},
            'name': {'label': _('Reference'), 'order': 'name'},
        }

        # default sortby order
        if not sortby:
            sortby = 'date'
        sort_order = searchbar_sortings[sortby]['order']

        archive_groups = self._get_archive_groups('sale.order', domain)
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # count for pager
        quotation_count = SaleOrder.search_count(domain)
        # make pager
        pager = request.website.pager(
            url="/my/express/cpo",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=quotation_count,
            page=page,
            step=self._items_per_page
        )
        # search the count to display, according to the pager data
        quotations = SaleOrder.search(domain, order=sort_order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_quotes_history'] = quotations.ids[:100]

        values.update({
            'date': date_begin,
            'quotations': quotations,
            'page_name': 'my express cpo',
            'pager': pager,
            'archive_groups': archive_groups,
            'default_url': '/my/express/cpo',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        return request.render("website_cpo_sale.portal_my_express_cpo", values)

    # /my/bom
    @http.route(['/my/bom', '/my/bom/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_bom(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        """

        :param page:
        :param date_begin:
        :param date_end:
        :param sortby:
        :param kw:
        :return:
        """
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        SaleOrder = request.env['sale.order']
        BOM_pool = request.env['cpo_offer_bom.bom'].sudo()

        domain = [
            #('partner_id', '=', partner.id)
            ('partner_id', 'child_of', [partner.commercial_partner_id.id]),
            #('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('state', 'in', ['draft', 'check']),
        ]

        unuse_bom_ids = BOM_pool.search(domain).filtered(lambda x:x.order_ids==request.env['sale.order.line']).mapped("id")
        domain += [('id', 'in', unuse_bom_ids)]

        searchbar_sortings = {
            'date': {'label': _('Order Date'), 'order': 'create_date desc'},
            'name': {'label': _('Reference'), 'order': 'name'},
        }

        # default sortby order
        if not sortby:
            sortby = 'date'
        sort_order = searchbar_sortings[sortby]['order']

        #archive_groups = self._get_archive_groups('sale.order', domain)
        archive_groups = self._get_archive_groups('cpo_offer_bom.bom', domain)
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # count for pager
        quotation_count = SaleOrder.search_count(domain)
        # make pager
        pager = request.website.pager(
            url="/my/bom",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=0,
            page=page,
            step=self._items_per_page
        )
        # search the count to display, according to the pager data
        #quotations = SaleOrder.search(domain, order=sort_order, limit=self._items_per_page, offset=pager['offset'])
        boms = BOM_pool.search(domain, order=sort_order, limit=self._items_per_page, offset=pager['offset'])
        #request.session['my_quotes_history'] = quotations.ids[:100]

        bom_att_ids = {}
        for bom_x in boms:
            bom_att_ids.update({
                bom_x.id:self._get_atta_id_for_bom(bom_x)
            })
        values.update({
            'date': date_begin,
            #'quotations': quotations,
            'boms':boms,
            'page_name': 'my bom',
            'pager': pager,
            'archive_groups': archive_groups,
            'default_url': '/my/bom',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'bom_att_ids': bom_att_ids,
        })
        return request.render("website_cpo_sale.portal_my_bom", values)

    # 优惠券
    @http.route(['/my/coupon', '/my/coupon/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_coupon(self, page=1, **kw):
        """
        客户个人中心优惠券展示，
        时间： 2019年12月3日16:55:18
        :param page:
        :param kw:
        :return:
        """
        values = {}
        state = 'under_review'
        order_qty = self.get_all_order_status(state)
        preferential = http.request.env['preferential.cpo_time_and_money']
        preferential.checking_function()
        coupon_list = []
        user_id = request.env.user.partner_id.id
        rows = http.request.env['preferential.cpo_customer_contact'].sudo().search([
                                  ('cpo_invalid_bool', '=', False),
                                  ('cpo_voucher_bool', '=', True),
                                  ('cpo_use_bool', '=', False),
                                  ('partner_id', '=', user_id)
                                ])
        values.update({
            'link_active': 'my_coupon',
            'rows': rows,
            'quotation_qty': order_qty,
            'user': request.env.user,
            'personal_id': self._cpo_get_user_ID(),
        })
        return request.render("website_cpo_sale.cpo_my_account_coupons", values)
    #
    # @http.route(['/my/coupon', '/my/coupon/page/<int:page>'], type='http', auth="user", website=True)
    # def portal_my_coupon(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
    #
    #     values = self._prepare_portal_layout_values()
    #     partner = request.env.user.partner_id
    #
    #     preferential = http.request.env['preferential.cpo_time_and_money']
    #     preferential.checking_function()
    #     coupon_list = []
    #     user_id = request.env.user.partner_id.id
    #     rows = http.request.env['preferential.cpo_customer_contact'].sudo().search([
    #                               ('cpo_invalid_bool', '=', False),
    #                               ('cpo_voucher_bool', '=', True),
    #                               ('cpo_use_bool', '=', False),
    #                               ('partner_id', '=', user_id)
    #                             ])
    #     domain = [
    #         ('partner_id', 'child_of', [partner.commercial_partner_id.id]),
    #         ('state', 'in', ['draft', 'check']),
    #     ]
    #
    #     if not sortby:
    #         sortby = 'date'
    #
    #     if date_begin and date_end:
    #         domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]
    #
    #     pager = request.website.pager(
    #         url="/my/coupon",
    #         url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
    #         total=0,
    #         page=page,
    #         step=self._items_per_page
    #     )
    #
    #     values.update({
    #         'date': date_begin,
    #         'page_name': 'my coupon',
    #         'pager': pager,
    #         'default_url': '/my/bom',
    #         'sortby': sortby,
    #         'rows': rows
    #     })
    #     return request.render("website_cpo_sale.portal_my_coupon", values)

    def _get_atta_id_for_bom(self, bom):
        atta_row = {}
        atta = request.env['ir.attachment']
        if bom:
            atta_row = atta.search([
                ('res_id', '=', bom.id),
                ('res_model', '=', 'cpo_offer_bom.bom')
            ])
        return atta_row.id if atta_row else False

    @http.route(['/my/bom/<model("cpo_offer_bom.bom"):bom>', '/my/bom/<model("cpo_offer_bom.bom"):bom>/page/<int:page>'], type='http', auth="user", website=True)
    def cpo_bom_followup(self, page=1, bom=None, **kw):
        bom_id = bom.id
        #bom = request.env['cpo_offer_bom.bom'].browse([bom_id])
        bom_line_pool = request.env['cpo_offer_bom.bom_line']
        try:
            bom.check_access_rights('read')
            bom.check_access_rule('read')
        except AccessError:
            return request.render("website.403")
        limit_page = self._items_per_page

        pager = request.website.pager(
            url="/my/bom/{bom_id}".format(bom_id=bom_id),
            #url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=len(bom.base_table_bom),
            page=page,
            step=limit_page
        )
        bom_line = bom_line_pool.search([('id', 'in', bom.base_table_bom.ids)], limit=limit_page,  offset=pager['offset'])

        #order_sudo = bom.sudo()
        #order_invoice_lines = {il.product_id.id: il.invoice_id for il in order_sudo.invoice_ids.mapped('invoice_line_ids')}

        #history = request.session.get('my_orders_history', [])

        values = {
            'bom': bom,
            'bom_line': bom_line,
            'pager':pager
            #'order_invoice_lines': order_invoice_lines,
        }
        #values.update(get_records_pager(history, order))
        return request.render("website_cpo_sale.bom_followup", values)
    # ------------------------------------------------------
    # Payment
    # ------------------------------------------------------


    @http.route(['/my/waitconf', '/my/waitconf/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_payment(self, page=1, date_begin=None, date_end=None, sortby=None, **post):
        """
        订单待确认状态
        :param page:
        :param date_begin:
        :param date_end:
        :param sortby:
        :param post:
        :return:
        """
        SaleOrder = request.env['sale.order']

        order = request.website.sale_get_order()

        # redirection = self.checkout_redirection(order)
        # if redirection:
        #     return redirection

        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        SaleOrder = request.env['sale.order']

        domain = [
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            #('state', 'in', ['sent', 'cancel'])
            # ('state', 'in', ['draft', 'cancel'])
            ('state', 'in', ['wait_confirm'])
        ]

        searchbar_sortings = {
            # 'search': {'label': _('Filter')},
            'date': {'label': _('Order Date'), 'order': 'date_order desc'},
            'name': {'label': _('Reference'), 'order': 'name'},
        }

        # default sortby order
        if not sortby:
            sortby = 'date'
        sort_order = searchbar_sortings[sortby]['order']

        archive_groups = self._get_archive_groups('sale.order', domain)
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # count for pager
        quotation_count = SaleOrder.search_count(domain)
        # make pager
        pager = request.website.pager(
            url="/my/waitconf",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=quotation_count,
            page=page,
            step=self._items_per_page
        )
        # search the count to display, according to the pager data

        quotations = SaleOrder.sudo().search(domain, order=sort_order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_quotes_history'] = quotations.ids[:100]

        shipping_partner_id = False
        if order:
            if order.partner_shipping_id.id:
                shipping_partner_id = order.partner_shipping_id.id
            else:
                shipping_partner_id = order.partner_invoice_id.id

        values.update({
            #'website_sale_order': order,
            'website_sale_order': quotations,
            # 'quotation_count':quotation_count
        })
        values['errors'] = SaleOrder._get_errors(order)
        values.update(SaleOrder._get_website_data(order))
        if not values['errors']:
            acquirers = request.env['payment.acquirer'].search(
                [('website_published', '=', True), ('company_id', '=', order.company_id.id)]
            )
            values['acquirers'] = []

            values.update({
                'date': date_begin,
                'page_name': 'waitconf',
                'pager': pager,
                'archive_groups': archive_groups,
                'default_url': '/my/waitconf',
                'searchbar_sortings': searchbar_sortings,
                'sortby': sortby,
            })

            values['tokens'] = request.env['payment.token'].search([('partner_id', '=', order.partner_id.id), ('acquirer_id', 'in', acquirers.ids)])

        return request.render("website_cpo_sale.waitconf", values)

    @http.route(['/my/waitconf/<int:order>'], type='http', auth="user", website=True)
    def confirm_orders_followup(self, order=None, **kw):
        """
        调用sales orders的模板，如果是state==sale显示蓝色，可以点击查看详情
        :param order:
        :param kw:
        :return:
        """
        order = request.env['sale.order'].browse([order])
        try:
            order.check_access_rights('read')
            order.check_access_rule('read')
        except AccessError:
            return request.render("website.403")

        order_sudo = order.sudo()
        order_invoice_lines = {il.product_id.id: il.invoice_id for il in
                               order_sudo.invoice_ids.mapped('invoice_line_ids')}

        pcba_order = order_sudo.order_line.only_pcba_order_line()
        pcb_order = order_sudo.order_line.only_pcb_order_line()
        # 2019-05-09
        stencil_order = order_sudo.order_line.only_stencil_order_line()
        if pcba_order and not pcb_order:
            order_line_type = 'PCBA'
        elif not pcba_order and pcb_order:
            order_line_type = 'PCB'
        # 2019-05-09
        elif stencil_order:
            order_line_type = 'Stencil'
        elif not pcba_order and not pcb_order and not stencil_order:
            raise ValidationError(_("Current types are not supported"))
        else:
            raise ValidationError(_("Current types are not supported"))
        history = request.session.get('my_orders_history', [])

        values = {
            'order': order_sudo,
            'order_invoice_lines': order_invoice_lines,
            'order_line_type': order_line_type
        }
        values.update(get_records_pager(history, order))
        return request.render("website_portal_sale.orders_followup", values)


    @http.route(['/my/orders/<int:order>'], type='http', auth="user", website=True)
    def orders_followup(self, order=None, **kw):
        """
        sales orders页面上，点击可以查看具体的订单详情
        :param order:
        :param kw:
        :return:
        """
        order = request.env['sale.order'].browse([order])
        try:
            order.check_access_rights('read')
            order.check_access_rule('read')
        except AccessError:
            return request.render("website.403")

        order_sudo = order.sudo()
        order_invoice_lines = {il.product_id.id: il.invoice_id for il in order_sudo.invoice_ids.mapped('invoice_line_ids')}


        pcba_order = order_sudo.order_line.only_pcba_order_line()
        pcb_order = order_sudo.order_line.only_pcb_order_line()
        if pcba_order and not pcb_order:
            order_line_type = 'PCBA'
        elif not pcba_order and pcb_order:
            order_line_type = 'PCB'
        elif not pcb_order and not pcba_order:
            order_line_type = 'Stencil'
        elif not pcba_order and not pcb_order:
            raise ValidationError(_("Current types are not supported"))
        else:
            raise ValidationError(_("Current types are not supported"))
        history = request.session.get('my_orders_history', [])

        values = {
            'order': order_sudo,
            'order_invoice_lines': order_invoice_lines,
            'order_line_type': order_line_type
        }
        values.update(get_records_pager(history, order))
        return request.render("website_portal_sale.orders_followup", values)

class cpo_electron_WebsiteSale(http.Controller):

    #@http.route(['/pcb'], type='http', auth="public", website=True)
    #def old_pcb(self, page=0, category=None, search='', ppg=False, ufile=None, **post):
    #    return request.redirect("/pcba")

    def __init__(self):
        self.session_active = {}
        return super(cpo_electron_WebsiteSale, self).__init__()

    # 服务条款
    @http.route('/service', type='http', auth='public', website=True)
    def cpoService(self, **kw):
        return request.render("website_cpo_sale.cpo_web_service")


    # PCBA点击跳转
    @http.route('/pcba_click_link', type='http', auth='public', website=True)
    def pcba_click_link(self, **kw):
        values = {}
        pcba_val = kw['cpo_create_pcba']
        for item in pcba_val:
            if item['name'] == 'csrf_token':
                pass
            else:
                values.update({
                    item['name']: item['value']
                })

        return request.render("website_cpo_sale.cpo_pcba_quotation_form", values)

    # PCBA 页面
    @http.route([
        '/pcba',
        '/pcba?source=<val>'
    ], type='http', auth="public", website=True)
    def shop(self, page=0, category=None, search='', login=None, edit=None, source=None, type=None, bom_id=False, ufile=None, **post):


        product_tmp_id = request.env.ref("website_cpo_sale.cpo_product_template_pcba_electron").product_tmpl_id
        if not product_tmp_id.website_published:
            product_tmp_id.write({'website_published':True})
        values = {
            'source': source,
            'path': '/pcba',
            'product_id': product_tmp_id,
            'bom_id': bom_id,
            'cpo_login': False,
            'edit': edit,
        }
        # 检查是否需要注册/登录才能报价
        try:
            # if not self.session_active:
            # 
            #     CpoQuotationRecordCode().get_website_source()
            # else:
            # cpo_quotation_record_code.SessionData().init_session_recode()
            CpoQuotationRecordCode().get_website_source()
            client_user_name = request.env.user.name
            if edit:
                edit_values = self.cpo_edit_order_pcba(edit)
                values.update({
                    'edit': edit,
                    'edit_values': edit_values,
                })
            if login:
                get_user_id = request.env.user.id
                if get_user_id != 4:
                    record_data = self.cpoRecordDateGet(get_user_id, type)
                    if not record_data:
                        values.update({
                            'login': False,
                        })
                    else:
                        values.update({
                            'edit_values': record_data,
                            'login': True
                        })
            # login_regist = request.env['cpo_login_and_register'].get_login_and_register_ingo()
            # if login_regist:
            #     for lr in login_regist:
            #         lr_boolean = lr.cpo_boolean
            #         if lr_boolean and client_user_name == 'Public user':
            #             values.update({
            #                 'cpo_login': True
            #             })
            #             break
        except Exception, e:
            _logger.error("website_sale postprocess: %s value has been dropped (empty or not writable)" % e)
        # 选择PCBA连接进入下单页面
        pcba_list = ['pcba_quantity', 'pcb_length', 'pcb_width', 'pcba_dip', 'pcba_smt']
        list_flag = False
        for list_item in pcba_list:
            if list_item in post.keys():
                list_flag = True
        if list_flag:
            values.update({
                'pcba_quantity': post['pcba_quantity'],
                'pcba_length': post['pcb_length'],
                'pcba_width': post['pcb_width'],
                'pcba_dip': post['pcba_dip'],
                'pcba_smt': post['pcba_smt'],
            })
        values = Website().get_seo_data(values)
        if type:
            if values.get('cpo_login'):
                return request.redirect("/web/login")
            if type == 'standard':
                return request.render("website_cpo_sale.website_smt_standard_template", values)
            elif type == 'material':
                return request.render("website_cpo_sale.website_smt_material_template", values)
            else:
                return request.render("website_cpo_sale.website_smt_no_material_template", values)
        else:
            return request.render("website_cpo_sale.pcba_quotation", values)
        # return request.render("website_cpo_sale.pcba_quotation", values)
        return values

    def cpo_edit_order_pcba(self, edit):
        """
        判断是否有编辑ID
        如果有获取数据并将数据返回页面
        :param edit:
        :return:
        """
        # 前面加入五位随机参数作为加密
        order_id = base64.b64decode(edit[5:]).decode()
        sale_order = request.env['sale.order'].sudo().search([('id', '=', order_id)])
        edit_values = {
            'edit_id': order_id,
            'product_uom_qty': sale_order.order_line.product_uom_qty,
            'pcb_length': sale_order.order_line.pcb_length,
            'pcb_width': sale_order.order_line.pcb_width,
            'smt_plug_qty': sale_order.order_line.smt_plug_qty,
            'smt_component_qty': sale_order.order_line.smt_component_qty,
            'layer_pcb': sale_order.order_line.layer_pcb,
            'pcb_thickness': sale_order.order_line.pcb_thickness,
            'pcb_special': sale_order.order_line.pcb_special,
            'surface_id': sale_order.order_line.surface_id.english_name,  # 表名处理
            'cpo_note': None,
            'bom_material_type': sale_order.order_line.bom_material_type,  # BOM 物料种类
            'quote_line': len(sale_order.quotation_line),
        }
        return edit_values

    def cpoRecordDateGet(self, user_id, type):
        """
        PCBA 报价，如果用户未登录，提示登录，跳转到登录界面，登录完返回该报价页面
        取最新的一条报价记录，返回数据
        :param user_id:
        :param type:
        :return:
        """
        quote_record, file_ids = None, None
        quote_signup_history = request.httprequest.cookies.get('quote_signup_history')
        if quote_signup_history:
            quote_history = json.loads(quote_signup_history)
            quote_record = request.env['cpo_pcba_record'].sudo().search([('id', '=', quote_history.get('quote_id'))])
            # redirect = werkzeug.utils.redirect('/pcb')
            # redirect.delete_cookie('quote_signup_history')
        else:
            cpo_cookie = request.httprequest.cookies.get('session_id')
            quote_record = request.env['cpo_pcba_record'].sudo().search([('session_id', '=', cpo_cookie)])
        if not quote_record:
            return False
        if quote_record.file_ids:
            file_ids = quote_record.file_ids
        edit_values = {
            'product_uom_qty': quote_record.quantity,
            'pcb_length': quote_record.lenght,
            'pcb_width': quote_record.width,
            'smt_plug_qty': quote_record.dip_qty,
            'smt_component_qty': quote_record.smt_qty,
            'layer_pcb': int(quote_record.smt_side),
            'pcb_thickness': quote_record.thickne,
            'pcb_special': 'No',
            'surface_id': 'Lead Free HASL',  # 表名处理
            'cpo_note': None,
            'bom_material_type': quote_record.bom_type,  # BOM 物料种类
            'quote_line': 0,
            'ir_file_ids': file_ids,
        }
        return edit_values

    @http.route([
        '/get_pcba_price',
    ], type='json', auth="public", website=True)
    def pcba_price(self, **post):
        """
        PCBA 报价计算
        # PCBA 计算
        route: /get_pcba_price
        :param post:
        :return:
        """
        cpo_price_list = {}
        smt_price_model = request.env['cpo_smt_price.smt'].sudo()
        try:
            # PCBA 传参
            qty = get_digi_data(post.get('pcba_value').get('cpo_quantity'))
            pcb_length = get_digi_data(post.get('pcba_value').get('cpo_length'), float)
            pcb_width = get_digi_data(post.get('pcba_value').get('cpo_width'), float)
            layer_pcb = get_digi_data(post.get('pcba_value').get('cpo_side'))
            if qty and layer_pcb and pcb_length and pcb_width:
                pcba_make_fee_no_bom = smt_price_model.pbca_and_pcb_price_integration(post) # 传参返回价格
                pcba_make_fee = pcba_make_fee_no_bom['pcba_fee'] # 获取PCBA价格
                if pcba_make_fee:
                    if post.get('cpo_select_pcb'):
                        pcb_make_fee = pcba_make_fee_no_bom['pcb_fee'] # 获取PCB价格
                        cpo_price_list.update({
                            'pcb_fee': pcb_make_fee,
                        })
                        pcb_special_value = cpo_price_list.get('pcb_fee').get('x_value').get('pcb_special')
                        post_special_value = post.get('pcb_value').get('pcb_special_requirements')
                        post_special_value['Total_holes'] = pcb_special_value['Total_holes']
                        post_special_value['Inner_hole_line'] = pcb_special_value['Inner_hole_line']
                        post_special_value['Number_core'] = pcb_special_value['Number_core']
                        post_special_value['PP_number'] = pcb_special_value['PP_number']
                        post_special_value['Blind_hole_structure'] = pcb_special_value['Blind_hole_structure']
                        post_special_value['Blind_and_buried_hole'] = pcb_special_value['Blind_and_buried_hole']
                        post_special_value['Min_line_width'] = pcb_special_value['Min_line_width']
                        post_special_value['Min_line_space'] = pcb_special_value['Min_line_space']
                        post_special_value['Min_aperture'] = pcb_special_value['Min_aperture']
                        post_special_value['Copper_weight_wall'] = pcb_special_value['Copper_weight_wall']
                        post_special_value['Countersunk_deep_holes'] = pcb_special_value['Countersunk_deep_holes']
                        post_special_value['Total_test_points'] = pcb_special_value['Total_test_points']

                    all_total = pcba_make_fee_no_bom.get('Total Cost')
                    cpo_price_list.update({
                        'smt_assembly_fee': pcba_make_fee.get('smt_assembly_fee', 0), # SMT价格
                        'stencil_fee': pcba_make_fee.get('stencil_fee', 0), # 钢网费
                        'jig_tool_fee': pcba_make_fee.get('jig_tool_fee', 0), # 夹具费
                        'freigth_fee': pcba_make_fee_no_bom.get('Shipping Cost', 0),  # yunfei
                        'test_tool_fee': pcba_make_fee.get('test_tool_fee', 0), # 测试架
                        'ele_tatol': all_total # 总价（预估价格）
                    })
                    post['cpo_price_list'] = cpo_price_list
                    # 检查用户是否登录
                    cpo_login = self.check_user_login()
                    if cpo_login:
                        source = request.httprequest.environ.get('HTTP_REFERER')
                        url = self.analysis_url(source)
                        cpo_url = self.analysis_url_return_data(source)
                        quote_id = self.getQuoteRecordId()
                        post.update({
                            'login': 'please log in first!',
                            'url': url,
                            'src': cpo_url.get('src'),
                            'type': cpo_url.get('type'),
                            'quote_id': quote_id,
                        })
                        return post
        except Exception, e:
            post['waring'] = {
                'warning': e
            }

        return post

    def analysis_url(self, url):
        """
        URL解析，返回路径
        :param url:
        :return:
        """
        cpo_url = None
        analysis = urlparse.urlsplit(url)
        if analysis.query:
            cpo_url = 'src='+analysis.path + '&' + analysis.query
        else:
            cpo_url = 'src='+analysis.path
        return cpo_url

    def analysis_url_return_data(self, url):
        """
        URL解析，返回对象
        :param url:
        :return:
        """
        vals = {}
        analysis = urlparse.urlsplit(url)
        if '&' in analysis.query:
            an_data = analysis.query.split('&')
            for a in an_data:
                ty_data = a.split('=')
                if ty_data[0] == 'type':
                    vals.update({
                        'src': analysis.path,
                        'type': ty_data[1],
                    })
                    break
        ty_data = analysis.query.split('=')
        if ty_data[0] == 'type':
            vals.update({
                'src': analysis.path,
                'type': ty_data[1],
            })
        return vals

    def check_user_login(self):
        """
        检查用户是否登录，强制用户登录接口
        时间：2019年12月10日14:05:57
        :return:
        """
        cpo_login = False
        client_user_name = request.env.user.name
        login_regist = request.env['cpo_login_and_register'].get_login_and_register_ingo()
        if login_regist:
            for lr in login_regist:
                lr_boolean = lr.cpo_boolean
                if lr_boolean and client_user_name == 'Public user':
                    cpo_login = True
                    break
        return cpo_login

    def getQuoteRecordId(self):
        """
        获取报价记录的第一条
        :return:
        """
        cpo_cookie = request.httprequest.cookies.get('session_id')
        quote_record = request.env['cpo_pcb_record'].sudo().search([('session_id', '=', cpo_cookie)])
        if not quote_record:
            return False
        quote_data = quote_record[0]
        return quote_data.id

    # PCB报价 计算
    @http.route([
        '/cpo_pcb_quotation',
    ], type='json', auth="public", website=True)
    def pcb_price(self, **post):
        pcb_quotation = False
        try:
            # 检查用户是否登录
            cpo_login = self.check_user_login()
            if cpo_login:
                source = request.httprequest.environ.get('HTTP_REFERER')
                url = self.analysis_url(source)
                # post['login'] = 'please log in first!'
                # post['url'] = '/web/login?' + cpo_url
                cpo_url = self.analysis_url_return_data(source)
                quote_id = self.getQuoteRecordId()
                if not quote_id:
                    quote_id = False
                post.update({
                    'login': 'please log in first!',
                    'url': url,
                    'src': cpo_url.get('src'),
                    'type': cpo_url.get('type'),
                    'quote_id': quote_id,
                })
                return post
            pcb_sale_quotation = request.env['sale.quotation'].sudo()
            pcb_quotation = pcb_sale_quotation.get_pcb_quotation_price(post)
            # pcb_quotation = pcb_sale_quotation.get_pcb_quotation_price(post)
            value = pcb_quotation['value']
            if value.get('PCB Area') >= 3.0:
                post['pcb_value']['pcb_test'] = 'E-test fixture'
            post['PCB Area'] = value['PCB Area']  # 面积
            post['Delivery Period'] = value['Delivery Period']  # 交期'

            pcb_price_detailed = {}
            pcb_price_detailed.update({
                'Special Process Cost': value['Special Process Cost'], # 特殊工艺费 spe_precess
                'Cost By': value['Cost By'],
                'Thickness Cost': value['Thickness Cost'],
                'Copper Cost': value['Copper Cost'],
                'Text Color Cost': value['Text Color Cost'],
                'Solder Mask Color Cost': value['Solder Mask Color Cost'],
                'Surface Cost': value['Surface Cost'],
                'Core&PP Cost': value['Core&PP Cost'],
                'Other Cost': value['Other Cost'],
                'Gold Finger Cost': value['Gold Finger Cost'],
                'Special Material Cost': value['Special Material Cost'],
                'Original Price': 0,
            })
            if value.get('Original Price'):
                pcb_price_detailed.update({
                    'Original Price': value['Original Price']
                })
            post['pcb_price_detailed'] = pcb_price_detailed
            post['Board Price Cost'] = value['Board Price Cost']  # (Board price)
            post['E-test Fixture Cost'] = value['E-test Fixture Cost']  #测试费
            # post['Stencil Cost'] = value['Stencil Cost']  #钢网费
            post['Film Cost'] = value['Film Cost']  #菲林费
            post['Process Cost'] = value['Process Cost']  #工艺费（跟特殊工艺费区别开）
            total_a = value['Total Cost'] + pcb_quotation['Shipping Cost']
            post['Total Cost'] = float('%.2f' % total_a)  # All fee
            post['Set Up Cost'] = value['Set Up Cost']  # 工程费(Set up cost)
            post['Shipping Cost'] = pcb_quotation['Shipping Cost']  # 运费
            post['cpo_expedited_list'] = value.get('cpo_quick_time_list')  # 加急列表
            # if value['pcb_special']['Total_holes']:
            #     post['pcb_special_requirements']['Total_holes'] = value['pcb_special']['Total_holes']
            #     post['pcb_special_requirements']['Inner_hole_line'] = value['pcb_special']['Inner_hole_line']
            #     post['pcb_special_requirements']['Number_core'] = value['pcb_special']['Number_core']
            #     post['pcb_special_requirements']['PP_number'] = value['pcb_special']['PP_number']
            #     post['pcb_special_requirements']['Blind_hole_structure'] = value['pcb_special']['Blind_hole_structure']
            #     post['pcb_special_requirements']['Blind_and_buried_hole'] = value['pcb_special']['Blind_and_buried_hole']
            #     post['pcb_special_requirements']['Min_line_width'] = value['pcb_special']['Min_line_width']
            #     post['pcb_special_requirements']['Min_line_space'] = value['pcb_special']['Min_line_space']
            #     post['pcb_special_requirements']['Min_aperture'] = value['pcb_special']['Min_aperture']
            #     post['pcb_special_requirements']['Copper_weight_wall'] = value['pcb_special']['Copper_weight_wall']
            #     post['pcb_special_requirements']['Countersunk_deep_holes'] = value['pcb_special']['Countersunk_deep_holes']
            #     post['pcb_special_requirements']['Total_test_points'] = value['pcb_special']['Total_test_points']
        except Exception,e:
            if pcb_quotation:
                error = pcb_quotation['warning']
                post.update({
                    'error': error,
                })
            else:
                error = 'data error'
                post.update({
                    'error': {'e': error},
                })
        return post

    # 钢网下单
    @http.route(['/stencil_order'], type='json', auth='public', website=True)
    def stencil_order(self, **post):
        stencil_quotiton = False
        try:
            stencil_quotiton = request.env['sale.quotation'].sudo()
            stencil_value = stencil_quotiton.get_steel_mesh_price(post)
            post['stencil_value'] = stencil_value
            post['stencil_data']['cpo_quantity'] = post.get('stencil_data').get('stencil_qty')
            if 'warning' in stencil_value.keys():
                post['error'] = stencil_value.get('warning')
        except Exception, e:
            post['error'] = e
        return post

    # PCB 加急计算
    @http.route([
        '/shop_pcb_confirm_urgent_service',
    ], type='json', auth="public", website=True)
    def pcb_confirm_urgent_service(self, **post):

        pcb_quotation = False
        try:
            pcb_sale_quotation = request.env['sale.quotation'].sudo()
            pcb_quotation = pcb_sale_quotation.get_pcb_quotation_price(post)
            # pcb_quotation = pcb_sale_quotation.get_pcb_quotation_price(post)
            value = pcb_quotation['value']

            post['PCB Area'] = value['PCB Area']  # 面积
            post['Delivery Period'] = value['Delivery Period']  # 交期'

            pcb_price_detailed = {}
            pcb_price_detailed.update({
                'Special Process Cost': value['Special Process Cost'],  # 特殊工艺费 spe_precess
                'Cost By': value['Cost By'],
                'Thickness Cost': value['Thickness Cost'],
                'Copper Cost': value['Copper Cost'],
                'Text Color Cost': value['Text Color Cost'],
                'Solder Mask Color Cost': value['Solder Mask Color Cost'],
                'Surface Cost': value['Surface Cost'],
                'Core&PP Cost': value['Core&PP Cost'],
                'Other Cost': value['Other Cost'],
                'Gold Finger Cost': value['Gold Finger Cost'],
                'Special Material Cost': value['Special Material Cost']
            })
            post['pcb_price_detailed'] = pcb_price_detailed
            post['Board Price Cost'] = value['Board Price Cost']  # (Board price)
            post['E-test Fixture Cost'] = value['E-test Fixture Cost']  # 测试费
            # post['Stencil Cost'] = value['Stencil Cost']  # 钢网费
            post['Film Cost'] = value['Film Cost']  # 菲林费
            post['Process Cost'] = value['Process Cost']  # 工艺费（跟特殊工艺费区别开）
            total_a = value['Total Cost'] + pcb_quotation['Shipping Cost']
            post['Total Cost'] = total_a  # All fee
            post['Set Up Cost'] = value['Set Up Cost']  # 工程费(Set up cost)
            post['Shipping Cost'] = pcb_quotation['Shipping Cost']  # 运费
            post['cpo_expedited_list'] = value.get('cpo_quick_time_list')  # 加急列表
            # if value['pcb_special']['Total_holes']:
            #     post['pcb_special_requirements']['Total_holes'] = value['pcb_special']['Total_holes']
            #     post['pcb_special_requirements']['Inner_hole_line'] = value['pcb_special']['Inner_hole_line']
            #     post['pcb_special_requirements']['Number_core'] = value['pcb_special']['Number_core']
            #     post['pcb_special_requirements']['PP_number'] = value['pcb_special']['PP_number']
            #     post['pcb_special_requirements']['Blind_hole_structure'] = value['pcb_special']['Blind_hole_structure']
            #     post['pcb_special_requirements']['Blind_and_buried_hole'] = value['pcb_special'][
            #         'Blind_and_buried_hole']
            #     post['pcb_special_requirements']['Min_line_width'] = value['pcb_special']['Min_line_width']
            #     post['pcb_special_requirements']['Min_line_space'] = value['pcb_special']['Min_line_space']
            #     post['pcb_special_requirements']['Min_aperture'] = value['pcb_special']['Min_aperture']
            #     post['pcb_special_requirements']['Copper_weight_wall'] = value['pcb_special']['Copper_weight_wall']
            #     post['pcb_special_requirements']['Countersunk_deep_holes'] = value['pcb_special'][
            #         'Countersunk_deep_holes']
            #     post['pcb_special_requirements']['Total_test_points'] = value['pcb_special']['Total_test_points']
        except Exception, e:
            if pcb_quotation:
                error = pcb_quotation['warning']
            else:
                error = e
            post.update({
                'error': error,
                # 'value': pcb_quotation['value']['value']
            })
        return post

    # PCBA 阶梯价计算
    @http.route([
        '/get_stair_price',
    ], type='json', auth="public", website=True)
    def cpo_stair_price(self, **post):
        smt_price_model = request.env['cpo_smt_price.smt'].sudo()
        cpo_quantity = int(post.get('pcba_value').get('cpo_quantity'))
        qty_list = []
        price_list = []
        n = 0
        while n < 4:
            if n < 1:
                cpo_quantity = cpo_quantity
            else:
                cpo_quantity += 50
            qty_list.append(cpo_quantity)
            n += 1
        try:
            for list_item in qty_list:
                if post.get('cpo_select_pcb'):
                    post['pcb_value']['cpo_quantity'] = str(list_item)
                post['pcba_value']['cpo_quantity'] = str(list_item)
                # PCBA 传参
                qty = get_digi_data(post.get('pcba_value').get('cpo_quantity'))
                pcb_length = get_digi_data(post.get('pcba_value').get('cpo_length'), float)
                pcb_width = get_digi_data(post.get('pcba_value').get('cpo_width'), float)
                layer_pcb = get_digi_data(post.get('pcba_value').get('cpo_side'))
                if qty and layer_pcb and pcb_length and pcb_width:
                    pcba_return_price = smt_price_model.pbca_and_pcb_price_integration(post)  # 传参返回价格
                    cpo_price = pcba_return_price.get('Total Cost', 0)
                    cpo_qty = post.get('pcba_value').get('cpo_quantity')
                    price_list.append({
                        cpo_qty: cpo_price
                    })

        except Exception, e:
            post['warning'] = e

        post['price_list'] = price_list

        return post

    # PCBA 阶梯价选择
    @http.route('/get_try_qty', type='json', auth="public", website=True)
    def cpo_try_qty(self, **post):
        post['pcba_value']['cpo_quantity'] = post['select_qty']
        cpo_price_list = {}
        smt_price_model = request.env['cpo_smt_price.smt'].sudo()
        try:
            # PCBA 传参
            qty = get_digi_data(post.get('pcba_value').get('cpo_quantity'))
            pcb_length = get_digi_data(post.get('pcba_value').get('cpo_length'), float)
            pcb_width = get_digi_data(post.get('pcba_value').get('cpo_width'), float)
            layer_pcb = get_digi_data(post.get('pcba_value').get('cpo_side'))
            if qty and layer_pcb and pcb_length and pcb_width:
                post['pcba_value']['cpo_quantity'] = post['select_qty']
                if post.get('cpo_select_pcb'):
                    post['pcb_value']['cpo_quantity'] = post['select_qty']
                pcba_make_fee_no_bom = smt_price_model.pbca_and_pcb_price_integration(post)  # 传参返回价格
                pcba_make_fee = pcba_make_fee_no_bom.get('pcba_fee')  # 获取PCBA价格
                if pcba_make_fee:
                    if post.get('cpo_select_pcb'):
                        pcb_make_fee = pcba_make_fee_no_bom.get('pcb_fee')  # 获取PCB价格
                        cpo_price_list.update({
                            'pcb_fee': pcb_make_fee,
                        })
                        pcb_special_value = cpo_price_list.get('pcb_fee').get('x_value').get('pcb_special')
                        post_special_value = post.get('pcb_value').get('pcb_special_requirements')
                        # post_special_value['Total_holes'] = pcb_special_value['Total_holes']
                        # post_special_value['Inner_hole_line'] = pcb_special_value['Inner_hole_line']
                        # post_special_value['Number_core'] = pcb_special_value['Number_core']
                        # post_special_value['PP_number'] = pcb_special_value['PP_number']
                        # post_special_value['Blind_hole_structure'] = pcb_special_value['Blind_hole_structure']
                        # post_special_value['Blind_and_buried_hole'] = pcb_special_value['Blind_and_buried_hole']
                        # post_special_value['Min_line_width'] = pcb_special_value['Min_line_width']
                        # post_special_value['Min_line_space'] = pcb_special_value['Min_line_space']
                        # post_special_value['Min_aperture'] = pcb_special_value['Min_aperture']
                        # post_special_value['Copper_weight_wall'] = pcb_special_value['Copper_weight_wall']
                        # post_special_value['Countersunk_deep_holes'] = pcb_special_value['Countersunk_deep_holes']
                        # post_special_value['Total_test_points'] = pcb_special_value['Total_test_points']

                    all_total = pcba_make_fee_no_bom.get('Total Cost')
                    cpo_price_list.update({
                        'smt_assembly_fee': pcba_make_fee.get('smt_assembly_fee', 0),  # SMT价格
                        'stencil_fee': pcba_make_fee.get('stencil_fee', 0),  # 钢网费
                        'jig_tool_fee': pcba_make_fee.get('jig_tool_fee', 0),  # 夹具费
                        'freigth_fee': pcba_make_fee_no_bom.get('Shipping Cost', 0),  # yunfei
                        'test_tool_fee': pcba_make_fee.get('test_tool_fee', 0),  # 测试架
                        'ele_tatol': all_total  # 总价（预估价格）
                    })
                    post['cpo_price_list'] = cpo_price_list

        except Exception, e:
            post['waring'] = e

        return post

    # PCB 阶梯价 get_pcb_stair_price
    @http.route('/get_pcb_stair_price', type='json', auth="public", website=True)
    def cpo_pcb_stair_price(self, **post):
        """
        PCB 阶梯价获取，目前基于客户填写的基数上增加50作为阶梯价
        :param post:
        :return:
        """
        cpo_quantity = int(post.get('pcb_value').get('cpo_quantity'))
        qty_list = []
        price_list = []
        n = 0
        while n < 4:
            if n < 1:
                cpo_quantity = cpo_quantity
            else:
                cpo_quantity += 50
            qty_list.append(cpo_quantity)
            n += 1
        pcb_quotation = False
        try:
            for qty_item in qty_list:
                post['pcb_value']['cpo_quantity'] = str(qty_item)
                pcb_sale_quotation = request.env['sale.quotation'].sudo()
                pcb_quotation = pcb_sale_quotation.get_pcb_quotation_price(post)
                price_list.append({
                    qty_item: pcb_quotation.get('value').get('Total Cost') + pcb_quotation.get('Shipping Cost')
                })

        except Exception, e:
            post['waring'] = e
        post['price_list'] = price_list
        return post

    # PCB 阶梯价选择
    @http.route('/get_pcb_try_qty', type='json', auth="public", website=True)
    def cpo_pcb_try_qty(self, **post):
        """
        PCB 阶梯价选择计算，将数据返回前端
        :param post:
        :return:
        """
        pcb_quotation = False
        try:
            post['pcb_value']['cpo_quantity'] = post.get('this_val')
            pcb_sale_quotation = request.env['sale.quotation'].sudo()
            pcb_quotation = pcb_sale_quotation.get_pcb_quotation_price(post)
            value = pcb_quotation['value']

            post['PCB Area'] = value['PCB Area']  # 面积
            post['Delivery Period'] = value['Delivery Period']  # 交期'

            pcb_price_detailed = {}
            pcb_price_detailed.update({
                'Special Process Cost': value['Special Process Cost'],  # 特殊工艺费 spe_precess
                'Cost By': value['Cost By'],
                'Thickness Cost': value['Thickness Cost'],
                'Copper Cost': value['Copper Cost'],
                'Text Color Cost': value['Text Color Cost'],
                'Solder Mask Color Cost': value['Solder Mask Color Cost'],
                'Surface Cost': value['Surface Cost'],
                'Core&PP Cost': value['Core&PP Cost'],
                'Other Cost': value['Other Cost'],
                'Gold Finger Cost': value['Gold Finger Cost'],
                'Special Material Cost': value['Special Material Cost'],
                'Original Price': 0,
            })
            if value.get('Original Price'):
                pcb_price_detailed.update({
                    'Original Price': value['Original Price']
                })
            post['pcb_price_detailed'] = pcb_price_detailed
            post['Board Price Cost'] = value['Board Price Cost']  # (Board price)
            post['E-test Fixture Cost'] = value['E-test Fixture Cost']  # 测试费
            # post['Stencil Cost'] = value['Stencil Cost']  # 钢网费
            post['Film Cost'] = value['Film Cost']  # 菲林费
            post['Process Cost'] = value['Process Cost']  # 工艺费（跟特殊工艺费区别开）
            total_a = value['Total Cost'] + pcb_quotation['Shipping Cost']
            post['Total Cost'] = total_a  # All fee
            post['Set Up Cost'] = value['Set Up Cost']  # 工程费(Set up cost)
            post['Shipping Cost'] = pcb_quotation['Shipping Cost']  # 运费
            post['cpo_expedited_list'] = value.get('cpo_quick_time_list')  # 加急列表
            # if value['pcb_special']['Total_holes']:
            #     post['pcb_special_requirements']['Total_holes'] = value['pcb_special']['Total_holes']
            #     post['pcb_special_requirements']['Inner_hole_line'] = value['pcb_special']['Inner_hole_line']
            #     post['pcb_special_requirements']['Number_core'] = value['pcb_special']['Number_core']
            #     post['pcb_special_requirements']['PP_number'] = value['pcb_special']['PP_number']
            #     post['pcb_special_requirements']['Blind_hole_structure'] = value['pcb_special']['Blind_hole_structure']
            #     post['pcb_special_requirements']['Blind_and_buried_hole'] = value['pcb_special'][
            #         'Blind_and_buried_hole']
            #     post['pcb_special_requirements']['Min_line_width'] = value['pcb_special']['Min_line_width']
            #     post['pcb_special_requirements']['Min_line_space'] = value['pcb_special']['Min_line_space']
            #     post['pcb_special_requirements']['Min_aperture'] = value['pcb_special']['Min_aperture']
            #     post['pcb_special_requirements']['Copper_weight_wall'] = value['pcb_special']['Copper_weight_wall']
            #     post['pcb_special_requirements']['Countersunk_deep_holes'] = value['pcb_special'][
            #         'Countersunk_deep_holes']
            #     post['pcb_special_requirements']['Total_test_points'] = value['pcb_special']['Total_test_points']
        except Exception, e:
            if pcb_quotation:
                error = pcb_quotation['warning']
            else:
                error = e
            post.update({
                'error': error,
            })
        return post

    #合并订单操作
    #讲PCB加入PCBA订单中
    @http.route([
        '/cpo_merger_order',
    ], type='json', auth="public", website=True)
    def cpo_merger_order_select(self, **post):
        cpo_sale_order_name = post['cpo_sale_order_name'].strip()
        cpo_sale_order = request.env['sale.order'].sudo().search([('name', '=', cpo_sale_order_name)])
        if cpo_sale_order.product_type == "PCBA" and cpo_sale_order.pcb_supply == "chinapcbone":
            post['cpo_sale_order_name'] = cpo_sale_order.name
            post['pcb_supply'] = cpo_sale_order.pcb_supply
            post['product_type'] = cpo_sale_order.product_type
            post['order_id'] = cpo_sale_order.id
        return post


    @http.route([
        '/cpo_method_of_supply',
    ], type='json', auth="public", website=True)
    def cpo_merger_order_select(self, **post):
        """
        #如果是由ChinaPCBONE提供，则要求客户添加PCB订单
        #讲PCB加入PCBA订单中
        :param post:
        :return:
        """
        cpo_sale_order_name = post['cpo_sale_order_name'].strip()
        cpo_sale_order = request.env['sale.order'].sudo().search([('name', '=', cpo_sale_order_name)])
        if cpo_sale_order.product_type == "PCBA" and cpo_sale_order.pcb_supply == "chinapcbone":
            cpo_quotation_line = request.env['sale.quotation.line'].sudo().search([('order_id','=',cpo_sale_order.id)])
            if cpo_quotation_line:
                pass
            else:
                post['pcb_supply'] = cpo_sale_order.pcb_supply
        return post


    @http.route([
        '/get_electron_type',
    ], type='json', auth="public", website=True)
    def get_electron_type(self, **post):
        p_type = post.get('product_type')
        if p_type == 'PCBA':
            return PCBA_ELECTRON_FILE_TYPE
        return PCB_ELECTRON_FILE_TYPE


    #def get_list_count_item(self, l, i):
    #    return len(l)-len([x for x in l if x!=i])

    #def recheck_bom_file_content(self, rows):
    #    rows = [x for x in rows if list(set(x))!=['']]
    #    rows_len_list = [len(list(set(x))) for x in rows]
    #    rows_len_list_only = list(set(rows_len_list))
    #    row_dict = {}
    #    for row in rows_len_list_only:
    #        row_dict[row] = self.get_list_count_item(rows_len_list, row)
    #    #get Header cols len
    #    header_len = [x[0] for x in row_dict.items() if x[1]==max(row_dict.values())][0]
    #    #remove title
    #    rows = [x for x in rows if len(list(set(x)))==header_len]
    #    return rows

    @http.route([
        '/pcba/ele/check_attach_file',
    ], type='http', auth="public", website=True)
    def shop_check_attach_file(self, return_url=None, atta_id=None, **post):
        """
        点击按钮，进行BOM分析(解析BOM)
        :param return_url:
        :param atta_id:
        :param post:
        :return:
        """
        if not atta_id:
            return False
        try:
            atta_row = request.env['ir.attachment'].sudo().search([('id','=',int(atta_id))])
        except Exception,e:
            return False
        bom_row = self.get_bom_obj(atta_row)
        if bom_row:
            if request.env.uid != request.website.user_id.id and request.env.uid not in bom_row.partner_id.user_ids.mapped('id'):
                return False
        data = atta_row.datas
        rows=[]
        sh_header = [""]
        if data:
            try:
                excel = xlrd.open_workbook(file_contents=base64.b64decode(data))
                sh = excel.sheet_by_index(0)
                #for ry in range(0,sh.ncols):
                #    if sh.cell(0,ry).value:
                #        sh_header.append(sh.cell(0,ry).value)
                for rx in range(0,sh.nrows):
                    cols = []
                    for ry in range(0,sh.ncols):
                        cols.append(sh.cell(rx,ry).value)

                    rows.append(cols)
                rows = recheck_bom_file_content(rows)
                for row in rows:
                    for x_row in row:
                        sh_header.append(x_row)
                    break
            except Exception,e:
                pass
        atta_obj = request.env['ir.attachment'].search([('id', '=', atta_id)])
        res_obj = request.env[atta_obj.res_model].sudo().search([('id', '=', atta_obj.res_id)])
        fields_ref = {}
        supply_ref = {}
        [fields_ref.update({x.cpo_title: x.src_title}) for x in res_obj.bom_fields_line]
        supply_ref = [x.mfr for x in res_obj.bom_supply_line if x.supply=='customer']
        cpo_mfr_p_n = fields_ref.get('cpo_mfr_p_n')
        cpo_mfr_p_n_index = 0
        if cpo_mfr_p_n:
            cpo_mfr_p_n_index = sh_header.index(cpo_mfr_p_n)
        values = {
            'atta_id': atta_id,
            'txt': rows,
            'return_url': return_url,
            'sh_header': sh_header,
            'fields_ref': fields_ref,
            'supply_ref': supply_ref,
            'cpo_mfr_p_n_index':  cpo_mfr_p_n_index-1 if cpo_mfr_p_n_index else -1,
        }

        # material_data = request.env['material.gift'].sudo()
        # if material_data:
        #     get_material = material_data.get_home_show()
        #     values.update({
        #         'material_dt': get_material
        #     })

        return request.render("website_cpo_sale.cpo_check_excel_file", values)

    @http.route([
        '/pcba/ele/delete_attach_file',
    ], type='http', auth="public", website=True)
    def shop_delete_attach_file(self, return_url=None, atta_id=None, **post):
        """
        购物车删除已上传的附件
        :param return_url: 返回路径
        :param atta_id: 附件ID
        :param post:
        :return:
        """
        if not atta_id:
            return request.redirect("/shop/cart")
        try:
            atta_row = request.env['ir.attachment'].sudo().search([('id','=',int(atta_id))]).unlink()
        except Exception,e:
            pass
        return request.redirect("/shop/cart")

    @http.route([
        '/confirm/order/delete_attach_file',
    ], type='http', auth="public", website=True)
    def confirm_delete_attach_file(self, return_url=None, atta_id=None, **post):
        """
        订单带确认状态删除已上传的附件，当订单设置为允许修改的时候才可以上传
        :param return_url: 返回路径
        :param atta_id: 附件ID
        :param post:
        :return:
        """
        if not atta_id:
            return request.redirect("/my/waitconf")
        try:
            atta_row = request.env['ir.attachment'].sudo().search([('id','=',int(atta_id))]).unlink()
        except Exception,e:
            pass
        return request.redirect("/my/waitconf")

    def get_bom_obj(self, atta_row):
        sale_order = request.env['sale.order']
        if atta_row.res_model == 'sale.order':
            sale_row = sale_order.sudo().search([('id', '=', atta_row.res_id)])
            order_pcba_line = sale_row.order_line.filtered(lambda x:x.product_id.name == 'PCBA')
            return order_pcba_line.bom_rootfile
        elif atta_row.res_model == 'cpo_offer_bom.bom':
            bom_pool = request.env['cpo_offer_bom.bom']
            return bom_pool.sudo().search([('id', '=', atta_row.res_id)])
        return False

    # Check the order BOM
    @http.route([
        '/pcb_electron/cpo_pcba_data_check',
    ], type='json', auth="public", website=True)
    def cpo_pcba_data_check(self, **post):
        """
        检查BOM是否已分析
        :param post:
        :return:
        """
        sale_pool = request.env['sale.order'].sudo()
        post['pcb_supply_method'] = self.cpo_sale_order_shipping_method(post)
        for order_id in post['order_ids']:
            sale_obj = sale_pool.search([('id', '=', int(order_id))])
            if sale_obj.check_state == 'check_off':
                post['check_state'] = sale_obj.check_state
                post['check_order_id'] = int(sale_obj.id) - 1
                break
            else:
                post['check_state'] = sale_obj.check_state
        post['error'] = self.cpo_atta_data_check(post)
        return post


    #@http.route([
        #'/pcb_order/cpo_pcb_type',
    #], type='json', auth="public", website=True)
    def cpo_atta_data_check(self, post):
        """
        判断订单类型
        :param post:
        :return:
        """
        sale_pool = request.env['sale.order'].sudo()
        # for order_id in post['order_ids']:
        order_ids = post['order_ids']
        res = []
        has_file_type_obj = post.get('has_file_type_obj')
        for order_id in order_ids:
            error_obj = {}
            sale_obj = sale_pool.search([('id', '=', int(order_id))])
            pcba_order = sale_obj.order_line.only_pcba_order_line()
            pcb_order = sale_obj.order_line.only_pcb_order_line()
            # stencil_order = sale_obj.order_line.only_stencil_order_line()
            #处理pcba订单
            if pcba_order and not pcb_order:
                order_type_list = ORDER_TYPE_PCBA
                if sale_obj.check_state != 'check_on':
                    error_obj['bom_check_state'] = sale_obj.check_state
                    error_obj['order_name'] = sale_obj.name
                #else:
                    #error_obj['bom_check_state'] = True
            #处理PCB订单
            elif not pcba_order and pcb_order:
                order_type_list = ORDER_TYPE_PCB
            elif not pcba_order and not pcb_order:
                order_type_list = []
            #res[order_id] = order_type_list
            if set(order_type_list)-set(has_file_type_obj.get(order_id)):
                error_obj['order_name'] = sale_obj.name
                error_obj['upload_error'] = list(set(order_type_list)-set(has_file_type_obj.get(order_id)))
                error_obj['bom_check_state'] = False
            if error_obj:
                res.append(error_obj)
                #res[sale_obj.name] = list(set(order_type_list)-set(has_file_type_obj.get(order_id)))
        return res



    def cpo_sale_order_shipping_method(self, post):
        """
        # 判断PCB是否为客供，或者部分客供
        :param post:
        :return:
        """
        order_ids = post['order_ids']
        supply_method_list = []
        for order_id in order_ids:
            supply_method = {}
            cpo_sale_order = request.env['sale.order'].sudo().search([('id', '=', order_id)])
            if cpo_sale_order.product_type == "PCBA" and cpo_sale_order.pcb_supply == "chinapcbone":
                cpo_quotation_line = request.env['sale.quotation.line'].sudo().search([('order_id', '=', int(order_id))])
                if not cpo_quotation_line.id:
                    supply_method['pcb_supply_message'] = "Please add a PCB order"
                    supply_method['pcb_supply'] = "Made in ChinaPCBOne"
                    supply_method['pcb_order_name'] = cpo_sale_order.name
                if supply_method:
                    supply_method_list.append(supply_method)

        return supply_method_list

    #get order number
    @http.route([
        '/pcb_user_expressage',
    ], type='json', auth="public", website=True)
    def pcb_user_expressage(self, **post):
        # express_page = request.website_cpo_sale.portal_my_express()
        if not post:
            pass
        else:
            express_number = post['express_number']
            express_provider = post['express_company']
            sale_express = request.env['sale_order.express_waybill'].sudo()
            sale_pool = request.env['sale.order'].sudo()
            sale_obj = sale_pool.search([('id', '=', post['order_number'])])
            # if express_number:
            try:
                sale_express.create({
                    'express_number': express_number,
                    'express_provider': express_provider,
                    'order_number': sale_obj.id
                })
            except Exception, e:
                post.update({'error':e})
                pass
        return post

    #Delete express
    @http.route([
        '/user_delete_express',
    ], type='json', auth="public", website=True)
    def user_delete_express(self, **post):
        sale_express = request.env['sale_order.express_waybill'].sudo()
        sale_obj = sale_express.search([('express_number', '=', post['express_no'])])
        sale_obj.unlink()
        return post

    #cpo check
    @http.route([
        '/shop/cart/cpo_checked',
    ], type='json', auth='public', website=True)
    def shop_cart_cpo_checked(self, **post):
        # post['checked'] = 'check_true'
        id_list = post.get('order_id_ls')
        id_list = [int(x) for x in id_list]
        cpo_lineid = post['cpo_lineID']
        # sale_check = request.env['sale.order.line'].sudo()
        sale_order_check = request.env['sale.order'].sudo()
        if type(cpo_lineid) == list:
            line_ls = [int(x) for x in cpo_lineid]
            sale_check_obj = sale_order_check.search([('id', 'in', line_ls)])
            for lineid in sale_check_obj:
                # sale_check_obj.write({'cpo_checked': post['checked']})
                lineid.order_line.cpo_checked = post['checked']
        else:
            sale_check_obj = sale_order_check.search([('id', '=', cpo_lineid)])
            sale_check_obj.order_line.cpo_checked = post['checked']
        sale_ids = sale_order_check.search([('id', 'in', id_list)])
        values = {
            'website_sale_order_ids': sale_ids,
        }
        return {
            'order_total_temp': request.env['ir.ui.view'].render_template(
                'website_cpo_sale.cpo_sale_total_template', values)
        }

    @http.route([
        '/pcb_electron/update_ele_supply',
    ], type='json', auth="public", website=True)
    def update_ele_supply(self, ref=None, field_ref=None, checked=None, atta_id=None, express_provider=None, express_number=None, **post):
        vals = {}
        atta_pool = request.env['ir.attachment'].sudo()
        atta_obj = atta_pool.search([('id', '=', get_digi_data(atta_id))])
        if atta_obj.res_model == 'sale.order':
            self.update_bom_set_data_to_saleorder(
                ref=ref,
                field_ref=field_ref,
                checked=checked,
                atta_obj=atta_obj,
                express_provider=express_provider,
                express_number=express_number
            )
        elif atta_obj.res_model == 'cpo_offer_bom.bom':
            self.update_bom_set_data_to_offer_bom(
                ref=ref,
                field_ref=field_ref,
                checked=checked,
                atta_obj=atta_obj,
                express_provider=express_provider,
                express_number=express_number
            )
        return ELECTRON_FILE_TYPE

    # 当客户check BOM的时候将BOM的状态改变为check_on
    def update_bom_set_data_to_saleorder(self, ref=None, field_ref=None, checked=None, atta_obj=None, express_provider=None, express_number=None):
        checked = 'check_on'
        fields_pool = request.env['cpo_bom_fields.line'].sudo()
        bom_supply = request.env['cpo_bom_supply.list'].sudo()
        sale_pool = request.env['sale.order'].sudo()
        sale_expres = request.env['sale_order.express_waybill'].sudo()
        sale_obj = sale_pool.search([('id', '=', atta_obj.res_id)])
        #update bom fields ref for sale order
        #update express information
        if express_provider and express_number:
            sale_expres.create({
                'express_number': express_number,
                'express_provider': express_provider,
                'order_number': sale_obj.id
            })
        sale_obj.write({'check_state': checked})
        #update supply ref
        #if not ref:
        bom_supply.del_old_data(order_id=sale_obj.id)
        for row in ref:
            row.update({'order_id': sale_obj.id})
            bom_supply.to_create_ref(row)

        #update bom fields ref for cpo_offer_bom.bom
        #if not field_ref:
        fields_pool.del_old_data(order_id=sale_obj.id)
        for row in field_ref:
            row.update({'order_id': sale_obj.id})
            fields_pool.to_create_fields_ref(row)
        bom_res = sale_obj.create_new_bom_for_saleorder(request.env.user.partner_id.id)
        bom_obj = bom_res.get('bom_obj')
        bom_atta_obj = bom_res.get('atta_obj')
        self.update_bom_set_data_to_offer_bom(
            ref=ref,
            field_ref=field_ref,
            checked=checked,
            atta_obj=bom_atta_obj,
            express_provider=express_provider,
            express_number=express_number
        )
        #add bom fields ref...
        return True

    def update_bom_set_data_to_offer_bom(self, ref=None, field_ref=None, checked=None, atta_obj=None, express_provider=None, express_number=None):
        fields_pool = request.env['cpo_bom_fields.line_for_bom'].sudo()
        bom_supply = request.env['cpo_bom_supply.list_for_bom'].sudo()
        bom_pool = request.env['cpo_offer_bom.bom'].sudo()
        bom_expres = request.env['express_waybill.line_for_bom'].sudo()
        bom_obj = bom_pool.search([('id', '=', atta_obj.res_id)])
        #update express information
        if express_provider and express_number:
            bom_expres.create({
                'express_number': express_number,
                'express_provider': express_provider,
                'bom_id': bom_obj.id
            })
        #update supply ref
        #if not ref:
        bom_supply.del_old_data(bom_id=bom_obj.id)
        for row in ref:
            row.update({'bom_id': bom_obj.id})
            bom_supply.to_create_ref(row)
        #update bom fields ref
        #if not field_ref:
        fields_pool.del_old_data(bom_id=bom_obj.id)
        for row in field_ref:
            row.update({'bom_id': bom_obj.id})
            fields_pool.to_create_fields_ref(row)
        bom_obj.to_auto_import_date()
        return True

    @http.route([
        '/pcb_electron/check_upload_file',
    ], type='json', auth="public", website=True)
    def shop_product_check_upload(self, datas=None, name=None, tag_ids=None, **post):
        rows=[]
        excel = xlrd.open_workbook(file_contents=base64.b64decode(datas))
        sh = excel.sheet_by_index(0)
        for rx in range(0,sh.nrows):
            cols = []
            for ry in range(0,sh.ncols):
                cols.append(sh.cell(rx,ry).value)
            rows.append(cols)
        values = {
            'txt': rows
        }
        return rows#request.render("website_cpo_sale.cpo_check_excel_file", values)

    def get_tag_ids(self, tag_num):
        file_list = ELECTRON_FILE_TYPE
        tag_ids = None
        for tag_id in file_list:
            if tag_id.get('id') == tag_num:
                tag_ids = tag_id.get('text')
            elif tag_id.get('text') == tag_num:
                tag_ids = tag_id.get('text')
        return tag_ids

    @http.route([
        '/pcb_electron/upload_file',
    ], type='json', auth="public", website=True)
    def shop_product_upload(self, datas=None, name=None, tag_ids=None, **post):
        """
        在已创建的订单中上传文件，
        :param datas:
        :param name:
        :param tag_ids:
        :param post:
        :return:
        """
        error = ''
        tag_val = self.get_tag_ids(tag_ids)
        #for row in ELECTRON_FILE_TYPE:
        #    if row.get('id') == tag_ids:
        #        tag_val = row.get('text')
        #        break
        size_length = 30 * 1024 * 1024
        if datas and len(base64.b64decode(datas)) > size_length:
            return {'error': 'file size length must less than 30M.'}
        if not datas:
            return {'error': 'file format error.'}
        atta_pool = request.env['ir.attachment'].sudo()
        if not post.get('order_id'):
            return self.shop_upload_partner_attachment(user=request.env.user, tag_val=tag_val, name=name, datas=datas)
        order_id = int(post.get('order_id'))
        ufiles = request.httprequest.files.getlist('upload')
        sale_order = request.env['sale.order'].sudo().search([('id', '=', order_id)])
        atta_pool.sudo().search([('description','=',tag_val),('res_id', '=', order_id),('res_model', '=', 'sale.order')]).unlink()

        #upload attachment file to sale_order
        update_res = sale_order.create_atta_for_saleorder(order_id=sale_order.id, name=name, tag_val=tag_val, datas=datas)
        has_atta = atta_pool.search([('datas','=',datas),('name','=',name),('res_id', '=', order_id),('res_model', '=', 'sale.order')])
        #if has_atta:
        #    if has_atta.description != tag_val:
        #        has_atta.description = tag_val
        #    else:
        #        error = 'already has atta file'
        #else:
        #    att_id = self.create_atta_for_saleorder(order_id=sale_order.id, name=name, tag_val=tag_val, datas=datas)

        #    #def orderLine bom fields ref in updated bom attachment file.
        #    sale_order.write({'bom_fields_line': [(2,x.id) for x in sale_order.bom_fields_line]})
        res = {
            'is_bom':True if has_atta.description == 'BOM File' else False,
            'url':'/shop/cart',
            'error':update_res.get('error'),
            'atta_id':has_atta.id,
        }
        return res

    @http.route([
        '/confirm/order/upload_file',
    ], type='json', auth="public", website=True)
    def confirm_order_upload(self, datas=None, name=None, tag_ids=None, **post):
        """
        订单上传文件和订单数据不符合时，允许客户重新上传文件
        :param datas:
        :param name:
        :param tag_ids:
        :param post:
        :return:
        """
        tag_val = self.get_tag_ids(tag_ids)
        size_length = 30 * 1024 * 1024
        if datas and len(base64.b64decode(datas)) > size_length:
            return {'error': 'file size length must less than 30M.'}
        if not datas:
            return {'error': 'file format error.'}
        atta_pool = request.env['ir.attachment'].sudo()
        if not post.get('order_id'):
            return self.shop_upload_partner_attachment(user=request.env.user, tag_val=tag_val, name=name, datas=datas)
        order_id = int(post.get('order_id'))
        ufiles = request.httprequest.files.getlist('upload')
        sale_order = request.env['sale.order'].sudo().search([('id', '=', order_id)])
        if sale_order.cpo_lock_bool:
            atta_pool.sudo().search(
                [('description', '=', tag_val), ('res_id', '=', order_id), ('res_model', '=', 'sale.order')]).unlink()
            # upload attachment file to sale_order
            update_res = sale_order.create_atta_for_saleorder(order_id=sale_order.id, name=name, tag_val=tag_val,
                                                              datas=datas)
            has_atta = atta_pool.search(
                [('datas', '=', datas), ('name', '=', name), ('res_id', '=', order_id), ('res_model', '=', 'sale.order')])
            res = {
                'is_bom': True if has_atta.description == 'BOM File' else False,
                'url': '/my/waitconf',
                'error': update_res.get('error'),
                'atta_id': has_atta.id,
            }
        else:
            res = {
                'error': "Please refresh the page !",
            }
        return res

    def shop_upload_partner_attachment(self, user, tag_val, name, datas):
        """
        在后台BOM管理中创建一个BOM单
        :param user:
        :param tag_val:
        :param name:
        :param datas:
        :return:
        """
        error = ''
        bom_pool = request.env['cpo_offer_bom.bom'].sudo()
        atta_id = bom_pool.create_atta_for_new_bom(partner_id=user.partner_id.id, tag_val=tag_val, name=name, datas=datas)
        res = {
            'is_bom':True,
            'atta_id': atta_id.get('atta_id'),
            'error':error
        }
        #return request.redirect("/pcba")
        return res

    #def create_atta_for_saleorder(self, order_id, name, tag_val, datas):
    #    vals = {
    #        'name':name,
    #        'description':tag_val,
    #        'res_model':'sale.order',
    #        'type': 'binary',
    #        'public': True,
    #        'datas':datas,
    #        'res_id':order_id,
    #        'datas_fname':name,
    #    }
    #    return request.env['ir.attachment'].sudo().create(vals)


class WebsiteSaleElectron(WebsiteSale):

    @http.route(['/shop'], type='http', auth="public", website=True)
    def shop(self, page=0, category=None, search='', ppg=False, **post):
        return request.redirect("/pcba")

    @http.route(['/shop/product/<model("product.template"):product>'], type='http', auth="public", website=True)
    def product(self, product, category='', search='', **kwargs):
        #values = self.old_product(product=product, category=category, search=search, kwargs=kwargs)
        values = self.old_product(product, category, search, kwargs=kwargs)
        #values.update({'abc':'AA'})
        values['cpo_quantity'] = kwargs.get('cpo_quantity') #PCBA 数量
        values['pcb_qty'] = kwargs.get('pcb_qty') # PCB 数量
        values['cpo_side'] = kwargs.get('cpo_side') #PCBA 单双面贴片
        values['cpo_smt_qty'] = kwargs.get('cpo_smt_qty') # smt 个数
        values['bom_id'] = kwargs.get('bom_id')
        values['cpo_dip_qty'] = kwargs.get('cpo_dip_qty') # DIP 数量
        values['cpo_components_supply'] = kwargs.get('cpo_components_supply') #BOM 供货方式
        values['cpo_pcb_supply'] = kwargs.get('cpo_pcb_supply') # PCB 供货方式
        values['cpo_length'] = kwargs.get('cpo_length') # PCBA and PCBA 共用字段，长度
        values['cpo_width'] = kwargs.get('cpo_width') ## PCBA and PCBA 共用字段，宽度
        values['pcb_thickness'] = kwargs.get('pcb_thickness') # PCBA 板厚
        values['cpo_select_value'] = kwargs.get('cpo_select_value') #PCBA 特殊要求


        values['price'] = kwargs.get('price')
        values['rental'] = kwargs.get('rental')
        values['Stencil'] = kwargs.get('Stencil')
        values['jig'] = kwargs.get('jig')
        values['e_test'] = kwargs.get('e_test')
        values['total'] = kwargs.get('total')
        values['cpo_select_pcb'] = kwargs.get('cpo_select_pcb')
        # 编辑ID
        values['edit_id'] = kwargs.get('edit_id')

        #钢网
        values['stencil_cost'] = kwargs.get('stencil_cost')
        values['stencil_thickness'] = kwargs.get('stencil_thickness')
        values['stencil_qty'] = kwargs.get('stencil_qty')
        values['stencil_size'] = kwargs.get('stencil_size')
        values['stencil_special'] = kwargs.get('stencil_special')
        values['stencil_freight'] = kwargs.get('stencil_freigth')
        values['stencil_total'] = kwargs.get('total_cost')

        pcb_special = {
            'Semi_hole': kwargs.get('Semi_hole'),
            'Edge_plating': kwargs.get('Edge_plating'),
            'Impedance': kwargs.get('Impedance'),
            'Press_fit': kwargs.get('Press_fit'),
            'Peelable_mask': kwargs.get('Peelable_mask'),
            'Carbon_oil': kwargs.get('Carbon_oil'),
            'Min_line_width': kwargs.get('Min_line_width'),
            'Min_line_space': kwargs.get('Min_line_space'),
            'Min_aperture': kwargs.get('Min_aperture'),
            'Total_holes': kwargs.get('Total_holes'),
            'Copper_weight_wall': kwargs.get('Copper_weight_wall'),
            'Number_core': kwargs.get('Number_core'),
            'PP_number': kwargs.get('PP_number'),
            # 'Acceptable_stanadard': kwargs.get('Acceptable_stanadard'),
            'Total_test_points': kwargs.get('Total_test_points'),
            'Blind_and_buried_hole': kwargs.get('Blind_and_buried_hole'),
            'Blind_hole_structure': kwargs.get('Blind_hole_structure'),
            'Depth_control_routing': kwargs.get('Depth_control_routing'),
            'Number_back_drilling': kwargs.get('Number_back_drilling'),
            'Countersunk_deep_holes': kwargs.get('Countersunk_deep_holes'),
            'Laser_drilling': kwargs.get('Laser_drilling'),
            'Inner_hole_line': kwargs.get('Inner_hole_line'),
            'The_space_for_drop_V_cut': kwargs.get('The_space_for_drop_V_cut'),
        }
        all_prices = {
            'cpo_special_process_fee': kwargs.get('Special Process Cost'), #特殊工艺费
            'cpo_smaterial_fee': kwargs.get('Special Material Cost'),
            'cpo_gold_finger_fee': kwargs.get('Gold Finger Cost'),
            'cpo_other_all_fee': kwargs.get('Other Cost'),
            'cpo_heart_pp_fee': kwargs.get('Core&PP Cost'),
            'cpo_text_color_fee': kwargs.get('Text Color Cost'),
            'cpo_silkscreen_color_fee': kwargs.get('Solder Mask Color Cost'),
            'cpo_surface_fee': kwargs.get('Surface Cost'),
            'cpo_benchmark_fee': kwargs.get('Cost By'),
            'cpo_thickness_fee': kwargs.get('Thickness Cost'),
            'cpo_copper_fee': kwargs.get('Copper Cost'),
            # PCB单独显示
            'cpo_test_fee': kwargs.get('E-test Fixture Cost'),
            'process_cost': kwargs.get('Process Cost'),
            'stencil_cost': kwargs.get('Stencil Cost'),
            'film_cost': kwargs.get('Film Cost'),
            'part_fee': kwargs.get('part_fee'),
            'all_fee': kwargs.get('all_fee'),
            'cpo_engineering_fee': kwargs.get('cpo_engineering_fee'),
            'cpo_freight_fee': kwargs.get('cpo_freight'),
            # PCBA
            'smt_assembly_fee': kwargs.get('smt_assembly_cost'),
            'stencil_fee': kwargs.get('stencil_cost'),
            'pcba_test_fee': kwargs.get('e_test'),
            'jig_cost': kwargs.get('jig_cost'),
            'total': kwargs.get('total_cost'),
            'pcb_pcba_all_fee': kwargs.get('pcb_pcba_all_fee'),
            'pcb_original_fee': kwargs.get('Original Price'),
        }
        # Flex-Rigid
        values['cpo_inner_outer'] = kwargs.get('cpo_inner_outer')
        values['cpo_flex_open'] = kwargs.get('cpo_flex_open')
        values['cpo_flex_number'] = kwargs.get('cpo_flex_number')
        values['cpo_flex_connect_len'] = kwargs.get('cpo_flex_connect_len')
        # PCBA 打包价
        values['pcba_package_included'] = kwargs.get('pcba_package_included')
        values['pcba_package_qty'] = kwargs.get('pcba_package_qty')
        values['pcba_package_width'] = kwargs.get('pcba_package_width')
        values['pcba_package_length'] = kwargs.get('pcba_package_length')
        values['pcba_material_type'] = kwargs.get('pcba_material_type')
        values['pcba_package_dip'] = kwargs.get('pcba_package_dip')
        values['pcba_package_smt'] = kwargs.get('pcba_package_smt')
        values['pcba_package_smt_side'] = kwargs.get('pcba_package_smt_side')
        values['pcba_package_thick'] = kwargs.get('pcba_package_thick')
        values['pcba_package_surface'] = kwargs.get('pcba_package_surface')

        # values['cpo_quantity'] = kwargs.get('pcb_quantity') # PCB 数量
        values['quality_standard'] = kwargs.get('quality_standard') # 验收标准
        values['pcb_qty_unit'] = kwargs.get('pcb_qty_unit') # PCB 单位（是否拼版）
        values['pcb_width'] = kwargs.get('pcb_breadth') # pcb宽度
        values['pcb_length'] = kwargs.get('pcb_length') # pcb长度
        values['pcb_pcs_size'] = kwargs.get('pcb_pcs_size') # Panl
        values['pcb_item_size'] = kwargs.get('pcb_item_size') # Item
        values['gold_finger_thickness'] = kwargs.get('gold_finger_thickness')
        values['gold_finger_width'] = kwargs.get('gold_finger_width')
        values['gold_finger_length'] = kwargs.get('gold_finger_length')
        values['gold_finger_qty'] = kwargs.get('gold_finger_qty')
        values['coated_area'] = kwargs.get('coated_area')
        values['nickel_thickness'] = kwargs.get('nickel_thickness')
        values['pcb_quotation_area'] = kwargs.get('pcb_quotation_area') #
        values['pcb_layer'] = kwargs.get('pcb_layer') #层数
        values['pcb_type'] = kwargs.get('pcb_type') #材料型号
        values['pcb_thickness'] = kwargs.get('pcb_thickness') #板厚
        values['pcb_inner_copper'] = kwargs.get('pcb_inner_copper') #内铜厚
        values['pcb_outer_copper'] = kwargs.get('pcb_outer_copper') #外铜厚
        values['pcb_solder_mask'] = kwargs.get('pcb_solder_mask') #
        values['pcb_silkscreen_color'] = kwargs.get('pcb_silkscreen_color')
        if kwargs.get('pcb_surface'):
            values['pcb_surface'] = kwargs.get('pcb_surface')
        else:
            values['pcb_surface'] = kwargs.get('surface_value')
        values['pcb_vias'] = kwargs.get('pcb_vias')
        values['cpo_pcb_frame'] = kwargs.get('cpo_pcb_frame')
        values['pcb_test'] = kwargs.get('pcb_test')
        values['expedited_days'] = kwargs.get('expedited_days') #加急
        values['cpo_delivery'] = kwargs.get('cpo_delivery') #交期
        values['pcba_src_order_id'] = kwargs.get('order_id') # PCBA 订单ID
        # Rogers
        values['core_thick'] = kwargs.get('core_thick')
        values['rogers_number'] = kwargs.get('rogers_number')
        # HDI
        values['number_of_step'] = kwargs.get('number_of_step')
        # 上传文件
        values['gerber_file_id'] = kwargs.get('gerber_file_id')
        values['gerber_atta_id'] = kwargs.get('gerber_atta_id')
        values['gerber_file_name'] = kwargs.get('gerber_file_name')
        values['bom_file_id'] = kwargs.get('bom_file_id')
        values['bom_atta_id'] = kwargs.get('bom_atta_id')
        values['bom_file_name'] = kwargs.get('bom_file_name')
        values['smt_file_id'] = kwargs.get('smt_file_id')
        values['smt_atta_id'] = kwargs.get('smt_atta_id')
        values['smt_file_name'] = kwargs.get('smt_file_name')

        values['package'] = kwargs.get('cpo_pcb_package')
        values['cpo_package_cost'] = kwargs.get('cpo_package_cost')

        values['pcb_special'] = pcb_special
        values['all_prices'] = all_prices #所有价格
        # 面积
        values['cpo_flat_area'] = kwargs.get('cpo_flat_area')
        try:
            CpoQuotationRecordCode().cpo_get_record_data(values, 'comfirm')
        except Exception, e:
            _logger.error("website_sale postprocess: %s value has been dropped (empty or not writable)" % e)
        return request.render("website_sale.product", values)

    def old_product(self, product, category="", search="", kwargs=None):
        product_context = dict(request.env.context,
                               active_id=product.id,
                               partner=request.env.user.partner_id)
        ProductCategory = request.env['product.public.category']
        Rating = request.env['rating.rating']

        if category:
            category = ProductCategory.browse(int(category)).exists()

        attrib_list = request.httprequest.args.getlist('attrib')
        attrib_values = [map(int, v.split("-")) for v in attrib_list if v]
        attrib_set = set([v[1] for v in attrib_values])

        keep = QueryURL('/shop', category=category and category.id, search=search, attrib=attrib_list)

        categs = ProductCategory.search([('parent_id', '=', False)])

        pricelist = request.website.get_current_pricelist()

        from_currency = request.env.user.company_id.currency_id
        to_currency = pricelist.currency_id
        compute_currency = lambda price: from_currency.compute(price, to_currency)

        # get the rating attached to a mail.message, and the rating stats of the product
        ratings = Rating.sudo().search([('message_id', 'in', product.website_message_ids.ids)])
        rating_message_values = dict([(record.message_id.id, record.rating) for record in ratings])
        rating_product = product.sudo().rating_get_stats([('website_published', '=', True)])

        if not product_context.get('pricelist'):
            product_context['pricelist'] = pricelist.id
            product = product.with_context(product_context)

        values = {
            'search': search,
            'category': category,
            'pricelist': pricelist,
            'attrib_values': attrib_values,
            'compute_currency': compute_currency,
            'attrib_set': attrib_set,
            'keep': keep,
            'categories': categs,
            'main_object': product,
            'product': product,
            'get_attribute_value_ids': self.get_attribute_value_ids,
            'rating_message_values': rating_message_values,
            'rating_product': rating_product,
        }
        return values

    def to_create_saleorde_for_pcba(self, product_id, kw):
        """
        创建PCBA订单
        :param product_id:
        :param kw:
        :return:
        """
        smt_price = kw.get('smt_price',0)
        sale_obj = request.website.sale_get_order(force_create=1, create_order=1)
        #aa =  self.product(values)
        cpo_select_pcb = kw.get('cpo_select_pcb')
        pcb_quantity = kw.get('cpo_quantity', 0)
        pcb_smt = kw.get('cpo_smt_qty', 0)
        pcb_dip = kw.get('cpo_dip_qty', 0)
        pcb_sided = kw.get('cpo_side', 0)
        pcb_length = kw.get('cpo_length', 0)
        pcb_breadth = kw.get('cpo_width', 0)
        text_val = kw.get('text_val')
        cpo_bom_supply = kw.get('cpo_components_supply')
        cpo_pcb_supply = kw.get('cpo_pcb_supply')
        pcb_thickness = kw.get('pcb_thickness')
        pcb_copper = kw.get('pcb_copper')
        pcb_special = kw.get('cpo_select_value')
        bom_id = kw.get('bom_id')
        file_dict = {
            'gerber_file_id': kw.get('gerber_file_id'),
            'gerber_atta_id': kw.get('gerber_atta_id'),
            'gerber_file_name': kw.get('gerber_file_name'),

            'bom_file_id': kw.get('bom_file_id'),
            'bom_atta_id': kw.get('bom_atta_id'),
            'bom_file_name': kw.get('bom_file_name'),

            'smt_file_id': kw.get('smt_file_id'),
            'smt_atta_id': kw.get('smt_atta_id'),
            'smt_file_name': kw.get('smt_file_name'),
        }

        order_id = sale_obj._cart_update(
            product_id=int(product_id),
            add_qty=0,
            set_qty = pcb_quantity,
            set_sided = pcb_sided,
            set_smt = pcb_smt,
            set_pcb_awh = pcb_dip,
            set_length = pcb_length,
            set_breadth = pcb_breadth,
            set_text = text_val,
            cpo_bom_supply = cpo_bom_supply,
            cpo_pcb_supply = cpo_pcb_supply,
            set_pcb_thickness = pcb_thickness,
            set_pcb_copper = pcb_copper,
            set_pcb_special = pcb_special,
            attributes=self._filter_attributes(**kw),
            bom_id = bom_id,
        )
        # 关联文件
        request.env['sale.order'].sudo().cpo_update_file({'order_id': order_id, 'create_upload_file': file_dict})
        return order_id



    def to_create_saleorde_for_pcb(self, kw, x_id, package=None):
        """
        创建PCB订单
        :param kw:
        :param x_id:
        :return:
        """
        # kw
        kw['pcb_user_name'] = request.env.user.name
        kw['pcb_user_id'] = request.env.user.id
        kw['pcb_partner_id'] = request.env.user.partner_id.id
        kw['pcb_surfaces'] = {
            'pcb_surface': kw.get('pcb_surface'),
            'gold_finger_thickness': kw.get('gold_finger_thickness'),
            'gold_finger_width': kw.get('gold_finger_width'),
            'gold_finger_length': kw.get('gold_finger_length'),
            'gold_finger_qty': kw.get('gold_finger_qty'),
            'coated_area': kw.get('coated_area'),
            'nickel_thickness': kw.get('nickel_thickness'),
        }
        # Rogers
        if kw.get('core_thick'):
            kw['pcb_rogers'] = {
                'core_thick': kw.get('core_thick'),
                'rogers_number': kw.get('rogers_number')
            }
        # HDI
        if kw.get('number_of_step'):
            kw['pcb_hdi'] = {
                'number_of_step': kw.get('number_of_step')
            }
        # flex-rigit
        if kw.get('cpo_flex_number'):
            kw['pcb_soft_hard'] = {
                'cpo_inner_outer': kw.get('cpo_inner_outer'),
                'cpo_flex_open': kw.get('cpo_flex_open'),
                'cpo_flex_number': kw.get('cpo_flex_number'),
                'cpo_flex_connect_len': kw.get('cpo_flex_connect_len'),
            }

        file_dict = {
            'gerber_file_id': kw.get('gerber_file_id'),
            'gerber_atta_id': kw.get('gerber_atta_id'),
            'gerber_file_name': kw.get('gerber_file_name'),

            'bom_file_id': kw.get('bom_file_id'),
            'bom_atta_id': kw.get('bom_atta_id'),
            'bom_file_name': kw.get('bom_file_name'),

            'smt_file_id': kw.get('smt_file_id'),
            'smt_atta_id': kw.get('smt_atta_id'),
            'smt_file_name': kw.get('smt_file_name'),
        }

        kw['pcb_specials'] = {
            'Semi_hole': kw.get('Semi_hole'),
            'Edge_plating': kw.get('Edge_plating'),
            'Impedance': kw.get('Impedance'),
            'Blind_and_buried_hole': kw.get('Blind_and_buried_hole'),
            'Countersunk_deep_holes': kw.get('Countersunk_deep_holes'),
            'Blind_hole_structure': kw.get('Blind_hole_structure'),
            'Press_fit': kw.get('Press_fit'),
            'Carbon_oil': kw.get('Carbon_oil'),
            'Peelable_mask': kw.get('Peelable_mask'),
            'Number_back_drilling': kw.get('Number_back_drilling'),
            'Depth_control_routing': kw.get('Depth_control_routing'),
            'Laser_drilling': kw.get('Laser_drilling'),
            'The_space_for_drop_V_cut': kw.get('The_space_for_drop_V_cut'),
            'Min_line_width': kw.get('Min_line_width'),
            'Min_line_space': kw.get('Min_line_space'),
            'Min_aperture': kw.get('Min_aperture'),
            'Inner_hole_line': kw.get('Inner_hole_line'),
            'Total_holes': kw.get('Total_holes'),
            'Copper_weight_wall': kw.get('Copper_weight_wall'),
            'Number_core': kw.get('Number_core'),
            'PP_number': kw.get('PP_number'),
            # 'Acceptable_stanadard': kw['Acceptable_stanadard'],
            'Total_test_points': kw.get('Total_test_points'),
        }

        order_id = request.env['sale.quotation'].sudo().CreateOrUpdatePCBQuote(x_id, kw, package=package)
        # 关联文件
        request.env['sale.order'].sudo().cpo_update_file({'order_id': order_id, 'create_upload_file': file_dict})

        saleorderids = request.session.get('sale_order_ids')
        if saleorderids:
            saleorderids.append(order_id)
        else:
            saleorderids = [order_id]
        request.session['sale_order_ids'] = saleorderids
        return order_id

    @http.route(['/cpo_load/cpo_load_coupon'], type='http', auth="public", website=True)
    def cpo_load_index_coupon(self, **post):
        values = {}
        return request.render("website_cpo_sale.cpo_load_coupon_tem", values)


    @http.route(['/pcba-need-pcb'], type='http', auth="public", website=True)
    def pcba_need_pcb(self, **post):
        values = {}
        product_tmp_id = request.env.ref("website_cpo_sale.cpo_product_template_pcba_electron").product_tmpl_id
        cpo_product_id = request.env['product.product'].search([('name', '=', product_tmp_id.name)])
        product_id = cpo_product_id.id

        file_dict = {
            'gerber_file_id': post.get('gerber_file_id'),
            'gerber_atta_id': post.get('gerber_atta_id'),
            'gerber_file_name': post.get('gerber_file_name'),

            'bom_file_id': post.get('bom_file_id'),
            'bom_atta_id': post.get('bom_atta_id'),
            'bom_file_name': post.get('bom_file_name'),

            'smt_file_id': post.get('smt_file_id'),
            'smt_atta_id': post.get('smt_atta_id'),
            'smt_file_name': post.get('smt_file_name'),
        }
        post.update({
            # 'cpo_select_pcb': True,
            'file_dict': file_dict,
        })

        if cpo_product_id.name == 'PCBA':
            order_line_id = self.to_create_saleorde_for_pcba(product_id, post)
            order = request.env['sale.order.line'].sudo().browse(order_line_id.get('line_id')).order_id

            values.update({
                'order_id': order.id,
                'product_id': product_id,
                'pcb_quantity': order.order_line.product_uom_qty,
                'pcb_width': order.order_line.pcb_width,
                'pcb_length': order.order_line.pcb_length,
                'pcb_thickness': order.order_line.pcb_thickness
            })
            # params = {
            #     'order_id': order.id,
            #     'product_id': product_id,
            #     'pcb_quantity': order.order_line.product_uom_qty,
            #     'pcb_width': order.order_line.pcb_width,
            #     'pcb_length': order.order_line.pcb_length,
            #     'pcb_thickness': order.order_line.pcb_thickness
            # }

            params = {
                'order_id': slug(order)
            }
            # url =
            url_encryption = werkzeug.url_encode(params)
            url = '/pcb?type=standard&' + url_encryption
        return request.redirect(url)

    # PCBA 和 PCB同时调用
    def to_create_saleorder_for_pcba_pcb(self, product_id, kw):
        """
        PCBA 和 PCB同时调用
        :param product_id:
        :param kw:
        :return:
        """
        x_dict = self.to_create_saleorde_for_pcba(product_id, kw)
        if kw.get('cpo_select_pcb'):
            self.to_create_saleorde_for_pcb(kw, x_dict.get('line_id'))

    def to_create_saleorder_for_stencil(self, product_id, kw):
        """
        调用钢网创建订单接口
        :param product_id:
        :param kw:
        :return:
        """
        kw['stencil_data'] = {
            'stencil_qty': kw['stencil_qty'],
            'stencil_size': kw['stencil_size'],
            'stencil_thickness': kw['stencil_thickness'],
            'stencil_special': kw['stencil_special'],
        }
        kw['partner_id'] = request.env.user.partner_id.id
        kw['product_id'] = product_id

        order_id = request.env['sale.quotation'].sudo().cpo_to_create_stencil(kw)

        saleorderids = request.session.get('sale_order_ids')
        if saleorderids:
            saleorderids.append(order_id)
        else:
            saleorderids = [order_id]
        request.session['sale_order_ids'] = saleorderids

        return order_id

    # 创建打包价订单
    def create_package_price_order(self, product_id, kw):
        """
        PCBA 打包价
        :param kw:
        :return:
        """

        packge_form = {
            'pcba_package_qty': kw.get('pcba_package_qty'),
            'pcba_package_length': kw.get('pcba_package_length'),
            'pcba_package_width': kw.get('pcba_package_width'),
            'pcba_material_type': kw.get('pcba_material_type'),
            'pcba_package_smt': kw.get('pcba_package_smt'),
            'pcba_package_dip': kw.get('pcba_package_dip'),
            'pcba_package_thick': kw.get('pcba_package_thick'),
            'pcba_package_included': kw.get('pcba_package_included'),
            'pcba_package_surface': kw.get('pcba_package_surface'),
            'pcba_package_smt_side': kw.get('pcba_package_smt_side'),
        }
        file_dict = {
            'gerber_file_id': kw.get('gerber_file_id'),
            'gerber_atta_id': kw.get('gerber_atta_id'),
            'gerber_file_name': kw.get('gerber_file_name'),

            'bom_file_id': kw.get('bom_file_id'),
            'bom_atta_id': kw.get('bom_atta_id'),
            'bom_file_name': kw.get('bom_file_name'),

            'smt_file_id': kw.get('smt_file_id'),
            'smt_atta_id': kw.get('smt_atta_id'),
            'smt_file_name': kw.get('smt_file_name'),
        }
        par_id = request.env.user.partner_id.id
        order_id = request.env['sale.order'].sudo().create_smt_package(packge_form, par_id)

        # 关联文件
        request.env['sale.order'].sudo().cpo_update_file({'order_id': order_id, 'create_upload_file': file_dict})
        saleorderids = request.session.get('sale_order_ids')
        if saleorderids:
            saleorderids.append(order_id)
        else:
            saleorderids = [order_id]
        request.session['sale_order_ids'] = saleorderids
        return order_id

    def update_pcba_order(self, kw, package=False):
        """
        更新PCBA（用户编辑订单，修改数据）
        :param kw:
        :param package:
        :return:
        """
        order = request.env['sale.order'].sudo()
        order_id = order.GetPCBAUpdate(kw, package=package)
        quotation_line = order.browse(order_id).quotation_line
        if quotation_line:
            quotation_line.sudo().GetQuoteLineUpdate()
        return order_id

    @http.route(['/shop/cart/update'], type='http', auth="public", methods=['POST'], website=True, csrf=False)
    def cart_update(self, product_id, add_qty=1, set_qty=0, **kw):
        """
        提交订单
        :param product_id:
        :param add_qty:
        :param set_qty:
        :param kw:
        :return:
        """
        pcba_src_order_id = None
        if kw.get('pcba_src_order_id'):
            pcba_src_order_id = kw.get('pcba_src_order_id')
        cpo_product_id = request.env['product.product'].search([('id', '=', product_id)])
        if cpo_product_id.name == 'PCBA':
            if (kw.get('pcba_package_qty') or kw.get('pcba_package_width') or kw.get(
                    'pcba_package_length')) and not kw.get('edit_id'):
                self.create_package_price_order(product_id, kw)
            elif kw.get('edit_id'):
                package = True if kw.get('pcba_package_qty') else False
                self.update_pcba_order(kw, package=package)
            else:
                self.to_create_saleorder_for_pcba_pcb(product_id, kw)
        elif cpo_product_id.name == 'PCB':
            if kw.get('package'):
                self.to_create_saleorde_for_pcb(kw, '', package=True)
            elif pcba_src_order_id:
                self.to_create_saleorde_for_pcb(kw, pcba_src_order_id, package=None)
            else:
                self.to_create_saleorde_for_pcb(kw, '', package=None)
        elif cpo_product_id.name == 'Stencil':
            self.to_create_saleorder_for_stencil(product_id, kw)
        try:
            cpo_ids_list = request.session['sale_order_ids']
            if cpo_ids_list:
                CpoQuotationRecordCode().get_order_ids_set_quotation_state(cpo_ids_list, 'cart')
        except Exception, e:
            _logger.error("website_sale postprocess: %s value has been dropped (empty or not writable)" % e)
        return request.redirect("/shop/cart")

    @http.route(['/shop/cart/update_json'], type='json', auth="public", methods=['POST'], website=True, csrf=False)
    def cart_update_json(self, product_id, line_id=None, add_qty=None, set_qty=None, display=True):
        #order = request.website.sale_get_order(force_create=1)
        order = request.env['sale.order.line'].sudo().search([('id', '=', line_id)]).order_id
        #if order.state != 'draft':
        #    request.website.sale_reset()
        #    return {}
        value = order._cart_update(product_id=product_id, line_id=line_id, add_qty=add_qty, set_qty=set_qty)
        #if not order.cart_quantity:
            #request.website.sale_reset()
            #return {}
        if not display:
            return None

        #order = request.website.sale_get_order()
        value['cart_quantity'] = order.cart_quantity
        from_currency = order.company_id.currency_id
        to_currency = order.pricelist_id.currency_id
        order_ids = request.website.sale_get_order_ids()
        value['website_sale.cart_lines'] = request.env['ir.ui.view'].render_template("website_sale.cart_lines", {
            'website_sale_order': order,
            'website_sale_order_ids': order_ids,
            'compute_currency': lambda price: from_currency.compute(price, to_currency),
            'suggested_products': order._cart_accessories()
        })
        value['website_sale.total'] = request.env['ir.ui.view'].render_template("website_sale.total", {
            'order_ids_untaxed':sum(order_ids.mapped("amount_untaxed")) if order_ids else 0,
            'order_ids_tax':sum(order_ids.mapped("amount_tax")) if order_ids else 0,
            'order_ids_total':sum(order_ids.mapped("amount_total")) if order_ids else 0,
            'website_sale_order_ids': order_ids,
        })
        if not order.order_line:
            order.sudo().unlink()
        return value

    def check_order_ids_partner(self):
        order_ids = request.website.sale_get_order_ids()
        partner_id = request.env.user.partner_id
        public_user = request.env.ref("base.public_user").sudo()
        if partner_id.id == public_user.partner_id.id:
            return False
        for order in order_ids:
            if order.partner_id.id != partner_id.id or order.partner_invoice_id.id != partner_id.id or order.partner_shipping_id.id != partner_id.id:
                order.partner_id = partner_id.id
                order.partner_invoice_id = partner_id.id
                order.partner_shipping_id = partner_id.id
        return True

    @http.route(['/shop/cart'], type='http', auth="public", website=True)
    def cart(self, **post):
        """
        购物车链接
        :param post:
        :return:
        """
        cpo_login = False
        order = request.website.sale_get_order()
        order_ids = request.website.sale_get_order_ids()
        order = order_ids[-1:]
        if order:
            from_currency = order.company_id.currency_id
            to_currency = order.pricelist_id.currency_id
            compute_currency = lambda price: from_currency.compute(price, to_currency)
        else:
            compute_currency = lambda price: price

        values = {
            'website_sale_order_ids': order_ids,
            'path': '/shop/cart',
            #'website_sale_order': order,
            'compute_currency': compute_currency,
            'suggested_products': [],
        }
        if order:
            _order = order
            if not request.env.context.get('pricelist'):
                _order = order.with_context(pricelist=order.pricelist_id.id)
            values['suggested_products'] = _order._cart_accessories()

        website_sale_order_ids = values.get('website_sale_order_ids')
        if website_sale_order_ids:
            values.update({
                'order_ids_untaxed': sum(website_sale_order_ids.mapped("amount_untaxed")),
                'order_ids_tax': sum(website_sale_order_ids.mapped("amount_tax")),
                'order_ids_total': sum(website_sale_order_ids.mapped("amount_total")),
            })
        values.update({
            'website_sale_order': order_ids,
        })
        if post.get('type') == 'popover':
            # force no-cache so IE11 doesn't cache this XHR
            return request.render("website_sale.cart_popover", values, headers={'Cache-Control': 'no-cache'})
        try:
            values = Website().get_seo_data(values)
            CpoQuotationRecordCode().get_website_source()
            client_user_name = request.env.user.name
            login_regist = request.env['cpo_login_and_register'].get_login_and_register_ingo()
            if login_regist:
                for lr in login_regist:
                    lr_boolean = lr.cpo_boolean
                    if lr_boolean and client_user_name == 'Public user':
                        cpo_login = True
                        break
            if cpo_login:
                return request.redirect("/web/login")
        except Exception, e:
            _logger.error("website_sale postprocess: %s value has been dropped (empty or not writable)" % e)
        return request.render("website_sale.cart", values)

    @http.route(['/edit/order'], type='json', auth="public", website=True)
    def cpo_edit_order(self, **post):
        if not post.get('url') or not post.get('order_id'):
            return request.redirect('/shop/cart')
        select_type = post.get('select_type')
        if select_type:
            if select_type == 'PCB':
                post['url'] = '/pcb?type=standard'
            elif select_type == 'PCBA':
                post['url'] = '/pcba?type=standard'
        str_encryption = base64.b64encode(post.get('order_id'))  # 字符串加密
        id = cpo_mark() + str_encryption
        params = {
            'edit': id
        }
        url_encryption = werkzeug.url_encode(params)
        if post.get('url') == '/pcb/package-price':
            url = post.get('url') + '?' + url_encryption
        else:
            url = post.get('url') + '&' + url_encryption
        post['url'] = url
        return post
        # return request.redirect(url)

    @http.route(['/shop/cpo_coupon_form'], type='json', auth="public", website=True)
    def shop_cpo_coupon_form(self, **post):
        """
        客户点击使用优惠券
        :param post:
        :return:
        """
        values, total_cost, c_money, cost = {}, 0, None, None
        post['partner_id'] = request.env.user.partner_id.id
        coupon_quotation = request.env['sale.order'].sudo()
        get_coupon_list = coupon_quotation.get_coupon_use_real_time_website(post)
        values.update({
            'order_ids': get_coupon_list.get('order_ids'),
            'coupon': get_coupon_list.get('coupon'),
        })
        coupon_data = get_coupon_list.get('coupon')
        if coupon_data:
            for k,v in coupon_data.items():
                if k == post.get('coupon_id') and post.get('checked_coupon_use') == True:
                    c_money = {
                        post.get('order_use_id'): (v.get('cpo_card_money') or v.get('cpo_no_card_money')),
                    }
                    break
            if post.get('cpo_supply_method') == "By Chinapcbone's account":
                cost = coupon_quotation.get_order_freight(values.get('order_ids').ids)
                total_cost = sum(cost.values())
        values.update({
            'c_money': c_money,
            'cost': cost,
            'total_cost': total_cost,
        })
        # order_ids = request.website.sale_get_order_ids().ids
        # return request.env['ir.ui.view'].render_template('website_cpo_sale.cpo_coupon_and_amount_total',
        #     values
        # )
        return {
            'cpo_coupon_list_content': request.env['ir.ui.view'].render_template('website_cpo_sale.cpo_coupon_list_content', values)
                }

    @http.route(['/shop/checkout'], type='http', auth="public", website=True)
    def checkout(self, **post):
        """
        从购物车提交到选择地址（地址发生改变时也会触发）
        :param post:
        :return:
        """
        if not request.session.get('uid'):
            request.session['redirect'] = '/shop/checkout'
            return request.redirect("/web/signup")
        if not request.session.get('checkout_order_ids') and not request.session.get('sale_order_ids'):
            return request.redirect("/shop/cart")
        order_ids_list = []
        order_ids = post.get('order_ids')
        src_checkout_order_ids = request.session.get('checkout_order_ids')
        if order_ids:
            for x in order_ids.split(","):
                assert int(x),'order_ids format is error.'
                order_ids_list.append(int(x))
        else:
            order_ids_list = order_ids = request.website.sale_get_checked_order().mapped("id")

        if not order_ids_list:
            return request.redirect("/shop/cart")
        else:
            if src_checkout_order_ids:
                order_ids_list = list(set(src_checkout_order_ids + order_ids_list))
            request.session['checkout_order_ids'] = order_ids_list
        vals = []
        #for order in order_ids_list:
        #order = request.website.sale_get_order()
        order = request.website.sale_get_order_ids()[:1]

        redirection = self.checkout_redirection(order)
        if redirection:
            return redirection

        if order.partner_id.id == request.website.user_id.sudo().partner_id.id:
            if not self.cpo_to_update_order_partner(order_ids_list):
                return request.redirect('/shop/address')

        for f in self._get_mandatory_billing_fields():
            if not order.partner_id[f]:
                return request.redirect('/shop/address?partner_id=%d' % order.partner_id.id)

        values = self.checkout_values(**post)
        if not values:
            return request.redirect('/shop/cart')

        values.update({'website_sale_order': order})

        # 优惠券(调用优惠券接口)
        coupon_partner_id = request.env.user.partner_id.id
        coupon = self.cpo_return_coupon(coupon_partner_id, order_ids_list)
        # 返回优惠券信息 加载优惠券信息
        if coupon:
            values.update({'coupon': coupon.get('coupon')})
            vals.append(values)

        # Avoid useless rendering if called in ajax
        if post.get('xhr'):
            return 'ok'
        # 记录报价
        try:
            cpo_ids_list = values.get('order_ids').ids
            if cpo_ids_list:
                CpoQuotationRecordCode().get_order_ids_set_quotation_state(cpo_ids_list, 'selected')
        except Exception, e:
            _logger.error("website_sale postprocess: %s value has been dropped (empty or not writable)" % e)
        values.update({
            'cost': None,
            'total_cost': 0,
            'c_money': None,
        })
        return request.render("website_sale.checkout", values)

    def cpo_return_coupon(self, partner_id, order_ids):
        """
        添加优惠券获取 返回'/shop/checkout' 在订单中显示可用优惠券
        :param partner_id:
        :param order_ids:
        :return:
        """
        coupon_quotation = request.env['sale.order'].sudo()
        try:
            # order_ids = request.website.sale_get_order_ids().ids
            get_coupon = {  # 获取订单id，或用户id
                'order_ids': order_ids,
                'partner_id': partner_id
            }
            rows = coupon_quotation.get_website_preferential(get_coupon)
        except Exception, e:
            rows = None
            return rows
        return rows

    @http.route("/customer/select/express", type="json", auth="public", website=True)
    def customer_select_express(self, **post):
        """
        选择地址时，确认快递收货方式：到付，在线支付
        :param post:
        :return:
        """
        vals, coupon, cost, total_cost, c_money = {}, None, None, 0, None
        partner_id = request.env.user.partner_id.id
        order_ids = request.website.sale_get_checked_order()
        sale_order = request.env['sale.order'].sudo()
        vals = {
            'cpo_supply_method': post.get('cpo_supply_method'),
            'cpo_express_select': post.get('cpo_express_select'),
            'account_number': post.get('express_number'),
            'order_list': order_ids,
        }
        values = sale_order.customer_delivery_method(vals)
        post['values'] = values
        if post.get('cpo_supply_method') == 'no':
            cost = sale_order.get_order_freight(order_ids.ids)
            total_cost = sum(cost.values())
        # 调用优惠券接口
        coupon = self.cpo_return_coupon(partner_id, order_ids.ids)
        # 返回优惠券信息 加载优惠券信息
        if coupon:
            vals.update({
                'coupon': coupon.get('coupon'),
                'order_ids': order_ids,
                'cost': cost,
                'total_cost': total_cost,
            })
        return {
            'cpo_checke_express': request.env['ir.ui.view'].render_template('website_cpo_sale.cpo_coupon_list_content', vals)}

    @http.route(['/cpo_coupon_form'], type='json', methods=['GET', 'POST'], auth="public", website=True)
    def cpo_coupon_form(self, **kw):
        # print kw
        return kw

    def cpo_to_update_order_partner(self, order_ids):
        if request.env.uid == request.website.user_id.id:
            return False
        sale_order = request.env['sale.order'].sudo()
        old_order = sale_order.search([
            ('partner_id', '=', request.env.user.partner_id.id),
            ('partner_id', '!=', request.website.user_id.sudo().partner_id.id),
        ])[:1]
        if not old_order or not old_order.partner_id:
            return False
        res = sale_order.search([('id', 'in', order_ids)]).write(
        {
            'partner_id': old_order.partner_id.id,
            'partner_shipping_id': old_order.partner_shipping_id.id,
            'partner_invoice_id': old_order.partner_invoice_id.id
        })
        return res

    """
        继承模块：website_sale
        路径：/website_sale/controllers/mian.py(line 459)
        继承函数名：checkout_form_validate
        作用：在数组中添加zip，phone，使zip，phone为必填
    """
    def checkout_form_validate(self, mode, all_form_values, data):
        # mode: tuple ('new|edit', 'billing|shipping')
        # all_form_values: all values before preprocess
        # data: values after preprocess
        error = dict()
        error_message = []

        # Required fields from form
        required_fields = filter(None, (all_form_values.get('field_required') or '').split(','))
        # Required fields from mandatory field function
        required_fields += mode[
                               1] == 'shipping' and self._get_mandatory_shipping_fields() or self._get_mandatory_billing_fields()
        # Check if state required
        if data.get('country_id'):
            country = request.env['res.country'].browse(int(data.get('country_id')))
            if 'state_code' in country.get_address_fields() and country.state_ids:
                required_fields += ['state_id']

        # error message for empty required fields
        # required_fields.append('zip') #增加zip code为必填信息
        # required_fields.append('phone') #增加zip code为必填信息
        # required_fields.append('email') #增加email 为必填信息
        required_fields = required_fields + ['zip', 'phone', 'email', 'type']
        for field_name in required_fields:
            if not data.get(field_name):
                error[field_name] = 'missing'

        # email validation
        if data.get('email') and not tools.single_email_re.match(data.get('email')):
            error["email"] = 'error'
            error_message.append(_('Invalid Email! Please enter a valid email address.'))

        # vat validation
        Partner = request.env['res.partner']
        if data.get("vat") and hasattr(Partner, "check_vat"):
            if data.get("country_id"):
                data["vat"] = Partner.fix_eu_vat_number(data.get("country_id"), data.get("vat"))
            check_func = request.website.company_id.vat_check_vies and Partner.vies_vat_check or Partner.simple_vat_check
            vat_country, vat_number = Partner._split_vat(data.get("vat"))
            if not check_func(vat_country, vat_number):
                error["vat"] = 'error'

        if [err for err in error.values() if err == 'missing']:
            error_message.append(_('Some required fields are empty.'))

        return error, error_message

    def get_all_order_status(self, status):
        """
        获取每个状态订单的数量
        :param status:
        :return:
        """
        order_qty = None
        partner = request.env.user.partner_id
        get_obj = request.env['personal.center'].sudo()
        state = status
        order_qty = get_obj.get_partner(partner, state)
        return order_qty

    @http.route(['/shop/address'], type='http', methods=['GET', 'POST'], auth="public", website=True)
    def address(self, **kw):
        """
        新增收货地址
        :param kw:
        :return:
        """
        # 地址信息的修改
        if kw.get('change_address'):
            return self.redirect_address_change(kw)
        # 个人信息的修改
        if kw.get('change_info'):
            return self.redirect_info_change(kw)
        Partner = request.env['res.partner'].with_context(show_address=1).sudo()
        #order = request.website.sale_get_order()
        #order_rows = request.website.sale_get_checkout_order()
        if not request.session.get('checkout_order_ids') and not request.session.get('sale_order_ids'):
            return request.redirect("/shop/cart")
        order_rows = request.website.sale_get_checked_order()
        order = order_rows[-1:]
        #= request.env['sale.order'].search([('id', 'in', order_ids)])

        redirection = self.checkout_redirection(order_rows)
        if redirection:
            return redirection

        mode = (False, False)
        def_country_id = order_rows[-1:].partner_id.country_id
        values, errors = {}, {}

        partner_id = int(kw.get('partner_id', -1))

        # IF PUBLIC ORDER
        if order_rows[-1:].partner_id.id == request.website.user_id.sudo().partner_id.id:
            mode = ('new', 'billing')
            country_code = request.session['geoip'].get('country_code')
            if country_code:
                def_country_id = request.env['res.country'].search([('code', '=', country_code)], limit=1)
            else:
                def_country_id = request.website.user_id.sudo().country_id
        # IF ORDER LINKED TO A PARTNER
        else:
            if partner_id > 0:
                if partner_id == order_rows[-1:].partner_id.id:
                    mode = ('edit', 'billing')
                else:
                    #shippings = Partner.search([('id', 'child_of', order.partner_id.commercial_partner_id.ids)])
                    partner_shippings = []
                    for p_row in order_rows:
                        partner_shippings += p_row.partner_id.commercial_partner_id.ids
                    shippings = Partner.search([('id', 'child_of', partner_shippings)])
                    if partner_id in shippings.mapped('id'):
                        mode = ('edit', 'shipping')
                    else:
                        return Forbidden()
                if mode:
                    values = Partner.browse(partner_id)
            elif partner_id == -1:
                mode = ('new', 'shipping')
            else:
                # no mode - refresh without post?
                return request.redirect('/shop/checkout')

        # IF POSTED
        if 'submitted' in kw:
            error_ids = []
            for order in order_rows[-1:]:
                pre_values = self.values_preprocess(order, mode, kw)
                # if pre_values['zip'] == '':
                #     pre_values["field_required"] = pre_values.pop("zip")
                errors, error_msg = self.checkout_form_validate(mode, kw, pre_values)
                post, errors, error_msg = self.values_postprocess(order, mode, pre_values, errors, error_msg)
                if errors not in error_ids and errors:
                    error_ids.append(errors)

                if errors:
                    errors['error_message'] = error_msg
                    values = kw
                else:
                    partner_id = self._checkout_form_save(mode, post, kw)

                    if mode[1] == 'billing':
                        order.partner_id = partner_id
                        order.onchange_partner_id()
                        order.partner_id = order.partner_id.commercial_partner_id
                    elif mode[1] == 'shipping':
                        order.partner_shipping_id = partner_id

            order_rows.write({'message_partner_ids':[(4, partner_id), (3, request.website.partner_id.id)]})
            if not error_ids:
                return request.redirect(kw.get('callback') or '/shop/checkout')

        country = 'country_id' in values and values['country_id'] != '' and request.env['res.country'].browse(int(values['country_id']))
        country = country and country.exists() or def_country_id
        # 调用个人中心的参数接口
        state = 'under_review'
        order_qty = self.get_all_order_status(state)
        # 检查values 的类型
        addr_type = self.checkAddressValueType(values)
        render_values = {
            'quotation_qty': order_qty,
            'website_sale_order': order,
            'partner_id': partner_id,
            'mode': mode,
            'checkout': values,
            'addr_type': addr_type,
            'country': country,
            'countries': country.get_website_sale_countries(mode=mode[1]),
            "states": country.get_website_sale_states(mode=mode[1]),
            'error': errors,
            'callback': kw.get('callback'),
            'change_address': kw.get('change_address'),
            'user': request.env.user,
            'personal_id': self._cpo_get_user_ID(),
        }
        return request.render("website_sale.address", render_values)

    def checkAddressValueType(self, values):
        """
        检查数据类型，实现地址类型的选择
        :param values:
        :return:
        """
        if not values:
            addr_type = False
            return addr_type
        if type(values) == dict:
            addr_type = True
        else:
            addr_type = False
        return addr_type

    def redirect_address_change(self, kw):
        """
        在客户端，新增收货地址，修改地址等，跳转这里
        2019年12月3日10:03:24
        :param kw:
        :return:
        """
        Partner = request.env['res.partner'].with_context(show_address=1).sudo()

        order_rows = request.website.sale_get_checked_order()
        order = order_rows[-1:]

        mode = (False, False)
        def_country_id = order_rows[-1:].partner_id.country_id
        values, errors = {}, {}

        partner_id = int(kw.get('partner_id', -1))

        if partner_id > 0:
            if partner_id == order_rows[-1:].partner_id.id:
                mode = ('edit', 'billing')
            else:
                mode = ('edit', 'shipping')
            if mode:
                values = Partner.browse(partner_id)
        elif partner_id == -1:
            mode = ('new', 'shipping')
        else:
            return request.redirect('/my/account/address')

        # IF POSTED
        if 'submitted' in kw:
            error_ids = []
            pre_values = self.values_preprocess(order, mode, kw)

            errors, error_msg = self.checkout_form_validate(mode, kw, pre_values)
            post, errors, error_msg = self.values_postprocess(order, mode, pre_values, errors, error_msg)
            if errors not in error_ids and errors:
                error_ids.append(errors)

            if errors:
                errors['error_message'] = error_msg
                values = kw
            else:
                partner_id = self._account_checkout_form_save(mode, post, kw)

            order_rows.write({'message_partner_ids': [(4, partner_id), (3, request.website.partner_id.id)]})
            if not error_ids:
                return request.redirect('/my/account/address')

        country = 'country_id' in values and values['country_id'] != '' and request.env['res.country'].browse(
            int(values['country_id']))
        country = country and country.exists() or def_country_id
        # 调用个人中心的参数接口
        state = 'under_review'
        order_qty = self.get_all_order_status(state)
        addr_type = self.checkAddressValueType(values)
        render_values = {
            'quotation_qty': order_qty,
            'link_active': 'shop_address',
            'website_sale_order': order,
            'partner_id': partner_id,
            'mode': mode,
            'addr_type': addr_type,
            'checkout': values,
            'country': country,
            'countries': country.get_website_sale_countries(mode=mode[1]),
            "states": country.get_website_sale_states(mode=mode[1]),
            'error': errors,
            'callback': kw.get('callback'),
            'change_address': kw.get('change_address'),
            'user': request.env.user,
            'personal_id': self._cpo_get_user_ID(),
        }
        return request.render("website_sale.address", render_values)

    def redirect_info_change(self, kw):
        """
        在客户端，新增个人信息的修改
        时间：2020年1月2日09:33:10
        author：Charlie
        :param kw:
        :return:
        """
        Partner = request.env['res.partner'].with_context(show_address=1).sudo()
        order_rows = request.website.sale_get_checked_order()
        order = order_rows[-1:]

        mode = (False, False)
        def_country_id = order_rows[-1:].partner_id.country_id
        values, errors = {}, {}

        partner_id = int(kw.get('partner_id', -1))

        if partner_id > 0:
            if partner_id == order_rows[-1:].partner_id.id:
                mode = ('edit', 'billing')
            else:
                mode = ('edit', 'shipping')
            if mode:
                values = Partner.browse(partner_id)
        elif partner_id == -1:
            mode = ('new', 'shipping')
        else:
            return request.redirect('/my/home')

        # IF POSTED
        if 'submitted' in kw:
            error_ids = []
            pre_values = self.values_preprocess(order, mode, kw)

            errors, error_msg = self.checkout_form_validate(mode, kw, pre_values)
            post, errors, error_msg = self.values_postprocess(order, mode, pre_values, errors, error_msg)
            if errors not in error_ids and errors:
                error_ids.append(errors)

            if errors:
                errors['error_message'] = error_msg
                values = kw
            else:
                partner_id = self._account_checkout_form_save(mode, post, kw)

            order_rows.write({'message_partner_ids': [(4, partner_id), (3, request.website.partner_id.id)]})
            if not error_ids:
                return request.redirect('/my/home')

        country = 'country_id' in values and values['country_id'] != '' and request.env['res.country'].browse(
            int(values['country_id']))
        country = country and country.exists() or def_country_id
        # 调用个人中心的参数接口
        state = 'under_review'
        order_qty = self.get_all_order_status(state)
        addr_type = self.checkAddressValueType(values)
        render_values = {
            'quotation_qty': order_qty,
            'link_active': 'my_home',
            'website_sale_order': order,
            'partner_id': partner_id,
            'mode': mode,
            'addr_type': addr_type,
            'checkout': values,
            'country': country,
            'countries': country.get_website_sale_countries(mode=mode[1]),
            "states": country.get_website_sale_states(mode=mode[1]),
            'error': errors,
            'callback': kw.get('callback'),
            'change_address': kw.get('change_address'),
            'change_info': kw.get('change_info'),
            'user': request.env.user,
            'personal_id': self._cpo_get_user_ID(),
        }
        return request.render("website_sale.address", render_values)

    def _account_checkout_form_save(self, mode, checkout, all_values):
        """
        时间：2019年12月3日10:15:17
        增加原因：原有是因为需要订单依赖，更改为不需要订单依赖
        功能：在用户个人中心增加修改地址信息
        :param mode:
        :param checkout:
        :param all_values:
        :return:
        """
        Partner = request.env['res.partner']
        if checkout.get('type') != all_values.get('type'):
            checkout['type'] = all_values.get('type')
        if mode[0] == 'new':
            partner_id = Partner.sudo().create(checkout).id
        elif mode[0] == 'edit':
            partner_id = int(all_values.get('partner_id', 0))
            if partner_id:
                if checkout.get('parent_id') == partner_id:
                    partner_id = checkout.pop('parent_id')
                Partner.browse(partner_id).sudo().write(checkout)
        return partner_id

    def _cpo_get_user_ID(self):
        """
        获取（personal对象）
        :return:
        """
        personal_id = 'CPO001001'
        personal_center = request.env['personal.center'].sudo()
        user_id = request.env.user.id
        if not user_id:
            return personal_id
        return personal_center.search([('user_id', '=', user_id)])



    def values_postprocess(self, order, mode, values, errors, error_msg):
        new_values = {}
        authorized_fields = request.env['ir.model']._get('res.partner')._get_form_writable_fields()
        for k, v in values.items():
            # don't drop empty value, it could be a field to reset
            if k in authorized_fields and v is not None:
                new_values[k] = v
            else:  # DEBUG ONLY
                if k not in ('field_required', 'partner_id', 'callback', 'submitted'): # classic case
                    _logger.debug("website_sale postprocess: %s value has been dropped (empty or not writable)" % k)
        new_values['type'] = values.get('type')
        new_values['customer'] = True
        new_values['team_id'] = request.website.salesteam_id and request.website.salesteam_id.id

        lang = request.lang if request.lang in request.website.mapped('language_ids.code') else None
        if lang:
            new_values['lang'] = lang
        if mode == ('edit', 'billing') and order.partner_id.type == 'contact':
            new_values['type'] = 'other'
        if mode[1] == 'shipping':
            new_values['parent_id'] = order.partner_id.commercial_partner_id.id
            new_values['type'] = 'delivery'
        if mode[1] == 'billing':
            new_values['type'] = 'invoice'

        new_values['parent_id'] = request.env.user.partner_id.id

        return new_values, errors, error_msg

    def _checkout_form_save(self, mode, checkout, all_values):
        Partner = request.env['res.partner']
        if mode[0] == 'new':
            partner_id = Partner.sudo().create(checkout).id
        elif mode[0] == 'edit':
            partner_id = int(all_values.get('partner_id', 0))
            if partner_id:
                # double check
                #order_rows = request.website.sale_get_order_ids()
                order_rows = request.website.sale_get_checked_order()
                partner_shippings = []
                for p_row in order_rows:
                    partner_shippings += p_row.partner_id.commercial_partner_id.ids
                shippings = Partner.sudo().search([("id", "child_of", partner_shippings)])
                if partner_id not in shippings.mapped('id') and partner_id != order.partner_id.id:
                    return Forbidden()
                if checkout.get('parent_id') == partner_id:
                    partner_id = checkout.pop('parent_id')
                Partner.browse(partner_id).sudo().write(checkout)
        return partner_id

    # ------------------------------------------------------
    # Checkout
    # ------------------------------------------------------

    def checkout_redirection(self, order):
        # must have a draft sales order with lines at this point, otherwise reset
        order_ids = request.session['sale_order_ids']
        if not order_ids:
            return request.redirect('/shop')
        order_ids = request.env['sale.order'].sudo().search([('id', 'in', order_ids), ('state', '=', 'draft')])
        if not order_ids:
            #request.session['sale_order_id'] = None
            #request.session['sale_order_ids'] = []
            request.session['sale_transaction_id'] = None
            return request.redirect('/shop')
        #if not order or order.state != 'draft':
            #request.session['sale_order_id'] = None
            #request.session['sale_transaction_id'] = None
            #return request.redirect('/shop')
        #
        # if transaction pending / done: redirect to confirmation
        #tx = request.env.context.get('website_sale_transaction')
        #if tx and tx.state != 'draft':
        #    return request.redirect('/shop/payment/confirmation/%s' % order.id)

    def checkout_values(self, **kw):
        #order = request.website.sale_get_order(force_create=1)
        #order_ids = request.website.sale_get_order_ids()
        order_ids = request.website.sale_get_checkout_order()
        if not order_ids:
            return False
        for order in order_ids:
            shippings = []
            if order.partner_id != request.website.user_id.sudo().partner_id:
                Partner = order.partner_id.with_context(show_address=1).sudo()
                shippings = Partner.search([
                    ("id", "child_of", order.partner_id.commercial_partner_id.ids),
                    '|', ("type", "in", ["delivery", "other", "contact", "invoice"]), ("id", "=", order.partner_id.commercial_partner_id.id)
                ], order='id desc')
                if shippings:
                    if kw.get('partner_id') or 'use_billing' in kw:
                        if 'use_billing' in kw:
                            partner_id = order.partner_id.id
                        else:
                            partner_id = int(kw.get('partner_id'))
                        if partner_id in shippings.mapped('id'):
                            order.partner_shipping_id = partner_id
                    elif not order.partner_shipping_id:
                        last_order = request.env['sale.order'].sudo().search([("partner_id", "=", order.partner_id.id)], order='id desc', limit=1)
                        order.partner_shipping_id.id = last_order and last_order.id
        values = {
            'order_ids': order_ids,
            'order': order,
            'shippings': shippings,
            'only_services': order and order.only_services or False
        }
        return values

    @http.route(['/shop/confirm_order'], type='http', auth="public", website=True)
    def confirm_order(self, **post):
        """
        确认收货地址，提交订单
        :param post:
        :return:
        """
        order = request.website.sale_get_order()
        #order_ids = request.website.sale_get_order_ids()
        order_ids = request.website.sale_get_checked_order()
        for order in order_ids:
            redirection = self.checkout_redirection(order)
            if redirection:
                return redirection
            order.act_wait_confirm()
            #if order.state == 'draf' or order.state == 'sent':
            #    order.do_await()
            # cancel to do_await of sale_order func

            order.onchange_partner_shipping_id()
            order.order_line._compute_tax_id()
            request.session['sale_last_order_id'] = order.id
            request.website.sale_get_order(update_pricelist=True)
        order_ids.cpo_clear_checkout_session()
        extra_step = request.env.ref('website_sale.extra_info_option')
        if extra_step.active:
            return request.redirect("/shop/extra_info")

        # return request.redirect("/shop/payment")
        try:
            cpo_ids_list = order_ids.ids
            value = InheritPayment().get_website_payment(cpo_ids_list)
            if cpo_ids_list:
                CpoQuotationRecordCode().get_order_ids_set_quotation_state(cpo_ids_list, 'pending')
            if value:
                return value
        except Exception, e:
            _logger.error("website_sale postprocess: %s value has been dropped (empty or not writable)" % e)
        return request.redirect("/my/home")

    # ------------------------------------------------------
    # Payment
    # ------------------------------------------------------

    @http.route(['/shop/payment'], type='http', auth="public", website=True)
    def payment(self, **post):
        """ Payment step. This page proposes several payment means based on available
        payment.acquirer. State at this point :

         - a draft sales order with lines; otherwise, clean context / session and
           back to the shop
         - no transaction in context / session, or only a draft one, if the customer
           did go to a payment.acquirer website but closed the tab without
           paying / canceling
        """
        SaleOrder = request.env['sale.order']

        #order = request.website.sale_get_order()
        #order_ids = request.website.sale_get_checkout_order_ids()

        partner = request.env.user.partner_id
        if request.website.partner_id.id == partner.id:
            return request.redirect("/shop/cart")
        SaleOrder = request.env['sale.order']

        domain = [
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            #('state', 'in', ['sent', 'cancel'])
            #('state', 'in', ['draft', 'cancel'])
            ('state', 'in', ['wait_confirm',])
        ]

        order_ids = SaleOrder.sudo().search(domain)
        order = order_ids[-1:]

        vals = []
        #for row in order_ids:

        redirection = self.checkout_redirection(order)
        if redirection and 1==2:
            return redirection

        shipping_partner_id = False
        if order:
            if order.partner_shipping_id.id:
                shipping_partner_id = order.partner_shipping_id.id
            else:
                shipping_partner_id = order.partner_invoice_id.id

        if not order and order_ids:
            order = order_ids[0]
        values = {
            'website_sale_order': order,
            'order_ids': order_ids,
            'order_ids_untaxed': sum(order_ids.mapped("amount_untaxed")) if order_ids else 0,
            'order_ids_tax': sum(order_ids.mapped("amount_tax")) if order_ids else 0,
            'order_ids_total': sum(order_ids.mapped("amount_total")) if order_ids else 0,
            'can_pay': False if order_ids and order_ids.filtered(lambda x:x.state!='sale') else True,
        }
        values['errors'] = SaleOrder._get_errors(order)
        values.update(SaleOrder._get_website_data(order))
        if not values['errors']:
            acquirers = request.env['payment.acquirer'].search(
                [('website_published', '=', True), ('company_id', '=', order.company_id.id)]
            )
            values['acquirers'] = []
            for acquirer in acquirers:
                acquirer_button = acquirer.with_context(submit_class='btn btn-primary', submit_txt=_('Pay Now')).sudo().render(
                    '/',
                    order.amount_total,
                    order.pricelist_id.currency_id.id,
                    values={
                        'return_url': '/shop/payment/validate',
                        'partner_id': shipping_partner_id,
                        'billing_partner_id': order.partner_invoice_id.id,
                    }
                )
                acquirer.button = acquirer_button
                values['acquirers'].append(acquirer)

            values['tokens'] = request.env['payment.token'].search([('partner_id', '=', order.partner_id.id), ('acquirer_id', 'in', acquirers.ids)])
            #vals.append(values)

        return request.render("website_sale.payment", values)

    @http.route('/shop/payment/validate', type='http', auth="public", website=True)
    def payment_validate(self, transaction_id=None, sale_order_id=None, **post):
        """ Method that should be called by the server when receiving an update
        for a transaction. State at this point :

         - UDPATE ME
        """
        if transaction_id is None:
            tx = request.website.sale_get_transaction()
        else:
            tx = request.env['payment.transaction'].browse(transaction_id)

        order_ids = request.website.sale_get_checkout_order_ids()
        #if sale_order_id is None:
        #    order = request.website.sale_get_order()
        #else:
        #    order = request.env['sale.order'].sudo().browse(sale_order_id)
        #    assert order.id == request.session.get('sale_last_order_id')

        for order in order_ids:
            if not order or (order.amount_total and not tx):
                return request.redirect('/shop')

            if (not order.amount_total and not tx) or tx.state in ['pending', 'done', 'authorized']:
                if (not order.amount_total and not tx):
                    # Orders are confirmed by payment transactions, but there is none for free orders,
                    # (e.g. free events), so confirm immediately
                    order.with_context(send_email=True).action_confirm()
            elif tx and tx.state == 'cancel':
                # cancel the quotation
                order.action_cancel()

        # clean context and session, then redirect to the confirmation page
        request.website.sale_reset()
        if tx and tx.state == 'draft':
            return request.redirect('/shop')

        return request.redirect('/shop/confirmation')

    @http.route(['/shop/payment/transaction/<int:acquirer_id>'], type='json', auth="public", website=True)
    def payment_transaction(self, acquirer_id, tx_type='form', token=None, **kwargs):
        """ Json method that creates a payment.transaction, used to create a
        transaction when the user clicks on 'pay now' button. After having
        created the transaction, the event continues and the user is redirected
        to the acquirer website.

        :param int acquirer_id: id of a payment.acquirer record. If not set the
                                user is redirected to the checkout page
        """
        Transaction = request.env['payment.transaction'].sudo()

        # In case the route is called directly from the JS (as done in Stripe payment method)
        so_id = kwargs.get('so_id')
        so_token = kwargs.get('so_token')
        if so_id and so_token:
            order = request.env['sale.order'].sudo().search([('id', '=', so_id), ('access_token', '=', so_token)])
        elif so_id:
            order = request.env['sale.order'].search([('id', '=', so_id)])
        else:
            order = request.website.sale_get_order()
            order_ids = request.website.sale_get_checkout_order_ids()
            request.session['sale_last_order_ids'] = request.session.get('checkout_order_ids')
        #if not order or not order.order_line or acquirer_id is None:
        if not order_ids or acquirer_id is None:
            return request.redirect("/shop/checkout")

        for order in order_ids:
            assert order.partner_id.id != request.website.partner_id.id

        # find an already existing transaction
        tx = request.website.sale_get_transaction()
        if tx:
            if tx.sale_order_id.id != order.id or tx.state in ['error', 'cancel'] or tx.acquirer_id.id != acquirer_id:
                tx = False
            elif token and tx.payment_token_id and token != tx.payment_token_id.id:
                # new or distinct token
                tx = False
            elif tx.state == 'draft':  # button cliked but no more info -> rewrite on tx or create a new one ?
                tx.write(dict(Transaction.on_change_partner_id(order.partner_id.id).get('value', {}), amount=order.amount_total, type=tx_type))
        if not tx:
            tx_values = {
                'acquirer_id': acquirer_id,
                'type': tx_type,
                #'amount': order.amount_total,
                'amount': sum(order_ids.mapped("amount_total")),
                'currency_id': order.pricelist_id.currency_id.id,
                'partner_id': order.partner_id.id,
                'partner_country_id': order.partner_id.country_id.id,
                'reference': Transaction.get_next_reference(order.name),
                'sale_order_id': order.id,
                #'sale_order_ids': order_ids.mapped("id"),
            }
            if token and request.env['payment.token'].sudo().browse(int(token)).partner_id == order.partner_id:
                tx_values['payment_token_id'] = token

            tx = Transaction.create(tx_values)
            request.session['sale_transaction_id'] = tx.id

        # update quotation
        order_ids.write({
            'payment_acquirer_id': acquirer_id,
            'payment_tx_id': request.session['sale_transaction_id']
        })
        if token:
            return request.env.ref('website_sale.payment_token_form').render(dict(tx=tx), engine='ir.qweb')

        return tx.acquirer_id.with_context(submit_class='btn btn-primary', submit_txt=_('Pay Now')).sudo().render(
            tx.reference,
            #order.amount_total,
            sum(order_ids.mapped("amount_total")),
            order.pricelist_id.currency_id.id,
            values={
                'return_url': '/shop/payment/validate',
                'partner_id': order.partner_shipping_id.id or order.partner_invoice_id.id,
                'billing_partner_id': order.partner_invoice_id.id,
            },
        )

    @http.route(['/shop/confirmation'], type='http', auth="public", website=True)
    def payment_confirmation(self, **post):
        """ End of checkout process controller. Confirmation is basically seing
        the status of a sale.order. State at this point :

         - should not have any context / session info: clean them
         - take a sale.order id, because we request a sale.order and are not
           session dependant anymore
        """
        sale_order_id = request.session.get('sale_last_order_id')
        if sale_order_id:
            order = request.env['sale.order'].sudo().browse(sale_order_id)
            order_ids = request.env['sale.order'].sudo().browse(request.session.get('sale_last_order_ids'))
            return request.render("website_sale.confirmation", {'order': order, 'order_ids':order_ids, 'total': sum(order_ids.mapped("amount_total"))})
        else:
            return request.redirect('/shop')


class WebsiteSourceHome(main.Home):
    """
    继承路径，增加路径来源记录
    """
    # @http.route()
    # def index(self,*args, **kw):
    #     try:
    #         res_id = CpoQuotationRecordCode().get_website_source()
    #     except Exception, e:
    #         _logger.error("website_sale postprocess: %s value has been dropped (empty or not writable)" % e)
    #     return super(WebsiteSourceHome, self).index(*args, **kw)
    def getQuoteRecordId(self):
        """
        获取报价记录的第一条
        :return:
        """
        cpo_cookie = request.httprequest.cookies.get('session_id')
        quote_record = request.env['cpo_pcb_record'].sudo().search([('session_id', '=', cpo_cookie)])
        if not quote_record:
            return False
        quote_data = quote_record[0]
        return quote_data

    @http.route()
    def web_login(self, redirect=None, *args, **kw):
        try:
            # kw['src'] = None
            # kw['type'] = None
            quote_signup_history = request.httprequest.cookies.get('quote_signup_history')
            if quote_signup_history:
                quote_history = json.loads(quote_signup_history)
                # quote = self.getQuoteRecordId()
                # if not quote_history.get('quote_id'):
                #     quote_history.update({
                #         'quote_id': quote.id,
                #     })
                if quote_history.get('src'):
                    if quote_history.get('type'):
                        type = 'type=' + quote_history.get('type')
                        redirect = quote_history.get('src') + '?' + type + '&login=true'
                    else:
                        redirect = kw.get('src') + '?login=true'
                    http.redirect_with_hash(redirect)
            if kw.get('src'):
                if kw.get('type'):
                    type = 'type=' + kw.get('type')
                    redirect = kw.get('src') + '?' + type + '&login=true'
                else:
                    redirect = kw.get('src') + '?login=true'
                http.redirect_with_hash(redirect)
            redirect = '/my/home'
            http.redirect_with_hash(redirect)
            response = super(WebsiteSourceHome, self).web_login(redirect, *args, **kw)
            CpoQuotationRecordCode().get_website_source()
        except Exception, e:
            _logger.error("website_sale postprocess: %s value has been dropped (empty or not writable)" % e)
        # return super(WebsiteSourceHome, self).web_login(redirect, *args, **kw)
        return response

    @http.route()
    def web_auth_signup(self, *args, **kw):
        try:
            quote_signup_history = request.httprequest.cookies.get('quote_signup_history')
            CpoQuotationRecordCode().get_website_source()
        except Exception, e:
            _logger.error("website_sale postprocess: %s value has been dropped (empty or not writable)" % e)
        return super(WebsiteSourceHome, self).web_auth_signup(*args, **kw)

    @http.route()
    def page(self, page, **opt):
        try:
            #if page == 'homepage':
            CpoQuotationRecordCode().get_website_source()
        except Exception, e:
            _logger.error("website_sale postprocess: %s value has been dropped (empty or not writable)" % e)
        return super(WebsiteSourceHome, self).page(page, **opt)


# class Inherit_CPOwebsite_account(CPOwebsite_account):
#
#     @http.route()
#     def account(self, **kw):
#         try:
#             CpoQuotationRecordCode().get_website_source()
#         except Exception, e:
#             _logger.error("Error message: %s (empty or not writable)" % e)
#         return super(Inherit_CPOwebsite_account, self).account(**kw)
#
# #
# class Inherit_WebsiteSaleElectron(WebsiteSaleElectron):
#
#     @http.route()
#     def cart(self, **post):
#         try:
#             CpoQuotationRecordCode().get_website_source()
#         except Exception, e:
#             _logger.error("Error message: %s (empty or not writable)" % e)
#         return super(Inherit_WebsiteSaleElectron, self).cart(**post)
#

# class cpo_inherit_WebsiteSale(cpo_electron_WebsiteSale):
#
#     @http.route()
#     def shop(self, page=0, category=None, search='', ppg=False, source=None, type=None, bom_id=False, ufile=None, **post):
#         try:
#             CpoQuotationRecordCode().get_website_source()
#         except Exception, e:
#             _logger.error("Error message: %s (empty or not writable)" % e)
#         return super(cpo_inherit_WebsiteSale, self).shop(page=0, category=None, search='', ppg=False, source=None, type=None, bom_id=False, ufile=None, **post)
#
#
