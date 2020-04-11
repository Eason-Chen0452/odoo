# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class Preferential_Sale_Order(models.Model):
    _name = 'sale.order'
    _inherit = 'sale.order'

    customer_id = fields.Many2many('preferential.cpo_customer_contact', string='Detail', readonly=True, index=False, ondelete='cascade')
    cpo_discount_type = fields.Selection([('%', '%'), ('money', 'money')], related='customer_id.cpo_discount_type', string='Discount type', default='%', readonly=True)
    cpo_no_card_bool = fields.Boolean(related='customer_id.cpo_no_card_bool', string='No card', help='Free shipping, No card product discounts', readonly=True)
    cpo_no_card_money = fields.Float(related='customer_id.cpo_no_card_money', string='Less/Discount', digits=(16, 2), readonly=True)
    cpo_card_bool = fields.Boolean(related='customer_id.cpo_card_bool', string='Card', help='Free shipping, Card product discounts', readonly=True)
    cpo_card_term = fields.Float(related='customer_id.cpo_card_term', string='Full amount', digits=(16, 2), readonly=True)
    cpo_card_money = fields.Float(related='customer_id.cpo_card_money', string='Less/Discount', digits=(16, 2), readonly=True)
    cpo_coupon_text = fields.Text('Discount Information', compute='_update_discount_information', readonly=True)

    # 将多条或单条优惠信息映射在这个字段
    @api.one
    @api.depends('cpo_coupon_text')
    def _update_discount_information(self):
        x_str = ''
        for x, x_cus in enumerate(self.customer_id, 1):
            cpo_discount_type = '%' if x_cus.cpo_discount_type == '%' else _('money')
            if x_cus.cpo_card_bool:
                x_str += str(x) + _(' Full(excluding shipping) ') + str(x_cus.cpo_card_term) + _(' Discount or discount amount ') + str(x_cus.cpo_card_money) + cpo_discount_type + '\n'
            elif x_cus.cpo_no_card_bool:
                x_str += str(x) + _(' Discount or discount amount ') + str(x_cus.cpo_no_card_money) + cpo_discount_type + '\n'
        if self.first_order_partner:
            discount = self.env['cpo_smt_price.smt'].search([('type_selection', '=', 'discount')])[0].price
            x_str += _('First discount ') + str(discount * 100 if discount < 1 else discount) + '%'
        self.update({'cpo_coupon_text': x_str})

    # @api.multi  # 计算报价按钮 - sale_order
    # def calculate_price(self):
    #     super(Preferential_Sale_Order, self).calculate_price()
    #     self.checke_coupon_discount(self.ids) # 有优惠券时 触发 - 暂时不启用

    # @api.multi
    # def write(self, vals):
    #     if vals.get('state') == 'wait_confirm' and self.quotation_line:  # 优惠券检查 - 暂时不启用
    #         self.checke_coupon_discount(self.ids)
    #     return super(Preferential_Sale_Order, self).write(vals)

    # 前端接口 优惠券 - 暂时不启用
    @api.model
    def get_website_preferential(self, args):
        return self.get_preferential_website(args)

    # 客户端选择地址页面中显示 符合条件的优惠券 同时 显示当前页面已经使用的过的优惠券 - 目前将PCBA 钢网两种封锁不得使用优惠券
    @api.multi
    def get_preferential_website(self, args):
        # 销售单-列表 客户 - 条件 时间 进行约束
        order_list, partner_id, coupon_dict, value = args.get('order_ids'), args.get('partner_id'), {}, 0
        order_ids = self.browse(order_list)
        order_ids = order_ids.filtered(lambda x: x.quotation_line and x.product_id.name not in ['PCBA', 'Stencil'] and not x.quotation_line.discount)
        for x, order_id in enumerate(order_ids):
            volume_id = self.env['cam.volume.level'].search([('name', '=', order_id.quotation_line.volume_type)]).id
            subtotal = order_id.quotation_line.subtotal  # PCB 板子价格
            sur_id = order_id.quotation_line.surface.id
            via_id = order_id.quotation_line.via_process.id
            spr_ids = order_id.quotation_line.sprocess_ids.ids
            sma_ids = order_id.quotation_line.smaterial_ids.ids
            sil_id = order_id.quotation_line.silkscreen_color.id
            coupon_ids = self.env['preferential.cpo_customer_contact'].search([('cpo_invalid_bool', '=', False),
                                                                               ('cpo_voucher_bool', '=', True),
                                                                               ('cpo_use_bool', '=', False),
                                                                               ('partner_id', '=', partner_id),
                                                                               ('cpo_con_start_time', '<=', fields.Datetime.now()),
                                                                               ('cpo_con_end_time', '>=', fields.Datetime.now()),
                                                                               ('base_type_ids', 'like', order_id.quotation_line.base_type.id),
                                                                               ('volume_level_ids', 'like', volume_id),
                                                                               ('layer_number_ids', 'like', order_id.quotation_line.layer_number.id),
                                                                               ('acceptance_criteria_ids', 'like', order_id.quotation_line.cpo_standard.id)])
            if via_id:
                coupon_ids = coupon_ids.filtered(lambda x: via_id in x.via_process_ids.ids)
            if sur_id:
                coupon_ids = coupon_ids.filtered(lambda x: sur_id in x.surface_process_ids.ids)
            if sil_id:
                coupon_ids = coupon_ids.filtered(lambda x: sil_id in x.silkscreen_color_ids.ids)
            if sma_ids and spr_ids:
                coupon_ids = coupon_ids.filtered(lambda x: set(x.special_material_ids.ids) & set(sma_ids) and set(x.special_process_ids.ids) & set(spr_ids))
            elif sma_ids:
                coupon_ids = coupon_ids.filtered(lambda x: set(x.special_material_ids.ids) & set(sma_ids))
            elif spr_ids:
                coupon_ids = coupon_ids.filtered(lambda x: set(x.special_process_ids.ids) & set(spr_ids))
            card_db = coupon_ids.filtered(lambda x: x.cpo_card_bool and x.cpo_card_term <= subtotal).ids
            no_card_db = coupon_ids.filtered(lambda x: x.cpo_no_card_bool).ids
            customer_ids = order_id.customer_id.ids
            preferential = self.env['preferential.cpo_customer_contact'].browse(card_db+no_card_db+customer_ids)
            for pre_id in preferential:
                value += 1
                y_dict = {
                    'cpo_con_start_time': pre_id.cpo_con_start_time,
                    'cpo_con_end_time': pre_id.cpo_con_end_time,
                    'cpo_discount_type': pre_id.cpo_discount_type,
                    'cpo_no_card_bool': pre_id.cpo_no_card_bool,
                    'cpo_no_card_money': pre_id.cpo_no_card_money,
                    'cpo_card_bool': pre_id.cpo_card_bool,
                    'cpo_card_term': pre_id.cpo_card_term,
                    'cpo_card_money': pre_id.cpo_card_money,
                    'cpo_coupon_id': pre_id.id,
                    'cpo_order_id': order_id.id,
                    'cpo_use': 1 if pre_id.id in customer_ids else 0,
                    'cpo_shared_bool': 1 if pre_id.cpo_shared_bool else 0,
                }
                coupon_dict.update({str(value): y_dict})
        # 目前只需要检查PCB的
        self.checke_coupon_discount(order_ids.ids)
        return {'coupon': coupon_dict}

    # 检查 优惠券使用是否异常 异常 终止使用 - 暂时不启用
    def checke_coupon_discount(self, order_list):
        order_ids = self.browse(order_list)
        amount_untaxed, amount_tax, discount, subtract = 0, 0, 0, 0
        for x_order_id in order_ids:
            amount_untaxed = sum(line.price_subtotal for line in x_order_id.order_line)
            amount_tax = sum(line.price_tax for line in x_order_id.order_line)
            if x_order_id.first_order_partner:
                discount_rule = self.env['cpo_smt_price.smt'].search([('type_selection', '=', 'discount')])
                discount = x_order_id.pricelist_id.currency_id.round(amount_untaxed * discount_rule.price)
            for x_coupon in x_order_id.customer_id:
                x_value = x_coupon.cpo_card_money if x_coupon.cpo_card_money > 0 else x_coupon.cpo_no_card_money
                subtract += amount_untaxed * (x_value / 100) if x_coupon.cpo_discount_type == '%' else x_value
            if x_order_id.quotation_line:
                x_order_id.quotation_line.write({'subtract': subtract})
            amount_untaxed += x_order_id.shipping_fee
            x_order_id.write({
                'amount_untaxed': x_order_id.pricelist_id.currency_id.round(amount_untaxed),
                'amount_tax': x_order_id.pricelist_id.currency_id.round(amount_tax),
                'amount_total': amount_untaxed + amount_tax - (discount + subtract),
                'discount_total': discount + subtract,
            })
        return True

    # 前端优惠券 实时接口 - 暂时不启用
    @api.model
    def get_coupon_use_real_time_website(self, args):
        return self.get_coupon_use_real_time_preferential(args)

    # 客户端优惠券使用的接口调用
    @api.multi
    def get_coupon_use_real_time_preferential(self, *args):
        args = args[0]
        order_id, coupon_id, partner_id = args.get('order_use_id'), args.get('coupon_id'), args.get('partner_id')
        check, order_list = args.get('checked_coupon_use'), [int(x) for x in args.get('order_names')]
        sale_order = self.browse(order_list)
        self.env['preferential.cpo_customer_contact'].get_contact_preferential({'order_id': order_id, 'coupon_id': coupon_id,
                                                                                'check': check,})
        update_data = self.get_preferential_website({'order_ids': order_list, 'partner_id': partner_id})
        update_data = update_data.pop('coupon')
        return {'coupon': update_data,
                'order_ids': sale_order}
