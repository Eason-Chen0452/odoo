#-*- coding: utf-8 -*-

from odoo import models,fields,api

class CpoVideo(models.Model):
    """ 添加视频 """

    _name = "cpo_video"
    _order = "sequence, id"

    VIDEO_SELECTION = [
            ('company', 'Company Profile Video'),
            ('process', 'Operation Introduction Video')
        ]
    sequence = fields.Integer(string='Sequence')
    cpo_video_title = fields.Selection(VIDEO_SELECTION, string='Video Type', default='company')
    cpo_video_link = fields.Char(string='Link')
