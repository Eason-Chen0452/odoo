# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime
import calendar, time

MATERIAL_TYPE = [
    ('Draft', 'Draft'),
    ('Gift Effective', 'Gift Effective'),
    ('Gift Invalid', 'Gift Invalid'),
]


class MaterialManagement(models.Model):
    _name = 'material.management'
    _description = 'Material Management Setting'
    _order = 'id desc'

    name = fields.Char('Material Name', size=64, required=True, translate=True)
    product_id = fields.Many2one('product.template', 'Product', index=True)
    active = fields.Boolean('Active', default=True)
    gift_bool = fields.Boolean('Gift Material', default=False)
    sale_bool = fields.Boolean('Can I Sell It For Sale?', default=False)
    start = fields.Date('Material Life Cycle')
    end = fields.Date('Material Life Cycle')
    cycle = fields.Char('Material Life Cycle')
    price = fields.Float('Price', digits=(16, 2))
    unit = fields.Selection([('Plate', 'Plate'), ('Single', 'Single')], string='Unit')
    quantity = fields.Integer('Quantity')
    description = fields.Text('Material Description', required=True)  # 物料描述
    manufacturer = fields.Char('Material Manufacturer Number', required=True)  # 制造商编号
    package = fields.Char('Material Package Number')  # 封装

    _sql_constraints = [(
        'name_unique', 'unique(name)',
        "The system has detected that the material name is duplicated. Please name the material name from the new one."
    )]

    @api.onchange('start', 'end')
    def _onchange_time(self):
        if not self.start or not self.end:
            return False
        self.cycle = self.start + ' - ' + self.end

    @api.multi
    def write(self, vals):
        return super(MaterialManagement, self).write(vals)

    @api.multi
    def unlink(self):
        return super(MaterialManagement, self).unlink()


class MaterialGift(models.Model):
    _name = 'material.gift'
    _description = 'Material Gift'
    _order = 'sequence, state desc'

    material_id = fields.Many2one('material.management', 'Material Name', required=True, index=True, domain=[('gift_bool', '=', True)], ondelete='cascade')
    name = fields.Char('Title', readonly=True)
    number = fields.Integer('How Many People Receive', required=True)
    active = fields.Boolean('Active', default=True)
    gift_start = fields.Date('Material Gift Time Period', required=True)
    gift_end = fields.Date('Material Gift Time Period', required=True)
    gift_cycle = fields.Char('Material Gift Time Period')
    use_start = fields.Date('Material Use Time Period', required=True)
    use_end = fields.Date('Material Use Time Period', required=True)
    use_cycle = fields.Char('Material Use Time Period')
    show_bool = fields.Boolean('Whether To Show')
    sequence = fields.Integer('Sequence')
    send = fields.Integer('How many pieces to send?')
    description = fields.Text('Material Description', readonly=True, related='material_id.description')  # 物料描述
    manufacturer = fields.Char('Material Manufacturer Number', readonly=True, related='material_id.manufacturer')  # 制造商编号
    package = fields.Char('Material Package Number', readonly=True, related='material_id.package')  # 封装
    state = fields.Selection(MATERIAL_TYPE, default='Draft', index=True, string='Gift State')
    gift_line_ids = fields.One2many('material.gift.line', 'gift_id', 'Material Gift Detail', readonly=True)

    _sql_constraints = [(
        'material_time_unique', 'unique(material_id,gift_start,gift_end)',
        "Gift materials and gift time periods cannot be repeated."
    )]

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

    @api.onchange('material_id')
    def _onchange_get_name(self):
        if not self.material_id:
            return False
        value = self.search([('material_id', '=', self.material_id.id)]).ids
        value.sort()
        if value:
            value = self.browse(value[-1])
            value = value.name
            value = value[:value.index('-')] + '-' + str(abs(int(value[value.index('-'):])) + 1)
        else:
            value = self.material_id.name + '-1'
        self.name = value

    # 检查相关数据
    def _check_error(self):
        if self.number <= 0:
            raise ValidationError(_('Please fill in how many people can get it'))
        elif self.send <= 0:
            raise ValidationError(_("Please fill in how many materials the customer can receive at one time."))

    # 赠送生效 创建明细
    def button_effective(self):
        self._check_error()
        self.GetCreateDetail(self)

    # 传入进来的是对象
    def GetCreateDetail(self, gift_ids=False):
        for x_id in gift_ids:
            number, name, uid, gift_id = x_id.number, x_id.name, x_id._uid, x_id.id
            for x in range(number):
                self.env.invalidate_all()
                value = str(x + 1) + '/' + name
                self._cr.execute("""INSERT INTO material_gift_line 
                (create_date,write_date,create_uid,write_uid,active,gift_id,name) VALUES 
                ((timestamp '%s'),(timestamp '%s'),'%d','%d',True,'%d','%s')""" %
                (datetime.utcnow().isoformat(), datetime.utcnow().isoformat(), uid, uid, gift_id, value))
            x_id.update({'state': 'Gift Effective'})
        return True

    # 返回相应字段
    def get_fields_name(self):
        value = {
            'default_material_id': self.material_id.id,
            'default_active': True,
            'default_state': 'Draft',
            'default_send': self.send,
            'default_show_bool': self.show_bool,
            'default_number': self.number,
            'default_gift_start': self.gift_start,
            'default_gift_end': self.gift_end,
            'default_use_start': self.use_start,
            'default_use_end': self.use_end,
        }
        return value

    # 再次创建
    def button_create(self):
        value = self.get_fields_name()
        view_id = self.env.ref('material_management.material_gift_form').id
        return {
            'name': _('Material Gift'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree, form',
            'res_model': 'material.gift',
            'views': [[view_id, 'form']],
            'context': value
        }

    # 前端首页展示 接口调用
    def get_home_show(self):
        return self.GetDataHome()

    # 独立界面展示 接口调用
    def get_independent_show(self):
        return self.GetDataHome(only=True)

    def CheckTime(self):
        data = self.search([('show_bool', '=', True), ('state', '=', 'Gift Effective')])
        now_time = fields.Datetime.now()
        for x_id in data:
            if x_id.gift_end + ' 23:59:59' < now_time:
                x_id.write({'state': 'Gift Invalid'})
        return True

    # 首页展示 根据条件返回 某一段时间比较重要的数据
    def GetDataHome(self, only=False):
        now_time, value = fields.Datetime.now(), {}
        self.CheckTime()
        if not only:
            data = self.search([('show_bool', '=', True), ('gift_start', '<=', now_time), ('gift_end', '>=', now_time), ('state', '=', 'Gift Effective')])
            if data:
                value.update({'time': data[0].gift_cycle, 'value': data})
            return value
        now_time = time.localtime()
        data, month = calendar.monthrange(now_time.tm_year, now_time.tm_mon)
        start = '%d-%02d-01' % (now_time.tm_year, now_time.tm_mon)
        end = '%d-%02d-%02d' % (now_time.tm_year, now_time.tm_mon, month)
        data = self.search([('show_bool', '=', True), ('gift_start', '>=', start), ('gift_end', '<=', end)])
        value.update({'month': str(now_time.tm_mon) + 'Month'})
        for x in data:
            if x.gift_cycle in value.keys():
                value[x.gift_cycle].update({x.material_id.name: x.description})
            elif x.gift_cycle not in value.keys():
                value.update({
                    x.gift_cycle: {
                        x.material_id.name: x.description
                    }
                })
        return value


class MaterialGiftLine(models.Model):
    _name = 'material.gift.line'
    _order = 'id'
    _description = 'Material Gift Detail'

    gift_id = fields.Many2one('material.gift', 'Material Gift', ondelete='cascade', index=True)
    name = fields.Char('Number')
    active = fields.Boolean('Active', default=True)
    center_id = fields.Many2one('personal.center', 'Client', ondelete='cascade', index=True)
    send = fields.Integer('How many pieces to send?', readonly=True, related='gift_id.send')
    gift_start = fields.Date('Material Gift Time Period', readonly=True, related='gift_id.gift_start')
    gift_end = fields.Date('Material Gift Time Period', readonly=True, related='gift_id.gift_end')
    gift_cycle = fields.Char('Material Gift Time Period', readonly=True, related='gift_id.gift_cycle')
    use_start = fields.Date('Material Use Time Period', readonly=True, related='gift_id.use_start')
    use_end = fields.Date('Material Use Time Period', readonly=True, related='gift_id.use_end')
    use_cycle = fields.Char('Material Use Time Period', readonly=True, related='gift_id.use_cycle')
    description = fields.Text('Material Description', readonly=True, related='gift_id.material_id.description')  # 物料描述
    manufacturer = fields.Char('Material Manufacturer Number', readonly=True, related='gift_id.material_id.manufacturer')  # 制造商编号
    package = fields.Char('Material Package Number', readonly=True, related='gift_id.material_id.package')  # 封装
    state = fields.Selection(MATERIAL_TYPE, default='Draft', string='Gift State', related='gift_id.state')

    # 客户领取接口调用
    def get_receive_materiel(self, partner_id, gift_id):
        return self.ReceiveMateriel(partner_id, gift_id)

    # 调用函数
    def ReceiveMateriel(self, partner_id, gift_id):
        center_id = self.env['personal.center'].search([('partner_id', '=', int(partner_id))]).id
        # 如果个人中心没有数据 就创建一条
        if not center_id:
            center_id = self.env['personal.center'].create({'partner_id': int('partner_id')}).id
        gift_data = self.search([('gift_id', '=', int(gift_id)), ('center_id', '=', center_id)])
        # 有领取过 返回错误
        if gift_data:
            return {'warning': 'You have already received this item'}
        gift_data = self.search([('gift_id', '=', int(gift_id)), ('center_id', '=', None)])[0]
        gift_data.update({'center_id': center_id, 'gift_count_bool': True if not gift_data.gift_count_bool else False})
        return True

