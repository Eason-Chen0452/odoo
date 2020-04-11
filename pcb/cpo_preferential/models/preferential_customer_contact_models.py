# -*- coding: utf-8 -*-
"""
    此模块是与优惠模块关联，客户的订单等之间的联系 - 后面可以用来做优惠政策分析
"""
from odoo import models, fields, api, _
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError


class preferential_cpo_customer_contact(models.Model):
    _name = 'preferential.cpo_customer_contact'
    _description = 'Offer to contact customers'
    _order = 'id'

    time_money_id = fields.Many2one('preferential.cpo_time_and_money', 'Offer label', readonly=True, index=True, ondelete='cascade')
    sale_order_id = fields.Many2one('sale.order', 'Sales order', readonly=True, index=True, ondelete='cascade', domain=[('state', 'in', ('sale', 'sent', 'wait_confirm'))])
    partner_id = fields.Many2one('res.partner', 'Client', readonly=True, index=True, ondelete='cascade')
    cpo_numeric = fields.Integer('Numeric', readonly=True)
    cpo_original_amount = fields.Float('Original amount', digits=(16, 3), readonly=True, compute='_update_amount', store=False)
    cpo_discounted_price = fields.Float('Discounted price', digits=(16, 3), readonly=True, compute='_update_amount', store=False)
    cpo_actual_amount = fields.Float('Actual amount', digits=(16, 3), readonly=True, compute='_update_amount', store=False)
    cpo_use_bool = fields.Boolean('Whether to use coupons', readonly=True)  # 是否使用优惠券
    cpo_coupon_bool = fields.Boolean('Coupon coupon')  # 是否领券优惠券
    cpo_coupon_time = fields.Datetime('Coupon time', readonly=True)  # 领券时间
    cpo_voucher_bool = fields.Boolean('Voucher')  # 识别哪种优惠类型
    cpo_con_start_time = fields.Date(related='time_money_id.cpo_start_time', string='Starting time', store=False, readonly=True)
    cpo_con_end_time = fields.Date(related='time_money_id.cpo_end_time', string='End time', store=False, readonly=True)
    cpo_discount_type = fields.Selection([('%', '%'), ('money', 'money')], related='time_money_id.cpo_discount_type', string='Discount type', default='%', readonly=True)
    cpo_no_card_bool = fields.Boolean(related='time_money_id.cpo_no_card_bool', string='No card', help='Free shipping, No card product discounts', readonly=True)
    cpo_no_card_money = fields.Float(related='time_money_id.cpo_no_card_money', string='Less/Discount', digits=(16, 2), readonly=True)
    cpo_card_bool = fields.Boolean(related='time_money_id.cpo_card_bool', string='Card', help='Free shipping, Card product discounts', readonly=True)
    cpo_card_term = fields.Float(related='time_money_id.cpo_card_term', string='Full amount', digits=(16, 2), readonly=True)
    cpo_card_money = fields.Float(related='time_money_id.cpo_card_money', string='Less/Discount', digits=(16, 2), readonly=True)
    cpo_allow_sharing_bool = fields.Boolean(related='time_money_id.cpo_allow_sharing_bool', string='Allow sharing', store=False, readonly=True)  # 父级允许分析
    cpo_physical_code_bool = fields.Boolean(related='time_money_id.cpo_physical_code_bool', string='Is it physical code?', store=False, readonly=True)  # 识别物理券还是电子券 True是物理券
    transfer_partner_id = fields.Many2one('res.partner', 'New customer', readonly=False, index=True, ondelete='cascade')
    color = fields.Integer('Color Index', compute='_color_replace', store=False)
    cpo_transfer_bool = fields.Boolean('Coupon transferred')  # 优惠券转让
    cpo_physical_code = fields.Char('Physical code', size=64, readonly=True)
    cpo_transfer_start_time = fields.Datetime('Transferred start time', readonly=False)
    cpo_transfer_end_time = fields.Datetime('Transferred end time', readonly=False)
    active = fields.Boolean('Active', default=True)
    cpo_invalid_bool = fields.Boolean(related='time_money_id.cpo_invalid_over_bool', string='Invalid over')  # 为True的时候 失效不能使用此优惠券
    cpo_public_bool = fields.Boolean('Tourist Status', default=False, readonly=True)  # 游客身份
    cpo_public_code = fields.Char('Tourist identification code', readonly=True)  # 游客身份识别码
    cpo_public_time = fields.Date('Tourist Time', readonly=True)  # 游客拿到此优惠券的时间戳
    cpo_public_coupon_bool = fields.Boolean(related='time_money_id.cpo_public_coupon_bool', string='Due to distribution to other websites', readonly=True)
    base_type_ids = fields.Many2many('cam.base.type', string='Base type', related='time_money_id.base_type_ids', readonly=True)
    # text_color_ids = fields.Many2many('cam.ink.color', string='Text color', related='time_money_id.text_color_ids', readonly=True)
    via_process_ids = fields.Many2many('cam.via.process', string='Via process', related='time_money_id.via_process_ids', readonly=True)
    volume_level_ids = fields.Many2many('cam.volume.level', string='Volume level', related='time_money_id.volume_level_ids', readonly=True)
    layer_number_ids = fields.Many2many('cam.layer.number', string='Layer number', related='time_money_id.layer_number_ids', readonly=True)
    material_brand_ids = fields.Many2many('cam.material.brand', string='Material brand', related='time_money_id.material_brand_ids', readonly=True)
    silkscreen_color_ids = fields.Many2many('cam.ink.color', string='Silkscreen color', related='time_money_id.silkscreen_color_ids', readonly=True)
    special_process_ids = fields.Many2many('cam.special.process', string='Special process', related='time_money_id.special_process_ids', readonly=True)
    surface_process_ids = fields.Many2many('cam.surface.process', string='Surface process', related='time_money_id.surface_process_ids', readonly=True)
    special_material_ids = fields.Many2many('cam.special.material', string='Special material', related='time_money_id.special_material_ids', readonly=True)
    acceptance_criteria_ids = fields.Many2many('cam.acceptance.criteria', string='Acceptance criteria', related='time_money_id.acceptance_criteria_ids', readonly=True)
    cpo_shared_bool = fields.Boolean(related='time_money_id.cpo_shared_bool', string='Shared coupon', readonly=True)
    cpo_no_shared_bool = fields.Boolean(related='time_money_id.cpo_no_shared_bool', string='Not Shared coupon', readonly=True)

    # 优惠券 时间段数据分析
    def time_coupon_date_analysis(self, *args):
        # 单一的数据分析
        if "x_id" in args[0].keys():
            x_db = self.env['preferential.cpo_time_and_money'].browse(args[0].get('x_id'))
            # 时间段
            if x_db.cpo_date_bool:
                pass
            # 优惠券
            elif x_db.cpo_amount_bool:
                pass
        # 多元素数据分析
        elif "x_ids" in args[0].keys():
            pass

    # 看板中 明细详情 优惠券领取了是绿色 使用了是黄色 如果不是优惠券 交易量直接是黄色
    @api.depends('color')
    def _color_replace(self):
        for x_id in self:
            # x_id = self.id
            self._cr.execute("""SELECT cpo_use_bool,cpo_coupon_bool FROM preferential_cpo_customer_contact WHERE id = %s""", (x_id.id,))
            dicts = self._cr.dictfetchall()[0]
            if x_id.cpo_voucher_bool:
                if dicts['cpo_use_bool'] and dicts['cpo_coupon_bool']:
                    x_id.update({'color': 5})
                elif dicts['cpo_coupon_bool']:
                    x_id.update({'color': 3})
            elif not x_id.cpo_voucher_bool:
                x_id.update({'color': 5})
        return True

    # 原金额 优惠金额 实际金额 - 暂时这样 - 目前只取 销售单中有PCB板子的单
    # @api.one
    @api.depends('cpo_original_amount', 'cpo_discounted_price', 'cpo_actual_amount')
    def _update_amount(self):
        for x_id in self:
            if x_id.sale_order_id:
                amount_total = self.sale_order_id.quotation_line.subtotal  # 实际总额
                discount_total = self.sale_order_id.quotation_line.subtract  # 折扣金额
                amount_untaxed = amount_total + discount_total  # 未含税金额 - 小计
                # self.time_money_id.search([('id', '=', self.time_money_id.id)])
                x_id.update({
                    'cpo_original_amount': amount_untaxed,
                    'cpo_discounted_price': discount_total,
                    'cpo_actual_amount': amount_total
                })
        return True

    # 接口调用 - 只负责优惠券的领取 - 同时将优惠券与客户进行关联
    @api.multi
    def get_coupon_collection(self, args):
        coupon_id = args.get('coupon_id')
        user_id = args.get('user_id')
        customer_db = self.search([('time_money_id', '=', coupon_id), ('partner_id', '=', user_id)])
        # 说明客户领取的优惠了
        if customer_db:
            return {'warning': 'This coupon has already been received.'}
        cus_db = self.search([('time_money_id', '=', int(coupon_id)), ('partner_id', '=', None)], limit=1)
        receive_time = datetime.strptime(fields.Datetime.now(), '%Y-%m-%d %H:%M:%S') + timedelta(hours=8)
        cus_db.update({'partner_id': user_id, 'cpo_coupon_time': receive_time, 'cpo_coupon_bool': True})
        return {'value': 'Successfully received'}

    # 接口调用 - 在选择使用优惠券时 只有同类型的同享券可以多张使用 其他的不可以同时使用 - 使用的同时将报价的价格进行更新
    @api.multi
    def get_contact_preferential(self, args):
        order_id, coupon_id, discount_total, check, cus_list = args.get('order_id'), args.get('coupon_id'), 0, args.get('check'), []
        sale_order = self.env['sale.order'].browse(int(order_id))
        preferential = self.browse(int(coupon_id))
        cus_yes = sale_order.customer_id.filtered(lambda x: x.cpo_shared_bool).ids  # 同享 可能是一条
        coupon_list = [int(coupon_id)]
        if sale_order.customer_id:
            if len(cus_yes) >= 1 and preferential.cpo_shared_bool is True and check:
                coupon_list = cus_yes + coupon_list
                preferential = self.browse(coupon_list)
            sale_order.quotation_line.write({'subtract': 0})
            sale_order.customer_id.write({'sale_order_id': False, 'cpo_use_bool': False})
            sale_order.write({'customer_id': [(5, sale_order.customer_id.ids)], 'discount_total': 0})
        subtract = sale_order.quotation_line.subtract  # 优惠
        subtotal = sale_order.quotation_line.subtotal
        if check:
            for x_id in preferential:
                x_id.write({'sale_order_id': order_id, 'cpo_use_bool': True})
                x_value = x_id.cpo_card_money if x_id.cpo_card_money > 0 else x_id.cpo_no_card_money
                subtract += subtotal * (x_value / 100) if x_id.cpo_discount_type == '%' else x_value
            sale_order.write({'customer_id': [(6, 0, coupon_list)], 'discount_total': subtract})
            sale_order.quotation_line.write({'subtract': subtract})
        if len(cus_yes) > 1 and check is False and int(coupon_id) in cus_yes:  # 情况不同 不得删除 - 如果两张同享 点掉一张 另外一张应该保留
            cus_yes.remove(int(coupon_id))
            cus_db = self.browse(cus_yes)
            for y_id in cus_db:
                y_id.write({'sale_order_id': sale_order.id, 'cpo_use_bool': True})
                x_value = y_id.cpo_card_money if y_id.cpo_card_money > 0 else y_id.cpo_no_card_money
                subtract += subtotal * (x_value / 100) if y_id.cpo_discount_type == '%' else x_value
            sale_order.write({'customer_id': [(6, 0, cus_yes)], 'discount_total': subtract})
            sale_order.quotation_line.write({'subtract': subtract})
        sale_order.write({'amount_total': (subtotal - subtract)})
        return True

    # # 明细显示 接口 - 暂时保留
    # @api.model
    # def get_contact_price(self, *args):
    #     args = args[0]
    #     user_id = args.get('user_id')
    #     coupon_ids = self.search([('cpo_invalid_bool', '=', False),
    #                               ('cpo_voucher_bool', '=', True),
    #                               ('cpo_use_bool', '=', False),
    #                               ('partner_id', '=', user_id)]).ids
    #     return coupon_ids

    # 路由接口调用 - 通过其他网站点击领取优惠券时给游客进行标记 - 目前只要传给我一个随机生成的13身份识别码
    @api.multi
    def get_public_mark_coupon(self, args):
        public_code = args.get('public_code')
        if len(public_code) != 13:
            raise ValidationError('Does not meet the rules')
        # 条件是 游客使用的系列 有物理码 没有游客占用 没有用户占用 有效的
        public_ids = self.search([('cpo_public_coupon_bool', '=', True),
                                  ('cpo_invalid_bool', '=', False),
                                  ('cpo_voucher_bool', '=', True),
                                  ('cpo_physical_code_bool', '=', True),
                                  ('cpo_use_bool', '=', False),
                                  ('cpo_public_bool', '=', False)])
        # 搜索得到的结果 取其中一条
        public_id = public_ids[0]
        # 将这一条进行记录登记 cpo_public_bool, cpo_public_code, cpo_public_time
        public_id.write({'cpo_public_bool': True, 'cpo_public_code': public_code, 'cpo_public_time': fields.Datetime.now()})
        # 之后返回一个物理码
        return {'coupon_code': public_id.cpo_physical_code}


