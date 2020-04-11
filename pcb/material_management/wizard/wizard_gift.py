# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime


class WizardMaterialGift(models.TransientModel):
    _name = 'wizard.material.gift'
    _description = 'Material Gift'

    material_ids = fields.Many2many('material.management', string='Material Name', domain=[('gift_bool', '=', True)], required=True)
    all_show_bool = fields.Boolean('All materials are displayed on the homepage')
    assign_show_bool = fields.Boolean('Manually specify the material display home page later')
    # show_ids = fields.Many2many('material.management', string='Material Name')
    gift_start = fields.Date('Material Gift Time Period', required=True)
    gift_end = fields.Date('Material Gift Time Period', required=True)
    gift_cycle = fields.Char('Material Gift Time Period')
    use_start = fields.Date('Material Use Time Period', required=True)
    use_end = fields.Date('Material Use Time Period', required=True)
    use_cycle = fields.Char('Material Use Time Period')
    send = fields.Integer('How many pieces to send?')
    number = fields.Integer('How Many People Receive', required=True)
    gift_create_bool = fields.Boolean('Whether To Create', default=False)  # 用来做一个视图判断 没有其他意义

    @api.onchange('gift_start', 'gift_end')
    def _onchange_gift_time(self):
        if not self.gift_start or not self.gift_end:
            return False
        self.gift_cycle = self.gift_start + ' - ' + self.gift_end

    @api.onchange('use_start', 'use_end')
    def _onchange_use_time(self):
        if not self.use_start or not self.use_end:
            return False
        self.use_cycle = self.use_start + ' - ' + self.use_end

    @api.onchange('all_show_bool')
    def _onchange_all_show(self):
        if self.all_show_bool:
            return self.update({'all_show_bool': True, 'assign_show_bool': False})

    @api.onchange('assign_show_bool')
    def _onchange_assign_show(self):
        if self.assign_show_bool:
            return self.update({'all_show_bool': False, 'assign_show_bool': True})

    # 检查相关数据
    def _check_error_data(self):
        if self.number <= 0:
            raise ValidationError(_('Please fill in how many people can get it'))
        elif self.send <= 0:
            raise ValidationError(_("Please fill in how many materials the customer can receive at one time."))
        elif not self.assign_show_bool and not self.all_show_bool:
            raise ValidationError(_('Please set whether to show all or part of the gains'))

    # 返回名称
    def get_name(self, x_id):
        value = self.env['material.gift'].search([('material_id', '=', x_id)]).ids
        value.sort()
        if value:
            value = self.env['material.gift'].browse(value[-1])
            value = value.name
            value = value[:value.index('-')] + '-' + str(abs(int(value[value.index('-'):])) + 1)
        else:
            value = self.env['material.management'].browse(x_id)
            value = value.name + '-1'
        return value

    # 创建赠送的数据
    def create_gift_data(self):
        material_ids, uid, gift_start, gift_end = self.material_ids.ids, self._uid, self.gift_start, self.gift_end
        gift_cycle, use_start, use_end, use_cycle = self.gift_cycle, self.use_start, self.use_end, self.use_cycle
        send, number, show, utc_time = self.send, self.number, self.all_show_bool, datetime.utcnow().isoformat()
        for x_id in material_ids:
            name = self.get_name(x_id)
            self.env.invalidate_all()
            self._cr.execute("""INSERT INTO material_gift
                (create_date,write_date,create_uid,write_uid,active,material_id,name,
                gift_start,gift_end,gift_cycle,use_start,use_end,use_cycle,send,number,state,show_bool) VALUES
                ((timestamp '%s'),(timestamp '%s'),'%d','%d',True,'%d','%s',(timestamp '%s'),(timestamp '%s'),
                '%s',(timestamp '%s'),(timestamp '%s'),'%s','%d','%d','Draft','%s')""" %
                (utc_time, utc_time, uid, uid, x_id, name, gift_start, gift_end,
                 gift_cycle, use_start, use_end, use_cycle, send, number, show))
        return True

    @api.multi
    # 按钮统一创建可赠送的
    def action_all_create(self):
        self._check_error_data()
        if self.all_show_bool:
            self.create_gift_data()
            self.update({'gift_create_bool': True})
        elif self.assign_show_bool:
            self.create_gift_data()
            self.update({'gift_create_bool': True})

    @api.multi
    # 返回 一个可以编辑的tree视图
    def action_check(self):
        view_id = self.env.ref('material_management.material_gift_tree').id
        gift_ids = self.env['material.gift'].search([('material_id', 'in', self.material_ids.ids),
                                                     ('gift_cycle', '=', self.gift_cycle),
                                                     ('use_cycle', '=', self.use_cycle),
                                                     ('state', 'in', ('Draft', 'Gift Effective'))]).ids
        return {
            'name': _('Material Gift'),
            'type': 'ir.actions.act_window',
            # 'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'material.gift',
            'views': [[view_id, 'tree']],
            'target': 'new',
            'domain': [('id', 'in', gift_ids)],
            "flags": {'mode': 'edit'},
        }

    @api.multi
    # 按钮统一生效
    def action_effective(self):
        gift_obj = self.env['material.gift']
        material_ids, gift_cycle, use_cycle = self.material_ids.ids, self.gift_cycle, self.use_cycle
        gift_ids = gift_obj.search([('material_id', 'in', material_ids),
                                    ('gift_cycle', '=', gift_cycle),
                                    ('use_cycle', '=', use_cycle),
                                    ('state', '=', 'Draft')])
        if not gift_ids:
            pass
        gift_obj.GetCreateDetail(gift_ids=gift_ids)
