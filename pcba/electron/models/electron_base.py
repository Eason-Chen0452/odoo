# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo.tools.translate import _

class Electron_type_code(models.Model):
    _name = 'electron.type.code'

    name = fields.Char(string = 'Name', index=True, copy=False)
    code = fields.Char(string = 'Code', index=True, copy=False)
    general = fields.Boolean(string="General")

    @api.constrains('general')
    def check_general(self):
        general = self.search([('general', '=', True)])
        if len(general)>1:
            raise ValidationError(_("Electron Type code rel table general field must only one!"))



class Electron_base(models.Model):
    _name = 'electron.base'

    #_sql_constraints = [
        #('pcb_number', 'UNIQUE(pcb_number)', 'Current data already exists!')
    #]

    p_type = fields.Many2one('electron.electronic', string="Type", index=True)  #关联字段
    name = fields.Char(string="PDF Explain", index=True)                        #PDF 说明书
    pcb_number = fields.Char(string="ChinaPCBONE P/N", index=True)              #瑞邦信息 零件编号
    dash_number = fields.Char(string="Manufacturer P/N", index=True)            #制造商 零件编号
    digi_number = fields.Char(string="Digikey P/N", index=True)                 #Digikey 零件编号
    mini_quantity = fields.Char(string="Minimum Order Quantity")    #最低订购数量是
    QOH = fields.Char(string="Existing Number")                     #现有数量（库存）
    price = fields.Char(string="Price")                             #单价
    description = fields.Char(string="Description", index=True)             #描述
    series = fields.Char(string="Series", index=True)                           #系列
    manufacture = fields.Char(string="Manufacturer", index=True)                #制造商
    tolerance = fields.Char(string="Tolerance", index=True)                     #容差
    size = fields.Char(string="Size", index=False)                               #大小/尺寸
    encapsulation = fields.Char(string="Encapsulation", index=False)             #封装/外壳
    inst_type = fields.Char(string="Install Type", index=False)                  #安装类型
    packaging = fields.Char(strin="Packaging", index=False)                      #包装
    character = fields.Char(string="Character", index=False)                     #特性
    parts_state = fields.Char(string="Parts State")                 #零件状态
    type_code = fields.Char(string="Type code",compute="_get_type_code", store=True)
    update_type_code = fields.Boolean(string="Update Type Code")

    @api.depends('p_type','update_type_code')
    def _get_type_code(self):
        for row in self:
            row.type_code = row.p_type.get_cu_code(row.p_type.id)

    @api.constrains('digi_number')
    def check_digi_number(self):
        digi_number = self.search([('digi_number', '=', self.digi_number),('id', '!=', self.id)])
        if len(digi_number) >= 1:
            digi_number.unlink()
            digi_number = self.search([('digi_number', '=', self.digi_number),('id', '!=', self.id)])
            if len(digi_number) >= 1:
                raise ValidationError(_("Model: electron_base,Feild: digi_number, ids:{field} already exists!").format(field = digi_number.mapped("id")))

class Electron_atta(models.Model):
    _name = "electron.atta"

    url_sources = fields.Char(string="Data Sources", index=True)                #数据来源
    cpo_image = fields.Binary(string="Image")                       # 图像
    mini_image_herf = fields.Char(string="Mini Image Herf")         #小图像链接
    big_image_herf = fields.Char(string="Big Image Herf")           #大图像链接

class Electron_base_item(models.Model):
    _name = 'electron.base.item'

    base_id = fields.Many2one("electron.base", required=True, ondelete='cascade', index=True)
    atta_id = fields.Many2one("electron.atta", required=True, ondelete='cascade', index=True)

    @api.multi
    def unlink(self):
        p_objs = [[getattr(y, str(x)) for x in y._inherits.values()] for y in self]
        res = super(Electron_base_item, self).unlink()
        for row in p_objs:
            [x.unlink() for x in row]
        return res


    @api.model
    def add_record(self, vals):

        if self.env['electron.content'].search([('pcb_number', '=', vals['pcb_number'])]):
            #if not vals.get('require_contract'):
                #raise ValidationError(_("Please perfect the contract first!"))
            return self.write(vals)
        return self.create(vals)
