#-*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import time
import datetime
from dateutil.parser import parse


SELECT_INTENTION = [
    ('yes', 'Yes'),
    ('no', 'No'),
]

class CpoQuotationRecord(models.Model):
    """  """

    _name = "cpo_quotation_record"
    _order = "sequence desc, id desc"

    sequence = fields.Integer(string='Sequence')
    user_id = fields.Char(string="User ID")
    user_name = fields.Char(string="User Name")
    order_type = fields.Char(string="Order Type")
    material = fields.Char(string="Material")
    bom_type = fields.Char(string="Bom Type")
    quantity = fields.Integer(string="Quantity")
    width = fields.Float(string="Width")
    lenght = fields.Float(string="Length")
    smt_qty = fields.Integer(string="SMT parts quantity")
    dip_qty = fields.Integer(string="DIP quantity")
    thickne = fields.Float(string="Board thickness")
    inner_copper = fields.Char(string="Inner Copper")
    outer_copper = fields.Char(string="Outer Copper")
    layers = fields.Char(string="Layers")
    smt_side = fields.Char(string="SMT Side")
    file_name = fields.Char(string="File Name")
    mask_color = fields.Char(string="Solder Mask Color")
    silkscreen_color = fields.Char(string="Silkscreen Color")
    cpo_country = fields.Char(string="Country")
    user_ip = fields.Char(string="User IP")
    session_id = fields.Char(string="Session ID")
    cpo_city = fields.Char(string="City")
    total = fields.Float(string="Total")
    cpo_time = fields.Datetime(string="Last update time")
    datas = fields.Binary(string="Datas", attachment=True)


# 基础表
class WebsiteQuotationRecord(models.Model):
    _name = 'cpo_quotation_record_base'
    _order = "sequence desc, id desc"

    SELECT_LIST = [
        ('calculation', 'Trial calculation'),
        ('comfirm', 'Comfirm'),
        ('cart', 'Shop Cart'),
        ('selected', 'Select address'),
        ('pending', 'Pending review'),
    ]

    SELECT_DEALWITH = [
        ('unprocessed', 'Unprocessed'),
        ('processed', 'Processed')
    ]

    sequence = fields.Integer(string='Sequence')
    # user_name = fields.Char(string="User Name")
    user_name = fields.Many2one('personal.center', compute="_matching_users", string="Panter Name", store=True)
    partner_info = fields.Many2one('cpo_session_association', string="Session coding")
    user_info = fields.Char(related='partner_info.user_name', string="User Name")
    order_type = fields.Char(string="Order Type")
    quantity = fields.Integer(string="Quantity")
    width = fields.Float(string="Width")
    lenght = fields.Float(string="Length")
    thickne = fields.Float(string="Board thickness")
    file_name = fields.Char(string="File Name")
    cpo_country = fields.Char(string="Country")
    user_ip = fields.Char(string="User IP")
    session_id = fields.Char(string="Session ID")
    cpo_city = fields.Char(string="City")
    total = fields.Float(string="Total")
    cpo_time = fields.Datetime(string="Last update time")
    cpo_code = fields.Selection(SELECT_LIST, string="Status", default="calculation")
    deal_with = fields.Selection(SELECT_DEALWITH, string="Deal with", default="unprocessed", index=True)
    file_ids = fields.Many2many('ir.attachment', string='Files')

    @api.one
    @api.depends('partner_info', 'partner_info.customer_name', 'partner_info.user_id')
    def _matching_users(self):
        if self.partner_info.user_id != self.env.ref("base.public_user").id:
            self.user_name = self.partner_info.customer_name.id


# PCB 报价记录表
class CpoPCBQuotationRecord(models.Model):
    _name = 'cpo_pcb_record'
    _inherits = {
        'cpo_quotation_record_base': 'record_pcb_id'
    }
    _order = "sequence desc, id desc"

    sequence = fields.Integer(string='Sequence')
    panel_size = fields.Char(string="Panel size")
    item_qty = fields.Char(string="Item Quantity")
    material = fields.Char(string="Material")
    inner_copper = fields.Char(string="Inner Copper")
    outer_copper = fields.Char(string="Outer Copper")
    layers = fields.Char(string="Layers")
    mask_color = fields.Char(string="Solder Mask Color")
    silkscreen_color = fields.Char(string="Silkscreen Color")
    surface = fields.Char(string='Surface Treatment')
    e_test = fields.Char(string='E-Test')
    flex_number = fields.Integer(string="Flex Number")
    golden_finger_thickness = fields.Integer(string="Golden finger golden thickness")
    record_pcb_id = fields.Many2one(
        'cpo_quotation_record_base', 'Base record',
        auto_join=True, index=True, ondelete="cascade", required=True)
    cpo_intention = fields.Selection(SELECT_INTENTION, string="PCBA Intention", default="no")
    Semi_hole = fields.Char(string='Semi hole')
    Edge_plating = fields.Char(string='Edge plating')
    Impedance = fields.Char(string='Impedance')
    Press_fit = fields.Char(string='Press fit')
    Peelable_mask = fields.Char(string='Peelable mask')
    Carbon_oil = fields.Char(string='Carbon oil')
    Min_line_width = fields.Char(string='Min line width')
    Min_line_space = fields.Char(string='Min line space')
    Min_aperture = fields.Char(string='Min aperture')
    Total_holes = fields.Char(string='Total holes')
    Copper_weight_wall = fields.Char(string='Copper weight wall')
    Number_core = fields.Char(string='Number core')
    PP_number = fields.Char(string='PP number')
    Total_test_points = fields.Char(string='Total test points')
    Blind_and_buried_hole = fields.Char(string='Blind and buried hole')
    Blind_hole_structure = fields.Char(string='Blind hole structure')
    Depth_control_routing = fields.Char(string='Depth control routing')
    Number_back_drilling = fields.Char(string='Number back drilling')
    Countersunk_deep_holes = fields.Char(string='Countersunk deep holes')
    Laser_drilling = fields.Char(string='Laser drilling')
    Inner_hole_line = fields.Char(string='Inner hole line')
    The_space_for_drop_V_cut = fields.Char(string='The space for drop V_cut')

    @api.multi
    def cpo_seaerch_pcba_intention(self):
        """
        查找有PCBA意向的记录
        :return:
        """
        session_coding = self.partner_info.name
        user_name = self.user_name
        return {
            'name': 'PCBA Intention',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form, tree',
            'res_model': 'cpo_pcba_record',
            'views': [(False, 'tree')],
            'view_id': False,
            'domain': [('partner_info', '=', session_coding), ('user_name', '=', user_name)],
            'context': {'group_by': 'partner_info', 'search_default_customer': session_coding}
        }

# PCBA 报价记录表
class CpoPCBAQuotationRecord(models.Model):
    _name = 'cpo_pcba_record'
    _inherits = {
        'cpo_quotation_record_base': 'record_pcba_id'
    }
    _order = "sequence desc, id desc"

    sequence = fields.Integer(string='Sequence')
    bom_type = fields.Char(string="Bom Type")
    smt_qty = fields.Integer(string="SMT parts quantity")
    dip_qty = fields.Integer(string="DIP quantity")
    smt_side = fields.Char(string="SMT Side")
    record_pcba_id = fields.Many2one(
        'cpo_quotation_record_base', 'Base record',
        auto_join=True, index=True, ondelete="cascade", required=True)
    cpo_intention = fields.Selection(SELECT_INTENTION, string="PCB Intention", default="no")

    @api.multi
    def cpo_seaerch_pcb_intention(self):
        """
        查找有PCB意向的记录
        :return:
        """
        session_coding = self.partner_info.name
        user_name = self.user_name
        return {
            'name': 'PCBA Intention',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form, tree',
            'res_model': 'cpo_pcb_record',
            'views': [(False, 'tree')],
            'view_id': False,
            'domain': [('partner_info', '=', session_coding), ('user_name', '=', user_name)],
            'context': {'group_by': 'partner_info', 'search_default_customer': session_coding}
        }

# PCB and PCBA 报价记录表
class CpoPCBAAndPCBQuotationRecord(models.Model):
    _name = 'cpo_pcb_and_pcba_record'
    _inherits = {
        'cpo_quotation_record_base': 'record_pcb_pcba_id'
    }
    _order = "sequence desc, id desc"

    sequence = fields.Integer(string='Sequence')
    panel_size = fields.Char(string="Panel size")
    item_qty = fields.Char(string="Item Quantity")
    material = fields.Char(string="Material")
    inner_copper = fields.Char(string="Inner Copper")
    outer_copper = fields.Char(string="Outer Copper")
    layers = fields.Char(string="Layers")
    mask_color = fields.Char(string="Solder Mask Color")
    silkscreen_color = fields.Char(string="Silkscreen Color")
    surface = fields.Char(string='Surface Treatment')
    e_test = fields.Char(string='E-Test')
    flex_number = fields.Integer(string="Flex Number")
    golden_finger_thickness = fields.Integer(string="Golden finger golden thickness")
    bom_type = fields.Char(string="Bom Type")
    smt_qty = fields.Integer(string="SMT parts quantity")
    dip_qty = fields.Integer(string="DIP quantity")
    smt_side = fields.Char(string="SMT Side")
    record_pcb_pcba_id = fields.Many2one(
        'cpo_quotation_record_base', 'Base record',
        auto_join=True, index=True, ondelete="cascade", required=True)


class CpoServiceProtocRecord(models.Model):
    _name = 'cpo_service_record'
    _inherits = {
        'cpo_quotation_record_base': 'record_service_id'
    }
    _order = "sequence desc, id desc"

    sequence = fields.Integer(string='Sequence')
    user_id = fields.Char(string="User ID")
    record_service_id = fields.Many2one(
        'cpo_quotation_record_base', 'Base record',
        auto_join=True, index=True, ondelete="cascade", required=True)

class CpoQuantationParrner(models.Model):
    _name = 'cpo_session_association'
    _order = 'id desc'
    user_list = {}

    @api.model
    def check_login_data(self, session_user):
        """
        用户从Public user 转成普通用户（登录）时，返回True，更新数据
        :param session_res:
        :return:
        """
        if not session_user:
            return self
        if session_user.keys()[0] not in self.user_list.keys():
            self.user_list[session_user.keys()[0]] = session_user.get(session_user.keys()[0])  # 不存在就添加
        else:
            now_uid = session_user.get(session_user.keys()[0]).keys()[0]
            list_uid = self.user_list.get(session_user.keys()[0]).keys()[0]
            # session相同时，且不能为Public user（游客）时，返回True更新
            if now_uid != list_uid and now_uid != 4:
                self.user_list[session_user.keys()[0]].update({
                    now_uid: fields.Datetime.now()
                })
                return True
            else:
                self.user_list[session_user.keys()[0]][list_uid] = fields.Datetime.now()
        return False

    @api.model
    def delete_session_time_out(self):
        now_time = fields.Datetime.now()
        self.user_list = dict([(x[0], x[1]) for x in self.user_list.items() if (parse(now_time) - parse(x[1].values()[0])).total_seconds() <= 3600])

    @api.model
    def _get_now_time(self):
        now_time = datetime.datetime.now()
        return now_time

    SELECT_DEALWITH = [
        ('unprocessed', 'Unprocessed'),
        ('processed', 'Processed')
    ]

    name = fields.Char(string="Session")
    user_info = fields.One2many('cpo_quotation_record_base', 'partner_info', string="Session")
    partner_name = fields.Many2one('res.partner', string="Panter Name")
    customer_name = fields.Many2one('personal.center', string="Panter Name")
    user_name = fields.Char(string="User Name")
    user_id = fields.Integer(string="User ID")
    session_id = fields.Char(string="Session ID")
    cpo_time = fields.Datetime(string="Last update time", defualt=_get_now_time)
    # deal_with = fields.Selection(SELECT_DEALWITH, string="Deal with", default="unprocessed", index=True)

    @api.model
    def check_session_info(self, vals):
        # 查找个人中心
        data = None
        get_customer = self.env['personal.center'].search([('user_id', '=', vals.get('user_id'))])
        if get_customer:
            customer = get_customer.id
        else:
            customer = None
        values = {
            'name': hash(vals.get('session_id')),
            'customer_name': customer,
            'user_name': vals.get('user_name'),
            'user_id': vals.get('user_id'),
            'session_id': vals.get('session_id'),
            'cpo_time': fields.Datetime.now()
        }
        get_data = self.sudo().search(
            [('session_id', '=', values.get('session_id')), ('name', '=', values.get('name'))])
        if get_data:
            data = get_data[-1]
        else:
            data = self.create(values)

        return {
            'get_customer': customer,
            'get_data': data.id
        }

    def update_user_info(self, vals):
        """
        用户从pubic user 登录了，更新数据
        :param vals:
        :return:
        """
        get_customer = self.env['personal.center'].sudo().search([('user_id', '=', vals.get('user_id'))])
        values = {
            'name': hash(vals.get('session_id')),
            'customer_name': get_customer.id,
            'user_name': vals.get('user_name'),
            'user_id': vals.get('user_id'),
            'session_id': vals.get('session_id'),
            'cpo_time': datetime.datetime.now()
        }
        get_data = self.sudo().search(
            [('session_id', '=', values.get('session_id')), ('name', '=', values.get('name'))])
        if get_data:
            if len(get_data) > 1:
                for gd in get_data:
                    gd.write({
                        'customer_name': get_customer.id,
                        'user_name': vals.get('user_name'),
                        'user_id': vals.get('user_id'),
                    })
            else:
                get_data.write({
                    'customer_name': get_customer.id,
                    'user_name': vals.get('user_name'),
                    'user_id': vals.get('user_id')
                })
            uid = get_data[-1].customer_name
            source_id = self.sudo().env['website_cpo_index.cpo_website_source'].sudo().search([('user_id', '=', uid.id)])
            source_list = None
            if source_id:
                source_list = source_id.filtered(lambda x: x.customer_related != None)
            if source_list:
                if uid.website_source:
                    c_related = self.env['website_cpo_index.cpo_partner_source'].matching_website(uid.website_source)
                    self.update_login_user_data(source_id, c_related)
                else:
                    uid.website_source = source_list[-1].cpo_source
                    c_related = source_list[-1].customer_related.id
                    self.update_login_user_data(source_id, c_related)
        return True

    def update_login_user_data(self, obj, related_id):
        for sid in obj:
            partner_source = self.env['website_cpo_index.cpo_partner_source'].matching_website(sid.cpo_source)
            sid.customer_related = partner_source
