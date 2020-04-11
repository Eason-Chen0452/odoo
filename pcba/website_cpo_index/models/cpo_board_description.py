#-*- coding: utf-8 -*-

from odoo import models,fields,api

class CpoBoardDescription(models.Model):
    """ 添加添加产品介绍，用户点击时可以查看详情 """

    _name = "cpo_product_description"
    _order = "sequence, id"

    sequence = fields.Integer(string='Sequence')
    title = fields.Char(string="Product Title")
    description = fields.Text(string='Product Description')
    Cover_img = fields.Binary(string="Cover Image")
    cpo_btn_name = fields.Char(string="Button Name")
