#-*- coding: utf-8 -*-

from odoo import models, fields, api


class CpoClickSelectBigCategory(models.Model):
    _name = 'cpo_big_category'
    name = fields.Char(string="Type")
    category_type_ids = fields.Many2many('cpo_click_select_category', string="Category Type")

class CpoWebsiteClickSelectCategory(models.Model):
    _name = 'cpo_click_select_category'

    cpo_category_type = fields.Char(string="Category Type")
    name = fields.Char(string="Name")
    cpo_relationship = fields.One2many('cpo_click_select_detailed', 'cpo_detailed_rel', string="Relationship")
    cpo_detailed_type = fields.Many2many('cpo_click_select_detailed', string="Detailed Type")



class CpoWebsiteClickSelectDetailed(models.Model):
    _name = 'cpo_click_select_detailed'

    cpo_detailed_type = fields.Char(string="Detailed Type", ondelete="cascade")
    name = fields.Char(string="Name", ondelete="cascade")
    cpo_detailed_rel = fields.Many2one('cpo_click_select_category', string="Rel", ondelete="cascade")
    cpo_detailed_rel_many = fields.Many2many('cpo_click_select_category', string="Rel", ondelete="cascade")