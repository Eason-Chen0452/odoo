# -*- encoding: utf-8 -*-

from odoo import models, fields, api, _
import odoo.addons.decimal_precision as dp
from odoo.osv import osv
from odoo.exceptions import ValidationError
import time, re

AVAILABLE_LEVEL = [
    ('template', 'Template'),
    ('batch', 'Batch'),
]

AVAILABLE_DELIVERY_UOS = [
    ('pcs', 'PCS'),
    ('set', 'SET'),
    ('pnl', 'PNL'),
]


class sale_quotation_price_item(models.Model):
    _name = "sale.quotation.price.item"
    _description = "Set Price Item"
    _order = "name desc"

    name = fields.Char('Code', size=64, required=True)
    description = fields.Char('Name', size=64, required=True, translate=True)
    note = fields.Text('Note', translate=True)
    active = fields.Boolean('Active', help="If unchecked, it will allow you to hide the price item without removing it.", default=True)

    def name_get(self):
        if isinstance(self.ids, (int, long)):
            ids = [self.ids]
        res = []
        for record in self.browse(self.ids):
            name = record.description
            res.append((record.id, name))
        return res


class sale_quotation(models.Model):
    _name = "sale.quotation"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Sales Quotation"
    _order = 'name desc'
    _track = {
            'state': {
                'sale_pcb_rfq.mt_order_confirmed': lambda self, obj: obj['state'] in ['done'],
                'sale_pcb_rfq.mt_order_sent': lambda self, obj: obj['state'] in ['sent']
            },
        }

    @api.onchange('shop_id')
    def onchange_shop_id(self):
        v = {}
        shop_id = self.shop_id
        if shop_id:
            shop = self.env['sale.order'].browse(shop_id)
            if shop.project_id.id:
                v['project_id'] = shop.project_id.id
        return {'value': v}

    def _amount_line_tax(self, line):
        val = 0.0
        tax = self.env['account.tax'].compute_all(line.tax_id, (line.subtotal / line.product_uom_qty) * (
                1 - (line.discount or 0.0) / 100.0), line.product_uom_qty, line.quotation_id.partner_id)
        # tax = self.env['account.tax'].compute_all(line.tax_id, (line.subtotal / line.product_uom_qty) * (
        #             1 - (line.discount or 0.0) / 100.0), line.product_uom_qty,
        #             line.product_id, line.quotation_id.partner_id)
        total = tax['total']
        total_included = tax['total_included']
        for c in tax['taxes']:
            val += c.get('amount', 0.0)
        return {'total': total,
                'total_included': total_included,
                'taxes': val}

    @api.depends('quotation_line.subtotal')
    def _amount_all(self, *args):
        cur_obj = self.env['res.currency']
        res = {}
        for quotation in self:
            amount_tax = amount_untaxed = amount_total = 0.0
            cur = quotation.currency_id
            for line in quotation.quotation_line:
                amount_untaxed += line.subtotal
            quotation.amount_untaxed = cur.round(amount_untaxed)
            quotation.amount_total = quotation.amount_untaxed

    def _get_order(self):
        result = {}
        for line in self.env['sale.quotation.line'].browse(self.ids):
            result[line.quotation_id.id] = True
        return result.keys()

    def _get_default_shop(self):
        company_id = self.env['res.users'].browse(self).company_id.id
        shop_ids = self.env['sale.order'].search([('company_id', '=', company_id)])
        if not shop_ids:
            raise osv.except_osv(_('Error!'), _('There is no default shop for the current user\'s company!'))
        return shop_ids[0]

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        if not self.partner_id:
            return {'value': {'partner_invoice_id': False, 'partner_shipping_id': False,  'payment_term': False, 'fiscal_position': False}}
        partner_id = self.partner_id.id
        part = self.env['res.partner'].browse(partner_id)
        addr = part.address_get(['delivery', 'invoice'])
        payment_term = part.property_payment_term_id and part.property_payment_term_id.id or False
        fiscal_position = part.property_account_position_id and part.property_account_position_id.id or False
        dedicated_salesman = part.user_id and part.user_id.id or self.env.uid
        val = {
            'partner_invoice_id': addr['invoice'],
            'partner_shipping_id': addr['delivery'],
            'payment_term': payment_term,
            'fiscal_position': fiscal_position,
            'user_id': dedicated_salesman,
            'currency_id': self.env.ref('base.USD').id,
        }
        return {'value': val}
    # 有5个索引字段
    name = fields.Char('Quotation Reference', size=64, required=False, readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, default='/')
    origin = fields.Char('Source Document', size=64, help="Reference of the document that generated this sales order request.")
    client_order_ref = fields.Char('Customer Reference', size=64)
    state = fields.Selection([('draft', 'Draft Quotation'), ('sent', 'Quotation Sent'), ('cancel', 'Cancelled'), ('done', 'Done')], 'Status', readonly=True, track_visibility='onchange',
                               help="Gives the status of the quotation or sales order. \nThe exception status is automatically set when a cancel operation occurs in the processing of a document linked to the sales order. \nThe 'Waiting Schedule' status is set when the invoice is confirmed but waiting for the scheduler to run on the order date.", index=True, default='draft')
    quotation_line = fields.One2many('sale.quotation.line', 'quotation_id', string='Quotation Lines')
    date_order = fields.Date('Date', required=True, readonly=False, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, default=fields.Date.context_today)
    create_date = fields.Datetime('Creation Date', readonly=True, help="Date on which sales order is created.")
    date_confirm = fields.Date('Confirmation Date', readonly=True, help="Date on which sales order is confirmed.")
    user_id = fields.Many2one('res.users', 'Salesperson', states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, index=True, track_visibility='onchange', default=lambda self: self.env.user.company_id.id)
    partner_id = fields.Many2one('res.partner', 'Customer', readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, required=True, change_default=True, index=True, track_visibility='always')
    note = fields.Text('Terms and conditions')
    payment_term = fields.Many2one('account.payment.term', 'Payment Term')
    partner_shipping_id = fields.Many2one('res.partner', 'Delivery Address', readonly=True, required=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, help="Delivery address for current sales order.")
    partner_invoice_id = fields.Many2one('res.partner', 'Invoice Address', readonly=True, required=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, help="Invoice address for current sales order.")
    fiscal_position = fields.Many2one('account.fiscal.position', 'Fiscal Position')
    shop_id = fields.Many2one('sale.order', 'Shop', required=False, readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, ondelete='cascade')
    currency_id = fields.Many2one('res.currency', 'Currency', states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, required=True)
    amount_untaxed = fields.Monetary(compute='_amount_all', digits=dp.get_precision('Account'), string='Untaxed Amount',
        store={
            'sale.quotation': (lambda self, ids, c={}: ids, ['quotation_line'], 10),
            'sale.quotation.line': (_get_order, ['price_unit', 'tax_id', 'discount', 'product_uom_qty'], 10),
        },
        multi='sums', help="The amount without tax.", track_visibility='always')
    amount_tax = fields.Monetary(compute='_amount_all', digits=dp.get_precision('Account'), string='Taxes',
        store={
            'sale.quotation': (lambda self, ids, c={}: ids, ['quotation_line'], 10),
            'sale.quotation.line': (_get_order, ['price_unit', 'tax_id', 'discount', 'product_uom_qty'], 10),
        },
        multi='sums', help="The tax amount.")
    amount_total = fields.Monetary(compute='_amount_all', digits=dp.get_precision('Account'), string='Total',
        store={
            'sale.quotation': (lambda self, ids, c={}: ids, ['quotation_line'], 10),
            'sale.quotation.line': (_get_order, ['price_unit', 'tax_id', 'discount', 'product_uom_qty'], 10),
        },
        multi='sums', help="The total amount.")
    merchandiser_id = fields.Many2one('res.users', 'Merchandiser', states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, track_visibility='onchange', default=lambda self: self.env.user.id)
    spare_qty = fields.Float('Spare Parts Quantity', digits=dp.get_precision('Product Unit of Measure'),required=False, states={'draft': [('readonly', False)]}, default=0)
    spare_bad = fields.Boolean('Spare Parts Not OK', states={'draft': [('readonly', False)]}, default=0)

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Quotations Reference must be unique per Company!'),
    ]

    # 直接在创建PCB报价单的时候 也将报价单明细创建了 点击更新时触发函数
    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].get('sale.quotation') or '/'
        res = super(sale_quotation, self).create(vals)
        return res

    def action_quotation_send(self):
        '''
        This function opens a window to compose an email, with the edi sale template message loaded by default
        '''
        assert len(self.ids) == 1, 'This option should only be used for a single id at a time.'
        for this in self.browse(self.ids):
            if not this.quotation_line:
                raise osv.except_osv(_('Quotation Line Error!'), _('Please enter at least one line of Quotation Line!'))
        self.signal_workflow('quotation_sent')
        ir_model_data = self.env['ir.model.data']
        try:
            if self.env.context.get('partner'):
                template_id = ir_model_data.get_object_reference('sale_pcb_rfq', 'email_template_edi_pcb_lead')[1]
            elif self.env.context.get('lead'):
                template_id = ir_model_data.get_object_reference('sale_pcb_rfq', 'email_template_edi_pcb_quotation')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = ({
            'default_model': 'sale.quotation',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True
        })
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

    def print_quotation(self):
        '''
        This function prints the sales quotation and mark it as sent, so that we can see more easily the next step of the workflow
        '''
        assert len(self.ids) == 1, 'This option should only be used for a single id at a time'
        for this in self.browse(self.ids):
            if not this.quotation_line:
                raise osv.except_osv(_('Quotation Line Error!'), _('Please enter at least one line of Quotation Line!'))
        datas = {'model': 'sale.quotation',
                 'ids': self.ids}
        return {'type': 'ir.actions.report.xml', 'report_name': 'sale.quotation.report.pcb.cn', 'datas': datas, 'nodestroy': True}

    def redirect_quotation_view(self, sale_id):
        model_data = self.env['ir.model.data']
        tree_view = model_data.get_object_reference('sale_pcb_rfq', 'view_quotation_pcb_tree')
        form_view = model_data.get_object_reference('sale_pcb_rfq', 'view_sale_quotation_form')
        value = {'name': _('quotation View'),
                 'view_type': 'form',
                 'view_mode': 'tree,form',
                 'res_model': 'sale.quotation',
                 'res_id': int(sale_id),
                 'views': [(form_view and form_view[1] or False, 'form'), (tree_view and tree_view[1] or False, 'tree'), (False, 'calendar')],
                 'type': 'ir.actions.act_window'}
        return value

    def redirect_sale_view(self, sale_id):
        model_data = self.env['ir.model.data']
        tree_view = model_data.get_object_reference('sale', 'view_order_tree')
        form_view = model_data.get_object_reference('sale', 'view_order_form')
        search_view = model_data.get_object_reference('sale', 'view_sales_order_filter')
        value = {'name': _('quotation 2 sale'),
                 'view_type': 'form',
                 'view_mode': 'tree,form',
                 'res_model': 'sale.order',
                 'res_id': int(sale_id),
                 'views': [(form_view and form_view[1] or False, 'form'), (tree_view and tree_view[1] or False, 'tree'), (False, 'calendar')],
                 'type': 'ir.actions.act_window',
                 'search_view_id': search_view and search_view[1] or False}
        return value

    def button_dummy(self):
        return True

    def action_done(self, *args):
        self.signal_workflow('action_done')
        ids = self.ids if self.ids else args[0].ids
        quotation_id = self.browse(ids)
        currency_id = quotation_id.currency_id.id
        line = quotation_id.quotation_line
        if not line:
            raise osv.except_osv(_('Quotation Line Error!'), _('Please enter at least one line of Quotation Line!'))
        price_list = self.env['product.pricelist'].get_pricelist_pcbone(ids=[], pricelist_type='sale', currency_id=currency_id)
        price_list = price_list.filtered(lambda x: x.selectable is True)
        if not price_list:
            price_list = self.env.ref('product.list0')
            price_list.update({'selectable': True, 'currency_id': self.env.ref('base.USD').id})
        price_list = price_list[0]
        new_id = self.env['sale.order'].create({
            'origin': _('Sale Quotation: %s') % str(quotation_id.id),
            'note': quotation_id.note,
            'currency_id': currency_id,
            'quotation_line': [(4, line.id)],
            'pricelist_id': price_list and price_list.id or False,
            'partner_id': quotation_id.partner_id and quotation_id.partner_id.id or False,
            'merchandiser_id': quotation_id.merchandiser_id and quotation_id.merchandiser_id.id or False,
            'partner_invoice_id': quotation_id.partner_invoice_id and quotation_id.partner_invoice_id.id or False,
            'partner_shipping_id': quotation_id.partner_shipping_id and quotation_id.partner_shipping_id.id or False,
            'product_id': line.layer_number.product_ids and line.layer_number.product_ids.id or False,
            'order_line': [(0, 0, {
                'sequence': line.sequence,
                'price_unit': line.price_unit,
                'pcs_number': line.pcs_number,
                'pcs_per_set': line.pcs_per_set,
                'combine_number': line.combine_number,
                'product_uom_qty': line.product_uom_qty,
                'product_uom': line.product_uom and line.product_uom.id or False,
                'product_id': line.layer_number.product_ids and line.layer_number.product_ids.id or False,
            })],
        })
        self.signal_workflow('order_confirm')
        return self.redirect_sale_view(new_id)

    @api.multi
    def btn_cancel(self):
        self.signal_workflow("cancel")
        self.quotation_line.write({'state': 'cancel'})

    # 一个订单只能一条报价单
    @api.onchange('quotation_line')
    def onchange_quotation_line(self):
        if len(self.quotation_line) > 1:
            raise ValidationError(_('You can only add one more Quotation Lines'))

    # 报价表的取消按钮
    def action_cancel(self):
        self.state = 'cancel'

    @api.model
    def copy(self, default=None):
        if not default:
            default = {}
        default.update({
            'state': 'draft',
            'date_confirm': False,
            'name': self.env['ir.sequence'].get('sale.quotation'),
        })
        return super(sale_quotation, self).copy(default)

    # 这里存在问题 - 暂时解决
    @api.multi
    def copy_quotation(self):
        obj = self.copy()
        view_ref = self.env['ir.model.data'].get_object_reference('sale_pcb_rfq', 'view_sale_quotation_form')
        view_id = view_ref and view_ref[1] or False,
        return {'type': 'ir.actions.act_window',
                'name': _('Sales Quotation'),
                'res_model': 'sale.quotation',
                'res_id': obj.id,
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': view_id,
                'target': 'current',
                'nodestroy': True}

    @api.model
    def get_pcb_quotation_price(self, args, package=False):
        if package:
            return self.get_pcb_package(args)
        else:
            return self.get_pcb_price(args)

    # 检查特殊值
    def CheckSpecialValue(self, value):
        if value['control'] == 'No':
            value.pop('control')
        if value['blind'] == 'No':
            value.pop('blind')
        if value['deep_hole'] == 'No':
            value.pop('deep_hole')
        if value['structure'] == 'No':
            value.pop('structure')
        value.update({
            'drilling': True if value['v_cut'] != 'No' else False,
            'v_cut': True if value['drilling'] != 'No' else False,
            'back': True if value['back'] != 'No' else False,
        })
        return value

    # 前端返回数据报价中心
    @api.model
    def get_pcb_price(self, args):
        args = self.GetNameField(args)  # 整理字段
        args = self.ClientErrorMessage(args)  # 检查错误
        if args.get('warning'):
            return args
        args = self.GetQuotation(args)
        if args.get('warning'):
            return args
        args = self.GetAllCost(args)
        return args

    # 前端 与 后端 通用字段处理 传入 create_order 判断创建订单用的 order 是判断传入订单用的
    def GetNameField(self, args, create_order=False, order=False, unquote=False):
        x_dict, y_dict, line = {}, {}, None
        if type(args) is dict and 'pcb_value' in args.keys():
            x_dict = args.get('pcb_value')
            y_dict = args.get('pcb_special_requirements')
        elif type(args) is not dict:
            line = args
            args = {}
        value = {
            # country = args[0].get('cpo_country') if args[0].get('cpo_country') else 'No',  # 国家
            # 'frame': x_dict.get('cpo_pcb_frame'),  # 钢网
            'hdi': x_dict.get('pcb_hdi') or args.get('pcb_hdi') or {},  # HDI 类型 - 网页是字典
            'rogers': x_dict.get('pcb_rogers') or args.get('pcb_rogers') or {},  # Rogers 类型 - 网页是字典
            'soft': x_dict.get('pcb_soft_hard') or args.get('pcb_soft_hard') or {},  # 软硬结合类型 - 网页是字典
            'text': x_dict.get('pcb_silkscreen_color') or args.get('pcb_silkscreen_color') or line.text_color.id,  # 字符颜色
            'inner': x_dict.get('pcb_inner_copper') or args.get('pcb_inner_copper'),  # 内铜厚
            'outer': x_dict.get('pcb_outer_copper') or args.get('pcb_outer_copper') or line.outer_copper,  # 外铜厚
            'solder': x_dict.get('pcb_solder_mask') or args.get('pcb_solder_mask') or line.silkscreen_color.id,  # 阻焊
            'thick': x_dict.get('pcb_thickness') or args.get('pcb_thickness') or line.thickness,  # 板厚
            'length': x_dict.get('pcb_length') or args.get('pcb_length') or line.cpo_length,  # 长度
            'width': x_dict.get('pcb_breadth') or args.get('pcb_width') or line.cpo_width,  # 宽度
            'layer': x_dict.get('pcb_layer') or args.get('pcb_layer') or line.layer_number.id,  # 层数
            'test': x_dict.get('pcb_test') or args.get('pcb_test'),  # 测试
            'type': x_dict.get('pcb_type') or args.get('pcb_type') or line.base_type.id,  # 板材
            'via': x_dict.get('pcb_vias') or args.get('pcb_vias') or line.via_process.id,  # 过孔处理
            'qty': x_dict.get('cpo_quantity') or args.get('cpo_quantity') or line.product_uom_qty,  # 数量
            'unit': x_dict.get('pcb_qty_unit') or args.get('pcb_qty_unit') or line.product_uom.name,  # 数量单位/PCS SET
            'standard': x_dict.get('quality_standard') or args.get('quality_standard') or line.cpo_standard.id,  # 验收标准
            'surface_dict': x_dict.get('pcb_surfaces') or args.get('pcb_surfaces') or {},  # 表面处理 - 是字典
            'blue_glue': y_dict.get('Peelable_mask') or args.get('Peelable_mask'),  # 蓝胶 - Peelable mask
            'carbon_oil': y_dict.get('Carbon_oil') or args.get('Carbon_oil'),  # 碳油 - Carbon oil
            'half_hole': y_dict.get('Semi_hole') or args.get('Semi_hole'),  # 半孔 - Semi-hole
            'edge': y_dict.get('Edge_plating') or args.get('Edge_plating'),  # 板边电镀 - Edge plating
            'impedance': y_dict.get('Impedance') or args.get('Impedance'),  # 阻抗 - Impedance
            'crimping': y_dict.get('Press_fit') or args.get('Press_fit'),  # 压接孔
            'total_holes': y_dict.get('Total_holes') or args.get('Total_holes') or 0,  # 总孔数
            'core': y_dict.get('Number_core') or args.get('Number_core')or 0,  # 芯板张数
            'pp': y_dict.get('PP_number') or args.get('PP_number')or 0,  # pp张数
            'min_width': y_dict.get('Min_line_width') or args.get('Min_line_width')or 0,  # 最小线宽
            'min_space': y_dict.get('Min_line_space') or args.get('Min_line_space')or 0,  # 最小线距
            'min_hole': y_dict.get('Min_aperture') or args.get('Min_aperture')or 0,  # 最小孔径
            'hole_copper': y_dict.get('Copper_weight_wall') or args.get('Copper_weight_wall')or 0,  # 孔铜厚度
            'test_points': y_dict.get('Total_test_points') or args.get('Total_test_points')or 0,  # 总测试点数
            'hole_distance': y_dict.get('Inner_hole_line') or args.get('Inner_hole_line')or 0,  # 内层孔到线 - 数值
            'v_cut': y_dict.get('The_space_for_drop_V_cut') or args.get('The_space_for_drop_V_cut'),  # 跳刀 三合一了 - 布尔
            'drilling': y_dict.get('Laser_drilling') or args.get('Laser_drilling'),  # 激光钻孔 - 布尔
            'back': y_dict.get('Number_back_drilling') or args.get('Number_back_drilling'),  # 背钻孔数 - 布尔
            'control': y_dict.get('Depth_control_routing') or args.get('Depth_control_routing'),  # 控深锣 - sprocess_ids
            'blind': y_dict.get('Blind_and_buried_hole') or args.get('Blind_and_buried_hole'),  # 埋盲孔钻带数 - sprocess_ids
            'deep_hole': y_dict.get('Countersunk_deep_holes') or args.get('Countersunk_deep_holes'),  # 沉头/控深孔数 - sprocess_ids
            'structure': y_dict.get('Blind_hole_structure') or args.get('Blind_hole_structure'),  # 埋盲孔结构 - sprocess_ids
        }
        if unquote:
            value = self.CheckSpecialValue(value)
        if line:
            value.update({
                'pcs_set': line.pcs_per_set,
                'together': line.cpo_item_number,
                'material_ids': line.smaterial_ids.ids,
                'process_ids': line.sprocess_ids.ids,
                'inner': line.inner_copper,
                'test': 'E-test fixture' if line.tooling else '',
                'total_holes': line.total_holes,  # 总孔数
                'core': line.cpo_core_number,  # 芯板张数
                'pp': line.cpo_pp_number,  # pp张数
                'min_width':  line.min_line_cpo_width,  # 最小线宽
                'min_space': line.min_line_distance,  # 最小线距
                'min_hole': line.min_hole,  # 最小孔径
                'hole_copper': line.cpo_hole_copper,  # 孔铜厚度
                'test_points': line.test_points,  # 总测试点数
                'hole_distance': line.line_to_hole_distance,  # 内层孔到线 - 数值
            })
            if line.urgent:
                value.update({'expedited': (line.delivery_hour + line.increase_delivery_hour) / 24})
            if line.cpo_hdi and line.cpo_hdi != '0':
                value.update({'hdi': True})
            elif line.soft_number > 0:
                value.update({'soft': {'cpo_flex_number': line.soft_number}})
            elif line.rogers_number > 0 and line.core_thick > 0:
                value.update({'rogers': {'rogers_number': line.rogers_number, 'core_thick': line.core_thick}})
        else:
            value.update({
                'pcs_set': x_dict.get('pcb_pcs_size') or args.get('pcb_pcs_size'),  # 一个set 放多少个 pcs - 交货方式
                'together': x_dict.get('pcb_item_size') or args.get('pcb_item_size')  # 拼版款数
            })
        if args.get('expedited_days'):
            value.update({'expedited': args.get('expedited_days')})
        # 创建订单需要的
        if create_order:
            value.update({
                'expedited': args.get('expedited_days'),
                'partner_id': args.get('pcb_partner_id'),
                'test': False if args.get('pcb_test') != 'E-test fixture' else True,
                'request': args.get('text_val'),
            })
        # 表面处理 将金手指 和 表面处理分开
        x_dict = value['surface_dict']
        y_dict = {
            'qty': x_dict.get('gold_finger_qty'),  # 金手指根数
            'length': x_dict.get('gold_finger_length'),  # 长度
            'width': x_dict.get('gold_finger_width'),  # 宽度
            'thick': x_dict.get('gold_finger_thickness'),  # 厚度
        }
        if line:
            y_dict.update({
                'qty': line.cpo_gold_root,  # 金手指根数
                'length': line.cpo_gold_height,  # 长度
                'width': line.cpo_gold_width,  # 宽度
                'thick': line.cpo_gold_thick,  # 厚度
            })
        value.update({'finger_dict': y_dict})
        y_dict = {
            'surface': x_dict.get('surface_value') or x_dict.get('pcb_surface') or line.surface.id,  # 表面处理
            'coating': x_dict.get('coated_area'),  # 涂覆面积
            'nickel': x_dict.get('nickel_thickness'),  # 镍厚
        }
        if line:
            y_dict.update({'coating': line.gold_size, 'nickel': line.cpo_nickel_thickness})
        value.update({'surface_dict': y_dict})
        if type(y_dict.get('surface')) not in [bool, int] and 'Gold finger' in y_dict.get('surface'):
            value['surface_dict'].update({'surface': y_dict['surface'][:y_dict['surface'].index(' +')]})
        # 生成订单后需要的
        if order:
            value['surface_dict'].update({'gold_thick': line.gold_thickness})  # 沉金金厚
        # 当有HDI 将基材类型改变为HDI
        if value.get('hdi'):
            if type(value.get('type')) is not int:
                value.update({'type': value['type'] + '-HDI'})
        # 当有罗杰斯时 改变完成板厚
        elif value.get('rogers'):
            y_dict = value.get('rogers')
            x_dict = 'material' if type(value.get('type')) is int else 'material.english_name'
            x_dict = self.env['cam.rogers.setting'].search([(x_dict, '=', value.get('type')),
                                                            ('core_thick', '>=', y_dict.get('core_thick'))])[0]
            if float(value.get('outer')) == 1:
                value.update({'thick': x_dict.thick_1})
            elif float(value.get('outer')) == 2:
                value.update({'thick': x_dict.thick_2})
        return value

    # 前端 报错提示
    def ClientErrorMessage(self, args):
        error = {}
        if float(args.get('length')) <= 0.0 or float(args.get('width')) <= 0.0 or int(args.get('qty')) <= 0 or float(args.get('thick')) <= 0.0 \
                or float(args.get('hole_distance')) < 0.0 or float(args.get('total_holes')) < 0.0 or float(args.get('core')) < 0.0 \
                or float(args.get('pp')) < 0.0 or float(args.get('min_width')) < 0.0 or float(args.get('min_space')) < 0.0 \
                or float(args.get('min_hole')) < 0.0 or float(args.get('hole_copper')) < 0.0 or float(args.get('test_points')) < 0.0:
            error.update({'Data': 'The relevant required data is ≤ "0",please recheck the data and quote .'})
        elif float(args.get('length')) >= 600.00:
            error.update({'length_dict': 'Length ≥600mm is unable to quote automatically , if you are interested, please turn to personal support.'})
        elif float(args.get('width')) >= 600.00:
            error.update({'width_dict': "Width ≥600mm is unable to quote automatically , if you are interested, please turn to personal support."})
        elif args.get('drilling') != 'No':
            error.update({'laser': "Sorry! The PCB parameters you entered are not included in the automatic quote system. The following parameters you entered exceed the system settings:</br>Laser drilling is unable to quote automatically </br> You can choose to modify according to the tips above, or let our engineers assist you. If you need the assistance of our engineers, please click the button below to switch to manual services."})
        elif args.get('control') != 'No':
            error.update({'depth': "Sorry! The PCB parameters you entered are not included in the automatic quote system. The following parameters you entered exceed the system settings:</br>Depth milling unable to quote automatically </br> You can choose to modify according to the tips above, or let our engineers assist you. If you need the assistance of our engineers, please click the button below to switch to manual services."})
        elif args.get('v_cut') != 'No':
            error.update({'CVT': "Sorry! The PCB parameters you entered are not included in the automatic quote system. The following parameters you entered exceed the system settings:</br>Jumping v-cut is unable to quote automatically </br>You can choose to modify according to the tips above, or let our engineers assist you. If you need the assistance of our engineers, please click the button below to switch to manual services."})
        elif args.get('back') != 'No':
            error.update({'back': "Sorry! The PCB parameters you entered are not included in the automatic quote system. The following parameters you entered exceed the system settings:</br>Back drilling is unable to quote automatically</br>You can choose to modify according to the tips above, or let our engineers assist you. If you need the assistance of our engineers, please click the button below to switch to manual services."})
        elif args.get('deep_hole') != 'No':
            error.update({'deep': "Sorry! The PCB parameters you entered are not included in the automatic quote system. The following parameters you entered exceed the system settings:</br>Countersunk/depth control hole is unable to quote automatically</br>You can choose to modify according to the tips above, or let our engineers assist you. If you need the assistance of our engineers, please click the button below to switch to manual services."})
        elif args.get('structure') != 'No':
            error.update({'structure': "Sorry! The PCB parameters you entered are not included in the automatic quote system. The following parameters you entered exceed the system settings:</br>Blind&Buried via is unable to quote automatically</br>You can choose to modify according to the tips above, or let our engineers assist you. If you need the assistance of our engineers, please click the button below to switch to manual services."})
        elif args.get('blind') != 'No':
            error.update({'blind': "Sorry! The PCB parameters you entered are not included in the automatic quote system. The following parameters you entered exceed the system settings:</br>Blind&Buried via is unable to quote automatically</br>You can choose to modify according to the tips above, or let our engineers assist you. If you need the assistance of our engineers, please click the button below to switch to manual services."})
        elif args.get('standard') == '3':
            error.update({'Quality Standard': "Sorry! The PCB parameters you entered are not included in the automatic quote system. The following parameters you entered exceed the system settings:</br>IPC Class III is unable to quote automatically</br>You can choose to modify according to the tips above, or let our engineers assist you. If you need the assistance of our engineers, please click the button below to switch to manual services."})
        # 超厚铜
        elif args.get('outer') >= '6':
            if args.get('layer') not in ['1', '2']:
                error.update({'layer': 'Heavy copper is only available to quote automatically for single or double side PCB.'})
            else:
                number = int(args.get('layer')) * float(args.get('outer')) * 0.07
                if number > float(args.get('thick')):
                    error.update({'thick': 'The min board thickness is %s mm for Heavy copper PCB.' % float(number)})
        # Rogers 目前支持单双面
        elif args.get('layer') not in ['1', '2'] and args.get('rogers'):
            error.update({'layer': 'Rogers material is only available to quote automatically for single or double side PCB.'})
        # # 软硬结合
        # elif args.get('soft'):
        #     if args.get('soft').get('cpo_flex_open') != 'No':
        #         error.update({'soft': 'Solder mask opening for flex part is unable to quote automatically , if you are interested, please turn to personal support.'})
        #     elif args.get('soft').get('cpo_inner_outer') != 'Inner layer':
        #         error.update({'soft': 'Flex part in outer layer is unable to quote automatically , if you are interested, please turn to personal support.'})
        elif args.get('hdi'):
            if args.get('hdi').get('number_of_step') != '1':
                error.update({'Number of step': "Sorry! The PCB parameters you entered are not included in the automatic quote system. The following parameters you entered exceed the system settings:</br>HDI 2 step is unable to quote automatically</br>You can choose to modify according to the tips above, or let our engineers assist you. If you need the assistance of our engineers, please click the button below to switch to manual services."})
        if error:
            args = {'warning': error}
        else:
            args.update({'deep_hole': 0, 'structure': 0, 'blind': 0})
        return args

    # 前后端通用 报价的控制中心
    def GetQuotation(self, args):
        price_id = self.env['pcb.quotation.pricelist'].search([('general_price', '=', True), ('pricelist_type', '=', 'sales')]).version_id
        discount_id = self.env['specific.product.offers'].search([('use_bool', '=', True)])
        if not price_id:
            return {'warning': {'data': 'System is shutting down,please wait for a second'}}
        # 层数 - 可以确定芯板费, pp费, 孔密度, 拼版费
        layer_dict = {
            'discount_id': discount_id,
            'price_id': price_id,
            'layer': args.get('layer'),  # 层数
            'length': args.get('length'),
            'width': args.get('width'),
            'pcs_set': args.get('pcs_set'),  # 交货方式
            'together': args.get('together'),  # 拼版款数
            'qty': args.get('qty'),
            'unit': args.get('unit'),  # 单位 PCS/SET
            'hole_distance': args.get('hole_distance'),  # 内层孔到线
            'total_holes': args.get('total_holes'),  # 总孔数
            'core': args.get('core'),  # 芯板张数
            'pp': args.get('pp'),  # pp张数
            'min_hole': args.get('min_hole'),  # 最小孔
        }
        layer_dict = self.GetLayerCost(layer_dict)
        if layer_dict.get('warning'):
            return {'warning': {'layer_dict': layer_dict.get('warning')}}
        # 板材 - 可以确定工程费,基准价交期等
        base_dict = {
            'discount_id': layer_dict.get('discount_id'),
            'price_id': layer_dict.get('layer_price'),
            'meter': layer_dict.get('meter'),
            'type': args.get('type'),
            'rogers': args.get('rogers')
        }
        base_dict = self.GetBaseCost(base_dict)
        if base_dict.get('warning'):
            return {'warning': {'base_dict': base_dict.get('warning')}}
        # 工程 测试 菲林
        eng_test_film_dict = {
            'size_id': base_dict.get('size_id'),
            'cm': layer_dict.get('cm'),
            'meter': layer_dict.get('meter'),
            'test': args.get('test'),
        }
        if args.get('hdi'):
            eng_test_film_dict.update({'type': args.get('type')})
        eng_test_film_dict = self.GetEngTestFilmCost(eng_test_film_dict)
        if eng_test_film_dict.get('warning'):
            return {'warning': {'eng_test_film_dict': eng_test_film_dict.get('warning')}}
        # 板厚
        thick_dict = {
            'discount_id': base_dict.get('discount_id'),
            'price_id': layer_dict.get('layer_price'),
            'meter': layer_dict.get('meter'),
            'thick': args.get('thick'),
        }
        thick_dict = self.GetThickCost(thick_dict)
        if thick_dict.get('warning'):
            return {'warning': {'thick_dict': thick_dict.get('warning')}}
        # 铜厚 内外
        copper_dict = {
            'discount_id': thick_dict.get('discount_id'),
            'price_id': layer_dict.get('layer_price'),
            'meter': layer_dict.get('meter'),
            'inner': args.get('inner'),
            'outer': args.get('outer'),
            'type': args.get('type'),
        }
        copper_dict = self.GetCopperCost(copper_dict)
        if copper_dict.get('warning'):
            return {'warning': {'copper_dict': copper_dict.get('warning')}}
        # 字符
        text_dict = {
            'discount_id': copper_dict.get('discount_id'),
            'price_id': price_id,
            'text': args.get('text'),
        }
        text_dict = self.GetTextCost(text_dict)
        # 阻焊
        solder_dict = {
            'discount_id': text_dict.get('discount_id'),
            'price_id': price_id,
            'meter': layer_dict.get('meter'),
            'solder': args.get('solder'),
        }
        solder_dict = self.GetSolderCost(solder_dict)
        if solder_dict.get('warning'):
            return {'warning': {'solder_dict': solder_dict.get('warning')}}
        # 表面处理
        surface_dict = {
            'discount_id': solder_dict.get('discount_id'),
            'price_id': price_id,
            'surface': args.get('surface_dict'),
            'meter': layer_dict.get('meter'),
        }
        surface_dict = self.GetSurfaceCost(surface_dict)
        if surface_dict.get('warning'):
            return {'warning': {'surface_dict': surface_dict.get('warning')}}
        # 特殊材料
        material_dict = {
            'discount_id': surface_dict.get('discount_id'),
            'price_id': price_id,
            'meter': layer_dict.get('meter'),
            'blue_glue': args.get('blue_glue'),
            'carbon_oil': args.get('carbon_oil'),
        }
        if args.get('material_ids'):
            material_dict.update({'material_ids': args.get('material_ids')})
        material_dict = self.GetMaterialCost(material_dict)
        process_dict = {
            'discount_id': material_dict.get('discount_id'),
            'price_id': price_id,
            'meter': layer_dict.get('meter'),
            'via': args.get('via'),  # 过孔处理
            'half_hole': args.get('half_hole'),  # 半孔
            'edge': args.get('edge'),  # 板边电镀
            'impedance': args.get('impedance'),  # 阻抗
            'crimping': args.get('crimping'),  # 压接孔
            'base_fee': base_dict.get('base_fee'),  # 基准价 价格
        }
        if args.get('process_ids'):
            process_dict.update({'process_ids': args.get('process_ids')})
        process_dict = self.GetProcessCost(process_dict)
        test_dict = {
            'price_id': price_id,
            'test_fee': eng_test_film_dict.get('test_fee'),
            'eng_fee': eng_test_film_dict.get('eng_fee'),
            'test_points': args.get('test_points'),
        }
        test_dict = self.GetTestCost(test_dict)
        # 金手指
        gold_finger_dict = {
            'price_id': price_id,
            'finger_dict': args.get('finger_dict'),
            'qty': args.get('qty'),
            'meter': layer_dict.get('meter'),
            'length': args.get('length'),
            'width': args.get('width'),
            'layer': args.get('layer'),
            'pcs_set': args.get('pcs_set'),  # 交货方式
        }
        gold_finger_dict = self.GetGoldFingerCost(gold_finger_dict)
        if gold_finger_dict.get('warning'):
            return {'warning': {'gold_finger_dict': gold_finger_dict.get('warning')}}
        if gold_finger_dict.get('process_fee') or gold_finger_dict.get('finger_fee') or gold_finger_dict.get('add_time'):
            process_dict.update({'discount_id': None})
        soft_dict = {
            'price_id': price_id,
            'layer': args.get('layer'),
            'meter': layer_dict.get('meter'),
            'soft': args.get('soft'),
        }
        if args.get('soft'):
            soft_dict = self.GetSoftCost(soft_dict)
            if soft_dict.get('warning'):
                return {'warning': {'soft_dict': soft_dict.get('warning')}}
        line_hole_copper_dict = {
            'price_id': price_id,
            'width': args.get('min_width'),
            'space': args.get('min_space'),
            'hole': args.get('min_hole'),
            'copper': args.get('hole_copper'),  # 孔铜
            'meter': layer_dict.get('meter'),
            'base_fee': base_dict.get('base_fee'),  # 基准价
            'outer': args.get('outer'),
            'thick': args.get('thick'),
            'standard': args.get('standard'),  # 验收标准
        }
        line_hole_copper_dict = self.GetLineHoleCopperCost(line_hole_copper_dict)
        if line_hole_copper_dict.get('warning'):
            return {'warning': {'line_hole_copper_dict': line_hole_copper_dict.get('warning')}}
        if line_hole_copper_dict.get('other_fee') or line_hole_copper_dict.get('process_fee'):
            process_dict.update({'discount_id': None})
        # 钢网
        # frame_pcb = self.cpo_frame_fee_one({
        #     'universal_id': universal_id,
        #     'cpo_pcb_frame': pcb_frame
        # })
        all_dict = {
            'layer': layer_dict,
            'base': base_dict,
            'eng_test_film': eng_test_film_dict,
            'thick': thick_dict,
            'copper': copper_dict,
            'text': text_dict,
            'solder': solder_dict,
            'surface': surface_dict,
            'material': material_dict,
            'process': process_dict,
            'test': test_dict,
            'gold_finger': gold_finger_dict,
            'line_hole': line_hole_copper_dict,
            'price_id': price_id,
            'discount_id': process_dict.get('discount_id')
        }
        if args.get('soft'):
            all_dict.update({'soft': soft_dict, 'discount_id': None})
        if args.get('hdi'):
            all_dict.update({'hdi': True})
        if args.get('expedited'):
            all_dict.update({'expedited': args.get('expedited')})
        delivery = self.GetDelivery(all_dict)
        all_dict.update({'expedited': delivery})
        return all_dict

    # 时间整理
    def GetDelivery(self, args):
        thick, process = args.get('thick').get('add_time'), args.get('process').get('add_time')
        material, surface = args.get('material').get('add_time'), args.get('surface').get('add_time')
        finger, solder = args.get('gold_finger').get('add_time'), args.get('solder').get('add_time')
        copper = args.get('copper').get('add_time')
        # 罗杰斯的情况 是增加时间
        x_time = 0 if not args.get('base').get('add_time') else args.get('base').get('add_time')
        delivery = thick + process + material + finger + solder + copper + x_time
        args = {
            'meter': args.get('layer').get('meter'),
            'size_id': args.get('base').get('size_id')[0],
            'add_time': delivery,
            'expedited': args.get('expedited'),  # 加急
            'hdi': args.get('hdi'),
            'soft': args.get('soft'),
        }
        args = self.GetTime(args)
        args.update({'add_time': delivery})
        return args

    # 整理明细价格
    def GetAllCost(self, args):
        base, copper, eng, expedited = args.get('base'), args.get('copper'), args.get('eng_test_film'), args.get('expedited')
        gold, layer, hole, material = args.get('gold_finger'), args.get('layer'), args.get('line_hole'), args.get('material')
        process, solder, surface, test = args.get('process'), args.get('solder'), args.get('surface'), args.get('test')
        text, thick, soft, discount = args.get('text'), args.get('thick'), args.get('soft'), 1
        quick = max(expedited['quick'], 1)  # 加急费用倍数 百分比
        ipc = max(hole['ipc_fee'], 1)  # 验收标准 不能直接乘于 基准价 - 百分比
        line_fee = max(hole['line_fee'], 1)  # 细线百分比
        film_cost = max(eng['film_fee'] * quick, 0)  # 所有菲林费之和
        eng_cost = max((eng['eng_fee'] + layer['combine_fee']) * quick * ipc, 0)  # 工程费
        # 当是罗杰斯的时候
        if base.get('eng_fee'):
            eng_cost = max((base['eng_fee'] + layer['combine_fee']) * quick * ipc, 0)
        # 当是超厚铜箔的时候
        elif copper.get('eng_fee'):
            eng_cost = max((copper['eng_fee'] + layer['combine_fee']) * quick * ipc, 0)
        test_cost = max(test['test_fee'] * quick, 0)  # 所有测试费之和
        process_cost = max((hole['process_fee'] + process['process_fee'] + material['process_fee'] + gold['process_fee'] +
                            surface['process_fee'] + layer['process_fee']) * quick, 0)  # 工艺费用
        process_fee = max((layer['density_fee'] + process['special_process_fee']) * ipc * quick * line_fee, 0)  # 特殊工艺费用 和 孔密度费用
        base_cost = max(base['base_fee'] * ipc * quick * line_fee, 0)  # 基准价
        thick_cost = max(thick['thick_fee'] * ipc * quick * line_fee, 0)  # 板厚加价
        copper_cost = max(copper['copper_fee'] * ipc * quick * line_fee, 0)  # 铜厚费用
        text_cost = max(text['text_fee'] * ipc * quick * line_fee, 0)  # 文字颜色费用
        solder_cost = max(solder['solder_fee'] * ipc * quick * line_fee, 0)  # 阻焊颜色费用
        surface_cost = max(surface['surface_fee'] * ipc * quick * line_fee, 0)  # 表面工艺费用
        gold_cost = max(gold['finger_fee'] * ipc * quick * line_fee, 0)  # 金手指费用
        core_pp_cost = max((layer['pp_fee'] + layer['core_fee']) * ipc * quick * line_fee, 0)  # 芯板费和pp之和
        other_cost = max(hole['other_fee'] * ipc * quick * line_fee, 0)  # 其他的费用
        material_cost = max(material['material_fee'] * ipc * quick * line_fee, 0)  # 特殊材料费用
        # 如果有软硬结合 工程费就不加收普通板子的工程费
        if soft:
            eng_cost = soft['eng_fee'] * quick * ipc
            base_cost = soft['board_fee'] * ipc * quick * line_fee
        if args['layer']['meter'] < 0.2 and (soft or args.get('hdi')):
            eng_cost += surface_cost
            # base_cost, thick_cost, copper_cost, text_cost, solder_cost, surface_cost, gold_cost = 0, 0, 0, 0, 0, 0, 0
            thick_cost, copper_cost, text_cost, solder_cost, surface_cost, gold_cost = 0, 0, 0, 0, 0, 0
        x_fee = (base_cost + thick_cost + copper_cost + text_cost + solder_cost + process_fee +
                 surface_cost + material_cost + core_pp_cost + other_cost)
        part_fee = x_fee * layer['meter'] + gold_cost
        all_cost = film_cost + eng_cost + test_cost + part_fee + process_cost
        if args.get('discount_id'):
            discount = max(args.get('discount_id')).discount * 0.01
            if discount <= 0:
                discount = 1
        value = {
            'value': {
                'PCB Area': round(layer['meter'], 4),  # 要的
                'Delivery Period': str(expedited['delivery']) + ' Day',  # 交期
                'pcb_expedited_days': None,  # 客户选择的加急时间
                'cpo_quick_time_list': expedited['quick_list'],  # 可选着的加急时间 是列表
                'Film Cost': round(film_cost * discount, 2),  # Film fee  菲林费用
                'Total Cost': round(all_cost * discount, 2),  # 所有费用 Total - 这个才是所有之和
                'Set Up Cost': round(eng_cost * discount, 2),  # 工程费 Set up cost
                'E-test Fixture Cost': round(test_cost * discount, 2),  # 测试费用 E-test fixture
                'Board Price Cost': round(part_fee * discount, 2),  # 版费 Board price
                'Process Cost': round(process_cost * discount, 2),  # 工艺费
                'Special Process Cost': round(process_fee, 2),  # 特殊工艺的价格
                'Cost By': round(base_cost * discount, 2),  # 基准价
                'Thickness Cost': round(thick_cost, 2),  # 板厚
                'Copper Cost': round(copper_cost, 2),  # 铜厚
                'Text Color Cost': round(text_cost, 2),  # 文字颜色
                'Solder Mask Color Cost': round(solder_cost, 2),  # 阻焊颜色
                'Surface Cost': round(surface_cost, 2),  # 表面工艺
                'Core&PP Cost': round(core_pp_cost, 2),  # Core and PP fee 芯板和PP费用
                'Other Cost': round(other_cost, 2),  # 其他费用
                'Gold Finger Cost': round(gold_cost, 2),  # 金手指
                'Special Material Cost': round(material_cost, 2),  # Special material fee 特殊材料费用
                'pcb_special': {
                    'Total_holes': round(layer['total_holes'], 0),  # 总孔数 - 这里存在 尺寸改变了 总数也会改变
                    'Inner_hole_line': layer['hole_distance'],  # 内层孔到线
                    'Number_core': layer['core'],  # 芯板张数
                    'PP_number': layer['pp'],  # pp张数
                    'Blind_hole_structure': 0,  # 埋盲孔结构
                    'Blind_and_buried_hole': 0,  # 埋盲孔钻带数
                    'Min_line_width': hole['width'],  # 线宽
                    'Min_line_space': hole['space'],  # 线距
                    'Min_aperture': hole['hole'],  # 孔
                    'Copper_weight_wall': hole['hole_copper'],  # 孔铜
                    'Countersunk_deep_holes': 0,  # 沉头/...
                    'Total_test_points': test['test_points']  # 测试总点数
                }
            },
            'Shipping Cost': 0,  # 运费费用
        }
        if soft:
            value.update({'soft': True, 'Total Layer': soft.get('total_layers')})
        if args.get('discount_id'):
            value.get('value').update({
                'Original Price': all_cost
            })
        return value

    # 层数
    def GetLayerCost(self, args):
        # offer 变量名是判断 是不是 特殊指定的规格可以进行折扣的
        price_id, layer, length, width = args.get('price_id'), args.get('layer'), args.get('length'), args.get('width')
        qty, combine_fee, density_fee, core_fee, pp_fee, process_fee, discount_id = args.get('qty'), 0, 0, 0, 0, 0, args.get('discount_id')
        # 该层数的相关数据
        price_id = price_id.items_id.search([('price_version_id', '=',  price_id.id),
                                             ('layer_number.layer_number', '=', layer)])
        if not price_id:
            return {'warning': "Sorry! The PCB parameters you entered are not included in the automatic quote system. The following parameters you entered exceed the system settings:</br> L≥20L is unable to quote automatically </br>You can choose to modify according to the tips above, or let our engineers assist you. If you need the assistance of our engineers, please click the button below to switch to manual services."}
        if discount_id:  # 先 尺寸 数量
            discount_id = discount_id.filtered(lambda x: x.length_1 <= float(length) <= x.length_2)
            discount_id = discount_id.filtered(lambda x: x.width_1 <= float(width) <= x.width_2)
            discount_id = discount_id.filtered(lambda x: x.qty_1 <= float(qty) <= x.qty_2)
            discount_id = discount_id.filtered(lambda x: price_id.layer_number.id in x.layer_ids.ids)
        meter = (float(length) * float(width) * 0.01) * int(qty) / 10000.0
        centimeter = float(length) * float(width) * 0.01
        if args.get('unit') != 'PCS' and args.get('pcs_set'):
            centimeter = (float(length) * float(width) * 0.01) / float(args.get('pcs_set'))
        # 拼板费用
        if args.get('together'):
            discount_id = discount_id.filtered(lambda x: x.combine_1 <= int(args.get('together')) <= x.combine_2)
            together = max((int(args.get('together')) - price_id.combine_number), 0)
            combine_fee = max(round(together / price_id.combine_fee_number, 0) * price_id.combine_fee, 0)
        # 内层孔到线 - 暂时不用计算价格
        if float(args.get('hole_distance')) in [0, 5.25, 5.5, 6, 6.5, 7, 7.5, 8.0, 8.5, 9, 9.5, 10]:
            args.update({'hole_distance': price_id.inner_hole_line})
        else:
            return {'warning': "Sorry! The PCB parameters you entered are not included in the automatic quote system. The following parameters you entered exceed the system settings:</br>The spacing from inner layer to trace is unable to quote automatically </br>You can choose to modify according to the tips above, or let our engineers assist you. If you need the assistance of our engineers, please click the button below to switch to manual services."}
        # 总孔数
        if args.get('total_holes'):
            total_hole = price_id.pore_density / 100.0 * float(length) * float(width)
            if args.get('total_holes') == '0':
                args.update({'total_holes': total_hole})
            # 最小孔不是6mil的情况
            elif total_hole != float(args.get('total_holes')) and float(args.get('min_hole')) != 6.0:
                density = float(args.get('total_holes')) / float(length) / float(width) * 100.0
                density_fee = max(density - price_id.pore_density, 0) * price_id.pore_density_fee
            # 最小孔是6mil的情况
            elif float(args.get('min_hole')) == 6.0:
                density = float(args.get('total_holes')) / float(length) / float(width) * 100.0
                density_fee = density * price_id.pore_density_fee
        # 芯板
        if args.get('core') and args.get('pp'):
            core = max((float(layer) - 2) / 2, 1)
            pp = core + 1
            if args.get('core') in ['', '0']:
                args.update({'core': core})
            elif float(args.get('core')) != core:
                core_fee = max(float(args.get('core')) - core, 0) * price_id.core_fee
            if args.get('pp') in ['', '0']:
                args.update({'pp': pp})
            elif float(args.get('pp')) != pp:
                pp_fee = max(float(args.get('pp')) - pp, 0) * price_id.pp_fee
                if float(args.get('core')) + 1 >= float(args.get('pp')):
                    pp_fee = 0
        # 最小尺寸要收工艺费
        if centimeter == 9 and not args.get('pcs_set'):
            process_fee = price_id.moq_pcs_fee * float(qty)
        elif centimeter == 9 and args.get('pcs_set'):
            process_fee = price_id.moq_pcs_fee * float(qty) * float(args.get('pcs_set'))
        elif centimeter < 9:
            return {'warning': "Sorry! The PCB parameters you entered are not included in the automatic quote system. The following parameters you entered exceed the system settings:</br> Size <9cm² is unable to quote automatically </br> You can choose to modify according to the tips above, or let our engineers assist you. If you need the assistance of our engineers, please click the button below to switch to manual services."}
        args = {
            'meter': meter,  # 平米数
            'cm': centimeter,  # 厘米数
            'combine_fee': combine_fee,  # 拼板费用
            'core_fee': core_fee,  # 芯板费用
            'pp_fee': pp_fee,  # pp费用
            'density_fee': density_fee,  # 孔密度费用
            'process_fee': process_fee,  # 工艺费
            'layer': layer,  # 层数
            'pcs_set': 1 if not args.get('pcs_set') else float(args.get('pcs_set')),  # 交货方式
            'hole_distance': args.get('hole_distance'),  # 内层孔到线
            'together': 1 if not args.get('together') else args.get('together'),  # 拼板数
            'pp': args.get('pp'),  # pp张数
            'core': args.get('core'),  # 芯板张数
            'total_holes': float(args.get('total_holes')),  # 总孔数
            'layer_price': price_id,  # 层数的价格表
            'discount_id': discount_id
        }
        return args

    # 基材 - 当中设计HDI 和 Rogers
    def GetBaseCost(self, args):
        price_id, meter, base_id = args.get('price_id'), args.get('meter'), args.get('type')
        x_value = 'base_type' if type(base_id) is int else 'base_type.english_name'
        size_id = price_id.item_size_ids.search([('layer_item_id', '=', price_id.id), ('max_size', '>', meter)])
        if not size_id:
            return {'warning': "Sorry! The PCB parameters you entered are not included in the automatic quote system. The following parameters you entered exceed the system settings:</br>  Exceeding the automatic quote area </br> You can choose to modify according to the tips above, or let our engineers assist you. If you need the assistance of our engineers, please click the button below to switch to manual services."}
        if x_value == 'base_type.english_name' and 'HDI' not in base_id:
            size_id = size_id.filtered(lambda s: s.max_size > 0.2)
        elif x_value == 'base_type' and 'HDI' not in self.env['cam.base.type'].browse(base_id).english_name:
            size_id = size_id.filtered(lambda s: s.max_size > 0.2)
        price_id = size_id[0].type_item_ids.search([(x_value, '=', base_id), ('size_item_id', '=', size_id[0].id)])
        if not price_id and not args.get('rogers'):
            return {'warning': "Sorry! The PCB parameters you entered are not included in the automatic quote system. The following parameters you entered exceed the system settings:</br>  The Base material is unable to quote be automatically </br> You can choose to modify according to the tips above, or let our engineers assist you. If you need the assistance of our engineers, please click the button below to switch to manual services."}
        base_fee = price_id.cpo_benchmark_fee
        value = {
            'base_fee': base_fee,  # 基准价
            'size_id': size_id,  # 层数中平米数的id
        }
        if args.get('discount_id'):
            x_obj = args.get('discount_id')
            x_obj = x_obj.filtered(lambda x: price_id.base_type.id in x.base_ids.ids)
            if x_obj:
                value.update({'discount_id': x_obj})
        if args.get('rogers'):
            core_thick, number = args.get('rogers').get('core_thick'), args.get('rogers').get('rogers_number')
            rogers_id = args.get('price_id').item_rogers_ids.search([('layer_item_id', '=', args.get('price_id').id),
                                                                     (x_value, '=', base_id),
                                                                     ('core_thick', '>=', core_thick)])
            if not rogers_id:
                return {'warning': "Sorry! The PCB parameters you entered are not included in the automatic quote system. The following parameters you entered exceed the system settings:</br>  The selected Rogers is unable to quote be automatically</br> You can choose to modify according to the tips above, or let our engineers assist you. If you need the assistance of our engineers, please click the button below to switch to manual services."}
            elif meter >= 3:
                return {'warning': "Sorry! The PCB parameters you entered are not included in the automatic quote system. The following parameters you entered exceed the system settings:</br>  Rogers material ≥3㎡ is unable to quote automatically</br> You can choose to modify according to the tips above, or let our engineers assist you. If you need the assistance of our engineers, please click the button below to switch to manual services."}
            if not base_fee:
                value.update({'base_fee': rogers_id[0].price, 'eng_fee': rogers_id[0].project_fee, 'add_time': rogers_id[0].delivery, 'discount_id': None})
        return value

    # 工程 测试 菲林费用
    def GetEngTestFilmCost(self, args):
        cm, meter, size_id, test = args.get('cm'), args.get('meter'), args.get('size_id'), args.get('test')
        if args.get('type'):
            x_value = 'base_type' if type(args.get('type')) is int else 'base_type.english_name'
            size_id = size_id[0].type_item_ids.search([(x_value, '=', args.get('type')),
                                                       ('size_item_id', '=', size_id[0].id)])
        if not size_id:
            return {'warning': "Sorry! The PCB parameters you entered are not included in the automatic quote system. The following parameters you entered exceed the system settings:</br>  The Base material is unable to quote be automatically</br> You can choose to modify according to the tips above, or let our engineers assist you. If you need the assistance of our engineers, please click the button below to switch to manual services."}
        size_id = size_id[0]
        size_range = size_id[0].engineering_fee_exceeding_type
        value = {'eng_fee': 0, 'test_fee': 0, 'film_fee': 0}
        # 如果是在3平米内的 不用测试费用 只要看看有没有菲林费用
        if meter < 3:
            # 当厘米数小于等于规格厘米是 只收工程费
            if test == 'E-test fixture':
                value.update({'eng_fee': size_id.etest_fee / 2, 'test_fee': size_id.etest_fee / 2})
            else:
                value.update({'eng_fee': size_id.engineering_fee})
            # 大于规格厘米数的情况
            if cm >= size_range:
                value.update(({'film_fee': (cm - size_range) * size_id.engineering_fee_exceeding}))
        # 测试费用 看菲林费用
        elif meter >= 3:
            value.update({'eng_fee': size_id.etest_fee / 2, 'test_fee': size_id.etest_fee / 2})
            if cm >= size_range:
                value.update(({'film_fee': (cm - size_range) * size_id.engineering_fee_exceeding}))
        # 菲林费的上限
        film_upper = size_id.cpo_film_upper_limit_fee
        value['film_fee'] = value['film_fee'] if value['film_fee'] <= film_upper else film_upper
        return value

    # 板厚
    def GetThickCost(self, args):
        price_id, meter, thickness = args.get('price_id'), args.get('meter'), args.get('thick')
        thick = price_id.item_thickness_ids.search([('layer_item_id', '=', price_id.id),
                                                    ('min_thickness', '<', thickness),
                                                    ('max_thickness', '>=', thickness)])
        if not thick:
            layer = price_id.layer_number.layer_number
            thick = price_id.item_thickness_ids.search([('layer_item_id', '=', price_id.id)])[0].min_thickness + 0.0001
            return {'warning': "Sorry! The PCB parameters you entered are not included in the automatic quote system. The following parameters you entered exceed the system settings:</br> The minimum thickness of the %s line is %s mm, but the thickness you enter is %s mm </br> You can choose to modify according to the tips above, or let our engineers assist you. If you need the assistance of our engineers, please click the button below to switch to manual services." % (layer, thick, thickness)}
        thick_fee = thick.add_fee
        add_time = thick.delivery_time_1 if meter < 3 else thick.delivery_time_2
        value = {
            'thick_fee': thick_fee,
            'add_time': add_time
        }
        if args.get('discount_id'):
            x_obj = args.get('discount_id')
            x_obj = x_obj.filtered(lambda x: x.thick_1 <= float(thickness) <= x.thick_2)
            if x_obj:
                value.update({'discount_id': x_obj})
        return value

    # 铜厚 内外之和
    def GetCopperCost(self, args):
        price_id, meter, inner, outer, number = args.get('price_id'), args.get('meter'), args.get('inner'), args.get('outer'), 1
        outer = price_id.item_outer_copper_ids.search([('layer_item_id', '=', price_id.id),
                                                       ('min_outer_copper', '<=', outer),
                                                       ('max_outer_copper', '>', outer)])
        if args.get('type') == self.env.ref('cam.base_type_fr4').id or '150' in str(args.get('type')):
            number = 1.1
        elif args.get('type') == self.env.ref('cam.base_type_fr4tg170').id or '170' in str(args.get('type')):
            number = 1.2
        if not outer:
            return {"warning": "Sorry! The PCB parameters you entered are not included in the automatic quote system. The following parameters you entered exceed the system settings:</br>  The outer layer copper thickness ≥3oz is unable to quote automatically </br> You can choose to modify according to the tips above, or let our engineers assist you. If you need the assistance of our engineers, please click the button below to switch to manual services."}
        value = {
            'copper_fee': outer.add_fee * number,
            'add_time': outer.delivery_time_1 if meter < 3 else outer.delivery_time_2
        }
        if outer.project_fee > 0:
            value.update({'eng_fee': outer.project_fee})
        if args.get('discount_id'):
            x_obj = args.get('discount_id')
            x_obj = x_obj.filtered(lambda x: x.outer_1 <= float(args.get('outer')) <= x.outer_2)
            if x_obj:
                value.update({'discount_id': x_obj})
        # 内铜厚 单双时 是没有的 网页上给的值是None
        if inner:
            inner = price_id.item_inner_copper_ids.search([('layer_item_id', '=', price_id.id),
                                                           ('min_inner_copper', '<=', inner),
                                                           ('max_inner_copper', '>', inner)])
            if not inner:
                return {"warning": "Sorry! The PCB parameters you entered are not included in the automatic quote system. The following parameters you entered exceed the system settings:</br> The inner layer copper thickness ≥3oz is unable to quote automatically </br> You can choose to modify according to the tips above, or let our engineers assist you. If you need the assistance of our engineers, please click the button below to switch to manual services."}
            add_time = inner.delivery_time_1 if meter < 3 else inner.delivery_time_2
            value['copper_fee'] = value['copper_fee'] + inner.add_fee * number
            value['add_time'] = add_time if add_time > value['add_time'] else value['add_time']
            if value.get('discount_id'):
                x_obj = value.get('discount_id')
                x_obj = x_obj.filtered(lambda x: x.inner_1 <= float(args.get('inner')) <= x.inner_2)
                if x_obj:
                    value.update({'discount_id': x_obj})
        return value

    # 字符颜色价格
    def GetTextCost(self, args):
        price_id, text = args.get('price_id'), args.get('text')
        x_value = 'text_color' if type(text) is int else 'text_color.english_name'
        text = price_id.textcolor_ids.search([('price_version_id', '=', price_id.id),
                                              (x_value, '=', text)])
        if args.get('discount_id'):
            x_obj = args.get('discount_id')
            x_obj = x_obj.filtered(lambda x: x.text_id.id == text.text_color.id)
            if x_obj:
                return {'text_fee': 0 if not text.price else text.price, 'discount_id': x_obj}
        return {'text_fee': 0 if not text.price else text.price}

    # 阻焊价格
    def GetSolderCost(self, args):
        price_id, meter, solder = args.get('price_id'), args.get('meter'), args.get('solder')
        x_value = 'silkscreen_color' if type(solder) is int else 'silkscreen_color.english_name'
        solder = price_id.silkscreencolor_ids.search([('price_version_id', '=', price_id.id),
                                                      (x_value, '=', solder)])
        if not solder and args.get('solder') != 'No' and args.get('solder') is not False:
            return {'warning': "Sorry! The PCB parameters you entered are not included in the automatic quote system. The following parameters you entered exceed the system settings:</br> The selected solder mask color is unable to quote be automatically </br> You can choose to modify according to the tips above, or let our engineers assist you. If you need the assistance of our engineers, please click the button below to switch to manual services."}
        value = {
            'solder_fee': solder.price,
            'add_time': solder.delivery_time_1 if meter < 3 else solder.delivery_time_2
        }
        if args.get('discount_id'):
            x_obj = args.get('discount_id')
            x_obj = x_obj.filtered(lambda x: x.mask_id.id == solder.silkscreen_color.id)
            if x_obj:
                value.update({'discount_id': x_obj})
        return value

    # 表面工艺
    def GetSurfaceCost(self, args, unquote=False):
        price_id, meter, surface = args.get('price_id'), args.get('meter'), args.get('surface')
        surface_id, thick_gold = surface.get('surface'), surface.get('gold_thick') or 0
        x_value = 'surface' if type(surface_id) in [int, bool] else 'surface.english_name'
        if type(surface_id) not in [int, bool]:
            if '+' not in surface_id:
                thick_gold = 0 if 'Immersion gold' not in surface_id else surface_id[16:17]  # 沉金厚度
                surface_id = surface_id if 'Immersion gold' not in surface_id else surface_id[:14]
            else:  # 乱序
                if 'OSP' in surface_id:
                    if surface_id[:surface_id.index(' +')] == 'OSP':
                        thick_gold = surface_id[surface_id.index('+'):][18:19]
                    elif surface_id[surface_id.index('+'):] == '+ OSP':
                        thick_gold = surface_id[:surface_id.index('+ ')][16:17]
                    surface_id = 'Immersion gold+ OSP'
                else:
                    surface_id = ''
            if unquote:
                return thick_gold, surface_id
        price_id = price_id.surfaceprocess_ids.search([('price_version_id', '=', price_id.id),
                                                       (x_value, '=', surface_id),
                                                       ('thick_gold', '=', thick_gold)])
        if not price_id and surface_id != 'No' and surface_id is not False:
            return {"warning": "Sorry! The PCB parameters you entered are not included in the automatic quote system. The following parameters you entered exceed the system settings:</br> The selected finishing is unable to quote be automatically </br> You can choose to modify according to the tips above, or let our engineers assist you. If you need the assistance of our engineers, please click the button below to switch to manual services."}
        if len(price_id) > 1:
            price_id = price_id[0]
        value = {
            'process_fee': 0,
            'add_time': price_id.delivery_time_1 if meter < 3 else price_id.delivery_time_2,
            'surface_fee': price_id.price,
            'thick_gold': thick_gold,  # 沉金金厚
            'surface': surface_id,
        }
        if surface.get('coating') and surface.get('nickel'):
            coating, nickel = surface.get('coating'), surface.get('nickel')
            value.update({'coating': coating, 'nickel': nickel})
            coating = max((float(coating) - 30), 0) / 30 * 70 / 100 + 1  # 临时这样写
            nickel = 1 if nickel in ['120', '0'] else max((((float(nickel) / 50) - 2) * 0.1 + 1), 1)
            value.update({'surface_fee': value['surface_fee'] * coating * nickel + price_id.extra_markup})
            if meter < 1:
                value.update({'surface_fee': value['surface_fee'] * coating * nickel, 'process_fee': price_id.extra_markup})
        if args.get('discount_id'):
            x_obj = args.get('discount_id')
            x_obj = x_obj.filtered(lambda x: price_id.surface.id in x.surface_ids.ids)
            if x_obj:
                value.update({'discount_id': x_obj})
        return value

    # 特殊材料价格
    def GetMaterialCost(self, args):
        price_id, meter, material, x_value, x_obj = args.get('price_id'), args.get('meter'), [], None, None
        value = {'material_ids': [], 'process_fee': 0, 'material_fee': 0, 'add_time': 0}
        if args.get('blue_glue') == 'Yes':
            material.append('Peelable_mask')
        if args.get('carbon_oil') == 'Yes':
            material.append('Carbon_oil')
        if 'material_ids' in args.keys():
            material = args.get('material_ids')
        if material:
            x_value = 'smaterial' if type(material[0]) is int else'smaterial.english_name'
        if args.get('discount_id'):
            x_obj = args.get('discount_id')
        for y_value in material:
            sma_id = price_id.smaterial_ids.search([('price_version_id', '=', price_id.id), (x_value, '=', y_value)])
            sma_id = sma_id.filtered(lambda s: s.max_size > meter)[0]
            value['material_ids'].append(sma_id.smaterial.id)
            if x_obj:
                x_obj = x_obj.filtered(lambda x: sma_id.smaterial.id in x.material_ids.ids)
            if meter >= 1:
                value['material_fee'] += sma_id.price
            else:
                value['process_fee'] += sma_id.price
            if meter < 3:
                value['add_time'] += (sma_id.delivery_time - 24) if sma_id.delivery_time > 24 else sma_id.delivery_time
            else:
                value['add_time'] += sma_id.delivery_time
        if x_obj:
            value.update({'discount_id': x_obj})
        return value

    # 特殊工艺价格
    def GetProcessCost(self, args):
        price_id, meter, process, x_value, x_obj = args.get('price_id'), args.get('meter'), [], None, None
        value = {'process_fee': 0, 'special_process_fee': 0, 'add_time': 0, 'special_ids': []}
        if args.get('impedance') == 'Yes':
            process.append('Impendance')
        if args.get('half_hole') == 'Yes':
            process.append('Semi-hole')
        if args.get('edge') == 'Yes':
            process.append('Edge Plating')
        if args.get('crimping') == 'Yes':
            process.append('Press-fit')
        if args.get('via') == 'Filled by Resin':
            process.append('Filled by Resin')
        if 'process_ids' in args.keys():
            process = args.get('process_ids')
        if process:
            x_value = 'sprocess' if type(process[0]) is int else'sprocess.english_name'
        if args.get('discount_id'):
            x_obj = args.get('discount_id')
        for y_value in process:
            special_id = price_id.sprocess_ids.search([('price_version_id', '=', price_id.id), (x_value, '=', y_value)])
            special_id = special_id.filtered(lambda s: s.max_size > meter)[0]
            value['special_ids'].append(special_id.sprocess.id)
            if x_obj:
                x_obj = x_obj.filtered(lambda x: special_id.sprocess.id in x.process_ids.ids)
            if meter >= 1:
                percentage_fee = special_id.percentage if special_id.percentage < 1 else special_id.percentage / 100
                value['special_process_fee'] += max((args.get('base_fee') * percentage_fee), 0) + special_id.price
            else:
                value['process_fee'] += special_id.price
            if meter >= 3:
                special_id = price_id.sprocess_ids.search([('price_version_id', '=', price_id.id),
                                                           (x_value, '=', y_value),
                                                           ('max_size', '>', meter)], limit=1)
                value['add_time'] += special_id.delivery_time
            else:
                special_id = price_id.sprocess_ids.search([('price_version_id', '=', price_id.id),
                                                           (x_value, '=', y_value),
                                                           ('max_size', '=', 1)])
                value['add_time'] += special_id.delivery_time
        if x_obj:
            value.update({'discount_id': x_obj})
        return value

    # 测试架 飞针费
    def GetTestCost(self, args):
        price_id, test_fee, points, check = args.get('price_id'), args.get('test_fee'), args.get('test_points'), False
        if int(points) <= 0:
            class_1, class_2, str_1, str_2 = 'price_type', 'price', '=', '='
            type_1, type_2, check = 'point', 0, True
        else:
            class_1, class_2, str_1, str_2 = 'min_test_points', 'max_test_points', '<', '>='
            type_1, type_2 = points, points
        tooling_ids = price_id.tooling_ids.search([('price_version_id', '=', price_id.id),
                                                   (class_1, str_1, type_1),
                                                   (class_2, str_2, type_2)])
        # 不需要计算价格 cpo_tooling_fee 此为 测试总点数产生的费用
        if check:
            points = tooling_ids.max_test_points
        else:
            tooling_fee = int(points) * tooling_ids.price
            if test_fee == 0:
                test_fee = max((tooling_fee - args.get('eng_fee')/2), 0)
            else:
                tooling_fee = max((tooling_fee - test_fee), 0)
                test_fee += tooling_fee
        return {'test_points': int(points),  'test_fee': test_fee}

    # 金手指
    def GetGoldFingerCost(self, args):
        price_id, gold, meter = args.get('price_id'), args.get('finger_dict'), args.get('meter')
        value = {'add_time': 0, 'finger_fee': 0, 'process_fee': 0}
        # 有金手指的时候专业版 可能会用到 所以保留
        if gold.get('length') and gold.get('width') and gold.get('thick') and gold.get('qty'):
            number = round(float(gold.get('length')) * float(gold.get('width')) * float(gold.get('qty')) / 7.0, 0) + 4  # 废弃小数
            if float(gold.get('length')) * float(gold.get('width')) <= 7.0:
                number = float(gold.get('qty')) + 4
            if number > 300:
                return {'warning': "Sorry! The PCB parameters you entered are not included in the automatic quote system. The following parameters you entered exceed the system settings:</br> Gold finger No. >300 pcs is unable to quote be automatically</br> You can choose to modify according to the tips above, or let our engineers assist you. If you need the assistance of our engineers, please click the button below to switch to manual services."}
            gold_id = price_id.gold_finger_id.search([('cpo_gold_finger_thickness', '>=', gold.get('thick'))])
            if not gold_id:
                return {'warning': "Sorry! The PCB parameters you entered are not included in the automatic quote system. The following parameters you entered exceed the system settings:</br> Gold finger thickness > 50μ is unable to quote be automatically </br> You can choose to modify according to the tips above, or let our engineers assist you. If you need the assistance of our engineers, please click the button below to switch to manual services."}
            gold_id = gold_id[0]
            # 最低的收费标准!!! 金厚标尺 - gold_id.cpo_moq
            min_fee = gold_id.cpo_min_fee if gold_id.cpo_moq > float(gold.get('thick')) else gold_id.cpo_max_fee
            cost_fee = gold_id.cpo_cost_fee  # 单PCS成本的费用
            profit_ratio = gold_id.cpo_profit_ratio if gold_id.cpo_profit_ratio < 1 else (gold_id.cpo_profit_ratio / 100.0) + 1  # 可收取的百分比
            fee_id = gold_id.cpo_gold_finger_number_id  # 获取根据金厚 根数得到的价格
            for x_id in fee_id:
                if x_id.cpo_gold_finger_number.cpo_root_number >= number:
                    fee_id = x_id
                    break
            number_fee = fee_id.cpo_gold_finger_fee  # 获取根据金厚 根数得到的价格
            increase_fee = cost_fee / float(1200.0 / float(args.get('length')) / float(args.get('width')))
            if (float(args.get('length')) * float(args.get('width'))) <= 150:
                increase_fee = 0
            increase_fee_2 = (int(args.get('layer')) - 2) / 75.0
            if (int(args.get('layer')) - 2) <= 0:
                increase_fee_2 = 0
            unit_price_fee = (number_fee + increase_fee) * profit_ratio * (1.04 + increase_fee_2)
            gold_finger_fee = unit_price_fee / (float(args.get('length')) * 0.01) / (float(args.get('width')) * 0.01)  # 厘米转化米
            value.update({'add_time': gold_id.delivery_time_1 if meter < 3 else gold_id.delivery_time_2})
            if min_fee < (gold_finger_fee * meter):
                value.update({'finger_fee': gold_finger_fee})
            else:
                value.update({'process_fee': min_fee})
        # 简约版
        elif gold.get('thick') and args.get('qty'):
            qty, pcs = args.get('qty'), args.get('pcs_set')
            if pcs:
                qty = int(qty) * int(pcs)
            thick_id = price_id.gold_finger_id.search([('cpo_gold_finger_thickness', '=', gold.get('thick'))])
            number_id = thick_id.cpo_gold_finger_number_id[-1]
            value.update({
                'add_time': thick_id.delivery_time_1 if meter < 3 else thick_id.delivery_time_2,
                'finger_fee': int(qty) * number_id.cpo_gold_finger_fee if thick_id.cpo_min_fee < int(qty) * number_id.cpo_gold_finger_fee else thick_id.cpo_min_fee
            })
        return value

    # 软硬结合报价
    def GetSoftCost(self, args):
        layer, size, soft = args.get('layer'), args.get('meter'), args.get('soft')
        price_id, number = args.get('price_id'), soft.get('cpo_flex_number')
        # 总层数
        layer = int(layer) + int(number) * 2
        soft_id = price_id.soft_hard_id.search([('price_version_id', '=', price_id.id), ('total_layers', '=', layer)])
        if not soft_id:
            return {'warning': "Sorry! The PCB parameters you entered are not included in the automatic quote system. The following parameters you entered exceed the system settings:</br> L≥20L Flex-Rigid is unable to quote automatically </br> You can choose to modify according to the tips above, or let our engineers assist you. If you need the assistance of our engineers, please click the button below to switch to manual services."}
        value = {'board_fee': 0, 'eng_fee': int(number) * soft_id.soft_inner, 'delivery': 0, 'total_layers': layer}
        if size < 1:
            value.update({'board_fee': soft_id.soft_board if size < 0.2 else soft_id.soft_board2, 'delivery': soft_id.delivery})
        elif 1 <= size < 3:
            value.update({'board_fee': soft_id.soft_board2, 'delivery': soft_id.delivery2})
        elif 3 <= size <= 10:
            value.update({'board_fee': soft_id.soft_board3, 'delivery': soft_id.delivery3})
        return value

    # 最小线宽线距 小孔 孔铜
    def GetLineHoleCopperCost(self, args):
        price_id, ipc_id, ben_fee = args.get('price_id'), args.get('standard'), args.get('base_fee')
        # 其他费用 工艺费 验收百分比 细线百分比
        value = {'other_fee': 0, 'process_fee': 0, 'ipc_fee': 1, 'line_fee': 1}
        other_id = price_id.other_ids.search([('price_version_id', '=', price_id.id), ('min_size', '<=', args['meter']), ('max_size', '>', args['meter'])])
        # 线距线宽 没有值的时候
        line_id = other_id.other_line_ids.search([('price', '=', 0), ('price_class', '=', '%'), ('price_other_fee_id', '=', other_id.id)])[0]  # 线宽线距的
        hole_id = other_id.other_hole_ids.search([('price', '=', 0), ('price_class', '=', '%'), ('price_other_fee_id', '=', other_id.id)])[0]  # 孔的
        value.update({
            'space': line_id.min_line_cpo_width if float(args.get('space')) == 0 else float(args.get('space')),
            'width': line_id.min_line_cpo_width if float(args.get('width')) == 0 else float(args.get('width')),
            'hole': hole_id.min_hole if float(args.get('hole')) == 0 else float(args.get('hole')),
        })
        # 如果是超厚铜箔需要重新限制 线宽线距
        if args.get('outer') and float(args.get('outer')) >= 6:
            x_value = 10 + (float(args.get('outer')) / 2 - 3) * 2.5
            value.update({
                'space': x_value if value.get('space') < x_value else value.get('space'),
                'width': x_value if value.get('width') < x_value else value.get('width')
            })
        # 验收标准 与 孔铜默认值所有关
        if ipc_id and int(ipc_id) == 2:
            value.update({'hole_copper': 20 if float(args.get('copper')) == 0 else float(args.get('copper'))})
        elif ipc_id and int(ipc_id) == 3:
            value.update({'hole_copper': 25 if float(args.get('copper')) == 0 else float(args.get('copper'))})
        elif args.get('copper'):
            value.update({'hole_copper': args.get('copper')})
        else:
            value.update({'hole_copper': args.get('copper')})
        for x_value in [value['width'], value['space']]:
            line_id = other_id.other_line_ids.search([('min_line_cpo_width', '<=', x_value),
                                                      ('max_line_cpo_width', '>', x_value),
                                                      ('price_other_fee_id', '=', other_id.id),
                                                      ('price_class', '=', '%')])  # 线宽线距的
            value['line_fee'] += line_id.price if line_id.price < 1 else line_id.price / 100.0
            if not line_id:
                return {'warning': "Sorry! The PCB parameters you entered are not included in the automatic quote system. The following parameters you entered exceed the system settings:</br>  The filled width/spacing is unable to quote be automatically</br> You can choose to modify according to the tips above, or let our engineers assist you. If you need the assistance of our engineers, please click the button below to switch to manual services."}
        # 最小孔
        if float(args.get('thick')) > 1 and value.get('hole') == 6:
            return {'warning': "Sorry! The PCB parameters you entered are not included in the automatic quote system. The following parameters you entered exceed the system settings:</br>  If 6mil holes exists,The board thickness need be ≤1mm </br> You can choose to modify according to the tips above, or let our engineers assist you. If you need the assistance of our engineers, please click the button below to switch to manual services."}
        elif value.get('hole') < 6:
            return {'warning': "Sorry! The PCB parameters you entered are not included in the automatic quote system. The following parameters you entered exceed the system settings:</br>  The min holes is ≤6mil, it is out of capacility </br> You can choose to modify according to the tips above, or let our engineers assist you. If you need the assistance of our engineers, please click the button below to switch to manual services."}
        str_x = '=' if value.get('hole') == 6 and float(args.get('thick')) <= 1 else '<='
        str_y = '=' if value.get('hole') == 6 and float(args.get('thick')) <= 1 else '>'
        hole_id = other_id.other_hole_ids.search([('min_hole', str_x, value['hole']),
                                                  ('max_hole', str_y, value['hole']),
                                                  ('price_class', '=', '%'),
                                                  ('price_other_fee_id', '=', other_id.id)])  # 孔的
        hole_fee = hole_id.price if hole_id.price < 1 else hole_id.price / 100.0
        value.update({'other_fee': hole_fee * (0 if not ben_fee else ben_fee)})
        # 孔铜 同时处理 验收标准
        copper_id = other_id.other_hole_copper_ids.search([('price_other_fee_id', '=', other_id.id),
                                                           ('hole_copper_thick', '<=', value['hole_copper']),
                                                           ('hole_copper_thick1', '>', value['hole_copper'])])  # 孔铜的
        if not copper_id:
            return {'warning': "Sorry! The PCB parameters you entered are not included in the automatic quote system. The following parameters you entered exceed the system settings:</br>  The filled hole wall copper is unable to quote be automatically </br> You can choose to modify according to the tips above, or let our engineers assist you. If you need the assistance of our engineers, please click the button below to switch to manual services."}
        hole_copper_fee = copper_id.hole_copper_fee
        if args['meter'] < 1:
            value.update({'process_fee': 0 if value['hole_copper'] <= 30 else hole_copper_fee * value['hole_copper'] / 35})
        copper_ids_fee = max((value['hole_copper'] - 20), 0) * (hole_copper_fee / 10)
        if value['hole_copper'] > 40:
            copper_ids_fee = (value['hole_copper'] - 35) / 35 * 100 + hole_copper_fee
        value['other_fee'] += copper_ids_fee
        if ipc_id and type(ipc_id) is not int:
            x_value = 'acceptance_criteria_id.cpo_level'
        else:
            x_value = 'acceptance_criteria_id'
            ipc_id = args['standard'] if type(args['standard']) == int else args['standard'].id
        ipc_id = other_id.other_acceptance_criteria_ids.search([('price_other_fee_id', '=', other_id.id),
                                                                (x_value, '=', ipc_id),
                                                                ('price_class', '=', '%')])  # 验收标准
        value['ipc_fee'] += ipc_id.price if ipc_id.price < 1 else ipc_id.price / 100.0
        value.update({'ipc_id': ipc_id.acceptance_criteria_id.id})
        return value

    # 独立处理 交期天数
    def GetTime(self, args):
        value = {'delivery': 0, 'quick': 1, 'quick_list': []}
        add_time, size_id, meter = args.get('add_time'), args.get('size_id'), args.get('meter')
        expedited = args.get('expedited')
        if size_id:
            min_day = size_id.min_delay_hours / (size_id.quick_time if size_id.quick_time > 0 else 1)  # 最快交期 - 天数
            max_day = size_id.max_delay_hours / (size_id.quick_time if size_id.quick_time > 0 else 1)  # 正常交期 - 天数
            quick_fee = size_id.quick_fee if size_id.quick_fee < 1 else size_id.quick_fee / 100.0  # 加急百分比
            for x in range(1, max_day - min_day + 1):
                value['quick_list'].append((max_day + add_time / 24) - x)
            value.update({'delivery': max_day + add_time / 24})
            # 加急时 走这一步
            if expedited:
                value.update({
                    'quick': quick_fee * (max_day - (int(expedited) - add_time / 24)) + 1,
                    'delivery': int(expedited)
                })
        if args.get('soft'):
            value.update({'delivery': (args.get('soft').get('delivery') + add_time) / 24})
        elif args.get('hdi'):
            size_id = size_id.type_item_ids.filtered(lambda s: s.base_type.english_name == 'FR4-Tg135-HDI')
            value.update({'delivery': (size_id.max_delay_hours + add_time) / 24})
        return value

    # 钢网费用
    def GetSteelCost(self, args):
        price_id, pcb_frame = args['price_id'], None
        if args['cpo_pcb_frame'] in ['With Frame', 'With_Frame']:
            pcb_frame = 'With_Frame'
        elif args['cpo_pcb_frame'] in ['Without Frame', 'Without_Frame']:
            pcb_frame = 'Without_Frame'
        elif args['cpo_pcb_frame'] == 'No':
            pcb_frame = 'No'
        with_frame_ids = price_id.with_frame_ids.search([('price_version_id', '=', price_id.id),
                                                         ('type_steel_mesh', '=', pcb_frame)])
        cpo_frame_fee = with_frame_ids.cpo_frame_fee if with_frame_ids else 0
        return {'cpo_frame_fee': cpo_frame_fee, 'pcb_frame': pcb_frame}

    @api.model  # 前端接口
    def CreateOrUpdatePCBQuote(self, x_id, args, package=False, unquote=False):
        if unquote:
            return self.create_or_update_order_unqute(args)
        if not args.get('edit_id') and package:
            return self.create_pcb_package(args)
        elif args.get('edit_id'):
            return self.update_pcb_quote(args, package=package)
        else:
            return self.create_pcb_quote(x_id, args)

    def create_or_update_order_unqute(self, args):
        quotation_id, partner = self.create_quote(args)
        args = self.GetNameField(args, create_order=True, unquote=True)
        vals = self.ArrangeUnquoteData(args)
        vals = self.update_vals(vals, partner, quotation_id)
        quotation_id.quotation_line.create(vals)
        order = self.action_done(quotation_id)
        quotation_id.signal_workflow('action_done')
        quotation_id.update({'state': 'done'})
        self.env['sale.order'].browse(order.get('res_id')).write({'state': 'wait_confirm'})
        return order['res_id'] if order['res_id'] else None

    # 直接搜索特殊工艺中的ID
    def search_process_id(self, args):
        process, process_id = [], []
        if args.get('impedance') == 'Yes':
            process.append('Impendance')
        if args.get('half_hole') == 'Yes':
            process.append('Semi-hole')
        if args.get('edge') == 'Yes':
            process.append('Edge Plating')
        if args.get('crimping') == 'Yes':
            process.append('Press-fit')
        if args.get('via') == 'Filled by Resin':
            process.append('Filled by Resin')
        if args.get('control'):
            process.append('Depth control routing')
        if args.get('blind'):
            process.append('Blind&Buired via')
        if args.get('deep_hole'):
            process.append('Number of countersunk/deep holes')
        if args.get('structure'):
            process.append('Blind hole structure')
        for x in process:
            x_id = self.env['cam.special.process'].search([('english_name', '=', x)]).id
            process_id.append(x_id)
        return process_id

    # 直接搜索特殊材料ID
    def search_material_id(self, args):
        material, material_ids = [], []
        if args.get('blue_glue') == 'Yes':
            material.append('Peelable_mask')
        if args.get('carbon_oil') == 'Yes':
            material.append('Carbon_oil')
        for x in material:
            x_id = self.env['cam.special.material'].search([('english_name', '=', x)]).id
            material_ids.append(x_id)
        return material_ids

    # 生成创建订单需要的数据 - 不可报价使用
    def ArrangeUnquoteData(self, args):
        process_ids = self.search_process_id({
            'via': args.get('via'),  # 过孔处理
            'half_hole': args.get('half_hole'),  # 半孔
            'edge': args.get('edge'),  # 板边电镀
            'impedance': args.get('impedance'),  # 阻抗
            'crimping': args.get('crimping'),  # 压接孔
            'control': args.get('control'),  # 控深锣
            'blind': args.get('blind'),  # 埋盲孔钻带数
            'deep_hole': args.get('deep_hole'),  # 沉头/控深孔数
            'structure': args.get('structure'),  # 埋盲孔结构
        })
        material_ids = self.search_material_id({
            'blue_glue': args.get('blue_glue'),
            'carbon_oil': args.get('carbon_oil'),
        })
        surface_dict, gold_dict = args.get('surface_dict'), args.get('finger_dict')
        thick_gold, surface_id = self.GetSurfaceCost({"surface": surface_dict}, unquote=True)
        text_id = self.env['cam.ink.color'].search([('english_name', '=', args.get('text'))]).id
        type_id = self.env['cam.base.type'].search([('english_name', '=', args.get('type'))]).id  # 基材
        solder_id = self.env['cam.ink.color'].search([('english_name', '=', args.get('solder'))]).id
        acceptance_id = self.env['cam.acceptance.criteria'].search([('cpo_level', '=', args.get('standard'))]).id
        layer_id = self.env['cam.layer.number'].search([('layer_number', '=', args.get('layer'))]).id
        surface_id = self.env['cam.surface.process'].search([('english_name', '=', surface_id)]).id
        via_id = self.env['cam.via.process'].search([('english_name', '=', args.get('via'))]).id
        if args.get('unit') != 'PCS':
            args.update({'unit': 'SET'})
        product_uom_id = self.env['product.uom'].search([('name', '=', args.get('unit'))]).id
        meter = (float(args['width']) * float(args['length']) * 0.01 * int(args['qty'])) / 10000.0
        centimeter = float(args['width']) * float(args['length']) * 0.01
        if args.get('unit') != 'PCS' and args.get('pcs_set'):
            centimeter = (float(args['width']) * float(args['length']) * 0.01) / float(args.get('pcs_set'))
        if 1 <= meter < 10:
            volume = 'small'
        elif 10 <= meter < 50:
            volume = 'medium'
        elif 50 <= meter:
            volume = 'large'
        else:
            volume = 'prototype'
        vals = {
            'unquote_bool': True,  # 不走计算
            'package_bool': False,  # 不是打包价的
            'rogers_number': args.get('rogers').get('rogers_number'),
            'core_thick': args.get('rogers').get('core_thick'),
            'soft_level': args.get('soft').get('cpo_inner_outer'),
            'window_bool': True if args.get('soft').get('cpo_flex_open') == 'Yes' else False,
            'soft_number': args.get('soft').get('cpo_flex_number'),
            'cpo_hdi': args.get('hdi').get('number_of_step'),
            # 'delivery_hour': (quick_dict['delivery'] * 24) - (quick_dict['add_time']),  # 原始的时间
            # 'increase_delivery_hour': quick_dict.get('add_time'),  # 增加的时间
            'urgent': False,  # 加不加急
            'cpo_gold_height': gold_dict.get('length'),  # 金手指 长
            'cpo_gold_width': gold_dict.get('width'),  # 金手指 宽
            'cpo_gold_thick': gold_dict.get('thick'),  # 金手指 厚度
            'cpo_gold_root': gold_dict.get('qty'),  # 金手指 根数
            'pcs_size': centimeter,  # 厘米面积
            'cpo_item_number': 1 if not args.get('together') else args.get('together'),  # 拼板数
            'total_size': meter,  # 平米面积
            'cpo_length': args.get('length'),
            'cpo_width': args.get('width'),
            'layer_number': layer_id,  # 层数
            'pcs_per_set': 1 if not args.get('pcs_set') else float(args.get('pcs_set')),  # pcs数
            'base_type': type_id,  # 基材
            'thickness': args.get('thick'),
            'volume_type': volume,
            'inner_copper': args.get('inner'),  # 内铜厚
            'outer_copper': args.get('outer'),  # 外铜厚
            'text_color': text_id,  # 字符颜色
            'surface': surface_id,  # 表面处理
            'gold_thickness': thick_gold,  # 沉金数值
            'silkscreen_color': solder_id,  # 阻焊
            'product_uom_qty': args.get('qty'),  # 数量
            'product_uom': product_uom_id,  # 计量单位
            'product_uos_qty': args.get('qty'),  # 数量
            'product_uos': product_uom_id,  # 计量单位
            'tooling': False if args.get('test') is False else True,  # 测试架
            'fly_probe': True if args.get('test') is False else False,  # 飞针
            'sprocess_ids': [(6, 0, process_ids)],  # 特殊工艺的id号 - 列表
            'via_process': via_id,  # 普通工艺的id号
            'smaterial_ids': [(6, 0, material_ids)],  # 特殊材料的id号 - 列表
            'test_points': int(float(args.get('test_points'))),  # 测试总点数
            'min_hole': args.get('min_hole'),  # 最小孔
            'min_line_cpo_width': args.get('min_width'),  # 线宽
            'min_line_distance': args.get('min_space'),  # 线距
            'line_to_hole_distance': args.get('hole_distance'),  # 内层孔到线
            'total_holes': int(float(args.get('total_holes'))),  # 总孔数
            'cpo_pp_number': args.get('pp'),  # pp张数
            'cpo_core_number': args.get('core'),  # 芯板张数
            'cpo_hole_copper': args.get('hole_copper'),  # 孔铜
            'cpo_standard': acceptance_id,  # 验收标准
            'gold_size': 0 if not surface_dict.get('coating') else surface_dict.get('coating'),  # 沉金面积
            'cpo_nickel_thickness': '0' if not surface_dict.get('nickel') else surface_dict.get('nickel'),  # 沉金镍厚
            'request': args.get('request'),
            'v_cut': args.get('v_cut'),
            'drilling': args.get('drilling'),
            'back': args.get('back'),
        }
        return vals

    # 生成创建订单需要的数据 - 可报价时调用的
    def ArrangeQuoteData(self, args):
        vals = self.GetQuotation(args)
        gold_dict, surface_dict, layer_dict = args.get('finger_dict'), args.get('surface_dict'), vals.get('layer')
        surface_dict, quick_dict, material, process = vals.get('surface'), vals.get('expedited'), vals.get('material'), vals.get('process')
        text_id = self.env['cam.ink.color'].search([('english_name', '=', args.get('text'))]).id
        type_id = self.env['cam.base.type'].search([('english_name', '=', args.get('type'))]).id  # 基材
        solder_id = self.env['cam.ink.color'].search([('english_name', '=', args.get('solder'))]).id
        acceptance_id = self.env['cam.acceptance.criteria'].search([('cpo_level', '=', args.get('standard'))]).id
        layer_id = self.env['cam.layer.number'].search([('layer_number', '=', layer_dict.get('layer'))]).id
        surface_id = self.env['cam.surface.process'].search([('english_name', '=', surface_dict.get('surface'))]).id
        via_id = self.env['cam.via.process'].search([('english_name', '=', args.get('via'))]).id
        if args.get('unit') != 'PCS':
            args.update({'unit': 'SET'})
        product_uom_id = self.env['product.uom'].search([('name', '=', args.get('unit'))]).id
        if 1 <= vals.get('layer').get('meter') < 10:
            volume = 'small'
        elif 10 <= vals.get('layer').get('meter') < 50:
            volume = 'medium'
        elif 50 <= vals.get('layer').get('meter'):
            volume = 'large'
        else:
            volume = 'prototype'
        vals = {
            'package_bool': False,  # 不是打包价的
            # 'cpo_type_steel_mesh': frame_pcb['pcb_frame'],  # 钢网
            'rogers_number': args.get('rogers').get('rogers_number'),
            'core_thick': args.get('rogers').get('core_thick'),
            'soft_level': args.get('soft').get('cpo_inner_outer'),
            'window_bool': True if args.get('soft').get('cpo_flex_open') == 'Yes' else False,
            'soft_number': args.get('soft').get('cpo_flex_number'),
            'cpo_hdi': args.get('hdi').get('number_of_step'),
            'delivery_hour': (quick_dict['delivery'] * 24) - (quick_dict['add_time']),  # 原始的时间
            'increase_delivery_hour': quick_dict.get('add_time'),  # 增加的时间
            'urgent': False if quick_dict.get('quick') <= 1 else True,  # 加不加急
            'cpo_gold_height': gold_dict.get('length'),  # 金手指 长
            'cpo_gold_width': gold_dict.get('width'),  # 金手指 宽
            'cpo_gold_thick': gold_dict.get('thick'),  # 金手指 厚度
            'cpo_gold_root': gold_dict.get('qty'),  # 金手指 根数
            'pcs_size': layer_dict.get('cm'),  # 厘米面积
            'cpo_item_number': layer_dict.get('together'),  # 拼板数
            'total_size': layer_dict.get('meter'),  # 平米面积
            'cpo_length': args.get('length'),
            'cpo_width': args.get('width'),
            'layer_number': layer_id,  # 层数
            'pcs_per_set': layer_dict.get('pcs_set'),  # pcs数
            'base_type': type_id,  # 基材
            'thickness': args.get('thick'),
            'volume_type': volume,
            'inner_copper': args.get('inner'),  # 内铜厚
            'outer_copper': args.get('outer'),  # 外铜厚
            'text_color': text_id,  # 字符颜色
            'surface': surface_id,  # 表面处理
            'gold_thickness': surface_dict.get('thick_gold'),  # 沉金数值
            'silkscreen_color': solder_id,  # 阻焊
            'product_uom_qty': args.get('qty'),  # 数量
            'product_uom': product_uom_id,  # 计量单位
            'product_uos_qty': args.get('qty'),  # 数量
            'product_uos': product_uom_id,  # 计量单位
            'tooling': False if args.get('test') is False else True,  # 测试架
            'fly_probe': True if args.get('test') is False else False,  # 飞针
            'sprocess_ids': [(6, 0, process['special_ids'])],  # 特殊工艺的id号 - 列表
            'via_process': via_id,  # 普通工艺的id号
            'smaterial_ids': [(6, 0, material['material_ids'])],  # 特殊材料的id号 - 列表
            'test_points': int(float(args.get('test_points'))),  # 测试总点数
            'min_hole': args.get('min_hole'),  # 最小孔
            'min_line_cpo_width': args.get('min_width'),  # 线宽
            'min_line_distance': args.get('min_space'),  # 线距
            'line_to_hole_distance': args.get('hole_distance'),  # 内层孔到线
            'total_holes': int(float(args.get('total_holes'))),  # 总孔数
            'cpo_pp_number': args.get('pp'),  # pp张数
            'cpo_core_number': args.get('core'),  # 芯板张数
            'cpo_hole_copper': args.get('hole_copper'),  # 孔铜
            'cpo_standard': acceptance_id,  # 验收标准
            'gold_size': 0 if not surface_dict.get('coating') else surface_dict.get('coating'),  # 沉金面积
            'cpo_nickel_thickness': '0' if not surface_dict.get('nickel') else surface_dict.get('nickel'),  # 沉金镍厚
            'request': args.get('request'),
        }
        return vals

    # 创建quotation 返回quote 和 partner
    def create_quote(self, args):
        if args.get('pcb_partner_id'):
            partner = self.env['res.partner'].browse(args.get('pcb_partner_id'))
        else:
            partner = self.env.ref("base.public_partner")
        addr = partner.address_get(['delivery', 'invoice'])
        quote = self.create({
            'partner_id': partner.id,  # 客户
            'partner_invoice_id': addr['invoice'],  # 发票地址
            'partner_shipping_id': addr['delivery'],  # 送货地址
            'currency_id': self.env.ref('base.USD').id,  # 货币 现在暂时写死
        })
        return quote, partner

    def update_vals(self, vals, partner, quotation_id):
        vals.update({
            'product_no': partner.name + str(int(time.time()))[:7],  # 产品编号
            'quotation_id': quotation_id.id,
        })
        return vals

    # 创建生成订单 - 创建PCB订单
    def create_pcb_quote(self, x_id, args):
        quotation_id, partner = self.create_quote(args)
        args = self.GetNameField(args, create_order=True)
        vals = self.ArrangeQuoteData(args)
        vals = self.update_vals(vals, partner, quotation_id)
        quotation_line = quotation_id.quotation_line.create(vals)
        cpo_sale_order = {}
        if quotation_id.amount_total != 0:
            cpo_sale_order = self.action_done(quotation_id)
            quotation_id.signal_workflow('action_done')
            quotation_id.update({'state': 'done'})
        if x_id != '':
            # order_id = self.env['sale.order.line'].browse(x_id).order_id.id
            order_id = self.env['sale.order'].browse(int(x_id))
            # pcba_src_order = self.env['sale.order'].search([('id', '=', order_id)])
            order_id.quotation_line.unlink()
            order_id.write({'quotation_line': [(4, quotation_line.id)]})
            order_id.cpo_pcba_sync_po_to_quo()
            self.env['sale.order'].search([('id', '=', cpo_sale_order['res_id'])]).unlink()
            cpo_sale_order['res_id'] = order_id.id
        return cpo_sale_order['res_id'] if cpo_sale_order['res_id'] else None

    # 更新生成订单 - 更新PCB订单
    def update_pcb_quote(self, args, package=False):
        order = self.env['sale.order'].browse(int(args.get('edit_id')))
        if package:
            args = self.ArrangeQuotePackage(args)
        else:
            args = self.GetNameField(args, create_order=True)
            args = self.ArrangeQuoteData(args)
        order.quotation_line.write(args)
        if package:
            order.quotation_line.pcb_package_calculation(order.quotation_line.id)
        else:
            order.quotation_line.pcb_price_calculation(order.quotation_line.id)
        args = {
            'product_uom_qty': args.get('product_uom_qty'),
            'product_id': order.quotation_line.layer_number.product_ids.id,
        }
        if order.product_type == 'PCBA':
            args.pop('product_id')
            args.update({
                'pcb_length': order.quotation_line.cpo_length,
                'pcb_width': order.quotation_line.cpo_width,
                'pcb_thickness': order.quotation_line.thickness,
            })
        order.order_line.write(args)
        return order.id

    # 钢网 - 独立报价 前端接口
    @api.model
    def get_steel_mesh_price(self, args):
        return self.get_steel_net_offer(args)

    # 网页中钢网的报价
    @api.model
    def get_steel_net_offer(self, args):
        country, stencil_data = args.get('cpo_country'), args.get('stencil_data')  # 国家
        # 数量 尺寸 厚度 - 钢网
        qty, size, thick = stencil_data.get('stencil_qty'), stencil_data.get('stencil_size'), stencil_data.get('stencil_thickness')
        size = re.split('m|\*', size)
        steel_db = self.env['laser.steel.mesh.price'].search([('quantity_1', '<', int(qty)),
                                                              ('quantity_2', '>=', int(qty)),
                                                              ('steel_size_id.stencil_size_1', '=', float(size[0])),
                                                              ('steel_size_id.stencil_size_2', '=', float(size[1]))])
        if not steel_db:
            return {'warning': 'There are too many steel meshes. If you need, you can contact customer service.'}
        if len(steel_db) > 1:
            steel_db = steel_db.filtered(lambda s: s.steel_thickness_id.name == float(thick))[0]
        # 价格 重量 交期
        price, weight, delivery = steel_db.cpo_price, steel_db.cpo_weight, steel_db.cpo_delivery
        freight_fee = self.env['cpo.pcb.freight'].cpo_create_freight({'country_id': country if country else 'No'.decode('gbk'), 'weight': weight * int(qty)})
        return {
            'Stencil Cost': round(price * int(qty), 2),
            'Stencil Delivery': delivery / 24,
            'Stencil Freight': round(freight_fee, 0),
            'Stencil Total': round(price * int(qty), 2) + round(freight_fee, 0)
        }

    # 前段创建订单接口
    @api.model
    def cpo_create_stencil(self, args):
        return self.cpo_to_create_stencil(args)

    # 创建钢网订单
    @api.model
    def cpo_to_create_stencil(self, *args):
        partner_id = args[0]['partner_id']  # 客户
        args = args[0].get('stencil_data')
        qty, size, thick = args.get('stencil_qty'), args.get('stencil_size'), args.get('stencil_thickness')
        size = re.split('m|\*', size)
        stencil_thick_id = self.env['cam.steel.mesh.thickness'].search([('name', '=', float(thick))]).id
        stencil_size_id = self.env['cam.laser.steel.mesh.size'].search([('stencil_size_1', '=', float(size[0])),
                                                                        ('stencil_size_2', '=', float(size[1]))]).id
        steel_db = self.env['laser.steel.mesh.price'].search([('steel_size_id', '=', stencil_size_id)])
        # 小计 交期 重量
        subtotal, delivery, weight = steel_db.cpo_price, steel_db.cpo_delivery, steel_db.cpo_weight
        if partner_id:
            partner = self.env['res.partner'].browse(partner_id)
        else:
            partner = self.env.ref("base.public_partner")
        addr = partner.address_get(['delivery', 'invoice'])
        product_id = self.env['product.product'].search([('name', '=', 'Stencil')])
        # 用户后面传过来
        order_id = self.env['sale.order'].create({
            'partner_id': partner.id,  # 客户
            'partner_invoice_id': addr['invoice'],  # 发票地址
            'partner_shipping_id': addr['delivery'],  # 送货地址
            'currency_id': self.env.ref('base.USD').id,  # 货币 现在暂时写死
            'product_type': product_id.name,
            'stencil_line': [(0, 0, {
                'steel_mesh_size_id': stencil_size_id,
                'steel_mesh_thickness_id': stencil_thick_id,
                'cpo_stencil_qty': int(qty),
                'cpo_stencil_delivery': delivery,
                'cpo_stencil_subtotal': subtotal * int(qty),
                'cpo_stencil_weight': weight * int(qty),
                'cpo_stencil_text': args.get('stencil_special')
            })],
            'order_line': [(0, 0, {
                'product_id': product_id.id,
                'product_uom_qty': int(qty),
            })]
        })
        return order_id.id
