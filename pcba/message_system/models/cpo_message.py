# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from urlparse import urljoin


class MessageCenter(models.Model):
    """
    消息中心，默认为客户端发过来的消息，销售人员要发送通知时，应该选择类型（通知类型）
    """
    _name = 'message.center'
    _description = 'Message Center'
    _order = 'id desc'

    SELECT_MESSAGE = [
        ('read', 'Have read'),
        ('unread', 'Unread'),
    ]

    MESSAGE_TYPE = [
        ('c_msg', 'Consulting Message'),  # 咨询
        ('n_msg', 'Notification Message'),  # 通知
        ('o_msg', 'Offer Message')  # 优惠
    ]

    name = fields.Char(string="Message Title", size=64, default='/')
    msg_type = fields.Selection(MESSAGE_TYPE, string="Type", default='n_msg', required=True)
    client_ids = fields.Many2many('personal.center', string='Client', ondelete='cascade')
    seller_id = fields.Many2one('cpo_sale_allocations.allocations', string="Seller", ondelete='cascade')
    message = fields.Html(string="Message")
    all_client_bool = fields.Boolean('All Client')
    place_order_bool = fields.Boolean('Place An Order Client')  # 下过单的客户
    order_type = fields.Selection([('all', 'All Type'),
                                   ('pcb', 'PCB Type'),
                                   ('pcba', 'PCBA Type'),
                                   ('stencil', 'Stencil Type')], string='Order Type', default='all')
    no_place_order_bool = fields.Boolean('No Place An Order Client')  # 没有下过单的客户
    login_start = fields.Datetime('Registration Start Time')
    login_end = fields.Datetime('Registration End Time')
    msg_line_ids = fields.One2many('message.center.line', 'msg_id', 'Message Center Line', auto_join=True)
    state = fields.Selection([('draft', 'Draft'),
                              ('send_notify', 'Send Notification'),
                              ('withdraw', 'Withdraw'),
                              ('cancel', 'Cancel')], string='Status', default='draft', index=True)
    send_time = fields.Datetime('Send Time')
    coupon_id = fields.Many2one('preferential.cpo_time_and_money', 'Coupon', ondelete='cascade', index=True)

    # 用于初始调用
    def organize_fields(self):
        return {
            'all_client_bool': False,
            'place_order_bool': False,
            'no_place_order_bool': False,
            'client_ids': False,
            'order_type': 'all',
            'login_start': self.login_start,
            'login_end': self.login_end,
        }

    # 根据条件进行客户筛选
    @api.onchange(
        'all_client_bool', 'order_type', 'no_place_order_bool', 'place_order_bool',
        'login_start', 'login_end',
    )
    def _onchange_select_client(self):
        client_ids = self.client_ids.search([('activation_type', '=', 'Activation')])
        value = self.organize_fields()
        if self.all_client_bool:
            value.update({'client_ids': client_ids.ids, 'all_client_bool': True})
        if self.place_order_bool:
            if not self.order_type:
                raise ValidationError(_('Filter order type cannot be empty'))
            client_ids = client_ids.filtered(lambda x: x.partner_id.sale_order_ids)
            x_tuple = None
            if self.order_type == 'pcb':
                x_tuple = ('product_type', 'not in', ('PCBA', 'Stencil'))
            elif self.order_type == 'pcba':
                x_tuple = ('product_type', '=', 'PCBA')
            elif self.order_type == 'stencil':
                x_tuple = ('product_type', '=', 'Stencil')
            if x_tuple:
                for x_id in client_ids:
                    if not x_id.partner_id.sale_order_ids.search([x_tuple, ('partner_id', '=', x_id.partner_id.id)]):
                        client_ids = client_ids.filtered(lambda x: x.id != x_id.id)
            value.update({'place_order_bool': True, 'order_type': self.order_type, 'client_ids': client_ids.ids})
        if self.no_place_order_bool:
            client_ids = client_ids.filtered(lambda x: not x.partner_id.sale_order_ids)
            value.update({'no_place_order_bool': True, 'client_ids': client_ids.ids})
        if self.login_start and self.login_end:
            client_ids = client_ids.filtered(lambda x: self.login_start <= x.create_date <= self.login_end)
            value.update({'login_start': self.login_start, 'login_end': self.login_end, 'client_ids': client_ids.ids})
        return self.update(value)

    # 根据选择的类型进行 主题的映射 主题名可以更改
    @api.onchange('msg_type')
    def _onchange_msg_type(self):
        if self.msg_type == 'c_msg':
            self.name = 'Consulting Message'
        elif self.msg_type == 'n_msg':
            self.name = 'Notification Message'
        elif self.msg_type == 'o_msg':
            self.name = 'Offer Message'

    # 返回一个销售员ID号
    @api.onchange('seller_id')
    def _onchange_seller_id(self):
        if not self.seller_id:
            seller_id = self.env['cpo_sale_allocations.allocations'].search([('name', '=', self._uid)]).id
            return self.update({'seller_id': seller_id})

    # 发送通知按钮
    def SendNotify(self):
        name, message, msg_type, msg_id = self.name, self.message, self.msg_type, self.id
        for x in self.client_ids:
            line_id = self.msg_line_ids.create({
                'msg_id': msg_id,
                'client_id': x.id,
                'state': 'unread',
                'name': name,
                'msg_type': msg_type,
                'message': message
            })
            self.env['chat.message'].create({'line_id': line_id.id, 'seller_msg': message})
        self.write({'send_time': fields.Datetime.now(), 'state': 'send_notify'})
        return True

    # 撤回通知按钮
    def WithdrawNotify(self):
        self.msg_line_ids.unlink()
        self.write({'send_time': False, 'state': 'withdraw'})
        return True

    # 取消通知按钮
    def CancelNotify(self):
        self.write({'state': 'cancel'})
        self.msg_line_ids.write({'state': 'cancel'})
        return True

    # 返回客户个人中心对象
    def get_client_id(self, user_id):
        return self.env['personal.center'].search([('user_id', '=', user_id)])

    # 展示 查看 回复
    def GetWebMessage(self, user_id, msg_id=False, reply=False):
        if msg_id:
            return self.get_message_line(msg_id, reply)
        elif reply:
            return self.get_client_consultation(user_id, reply)
        return self.get_web_show(user_id)

    # 显示关于这个客户所有的消息
    def get_web_show(self, user_id):
        client_id = self.get_client_id(user_id)
        line = self.env['message.center.line'].search([('client_id', '=', client_id.id), ('state', '!=', 'cancel')])
        number = line.filtered(lambda x: x.state in ['unread', 's_reply']).ids
        return {'msg_obj': line, 'number': len(number)}

    def get_css_div(self, reply):
        div = """
        <div class="ly-message-content-left">
            %s
        </div>
        """ % reply
        return div

    # 点击了消息 进行状态改变
    def get_message_line(self, line_id, reply):
        line = self.env['message.center.line'].browse(int(line_id))
        if line.state in ['unread', 's_reply']:
            line.write({'state': 'read'})
        if reply:
            div = self.get_css_div(reply)
            line.write({
                'state': 'c_consult',
                'message': line.message + '</br>' + div,
            })
            self.env['chat.message'].create({'line_id': line.id, 'client_msg': reply})
        return line

    # 客户进行咨询
    def get_client_consultation(self, user_id, reply):
        div = self.get_css_div(reply)
        client_id = self.get_client_id(user_id)
        line_id = self.env['message.center.line'].create({
            'msg_type': 'c_msg',
            'reply_bool': True,
            'state': 'c_consult',
            'client_id': client_id.id,
            'message': div,
        })
        self.env['chat.message'].create({'line_id': line_id.id, 'client_msg': reply})
        return line_id


class MessageCenterLine(models.Model):
    _name = 'message.center.line'
    _description = 'Message Center Line'
    _order = 'id desc, client_id'

    MESSAGE_TYPE = [
        ('c_msg', 'Consulting Message'),  # 咨询
        ('n_msg', 'Notification Message'),  # 通知
        ('o_msg', 'Offer Message')  # 优惠
    ]

    name = fields.Char('Title')
    msg_id = fields.Many2one('message.center', 'Message Center', ondelete='cascade', index=True)
    msg_type = fields.Selection(MESSAGE_TYPE, string="Type", readonly=True)
    message = fields.Html(string='Message', readonly=True)
    client_id = fields.Many2one('personal.center', string='Client', ondelete='cascade', index=True)
    seller_id = fields.Many2one('cpo_sale_allocations.allocations', string="Seller", ondelete='cascade')
    country = fields.Char(related='client_id.country', string='Country', readonly=True)
    city = fields.Char(related='client_id.city', string='City', readonly=True)
    phone = fields.Char(related='client_id.phone', string='Phone', readonly=True)
    email = fields.Char(related='client_id.email', string='Email', readonly=True)
    reply_bool = fields.Boolean('Client Reply', default=False)
    state = fields.Selection([('read', 'Read'),
                              ('unread', 'Unread'),
                              ('c_consult', 'Client Consultation'),
                              ('s_reply', 'Seller Reply'),
                              ('cancel', 'Cancel')], string='Status', index=True)
    chat_ids = fields.One2many('chat.message', 'line_id', 'Chat Message', auto_join=True)
    msg_reply = fields.Html('Seller Message')

    def _get_name(self, msg_type):
        if msg_type == 'c_msg':
            return 'Consulting Message'
        elif msg_type == 'n_msg':
            return 'Notification Message'
        elif msg_type == 'o_msg':
            return 'Offer Message'

    @api.model
    def create(self, vals):
        if not vals.get('name') or vals.get('name') is False:
            vals.update({'name': self._get_name(vals.get('msg_type'))})
        return super(MessageCenterLine, self).create(vals)

    def GetReply(self):
        if not self.seller_id:
            seller_id = self.env['cpo_sale_allocations.allocations'].search([('name', '=', self._uid)]).id
            self.update({'seller_id': seller_id})
        view_id = self.env.ref('message_system.chat_form').id
        value = {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'message.center.line',
            'res_id': self.id,
            "flags": {'mode': 'edit'},
            "target": 'new',
            'views': [[view_id, 'form']],
        }
        return value

    def determine_reply(self):
        div = """
        <div class="ly-message-content-right">
            %s
        </div>
        """ % self.msg_reply
        self.env['chat.message'].create({'line_id': self.id, 'seller_msg': self.msg_reply})
        self.write({
            'state': 's_reply',
            'message': self.message + '</br>' + div,
            'msg_reply': None,
        })
        return True

    # 新用户注册时 发送一个操作通知
    def get_new_client_message(self, client):
        url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        url = urljoin(url, "/page/help")
        div = """
        <div class="ly-message-content-right">
            <p>Dear %s:</p>
            <p>Thank you for your registration and trust in us!</p>
            <p>The link below is to make you better use our website</p>
            </br>
            <center>
                <a href="%s" style="background-color: #1abc9c; padding: 2.5px 30px; text-decoration: none; color: #fff; border-radius: 5px; font-size: 16px;" class="o_default_snippet_text">HELP</a>
                <br/>
            </center>
        </div>
        """ % (client.name, url)
        value = {
            'seller_id': client.seller_id.id,
            'client_id': client.id,
            'msg_type': 'n_msg',
            'state': 'unread',
            'message': div
        }
        line_id = self.create(value)
        self.env['chat.message'].create({'line_id': line_id.id, 'seller_msg': div})
        return True


class ChatMessage(models.Model):
    _name = 'chat.message'
    _description = 'Chat Message'
    _order = 'id desc'

    msg_id = fields.Many2one(related='line_id.msg_id', string='Message Center', index=True, ondelete='cascade')
    line_id = fields.Many2one('message.center.line', 'Message Center Line', index=True, ondelete='cascade')
    client_msg = fields.Html('Client Message')
    seller_msg = fields.Html('Seller Message')

