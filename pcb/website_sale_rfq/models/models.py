# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class SaleOrderRFQ(models.Model):
    _inherit = 'sale.order'

    applied_bool = fields.Boolean('Already Submitted', default=False)  # 作用表示 是不是申请过了
    ask_ids = fields.One2many('ask.guest', 'order_id', 'Ask Guest', auto_join=True)

    # 跳转试图 从销售单 跳转 退款界面 - 这里是 申请退款的状态
    def GetProcessRefund(self):
        refund = self.env['sales.refund'].search([('order_id', '=', self.id)])
        action = self.env.ref('website_sale_rfq.client_refund_window').read()[0]
        action.update({
            'display_name': _("%s Customer Requests Refund Line") % self.name,
            'domain': [('id', 'in', refund.ids), ('state', 'in', ('c_apply', 's_process', 'c_fail', 'c_success'))],
            'target': 'current',
        })
        return action

    # 销售员直接发起退款
    def GetInitiateRefund(self):
        return self.env['sales.refund'].GetInitiateRefundView(self.id)

    # 销售员 发起问客
    def GetInitiateAskGuest(self):
        ask_ids = self.mapped('ask_ids').ids
        if not ask_ids:
            return self.env['ask.guest'].GetInitiateAskGuestView(self.id)
        action = self.env.ref('website_sale_rfq.ask_guest_window').read()[0]
        action.update({
            'display_name': _("%s Ask Guest Line") % self.name,
            'domain': [('id', 'in', ask_ids)],
            'target': 'current',
            'context': {
                'default_order_id': self.id,
                'default_seller_id': self._uid,
            },
        })
        return action


class SalesRefund(models.Model):
    _name = 'sales.refund'
    _order = 'id desc'
    _description = 'Sales Refund'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    STATE_TYPE = [
        ('draft', 'Draft'),  # 草稿
        ('c_apply', 'Client Refund Application'),  # 客户申请退款
        ('s_process', 'Processing'),  # 正在处理
        ('c_fail', 'Do Not Agree To Refund'),  # 不同意退款
        ('c_success', 'Agree To A Refund'),  # 同意退款
        ('s_refund', 'Merchant Direct Refund'),  # 商家直接退款
        ('c_cancel', 'Customer Cancelled Refund'),  # 客户取消退款
    ]

    name = fields.Char('Refund Code', index=True, readonly=True, size=64, compute='_get_parameter_value', store=True)
    order_id = fields.Many2one('sale.order', 'Sale Order', index=True, ondelete='cascade', track_visibility='onchange')
    seller_id = fields.Many2one('res.users', 'Seller', ondelete='cascade', track_visibility='onchange')
    partner_id = fields.Many2one('res.partner', string='Client', related='order_id.partner_id', readonly=True, index=True)
    country_id = fields.Many2one('res.country', string='Country', related='order_id.partner_id.country_id', readonly=True)
    city = fields.Char(string='City', related='order_id.partner_id.city', readonly=True)
    phone = fields.Char(string='Phone', related='order_id.partner_id.phone', readonly=True)
    email = fields.Char(string='E-mail', related='order_id.partner_id.email', readonly=True)
    applied_bool = fields.Boolean(string='Already Submitted', related='order_id.applied_bool', readonly=True)
    currency_id = fields.Many2one("res.currency", related='order_id.currency_id', string="Currency", readonly=True)
    order_amount = fields.Monetary(string='Order Original Amount', related='order_id.amount_total', readonly=True)
    order_state = fields.Selection(string='Order Status', related='order_id.state', readonly=True)
    confirmation_date = fields.Datetime(string='Order Confirmation Date', related='order_id.confirmation_date', readonly=True)
    product_name = fields.Char(string='Product Name', related='order_id.product_name', readonly=True)
    refund_amount = fields.Float(string='Refund Amount', digits=(16, 2), compute='_get_parameter_value', track_visibility='onchange', store=True)
    state = fields.Selection(STATE_TYPE, string='Status', readonly=True, default='draft', track_visibility='onchange')
    client_refund = fields.Text('Customer Request Refund')  # 客户申请退款原因
    sale_refund = fields.Text('Reason For Salesperson Refund')  # 销售员退款原因
    serial_number = fields.Char('Serial Number', readonly=True)

    @api.depends('order_id')
    def _get_parameter_value(self):
        x_str = 'SR000000'
        for x_id in self:
            x_id.refund_amount = x_id.order_amount
            if type(x_id.id) is not int:
                x_id.name = False
                continue
            x_id.name = x_str[:-len(str(x_id.id))] + str(x_id.id)
        return True

    @api.onchange('refund_amount')
    def _onchange_refund_amount(self):
        if self.refund_amount > self.order_amount:
            raise ValidationError(_('The refund amount cannot be greater than the order amount'))

    # 处理退款 打开视图 - 给调用 - 这是有客户主导的 已经存在的数据
    def GetProcessRefundView(self):
        self.write({'seller_id': self._uid, 'state': 's_process'})
        view_id = self.env.ref('website_sale_rfq.client_refund_form').id
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sales.refund',
            'res_id': self.id,
            "flags": {'mode': 'edit'},
            "target": 'current',
            'views': [[view_id, 'form']],
        }

    # 直接发起退款 打开视图 - 给调用 - 状态默认草稿 - 这是销售员主导的 还没有创建数据
    def GetInitiateRefundView(self, order_id):
        view_id = self.env.ref('website_sale_rfq.sale_refund_form').id
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sales.refund',
            'res_id': self.id,
            "flags": {'mode': 'edit'},
            "target": 'current',
            'views': [[view_id, 'form']],
            'context': {
                'default_seller_id': self._uid,
                'default_order_id': order_id,
            },
        }

    def get_paypal_refund(self, order, refund_amount):
        return self.env['payment.acquirer'].paypal_api_refund(order, refund_amount)

    # 直接退款的按钮
    def DirectRefund(self):
        if not self.sale_refund:
            raise ValidationError(_("The system detected that the 'Refund Instructions For Salesperson' was not filled in, please explain in detail the reason for the direct refund."))
        try:
            value = self.get_paypal_refund(self.order_id, self.refund_amount)
            self.order_id.update({'state': 'refunded'})
            return self.write({'state': 's_refund', 'serial_number': value})
        except Exception as e:
            raise ValidationError(e)

    # 同意退款 - 按钮
    def AgreeRefund(self):
        if not self.sale_refund:
            raise ValidationError(_("The system detected that the 'Refund Instructions For Salesperson' field did not fill in the reason for consent."))
        try:
            value = self.get_paypal_refund(self.order_id, self.refund_amount)
            self.order_id.update({'state': 'refunded'})
            return self.write({'state': 'c_success', 'serial_number': value})
        except Exception as e:
            raise ValidationError(e)

    # 不同意退款
    def DisagreeRefund(self):
        if not self.sale_refund:
            raise ValidationError(_("The system detected that the 'Refund Instructions For Salesperson' field was not filled in."))
        self.order_id.update({'state': 'wait_make'})
        return self.update({'state': 'c_fail'})

    # 前端客户 展示以及申请接口  在单纯展示 需要传入客户的id号, 申请退款需要明确那个订单id
    def GetShowOrApply(self, client_id, order_id=False, reason=False, value=False):
        return self.ClientRefundApplyOrShow(client_id, order_id=order_id, reason=reason, value=value)

    def ClientRefundApplyOrShow(self, client_id, order_id=False, reason=False, value=False):
        dicts = {}
        refund = self.search([('partner_id', '=', client_id.id)])
        order = client_id.sale_order_ids.filtered(lambda x: x.state in ['wait_make', 'manufacturing', 'wait_delivery', 'wait_receipt', 'complete', 'request_refund'])
        if order_id and reason:
            self.create({'order_id': order_id, 'client_refund': reason, 'state': 'c_apply'})
            self.env['sale.order'].browse(int(order_id)).update({'applied_bool': True, 'state': 'request_refund'})
            dicts.update({'refund_id': True})
        if value:
            dicts.update({'refund_obj': refund})
        else:
            dicts.update({'order_obj': order})
        dicts.update({
            'qty': {
                'p_qty': len(order),
                'rf_qty': len(refund),
            }
        })
        return dicts

    # 检查订单 有没有 申请过被拒绝退款的情况
    def CheckApplyRecord(self, order_id):
        x_obj = self.search([('order_id', '=', int(order_id)),
                             ('state', '=', 'c_fail')])
        if x_obj:
            return {'reason': x_obj.sale_refund}
        return False

    # 前端调用 客户主动取消退款接口
    def GetCancelRefund(self, refund_id):
        return self.ClientCancelRefund(refund_id)

    # 客户主动取消退款
    def ClientCancelRefund(self, refund_id):
        refund = self.browse(int(refund_id))
        refund.write({'state': 'c_cancel'})
        refund.order_id.write({'applied_bool': False, 'state': 'wait_make'})
        return True


class AskGuest(models.Model):
    _name = 'ask.guest'
    _order = 'order_id desc, name, id desc'
    _description = 'Ask Guest'

    STATE_TYPE = [
        ('draft', 'Draft'),
        ('wait_reply', 'Waiting For Customer Response'),  # 等待客户回复
        ('replied', 'Customer Has Responded'),  # 客户已回复
        ('read', 'Customer Read'),  # 客户已读
        ('complete', 'Complete'),  # 完成
    ]

    name = fields.Char('Problem', readonly=True, size=64)
    name_title = fields.Char('Problem', required=True, size=64)
    seller_id = fields.Many2one('res.users', 'Seller', ondelete='cascade', track_visibility='onchange')
    line_ids = fields.One2many('ask.guest.line', 'ask_guest_id', 'Ask Guest', auto_join=True, readonly=True)
    ask_reason = fields.Html('Suggestions')
    ask_message = fields.Html('Message')
    order_id = fields.Many2one('sale.order', 'Sale Order', index=True, ondelete='cascade', track_visibility='onchange')
    partner_id = fields.Many2one('res.partner', string='Client', related='order_id.partner_id', readonly=True, index=True)
    country_id = fields.Many2one('res.country', string='Country', related='order_id.partner_id.country_id', readonly=True)
    city = fields.Char(string='City', related='order_id.partner_id.city', readonly=True)
    phone = fields.Char(string='Phone', related='order_id.partner_id.phone', readonly=True)
    email = fields.Char(string='E-mail', related='order_id.partner_id.email', readonly=True)
    order_state = fields.Selection(string='Order Status', related='order_id.state', readonly=True)
    confirmation_date = fields.Datetime(string='Order Confirmation Date', related='order_id.confirmation_date', readonly=True)
    product_name = fields.Char(string='Product Name', related='order_id.product_name', readonly=True)
    time_cost = fields.Char(string='Time Cost')
    state = fields.Selection(STATE_TYPE, string='Status', readonly=True, default='draft')

    @api.multi
    def write(self, vals):
        if not self.name and self.state == 'draft' and vals.get('state'):
            vals.update({"name": self.GetNameValue(self.order_id.id)})
        return super(AskGuest, self).write(vals)

    # 附上编号
    def GetNameValue(self, order_id):
        x_str = 'NO.'
        num = self.search_count([('order_id', '=', order_id), ('name', 'like', x_str)]) + 1
        return x_str + str(num)

    # 检查参数
    def CheckParameter(self):
        if not self.ask_reason:
            raise ValidationError(_("The system detected that 'Suggestions' was not filled in, please fill in the details in the confirmation."))
        elif not self.order_id:
            raise ValidationError(_("The system detected that there are no related orders, please select the order to ask for customers."))

    def get_css_div(self):
        div = """
            <div class="ask-message-content-right">
                %s
            </div>
            </br>
        """ % self.ask_reason
        return div

    # 打开提出建议视图 第一次时会调用
    def GetInitiateAskGuestView(self, order_id):
        view_id = self.env.ref('website_sale_rfq.ask_guest_form').id
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'ask.guest',
            'res_id': self.id,
            "flags": {'mode': 'edit'},
            "target": 'new',
            'views': [[view_id, 'form']],
            'context': {
                'default_seller_id': self._uid,
                'default_order_id': order_id,
            },
        }

    # 提出建议按钮
    def ProposeSuggest(self):
        div = self.get_css_div()
        self.CheckParameter()
        self.line_ids.create({'ask_guest_id': self.id, 'reason': self.ask_reason})
        self.write({"ask_message": div, 'state': 'wait_reply', 'ask_reason': None})
        return True

    # 打开 回复或再次建议 视图 按钮
    def QuestioningReply(self):
        view_id = self.env.ref('website_sale_rfq.ask_guest_form_append').id
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'ask.guest',
            'res_id': self.id,
            "flags": {'mode': 'edit'},
            "target": 'new',
            'views': [[view_id, 'form']],
        }

    # 确定回复按钮
    def DetermineSend(self):
        div = self.get_css_div()
        self.line_ids.create({'ask_guest_id': self.id, 'reason': self.ask_reason})
        self.write({"ask_message": self.ask_message + div, 'state': 'wait_reply', 'ask_reason': None})
        return True

    # 问客 前端展示
    def GetAskGuestShow(self, client_id, order_id=False, reply=False, ask_id=False, images=False):
        if order_id:
            return self.get_ask_guest(order_id, ask_id=ask_id)
        elif reply and ask_id:
            return self.client_reply(reply, ask_id, images=images)
        return self.get_making_order(client_id)

    # 正常情况 先返回 制作中的订单
    def get_making_order(self, client_id):
        order = client_id.sale_order_ids.filtered(lambda x: x.state == 'manufacturing')
        return order

    # 查看问客 内容
    def get_ask_guest(self, order_id, ask_id=False):
        ask_ids = self.env['sale.order'].browse(int(order_id)).ask_ids
        ask_ids = ask_ids.filtered(lambda x: x.state != 'draft')
        if ask_id:
            ask_id = self.browse(int(ask_id))
            if ask_id.state not in ['replied', 'complete']:
                ask_id.write({'state': 'read'})
        return ask_ids

    # 提交 问客的回复
    def client_reply(self, reply, ask_id, images=False):
        ask_id = self.browse(int(ask_id))
        ask_id.line_ids.create({'reply': reply, 'ask_guest_id': ask_id.id})
        div = """
        <div class="ask-message-content-left">
            %s
        </div>
        </br>
        """ % reply
        reply = ask_id.ask_message + '<br/>' + div
        ask_id.write({'ask_message': reply, 'state': 'replied'})
        return True

    def AskGuestComplete(self):
        return self.write({'state': 'complete'})


class AskGuestLine(models.Model):
    _name = 'ask.guest.line'
    _description = 'Ask Guest'
    _order = 'id desc'

    ask_guest_id = fields.Many2one('ask.guest', 'Ask Guest', ondelete='cascade')
    reason = fields.Html('Suggestions')
    reply = fields.Html('Client Reply')






