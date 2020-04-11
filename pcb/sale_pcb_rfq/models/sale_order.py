# -*- coding: utf-8 -*-

import xlrd, base64, random, werkzeug
from datetime import datetime, timedelta
from time import time
from urlparse import urljoin
from base64 import b64encode as e64
from odoo.exceptions import ValidationError
from odoo.addons.cpo_offer_base.models.cpo_offer_bom import recheck_bom_file_content
from odoo.addons.cpo_offer_base.models.cpo_inherit_sale_order import SaleOrderLine
from odoo import models, fields, api, _
from odoo.tools import pycompat


def random_token(string=False):
    # the token has an entropy of about 120 bits (6 bits/char * 20 chars)
    chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    if string:
        return ''.join(random.SystemRandom().choice(chars) for _ in pycompat.range(8))
    else:
        return random.choice(chars)


class RFQSaleOrderModify(models.Model):
    _name = 'rfq.sale.order.modify'
    _order = 'china_time desc'

    china_time = fields.Datetime('China Time')
    cpo_seller = fields.Char('Seller')
    cpo_old_field = fields.Char('Original Value')
    cpo_new_field = fields.Char('Modified Value')
    cpo_modify = fields.Char('Modify What', index=True)
    order_id = fields.Many2one('sale.order', 'Sale Order', index=True)


class MakeCircuit(models.Model):
    _name = 'make.circuit'
    _description = 'Production Process Information'

    name = fields.Char('Name', size=64)
    make_time = fields.Datetime('Make Time')
    order_id = fields.Many2one('sale.order', 'Sale Order', index=True, ondelete='cascade')


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    _order = 'id desc'

    WEB_TYPE = [
        ('package-price', 'package-price'),
        ('standard', 'standard'),
        ('rigid-flex', 'rigid-flex'),
        ('hdi', 'hdi'),
        ('stencil', 'stencil'),
        ('no-material', 'no-material'),
        ('material', 'material'),
        ('standard', 'standard'),
    ]

    STATE = [
        ('draft', 'Draft'),  # 询价 - 不检查
        ('wait_confirm', 'Quotation Pending'),  # 报价单待检查
        ('sent', 'Quotation Sent'),  # 报价单送出
        ('sale', 'Pending Invoice'),  # 待开发票
        ('wait_payment', 'Waiting Payment'),  # 待登记付款
        ('wait_make', 'To Be Manufactured'),  # 待制造
        ('request_refund', 'Request A Refund'),  # 申请退款 - 正常情况 不会有这个状态
        ('manufacturing', 'In Manufacturing'),  # 制造中
        ('wait_delivery', 'Waiting Delivery'),  # 待快递单号
        ('wait_receipt', 'Wait Receipt'),  # 等待收货
        ('complete', 'Complete'),  # 客户收到完毕 - 暂时算是彻底完成
        ('refunded', 'Refunded'),  # 已退款 - 正常情况 不会有这个状态
        ('done', 'Locked'),  # 锁
        ('cancel', 'Cancelled'),  # 取消
        # ('markup_draft', 'Draft'),  # 草稿
        ('markup', 'Increase Cost'),  # 增加费用
    ]

    # 目前有8个索引字段
    quotation_line = fields.One2many("sale.quotation.line", 'order_id', 'PCB Quotation Line', auto_join=True)
    stencil_line = fields.One2many('sale.stencil.line', 'sale_order_id', 'Stencil line', auto_join=True)
    product_type = fields.Char('Product type', size=64, readonly=True, compute='_get_product_type', store=True)
    cpo_text = fields.Text('Remarks', compute='_get_remarks_text', readonly=True)  # 客户的留言
    state = fields.Selection(STATE, string='Stats', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft', group_expand='_expand_states')
    cpo_lock_bool = fields.Boolean(default=False)
    cpo_courier_bool = fields.Boolean(default=False, string='Whether To Pay')  # 为True表示 到付
    cpo_courier = fields.Selection([('DHL', 'DHL'), ('UPS', 'UPS'), ('Fedex', 'Fedex')], string='Courier')  # 快递方式
    cpo_courier_number = fields.Char('Tracking Number')  # 快递单号
    cpo_sale_text = fields.Text('Sale Text')
    modify_ids = fields.One2many('rfq.sale.order.modify', 'order_id', 'Sale Order Modify Recording', auto_join=True)
    modify_name_id = fields.Many2one('res.users', 'Modify Name', track_visibility='onchange', ondelete='cascade')
    calculate_bool = fields.Boolean("Calculation", default=False)
    package_bool = fields.Boolean(string='Package Price Order', compute='_get_product_name', store=True)  # 打包价
    proof_bool = fields.Boolean(string='Package Price Order')  # 此属性是为了证明有打包价变为常规时 计算按钮需要重新计算
    product_name = fields.Char('Product name', size=64, readonly=True, compute='_get_product_name', store=True, translate=True)
    web_type = fields.Selection(WEB_TYPE, string='Website Type', compute='_get_product_name', store=True)
    quotation_bool = fields.Boolean('PCB Quotation Line', compute='_get_display_content', store=True)
    stencil_bool = fields.Boolean('Stencil line', compute='_get_display_content', store=True)
    modify_bool = fields.Boolean('Sale Order Modify Recording', compute='_get_display_content', store=True)
    refund_bool = fields.Boolean('Refund', compute='_get_refund_bool', store=True)
    circuit_ids = fields.One2many('make.circuit', 'order_id', 'Production Process Information', auto_join=True)  # 这个字段用来展示筛选过后的工艺流程
    client_account = fields.Char("Customer's Account", size=64, readonly=True)
    markup_order_id = fields.Many2one('sale.order', 'Sale Order', ondelete='cascade')  # 识别父级订单 只是作用于加收费用的
    markup_bool = fields.Boolean('Markup', default=False)  # 识别子订单
    order_markup_bool = fields.Boolean('Order Markup', default=False)  # 识别父级订单 只是作用于加收费用的
    unquote_bool = fields.Boolean('Order Unquote', default=False)

    @api.depends('state')
    def _get_refund_bool(self):
        for x_id in self:
            x_id.refund_bool = True if x_id.state not in ['manufacturing', 'wait_delivery', 'wait_receipt', 'complete', 'refunded', 'request_refund'] else False

    @api.depends('quotation_line', 'stencil_line', 'modify_ids')
    def _get_display_content(self):
        for x_id in self:
            if x_id.quotation_line:
                x_id.quotation_bool = True
            if x_id.stencil_line:
                x_id.stencil_bool = True
            if x_id.modify_ids:
                x_id.modify_bool = True

    @api.depends('product_type', 'order_line.product_id')
    def _get_product_type(self):
        for x_id in self:
            x_id.product_type = x_id.product_id.name

    # 直观的分类
    @api.one
    @api.depends('product_type', 'order_line.product_id', 'package_bool')
    def _get_product_name(self):
        name = self.product_id.name
        if name == 'Stencil':
            self.product_name, self.web_type = name, 'stencil'
        elif name == 'PCBA':
            if self.order_line.package_type == 'Material':
                self.product_name = _('Package Price Material') + name
                self.package_bool, self.web_type = True, 'material'
            elif self.order_line.package_type == 'No Material':
                self.product_name = _('Package Price No Material') + name
                self.package_bool, self.web_type = True, 'no-material'
            else:
                self.product_name, self.web_type = name, 'standard'
        elif name:
            quote = self.quotation_line
            if quote.package_bool:
                self.product_name = _('Package Price') + name
                self.package_bool, self.web_type = True, 'package-price'
            elif quote.cpo_hdi and quote.cpo_hdi != '0':
                self.product_name, self.web_type = 'HDI ' + name, 'hdi'
            elif quote.core_thick > 0 and quote.rogers_number > 0:
                self.product_name = 'Rogers ' + name
                self.web_type = 'standard'
            elif quote.outer_copper >= 6:
                self.product_name = _('Extra Thick Copper Foil') + name
                self.web_type = 'standard'
            elif quote.soft_level and quote.soft_number > 0:
                self.product_name = _('PCB Soft And Hard Combination')
                self.web_type = 'rigid-flex'
            else:
                self.product_name, self.web_type = name, 'standard'

    def _expand_states(self, states, domain, order):
        return [key for key, val in type(self).state.selection if key not in ('done', 'cancel', 'draft', 'complete', 'refunded', 'request_refund')]

    # 继承cpo_offer_base中cpo_inherit_sale_order的方法 只增加一句话
    @api.depends('order_line.price_total', 'first_order_partner', 'shipping_fee')
    def _amount_all(self):
        for order in self:
            amount_untaxed = amount_tax = 0.0
            discount = 0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
            if order.first_order_partner:
                discount_rule = self.env['cpo_smt_price.smt'].search([('type_selection', '=', 'discount')])
                discount = order.pricelist_id.currency_id.round(amount_untaxed * discount_rule.price)
            if order.quotation_line:  # 增加这一句
                discount += order.quotation_line.subtract
            amount_untaxed += order.shipping_fee
            order.update({
                'amount_untaxed': order.pricelist_id.currency_id.round(amount_untaxed),
                'amount_tax': order.pricelist_id.currency_id.round(amount_tax),
                'amount_total': amount_untaxed + amount_tax - discount,
                'discount_total': discount,
            })

    # 自动将客户端的留言映射在这个字段
    @api.one
    @api.depends('quotation_line.request', 'stencil_line.cpo_stencil_text', 'order_line.cpo_note')
    def _get_remarks_text(self):
        pcb, stencil, pcba, x_str = '', '', '', ''
        if len(self.order_line) == 1 and self.order_line.cpo_note:
            pcba = self.order_line.cpo_note
            if pcba:
                x_str += 'PCBA Product Message: ' + pcba + '\r\n'
        if self.quotation_line.request:
            pcb = self.quotation_line.request
            if pcb:
                x_str += 'PCB Product Message: ' + pcb + '\r\n'
        if self.stencil_line.cpo_stencil_text:
            stencil = self.stencil_line.cpo_stencil_text
            if stencil:
                x_str += 'Stencil Product Message: ' + stencil + '\r\n'
        self.cpo_text = x_str

    # 订单创建成功 同时进行product_type产品名的映射
    @api.model
    def create(self, vals):
        res = super(SaleOrder, self).create(vals)
        if res.partner_id.id != self.env.ref("base.public_partner").id:
            res.update_cpo_customer_id()
        return res

    # 这里理论上应该会有文件上传 - 情况很多
    @api.one
    @api.multi
    def write(self, vals):
        var = ['stencil_line', 'order_line', 'quotation_line']
        if len(self) == 1 and (set(var) & set(vals.keys())) and self.cpo_lock_bool:
            vals = self._check_fields(vals)
            self._automatic_recording(vals)
        if 'user_id' in vals.keys():
            self.update_quotation_user_id_for_order(user_id=vals.get('user_id'))
        if vals.get('state') == 'wait_confirm':
            freight, partner_bool = 0, False
            if self.stencil_line:  # 有钢网 文件更新
                self.update_stencil_line_file()
                if self.cpo_courier_bool is False:  # 不是 到付 在计算钢网的快递费
                    freight = self.update_stencil_line_shipping_fee()
            if self.quotation_line and self.cpo_courier_bool is False:
                freight = self.freight_function_transfer()
            if self.partner_id.whether_discount:
                partner_bool = True if not self.quotation_line.discount else False
                if partner_bool:
                    self.partner_id.update({'whether_discount': False})
            vals.update({'first_order_partner': partner_bool, 'shipping_fee': freight})
            self.env['order.notice'].CreateNotice(self)
        if vals.get('state') == 'sale' and self.product_type == 'PCBA':
            if self.order_line.etdel <= 0:
                raise ValidationError(_("It is detected that the product is PCBA and the delivery time is manually filled in, Click on the 'Order Line' details to fill in the 'Estimated Delivery Time'."))
        return super(SaleOrder, self).write(vals)

    # 删除相关联的PCB订单
    @api.multi
    def unlink(self):
        for x_id in self:
            quotation_id = x_id.quotation_line.quotation_id
            quotation_id.unlink()
        return super(SaleOrder, self).unlink()

    @api.model
    def set_sale_person_rule_active(self, rule_id, value):
        try:
            self.env.ref(rule_id).write({'active': value})
        except Exception:
            pass
        return

    # 用来检查哪些字段不能更改的 - 销售员一更改就报错
    def _check_fields(self, value):
        group_ids = self.env['res.users'].browse(self._uid).groups_id.ids
        group_id = self.env.ref('sales_team.group_sale_manager').id
        quotation_list = ['tax_id', 'customer_file_name', 'cpo_buried_blind_id', 'subtract', 'reorder_no_change','set_material_fee',
                          'other_fee', 'process_fee', 'test_fee', 'engine_fee', 'set_drill_fee', 'set_test_tooling_fee', 'set_film_fee']
        order_list = ['analytic_tag_ids', 'customer_lead', 'etdel', 'tax_id', 'route_id', 'layout_category_id', 'product_packaging',
                      'product_uom_qty', 'product_uom', 'pcb_plate_fee', 'special_fee', 'invoice_lines', 'bom_rootfile', 'product_id',
                      'cpo_note', 'pcb_special', 'price_unit']
        if 'order_line' in value.keys():
            number = len(set(value['order_line'][0][2]) - set(order_list))
            if number != 0 and group_id not in group_ids:
                raise ValidationError(_('You have modified ‘price’ or ‘customer information’'))
            if (self.quotation_line or self.stencil_line) and 'product_uom_qty' in value['order_line'][0][2].keys():
                raise ValidationError(_("It is detected that there is 'steel mesh detail' or 'PCB detail' in the quotation. It is not allowed to modify the quantity directly in the order line. If you want to modify it, modify it in these two parts list."))
        if 'quotation_line' in value.keys():
            quotation_dict = value.get('quotation_line')[0][2]
            number = len(set(quotation_dict.keys()) - set(quotation_list))
            if len(quotation_dict) != number and group_id not in group_ids:
                raise ValidationError(_('You have modified ‘price’ or ‘customer information’'))
            if 'layer_number' in quotation_dict.keys() and self.product_type != 'PCBA':
                layer = quotation_dict.get('layer_number')
                product_id = self.env['cam.layer.number'].browse(layer).product_ids.id
                value['order_line'][0][2].update({'product_id': product_id})
            if 'product_uom_qty' in quotation_dict.keys():
                value['order_line'][0][2].update({'product_uom_qty': quotation_dict.get('product_uom_qty')})
        if 'stencil_line' in value.keys():
            if 'cpo_stencil_qty' in value.get('stencil_line')[0][2].keys():
                value['order_line'][0][2].update({'product_uom_qty': value.get('stencil_line')[0][2].get('cpo_stencil_qty')})
        return value

    # 记录销售人员 修改的订单
    def _automatic_recording(self, value):
        if self._uid != self.modify_name_id.id:
            raise ValidationError(_('You are not {name}; Do not modify more than one person').format(name=self.modify_name_id.name))
        sale_name = self.modify_name_id.name
        china_time = datetime.utcfromtimestamp(time())
        modify_dict = {'cpo_seller': sale_name, 'china_time': str(china_time), 'order_id': self.id}
        models_list = ['sprocess_ids', 'smaterial_ids', 'tax_id', 'analytic_tag_ids', 'invoice_lines']
        for x_dict in value:
            if type(value[x_dict]) is not list:
                continue
            for x_key in value[x_dict][0][2]:
                x_value = value[x_dict][0][2][x_key]
                old_value = eval('self.'+x_dict+'.'+x_key)  # 可能是值 也可能是对象
                new_value = x_value if x_key not in models_list else x_value[0][2]
                if not old_value and (new_value is False or not new_value):
                    continue
                modify_name = eval('self.'+x_dict+'._fields["%s"].string' % x_key)
                old_value = old_value if type(old_value) not in [float, int] else float(old_value)
                new_value = new_value if type(new_value) not in [float, int] else float(new_value)
                modify_dict.update({'cpo_modify': modify_name, 'cpo_old_field': str(old_value), 'cpo_new_field': str(new_value)})
                if type(old_value) not in [int, float, str, unicode, bool]:
                    new_value = new_value if type(new_value) is not float else int(new_value)
                    name_model = self.env[old_value._name].browse(new_value)
                    old_str, new_str = '', ''
                    for old in old_value:
                        old_str += unicode(old.name)+','
                    for new in name_model:
                        new_str += unicode(new.name)+','
                    modify_dict.update({'cpo_old_field': old_str, 'cpo_new_field': new_str})
                modify_id = self.modify_ids.search([('cpo_modify', '=', modify_name), ('order_id', '=', self.id)])
                if modify_id:
                    modify_dict.pop('cpo_old_field')
                    if modify_id.cpo_old_field == str(modify_dict.get('cpo_new_field')):
                        modify_id.unlink()
                    else:
                        modify_id.write(modify_dict)
                else:
                    self.modify_ids.create(modify_dict)

    # 当已经生成 且完成收货地址选择时 钢网独立报价进行更新
    def update_stencil_line_shipping_fee(self):
        for x_id in self:
            weight, country_id = x_id.stencil_line.cpo_stencil_weight, x_id.partner_shipping_id
            freight = self.env['cpo.pcb.freight'].cpo_create_freight({'weight': weight, 'country_id': country_id})
            return freight

    # 钢网文件更新名字
    def update_stencil_line_file(self):
        for x_id in self:
            file_name = self.env['ir.attachment'].search([('res_model', '=', x_id._name), ('res_id', '=', x_id.id)]).name
            x_id.order_line.write({'customer_file_name': file_name})
        return True

    # 更新cpo_customer_id 此字段是要取登入账户的id号非客户id
    @api.multi
    def update_cpo_customer_id(self, x_uid=False):
        for x_id in self:
            if not x_uid:
                x_uid = self.env['res.users'].search([('partner_id', '=', x_id.partner_id.id)]).id
            x_id.write({'cpo_customer_id': x_uid})
        return True

    # 订单创建的时候 将文件进行更新关联
    @api.multi
    def cpo_update_file(self, args):
        order_id, x_file, file_list_ids, att_list_ids = args.get('order_id'), args.pop('create_upload_file'), [], []
        ger_file_id, bom_file_id, smt_file_id = x_file.get('gerber_file_id'), x_file.get('bom_file_id'), x_file.get('smt_file_id')
        ger_att_id, bom_att_id, smt_att_id = x_file.get('gerber_atta_id'), x_file.get('bom_atta_id'), x_file.get('smt_atta_id')
        sale_order = self.browse(order_id) if type(order_id) is not dict else self.env['sale.order.line'].browse(order_id['line_id']).order_id
        sh_header, rows, att_row = [], [], None
        if ger_file_id:
            file_list_ids.append(int(ger_file_id))
            att_list_ids.append(int(ger_att_id))
        if bom_file_id:
            file_list_ids.append(int(bom_file_id))
            att_list_ids.append(int(bom_att_id))
        if smt_file_id:
            file_list_ids.append(int(smt_file_id))
            att_list_ids.append(int(smt_att_id))
        file_ids = self.env['cpo_annex_file'].browse(file_list_ids)
        att_ids = self.env['ir.attachment'].browse(att_list_ids)
        for x_annex, x_att in zip(file_ids, att_ids):
            self.create_atta_for_saleorder(sale_order.id, x_annex.name, x_annex.file_type, x_att.datas)
        try:
            att_row = self.env['ir.attachment'].browse(int(bom_att_id))
            data = att_row.datas
            excel = xlrd.open_workbook(file_contents=base64.b64decode(data))
            sh = excel.sheet_by_index(0)
            for rx in range(0, sh.nrows):
                cols = []
                for ry in range(0, sh.ncols):
                    cols.append(sh.cell(rx, ry).value)
                rows.append(cols)
            rows = recheck_bom_file_content(rows)
            for row in rows:
                for x_row in row:
                    sh_header.append(x_row)
                break
        except Exception:
            pass
        if rows and sh_header:
            ref_list = []
            x_item = set(','.join('item').split(','))
            x_qty = set(','.join('quantity').split(','))
            x_pn = set(','.join('p/n').split(','))
            x_bom = set(','.join('bom description').split(','))
            x_ven = set(','.join('vendor p/n').split(','))
            x_mfr = set(','.join('manufacturer').split(','))
            x_mfr_pn = set(','.join('manufacturer p/n').split(','))
            for x in sh_header:
                x_value = set(','.join(x.lower()).split(','))
                min_x = min(len(list(x_item ^ x_value)), len(list(x_qty ^ x_value)), len(list(x_pn ^ x_value)),
                            len(list(x_bom ^ x_value)),
                            len(list(x_ven ^ x_value)), len(list(x_mfr ^ x_value)), len(list(x_mfr_pn ^ x_value)))
                if min_x == len(list(x_item ^ x_value)):
                    x_dict = {'src_title': x, 'cpo_title': 'cpo_item'}
                elif min_x == len(list(x_qty ^ x_value)):
                    x_dict = {'src_title': x, 'cpo_title': 'cpo_qty'}
                elif min_x == len(list(x_pn ^ x_value)):
                    x_dict = {'src_title': x, 'cpo_title': 'cpo_p_n'}
                elif min_x == len(list(x_bom ^ x_value)):
                    x_dict = {'src_title': x, 'cpo_title': 'cpo_description'}
                elif min_x == len(list(x_ven ^ x_value)):
                    x_dict = {'src_title': x, 'cpo_title': 'cpo_vendor_p_n'}
                elif min_x == len(list(x_mfr ^ x_value)):
                    x_dict = {'src_title': x, 'cpo_title': 'cpo_mfr'}
                elif min_x == len(list(x_mfr_pn ^ x_value)):
                    x_dict = {'src_title': x, 'cpo_title': 'cpo_mfr_p_n'}
                else:
                    x_dict = {'src_title': x}
                ref_list.append(x_dict)
            sale_order.write({'check_state': 'check_on'})
            fields_line = self.env['cpo_bom_fields.line']
            supply_list = self.env['cpo_bom_supply.list']
            supply_list.del_old_data(order_id=sale_order.id)
            fields_line.del_old_data(order_id=sale_order.id)
            for row in ref_list:
                row.update({'order_id': sale_order.id})
                fields_line.to_create_fields_ref(row)
            bom_res = sale_order.create_new_bom_for_saleorder(sale_order.partner_id.id)
            bom_att_obj = bom_res.get('atta_obj')
            fields_line_for = self.env['cpo_bom_fields.line_for_bom']
            supply_list_for = self.env['cpo_bom_supply.list_for_bom']
            bom_obj = self.env['cpo_offer_bom.bom'].search([('id', '=', bom_att_obj.res_id)])
            supply_list_for.del_old_data(bom_id=bom_obj.id)
            fields_line_for.del_old_data(bom_id=bom_obj.id)
            for row in ref_list:
                row.update({'bom_id': bom_obj.id})
                fields_line_for.to_create_fields_ref(row)
            bom_obj.to_auto_import_date()
        return True

    # 确定快递方式 - 收货地址时触发 - 前端交互
    @api.model
    def customer_delivery_method(self, args):
        client, express, order_list, account_number = args.get('cpo_supply_method'), args.get('cpo_express_select'), args.get('order_list'), args.get('account_number')
        if client == 'yes':  # 客户选择到付
            for x_id in order_list:
                x_id.write({'cpo_courier_bool': True, 'cpo_courier': express, 'client_account': account_number})
        elif client == 'no':
            for x_id in order_list:
                x_id.write({'cpo_courier_bool': False, 'cpo_courier': express})
        return True

    # 独立计算运费接口
    def get_order_freight(self, order_ids):
        order = self.browse(order_ids).filtered(lambda x: x.product_type != 'PCBA')
        return order.freight_function_transfer(web=True)

    # 运费调用 - 在客户端生成订单选择地址会调用 同时 计算sale_order计算价格会调用 - 这是PCB运费的调用
    def freight_function_transfer(self, web=False):
        freight_dict = {}
        for x_id in self:
            freight_fee = {
                'address': x_id.partner_shipping_id,
                'meter': x_id.quotation_line.total_size,
                'thick': x_id.quotation_line.thickness,
                'inner': x_id.quotation_line.inner_copper,
                'outer': x_id.quotation_line.outer_copper,
                'layer': x_id.quotation_line.layer_number.layer_number,
                'frame': x_id.quotation_line.cpo_type_steel_mesh
            }
            freight_fee = self.env['cpo.pcb.freight'].cpo_create_freight(freight_fee)
            freight_fee = freight_fee if (freight_fee - int(freight_fee)) == 0 else int(freight_fee) + 1
            if x_id.product_type == 'PCBA':
                freight_fee = round(freight_fee * 1.5, 0)
            if not web:
                return freight_fee
            else:
                freight_dict.update({x_id.id: freight_fee})
        if web:
            return freight_dict

    # sale_quotation里的客户信息及销售人员 与 sale_order的同步
    @api.multi
    def update_quotation_user_id_for_order(self, user_id=False):
        for order in self:
            vals = {
                'user_id': user_id,
                'partner_id': order.partner_id.id,
                'partner_invoice_id': order.partner_invoice_id.id,
                'partner_shipping_id': order.partner_shipping_id.id
            }
            if order.quotation_line.quotation_id:
                if not user_id:
                    vals.update({'user_id': order.user_id.id})
                order.quotation_line.quotation_id.write(vals)
        return True

    @api.multi  # 计算报价按钮 - sale_order
    def calculate_price(self):
        if self.product_type == 'PCBA' and not self.package_bool:  # 除去打包价
            super(SaleOrder, self).calculate_price()
        elif self.product_type == 'PCBA' and self.bom_state != 'complete':
            raise ValidationError(_('BOM has not been checked yet'))
        if self.cpo_courier_bool is False:
            if self.quotation_line:
                self.shipping_fee = self.freight_function_transfer()
            if self.stencil_line:
                self.shipping_fee = self.update_stencil_line_shipping_fee()
        if self.product_type != 'PCBA':
            for line in self.order_line:
                if line.product_id.type == 'pcb':
                    line.update_pcb_price = False if line.update_pcb_price else True
                if line.product_id.name == 'Stencil':
                    line.update_stencil_price = False if line.update_stencil_price else True
        if not self.calculate_bool:
            self.calculate_bool = True
        if self.proof_bool and not self.package_bool:
            if self.quotation_line:
                self.quotation_line.pcb_price_calculation(self.quotation_line.id)
        self.order_line.price_unit = self.order_line.price_total / self.order_line.product_uom_qty

    # 发现Gerber文件与订单有问题 - cpo_lock_bool为True 进行修改 - 只允许在待确定下
    def update_sale_order_lock_true(self):
        self.write({'cpo_lock_bool': True, 'modify_name_id': self._uid})
        view_id = self.env.ref('sale.view_order_form').id
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sale.order',
            'res_id': self.id,
            "flags": {'mode': 'edit'},
            "target": 'current',
            'views': [[view_id, 'form']],
        }

    # 发现Gerber文件与订单有问题 - cpo_lock_bool为FALSE 修改完成 - 只允许在待确定下
    def update_sale_order_lock_false(self):
        if self.modify_name_id.id != self._uid:
            raise ValidationError(_('You are not {name}; Do not modify more than one person').format(name=self.modify_name_id.name))
        self.write({'cpo_lock_bool': False, 'modify_name_id': None, 'calculate_bool': False})

    # 点击按钮 返回到 PCB 订单中
    def Check_PCB_views(self):
        if self.quotation_line:
            view_id = self.env.ref('sale_pcb_rfq.view_sale_quotation_form').id
            return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'sale.quotation',
                'res_id': self.quotation_line.quotation_id.id,
                'views': [[view_id, 'form']],
            }
        else:
            # 可能存在没有PCB单子的时候
            raise ValidationError(_('No PCB list'))

    # 退回上一步状态
    @api.multi
    def Previous(self):
        self.write({"state": 'sent'})

    # 创建发票按钮 - 继承销售的函数
    @api.multi
    def action_invoice_create(self, grouped=False, final=False):
        res = super(SaleOrder, self).action_invoice_create()
        self.write({'state': 'wait_payment'})
        return res

    # 查看发票 - 简单的返回视图
    @api.multi
    def action_check_invoices(self):
        return super(SaleOrder, self).action_view_invoice()

    # 手动制造中
    @api.multi
    def action_manufacturing(self):
        self.write({'state': 'manufacturing'})

    # 手动确定 制造完成
    @api.multi
    def action_manufacturing_completed(self):
        self.write({'state': 'wait_delivery'})

    # 填写快递单号 - 发货按钮 发送邮件
    @api.multi
    def action_tracking_number(self):
        if self.cpo_courier_number and self.cpo_courier:
            self.ensure_one()
            ir_model_data = self.env['ir.model.data']
            try:
                template_id = ir_model_data.get_object_reference('sale_pcb_rfq', 'ship_email_template')[1]
            except ValueError:
                template_id = False
            try:
                compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
            except ValueError:
                compose_form_id = False
            ctx = {
                'default_model': 'sale.order',
                'default_res_id': self.ids[0],
                'default_use_template': bool(template_id),
                'default_template_id': template_id,
                'default_composition_mode': 'comment',
                'mark_so_as_sent': True,
                'custom_layout': "sale.mail_template_data_notification_email_sale_order",
                'proforma': self.env.context.get('proforma', False)
            }
            return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'mail.compose.message',
                'views': [(compose_form_id, 'form')],
                'view_id': compose_form_id,
                'target': 'new',
                'context': ctx,
            }
            # self.write({'state': 'wait_receipt'})
        else:
            raise ValidationError(_('Please fill in the courier number and choose which courier company'))

    # 管理员权限确认收货
    @api.multi
    def action_confirm_receipt(self):
        self.write({'state': 'complete'})

    # 单向取消打包价bool 暂时不可逆
    @api.multi
    def action_cancel_package(self):
        if self.quotation_line:
            self.quotation_line.update({'package_bool': False})
        elif self.order_line.surface_id and self.order_line.package_type:
            self.order_line.update({'surface_id': False, 'package_type': False, 'smt_assembly_fee': 0})
        self.package_bool, self.proof_bool = False, True

    # 加收费用 - 打开视图的按钮
    def action_open_additional_cost_view(self):
        action = self.env.ref('sale_pcb_rfq.markup_actions').read()[0]
        context = {
            'default_partner_id': self.partner_id.id,
            'default_pricelist_id': self.pricelist_id.id,
            'default_user_id': self._uid,
            'default_partner_invoice_id': self.partner_invoice_id.id,
            'default_partner_shipping_id': self.partner_shipping_id.id,
            'default_markup_order_id': self.id,
            'default_currency_id': self.currency_id.id,
            'default_product_id': self.product_id.id,
            'default_markup_bool': True,
        }
        action.update({
            'display_name': _("%s Additional Cost") % self.name,
            'domain': [('markup_order_id', '=', self.id)],
            'target': 'current',
            'context': context
        })
        if self.search_count([('markup_order_id', '=', self.id)]) <= 0:
            view_id = self.env.ref('sale_pcb_rfq.markup_view_order_form').id
            action.update({
                'views': [[view_id, 'form']],
                'flags': {'mode': 'edit'},
                # 'target': 'new',
            })
        return action

    # 加收费用的按钮
    def action_additional_cost(self):
        line_ids = self.mapped('order_line').ids
        if len(line_ids) <= 0:
            # 系统检测到没有订单行，无法进行下一步
            raise ValidationError(_('The system detected that there is no order line and cannot proceed to the next step'))
        self.markup_order_id.order_markup_bool = True
        return self.write({"state": 'sale'})

    # 加收费用发送的邮件按钮
    def action_additional_email(self):
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('sale_pcb_rfq', 'markup_email_template')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = {
            'default_model': 'sale.order',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'custom_layout': "sale.mail_template_data_notification_email_sale_order",
            'proforma': self.env.context.get('proforma', False)
        }
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    # 发送邮件时 被调用的函数
    def get_number(self):
        x_dict = {}
        for x, y in enumerate(self.order_line, 1):
            x_dict.update({y.id: x})
        return x_dict

    # 发送邮件时 调用的函数 进行制定的路由跳转
    def get_additional_url(self):
        url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        x_str = e64(str(self.id))
        token = random_token(string=True)
        token = token[:4] + x_str + token[4:]
        token = {'token': token}
        url = urljoin(url, '/email/additional?%s' % werkzeug.url_encode(token))
        return url


class RFQSaleOrderLine(models.Model):
    _name = 'sale.order.line'
    _inherit = 'sale.order.line'
    # 目前有2个索引字段
    update_pcb_price = fields.Boolean("Update PCB Price")
    update_stencil_price = fields.Boolean('Update Stencil price')
    pcs_per_set = fields.Integer('PCS Number Per Set')
    pcs_number = fields.Float(string='PCS Number')
    combine_number = fields.Integer('Combine Number')
    # markup_order_line_id = fields.Many2one('sale.order', 'Sale Order', ondelete='cascade')  # 加价时字段
    markup_cost = fields.Float('Additional Cost', digits=(16, 2))

    @api.model
    def create(self, vals):
        res = super(SaleOrderLine, self).create(vals)
        for x_id in res:
            if x_id.product_id.name in ['PCBA', 'PCB', 'Stencil'] and not x_id.order_id.markup_bool:
                if len(x_id.order_id.order_line) > 1:
                    raise ValidationError(_("Create Order Line Length Error, Order Line Length must is one!"))
        return res

    @api.onchange('product_id')
    def _get_product_id(self):
        if self.order_id.markup_bool:
            if not self.product_id:
                return self.update({"product_id": self.order_id.markup_order_id.product_id.id})

    # 前端调用 勿删除
    @api.multi
    def only_pcb_order_line(self):
        return self.filtered(lambda x: x.product_id.type == 'pcb')

    # 前端未调用 暂不删除
    @api.multi
    def only_stencil_order_line(self):
        return self.filtered(lambda x: x.product_id.name == 'Stencil')

    # 实时价格变化
    @api.one
    @api.depends('update_pcb_price', 'product_uom_qty', 'update_stencil_price', 'markup_cost')
    def _compute_amount(self):
        subtract, subtotal = 0, 0
        if self.order_id.markup_bool:
            subtotal = self.markup_cost
        elif self.product_id.name == 'PCBA':
            return super(SaleOrderLine, self)._compute_amount()
        elif self.product_id.name != 'PCBA':
            if self.product_id.type == 'pcb':  # 有PCB单触发
                subtotal = self.order_id.quotation_line.subtotal
                subtract = self.order_id.quotation_line.subtract
            elif self.product_id.name == 'Stencil':  # 有激光钢网触发
                subtotal = self.order_id.stencil_line.cpo_stencil_subtotal
        self.update({
            'price_tax': 0,
            'price_total': subtotal + subtract,
            'price_subtotal': subtotal + subtract,
        })
        return True


class inherit_account_invoice(models.Model):
    _name = 'account.invoice'
    _inherit = 'account.invoice'
    # 有6个索引 4个唯一索引
    sale_order_id = fields.Many2one('sale.order', string='Sale Order', compute='_update_sale_order_id')

    # 自动关联销售单号
    @api.depends('sale_order_id')
    def _update_sale_order_id(self):
        for inv in self:
            order_id = max(inv.invoice_line_ids).sale_line_ids.order_id.id
            inv.update({'sale_order_id': order_id})

    # 继承 进行 添加折扣信息 同时将运费加上
    @api.one
    @api.depends('invoice_line_ids.price_subtotal', 'tax_line_ids.amount', 'currency_id', 'company_id', 'date_invoice', 'type')
    def _compute_amount(self):
        round_curr = self.currency_id.round
        amount_untaxed = sum(line.cpo_product_price_subtotal for line in self.invoice_line_ids)
        cpo_discount_total = sum(line.cpo_discount_total for line in self.invoice_line_ids)
        cpo_shipping_cost = sum(line.cpo_shipping_cost for line in self.invoice_line_ids)
        self.amount_tax = sum(round_curr(line.amount) for line in self.tax_line_ids)
        self.amount_untaxed = amount_untaxed + self.amount_tax + cpo_shipping_cost - cpo_discount_total
        self.amount_total = self.amount_untaxed
        amount_total_company_signed = self.amount_total
        amount_untaxed_signed = self.amount_untaxed
        if self.currency_id and self.company_id and self.currency_id != self.company_id.currency_id:
            currency_id = self.currency_id.with_context(date=self.date_invoice)
            amount_total_company_signed = currency_id.compute(self.amount_total, self.company_id.currency_id)
            amount_untaxed_signed = currency_id.compute(self.amount_untaxed, self.company_id.currency_id)
        sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
        self.amount_total_company_signed = amount_total_company_signed * sign
        self.amount_total_signed = self.amount_total * sign
        self.amount_untaxed_signed = amount_untaxed_signed * sign

    # 创建的同时 将时间和销售员追踪上
    @api.model
    def create(self, vals):
        time = datetime.strptime(fields.Datetime.now(), '%Y-%m-%d %H:%M:%S') + timedelta(hours=8)
        vals.update({'user_id': self.env.user.id, 'date_invoice': time, 'date_due': time})
        return super(inherit_account_invoice, self).create(vals)

    # 查看付款交易
    @api.multi
    def action_transaction(self):
        transaction_ids = self.env['payment.transaction'].search([('reference', 'like', self.number)]).ids
        view_id = self.env.ref('payment.transaction_list').id
        return {
            'name': _('View transaction history'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree, form',
            'res_model': 'payment.transaction',
            'views': [[view_id, 'tree']],
            'target': 'new',
            'domain': [('id', 'in', transaction_ids)],
        }

    @api.multi
    def action_invoice_cancel(self):
        self.sale_order_id.write({'state': 'sale'})
        return super(inherit_account_invoice, self).action_invoice_cancel()


class inherit_account_invoice_line(models.Model):
    _name = 'account.invoice.line'
    _inherit = 'account.invoice.line'

    cpo_shipping_cost = fields.Float('Freight', digits=(16, 2), compute='_get_cpo_freight')
    cpo_discount_total = fields.Float('Discount total', digits=(16, 2), compute='_get_cpo_freight')
    cpo_product_price_subtotal = fields.Float('Product price subtotal', digits=(16, 2), compute='_get_cpo_freight')

    # 自动映射运费 优惠金额 产品小计(非产品优惠后的小计)
    @api.depends('price_subtotal')
    def _get_cpo_freight(self):
        for x_id in self:
            # 现在目前只有每个报价单是一条记录
            cpo_shipping_cost = x_id.sale_line_ids.order_id.shipping_fee
            cpo_product_price_subtotal = x_id.sale_line_ids.price_subtotal
            discount_total = x_id.sale_line_ids.order_id.discount_total
            x_id.update({
                'cpo_shipping_cost': cpo_shipping_cost,
                'cpo_product_price_subtotal': cpo_product_price_subtotal,
                'cpo_discount_total': discount_total,
            })

    @api.one
    @api.depends('price_unit', 'discount', 'invoice_line_tax_ids', 'quantity', 'product_id', 'invoice_id.partner_id',
                 'invoice_id.currency_id', 'invoice_id.company_id', 'invoice_id.date_invoice', 'invoice_id.date')
    def _compute_price(self):
        currency = self.invoice_id and self.invoice_id.currency_id or None
        price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
        taxes = False
        if self.invoice_line_tax_ids:
            taxes = self.invoice_line_tax_ids.compute_all(price, currency, self.quantity, product=self.product_id,partner=self.invoice_id.partner_id)
        # self.price_subtotal = price_subtotal_signed = taxes['total_excluded'] if taxes else self.quantity * price
        self.price_subtotal = price_subtotal_signed = self.cpo_product_price_subtotal + self.cpo_shipping_cost - self.cpo_discount_total
        if self.invoice_id.currency_id and self.invoice_id.company_id and self.invoice_id.currency_id != self.invoice_id.company_id.currency_id:
            price_subtotal_signed = self.invoice_id.currency_id.with_context(date=self.invoice_id._get_currency_rate_date()).compute(price_subtotal_signed, self.invoice_id.company_id.currency_id)
        sign = self.invoice_id.type in ['in_refund', 'out_refund'] and -1 or 1
        self.price_subtotal_signed = price_subtotal_signed * sign


class inherit_account_payment(models.Model):
    _name = 'account.payment'
    _inherit = 'account.payment'

    # 在登记付款的同时进行销售单状态改变
    @api.model
    def create(self, vals):
        res = super(inherit_account_payment, self).create(vals)
        order = res.invoice_ids.sale_order_id
        if order.markup_bool:
            order.write({'state': 'complete'})
        else:
            order.write({'state': 'wait_make'})
        return res
