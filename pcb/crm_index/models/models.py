# -*- coding: utf-8 -*-

from odoo import models, fields, api

SELECT_LIST = [
    ('calculation', 'Trial Calculation'),
    ('comfirm', 'Confirm'),
    ('cart', 'Shop Cart'),
    ('selected', 'Select Address'),
    ('pending', 'Pending review'),
]


# 将session 进行处理 原始表中session没有创建 这里记录IP 国家 城市才对
class ClientSessionRecord(models.Model):
    _name = 'session.record'
    _description = 'Client Session Record'
    _order = 'name desc, id desc'

    client_id = fields.Many2one('personal.center', 'Customer', ondelete='cascade', index=True)
    # name = fields.Many2one('personal.center', 'Customer', ondelete='cascade', index=True)
    # session_code = fields.Char('Session Coding')
    name = fields.Char('Session Coding')
    association_id = fields.Many2one('cpo_session_association', 'Session ID', ondelete='cascade')
    session_str = fields.Char('Conversation ID', index=True)
    session_time = fields.Datetime('Session Time')
    session_ip = fields.Char('Session IP')
    session_country = fields.Char('Country')
    session_city = fields.Char('City')
    behavior_ids = fields.One2many('behavior.record', 'session_id', 'Behavior Record')  # 行为记录
    source_ids = fields.One2many('session.source', 'session_id', 'Session Source')  # session 来源
    trial_ids = fields.One2many('trial_price.record', 'session_id', 'Website Trial Price Record')  # 试价记录

    def AutomaticProcessSession(self):
        self._cr.execute("SELECT NAME, SESSION_ID, USER_ID FROM CPO_SESSION_ASSOCIATION WHERE deal_with='unprocessed' GROUP BY NAME, SESSION_ID, USER_ID ORDER BY USER_ID LIMIT 1")
        x_sql = self._cr.dictfetchall()
        if not x_sql:
            return False
        x_sql = x_sql[0]
        self._cr.execute('SELECT ID FROM CPO_SESSION_ASSOCIATION WHERE USER_ID=%s AND NAME=%s ORDER BY ID DESC', (x_sql.get('user_id'), x_sql.get('name')))
        y_sql = self._cr.dictfetchall()
        for x_dict in y_sql:
            # 先去搜索行为记录 试价记录 以及来源
            trial_data = self.env['cpo_pcb_and_pcba_record'].search([('partner_info', '=', x_dict.get('id'))])
            behavior_data = self.env['website_cpo_index.cpo_website_source'].search([('session_id', '=', x_dict.get('id'))])
            # source_data = self.env['']


# session 的来源
class SessionSource(models.Model):
    _name = 'session.source'
    _description = 'Session Source'
    _order = 'id desc'

    session_id = fields.Many2one('session.record', 'Session Coding')
    name = fields.Char('Name', size=64, translate=True)
    source_url = fields.Char('Website')
    source_time = fields.Datetime('Source Time')
    # source_label = fields.Many2many('label')


# 行为记录
class BehaviorRecord(models.Model):
    _name = 'behavior.record'
    _description = 'Behavior Record'
    _order = 'id'

    session_id = fields.Many2one('session.record', 'Session Coding')
    do_time = fields.Datetime('Behavior Record Time')
    do_ip = fields.Char('Customer IP')
    do_city = fields.Char('City')


# 将PCB PCBA 试价记录进行整理
class TrialPriceRecord(models.Model):
    _name = 'trial_price.record'
    _description = 'Website Trial Price Record'
    _order = 'trial_time desc, client_id desc'

    record_id = fields.Many2one('cpo_pcb_and_pcba_record', 'Record', ondelete='cascade')
    client_id = fields.Many2one('personal.center', 'Customer', ondelete='cascade', index=True)
    client_ip = fields.Char('Customer IP')
    session_id = fields.Many2one('session.record', 'Session Coding')  # session_id 对象会改
    session_str = fields.Char('Conversation ID')  # session 会话
    country = fields.Char('Country')
    city = fields.Char('City')
    trial_type = fields.Char('Quotation Type')
    trial_number = fields.Integer('Number')
    trial_file = fields.Char('File Name')
    trial_width = fields.Float(digits=(16, 2), string='Width')
    trial_length = fields.Float(digits=(16, 2), string='Length')
    trial_thick = fields.Float(digits=(16, 2), string='Plate Thickness')
    trial_fee = fields.Float(digits=(16, 2), string='Quotation Price')
    trial_inner = fields.Float(digits=(16, 2), string='Inner Copper')
    trial_outer = fields.Float(digits=(16, 2), string='Outer Copper')
    trial_time = fields.Datetime('Recording Time')
    trial_layer = fields.Integer('Number Layers')
    trial_material = fields.Char('Substrate')
    trial_means = fields.Integer('Means Number')
    trial_pcs = fields.Char('Panel/PCS')
    trial_mask = fields.Char('Solder Mask Color')
    trial_text = fields.Char('Text Color')
    trial_surface = fields.Char('Surface Treatment')
    trial_test = fields.Char('E-Test')
    trial_bom = fields.Integer('Bom Type')
    trial_smt = fields.Integer('SMT Parts Quantity')
    trial_dip = fields.Integer('DIP Quantity')
    trial_side = fields.Integer('SMT Side')
    state = fields.Selection(SELECT_LIST, string='Trial Progress', default='calculation', compute='_depends_state', store=True)
    pcb_bool = fields.Boolean('Judge', default=False)
    pcba_bool = fields.Boolean('Judge', default=False)

    @api.depends('record_id.cpo_code')
    def _depends_state(self):
        for x_id in self:
            if x_id.record_id:
                x_id.state = x_id.record_id.cpo_code

    # 自动处理整理的数据
    def AutomaticProcessTrialPrice(self):
        data = self.env['cpo_pcb_and_pcba_record'].search([('deal_with', '=', 'unprocessed')], limit=80)
        for x in data:
            value = {
                'client_id': x.user_name.id,
                'client_ip': x.user_ip,
                'record_id': x.id,
                'session_id': x.partner_info.id,
                'session_str': x.session_id,
                'country': x.cpo_country,
                'city': x.cpo_city,
                'trial_type': x.order_type,
                'trial_number': x.quantity,
                'trial_file': x.file_name,
                'trial_width': x.width,
                'trial_length': x.lenght,
                'trial_thick': x.thickne,
                'trial_fee': x.total,
                'trial_time': x.cpo_time,
                'state': x.cpo_code,
            }
            # 判断 层数 外铜厚 材料 测试
            if int(x.layers) and float(x.outer_copper) and x.material and x.e_test:
                value.update({
                    'pcb_bool': True,
                    'trial_inner': x.inner_copper,
                    'trial_outer': x.outer_copper,
                    'trial_layer': x.layers,
                    'trial_material': x.material,
                    'trial_means': 0 if not x.item_qty else x.item_qty,
                    'trial_pcs': False if not x.panel_size else x.panel_size,
                    'trial_mask': x.mask_color,
                    'trial_text': x.silkscreen_color,
                    'trial_surface': x.surface,
                    'trial_test': x.e_test,
                })
            # 判断 bom种类 单双面
            if int(x.bom_type) and int(x.smt_side):
                value.update({
                    'pcba_bool': True,
                    'trial_bom': x.bom_type,
                    'trial_smt': x.smt_qty,
                    'trial_dip': x.dip_qty,
                    'trial_side': x.smt_side,
                })
            self.create(value)
        return True



