# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import ValidationError
from time import time

PRODUCT_TYPE = [
    ('Stencil', 'Stencil'),
    ('PCB', 'PCB'),
    ('PCBA', 'PCBA')
]

ACTIVE_STATUS = [
        ('draft', 'Draft'),  # 草稿
        ('force_no_started', 'Effective yet started'),  # 已生效未开始
        ('started_and_started', 'Effective and started'),  # 已生效且已开始
        ('invalid_over', 'Invalid and over'),  # 已失效且已结束
        ('cancel', 'Forced cancellation'),  # 取消
    ]


class CashCoupons(models.Model):
    _name = 'cash.coupons'
    _description = 'Cash Coupons'
    _order = 'id'

    name = fields.Char('Cash Voucher Name', required=True, size=64, translate=True)
    issue_number = fields.Integer('Number Of Cash Coupons Issued', default=0)
    issue_amount = fields.Float('Issue Cash Coupon Amount', digits=(16, 2), default=0.0)
    designation_bool = fields.Boolean('Specified Product Use', default=False)
    all_bool = fields.Boolean('All Product Use', default=False)
    product_type = fields.Selection(PRODUCT_TYPE, string='Product Type')
    package_bool = fields.Boolean('Can Be Used For Package Price', default=False)
    start = fields.Date('Cash Coupon Time Period', required=True)
    end = fields.Date('Cash Coupon Time Period', required=True)
    period = fields.Char('Cash Coupon Time Period')
    active = fields.Boolean('Active', default=True)
    state = fields.Selection(ACTIVE_STATUS, string='status', default='draft')
    cash_line_ids = fields.One2many('cash.coupons.line', 'cash_id', 'Cash Coupons Detail', readonly=True)
    show_bool = fields.Boolean('Show Home', default=False)  # 展示问题

    @api.onchange('all_bool')
    def _onchange_all(self):
        if self.all_bool:
            self.update({'all_bool': True, 'designation_bool': False})

    @api.onchange('designation_bool')
    def _onchange_designation(self):
        if self.designation_bool:
            self.update({'all_bool': False, 'designation_bool': True})

    @api.model
    def create(self, vals):
        return super(CashCoupons, self).create(vals)

    @api.multi
    def write(self, vals):
        return super(CashCoupons, self).write(vals)

    # 检查错误
    def CheckError(self):
        if self.issue_number <= 0 or self.issue_amount <= 0:
            raise ValidationError(_('Please set "Issuance Quantity And Amount"'))
        elif not self.all_bool and not self.designation_bool:
            raise ValidationError(_('Please set "Usage Rules"'))

    # 生效 没开始
    def ButtonEffect(self):
        self.CheckError()
        number, count, cash_id, uid = self.issue_number, 1, self.id, self._uid
        while count <= number:
            self.env.invalidate_all()
            self._cr.execute("""
                INSERT INTO cash_coupons_line 
                (create_date,write_date,cash_id,number,create_uid,write_uid,active) VALUES 
                ((timestamp '%s'), (timestamp '%s'), '%d', '%d', '%d', '%d', True)"""
                % (datetime.utcnow().isoformat(), datetime.utcnow().isoformat(), cash_id, count, uid, uid))
            count += 1
        return self.update({'state': 'force_no_started'})

    # 重置
    def ButtonReset(self):
        cash_id = self.id
        self.env.invalidate_all()
        self._cr.execute("""DELETE FROM cash_coupons_line WHERE cash_id='%s'"""% cash_id)
        return self.update({'state': 'draft'})

    # 生效 开始
    def ButtonBegins(self):
        return self.update({'state': 'started_and_started', 'show_bool': True})

    # 结束
    def ButtonInvalid(self):
        return self.update({'state': 'invalid_over', 'show_bool': False})

    # 强制取消
    def ButtonCancel(self):
        cash_id = self.id
        self.update({'state': 'cancel', 'show_bool': False, 'active': False})
        self.env.invalidate_all()
        self._cr.execute("""UPDATE cash_coupons_line WHERE cash_id='%s'""" % cash_id)
        return True

    # 手动操作是否展示该现金券
    def ShowOrWithdraw(self):
        if self.show_bool:
            self.update({'show_bool': False})
        else:
            self.update({'show_bool': True})

    # 前端接口 - 显示 以及 领取现金券
    @api.model
    def get_cash_coupon(self, args):
        return self.ReceiveCashCoupon(args)

    def ReceiveCashCoupon(self, args):
        partner_id, cash_id, value = args.get('partner_id'), args.get('cash_id'), {}
        cash_ids = self.search([('state', 'not in', ('cancel', 'invalid_over')),
                                ('show_bool', '=', True)])
        if partner_id and cash_id:
            value = self.env['cash.coupons.line'].GetReciveCash({'partner_id': partner_id, 'cash_id': cash_id})
            if value.get('warning'):
                return {'warning': value.get('warning'), 'verification': False}
            return {'value': value.get('value'), 'verification': True}
        value = {'cash_ids': cash_ids}
        return value

    # 检查现金券时间问题
    def check_cash_coupons(self):
        self._cr.execute("""SELECT ID,STATE,START,END FROM cash_coupons_line WHERE STATE NOT IN ('draft','cancel','invalid_over')""")
        dicts = self._cr.dictfetchall()
        utc_tm = datetime.utcfromtimestamp(time())
        for x_dict in dicts:
            x_id = self.browse(x_dict['id'])
            if x_dict['state'] == 'force_no_started':
                if x_dict['start'] <= str(utc_tm)[0:10] <= x_dict['end']:
                    x_id.write({'state': 'started_and_started', 'show_bool': True})
                elif x_dict['end'] < str(utc_tm)[0:10]:
                    x_id.write({'state': 'invalid_over', 'show_bool': False})
            elif x_dict['state'] == 'started_and_started':
                if x_dict['end'] < str(utc_tm)[0:10]:
                    x_id.write({'state': 'invalid_over', 'show_bool': False})
            pass


class CashCouponsLine(models.Model):
    _name = 'cash.coupons.line'
    _description = 'Cash Coupons Detail'
    _order = 'id'

    cash_id = fields.Many2one('cash.coupons', 'Cash Coupons', readonly=True, index=True, ondelete='cascade')
    sale_id = fields.Many2one('sale.order', 'Sales order', readonly=True, index=True, ondelete='cascade')
    partner_id = fields.Many2one('res.partner', "Client", readonly=True, index=True, ondelete='cascade')
    receive_bool = fields.Boolean('Whether To Receive Cash Coupons', default=False)
    use_bool = fields.Boolean('Whether To Use Cash Coupons', default=False)
    active = fields.Boolean('Active', default=True)
    number = fields.Integer('Number', readonly=True)
    issue_amount = fields.Float(related='cash_id.issue_amount', string='Issue Amount', digits=(16, 2), readonly=True)
    start = fields.Date(related='cash_id.start', string='Cash Coupon Time Period', readonly=True)
    end = fields.Date(related='cash_id.end', string='Cash Coupon Time Period', readonly=True)
    designation_bool = fields.Boolean(related='cash_id.designation_bool', string='Specified Product Use', readonly=True)
    all_bool = fields.Boolean(related='cash_id.all_bool', string='All Product Use', readonly=True)
    product_type = fields.Selection(PRODUCT_TYPE, related='cash_id.product_type', string='Product Type', readonly=True)
    package_bool = fields.Boolean(related='cash_id.package_bool', string='Can Be Used For Package Price', readonly=True)

    # 现金券领取
    def GetReciveCash(self, args):
        cash_id, partner_id = args.get('cash_id'), args.get('partner_id')
        data = self.search([('partner_id', '=', int(partner_id)), ('cash_id', '=', cash_id)])
        # 说明领取了
        if data:
            return {'warning': 'This cash coupon has already been received.'}
        # 这里可能会给领完
        data = self.search([('partner_id', '=', None), ('cash_id', '=', cash_id)], limit=1)
        if not data:
            return {'warning': 'The cash voucher was received.'}
        data.update({'partner_id': partner_id, 'cash_id': cash_id, 'receive_bool': True})
        return {'value': 'Successfully received'}

    # 使用现金券
    def GetCashCouponUse(self, args):
        order_id, cash_id = args.get('order_id'), args.get('cash_id')
        pass
