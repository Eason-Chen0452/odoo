# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime, timedelta
import pytz
from lxml import etree
from odoo.exceptions import ValidationError

from odoo import api, fields, models, SUPERUSER_ID, tools, netsvc
from odoo.tools.translate import _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError, AccessError


AVAILABLE_PRIORITIES = [
    ('1', 'Highest'),
    ('2', 'High'),
    ('3', 'Normal'),
    ('4', 'Low'),
    ('5', 'Lowest'),
]

AVAILABLE_PRICE_TYPE = [
    ('item', 'Item'),
    ('csize', 'Size(cm²)'),
    ('msize', 'Size(㎡)'),
    ('pcs', 'PCS'),
    ('set', 'SET'),
]


class cam_volume_level(models.Model):
    _name = 'cam.volume.level'
    _order = "name, min_size, max_size, id"
    _description = 'Volume Level'

    name = fields.Char('Key', size=64, required=True, translate=False, index=True)
    description = fields.Char('Name', Size=64, required=True, translate=True)
    min_size = fields.Float('Min Size', required=True, digits=dp.get_precision('size'), default = 0)
    max_size = fields.Float('Max Size', required=True, digits=dp.get_precision('size'), default = 0)
    price_type = fields.Selection(AVAILABLE_PRICE_TYPE, string='Price Type', track_visibility='onchange', default = AVAILABLE_PRICE_TYPE[0][0])
    note = fields.Text('Note', translate=False)
    company_id = fields.Many2one('res.company','Company',required=True, default=lambda self: self.env.user.company_id.id)
    auto_create = fields.Boolean('Auto Create Price List', default = False)
    active = fields.Boolean('Active', default=True)

    _sql_constraints =[
        ('cam_volume_level_name_uniq', 'unique(name)', 'Volume Level key must be unique'),
        ('cam_volume_level_uniq', 'unique(name, min_size, max_size)', 'Volume Level and pcb size must be unique in volume level config file'),
    ]


class cam_ink_color(models.Model):
    _name = 'cam.ink.color'
    _description = 'Ink Color'
    _inherit = ['mail.thread']

    name = fields.Char('Name', size=64, required=True, translate=True, index=True)
    silk_screen = fields.Boolean('To Silk screen', default=True)
    def_silk_screen = fields.Boolean('Default Silk Screen', default=False)
    text = fields.Boolean('To Text', default=False)
    def_text = fields.Boolean('Default Text Color', default=False)
    rohs = fields.Boolean('ROHS', default=False)
    color_property = fields.Selection([
        ('matt', 'Matte Ink'),
        ('bright', 'Bright Ink'),
        ('normal', 'Normal Ink'),
        ('transparent', 'Transparent Ink')
    ], string='Color Property', default='normal')
    price_type = fields.Selection(AVAILABLE_PRICE_TYPE, string='Price Type', index=True, track_visibility='onchange', default=AVAILABLE_PRICE_TYPE[0][0])
    price = fields.Float('Price', digits=dp.get_precision('Account'), index=True, track_visibility='onchange', default=0.0)
    note = fields.Text('Note', translate=True)
    memo = fields.Text('Memo', translate=True)
    company_id = fields.Many2one('res.company','Company',required=True, default=lambda self: self.env.user.company_id.id)
    auto_create = fields.Boolean('Auto Create Price List', default=False)
    line_ids = fields.One2many('cam.ink.color.line', 'ink_color_id', string='Compute Ink Price')
    active = fields.Boolean('Active', default=True)

    def _ink_color_default_get(self, type='silk_screen'):
        if type == 'silk_screen':
            self.env.cr.execute("SELECT id FROM cam_ink_color WHERE def_silk_screen=True and silk_screen=True and company_id=%s",(self.env.user.company_id.id,))
        else:
            self.env.cr.execute("SELECT id FROM cam_ink_color WHERE def_text=True and text=True and company_id=%s",(self.env.user.company_id.id,))
        ink_color_id = self.env.cr.fetchone()[0] or 0
        return ink_color_id


class cam_ink_color_line(models.Model):
    _name = 'cam.ink.color.line'
    _description = 'Ink Color Line'
    _order = "ink_type,max_size"

    ink_color_id = fields.Many2one('cam.ink.color', string='Ink Color', required=True, index=True, ondelete='cascade')
    ink_type = fields.Selection([
        ('silk_screen', 'Silk screen Ink'),
        ('text', 'Text Ink'),
    ], string='Ink Type', default='silk_screen')
    max_size = fields.Float('Max Size', required=True, digits=dp.get_precision('size'), default=0.0)
    price_type = fields.Selection(AVAILABLE_PRICE_TYPE, string='Price Type', required=True, default=AVAILABLE_PRICE_TYPE[0][0])
    price = fields.Float('Price', required=True, digits=dp.get_precision('Product Price'), default=0.0)

    _sql_constraints = [
        ('color_ink_maxsize_uniq', 'unique(ink_color_id, ink_type, max_size)', 'Ink type and max size must be unique for every ink!'),
    ]


class cam_surface_process(models.Model):
    _name = 'cam.surface.process'
    _description = 'Surface Process'
    _inherit = ['mail.thread']

    name = fields.Char('Name', size=64, required=True, translate=True, index=True)
    def_surface = fields.Boolean('Default Surface', default=False)
    rohs = fields.Boolean('ROHS', default=True)
    price_type = fields.Selection(AVAILABLE_PRICE_TYPE, string='Price Type', track_visibility='onchange', default=AVAILABLE_PRICE_TYPE[0][0])
    price = fields.Float('Price', digits=dp.get_precision('Account'), index=True, track_visibility='onchange', default=0.0)
    note = fields.Text('Note', translate=True)
    memo = fields.Text('Memo', translate=True)
    company_id = fields.Many2one('res.company','Company',required=True, default=lambda self: self.env.user.company_id.id)
    code = fields.Char('Code', size=32, required=True)
    auto_create = fields.Boolean('Auto Create Price List', default=False)
    line_ids = fields.One2many('cam.surface.process.line', 'surface_process_id', string='Compute Surface Process Price')
    active = fields.Boolean('Active', default=True)

    def _surface_process_default_get(self):
        self.env.cr.execute("SELECT id FROM cam_surface_process WHERE def_surface=True and company_id=%s",(self.env.user.company_id.id,))
        surface_process_id = self.env.cr.fetchone()[0]
        return surface_process_id


class cam_surface_process_line(models.Model):
    _name = 'cam.surface.process.line'
    _description = 'Surface Process Line'
    _order = "surface_process_id, max_size, id"

    surface_process_id = fields.Many2one('cam.surface.process', string='Surface Process', required=True, index=True, ondelete='cascade')
    max_size = fields.Float('Max Size', required=True, digits=dp.get_precision('size'), default=0.0)
    price_type = fields.Selection(AVAILABLE_PRICE_TYPE, string='Price Type', required=True, default=AVAILABLE_PRICE_TYPE[0][0])
    price = fields.Float('Price', required=True, digits=dp.get_precision('Product Price'), default=0.0)

    _sql_constraints = [
        ('cam_surface_process_maxsize_uniq', 'unique(surface_process_id, max_size)', 'Surface process and max size must be unique for every surface process!'),
    ]


class cam_via_process(models.Model):
    _name = 'cam.via.process'
    _description = 'Via Process'
    _inherit = ['mail.thread']

    name = fields.Char('Name', size=64, required=True, translate=True, index=True)
    price_type = fields.Selection(AVAILABLE_PRICE_TYPE, string='Price Type', index=True, track_visibility='onchange', default=AVAILABLE_PRICE_TYPE[0][0])
    price = fields.Float('Price', digits=dp.get_precision('Account'), index=True, track_visibility='onchange', default=0.0)
    note = fields.Text('Note', translate=True)
    memo = fields.Text('Memo', translate=True)
    company_id = fields.Many2one('res.company','Company',required=True, default=lambda self: self.env.user.company_id.id)
    auto_create = fields.Boolean('Auto Create Price List', default=False)
    active = fields.Boolean('Active', default=True)


class cam_special_process(models.Model):
    _name = 'cam.special.process'
    _description = 'Special Process'
    _inherit = ['mail.thread']

    name = fields.Char('Name', size=64, required=True, translate=True, index=True)
    price_type = fields.Selection(AVAILABLE_PRICE_TYPE, string='Price Type', index=True, track_visibility='onchange', default=AVAILABLE_PRICE_TYPE[0][0])
    price = fields.Float('Price', digits=dp.get_precision('Account'), index=True, track_visibility='onchange', default=0.0)
    note = fields.Text('Note', translate=True)
    memo = fields.Text('Memo', translate=True)
    company_id = fields.Many2one('res.company','Company',required=True, default=lambda self: self.env.user.company_id.id)
    auto_create = fields.Boolean('Auto Create Price List', default=False)
    line_ids = fields.One2many('cam.special.process.line', 'special_process_id', string='Compute Special Process Price')
    active = fields.Boolean('Active', default=True)


class cam_special_process_line(models.Model):
    _name = 'cam.special.process.line'
    _description = 'Special Process Line'
    _order = "special_process_id,max_size, id"

    special_process_id = fields.Many2one('cam.special.process', string='Special Process', required=True, index=True, ondelete='cascade')
    max_size = fields.Float('Max Size', required=True, digits=dp.get_precision('size'), default=0.0)
    price_type = fields.Selection(AVAILABLE_PRICE_TYPE, string='Price Type', required=True, default=AVAILABLE_PRICE_TYPE[0][0])
    price = fields.Float('Price', required=True, digits=dp.get_precision('Product Price'), default=0.0)

    _sql_constraints = [
        ('cam_special_process_maxsize_uniq', 'unique(special_process_id, max_size)', 'Special process and max size must be unique for every special process!'),
    ]


class cam_special_material(models.Model):
    _name = 'cam.special.material'
    _description = 'Special Material'
    _inherit = ['mail.thread']

    name = fields.Char('Name', size=64, required=True, translate=True, index=True)
    price_type = fields.Selection(AVAILABLE_PRICE_TYPE, string='Price Type', index=True, track_visibility='onchange', default=AVAILABLE_PRICE_TYPE[0][0])
    price = fields.Float('Price', digits=dp.get_precision('Account'), index=True, track_visibility='onchange', default=0.0)
    note = fields.Text('Note', translate=True)
    memo = fields.Text('Memo', translate=True)
    company_id = fields.Many2one('res.company','Company',required=True, default=lambda self: self.env.user.company_id.id)
    auto_create = fields.Boolean('Auto Create Price List', default=False)
    line_ids = fields.One2many('cam.special.material.line', 'special_material_id', string='Compute Special Material Price')
    active = fields.Boolean('Active', default=True)


class cam_special_material_line(models.Model):
    _name = 'cam.special.material.line'
    _description = 'Special Material Line'
    _order = "special_material_id, max_size, id"

    special_material_id = fields.Many2one('cam.special.material', string='Special Material', required=True, index=True, ondelete='cascade')
    max_size = fields.Float('Max Size', required=True, digits=dp.get_precision('size'), default=0.0)
    price_type = fields.Selection(AVAILABLE_PRICE_TYPE, string='Price Type', required=True, default=AVAILABLE_PRICE_TYPE[0][0])
    price = fields.Float('Price', required=True, digits=dp.get_precision('Product Price'), default=0.0)

    _sql_constraints = [
        ('cam_special_material_maxsize_uniq', 'unique(special_material_id, max_size)', 'Special material and max size must be unique for every special material!'),
    ]


class cam_material_brand(models.Model):
    _name = 'cam.material.brand'
    _description = 'Material Brand'
    _inherit = ['mail.thread']

    name = fields.Char('Name', size=64, required=True, translate=True, index=True)
    ink = fields.Boolean('Ink Brand', default=False)
    board = fields.Boolean('Copper Base Brand', default=True)
    pp = fields.Boolean('PP Brand', default=False)
    price_type = fields.Selection(AVAILABLE_PRICE_TYPE, string='Price Type', index=True, track_visibility='onchange', default=AVAILABLE_PRICE_TYPE[0][0])
    price = fields.Float('Price', digits=dp.get_precision('Account'), index=True, track_visibility='onchange', default=0.0)
    note = fields.Text('Note', translate=True)
    memo = fields.Text('Memo', translate=True)
    company_id = fields.Many2one('res.company','Company',required=True, default=lambda self: self.env.user.company_id.id)
    auto_create = fields.Boolean('Auto Create Price List', default=False)
    active = fields.Boolean('Active', default=True)


class cam_layer_number(models.Model):
    _name = 'cam.layer.number'
    _description = 'PCB Layer Number'
    _order = "layer_number"

    name = fields.Char('Name', size=64, required=True, translate=True)
    layer_number = fields.Integer('Layer Number', required=True, help='Give the layer_number How is it layer number', index=True)
    product_ids = fields.One2many("product.product", 'layer_number', string='Product IDS', readonly=True)
    aperture_ratio = fields.Float('Aperture Ratio', required=True, digits=dp.get_precision('size'))
    min_thickness = fields.Float('Min Thickness', required=True, digits=dp.get_precision('size'))
    max_thickness = fields.Float('Max Thickness', required=True, digits=dp.get_precision('size'))
    min_inner_copper = fields.Float('Min Inner Copper', required=True, digits=dp.get_precision('size'))
    max_inner_copper = fields.Float('Max Inner Copper', required=True, digits=dp.get_precision('size'))
    min_outer_copper = fields.Float('Min Outer Copper', required=True, digits=dp.get_precision('size'))
    max_outer_copper = fields.Float('Max Outer Copper', required=True, digits=dp.get_precision('size'))
    note = fields.Text('Note', translate=True)
    memo = fields.Text('Memo', translate=True)
    company_id = fields.Many2one('res.company','Company',required=True, default=lambda self: self.env.user.company_id.id)
    auto_create = fields.Boolean('Auto Create Price List', default=False)
    size_ids = fields.One2many('cam.layer.number.size', 'layer_id', string='PCB Layer Size Price')
    active = fields.Boolean('Active', default=True)

    def name_get(self):
        res = []
        if self._context.get('show_number'):
            for record in self:
                name = record.name
                res.append((record.id, name))
        else:
            res = super(cam_layer_number,self).name_get()
        return res

    def onchange_create(self):
        line_ids = []
        for layer_item in self:
            if not layer_item.size_ids:
                volume_object = self.env['cam.volume.level']
                volume_ids = volume_object.search([])
                volume_items = volume_object.browse(volume_ids)
                for volume_item in volume_items:
                    line_value = {
                        'max_size': volume_item.max_size or 0.0,
                        'volume_type':volume_item.name,
                        'material_fee_type': volume_item.price_type,
                        'material_fee': 0.0,
                        'engineering_fee_type': volume_item.price_type,
                        'engineering_fee': 0.0,
                        'etest_fee_type': volume_item.price_type,
                        'etest_fee': 0.0,
                        'film_fee_type': volume_item.price_type,
                        'film_fee': 0.0,
                        'min_delay_hours': 24,
                        'max_delay_hours': 144,
                        'quick_time': 24,
                        'quick_fee': 10,
                    }
                    line_ids.append(line_value)
        if line_ids:
            return {'value': {'size_ids':line_ids}}
        else:
            return {'value': {}}


class cam_layer_number_size(models.Model):
    _name = 'cam.layer.number.size'
    _description = 'PCB Layer Size Price'
    _order = "layer_id, max_size, id"

    layer_id = fields.Many2one('cam.layer.number', string='PCB Layer Number')
    max_size = fields.Float('Max Size', required=True, digits=dp.get_precision('size'), default=0.0)
    volume_type = fields.Selection([('prototype', 'Prototype'),
                                     ('small', 'Small Volume'),
                                     ('medium', 'Medium Volume'),
                                     ('large', 'Large Volume'),
                                     ('larger', 'Larger Volume'),
                                     ], 'Volume Type')
    material_fee_type = fields.Selection(AVAILABLE_PRICE_TYPE, string='Material Fee Type', required=True, default=AVAILABLE_PRICE_TYPE[0][0])
    material_fee = fields.Float('Material Unit Price', required=True, digits=dp.get_precision('Product Price'), default=0.0)
    engineering_fee_type = fields.Selection(AVAILABLE_PRICE_TYPE, string='Engineering Fee Type', required=True, default=AVAILABLE_PRICE_TYPE[0][0])
    engineering_fee = fields.Float('Engineering Fee', required=True, digits=dp.get_precision('Product Price'), default=0.0)
    etest_fee_type = fields.Selection(AVAILABLE_PRICE_TYPE, string='ETest Fee Type', required=True, default=AVAILABLE_PRICE_TYPE)
    etest_fee = fields.Float('ETest Fee', required=True, digits=dp.get_precision('Product Price'), default=0.0)
    film_fee_type = fields.Selection(AVAILABLE_PRICE_TYPE, string='Film Fee Type', required=True, default=AVAILABLE_PRICE_TYPE[0][0])
    film_fee = fields.Float('Film Fee', required=True, digits=dp.get_precision('Product Price'), default=0.0)
    min_delay_hours = fields.Integer('Min Delay Hours', required=True, default=24, help="This is the min delay in days between the sales order confirmation and the  reception of goods for this PCB and for the customer. It is used by the scheduler to order requests based on reordering delays.")
    max_delay_hours = fields.Integer('Max Delay Hours', required=True, default=0, help="This is the max delay in days between the sales order confirmation and the  reception of goods for this PCB and for the customer. It is used by the scheduler to order requests based on reordering delays.")
    quick_time = fields.Integer('Quick Time(H)', required=True, default=24)
    quick_fee = fields.Integer('Quick Fee(%)', required=True, default=10.0)
    type_item_ids = fields.One2many('cam.layer.number.size.type', 'layer_size_id', string='Price List of Copper Base')

    _sql_constraints = [
        ('cam_layer_size_uniq', 'unique(layer_id, max_size)', 'Layer size must be unique for every layer number!'),
    ]

    def act_auto_create(self):
        base_type_obj = self.env['cam.base.type']
        for layer_size_row in self:
            layer_size_id = layer_size_row.id
            base_type_ids = base_type_obj.search([('include_base_price', '=', False) ,('auto_create', '=', True) , ('active', '=', True)])
            no_base_type_ids = []
            for type_row in layer_size_row.type_item_ids:
                base_type_ids.remove(type_row.base_type.id)
            base_type_items = base_type_obj.browse(base_type_ids)
            for type_row in base_type_items:
                if type_row.price_class == '%':
                    material_fee = layer_size_row.material_fee*(1+(type_row.price/100))
                else:
                    material_fee = layer_size_row.material_fee + type_row.price
                value = {
                    'layer_size_id': layer_size_id,
                    'base_type': type_row.id,
                    'material_fee_type': layer_size_row.material_fee_type,
                    'material_fee': material_fee,
                    'engineering_fee_type': layer_size_row.engineering_fee_type,
                    'engineering_fee': layer_size_row.engineering_fee,
                    'etest_fee_type': layer_size_row.etest_fee_type,
                    'etest_fee': layer_size_row.etest_fee,
                    'film_fee_type': layer_size_row.film_fee_type,
                    'film_fee': layer_size_row.film_fee,
                    'min_delay_hours': layer_size_row.min_delay_hours,
                    'max_delay_hours': layer_size_row.max_delay_hours,
                    'quick_time': layer_size_row.quick_time,
                    'quick_fee': layer_size_row.quick_fee,
                }
                size_type_id = self.env['cam.layer.number.size.type'].create(value)


class cam_layer_number_size_type(models.Model):
    _name = "cam.layer.number.size.type"
    _description = "Price List of Copper Base"
    _order = "layer_size_id, base_type, id"

    layer_size_id = fields.Many2one('cam.layer.number.size', string='Price List of Board Size')
    base_type = fields.Many2one('cam.base.type', string='Copper Base Tye', required=True, index=True)
    material_fee_type = fields.Selection(AVAILABLE_PRICE_TYPE, string='Material Fee Type', required=True, default=AVAILABLE_PRICE_TYPE[0][0])
    material_fee = fields.Float('Material Unit Price', required=True, digits=dp.get_precision('Product Price'), default=0.0)
    engineering_fee_type = fields.Selection(AVAILABLE_PRICE_TYPE, string='Engineering Fee Type', required=True, default=AVAILABLE_PRICE_TYPE[0][0])
    engineering_fee = fields.Float('Engineering Fee', required=True, digits=dp.get_precision('Product Price'), default=0.0)
    etest_fee_type = fields.Selection(AVAILABLE_PRICE_TYPE, string='ETest Fee Type', required=True, default=AVAILABLE_PRICE_TYPE[0][0])
    etest_fee = fields.Float('ETest Fee', required=True, digits=dp.get_precision('Product Price'), default=0.0)
    film_fee_type = fields.Selection(AVAILABLE_PRICE_TYPE, string='Film Fee Type', required=True, default=AVAILABLE_PRICE_TYPE[0][0])
    film_fee = fields.Float('Film Fee', required=True, digits=dp.get_precision('Product Price'), default=0.0)
    min_delay_hours = fields.Integer('Min Delay Hours', required=True, default=24, help="This is the min delay in days between the sales order confirmation and the  reception of goods for this PCB and for the customer. It is used by the scheduler to order requests based on reordering delays.")
    max_delay_hours = fields.Integer('Max Delay Hours', required=True, default=0, help="This is the max delay in days between the sales order confirmation and the  reception of goods for this PCB and for the customer. It is used by the scheduler to order requests based on reordering delays.")
    quick_time = fields.Integer('Quick Time(H)', required=True, default=24)
    quick_fee = fields.Integer('Quick Fee(%)', required=True, default=10)

    _sql_constraints = [
        ('layer_size_base_uniq', 'unique(layer_size_id, base_type)', 'Copper Base Tye must be unique in every board size for every layer number!'),
    ]


class cam_base_type(models.Model):
    _name = 'cam.base.type'
    _description = 'Copper base Type'
    _order = "name, tg_value"
    _parent_name = "parent_id"
    _inherit = ['mail.thread']

    name = fields.Char('Name', size=64, required=True, index=True)
    tg_value = fields.Integer('Tg Value', required=True, default=150)
    price_type = fields.Selection(AVAILABLE_PRICE_TYPE, string='Price Type', index=True, track_visibility='onchange', default=AVAILABLE_PRICE_TYPE[0][0])
    price = fields.Float('Price', digits=dp.get_precision('Account'), index=True, track_visibility='onchange', default=0.0)
    price_class = fields.Selection([('l', 'L'), ('%', '%')], 'Price Class', default='l')
    note = fields.Text('Note', translate=True)
    memo = fields.Text('Memo', translate=True)
    parent_id = fields.Many2one('cam.base.type', string='Parent Types', ondelete='cascade', index=True)
    child_ids = fields.One2many('cam.base.type','parent_id', string='Child Types')
    company_id = fields.Many2one('res.company','Company',required=True, default=lambda self: self.env.user.company_id.id)
    auto_create = fields.Boolean('Auto Create Price List', default=False)
    include_base_price = fields.Boolean('Include In Base Price', default=False)
    active = fields.Boolean('Active', default=True)
