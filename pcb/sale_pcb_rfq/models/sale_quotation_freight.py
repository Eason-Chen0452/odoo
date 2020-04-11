# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

FREIGHT_REGION = [
        ('1', 'One district'),
        ('2', 'Two district'),
        ('3', 'Three district'),
        ('4', 'Four district'),
        ('5', 'Fives district'),
        ('6', 'Six district'),
        ('7', 'Seven district'),
        ('8', 'Eight district'),
        ('9', 'Nine district'),
    ]


class cpo_freight_region(models.Model):
    _name = 'cpo.freight.region'
    _order = 'cpo_region'

    cpo_region = fields.Selection(FREIGHT_REGION, 'Freight Region')
    cpo_country = fields.Many2many('res.country', string='Country', compute='_depends_country', store=True)
    cpo_pcb_freight_id = fields.One2many('cpo.pcb.freight', 'cpo_freight_region_id', 'Country')
    cpo_pcb_weight_breakdown_id = fields.One2many('cpo.pcb.weight.breakdown', 'cpo_freight_region_id', 'Weight Breakdown')
    cpo_pcb_weight_breakdown_range_id = fields.One2many('cpo.pcb.weight.breakdown.range', 'cpo_freight_region_id', 'Weight Breakdown Range')

    @api.depends('cpo_pcb_freight_id', 'cpo_pcb_freight_id.cpo_country_id')
    def _depends_country(self):
        for x_id in self:
            freight_ids = self.env['cpo.pcb.freight'].search([('cpo_freight_region_id', '=', x_id.id)])
            freight_ids = [x.cpo_country_id.id for x in freight_ids]
            x_id.cpo_country = [(6, 0, freight_ids)]


# 运费 - 公式
class cpo_pcb_freight(models.Model):
    _name = 'cpo.pcb.freight'
    _order = 'cpo_country_id'

    cpo_country_id = fields.Many2one('res.country', string='country', index=True)
    cpo_freight_region_id = fields.Many2one('cpo.freight.region')
    cpo_size = fields.Float('Size/㎡', digits=(16, 5))  # 平米数
    cpo_thickness = fields.Float('Thickness/mm', digits=(16, 2))  # 板厚
    cpo_oz = fields.Float('Copper/OZ', digits=(16, 2))  # 铜厚
    cpo_oz_kg = fields.Float('OZ/kg', digits=(16, 2))  # 每OZ/kg
    cpo_weight = fields.Float('Kg/㎡', digits=(16, 2))  # 首重量

    @api.onchange('cpo_country_id')
    def onchange_check_up_cpo_country_id(self):
        if self.cpo_country_id:
            cpo_country_id = self.search([('cpo_country_id', '=', self.cpo_country_id.id)])
            if len(cpo_country_id) >= 1:
                raise ValidationError(_('The country’s shipping has been created'))
            self.update({'cpo_size': 1, 'cpo_thickness': 1.6, 'cpo_oz': 1, 'cpo_weight': 3.5, 'cpo_oz_kg': 0.15})

    @api.model
    def cpo_create_freight(self, *args):
        args = args[0]
        # 平米 钢网 内铜 外铜
        meter, frame, inner, outer = args.get('meter'), args.get('frame'), args.get('inner'), args.get('outer')
        # 板厚 层数 运费
        thick, layer, freight_fee, country = args.get('thick'), args.get('layer'), 0, args.get('country')
        address_id = self.env['res.country'].search([('code', '=', country)]).id
        if not country and not args.get('country_id'):
            address_id = args.get('address').country_id.id
        freight = self.search([('cpo_country_id', '=', address_id)])
        if freight and address_id:
            cpo_size = freight.cpo_size  # 面积
            cpo_thick = freight.cpo_thickness  # 板厚
            cpo_oz = freight.cpo_oz  # 铜厚 - 无内外之分 - 减去本身
            cpo_weight = freight.cpo_weight  # 重量
            cpo_oz_kg = freight.cpo_oz_kg  # OZ/kg
            if cpo_size != 0 and cpo_thick != 0 and cpo_oz != 0 and cpo_weight != 0 and cpo_oz_kg != 0:
                # 单层 只有一面是有外铜厚
                if int(layer) <= 2:
                    oz_number = max((float(outer) - cpo_oz), 0)
                    oz_weight = oz_number * cpo_oz_kg
                else:
                    x_layer_number = max((int(layer) - 2), 0)
                    oz_inner_number = x_layer_number * (float(inner) if inner else 0)
                    oz_outer_number = (int(layer) - x_layer_number) * float(outer)
                    oz_number = oz_inner_number + oz_outer_number - cpo_oz
                    oz_weight = oz_number * cpo_oz_kg
                thickness_weight = cpo_weight / cpo_thick * float(thick) / cpo_size
                weight = oz_weight + thickness_weight * float(meter)
                weight = (int(weight) + 1) if (weight - int(weight)) > 0.5 else int(weight) + 0.5
                if frame:
                    frame = frame.replace(' ', '_')
                x_kg = self.env['pcb.quotation.pricelist.other.steel.mesh'].search([('type_steel_mesh', '=', frame)])
                weight += x_kg.cpo_frame_kg
                region_id = freight.cpo_freight_region_id.id
                freight_id = freight.cpo_freight_region_id.cpo_pcb_weight_breakdown_id.search([('cpo_freight_region_id', '=', region_id),
                                                                                               ('weight_pcb', '=', weight)])
                freight_fee = freight_id.cpo_freight_fee
                if not freight_fee or freight_fee == 0:
                    breakdown_id = freight.cpo_freight_region_id.cpo_pcb_weight_breakdown_range_id.search([('cpo_freight_region_id', '=', region_id),
                                                                                                           ('weight_pcb_range_1', '<', weight),
                                                                                                           ('weight_pcb_range_2', '>=', weight)])
                    breakdown_fee = breakdown_id.cpo_freight_range_fee
                    weight = int(weight) + 1 if type(weight) is float else weight
                    freight_fee = breakdown_fee * weight
                return freight_fee
            else:
                return freight_fee
        # 钢网独立
        elif args.get('weight') and args.get('country_id'):
            weight, country = args.get('weight'), args.get('country_id')
            if type(country) is unicode:
                address_id = self.env['res.country'].search([('code', '=', country)]).id
            weight = int(weight) + 1 if weight - int(weight) >= 0.5 else int(weight)
            if not address_id and type(country) is not unicode:
                address_id = args.get('country_id').country_id.id
            freight = self.search([('cpo_country_id', '=', address_id)])
            region_id = freight.cpo_freight_region_id.id
            freight_id = freight.cpo_freight_region_id.cpo_pcb_weight_breakdown_id.search([('cpo_freight_region_id', '=', region_id),
                                                                                           ('weight_pcb', '=', weight)])
            return freight_id.cpo_freight_fee
        else:
            return freight_fee


# 重量明细
class cpo_pcb_weight_breakdown(models.Model):
    _name = 'cpo.pcb.weight.breakdown'
    _order = 'weight_pcb'

    cpo_freight_region_id = fields.Many2one('cpo.freight.region')
    weight_pcb = fields.Float('Weight Breakdown', digits=(16, 2), required=True)
    cpo_freight_fee = fields.Float('Freight price/$', digits=(16, 2), required=True)  # 运费价格

    @api.onchange('weight_pcb')
    def onchange_check_weight_pcb(self):
        if self.weight_pcb:
            weight_pcb_ids = self.search([('weight_pcb', '=', self.weight_pcb)])
            if len(weight_pcb_ids) >= 1:
                raise ValidationError(_('The weight detail to increase without creating'))


# 超出重量
class cpo_pcb_weight_breakdown_range(models.Model):
    _name = 'cpo.pcb.weight.breakdown.range'
    _order = 'weight_pcb_range_1'

    weight_pcb_range_1 = fields.Float('Weight Breakdown range', digits=(16, 2), required=True)
    weight_pcb_range_2 = fields.Float('Weight Breakdown range', digits=(16, 2), required=True)
    cpo_freight_range_fee = fields.Float('Freight price', digits=(16, 2), required=True)  # 运费价格
    cpo_freight_region_id = fields.Many2one('cpo.freight.region')
