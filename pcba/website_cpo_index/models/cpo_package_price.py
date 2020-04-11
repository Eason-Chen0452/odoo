# -*- coding: utf-8 -*-

from odoo import fields, models, api
from odoo.exceptions import ValidationError

class CpoPackagePrice(models.Model):
    """ 在视图上添加内容，产品等等，可以在前端排版显示 """
    _name = 'cpo_package_price'
    _order = "sequence"

    sequence = fields.Integer(string="Squence")
    cpo_layer_photo = fields.Binary(string="Layers Picture")
    cpo_product_name = fields.Char(string="Product Name")
    cpo_product_area = fields.Char(string="Area")
    cpo_process = fields.Char(string="Process")
    cpo_product_amount = fields.Char(string="Amount")
    link = fields.Char(string="Package Price Link")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('release', 'Release'),
        ('maintain', 'Maintenance update'),
        ('complete_maintain', 'Complete maintenance update'),
        ('invalid', 'Become invalid')
        ], string='Status', copy=False, index=True, default='draft')
    # cpo_product_layers = fields.Char(string="Layers")
    # cpo_turn_time = fields.Char(string="Turn Time")
    # cpo_qty_req = fields.Char(string="Quantity")
    # cpo_product_materials = fields.Char(string="Materials")
    # cpo_finished_copper = fields.Char(string="Finished copper")
    # cpo_trace_space = fields.Char(string="Trace / space")


    @api.multi
    def do_draft(self):
        if self.state == 'invalid':
            self.state = 'draft'
        return True


    @api.multi
    def do_release(self):
        if self.state == 'draft':
            self.state = 'release'
        return True


    @api.multi
    def do_maintain(self):
        if self.state == 'release':
            self.state = 'maintain'
        return True

    @api.multi
    def do_complete_maintain(self):
        if self.state == 'maintain':
            self.state = 'release'
        return True


    @api.multi
    def do_invalid(self):

        self.state = 'invalid'
        return True
