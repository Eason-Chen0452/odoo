# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class InheritPersonalCenter(models.Model):
    _inherit = 'personal.center'

    # material_buy_ids = fields.Many2many('material.management', string='Purchased Material')
    # material_gift_ids = fields.Many2many('material.gift', string='Gifted Material')
    gift_count = fields.Integer(string='Gift Material', compute='_compute_gift_count', store=True)
    buy_count = fields.Integer(string='Purchased Material', compute='_compute_buy_count', store=True)
    gift_count_bool = fields.Boolean('Gift Material', default=False)  # 做检测使用
    buy_count_bool = fields.Boolean('Purchased Material', default=False)  # 做检测使用

    @api.one
    @api.depends('gift_count_bool')
    # 这里搜索的数据 可能会很庞大
    def _compute_gift_count(self):
        if not self:
            return False
        center_id = self.id
        self._cr.execute("SELECT ID FROM MATERIAL_GIFT_LINE WHERE CENTER_ID = %s", (center_id, ))
        if self._cr.fetchall():
            self.gift_count = len(self._cr.fetchall()[0])


    @api.one
    @api.depends('buy_count_bool')
    def _compute_buy_count(self):
        pass

    @api.multi
    def get_material_views(self):
        if self._context.get('value') == 'gift':
            return self._get_action('material_management.act_gift_line')
        elif self._context.get('value') == 'buy':
            pass

    @api.multi
    def _get_action(self, action_xmlid):
        action = self.env.ref(action_xmlid).read()[0]
        if self._context.get('value') == 'gift':
            action['domain'] = [('center_id', '=', self.id)]
        elif self._context.get('value') == 'buy':
            pass
        return action

