# -*- coding: utf-8 -*-
"""
    这是优惠模块 暂时分两块 时间优惠 和 满减优惠
"""
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
from time import time
import random, string


class preferential_cpo_time_and_money(models.Model):
    _name = 'preferential.cpo_time_and_money'
    _description = 'Public offers, time and amount'
    _order = 'sequence, id desc'

    ACTIVE_STATUS = [
        ('draft', 'Draft'),  # 草稿
        ('force_no_started', 'Effective yet started'),  # 已生效未开始
        ('started_and_started', 'Effective and started'),  # 已生效且已开始
        ('invalid_over', 'Invalid and over'),  # 已失效且已结束
        ('cancel', 'Forced cancellation'),  # 取消
    ]

    name = fields.Char('Activity tag', readonly=True, size=64, translate=True)
    name_title = fields.Char('Activity theme', required=True, size=64, translate=True)
    cpo_time_id = fields.One2many('preferential.cpo_customer_contact', 'time_money_id', 'Participation time customers', readonly=True, domain=[('cpo_voucher_bool', '=', False)])  # 参与时间优惠客户
    cpo_voucher_id = fields.One2many('preferential.cpo_customer_contact', 'time_money_id', 'Participate in coupon customers', readonly=True, domain=[('cpo_voucher_bool', '=', True)])  # 参与优惠券客户
    cpo_date_bool = fields.Boolean('Time offer', index=True)  # 时间段优惠
    cpo_amount_bool = fields.Boolean('Full reduction offer', index=True)  # 满减优惠
    cpo_start_time = fields.Date('Starting time', required=True)
    cpo_end_time = fields.Date('End Time', required=True)
    cpo_voucher_number = fields.Integer('Number of coupons', required=True)
    volume_level_ids = fields.Many2many('cam.volume.level', string='Volume level')
    silkscreen_color_ids = fields.Many2many('cam.ink.color', string='Silkscreen color', domain=[('silk_screen', '=', True)])
    surface_process_ids = fields.Many2many('cam.surface.process', string='Surface process')
    via_process_ids = fields.Many2many('cam.via.process', string='Via process')
    special_process_ids = fields.Many2many('cam.special.process', string='Special process')
    special_material_ids = fields.Many2many('cam.special.material', string='Special material')
    material_brand_ids = fields.Many2many('cam.material.brand', string='Material brand')
    layer_number_ids = fields.Many2many('cam.layer.number', string='Layer number')
    base_type_ids = fields.Many2many('cam.base.type', string='Base type')
    acceptance_criteria_ids = fields.Many2many('cam.acceptance.criteria', string='Acceptance criteria')
    cpo_offer_bool = fields.Boolean('Participation offer')
    cpo_all_offer_bool = fields.Boolean('All participation offer')
    cpo_shared_bool = fields.Boolean('Shared coupon')
    cpo_no_shared_bool = fields.Boolean('Not Shared coupon')
    state = fields.Selection(ACTIVE_STATUS, default='draft', readonly=True, string='status', group_expand='_expand_states')
    cpo_creation_time = fields.Datetime('Activity creation time')
    active = fields.Boolean('Active', default=True)  # 处理强制取消的  !!
    cpo_invalid_over_bool = fields.Boolean('Invalid over', index=True)  # 优惠活动结束为True !!
    cpo_check_time_bool = fields.Boolean("Check time", compute='_definite_time_ware', store=False)
    cpo_discount_type = fields.Selection([('%', '%'), ('money', 'money')], 'Discount type', default='%', required=True)  # 折扣类型
    cpo_no_card_bool = fields.Boolean('No card', help='Free shipping, No card product discounts')  # 无门槛
    cpo_no_card_money = fields.Float('Less/Discount', digits=(16, 2), required=True)
    cpo_card_bool = fields.Boolean('Card', help='Free shipping, Card product discounts')  # 有门槛
    cpo_card_term = fields.Float('Full amount', digits=(16, 2), required=True)
    cpo_card_money = fields.Float('Less/Discount', digits=(16, 2), required=True)
    cpo_remarks = fields.Text('Remarks')
    cpo_trading_volume = fields.Integer('Trading volume', compute='_coupon_trading_volume', store=False)  # 时间段优惠的交易量
    cpo_coupon_volume = fields.Integer('Coupon volume', compute='_coupon_trading_volume', store=False)  # 优惠券的使用数量
    color = fields.Integer('Color Index', compute='_state_color_replace', store=False)
    cpo_state = fields.Selection([('no_started', 'has not started'),
                                  ('using', 'Using'),
                                  ('invalid', 'Invalid')], compute='_state_color_replace', store=False)
    cpo_physical_code_bool = fields.Boolean('Coupon physics code')  # 优惠券物理码
    cpo_allow_sharing_bool = fields.Boolean('Allow sharing')  # 允许分享
    cpo_limit_days = fields.Integer('Limited time days', required=True)  # 当客户分享优惠券时，此优惠券在什么时间内领取有效
    sequence = fields.Integer('Sequence')
    cpo_display = fields.Boolean('Priority display in web pages', index=True)  # 优先显示网页中
    cpo_full = fields.Boolean('Full', index=True)  # 识别优惠券是不是领完了
    cpo_public_coupon_bool = fields.Boolean('Due to distribution to other websites', default=False)
    new_user_bool = fields.Boolean('For New Users', index=True, default=False)

    @api.depends('color', 'cpo_state')
    # 看板颜色自动更换
    def _state_color_replace(self):
        for x_id in self:
            # x_id = self.id
            self._cr.execute("""SELECT state FROM preferential_cpo_time_and_money WHERE id = %s""", (x_id.id,))
            dicts = self._cr.dictfetchall()[0]
            if dicts['state'] in ['draft', 'cancel']:
                pass
            elif dicts['state'] == 'force_no_started':
                x_id.update({'color': 6, 'cpo_state': 'no_started'})
            elif dicts['state'] == 'started_and_started':
                x_id.update({'color': 9, 'cpo_state': 'using'})
            elif dicts['state'] == 'invalid_over':
                x_id.update({'color': 1, 'cpo_state': 'invalid'})

    # 看板中 统计出交易量 和 优惠券使用量
    @api.depends('cpo_trading_volume', 'cpo_coupon_volume')
    def _coupon_trading_volume(self):
        for x_id in self:
            # x_id = self.id
            if x_id.cpo_amount_bool:
                self._cr.execute("""SELECT id FROM preferential_cpo_customer_contact WHERE 
                                 time_money_id = %s and cpo_use_bool = %s and cpo_voucher_bool = %s""", (x_id.id, True, True))
                dicts = self._cr.dictfetchall()
                x_id.update({'cpo_coupon_volume': len(dicts)})
            else:
                self._cr.execute("""SELECT id FROM preferential_cpo_customer_contact WHERE time_money_id = %s 
                                 and cpo_voucher_bool = %s""", (x_id.id, False))
                dicts = self._cr.dictfetchall()
                x_id.update({'cpo_trading_volume': len(dicts)})

    @api.onchange('cpo_date_bool', 'cpo_no_card_bool', 'cpo_no_shared_bool', 'cpo_offer_bool')
    def _onchange_not_feasible_bool(self):
        if self.cpo_no_card_bool:
            self.update({'cpo_no_card_bool': True, 'cpo_card_bool': False})
        if self.cpo_no_shared_bool:
            self.update({'cpo_shared_bool': False, 'cpo_no_shared_bool': True})
        if self.cpo_offer_bool:
            self.update({'cpo_offer_bool': True, 'cpo_all_offer_bool': False})
        if self.cpo_date_bool:
            self.update({'cpo_date_bool': True, 'cpo_amount_bool': False})

    @api.onchange('cpo_amount_bool', 'cpo_card_bool', 'cpo_shared_bool', 'cpo_all_offer_bool')
    def _onchange_feasible_bool(self):
        if self.cpo_card_bool:
            self.update({'cpo_no_card_bool': False, 'cpo_card_bool': True})
        if self.cpo_shared_bool:
            self.update({'cpo_shared_bool': True, 'cpo_no_shared_bool': False})
        if self.cpo_all_offer_bool:
            self.select_all_product()
            self.update({'cpo_offer_bool': False, 'cpo_all_offer_bool': True})
        if self.cpo_amount_bool:
            self.update({'cpo_date_bool': False, 'cpo_amount_bool': True})

    def select_all_product(self):
        acceptance_criteria_ids = self.acceptance_criteria_ids.search([]).ids
        silkscreen_color_ids = self.silkscreen_color_ids.search([('silk_screen', '=', True)]).ids
        special_material_ids = self.special_material_ids.search([]).ids
        special_process_ids = self.special_process_ids.search([]).ids
        surface_process_ids = self.surface_process_ids.search([]).ids
        material_brand_ids = self.material_brand_ids.search([]).ids
        volume_level_ids = self.volume_level_ids.search([]).ids
        layer_number_ids = self.layer_number_ids.search([]).ids
        via_process_ids = self.via_process_ids.search([]).ids
        base_type_ids = self.base_type_ids.search([]).ids
        return self.update({
            'acceptance_criteria_ids': [(6, 0, acceptance_criteria_ids)] if not self.acceptance_criteria_ids else self.acceptance_criteria_ids.ids,
            'silkscreen_color_ids': [(6, 0, silkscreen_color_ids)] if not self.silkscreen_color_ids else self.silkscreen_color_ids.ids,
            'special_material_ids': [(6, 0, special_material_ids)] if not self.special_material_ids else self.special_material_ids.ids,
            'special_process_ids': [(6, 0, special_process_ids)] if not self.special_process_ids else self.special_process_ids.ids,
            'surface_process_ids': [(6, 0, surface_process_ids)] if not self.surface_process_ids else self.surface_process_ids.ids,
            'material_brand_ids': [(6, 0, material_brand_ids)] if not self.material_brand_ids else self.material_brand_ids.ids,
            'volume_level_ids': [(6, 0, volume_level_ids)] if not self.volume_level_ids else self.volume_level_ids.ids,
            'layer_number_ids': [(6, 0, layer_number_ids)] if not self.layer_number_ids else self.layer_number_ids.ids,
            'via_process_ids': [(6, 0, via_process_ids)] if not self.via_process_ids else self.via_process_ids.ids,
            'base_type_ids': [(6, 0, base_type_ids)] if not self.base_type_ids else self.base_type_ids.ids,
        })

    @api.onchange('cpo_voucher_number', 'cpo_no_card_money', 'cpo_discount_type', 'cpo_card_term', 'cpo_card_money')
    def _onchange_number_coupons(self):
        if self.cpo_voucher_number < 0:
            self.update({'cpo_voucher_number': 0})
            return {
                'warning': {
                    'title': _("Incorrect 'Number of coupons'"),
                    'message': _("The number of coupons is at least one"),
                },
            }
        if self.cpo_no_card_money < 0:
            self.update({'cpo_no_card_money': 0})
            return {
                'warning': {
                    'title': _("Incorrect 'No card money'"),
                    'message': _("Please set the discount or discount amount without threshold."),
                },
            }
        if self.cpo_card_term < 0:
            self.update({'cpo_card_term': 0})
            return {
                'warning': {
                    'title': _("Incorrect 'Card term'"),
                    'message': _("Please set the threshold correctly."),
                },
            }
        if self.cpo_card_money < 0:
            self.update({'cpo_card_money': 0})
            return {
                'warning': {
                    'title': _("Incorrect 'Card money'"),
                    'message': _("Please set the discount or discount amount after the full reduction."),
                },
            }
        if self.cpo_discount_type is False:
            self.update({'cpo_discount_type': '%'})
            return {
                'warning': {
                    'title': _("Incorrect 'Discount type'"),
                    'message': _("Please set the offer type correctly."),
                },
            }

    @api.onchange('cpo_start_time', 'cpo_end_time')
    def _onchange_start_end_time(self):
        if self.cpo_end_time and self.cpo_start_time:
            preferential_time_db = self.search([('cpo_amount_bool', '=?', self.cpo_amount_bool),
                                                ('cpo_date_bool', '=?', self.cpo_date_bool),
                                                ('cpo_start_time', '>=', self.cpo_start_time),
                                                ('cpo_end_time', '<=', self.cpo_end_time),
                                                ('state', 'not in', ('draft', 'cancel', 'invalid_over'))])
            if self.cpo_amount_bool:
                if preferential_time_db:
                    return {
                        'warning': {
                            'title': _("Warm Prompt"),
                            'message': _(
                                "The time period discount you set coincides with other times. For details, please click the button on the side."),
                        },
                    }
            elif self.cpo_date_bool:
                if preferential_time_db:
                    return {
                        'warning': {
                            'title': _("Warm Prompt"),
                            'message': _(
                                "The coupons you set will coincide with the time of other coupons. For details, please click the button on the side."),
                        },
                    }

    @api.model  # 暂时ok不用理 处理好选择
    def create(self, vals):
        value_name, name_id = None, None
        create_time = datetime.strptime(fields.Datetime.now(), '%Y-%m-%d %H:%M:%S') + timedelta(hours=8)
        if vals.get('cpo_date_bool') or vals.get('cpo_amount_bool'):
            if not vals.get('cpo_shared_bool') and not vals.get('cpo_no_shared_bool'):
                raise ValidationError(_('Please set "Share with other offers"'))
            if not vals.get('cpo_offer_bool') and not vals.get('cpo_all_offer_bool'):
                raise ValidationError(_('Please set "Promotional Participation Settings"'))
            if not vals.get('cpo_card_bool') and not vals.get('cpo_no_card_bool'):
                raise ValidationError(_('Please select the offer "there is no threshold type"'))
            name_ids = self.search([('cpo_date_bool', '=?', vals.get('cpo_date_bool')),
                                    ('cpo_amount_bool', '=?', vals.get('cpo_amount_bool')),
                                    ('name', '!=', False)]).ids
            if name_ids:
                name_id = self.browse(max(name_ids)).name
            a_two = ''.join(fields.Datetime.now()[0:7].split('-'))
            a_three = '01' if not name_id else ('0' + str(int(name_id[-2:])+1))
            if name_id and len(str(int(name_id[-2:])+1)) > 1:
                a_three = str(int(name_id[-2:])+1)
            a_one = 'SJ' if vals.get('cpo_date_bool') else 'JE'
            value_name = a_one + a_two + a_three
        if vals.get('cpo_amount_bool'):
            if vals.get('cpo_voucher_number') == 0:
                raise ValidationError(_('Please set "Number of Coupons"'))
        if vals.get('cpo_card_bool'):
            if vals.get('cpo_card_term') == 0 or vals.get('cpo_card_money') == 0:
                raise ValidationError(_('Please check "There is a threshold condition amount; discount or discount amount after full reduction"'))
        if vals.get('cpo_no_card_bool'):
            if vals.get('cpo_no_card_money') == 0:
                raise ValidationError(_('Please check "No threshold discount or discount amount"'))
        if vals.get('cpo_allow_sharing_bool'):
            if vals.get('cpo_limit_days') == 0:
                raise ValidationError(_("You have chosen to allow sharing, please also fill in the number of days in the box, if you don't understand the question mark on the side you can click"))
        vals.update({'cpo_creation_time': create_time, 'name': value_name})
        return super(preferential_cpo_time_and_money, self).create(vals)

    @api.multi
    def write(self, vals):
        # 先进行数据更新保存
        res = super(preferential_cpo_time_and_money, self).write(vals)
        if ('cpo_date_bool' or 'cpo_amount_bool') in vals.keys() and 'active' not in vals.keys():
            self.check_form_data()
            self.update_name_title()
        return res

    # 检查form表单相关所需数据
    def check_form_data(self):
        if self.cpo_date_bool or self.cpo_amount_bool:
            if not self.cpo_card_bool and not self.cpo_no_card_bool:
                raise ValidationError(_('Please select the offer "there is no threshold type"'))
            if not self.cpo_shared_bool and not self.cpo_no_shared_bool:
                raise ValidationError(_('Please set "Share with other offers"'))
            if not self.cpo_offer_bool and not self.cpo_all_offer_bool:
                raise ValidationError(_('Please set "Promotional Participation Settings"'))
        if self.cpo_amount_bool:
            if self.cpo_voucher_number == 0:
                raise ValidationError(_('Please set "Number of Coupons"'))
        if self.cpo_card_bool:
            if self.cpo_card_term == 0 or self.cpo_card_money == 0:
                raise ValidationError(_('Please check "There is a threshold condition amount; discount or discount amount after full reduction"'))
        if self.cpo_no_card_bool:
            if self.cpo_no_card_money == 0:
                raise ValidationError(_('Please check "No threshold discount or discount amount"'))
        if self.cpo_allow_sharing_bool:
            if self.cpo_limit_days == 0:
                raise ValidationError(_("You have chosen to allow sharing, please also fill in the number of days in the box, if you don't understand the question mark on the side you can click"))

    # 活动生效 - 进行 优惠券数据的创建
    @api.multi
    def button_force(self):
        if not self.cpo_date_bool and not self.cpo_amount_bool:
            raise ValidationError(_('Please set "time period offer or full reduction offer"!'))
        self.check_form_data()
        self.update_name_title()
        if self.cpo_amount_bool:
            time_money_id = self.id
            number_1 = 1
            number = self.cpo_voucher_number
            ran_char = ''
            uid = self._uid
            cpo_physics_bool = self.cpo_physical_code_bool
            # 十万数据大概30秒 - 先这样
            while number_1 <= number:
                if cpo_physics_bool:
                    num = random.randint(1, 10)
                    slc_num = [random.choice(string.digits) for i in range(num)]
                    slc_letter = [random.choice(string.ascii_letters) for i in range(10 - num)]
                    ran_char = ''.join(random.sample(slc_letter+slc_num, 8))
                self.env.invalidate_all()
                self._cr.execute("""
                    INSERT INTO preferential_cpo_customer_contact (create_date,write_date,cpo_numeric,time_money_id,
                    cpo_voucher_bool,create_uid,write_uid,cpo_use_bool,cpo_coupon_bool,cpo_physical_code,active
                    ) VALUES ((timestamp '%s'),(timestamp '%s'),'%s','%d',True,'%d','%d',False,False,'%s',True)""" %
                    (datetime.utcnow().isoformat(), datetime.utcnow().isoformat(),
                     number_1, time_money_id, uid, uid, ran_char))
                number_1 += 1
        return self.update({'state': 'force_no_started'})

    # 强制取消 - 页面不能显示 - 活跃度改为False
    @api.multi
    def button_cancel(self):
        time_money_id = self.id
        self.update({'state': 'cancel', 'cpo_display': False, 'active': False})
        self.env.invalidate_all()
        self._cr.execute("""
            UPDATE preferential_cpo_customer_contact SET active=False WHERE time_money_id='%s'
        """ % time_money_id)
        return True

    # 活动重置 - 进行删除
    @api.multi
    def button_reset(self):
        if self.cpo_amount_bool:
            time_money_id = self.id
            self.env.invalidate_all()
            self._cr.execute("""
                DELETE FROM preferential_cpo_customer_contact WHERE time_money_id='%s' and cpo_voucher_bool=True
            """ % time_money_id)
        return self.update({'state': 'draft'})

    # 活动开始 - 更改状态 显示在页面中
    @api.multi
    def button_begins(self):
        return self.update({'state': 'started_and_started', 'cpo_display': True})

    # 失效且结束 - 更改状态 不显示在页面中 同时活动失效为True
    @api.multi
    def button_invalid(self):
        return self.update({'state': 'invalid_over', 'cpo_invalid_over_bool': True, 'cpo_display': False})

    # 进行name编号
    def update_name_title(self):
        name_id = None
        name_ids = self.search([('cpo_date_bool', '=?', self.cpo_date_bool),
                                ('cpo_amount_bool', '=?', self.cpo_amount_bool),
                                ('id', '!=', self.id),
                                ('name', '!=', False)]).ids
        if name_ids:
            name_id = self.browse(max(name_ids)).name
        a_two = ''.join(fields.Datetime.now()[0:7].split('-'))
        a_three = '01' if not name_id else ('0' + str(int(name_id[-2:]) + 1))
        if name_id and len(str(int(name_id[-2:]) + 1)) > 1:
            a_three = str(int(name_id[-2:]) + 1)
        a_one = 'SJ' if self.cpo_date_bool else 'JE'
        value_name = a_one + a_two + a_three if self.cpo_date_bool or self.cpo_amount_bool else None
        create_time = datetime.strptime(fields.Datetime.now(), '%Y-%m-%d %H:%M:%S') + timedelta(hours=8)
        self.update({'cpo_creation_time': create_time, 'name': value_name})
        return True

    # 只允许删除草稿 - 已失效且已结束 - 为后期做数据分析
    @api.multi
    def unlink(self):
        for x_id in self:
            if x_id.state != 'draft':
                raise ValidationError(_("Allow only deletion of activity status for draft status"))
            else:
                super(preferential_cpo_time_and_money, x_id).unlink()
        return True

    # 视图弹框 查看时间段优惠 创建了多少
    def check_date(self):
        view_id = self.env.ref('cpo_preferential.views_check_date_tree').id
        return {
            'name': _('Time of all time periods'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'preferential.cpo_time_and_money',
            'views': [[view_id, 'tree']],
            'target': 'new',
            'domain': [('cpo_date_bool', '=', True), ('name', '!=', False), ('state', 'not in', ('draft', 'cancel', 'invalid_over'))],
        }

    # 视图弹框 查看优惠券 创建了多少
    def check_amount(self):
        view_id = self.env.ref('cpo_preferential.views_check_amount_tree').id
        return {
            'name': _('Time of all coupons'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'preferential.cpo_time_and_money',
            'views': [[view_id, 'tree']],
            'target': 'new',
            'domain': [('cpo_amount_bool', '=', True), ('name', '!=', False), ('state', 'not in', ('draft', 'cancel', 'invalid_over'))],
        }

    # 视图跳转 查看form视图表单中的活动详情
    def check_view_form_date_amount(self):
        view_id = self.env.ref('cpo_preferential.preferential_activity_plan_form').id
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'preferential.cpo_time_and_money',
            'res_id': self.id,
            'views': [[view_id, 'form']],
        }

    # 后台中触发 点击 进行时间检查 同时自动更改状态、是否失效、是否可以显示在页面中
    # @api.one
    @api.depends('cpo_check_time_bool')
    def _definite_time_ware(self):
        for x_id in self:
            # x_id = self.id
            now = time()
            utc_tm = datetime.utcfromtimestamp(now)
            self._cr.execute("""SELECT state,cpo_start_time,cpo_end_time
                             FROM preferential_cpo_time_and_money WHERE id = %s""", (x_id.id,))
            dicts = self._cr.dictfetchall()[0]
            if dicts['state'] == 'force_no_started':
                if dicts['cpo_start_time'] <= str(utc_tm)[0:10] <= dicts['cpo_end_time']:
                    x_id.write({'state': 'started_and_started', 'cpo_display': True})
                elif dicts['cpo_end_time'] < str(utc_tm)[0:10]:
                    x_id.write({'state': 'invalid_over', 'cpo_invalid_over_bool': True, 'cpo_display': False})
            elif dicts['state'] == 'started_and_started':
                if dicts['cpo_end_time'] < str(utc_tm)[0:10]:
                    x_id.write({'state': 'invalid_over', 'cpo_invalid_over_bool': True, 'cpo_display': False})
        return True

    # 预留 还没有写好 - 这是做数据分析的 但是没有写好
    def jump_another_model(self):
        customer_contact = self.env['preferential.cpo_customer_contact']
        customer_contact.time_coupon_date_analysis({"x_id": self.id})
        view_id = self.env.ref('cpo_preferential.preferential_data_analysis_graph_view').id
        return {
            'name': _('Single element data analysis chart'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'graph',
            'res_model': 'preferential.cpo_customer_contact',
            'views': [[view_id, 'graph']],
            'domain': [('id', 'in', self.ids)],
        }

    # 用返回错误的方式进行提示 - 告诉使用者优惠券转让的使用法则 # 同时请记得填写分享的限时天数
    def inform_allow_sharing(self):
        raise ValidationError(_(
            u'Coupon physical code and allowed to share; two can be selected, you can also choose!\n'
            u'Allow sharing: \n'
            u'Allow old customers to share coupons with new customers who are not'
            u' using our website!\n'
            u'Please also remember to fill in the limited hours of sharing.\n'  
            u'PS:Time-limited days: \n'
            u'refers to the moment when the old customer clicks to share the coupon.\n'
            u'If you receive it within the number of days you specify, '
            u'it will be considered successful; \n'
            u'if the time limit is exceeded, \n'
            u'the new customer will not be able to get the coupon shared by the old customer, \n'
            u'but the coupon of the old customer is not invalid!'
        ))

    # 用返回错误的方式进行提示 - 告诉使用者物理优惠券法则
    def inform_coupon_physics_code(self):
        raise ValidationError(_(
            u'Coupon physical code and allowed to share; two can be selected, you can also choose!\n'
            u'Coupon physics code: \n'
            u'The coupon will be generated in paper or other form for distribution;\n'
            u'new and old customers can use'
        ))

    # 返回看板中的 状态列
    def _expand_states(self, states, domain, order):
        return [key for key, val in type(self).state.selection if key not in ('draft', 'cancel')]

    # 手动操作 页面可否显示某优惠券
    def display_or_withdraw(self):
        if self.cpo_display:
            self.update({'cpo_display': False})
        else:
            self.update({'cpo_display': True})

    # 前端接口 - 前端专用
    @api.model
    def get_preferential_price(self, args):
        return self.get_preferential_settings(args)

    # 输出输入前端 - 后端专用 - 优惠券领取问题
    @api.model
    def get_preferential_settings(self, args):
        preferential_ids = self.sudo().search([('state', 'not in', ('cancel', 'invalid_over')),
                                               ('cpo_display', '=', True),
                                               ('cpo_full', '=', False),
                                               ('cpo_amount_bool', '=', True)]).ids
        coupon_id = args.get('coupon_id')  # 优惠的id号
        user_id = args.get('user_id')  # 客户id号
        if coupon_id and user_id:
            customer = self.env['preferential.cpo_customer_contact']
            x_value = customer.sudo().get_coupon_collection({'coupon_id': int(coupon_id), 'user_id': int(user_id)})
            if x_value.get('warning'):
                return {'warning': x_value.get('warning'), 'verification': False}
            return {'value': x_value.get('value'), 'verification': True}
        return {
            'preferential_ids': preferential_ids,  # 优惠券id号
        }

    # 判断实效 优惠券是不是领取完了 同时 检查时间 自动更改状态
    @api.model
    def checking_function(self):
        self._cr.execute("""SELECT id,cpo_voucher_number,state,cpo_start_time,cpo_end_time FROM 
                            preferential_cpo_time_and_money WHERE state NOT IN ('draft','cancel','invalid_over')""")
        dicts = self._cr.dictfetchall()
        utc_tm = datetime.utcfromtimestamp(time())
        for x_dict in dicts:
            preferential_db = self.browse(x_dict['id'])
            if x_dict['state'] == 'force_no_started':
                if x_dict['cpo_start_time'] <= str(utc_tm)[0:10] <= x_dict['cpo_end_time']:
                    preferential_db.write({'state': 'started_and_started', 'cpo_display': True})
                elif x_dict['cpo_end_time'] < str(utc_tm)[0:10]:
                    preferential_db.write({'state': 'invalid_over', 'cpo_invalid_over_bool': True, 'cpo_display': False})
            elif x_dict['state'] == 'started_and_started':
                if x_dict['cpo_end_time'] < str(utc_tm)[0:10]:
                    preferential_db.write({'state': 'invalid_over', 'cpo_invalid_over_bool': True, 'cpo_display': False})
            if x_dict['cpo_voucher_number'] > 0:
                self._cr.execute("""SELECT id FROM preferential_cpo_customer_contact WHERE 
                                 time_money_id = %s and cpo_coupon_bool = %s and cpo_voucher_bool = %s""",
                                 (x_dict['id'], True, True))
                dicts_db = self._cr.dictfetchall()
                if len(dicts_db) == x_dict['cpo_voucher_number']:
                    preferential_db.write({'cpo_full': True})
        return True

    def GetWebRegistered(self):
        return self.get_coupon_new_user_show()

    def get_coupon_new_user_show(self):
        self._cr.execute("""
            SELECT ID FROM PREFERENTIAL_CPO_TIME_AND_MONEY WHERE new_user_bool=True and cpo_amount_bool=True and cpo_full=False and 
            cpo_display=True and cpo_invalid_over_bool=False
        """)
        data = self._cr.dictfetchall()
        data = [x.get('id') for x in data]
        if data:
            data = self.browse(max(data))
        return data

    # # 查看页面展示效果
    # def view_effects(self):
    #     view_id = self.env.ref('cpo_preferential.view_interface_display_effects').id
    #     return {
    #         'name': _('View interface display effects'),
    #         'type': 'ir.actions.act_window',
    #         'view_type': 'form',
    #         'view_mode': 'form',
    #         'res_model': 'preferential.cpo_time_and_money',
    #         'res_id': self.quotation_line.quotation_id.id,
    #         'views': [[view_id, 'form']],
    #         'target': 'new',
    #         # 'domain': [('id', 'in', self.ids)],
    #     }
