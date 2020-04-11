# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SalesAgent(models.Model):
    _name = 'sales.agent'
    _inherits = {'res.users': 'user_id'}
    _description = 'Regional Sales Agent'

    user_id = fields.Many2one('res.users', 'User', index=True, ondelete='cascade')
    client_ids = fields.Many2many('personal.center', string='Agent Manageable Customer')
    country_ids = fields.Many2many('res.country', string='Agent Manageable Country')

    # 同时删除相关联的用户
    @api.multi
    def unlink(self):
        for x_id in self:
            x_id.user_id.unlink()
        return super(SalesAgent, self).unlink()
