# -*- coding: utf-8 -*-
import logging
import odoo.addons.decimal_precision as dp
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
_logger = logging.getLogger(__name__)

AVAILABLE_DELIVERY_UOS = [
    ('pcs', 'PCS'),
    ('set', 'SET'),
    ('pnl', 'PNL'),
]
NICKEL_THICKNESS = [
    ('0', '0'),
    ('120', '120'),
    ('150', '150'),
    ('200', '200'),
    ('250', '250'),
    ('300', '300'),
    ('350', '350'),
    ('400', '400')
]
STEEL_MESH_TYPE = [
        ('With_Frame', 'With Frame'),
        ('Without_Frame', 'Without Frame'),
        ('No', 'No')
    ]


# 钢网独立报价的class
class sale_stencil_line(models.Model):
    _name = 'sale.stencil.line'
    _description = 'Sale stencil line'
    # 三个索引字段
    sale_order_id = fields.Many2one('sale.order', 'Sale Order', index=True, ondelete='cascade')
    steel_mesh_size_id = fields.Many2one('cam.laser.steel.mesh.size', 'Stencil Size And Effective Size', index=True)
    steel_mesh_thickness_id = fields.Many2one('cam.steel.mesh.thickness', 'Stencil Thickness')
    cpo_stencil_qty = fields.Integer('Stencil Quantity')
    cpo_stencil_delivery = fields.Integer('Stencil Delivery / H')
    cpo_stencil_subtotal = fields.Float('Stencil Subtotal', digits=(16, 2))
    cpo_stencil_weight = fields.Float('Stencil Weight', digits=(16, 2))
    cpo_stencil_text = fields.Text("Remarks")

    def write(self, vals):
        stencil_list = ['steel_mesh_size_id', 'cpo_stencil_qty']
        difference = len(set(vals.keys()) - set(stencil_list))
        if len(vals.keys()) != difference:
            subtotal = self.stencil_calculation(size_id=vals.get('steel_mesh_size_id'), qty=vals.get('cpo_stencil_qty'))
            vals.update({'cpo_stencil_subtotal': subtotal})
        return super(sale_stencil_line, self).write(vals)

    def stencil_calculation(self, size_id=False, qty=False):
        if not size_id:
            size_id = self.steel_mesh_size_id.id
        if not qty:
            qty = self.cpo_stencil_qty
        steel_db = self.env['laser.steel.mesh.price'].search([('steel_size_id', '=', size_id)])
        return steel_db.cpo_price * qty

    @api.onchange('steel_mesh_size_id', 'cpo_stencil_qty')
    def _onchange_stencil_size_id(self):
        size_id, qty = self.steel_mesh_size_id.id, self.cpo_stencil_qty
        steel_db = self.env['laser.steel.mesh.price'].search([('steel_size_id', '=', size_id)])
        if not size_id or qty <= 0:
            return {'value': {}, 'warning': {}}
        return self.update({'cpo_stencil_weight': steel_db.cpo_weight * qty})


# 原版费 改为 基准价 增加了拼版款数 金手指的相关参数 将原本勾选的金手指和金手指斜角替换
# 测试架费用 改为 版费
class sale_quotation_line(models.Model):
    _name = "sale.quotation.line"
    _description = "Sales Quotation Line"
    _order = 'quotation_id desc, sequence, id'

    def _compute_unit_size(self, field_name, *args):
        res = {}
        for line in self.browse(self.ids):
            pcb_cpo_length = float(line.cpo_length)
            pcb_cpo_width = float(line.cpo_width)
            res[line.id] = pcb_cpo_length * pcb_cpo_width
        return res

    def _compute_size(self, field_name, *args):
        res = {}
        for line in self.browse(self.ids):
            pcb_cpo_length = float(line.cpo_length)
            pcb_cpo_width = float(line.cpo_width)
            qty = float(line.product_uom_qty)
            res[line.id] = (pcb_cpo_length * pcb_cpo_width * qty)/10000.0000
        return res

    def _get_uom_id(self, *args):
        try:
            proxy = self.env['ir.model.data']
            result = proxy.get_object_reference('product', 'product_uom_unit')
            return result[1]
        except Exception as e:
            _logger.error(e.message)
            return False

    @api.depends('product_uom_qty', 'pcs_per_set')
    def get_pcs_number(self, *args):
        for obj in self:
            if obj.product_uom_qty <= 0 or obj.pcs_per_set <= 0:
                obj.pcs_number = 0
            else:
                obj.pcs_number = obj.product_uom_qty / obj.pcs_per_set
                obj.pcs_number = int(obj.pcs_number)
    # 有3个索引字段
    quotation_id = fields.Many2one('sale.quotation', 'Order Reference', required=True, ondelete='cascade', index=True)
    order_id = fields.Many2one('sale.order', 'Sale Order', index=True, ondelete='cascade')  # domain="[()]"
    cpo_lock_bool = fields.Boolean(related='order_id.cpo_lock_bool', string='Lock')
    # name = fields.Text('Description')
    sequence = fields.Integer('Sequence', help="Gives the sequence order when displaying a list of sales order lines.", default=10)
    # product_id = fields.Many2one('product.product', 'Product', change_default=True)
    state = fields.Selection([('cancel', 'Cancelled'), ('draft', 'Draft'),('confirmed', 'Confirmed'),('exception', 'Exception'),('done', 'Done')], 'Status', required=True, readonly=True,
            help='* The \'Draft\' status is set when the related sales order in draft status. \
                \n* The \'Confirmed\' status is set when the related sales order is confirmed. \
                \n* The \'Exception\' status is set when the related sales order is set as exception. \
                \n* The \'Done\' status is set when the sales order line has been picked. \
                \n* The \'Cancelled\' status is set when a user cancel the sales order related.', default='draft')
    tax_id = fields.Many2many('account.tax', 'sale_quotation_tax', 'quotation_line_id', 'tax_id', 'Taxes', readonly=True, states={'draft': [('readonly', False)]})
    pricelist_id = fields.Many2one('pcb.quotation.pricelist', 'Pricelist', required=False, readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, help="Pricelist for current sales order.")
    # th_weight = fields.Float('Weight', readonly=True, states={'draft': [('readonly', False)]})
    # address_allotment_id = fields.Many2one('res.partner', 'Allotment Partner', help="A partner to whom the particular product needs to be allotted.")
    product_uom_qty = fields.Float('Quantity', digits=dp.get_precision('Product UoS'), required=True, readonly=True, states={'draft': [('readonly', False)]}, default=1)
    product_uom = fields.Many2one('product.uom', 'Unit of Measure', required=True, readonly=True, states={'draft': [('readonly', False)]}, default=_get_uom_id)
    product_uos_qty = fields.Float('Quantity (UoS)', digits=dp.get_precision('Product UoS'), readonly=True, states={'draft': [('readonly', False)]}, default=1)
    product_uos = fields.Many2one('product.uom', 'Product UoS')
    discount = fields.Char('Discount (%)', digits=dp.get_precision('Discount'), readonly=True, states={'draft': [('readonly', False)]}, default=0.0)
    price_unit = fields.Float('Unit Price', required=True, digits=dp.get_precision('Product Price'), readonly=True, default=0.0)  # states={'draft': [('readonly', False)]},
    origin = fields.Char('Source Document', size=64, help="Reference of the document that generated this sales order request.")
    layer_number = fields.Many2one('cam.layer.number', 'Layer Count', required=True)
    base_type = fields.Many2one('cam.base.type', 'Raw Material', required=True)
    material_brand = fields.Many2one('cam.material.brand', 'Material Brand')
    sprocess_ids = fields.Many2many('cam.special.process', 'sale_quotation_line_special_process_rel', 'sale_quotation_line_id', 'special_process_id', 'Special Processes')
    smaterial_ids = fields.Many2many('cam.special.material', 'sale_quotation_line_special_material_rel', 'sale_quotation_line_id', 'special_material_id', 'Special Material')
    inner_copper = fields.Float('Inner Copper', required=False)
    outer_copper = fields.Float('Outer Copper', required=False)
    thickness = fields.Float('Board Thickness', required=False)
    surface = fields.Many2one('cam.surface.process', 'Surface Treatment')
    # gold_finger = fields.Boolean('Gold Finger')
    via_process = fields.Many2one('cam.via.process', 'Vias')
    silkscreen_color = fields.Many2one('cam.ink.color', 'Solder Mask Color', domain=['|', ('silk_screen', '=', True), '&', ('silk_screen', '=', False), ('text', '=', False)])
    text_color = fields.Many2one('cam.ink.color', 'Silkscreen Color', domain=['|', ('text', '=', True), '&', ('silk_screen', '=', False), ('text', '=', False)])
    min_line_cpo_width = fields.Float('Min Line cpo_Width')
    min_line_distance = fields.Float('Min Line Distnace')
    min_hole = fields.Float('Min Hole')
    line_to_hole_distance = fields.Float('Line to Hole Distance', readonly=True)
    total_holes = fields.Integer('Total Holes')
    test_points = fields.Integer('ETest Points')
    cnc = fields.Boolean('CNC')
    v_cut = fields.Boolean('V_Cut')  # 跳刀
    drilling = fields.Boolean('Laser Drilling')  # 激光钻孔
    back = fields.Boolean('Back Drilling')  # 背钻孔数
    # punch = fields.Boolean('Punch')
    # champer_gold_finger = fields.Boolean('Champer Gold Finger')
    tooling = fields.Boolean('Tooling')
    tooling_source = fields.Selection([('customer', 'Customer Provide'), ('purchaser', 'Purchaser Provide'),('stock','Stock')], string='Tooling Source', default='purchaser')
    pcb_delivery_uos = fields.Selection(AVAILABLE_DELIVERY_UOS, string="Delivery UOS",default='pcs')
    fly_probe = fields.Boolean('Fly Probe')
    request = fields.Text('Request')
    gold_thickness = fields.Float('Gold Thickness', default=0)
    gold_size = fields.Float('Gold Size', default=0)
    product_no = fields.Char('Product No', size=100, required=False, readonly=True)
    customer_file_name = fields.Char('Customer File Name', size=100, required=False)
    cpo_length = fields.Float('Length', required=False)
    cpo_width = fields.Float('Width', required=False)
    unit_size = fields.Float(compute=_compute_unit_size, string='Unit Size', type='float', digits=dp.get_precision('size'), store=True),
    size = fields.Float(compute=_compute_size, string='Size', type='float', digits=dp.get_precision('size'), store=True),
    pcs_size = fields.Float('PCS Size', required=True, digits=dp.get_precision('size'), readonly=True, states={'draft': [('readonly', False)]})
    total_size = fields.Float('Total Size', required=False, digits=dp.get_precision('size'), readonly=True, states={'draft': [('readonly', False)]})
    material_fee = fields.Float(string='Base Price Fee', required=False, digits=(16, 3), readonly=True, states={'draft': [('readonly', False)]})  # 改为基准价
    engine_fee = fields.Float('Engine Fee', required=False, digits=(16, 3), readonly=True, states={'draft': [('readonly', False)]})
    test_fee = fields.Float('Test Fee', required=False, digits=(16, 3), readonly=True, states={'draft': [('readonly', False)]})
    process_fee = fields.Float('Process Fee', required=False, digits=(16, 3), readonly=True, states={'draft': [('readonly', False)]})
    test_tooling_fee = fields.Float(string='Version Fee', required=False, digits=(16, 3), readonly=True, states={'draft': [('readonly', False)]})  # 改为版费
    film_fee = fields.Float('Film Fee', required=False, digits=(16, 3), readonly=True, states={'draft': [('readonly', False)]})
    drill_fee = fields.Float('Steel Net Fee', required=False, digits=(16, 3), readonly=True, states={'draft': [('readonly', False)]}, default=0.0)
    subtract = fields.Float('Subtract', required=True, digits=dp.get_precision('Sale Price'), readonly=True, states={'draft': [('readonly', False)]}, default=0.0)
    subtotal = fields.Float('SubTotal', rquired=True, digits=dp.get_precision('Account'), readonly=True, states={'draft': [('readonly', False)]})
    total = fields.Float('SubTotal', readonly=True, states={'draft': [('readonly', False)]}, digits=(16, 2))
    delivery_hour = fields.Integer('Delivery Hours', default=0)
    urgent = fields.Boolean('The Urgent')
    aa_partner = fields.Boolean('AA Partner')
    a_partner = fields.Boolean('A Partner')
    b_partner = fields.Boolean('B Partner')
    c_partner = fields.Boolean('C Partner')
    volume_type = fields.Selection([('prototype', 'Prototype'), ('small', 'Small Volume'), ('medium', 'Medium Volume'), ('large', 'Large Volume'), ('larger', 'Larger Volume')], 'Volume Type', required=True, default='prototype')
    set_material_fee = fields.Float('Set Base Price Fee', required=False, digits=(16, 3), default=0.0)
    set_engine_fee = fields.Float('Set Engine Fee', required=False, digits=(16, 3), default=0.0)
    set_test_fee = fields.Float('Set Test Fee', required=False, digits=(16, 3), default=0.0)
    set_process_fee = fields.Float('Set Process Fee', required=False, digits=(16, 3), default=0.0)
    set_test_tooling_fee = fields.Float('Set Version Fee', required=False, digits=(16, 3), default=0.0)
    set_film_fee = fields.Float('Set Film Fee', required=False, digits=(16, 3), default=0.0)
    set_drill_fee = fields.Float('Set Steel Net Fee', required=False, digits=(16, 3), default=0.0)
    quick_fee = fields.Float('Quick Fee', digits=dp.get_precision('Sale Price'), readonly=True, states={'draft': [('readonly', True)]})
    pcs_per_set = fields.Integer('PCS Number Per Set', states={'draft': [('readonly', False)]}, required=True, default=1)
    pcs_number = fields.Float(compute=get_pcs_number, string='PCS Number', type="integer", store=True)
    combine_number = fields.Integer('Combine Number', states={'draft': [('readonly', False)]}, default=1)
    other_fee = fields.Float('Other Fee', required=False, digits=(16, 3), readonly=True, states={'draft': [('readonly', False)]}, default=0.0)
    reorder_no_change = fields.Boolean('ReOrder No Change', ddefault=False)
    # cpo_recompute = fields.Boolean('ReCompute', default=False)
    spare_qty = fields.Float('Spare Parts Quantity', digits=dp.get_precision('Product Unit of Measure'),required=False, states={'draft': [('readonly', False)]}, default=0)
    spare_bad = fields.Boolean('Spare Parts Not OK', states={'draft': [('readonly', False)]}, default=False)
    cpo_item_number = fields.Integer('Item number')  # 拼版款数
    cpo_gold_height = fields.Float('Gold Height', digits=(16, 2), default=0)  # 金手指 长
    cpo_gold_width = fields.Float('Gold Width', digits=(16, 2), default=0)  # 金手指 宽
    cpo_gold_thick = fields.Float('Gold Thick / μ"', digits=(16, 2), default=0)  # 金手指 厚度
    cpo_gold_root = fields.Float('Gold Root', digits=(16, 2), default=0)  # 金手指 根数
    cpo_pp_number = fields.Integer('PP Number', digits=(16, 2), default=0)  # pp张数
    cpo_core_number = fields.Integer('Core Number', digits=(16, 2), default=0)  # 芯板张数
    cpo_hole_copper = fields.Float('Hole Copper', digits=(16, 2), default=0)  # 孔铜
    cpo_standard = fields.Many2one('cam.acceptance.criteria', 'Acceptance Criteria')  # 验收标准
    cpo_percentage = fields.Float('Acceptance Criteria Percentage', digits=(16, 2), readonly=True)  # 验收标准的百分比
    cpo_line_percentage = fields.Float('Line Width Spacing', digits=(16, 2), readonly=True)  # 细线百分比
    cpo_nickel_thickness = fields.Selection(NICKEL_THICKNESS, 'Nickel Thickness', default='0')  # 沉金镍厚
    increase_delivery_hour = fields.Integer('Increase Delivery Hour', readonly=True)  # 增加出货时间
    cpo_type_steel_mesh = fields.Selection(STEEL_MESH_TYPE, default='No')
    cpo_delivery_day = fields.Integer('Delivery', readonly=True, compute='_update_cpo_delivery_day', store=True)
    core_thick = fields.Float('Core Thick', digits=(16, 2))
    rogers_number = fields.Integer('Rogers Number')
    package_bool = fields.Boolean('Package Price', default=False)  # 是不是打包价
    cpo_hdi = fields.Selection([('0', '0'), ('1', '1')], string='Step HDI', default='0')  # HDI
    soft_level = fields.Selection([('Inner layer', 'Inner layer'), ('Outer layer', 'Outer layer')], string='Soft board level')  # 软板所在层次
    window_bool = fields.Boolean('Whether the soft board opens the window')
    soft_number = fields.Integer('Number of sheets')
    unquote_bool = fields.Boolean('Not Quote', default=False)

    @api.depends('increase_delivery_hour', 'delivery_hour')
    def _update_cpo_delivery_day(self):
        for x_quotation in self:
            x_quotation.update({'cpo_delivery_day': (x_quotation.increase_delivery_hour + x_quotation.delivery_hour) / 24})

    @api.model
    def create(self, vals):
        res = super(sale_quotation_line, self).create(vals)
        if not vals.get('unquote_bool') and vals.get('layer_number'):
            if vals.get('package_bool') is False:
                self.pcb_price_calculation(res.id)
            else:
                self.pcb_package_calculation(res.id)
        return res

    # 计算单PCS的面积
    def get_unit_size(self):
        (length, width, pcs) = (self.cpo_length * 0.1, self.cpo_width * 0.1, self.pcs_per_set)
        if length <= 0 or width <= 0 or pcs <= 0:
            return 0
        return length * width / pcs

    # 计算平米面积
    def get_size(self):
        length, width, qty = self.cpo_length * 0.1, self.cpo_width * 0.1, self.product_uom_qty
        if length <= 0 or width <= 0 or qty <= 0:
            return 0
        return (length * width * qty)/10000.00

    # 获取内外铜厚 默认值
    def get_outer_inner(self):
        outer = 1 if self.outer_copper <= 0.0 else self.outer_copper
        if self.layer_number.layer_number in [1, 2]:
            return outer, 0
        else:
            inner = 0.5 if self.inner_copper <= 0.0 else self.inner_copper
            return outer, inner

    # 给出改变的面积 层数是否影响相对的正常出货时间
    def get_delivery(self):
        size = self.get_size()
        items_id = self.pricelist_id.version_id.items_id.search([('layer_number', '=', self.layer_number.id)])
        times = items_id.item_size_ids.filtered(lambda x: x.max_size > size)[0]  # 获得正常交期时间
        delivery, quick, urgent = times.max_delay_hours, 1, False
        if self.quick_fee > 1 and size < 3:
            delivery = times.max_delay_hours - (((self.quick_fee - 1) / 0.2) * 24)
            quick = self.quick_fee
            urgent = True
        return delivery, quick, urgent

    # 根据金手指更改变化进行变化
    def get_gold_delivery(self):
        height, width, thick, root = self.cpo_gold_height, self.cpo_gold_width, self.cpo_gold_thick, self.cpo_gold_root
        if height <= 0 or width <= 0 or thick <= 0 or root <= 0:
            return False
        gold_id = self.pricelist_id.version_id.gold_finger_id.search([('cpo_gold_finger_thickness', '>=', thick)])
        gold_number = round(float(height) * float(width) * float(root) / 7.0, 0) + 4
        if float(height) * float(width) <= 7:
            gold_number = root + 4
        if gold_number > 300:
            raise ValidationError(_('After the gold finger is folded, the number of roots exceeds 300. Please re-enter'))
        if not gold_id:
            raise ValidationError(_('Gold finger gold thickness exceeds the range of automatic quotes'))
        gold_id = gold_id[0]
        deliver = gold_id.delivery_time_2 if self.total_size >= 3 else gold_id.delivery_time_1
        return deliver

    # 只处理 总平米数 单pcs面积 测试架的问题 - 变相留言加急情况
    @api.onchange("cpo_length", "cpo_width", "product_uom_qty", "pcs_per_set")
    def _onchange_pcb_quotation(self):
        if self.package_bool:
            return False
        total_size, pcs_size, = self.get_size(), self.get_unit_size()
        if total_size <= 0.0:
            return {'warning': {}, 'value': {}}
        tooling = False if total_size < 3.0 else True
        fly_probe = True if total_size < 3.0 else False
        delivery, quick_fee, urgent = self.get_delivery()
        if 1 <= total_size < 10:
            volume = 'small'
        elif 10 <= total_size < 50:
            volume = 'medium'
        elif 50 <= total_size:
            volume = 'large'
        else:
            volume = 'prototype'
        return self.update({'total_size': total_size, 'pcs_size': pcs_size, 'volume_type': volume, 'tooling': tooling,
                            'fly_probe': fly_probe, 'delivery_hour': delivery, 'quick_fee': quick_fee, 'urgent': urgent})

    # 验收标准变化 孔铜就重置 !! 在算法中会自动更新验收标准百分比 和 细线百分比
    @api.onchange('cpo_standard')
    def _onchange_standard(self):
        if self.package_bool:
            return False
        if self.cpo_standard.cpo_level == 2:
            return self.update({'cpo_hole_copper': 20})
        elif self.cpo_standard.cpo_level == 3:
            return self.update({'cpo_hole_copper': 25})

    # 当层数变化了 相关数据信息重置
    @api.onchange('layer_number')
    def _onchange_layer_number(self):
        if self.package_bool:
            return False
        if not self.layer_number:
            return {'warning': {}, 'value': {}}
        product_ids = self.env['product.product'].search([('layer_number', '=', self.layer_number.id)])
        if not product_ids:
            return {'warning': {
                    'title': _('Layer Number Setting is Wrong !'),
                    'message': _('Please check your layer number and product, Confirm layer number connected to a product!')}}
        items_id = self.pricelist_id.version_id.items_id.search([('layer_number', '=', self.layer_number.id)])
        norm = self.env.ref('cam.Acceptance_Criteria_II').id
        substrate = self.env.ref('cam.base_type_fr4tg135').id
        outer, inner = self.get_outer_inner()
        hole = 10 if self.min_hole <= 0.0 else self.min_hole
        thick = 1.6 if self.thickness <= 0.0 else self.thickness
        width = 100 if self.cpo_width <= 0.0 else self.cpo_width
        length = 100 if self.cpo_length <= 0.0 else self.cpo_length
        standard = norm if not self.cpo_standard else self.cpo_standard.id
        base_type = substrate if not self.base_type else self.base_type.id
        test_point = 500 if self.test_points <= 0.0 else self.test_points
        line_width = 4 if self.min_line_cpo_width <= 0.0 else self.min_line_cpo_width
        line_distance = 4 if self.min_line_distance <= 0.0 else self.min_line_distance
        holes = items_id.pore_density / 100 * width * length  # 层数变化重置
        core = max((self.layer_number.layer_number-2)/2, 1)  # 层数变化重置
        line_to_hole = items_id.inner_hole_line
        delivery, quick_fee, urgent = self.get_delivery()
        return self.update({
            'min_hole': hole, 'thickness': thick, 'cpo_width': width, 'cpo_length': length, 'inner_copper': inner,
            'outer_copper': outer, 'base_type': base_type, 'cpo_standard': standard, 'test_points': test_point,
            'min_line_cpo_width': line_width, 'min_line_distance': line_distance,
            'total_holes': holes,   # 层数变化重置
            'cpo_core_number': core,   # 层数变化重置
            'cpo_pp_number': core + 1,   # 层数变化重置
            'line_to_hole_distance': line_to_hole,   # 层数变化重置
            'delivery_hour': delivery, 'quick_fee': quick_fee, 'urgent': urgent
        })

    # 阻焊、板厚、特殊材料、特殊工艺、表面工艺、 金手指、铜厚 这些工艺变化是 可能会增加出货时间 - 少了金手指！！
    @api.onchange('surface', 'silkscreen_color', 'inner_copper', 'outer_copper', "cpo_gold_height", "cpo_gold_width",
                  'thickness', 'smaterial_ids', 'sprocess_ids', "layer_number", 'cpo_gold_thick', 'cpo_gold_root')
    def _onchange_process(self):
        if self.package_bool:
            return False
        surface, size, solder_mask, inner = self.surface, self.total_size, self.silkscreen_color, self.inner_copper
        day_time, outer, thick, sma_ids, spr_ids = 0, self.outer_copper, self.thickness, self.smaterial_ids.ids, self.sprocess_ids.ids
        item_id = self.pricelist_id.version_id.items_id.search([('layer_number', '=', self.layer_number.id)])
        if not item_id:
            return {'warning': {}, 'value': {}}
        if surface:
            surface_ids = self.env['cam.surface.process'].search([('code', 'in', ('C', 'C+D', 'C+E'))]).ids
            surface_price = self.pricelist_id.version_id.surfaceprocess_ids.search([('surface', '=', surface.id)])
            if surface.id in surface_ids:
                self.update({'gold_thickness': self.gold_thickness if self.gold_thickness != 0.0 else 1,
                             'gold_size': self.gold_size if self.gold_size != 0.0 else 30,
                             'cpo_nickel_thickness': self.cpo_nickel_thickness if self.cpo_nickel_thickness != '0' else '120'})
            else:
                self.update({'gold_thickness': 0.0, 'gold_size': 0.0, 'cpo_nickel_thickness': '0'})
            price = surface_price.filtered(lambda x:self.gold_thickness == x.thick_gold and x.price_type == 'msize')
            day_time += price.delivery_time_1 if size < 3 else price.delivery_time_2
        if solder_mask:
            solder_price = self.pricelist_id.version_id.silkscreencolor_ids.search([('silkscreen_color', '=', solder_mask.id)])
            day_time += solder_price.delivery_time_1 if size < 3 else solder_price.delivery_time_2
        if outer > 0:
            inner_time, outer_time = 0, 0
            if inner > 0:
                inner_price = item_id.item_inner_copper_ids.search([('layer_item_id', '=', item_id.id),
                                                                    ('min_inner_copper', '<=', inner),
                                                                    ('max_inner_copper', '>', inner)])
                inner_time += inner_price.delivery_time_1 if size < 3 else inner_price.delivery_time_2
            outer_price = item_id.item_outer_copper_ids.search([('layer_item_id', '=', item_id.id),
                                                                ('min_outer_copper', '<=', outer),
                                                                ('max_outer_copper', '>', outer)])
            outer_time += outer_price.delivery_time_1 if size < 3 else outer_price.delivery_time_2
            day_time += outer_time if outer_time >= inner_time else inner_time
        if thick > 0:
            thick_price = item_id.item_thickness_ids.search([('layer_item_id', '=', item_id.id),
                                                             ('min_thickness', '<', thick),
                                                             ('max_thickness', '>=', thick)])
            day_time += thick_price.delivery_time_1 if size < 3 else thick_price.delivery_time_2
        if sma_ids:
            sma_price = self.pricelist_id.version_id.smaterial_ids.search([('smaterial', 'in', sma_ids)])
            if size >= 3:
                sma_price = sma_price.filtered(lambda x: x.smaterial.id in sma_ids and x.max_size > size)
            else:
                sma_price = sma_price.filtered(lambda x: x.smaterial.id in sma_ids and x.max_size == 1)
            for x_id in sma_price:
                day_time += x_id.delivery_time
        if spr_ids:
            spe_price = self.pricelist_id.version_id.sprocess_ids.search([('sprocess', 'in', spr_ids)])
            if size >= 3:
                spe_price = spe_price.filtered(lambda x: x.sprocess.id in spr_ids and x.max_size > size)
            else:
                spe_price = spe_price.filtered(lambda x: x.sprocess.id in spr_ids and x.max_size == 1)
            for x_id in spe_price:
                day_time += x_id.delivery_time
        gold_time = self.get_gold_delivery()
        if gold_time:
            day_time += gold_time
        delivery, quick, urgent = self.get_delivery()
        return self.update({'increase_delivery_hour': day_time, 'delivery_hour': delivery, 'quick_fee': quick, 'urgent': urgent})

    # 计算PCB价格
    @api.multi
    def pcb_price_calculation(self, *args):
        line = self.browse(args[0])
        sale, discount = self.env['sale.quotation'], 0.0
        args = sale.GetNameField(line, order=True)
        # 此时层数是id号 转换 层数
        layer = self.env['cam.layer.number'].browse(args.get('layer')).layer_number
        args.update({'layer': layer})
        args = sale.GetQuotation(args)
        quick_fee = args.get('expedited').get('quick')
        ipc_fee = args.get('line_hole').get('ipc_fee')
        line_fee = args.get('line_hole').get('line_fee')
        price_id = args.get('price_id').pricelist_id.id
        if args.get('discount_id'):
            discount = max(args.get('discount_id')).discount
        args = sale.GetAllCost(args)
        film_fee = args.get('value').get('Film Cost')  # 菲林费
        engine_fee = args.get('value').get('Set Up Cost')  # 工程费
        process_fee = args.get('value').get('Process Cost')  # 工艺费
        material_fee = args.get('value').get('Cost By')   # 基准价
        test_fee = args.get('value').get('E-test Fixture Cost')  # 测试费
        test_tooling_fee = args.get('value').get('Board Price Cost')  # 板费
        drill_fee = 0
        subtotal = engine_fee + test_fee + film_fee + process_fee + test_tooling_fee + drill_fee
        if args.get('value').get('PCB Area') < 1:
            material_fee = args.get('value').get('Cost By') * args.get('value').get('PCB Area')
        # 总费用
        if args.get('soft'):
            subtotal = engine_fee + test_fee + film_fee + process_fee + test_tooling_fee + drill_fee
        subtotal += line.other_fee
        price_unit = (test_tooling_fee + film_fee + line.other_fee) / line.product_uom_qty  # 单价
        line.write({
            'material_fee': material_fee,  # 基准价
            'engine_fee': engine_fee,  # 工程
            'test_fee': test_fee,  # 测试
            'film_fee': film_fee,  # 菲林
            'process_fee': process_fee,  # 工艺
            'test_tooling_fee': test_tooling_fee,  # 版费
            'drill_fee': drill_fee,  # 钢网
            'set_material_fee': material_fee,  # 记录基准价
            'set_engine_fee': engine_fee,  # 记录工程
            'set_test_fee': test_fee,  # 记录测试
            'set_film_fee': film_fee,  # 记录菲林
            'set_process_fee': process_fee,  # 记录工艺费
            'set_test_tooling_fee': test_tooling_fee,  # 记录板费
            'set_drill_fee': drill_fee,  # 记录钢网
            'quick_fee': quick_fee,
            'pricelist_id': price_id,
            'cpo_percentage': ipc_fee,  # 自动更新百分比
            'cpo_line_percentage': line_fee,  # 会自动更新细线百分比
            'price_unit': price_unit,
            'subtotal': subtotal,
            "total": subtotal,
            "discount": discount
        })
        return True

    # PCB打包价计算
    @api.multi
    def pcb_package_calculation(self, *args):
        line = self.env['sale.quotation.line'].browse(args[0])
        sale = self.env['sale.quotation']
        currency_id = line.quotation_id.currency_id.id
        price_id = self.env['package.price.main'].search([('bale_general_bool', '=', True)])
        # 层数 基材 字符颜色
        layer, base, text = line.layer_number.layer_number, line.base_type.id, line.text_color.id  # 层数 基材 字符颜色
        mask, surface = line.silkscreen_color.id, line.surface.id  # 阻焊 表面处理
        qty, size = line.product_uom_qty, line.total_size  # 数量 面积平米
        min_aperture = line.min_hole  # 最小孔
        (inner, outer, thick) = (line.inner_copper, line.outer_copper, line.thickness)
        (length, width) = (line.cpo_length, line.cpo_width)
        min_space = line.min_line_distance  # 最小线距
        min_width = line.min_line_cpo_width  # 最小线宽
        thick_gold = line.gold_thickness
        coated = line.gold_size  # 沉金面积
        nickel = line.cpo_nickel_thickness  # 沉金镍厚
        # 确定尺寸,面积,数量符不符合
        area_dict = sale.get_area({'length': length, 'width': width, 'qty': qty, 'price_id': price_id})
        layer_dict = sale.get_layer_base({'area_id': area_dict.get('area_id'), 'layer': layer, 'base': base, 'length': length, 'width': width})
        surface_dict = sale.get_surface({'area_id': area_dict.get('area_id'),
                                         'surface': surface,
                                         'pcb_coated_area': coated,
                                         'pcb_nickel_thickness': nickel,
                                         'gold_thickness': thick_gold})
        thick_dict = sale.get_thickness({'thick': thick, 'layer_id': layer_dict.get('layer_id')})
        copper_dict = sale.get_copper({'inner': inner, 'outer': outer, 'layer_id': layer_dict.get('layer_id')})
        text_dict = sale.get_text({'text': text, 'area_id': area_dict.get('area_id')})
        mask_dict = sale.get_mask({'mask': mask, 'area_id': area_dict.get('area_id')})
        hole_line_dict = sale.get_hole_line({'width': min_width, 'space': min_space, 'aperture': min_aperture, 'area_id': area_dict.get('area_id')})
        price = (layer_dict['price'] + thick_dict['price'] + copper_dict['price'] + text_dict['price'] + mask_dict['price'] +
                 hole_line_dict['aperture_price'] + hole_line_dict['line_price'] + surface_dict['price'])
        line.update({'material_fee': price,
                     'quick_fee': 1,
                     'cpo_percentage': 1,  # 自动更新百分比
                     'cpo_line_percentage': 1})  # 会自动更新细线百分比
        price = self.get_price(price, currency_id, qty)
        line.update(price)

    @api.multi
    def get_price(self, price, currency_id, pcb_qty):
        cur_obj = self.env['res.currency']
        price_unit = price / pcb_qty
        cur = cur_obj.browse(currency_id)
        price_unit = cur.round(price_unit)
        subtotal = cur.round(price)
        return {'price_unit': price_unit, 'subtotal': subtotal, 'total': subtotal}

    def RecalculatePrice(self):
        # 通过直接修改价格进行合计 忽略工艺
        if self._context.get('Force'):
            value = {
                'test_tooling_fee': self.test_tooling_fee,
                'material_fee': self.material_fee,
                'product_uom_qty': self.product_uom_qty,
                'process_fee': self.process_fee,
                'engine_fee': self.engine_fee,
                'film_fee': self.film_fee,
                'drill_fee': self.drill_fee,
                'test_fee': self.test_fee,
                'other_fee': self.other_fee,
                'subtract': self.subtract,
            }
            x_cost = self.test_tooling_fee if self.test_tooling_fee > 0 else self.material_fee
            qty = self.product_uom_qty
            price_unit = x_cost / qty
            subtotal = self.process_fee + self.engine_fee + self.film_fee + self.drill_fee + self.test_fee + self.other_fee + (price_unit * qty)
            total = subtotal - self.subtract
            if total <= 0:
                raise ValidationError(_('The calculated total is <= 0'))
            value.update({'price_unit': price_unit, 'subtotal': subtotal, 'total': total})
            context = dict(self._context)
            context.update({'default_total': total})
            self.with_context(context).write(value)
            # return self.update(value)
        # 通过修改工艺之后 重新计算价格 - 常规
        elif not self.package_bool:
            self.pcb_price_calculation(self.id)
        # 打包价
        else:
            self.pcb_package_calculation(self.id)
        return True

    @api.multi
    def write(self, vals):
        return super(sale_quotation_line, self).write(vals)

    # 直接被前端接口调用 - 仅仅是作用在当有PCBA和PCB单存在的时候 才被调用
    def GetQuoteLineUpdate(self):
        order_line = self.order_id.order_line
        value = {
            'product_uom_qty': order_line.product_uom_qty,
            'cpo_length': order_line.pcb_length,
            'cpo_width': order_line.pcb_width,
            'thickness': order_line.pcb_thickness,
        }
        self.write(value)
        self.pcb_price_calculation(self.id)
        return True
