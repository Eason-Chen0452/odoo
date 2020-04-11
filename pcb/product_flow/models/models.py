# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ProductFlow(models.Model):
    _inherit = 'sale.order'

    pcb_flow = fields.Selection([('Cutting', 'Cutting'),  # 开料
                                 ('Inner Layer Wiring/Etching', 'Inner Layer Wiring/Etching'),  # 内层线路/蚀刻
                                 ('AOI Check', 'AOI Check'),  # AOI检查
                                 ('Browning', 'Browning'),   # 棕化
                                 ('Lamination', 'Lamination'),  # 压合
                                 ('Drilling', 'Drilling'),  # 钻孔
                                 ('Copper Sink/Board Power', 'Copper Sink/Board Power'),  # 沉铜/板电
                                 ('Outer Line/Check', 'Outer Line/Check'),  # 外层线路检查
                                 ('Graphic Plating', 'Graphic Plating'),  # 图形电镀
                                 ('Etching/Check', 'Etching/Check'),  # 蚀刻/检查
                                 ('Solder Mask/Check', 'Solder Mask/Check'),  # 阻焊/检查
                                 ('Character', 'Character'),  # 字符
                                 ('Surface Treatment', 'Surface Treatment'),  # 表面处理
                                 ('Test', 'Test'),  # 测试
                                 ('Forming', 'Forming'),  # 成形
                                 ('FQC', 'FQC'),
                                 ('FQA', 'FQA'),
                                 ('Package', 'Package'),  # 包装
                                 ], default='Cutting', string='PCB Product Flow')
    pcba_flow = fields.Selection([('Incoming', 'Incoming'),
                                  ('Raw Material Inspection', 'Raw Material Inspection'),
                                  ('Solder Paste Printing/Check', 'Solder Paste Printing/Check'),
                                  ('Pre-reflow Assurance', 'Pre-reflow Assurance'),
                                  ('Reflow', 'Reflow'),
                                  ('Quality Assurance Pro-reflow', 'Quality Assurance Pro-reflow'),
                                  ('Testing or Measurement', 'Testing or Measurement'),
                                  ('FQA', 'FQA'),
                                  ('Packing', 'Packing'),
                                  ('Final Store', 'Final Store')
                                  ], string='PCBA Product Flow', default='Incoming')
    check_quotation_line = fields.Boolean('Check PCB', compute='_check_quotation_line', sotre=True, default=False)

    @api.one
    @api.depends('quotation_line')
    def _check_quotation_line(self):
        self.ensure_one()
        if self.quotation_line:
            self.check_quotation_line = True

    @api.multi
    # 发送邮件
    def EmailReminderProgress(self):
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        # 选择模板
        template_id = ir_model_data.get_object_reference('product_flow', 'flow_email_sale_template')[1]
        compose_form_id = ir_model_data.get_object_reference('product_flow', 'flow_email_message_wizard')[1]
        ctx = {
            'default_model': 'sale.order',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'custom_layout': "product_flow.flow_mail_template",
            'proforma': self.env.context.get('proforma', False)
        }
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    def GetProductType(self):
        return self._context.get('product')


class InheritPersonalCenter(models.Model):
    _inherit = 'personal.center'


