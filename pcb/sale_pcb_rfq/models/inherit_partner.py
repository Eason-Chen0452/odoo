# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


# 继承res.partner 当创建新用户时whether_discount进行更新为True促使新客户首单可以优惠
class Partner(models.Model):
    _inherit = 'res.partner'

    whether_discount = fields.Boolean(string='Whether Discount', default=False)

    # 当客户端创建一个新的用户时 whether_discount = Turn -- 只在创建时候 将这个字段进行改变
    @api.model
    def create(self, vals):
        vals.update({'whether_discount': True})
        return super(Partner, self).create(vals)
