#-*- coding: utf-8 -*-
from odoo import models, fields, api
import datetime

class CpoAnnexFile(models.Model):
    _name = 'cpo_annex_file'
    _order = "id desc"

    # information_attachment = fields.Many2many('ir.attachment', compute='_get_attachment_ids', string='Annex')
    name = fields.Char(string="Name")
    file_type = fields.Char('File type')
    order_type = fields.Char('Order type')
    datas = fields.Binary(string="Datas", attachment=True)
    upload_date = fields.Datetime(string="Create Time")
    user_name = fields.Char(string="User Name")
    cpo_country = fields.Char(string="Country")
    user_ip = fields.Char(string="User IP")
    session_id = fields.Char(string="Session ID")
    cpo_city = fields.Char(string="City")

    @api.model
    def cpo_sync_att_to_quotation_record(self, ids_dict, quo_id, session_data):
        atta_pool = self.env['ir.attachment'].sudo()
        cpo_atta_data = {
            'cpo_country': session_data.get('cpo_country'),
            'user_ip': session_data.get('user_ip'),
            'session_id': session_data.get('session_id'),
            'cpo_city': session_data.get('cpo_city'),
        }

        ids = []
        if ids_dict.get('gerber_file_id'):
            ids.append(ids_dict.get('gerber_file_id'))
        if ids_dict.get('bom_file_id'):
            ids.append(ids_dict.get('bom_file_id'))
        if ids_dict.get('smt_file_id'):
            ids.append(ids_dict.get('smt_file_id'))
        all_ids = self.sudo().search([('id', 'in', ids)])
        if all_ids:
            if all_ids[0].order_type == 'PCBA':
                model_obj = 'cpo_pcba_record'
            else:
                model_obj = 'cpo_pcb_record'
            ids = all_ids.mapped("id")
            atta_ids = atta_pool.search([('res_model', '=', 'cpo_annex_file'), ('res_id', 'in', ids)])
            for file_obj in all_ids:
                file_obj.write(cpo_atta_data)
            # for atta_id in atta_ids:
            #     vals = {
            #         'name': atta_id.name,
            #         'description': atta_id.description,
            #         'type': atta_id.type,
            #         'public': True,
            #         'res_model': model_obj,
            #         'res_id': quo_id.id,
            #         'datas_fname': atta_id.datas_fname,
            #         'store_fname': atta_id.store_fname,
            #     }
            #     atta_pool.create(vals)

        return True

    @api.multi
    def cpoRegularlyCleanAttachments(self):
        """
        定期清理附件
        :return:
        """
        annex_file = self.env['cpo_annex_file'].search([])
        now_time = datetime.datetime.now()
        print now_time
        for row in annex_file:
            create_date = datetime.datetime.strptime(row.create_date, '%Y-%m-%d %H:%M:%S')
            time_diff = (now_time - create_date).total_seconds()
            cpo_term = 30*24*60*60
            if time_diff >= cpo_term:
                row.unlink()



    # @api.multi
    # def _compute_attachment_number(self):
    #     """附件上传"""
    #     attachment_data = self.env['ir.attachment'].read_group(
    #         [('res_model', '=', 'cms_su'), ('res_id', 'in', self.ids)], ['res_id'], ['res_id'])
    #     attachment = dict((data['res_id'], data['res_id_count']) for data in attachment_data)
    #     for expense in self:
    #         expense.attachment_number = attachment.get(expense.id, 0)
    # def _get_attachment_ids(self):
    #     att_model = self.env['ir.attachment']  # 获取附件模型
    #     for obj in self:
    #         query = [('res_model', '=', self._name), ('res_id', '=', obj.id)]  # 根据res_model和res_id查询附件
    #         obj.information_attachment = att_model.search(query)
