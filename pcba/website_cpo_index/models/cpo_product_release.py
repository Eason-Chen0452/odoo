# -*- coding: utf-8 -*-

from odoo import fields, models, api

class CpoProductRelease(models.Model):
    """ 在视图上添加内容，产品等等，可以在前端排版显示 """
    _name = 'cpo_product_release'
    _order = "sequence, id"

    sequence = fields.Integer(string="Squence")
    cpo_layer_photo = fields.Binary(string="Layers Picture")
    cpo_product_name = fields.Char(string="Product Name")
    cpo_product_amount = fields.Char(string="Amount")
    cpo_product_layers = fields.Char(string="Layers")
    cpo_turn_time = fields.Char(string="Turn Time")
    cpo_qty_req = fields.Char(string="Quantity")
    cpo_product_materials = fields.Char(string="Materials")
    cpo_finished_copper = fields.Char(string="Finished copper")
    cpo_trace_space = fields.Char(string="Trace / space")
