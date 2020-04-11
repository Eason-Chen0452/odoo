# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class product_pricelist(models.Model):
    _name = 'product.pricelist'
    _inherit = 'product.pricelist'
    
    def _get_currency(self):
        comp = self.env['res.users'].browse(self.env.uid).company_id
        if not comp:
            comp_id = self.env['res.company'].search([])[0]
            comp = self.env['res.company'].browse(comp_id)
        return comp.currency_id.id
    
    def get_pricelist_pcbone(self, ids, pricelist_type, currency_id):
        if not currency_id:
            currency_id = self._get_currency()
        rows = self.search([('currency_id', '=', currency_id)]).ids
        res = self.browse(rows)
        if isinstance(res, list):
            res = res[0]
        return res


#  特定产品规格 进行 特定产品的折扣
class SpecificProductOffers(models.Model):
    _name = 'specific.product.offers'
    _description = 'Specific Product Offers'

    use_bool = fields.Boolean('Take Effect', default=False, index=True)
    product = fields.Selection([("PCB", "PCB"),
                                ("PCBA", "PCBA"),
                                ("Stencil", "Stencil")], 'Product', default="PCB")
    discount = fields.Float('Discount %', digits=(16, 2))
    args_bool = fields.Boolean("Specifying Parameters", default=False)
    range_bool = fields.Boolean("Specifying Range", default=False)
    length_1 = fields.Float('Length', digits=(16, 2))
    length_2 = fields.Float('Length', digits=(16, 2))
    width_1 = fields.Float('Width', digits=(16, 2))
    width_2 = fields.Float('Width', digits=(16, 2))
    outer_1 = fields.Float('Outer Copper Thickness', digits=(16, 2))
    outer_2 = fields.Float('Outer Copper Thickness', digits=(16, 2))
    inner_1 = fields.Float('Inner Copper Thickness', digits=(16, 2))
    inner_2 = fields.Float('Inner Copper Thickness', digits=(16, 2))
    qty_1 = fields.Integer('Quantity')
    qty_2 = fields.Integer('Quantity')
    thick_1 = fields.Float('Plate Thickness')
    thick_2 = fields.Float('Plate Thickness')
    combine_1 = fields.Integer('Number Imposition')
    combine_2 = fields.Integer('Number Imposition')
    # volume_ids = fields.Many2many('cam.volume.level', string='Volume level')
    mask_id = fields.Many2one('cam.ink.color', string='Solder Mask Color', domain=[('silk_screen', '=', True)])
    text_id = fields.Many2one('cam.ink.color', string='Text Color', domain=[('text', '=', True)])
    surface_ids = fields.Many2many('cam.surface.process', string='Surface process')
    via_ids = fields.Many2many('cam.via.process', string='Via process')
    process_ids = fields.Many2many('cam.special.process', string='Special process')
    material_ids = fields.Many2many('cam.special.material', string='Special material')
    # material_brand_ids = fields.Many2many('cam.material.brand', string='Material brand')
    layer_ids = fields.Many2many('cam.layer.number', string='Layer number')
    base_ids = fields.Many2many('cam.base.type', string='Base type')
    ipc_ids = fields.Many2many('cam.acceptance.criteria', string='Acceptance criteria')
    state = fields.Selection([('Draft', 'Draft'),
                              ('Take Effect', 'Take Effect'),
                              ('Lapse', 'Lapse'),
                              ('Withdraw', 'Withdraw'),
                              ('Cancel', 'Cancel')], default='Draft', string='Status')
    time_bool = fields.Boolean('Set Valid Time Period')
    start_time = fields.Date('Start Time')
    end_time = fields.Date('End Time')

    def PlanEffective(self):
        self.write({'use_bool': True, 'state': 'Take Effect'})





