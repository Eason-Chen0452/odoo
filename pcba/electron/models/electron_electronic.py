# -*- coding: utf-8 -*-

from odoo import models, fields, api
#code_dicts = {
    #u'电阻器': 'resist',
    #u'电容器': 'capa',
    #'general': 'general'
#}



class Electroncomponent(models.Model):
    _name = 'electron.electronic'

    name = fields.Char(string="Electron component", index=True)
    code = fields.Char(string="Code", compute="_get_code", index=True)
    parent_id = fields.Many2one('electron.electronic', string='Parent electronic', index=True)
    child_ids = fields.One2many('electron.electronic', 'parent_id')
    not_show = fields.Boolean("Not show")


    @api.model
    def get_cu_code(self, obj_id):
        row = self.browse(obj_id)
        if row.code:
            return row.code
        elif row.parent_id:
            return self.get_cu_code(row.parent_id.id)
        else:
            general = self.env['electron.type.code'].search([('general', '=', True)])
            return general.code if general else 'general'

    #total=fields.Float(string='Total', compute='_get_total')

    #@api.multi
    @api.depends('name')
    def _get_code(self):
        codes = self.env['electron.type.code'].search([])
        code_dicts = {}
        for row in codes:
            code_dicts.update({row.name:row.code})
        for record in self:
            record.code= code_dicts.get(record.name, '')

    @api.model
    def add_type(self, main_type_text, child_type_text):
        type_obj = self.env['electron.electronic']
        main_type_obj = type_obj.search([('name', '=', main_type_text)], limit=1)
        child_type_obj = type_obj.search([('name','=',child_type_text)], limit=1)
        if not main_type_obj:
            m_type_row = type_obj.create({'name': main_type_text})
            child_type_row = type_obj.create({
                'name': child_type_text,
                'parent_id': m_type_row.id,
                })
            return {
                'main_type':m_type_row.id,
                'child_type':child_type_row.id,
                }
        elif main_type_obj and not child_type_obj:
            child_type_row = type_obj.create({
                'name': child_type_text,
                'parent_id': main_type_obj.id,
                })
            return {
                'main_type':main_type_obj.id,
                'child_type':child_type_row.id,
                }
        else:
            return {
                'main_type':main_type_obj.id,
                'child_type':child_type_obj.id,
            }
