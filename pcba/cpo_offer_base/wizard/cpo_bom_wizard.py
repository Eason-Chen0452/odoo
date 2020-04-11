# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo import _
import xlrd
import xlwt
import base64
import re
from ..models.cpo_bom_supply_list import BOM_HEAD_SELECTION
from ..models.cpo_offer_bom import recheck_bom_file_content


class cpo_bom_wizard(models.TransientModel):
    _name = 'cpo_bom_wizard.wizard'

    cpo_bom = fields.Many2one('cpo_offer_bom.bom', string="Bom")
    force_import = fields.Boolean("Force Import")
    refresh_bom = fields.Boolean("Refresh Bom")
    cpo_title = fields.One2many('cpo_bom_table_head.head', 'basedata_id', string="Table title", ondelete="cascade")

    @api.model
    def default_get(self, fields_list):
        res = super(cpo_bom_wizard, self).default_get(fields_list)
        if self.env.context.get('default_model') == 'cpo_offer_bom.bom':
            bom_obj = self.env['cpo_offer_bom.bom']
            bom_res = self.env.context.get('default_res_id')
            bom_id = bom_obj.search([('id', '=', bom_res)])
            res.update({'cpo_bom': bom_id.id})
            # bom_ref = {}
            # for row in bom_fields_pool:
            # bom_ref.update({row.src_title: row.cpo_title})
        return res

    # 返回相同记录的向导视图
    @api.multi
    def _reopen_form(self):
        return {'type': 'file_table_head_action',
                'res_model': self._name,
                'view_type': 'form',
                'view_mode': 'form',
                'res_id': self.id,
                'target': 'new'}

    # 获取上传文件的表头
    @api.multi
    def head_create(self):
        cpo_bom_file = self.cpo_bom.search([('id', '=', self.cpo_bom.id)])
        if self.cpo_bom:
            if self.cpo_bom.order_ids.order_id.bom_fields_line:
                bom_fields_pool = self.cpo_bom.order_ids.order_id.bom_fields_line
                bom_ref = [(0, 0, {'src_title': x.src_title, 'cpo_title': x.cpo_title}) for x in bom_fields_pool]
                return {'cpo_title': bom_ref}
                # self.update({'cpo_title' :bom_ref})
            elif cpo_bom_file.bom_file:
                workbook = xlrd.open_workbook(file_contents=base64.decodestring(cpo_bom_file.bom_file))
                head_count_repetition = int(self.cpo_title.search_count([('basedata_id', '=', self.id)]))
                if len(workbook._sheet_list) >= 1:
                    workbook_content = workbook.sheet_by_index(0)
                    b = []
                    # for y_col in range(workbook_content.ncols) :
                    #    cell_head = workbook_content.cell(0,y_col).value
                    #    #aa = {'original_col' : cell_head}
                    #    aa = {'src_title' : cell_head}
                    #    b.append((0,0, aa))
                    #    if y_col+1 == head_count_repetition :
                    #        raise ValidationError(_("Create duplicate data is not allowed !!"))
                    ce_rows = []
                    for x_row in range(0, workbook_content.nrows):
                        i_row = []
                        for y_col in range(workbook_content.ncols):
                            i_row.append(workbook_content.cell(x_row, y_col).value)
                        ce_rows.append(i_row)
                    rows = recheck_bom_file_content(ce_rows)
                    res = []
                    b = [(0, 0, {'src_title': x}) for x in rows[0]]
                    # for x_row in rows[1:]:
                    #    bom_row_data = {}
                    #    for src_title,cpo_title in bom_head_dict.items():
                    #        bom_row_data.update({src_title:x_row[t_index]})
                    #    res.append((0,0,bom_row_data))
                    # row.write({'base_table_bom' : res})
                    return {'cpo_title': b}
                    # self.update({'cpo_title' : b})
        return {}  # return self._reopen_form()

    @api.multi
    def update_head_ref(self):
        if self.cpo_bom and self.cpo_bom.order_ids and self.cpo_title:
            bom_ref = [(0, 0, {'src_title': x.src_title, 'cpo_title': x.cpo_title}) for x in self.cpo_title if
                       x.cpo_title]
            for order_id in self.cpo_bom.order_ids:
                order_id.order_id.write({'bom_fields_line': [(2, x.id) for x in order_id.order_id.bom_fields_line]})
                order_id.order_id.write({'bom_fields_line': bom_ref})
            return True

    # 检查表头是否一致
    @api.multi
    def do_check(self):
        # offer_bom = self.env['cpo_offer_bom.bom']
        self.update_head_ref()
        head_count = int(self.cpo_title.search_count([('basedata_id', '=', self.id)]))
        table_head_id = self.cpo_title.search([('basedata_id', '=', self.id)])
        if self.cpo_title:
            for count_head in range(head_count):
                head_original_col = table_head_id[count_head].src_title
            bom_head_dict = dict([(x.src_title, x.cpo_title) for x in self.cpo_title if x.cpo_title])
            # bom_head_dict = dict([(x.original_col, x.new_table_head) for x in self.cpo_title if x.new_table_head])
            self.cpo_bom.force_import = self.force_import
            self.cpo_bom.do_importing(bom_head_dict=bom_head_dict)
            self.cpo_bom.state = 'check'
        view = self.env.ref('cpo_offer_base.cpo_offer_bom_form')
        res = {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'cpo_offer_bom.bom',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'res_id': self.cpo_bom.id,
        }
        return res

    @api.onchange('cpo_bom', 'refresh_bom')
    def change_head(self):
        res = self.head_create()
        return {'value': res}
        # return self._reopen_form()


class cpo_bom_table_head(models.TransientModel):
    _name = 'cpo_bom_table_head.head'

    basedata_id = fields.Many2one('cpo_bom_wizard.wizard', string="Base data", ondelete="cascade")

    cpo_title = fields.Selection(BOM_HEAD_SELECTION, string="Headline")
    src_title = fields.Char(string="Col content")
    # new_table_head = fields.Selection(BOM_HEAD_SELECTION, string="Headline")
    # original_col = fields.Char(string="Col content")

    # @api.one
    # @api.constrains('new_table_head')
    # def out_repetition(self):
    #    for this in self:
    #        if this.new_table_head :
    #            head_one = this.search_count([('new_table_head', '=', this.new_table_head),('id', '!=', this.id),('basedata_id', '=', this.basedata_id.id)])
    #            print head_one
    #            if head_one > 0 :
    #                raise ValidationError(_("Error, Headline ("+this.new_table_head+") repetition!!"))
