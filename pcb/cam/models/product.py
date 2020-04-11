# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.tools.translate import _


class product_template(models.Model):
    _inherit="product.template"

    type = fields.Selection([
        ('pcb', 'PCB Product'),
        ('material', 'PCB Materials'),
        ('tool', 'Tools'),
        ('office', 'Office supplies'),
        ('labour', 'Labour protection'),
        ('product','Stockable Product'),
        ('consu', 'Consumable'),
        ('service', 'Service')], string='Product Type', required=False, help="Consumable: Will not imply stock management for this product. \nStockable product: Will imply stock management for this product.")


class product_product(models.Model):
    _inherit = "product.product"    
    
    layer_number = fields.Many2one('cam.layer.number', string='Layer Number', required=False, select=True)
    stencil_id = fields.Many2one('cam.laser.steel.mesh.size', string='Stencil', required=False, select=True)
    
    def copy(self, default=None):
        default = default or {}
        default['layer_number'] = []
        default['stencil_id'] = []
        
        return super(product_product, self).copy(id, default)

