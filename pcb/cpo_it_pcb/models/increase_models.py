# -*- coding: utf-8 -*-
"""
    在models中 进行新的字段增加
"""
from odoo import models, fields, api, _
import odoo.addons.decimal_precision as dp

AVAILABLE_PRICE_TYPE = [
    ('item', 'Item'),
    ('csize', 'Size(cm²)'),
    ('msize', 'Size(㎡)'),
    ('pcs', 'PCS'),
    ('set', 'SET'),
]


# 层数的规则
class increase_pcb_quotation_pricelist_layer_item(models.Model):
    _name = 'pcb.quotation.pricelist.layer.item'
    _inherit = 'pcb.quotation.pricelist.layer.item'

    inner_hole_line = fields.Float('Inner hole to line', digits=(16, 2))  # 内层孔到线
    inner_hole_line_fee = fields.Float('Inner hole to line fee', digits=(16, 2))
    pore_density = fields.Float('Pore density', digits=(16, 2))  # 孔密度
    pore_density_fee = fields.Float('Pore density fee', digits=(16, 2))
    core_fee = fields.Float('Core fee', digits=(16, 2))  # 芯板费用
    pp_fee = fields.Float('PP fee', digits=(16, 2))  # PP费用
    moq_pcs_fee = fields.Float('MOQ', digits=(16, 2))  # MOQ单pcs收费
    item_rogers_ids = fields.One2many('pcb.rogers.material', 'layer_item_id', 'Price List of Inner Copper')


# 层数里面 版费增加 基准价
class increase_pcb_quotation_pricelist_layer_size(models.Model):
    _name = "pcb.quotation.pricelist.layer.size"
    _inherit = "pcb.quotation.pricelist.layer.size"

    # 基准价
    cpo_benchmark_fee_type = fields.Selection(AVAILABLE_PRICE_TYPE, 'Benchmark Fee Type', required=False, default='item')
    cpo_benchmark_fee = fields.Float(string='Benchmark Unit Price', required=False,
                                     digits=dp.get_precision('Product Price'), default=0.0)
    # 工程费超出费用
    engineering_fee_exceeding_type = fields.Float(string='Engineering Fee Exceeding type', required=False,
                                                  digits=dp.get_precision('Product Price'), default=0.0)
    engineering_fee_exceeding = fields.Float(string='Engineering Fee Exceeding', required=False,
                                             digits=dp.get_precision('Product Price'), default=0.0)
    cpo_film_upper_limit_fee = fields.Float(string='Film Upper Limit Fee', required=False,
                                            digits=dp.get_precision('Product Price'), default=0.0)


# 层数里面版费的基材 增加 基准价
class increase_pcb_quotation_pricelist_size_type(models.Model):
    _name = 'pcb.quotation.pricelist.size.type'
    _inherit = 'pcb.quotation.pricelist.size.type'

    # 工程费超出费用
    engineering_fee_exceeding_type = fields.Float(string='Engineering Fee Exceeding type', required=False,
                                                  digits=dp.get_precision('Product Price'), default=0.0)
    engineering_fee_exceeding = fields.Float(string='Engineering Fee Exceeding', required=False,
                                             digits=dp.get_precision('Product Price'), default=0.0)
    cpo_benchmark_fee_type = fields.Selection(AVAILABLE_PRICE_TYPE, 'Benchmark Fee Type', required=False,
                                              default='item')
    cpo_benchmark_fee = fields.Float(string='Benchmark Unit Price', required=False,
                                     digits=dp.get_precision('Product Price'), default=0.0)
    cpo_film_upper_limit_fee = fields.Float(string='Film Upper Limit Fee', required=False,
                                            digits=dp.get_precision('Product Price'), default=0.0)


# 表面工艺的规则
class increase_pcb_quotation_pricelist_surface_process(models.Model):
    _name = "pcb.quotation.pricelist.surface.process"
    _inherit = "pcb.quotation.pricelist.surface.process"
    # _order = "thick_gold"

    thick_gold = fields.Float('Thick gold', digits=(16, 2), required=False, default=0)
    delivery_time_1 = fields.Integer('S<3/Increase delivery time (H)')
    delivery_time_2 = fields.Integer('S>=3/Increase delivery time (H)')
    extra_markup = fields.Float('Extra markup', digits=(16, 2))
    _sql_constraints = [
        ('surface_maxsize_uniq', 'unique(price_version_id, surface, max_size, thick_gold)',
         'Surface Process and Max Size and Thick gold must be unique per pricelist!'),
    ]


# 特殊材料规则
class increase_pcb_quotation_pricelist_special_material(models.Model):
    _name = "pcb.quotation.pricelist.special.material"
    _inherit = "pcb.quotation.pricelist.special.material"
    # _order = "min_size"

    min_size = fields.Float('Min Size', digits=(16, 2), required=True, default=0)
    delivery_time = fields.Integer('Increase delivery time (H)')


# 特殊工艺规则
class increase_pcb_quotation_pricelist_special_process(models.Model):
    _name = "pcb.quotation.pricelist.special.process"
    _inherit = "pcb.quotation.pricelist.special.process"
    # _order = "min_size"

    min_size = fields.Float('Min Size', digits=(16, 2), required=True, default=0)
    percentage = fields.Float('Percentage', digits=(16, 2), default=0)
    delivery_time = fields.Integer('Increase delivery time (H)')

    # 检查 当特殊工艺是埋盲孔时 进行进行告知到别处设置
    @api.onchange('sprocess')
    def _checking_sprocess(self):
        if self.sprocess:
            blind_via = self.env.ref('cam.sf_blind_via').id
            buried = self.env.ref('cam.sf_buried_blind_via').id
            if self.sprocess.id in [blind_via, buried]:
                self.sprocess = None
                return {
                    'warning': {
                        'title': _("Tips"),
                        'message': _("The blind hole or burying of your choice should be set in the ‘Blind hole’ section."),
                    },
                }


# 附表规则
class increase_pcb_quotation_pricelist_version(models.Model):
    _name = 'pcb.quotation.pricelist.version'
    _inherit = 'pcb.quotation.pricelist.version'

    gold_finger_id = fields.One2many('pcb.quotation.pricelist.gold.finger', 'price_version_id', 'Price List of Gold Finger')
    with_frame_ids = fields.One2many('pcb.quotation.pricelist.other.steel.mesh', 'price_version_id', 'Steel mesh')
    soft_hard_id = fields.One2many('pcb.soft.hard', 'price_version_id', 'Soft Hard')


# 其他表中的规则 增加 孔铜
class increase_pcb_quotation_pricelist_other(models.Model):
    _name = "pcb.quotation.pricelist.other"
    _inherit = 'pcb.quotation.pricelist.other'

    other_hole_copper_ids = fields.One2many('pcb.quotation.pricelist.other.hole.copper', 'price_other_fee_id', 'Hole Copper Thickness')
    other_acceptance_criteria_ids = fields.One2many('pcb.quotation.pricelist.acceptance.criteria', 'price_other_fee_id', 'Acceptance Criteria')


# PCB里使用的钢网
class pcb_quotation_pricelist_other_steel_mesh(models.Model):
    _name = 'pcb.quotation.pricelist.other.steel.mesh'
    _description = 'Steel mesh'
    _order = 'type_steel_mesh'

    STEEL_MESH_TYPE = [
        ('With_Frame', 'With Frame'),
        ('Without_Frame', 'Without Frame'),
        ('No', 'No')
    ]

    price_version_id = fields.Many2one('pcb.quotation.pricelist.version', 'Price List Versions', required=True,
                                         index=True, ondelete='cascade')
    type_steel_mesh = fields.Selection(STEEL_MESH_TYPE, default='No')
    cpo_frame_fee = fields.Float('Steel net fee', digits=(16, 2))
    cpo_frame_kg = fields.Float('Steel mesh weight / KG', digits=(16, 2))


# 孔铜规则
class pcb_quotation_pricelist_other_hole_copper(models.Model):
    _name = 'pcb.quotation.pricelist.other.hole.copper'
    _description = 'Hole Copper Thickness'
    _order = 'price_other_fee_id, hole_copper_thick'

    price_other_fee_id = fields.Many2one('pcb.quotation.pricelist.other', 'Other Fee of Price List', required=True,
                                         index=True, ondelete='cascade')
    hole_copper_thick = fields.Float('Min Hole Copper Thick', digits=(16, 2))  # 孔铜厚度
    hole_copper_thick1 = fields.Float('Max Hole Copper Thick', digits=(16, 2))
    hole_copper_fee = fields.Float('Hole Copper Fee', digits=(16, 2))  # 孔铜费用
    hole_copper_type = fields.Selection(AVAILABLE_PRICE_TYPE, 'Hole Copper Type', required=False, default='item')


# 验收标准
class pcb_quotation_pricelist_acceptance_criteria(models.Model):
    _name = 'pcb.quotation.pricelist.acceptance.criteria'
    _description = 'Acceptance Criteria'
    _order = 'price_other_fee_id, acceptance_criteria_id'

    price_other_fee_id = fields.Many2one('pcb.quotation.pricelist.other', 'Other Fee of Price List', required=True,
                                         index=True, ondelete='cascade')
    acceptance_criteria_id = fields.Many2one('cam.acceptance.criteria', 'Acceptance Criteria', index=True, ondelete='cascade')
    price = fields.Float('Acceptance Criteria Fee', digits=(16, 2))  # 验收标准费用
    price_class = fields.Selection([('l', 'L'), ('%', '%')], 'Price Class', default='l')
    acceptance_criteria_type = fields.Selection(AVAILABLE_PRICE_TYPE, 'Acceptance Criteria Type', required=False, default='item')


# 金手指规则表
class pcb_quotation_pricelist_gold_finger(models.Model):
    _name = 'pcb.quotation.pricelist.gold.finger'
    _description = 'Price List of Gold Finger'
    _order = 'cpo_gold_finger_thickness, price_version_id'

    name = fields.Char('name', size=64, translate=True, index=True, readonly=True)
    price_version_id = fields.Many2one('pcb.quotation.pricelist.version', 'Price List Versions', required=True,
                                       index=True, ondelete='cascade')
    cpo_gold_finger_number_id = fields.One2many('pcb.quotation.pricelist.gold.finger.number', 'cpo_gold_finger_id', 'Price List of Gold Finger Number')
    cpo_gold_finger_fee = fields.Float('Gold Finger Fee', digits=(16, 4))
    cpo_gold_finger_thickness = fields.Float('Gold Finger Thickness', digits=(16, 2))
    cpo_min_fee = fields.Float('MOQ > /Min Fee', digits=(16, 2), default=50)
    cpo_max_fee = fields.Float('MOQ <= /Min Fee', digits=(16, 2), default=100)
    cpo_cost_fee = fields.Float('Unit costs', digits=(16, 4), default=0.3985)
    cpo_profit_ratio = fields.Float('Profit ratio/%', digits=(16, 2), default=25)
    cpo_moq = fields.Float(string='MOQ/μ"', digits=(16, 2), default=20)
    delivery_time_1 = fields.Integer('S<3/Increase delivery time (H)', default=24)
    delivery_time_2 = fields.Integer('S>=3/Increase delivery time (H)', default=48)

    @api.onchange('cpo_gold_finger_thickness')
    def onchange_cpo_gole_thickness(self):
        if self.cpo_gold_finger_thickness:
            self.name = str(self.cpo_gold_finger_thickness) + 'μ"'


class pcb_quotation_pricelist_gold_finger_number(models.Model):
    _name = 'pcb.quotation.pricelist.gold.finger.number'
    _description = 'Price List of Gold Finger Number'
    _order = 'cpo_gold_finger_number, cpo_gold_finger_fee'

    cpo_gold_finger_id = fields.Many2one('pcb.quotation.pricelist.gold.finger', required=True, index=True, ondelete='cascade')
    cpo_gold_finger_number = fields.Many2one('cam.root.number', string='Gold Finger Number')
    cpo_gold_finger_fee = fields.Float('Gold Finger Fee', digits=(16, 4))


# 板厚增加字段 - 交期相应增加
class inherit_pcb_quotation_pricelist_layer_thickness(models.Model):
    _name = 'pcb.quotation.pricelist.layer.thickness'
    _inherit = 'pcb.quotation.pricelist.layer.thickness'

    delivery_time_1 = fields.Integer('S<3/Increase delivery time (H)')
    delivery_time_2 = fields.Integer('S>=3/Increase delivery time (H)')


# 外铜厚增加字段 - 交期相应增加
class inherit_pcb_quotation_pricelist_layer_outer_copper(models.Model):
    _name = 'pcb.quotation.pricelist.layer.outer.copper'
    _inherit = 'pcb.quotation.pricelist.layer.outer.copper'

    delivery_time_1 = fields.Integer('S<3/Increase delivery time (H)')
    delivery_time_2 = fields.Integer('S>=3/Increase delivery time (H)')
    project_fee = fields.Float('Add Project costs', digits=(16, 2))


# 内铜厚增加字段 - 交期相应增加
class inherit_pcb_quotation_pricelist_layer_inner_copper(models.Model):
    _name = "pcb.quotation.pricelist.layer.inner.copper"
    _inherit = 'pcb.quotation.pricelist.layer.inner.copper'

    delivery_time_1 = fields.Integer('S<3/Increase delivery time (H)')
    delivery_time_2 = fields.Integer('S>=3/Increase delivery time (H)')


# 阻焊颜色增加字段 - 交期相应增加
class inherit_pcb_quotation_pricelist_silkscreen_color(models.Model):
    _name = 'pcb.quotation.pricelist.silkscreen.color'
    _inherit = 'pcb.quotation.pricelist.silkscreen.color'

    delivery_time_1 = fields.Integer('S<3/Increase delivery time (H)')
    delivery_time_2 = fields.Integer('S>=3/Increase delivery time (H)')


# 钢网 - 独立
class laser_steel_mesh_price(models.Model):
    _name = 'laser.steel.mesh.price'
    _description = 'Laser steel mesh price'

    name = fields.Char('Quantity', size=64, translate=True, index=True, readonly=True)
    quantity_1 = fields.Integer('Quantity', required=True, index=True)
    quantity_2 = fields.Integer('Quantity', required=True, index=True)
    cpo_delivery = fields.Integer('Delivery period/H')  # 交期
    cpo_price = fields.Float('Price', digits=(16, 2), required=True)
    cpo_weight = fields.Float('One slice weight/KG', digits=(16, 2), required=True)
    steel_size_id = fields.Many2one('cam.laser.steel.mesh.size', string='Steel mesh size', index=True, required=True, ondelete='cascade')
    steel_thickness_id = fields.Many2many('cam.steel.mesh.thickness', index=True)

    @api.onchange('quantity_1', 'quantity_2')
    def _onchange_quantity_name(self):
        if self.quantity_1 >= 0 and self.quantity_2 > 0:
            name = str(self.quantity_1) + '-' + str(self.quantity_2) + u' Quantity'
            return self.update({'name': name})


# ROGERS
class Rogers_Material_PCB(models.Model):
    _name = 'pcb.rogers.material'
    _description = 'Rogers Material'
    _order = 'id'

    layer_item_id = fields.Many2one('pcb.quotation.pricelist.layer.item', 'Price List of Board Material', ondelete='cascade')
    base_type = fields.Many2one('cam.base.type', 'Copper Base Tye', index=True)
    project_fee = fields.Float('Add Project costs', digits=(16, 2))
    price = fields.Float('Price/㎡', required=True, digits=(16, 2), default=0.0)
    core_thick = fields.Float('Core plate thickness', digits=(16, 2))
    delivery = fields.Integer('Increase delivery')


# 软硬结合
class Soft_Hard_PCB(models.Model):
    _name = 'pcb.soft.hard'
    _description = 'Soft Hard'
    _order = 'total_layers, id'

    price_version_id = fields.Many2one('pcb.quotation.pricelist.version', 'Price List Versions', required=True,
                                       index=True, ondelete='cascade')
    total_layers = fields.Integer('Total Layers')
    soft_inner = fields.Float('Engineering Soft Inner /m²', digits=(16, 2))
    soft_outer = fields.Float('Engineering Soft Outer /m²', digits=(16, 2))
    soft_board = fields.Float('Board Soft / S<0.2 m²', digits=(16, 2))
    soft_board2 = fields.Float('Board Soft / 0.2<S<3 m²', digits=(16, 2))
    soft_board3 = fields.Float('Board Soft / 3<S<10 m²', digits=(16, 2))
    delivery = fields.Integer('Increase delivery / S<1m²')
    delivery2 = fields.Integer('Increase delivery / S<3m²')
    delivery3 = fields.Integer('Increase delivery / S<10m²')


