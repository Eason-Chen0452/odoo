# -*- coding: utf-8 -*-
"""
    新增加写cam的东西
"""
from odoo import api, fields, models, SUPERUSER_ID, tools, netsvc

AVAILABLE_PRICE_TYPE = [
    ('item', 'Item'),
    ('csize', 'Size(cm²)'),
    ('msize', 'Size(㎡)'),
    ('pcs', 'PCS'),
    ('set', 'SET'),
]


# 阻焊颜色
class cam_ink_color(models.Model):
    _name = 'cam.ink.color'
    _inherit = 'cam.ink.color'

    english_name = fields.Char('English name', size=64, translate=False, index=True)


# 表面工艺
class cam_surface_process(models.Model):
    _name = 'cam.surface.process'
    _inherit = 'cam.surface.process'

    english_name = fields.Char('English name', size=64, translate=False, index=True)


# 过孔工艺
class cam_via_process(models.Model):
    _name = 'cam.via.process'
    _inherit = 'cam.via.process'

    english_name = fields.Char('English name', size=64, translate=False, index=True)


# 特殊工艺
class cam_special_process(models.Model):
    _name = 'cam.special.process'
    _inherit = 'cam.special.process'

    english_name = fields.Char('English name', size=64, translate=False, index=True)
    cpo_boolean = fields.Boolean('This process is relatively complicated', default=False)


# 特殊材料
class cam_special_material(models.Model):
    _name = 'cam.special.material'
    _inherit = 'cam.special.material'

    english_name = fields.Char('English name', size=64, translate=False, index=True)


# 基材类型
class cam_base_type(models.Model):
    _name = 'cam.base.type'
    _inherit = 'cam.base.type'

    english_name = fields.Char('English name', size=64, translate=False, index=True)


# 罗杰斯芯板 板厚设置
class cam_rogers_setting(models.Model):
    _name = 'cam.rogers.setting'
    _description = 'CAM Rogers Setting'
    _order = 'material, core_thick'

    material = fields.Many2one('cam.base.type', 'Material')
    core_thick = fields.Float('Core Thickness/mil', digits=(16, 2))
    thick_1 = fields.Float('1OZ Finished Thickness/mm', digits=(16, 2))
    thick_2 = fields.Float('2OZ Finished Thickness/mm', digits=(16, 2))


# 类型增加金手指 - 厚度 - 独立
class cam_gold_finger(models.Model):
    _name = 'cam.gold.finger'
    _description = 'Gold Finger'
    _order = 'cpo_gole_thickness'

    name = fields.Char('name', size=64, translate=True, readonly=True)
    cpo_gole_thickness = fields.Float(digits=(16, 2), string='gole thickness/μ"')
    cam_root_number_id = fields.Many2many('cam.root.number', string='Root Number')
    memo = fields.Text('Memo')
    active = fields.Boolean('Active', default=True)

    @api.onchange('cpo_gole_thickness')
    def onchange_cpo_gole_thickness(self):
        if self.cpo_gole_thickness:
            self.name = str(self.cpo_gole_thickness) + 'μ"'


# 类型增加金手指 - 根数 - 独立
class cam_root_number(models.Model):
    _name = 'cam.root.number'
    _description = 'Root Number'
    _order = 'cpo_root_number'

    name = fields.Char('name', size=64, translate=True, readonly=True)
    cpo_root_number = fields.Integer('Root number')
    active = fields.Boolean('Active', default=True)

    @api.onchange('cpo_root_number')
    def onchange_name(self):
        if self.cpo_root_number:
            self.name = str(self.cpo_root_number) + 'branch'


# 验收标准
class cam_acceptance_criteria(models.Model):
    _name = 'cam.acceptance.criteria'
    _description = 'Acceptance Criteria'
    _order = 'cpo_level'

    name = fields.Char('name', size=64, translate=True, readonly=True)
    cpo_level = fields.Integer('Level')
    english_name = fields.Char('English name', size=64, translate=True)
    memo = fields.Text('Memo')
    active = fields.Boolean('Active', default=True)

    @api.onchange('cpo_level')
    def onchange_name(self):
        if self.cpo_level:
            self.name = 'IPC Class ' + str(self.cpo_level)


# 钢网 - 尺寸
class cam_laser_steel_mesh_size(models.Model):
    _name = 'cam.laser.steel.mesh.size'
    _description = 'Laser steel mesh size'

    name = fields.Char('name', size=64, translate=True, index=True, readonly=True)
    product_ids = fields.One2many("product.product", 'stencil_id', string='Product IDS', readonly=True)
    stencil_size_1 = fields.Float('Steel mesh size/MM', digits=(16, 2), required=True)
    stencil_size_2 = fields.Float('Steel mesh size/MM', digits=(16, 2), required=True)
    effective_size_1 = fields.Float('Effective size/MM', digits=(16, 2), required=True)
    effective_size_2 = fields.Float('Effective size/MM', digits=(16, 2), required=True)
    steel_mesh_thickness_id = fields.Many2many('cam.steel.mesh.thickness', string='Steel mesh thickness')
    active = fields.Boolean('Active', default=True)

    @api.onchange('stencil_size_1', 'stencil_size_2', 'effective_size_1', 'effective_size_2')
    def _onchange_stencil_effective(self):
        stencil_1, stencil_2 = self.stencil_size_1, self.stencil_size_2
        effective_1, effective_2 = self.effective_size_1, self.effective_size_2
        if stencil_1 > 0 and stencil_2 > 0 and effective_1 > 0 and effective_2 > 0:
            name = str(stencil_1) + '*' + str(stencil_2) + '/' + str(effective_1) + '*' + str(effective_2)
            return self.update({'name': name})


# 钢网 - 厚度
class cam_steel_mesh_thickness(models.Model):
    _name = 'cam.steel.mesh.thickness'
    _description = 'Steel mesh thickness'

    name = fields.Float('Steel mesh thickness/MM', digits=(16, 2), required=True)
    active = fields.Boolean('Active', default=True)

