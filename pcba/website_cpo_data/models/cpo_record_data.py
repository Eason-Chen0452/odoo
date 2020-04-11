#-*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo import tools

class WebsiteRecordData(models.Model):

    _name = 'website_cpo_data.record_data'
    _order = 'cpo_time desc'
    _auto = False

    user_name = fields.Many2one('personal.center', string="Panter Name")
    order_type = fields.Char(string="Order Type")
    quantity = fields.Integer(string="Quantity")
    width = fields.Float(string="Width")
    lenght = fields.Float(string="Length")
    thickne = fields.Float(string="Board thickness")
    cpo_country = fields.Char(string="Country")
    user_ip = fields.Char(string="User IP")
    cpo_time = fields.Datetime(string="Create Time")
    count_pcb = fields.Integer(string="PCB Count")
    count_pcba = fields.Integer(string="PCBA Count")
    count_num = fields.Integer(string="Total count")

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        from_str = """
                    select
                      max(base.id) as id,
                      base.user_name as user_name,
                      max(base.cpo_time) as cpo_time,
                      max(base.order_type) as order_type,
                      max(base.quantity) as quantity,
                      max(base.width) as width,
                      max(base.lenght) as lenght,
                      max(base.thickne) as thickne,
                      max(base.cpo_country) as cpo_country,
                      max(base.user_ip) as user_ip,
                      SUM(
                          CASE 
                            WHEN order_type='PCB' THEN 1
                            WHEN order_type='HDI' THEN 1
                            WHEN order_type='Rigid-FLex' THEN 1
                            WHEN order_type='PCB Package' THEN 1
                            ELSE 0 END)AS count_pcb,
                        SUM(
                          CASE 
                            WHEN order_type='PCBA' THEN 1 
                            WHEN order_type='PCBA Package Price' THEN 1 
                            ELSE 0 END)AS count_pcba,
                          count(*) as count_num
                    FROM cpo_pcb_and_pcba_record pcb_pcba LEFT OUTER JOIN cpo_quotation_record_base base on pcb_pcba.record_pcb_pcba_id=base.id
                    WHERE base.order_type IS NOT NULL
                    GROUP BY user_name
                    ORDER BY cpo_time desc
                """
        sql_str = """create or REPLACE view %s as  (%s) """ % (self._table, from_str)
        self.env.cr.execute(sql_str)

    @api.multi
    def cpo_usre_record(self):
        object_model = None
        condition = None
        order_type = self.order_type
        user_name = self.user_name.id
        pcb_pool = 'cpo_pcb_record'
        pcba_pool = 'cpo_pcba_record'
        pcb_and_pcba = 'cpo_pcb_and_pcba_record'
        values = {
            'pcb': ['PCB', 'HDI', 'Rigid-FLex', 'PCB Package'],
            'pcba': ['PCBA', 'PCBA Package Price'],
            'pcb_and_pcba': ['PCBA', 'PCBA Package Price', 'PCB', 'HDI', 'Rigid-FLex', 'PCB Package']
        }
        object_model = pcb_and_pcba
        if user_name:
            if order_type in values.get('pcb'):
                condition = [('order_type', 'in', values.get('pcb_and_pcba')), ('user_name', '=', user_name)]
            elif order_type in values.get('pcba'):
                condition = [('order_type', 'in', values.get('pcb_and_pcba')), ('user_name', '=', user_name)]
        else:
            condition = [('order_type', 'in', values.get('pcb_and_pcba')), ('user_name', '=', None)]

        return {
            'name': 'User quotation record',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form, tree',
            'res_model': object_model,
            'views': [(False, 'tree'), (False, 'form')],
            'view_id': False,
            'domain': condition,
            'context': {
                'search_default_current': 1,
                'search_default_group_by_cpo_time': 1,
                'search_default_group_by_order_type': 1,
                'search_default_this_week': 1
            }
        }






