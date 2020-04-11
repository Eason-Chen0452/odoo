#-*- coding: utf-8 -*-

from odoo import models,fields,api

class CpoNewList(models.Model):
    """ 添加新闻消息，用户点击时可以查看详情 """

    _name = "cpo_news_list"
    _order = "sequence, id"

    sequence = fields.Integer(string='Sequence')
    cpo_new_title = fields.Char(string='Title')
    cpo_new_date = fields.Date(string='Date')
    cpo_new_editor = fields.Char(string='Editor')
    cpo_new_content = fields.Html(string='New Content', sanitize=False)
