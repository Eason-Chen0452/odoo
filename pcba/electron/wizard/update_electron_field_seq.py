# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo import _

class electron_update_field_sequence(models.TransientModel):
    _name = 'electron.update_field_sequence'

    ele_type = fields.Many2one("electron.electronic", "Type")
    ele_fields = fields.One2many('electron.update_field_sequence_line', 'ele_update_id', string="Electron Update Sequence")

    @api.onchange("ele_type")
    def onchange_ele_type(self):
        vals = {}
        disk_rel = self.env['electron.disk_rel']
        disk_rel_ids = disk_rel.search([('tt_type', '=', self.ele_type.id)])
        #disk_dict = disk_rel.get_disk_rel(self.ele_type.name)
        vals = [(0,0,{'disk_rel_id':x}) for x in disk_rel.search([('tt_type', '=', self.ele_type.id)], order="sequence, id").mapped("id")]
        return {'value': {'ele_fields': vals}}

    @api.multi
    def do_set_default(self):
        return self.ele_fields.write({'sequence': 10})

class electron_update_field_sequence_line(models.TransientModel):
    _name = 'electron.update_field_sequence_line'
    _order ="sequence"

    ele_update_id = fields.Many2one("electron.update_field_sequence", "Electron Update Field Sequence", ondelete="cascade")
    disk_rel_id = fields.Many2one("electron.disk_rel", 'Disk Rel id')
    sequence = fields.Integer(related='disk_rel_id.sequence', store=True, string='Sequence')
    ele_disk_field_id = fields.Many2one('electron.disk_fields', related='disk_rel_id.ele_disk_field_id', string="Field id")   #关联字段
    ele_title = fields.Char(related='disk_rel_id.ele_title', string="Title", translate=True)                          #标题
