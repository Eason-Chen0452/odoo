# -*- coding: utf-8 -*-
import logging, werkzeug, urllib, re, socket, random
from odoo import _, api, exceptions, fields, models, tools
from bs4 import BeautifulSoup as BS
from urlparse import urljoin
from email.message import Message
from datetime import timedelta
from base64 import b64encode as e64
from odoo.tools.safe_eval import safe_eval
from odoo.tools import pycompat


_logger = logging.getLogger(__name__)


def random_token():
    # the token has an entropy of about 120 bits (6 bits/char * 20 chars)
    chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    return ''.join(random.SystemRandom().choice(chars) for _ in pycompat.range(5))


# 邮件中的模板
class CustomMessageText(models.Model):
    _name = 'custom.message_text'
    _description = 'Custom Message Text'

    name = fields.Char('Custom Message Text Name', size=64, translate=True)
    message_text = fields.Html('Custom Message Text')


# 营销邮件主体
class MassSalesMail(models.Model):
    _name = 'mass_sales.mail'
    _description = 'Marketing Mail'
    _order = 'id desc'

    name = fields.Char('Email Subject', size=64, translate=True, required=True)
    filter_bool = fields.Boolean('Whether To Filter', default=False)
    select_all_bool = fields.Boolean('Select All Customer', default=False)
    order_bool = fields.Boolean('Billing Under Icloudfactory', default=False)
    no_order_bool = fields.Boolean('No Billing Under Icloudfactory', default=False)
    login_start = fields.Date('Filter Customers By Registering Time Period')
    login_end = fields.Date('Filter Customers By Registering Time Period')
    order_start = fields.Date('Filter Customers By Ordering Time Period')
    order_end = fields.Date('Filter Customers By Ordering Time Period')
    country_ids = fields.Many2many('res.country', string='Country')
    personal_ids = fields.Many2many('personal.center', string='Customer', required=True)
    mail_content = fields.Html('Mail Content')
    select_template = fields.Many2one('custom.message_text', 'Select Mail Template', ondelete='cascade')
    state = fields.Selection([('Draft', 'Draft'), ('Sending', 'Sending'), ('Has Been Sent', 'Has Been Sent')], string='Status', default='Draft')
    people_mail = fields.Integer('The Total Number Of People Who Send Marketing Emails', default=0)  # 发送营销邮件的总人数
    receive_mail = fields.Integer('The Total Number Of People Who Received Marketing Emails', default=0)  # 收到营销邮件的总人数
    open_mail = fields.Integer('The Total Number Of Open Marketing Messages', default=0)  # 打开营销邮件的总人数
    receive_scale = fields.Float('Proportion Of Receiving Marketing Emails', digits=(16, 2), compute='_count_receive_mail', store=True)  # 收到营销邮件的比例
    open_scale = fields.Float('Open Marketing Emails', digits=(16, 2), compute='_count_open_mail', store=True)  # 打开营销邮件的比例
    send_time = fields.Datetime('Mail Delivery Time')  # 邮件发送时间
    mail_line = fields.One2many('mass_sales.mail.line', 'mail_id', 'Customer Personal Mail')
    process_bool = fields.Boolean('Process', default=False)
    email_type = fields.Selection([('Registered', 'Registered'),  # 注册
                                   ('Marketing', 'Marketing')], default='Marketing', string='Email Type', index=True)
    test_email = fields.Boolean('View Performance', default=False)
    channel_id = fields.Many2one('mail.channel', 'Channel')

    @api.depends('receive_mail')
    def _count_receive_mail(self):
        for x_id in self:
            if x_id.receive_mail > 0:
                x_id.receive_scale = float(x_id.receive_mail) / float(x_id.people_mail) * 100.0

    @api.depends('open_mail')
    def _count_open_mail(self):
        for x_id in self:
            if x_id.open_mail > 0:
                x_id.open_scale = float(x_id.open_mail) / float(x_id.people_mail) * 100.0

    @api.onchange('select_all_bool')
    def _onchange_select_all_bool(self):
        # 都会有邮箱
        if self.select_all_bool:
            cen_ids = self.personal_ids.search([('activation_type', '=', 'Activation')]).ids
            return self.update({'personal_ids': [(6, 0, cen_ids)], 'select_all_bool': True, 'filter_bool': False})
        elif not self.select_all_bool:
            return self.update({'personal_ids': False, 'select_all_bool': False})

    @api.onchange('filter_bool')
    def _onchange_filter_bool(self):
        if self.filter_bool:
            return self.update({'select_all_bool': False, 'filter_bool': True})
        elif not self.filter_bool:
            return self.update({
                'filter_bool': False,
                'order_bool': False,
                'no_order_bool': False,
                'login_start': False,
                'login_end': False,
                'order_start': False,
                'order_end': False,
                'country_ids': []
            })

    @api.onchange('login_start', 'login_end')
    def _onchange_login_time(self):
        if self.login_start and self.login_end:
            if self.login_start > self.login_end:
                # path = os.path.realpath(__file__).replace('\\', '/')
                # path = path[:path.index('/models')] + '/static/src/js/pendant.js'
                # js_fun = execjs.compile(open(path).read().decode("utf-8")).call('test_test')
                return {
                    'warning': {
                        'title': _('Setting Filter Customers By Registering Time Period Error!!'),
                        'message': _('Please set the start and end time correctly!')
                    }
                }
            self._onchange_filter_condition()

    @api.onchange('order_start', 'order_end')
    def _onchange_order_time(self):
        if self.order_start and self.order_end:
            if self.order_start > self.order_end:
                return {
                    'warning': {
                        'title': _('Setting Filter Customers By Ordering Time Period Error!!'),
                        'message': _('Please set the start and end time correctly!')
                    }
                }
            self._onchange_filter_condition()

    @api.onchange('no_order_bool')
    def _onchange_no_order_bool(self):
        if self.no_order_bool:
            self.update({'no_order_bool': True, 'order_bool': False})
            self._onchange_filter_condition()
        else:
            if self.personal_ids:
                self._onchange_filter_condition()

    @api.onchange('order_bool')
    def _onchange_order_bool(self):
        if self.order_bool:
            self.update({'no_order_bool': False, 'order_bool': True})
            self._onchange_filter_condition()
        else:
            if self.personal_ids:
                self._onchange_filter_condition()

    @api.onchange('country_ids')
    def _onchange_filter_condition(self):
        cen_ids = self.personal_ids.search([])
        # 这个是一定付过款的
        if self.order_bool:
            cen_ids = cen_ids.filtered(lambda x: x.paid > 0)
        if self.no_order_bool:
            cen_ids = cen_ids.filtered(lambda x: x.paid == 0)
        if self.login_start and self.login_end:
            start, end = self.login_start, self.login_end
            cen_ids = cen_ids.filtered(lambda x: start <= x.create_date <= end)
        # 这一定有下单 但是不一定付过款的
        if self.order_start and self.order_end:
            start, end = self.order_start, self.order_end
            list_ids = []
            for x_id in cen_ids:
                partner_id = x_id.partner_id.id
                sale = self.env['sale.order'].search([('date_order', '>=', start), ('date_order', '<=', end), ('partner_id', '=', partner_id)])
                if sale:
                    list_ids.append(x_id.id)
            cen_ids = self.env['personal.center'].browse(list_ids)
        if self.country_ids:
            country_ids = self.country_ids.ids
            cen_ids = cen_ids.filtered(lambda x: x.country_id.id in country_ids)
        if (self.order_bool or self.no_order_bool or self.order_start or self.order_end or self.login_start or self.login_end) is False and not self.country_ids:
            return self.update({'personal_ids': []})
        return self.update({'personal_ids': cen_ids.ids})

    @api.onchange('select_template')
    def _onchange_tone_selection(self):
        if self.select_template:
            self.mail_content = self.select_template.message_text
        else:
            self.mail_content = None

    # 点击发送 将状态改为 正在发送中 由定时器去处理这事情
    def mass_send_email(self):
        for x_id in self.personal_ids:
            self.mail_line.create({'center_id': x_id.id, 'mail_id': self.id})
        self.update({'state': 'Sending'})

    # 定时动作完成 发送促销邮件
    @api.model
    def MassSalesSendEmail(self):
        data = self.search([('state', '=', 'Sending')], limit=1)
        if data:
            template = self.env.ref('crm_msa.sales_promotion_mail_template')
            for x_id in data.personal_ids:
                template.update({'partner_to': x_id.partner_id.id})
                template.with_context(lang=data._context.get('lang')).send_mail(data.id, force_send=True, raise_exception=True)
                _logger.info('Mail sent successfully to %s' % x_id.email)
            data.update({'state': 'Has Been Sent', 'send_time': fields.datetime.now()})
        return True

    # 定时动作 处理发去邮件后的状态
    @api.model
    def CustomerEmailState(self):
        data = self.search([('state', '=', 'Has Been Sent'), ('process_bool', '=', False)])
        if data:
            for x_id in data:
                mail_line = x_id.mail_line.filtered(lambda x: x.state == 'Ready')
                mail_line.write({'receive_bool': True, 'state': 'Sent'})
            data.write({'process_bool': True})
        return True

    # 测试按钮 查看邮件效果
    @api.multi
    def CheckEmailView(self):
        template = self.env.ref('crm_msa.sales_promotion_mail_template')
        partner_ids = ''
        for x in self.channel_id.channel_partner_ids.ids:
            partner_ids += str(x) + ','
        template.update({'partner_to': partner_ids, 'auto_delete': True})
        template.with_context(lang=self._context.get('lang')).send_mail(self.id, force_send=True, raise_exception=True)
        _logger.info('Send a test email to view, time to %s' % fields.Datetime.now())
        template.update({'auto_delete': False, 'partner_to': False})

    # 重定向url
    def get_redirect_url(self, txt):
        home = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        mail = self.mail_line.search([('mail_id', '=', self.id), ('mark_bool', '=', False)], limit=1)
        mail.write({'mark_bool': True})
        txt = BS(txt, 'html.parser')
        text = txt.find_all('a')
        for a_label in text:
            if a_label.attrs.get('href') == '#':
                x_str = home + '&' + str(mail.id)
            else:
                x_str = a_label.attrs.get('href') + '&' + str(mail.id)
            x_str = e64(x_str)
            x_str = {'value': x_str[:17] + random_token() + x_str[17:]}
            a_label.attrs.update({'href': urljoin(home, "/crm/ordinary?%s" % werkzeug.url_encode(x_str))})
        return unicode(txt)

    @api.model
    def create(self, vals):
        return super(MassSalesMail, self).create(vals)

    @api.multi
    def write(self, vals):
        if vals.get('state') == 'Has Been Sent':
            vals.update({'people_mail': len(self.personal_ids), 'receive_mail': len(self.personal_ids)})
        return super(MassSalesMail, self).write(vals)

    @api.multi
    def unlink(self):
        for x_id in self:
            self.env['mail.mail'].search([('model', '=', 'mass_sales.mail'), ('res_id', '=', x_id.id)]).unlink()
        return super(MassSalesMail, self).unlink()


# 营销邮件中的明细
class MailCustomerEmail(models.Model):
    _name = 'mass_sales.mail.line'
    _description = 'Customer Personal Mail'

    center_id = fields.Many2one('personal.center', string='Customer', index=True, ondelete='cascade')
    mail_id = fields.Many2one('mass_sales.mail', 'Email Subject', index=True, ondelete='cascade')
    country = fields.Char(related='center_id.country', string='Country')
    mail_content = fields.Html(related='mail_id.mail_content', string='Mail Content')
    send_time = fields.Datetime(related='mail_id.send_time', string='Mail Delivery Time')
    receive_bool = fields.Boolean('Did you receive', default=False)
    read_bool = fields.Boolean('Whether To Click On The Link In The Email', default=False)
    state = fields.Selection([('Ready', 'Ready'),
                              ('Sent', 'Sent'),
                              ('Bounce', 'Bounce'),
                              ('Exception', 'Exception')], string='Email Status', default='Ready')
    reason = fields.Text('Return Reason')
    click_ids = fields.One2many('mail.click_link', 'line_id', string='Click Link')
    mark_bool = fields.Boolean('Mark', default=False)


# 客户点击链接的数据 - 往后会有用
class MailClickLink(models.Model):
    _name = 'mail.click_link'
    _description = 'Mail Click Link'
    _order = 'id'

    line_id = fields.Many2one('mass_sales.mail.line', string='Customer Personal Mail', index=True, ondelete='cascade')
    center_id = fields.Many2one('personal.center', string='Customer', related='line_id.center_id')
    mail_id = fields.Many2one('mass_sales.mail', string='Email Subject', related='line_id.mail_id')
    click_time = fields.Datetime('Click Link Time')
    click_name = fields.Char('Click Name')


# 临时数据表
class ReturnProcessing(models.Model):
    _name = 'mail.return_processing'
    _description = 'Mail Return Processing'

    name = fields.Selection([('Mailbox Does Not Exist', 'Mailbox Does Not Exist')], string='Return Reason', default='Mailbox Does Not Exist')
    body = fields.Text('Return Content')
    subject = fields.Char('Return Subject')
    email_from = fields.Char('Return Email From')
    email_to = fields.Char('Return Email TO')
    message_id = fields.Char('Return Message')
    message_type = fields.Char('Return Message Type')
    date_time = fields.Datetime('Return Time')
    state = fields.Selection([('Processed', 'Processed'),
                              ('Unprocessed', 'Unprocessed')], string='Status', default='Unprocessed', index=True)

    # 定时器 处理退回来的信息
    @api.model
    def ProcessReturnEmail(self):
        data = self.search([('state', '=', 'Unprocessed')], limit=30)
        if data:
            # 发出去的邮件 时间超过三天的不进行数据对比
            old_date = str(fields.datetime.now() - timedelta(days=2))
            mail_data = self.env['mail.mail'].search([('model', '=', 'mass_sales.mail')])
            mail_data = mail_data.filtered(lambda x: old_date <= x.date <= str(fields.datetime.now()))
            for x_id in data:
                try:
                    body = BS(x_id.body, 'html.parser')
                    value = [x.extract() for x in body('pre')]
                    del value
                    x_mail = mail_data.filtered(lambda x: x.message_id == x_id.message_id)
                    partner_id = x_mail.recipient_ids.filtered(lambda x: x.email_formatted == x_id.email_to).id
                    x_model = self.env['mass_sales.mail'].browse(x_mail.res_id)
                    x_mail = x_model.mail_line.filtered(lambda x: x.center_id.partner_id.id == partner_id)
                    x_mail.write({'state': 'Bounce', 'reason': unicode(body), 'receive_bool': False})
                    x_model.write({'receive_mail': x_model.receive_mail - 1})
                    x_id.write({'state': 'Processed'})
                except Exception as e:
                    _logger.warning(e.message)
                    continue
        return True

    # 删除 处理好的退回来的信息
    @api.model
    def DeleteProcessedEmail(self):
        data = self.search([('state', '=', 'Processed')])
        if data:
            data.unlink()
            _logger.info('%s delete %s' % (fields.datetime.now(), data))
        return True

    # 删除 Email中邮件信息
    @api.model
    def DeleteMailMessage(self):
        data = self.env['mail.message'].search([('model', '=', 'mass_sales.mail')])
        if data:
            time_1 = str(fields.datetime.now() - timedelta(days=5))
            time_2 = str(fields.datetime.now() - timedelta(days=3))
            data = data.filtered(lambda x: time_1 <= x.date < time_2)
            data.unlink()
        return True


# 增加创建临时数据逻辑
class MailThreadInherit(models.AbstractModel):
    _inherit = 'mail.thread'
    _description = 'Email Thread'

    @api.model
    def message_route(self, message, message_dict, model=None, thread_id=None, custom_values=None):
        if not isinstance(message, Message):
            raise TypeError('message must be an email.message.Message at this point')
        MailMessage = self.env['mail.message']
        Alias, dest_aliases = self.env['mail.alias'], self.env['mail.alias']
        bounce_alias = self.env['ir.config_parameter'].sudo().get_param("mail.bounce.alias")
        fallback_model = model

        # get email.message.Message variables for future processing
        local_hostname = socket.gethostname()
        message_id = message.get('Message-Id')

        # compute references to find if message is a reply to an existing thread
        references = tools.decode_message_header(message, 'References')
        in_reply_to = tools.decode_message_header(message, 'In-Reply-To').strip()
        thread_references = references or in_reply_to
        reply_match, reply_model, reply_thread_id, reply_hostname, reply_private = tools.email_references(thread_references)

        # author and recipients
        email_from = tools.decode_message_header(message, 'From')
        email_from_localpart = (tools.email_split(email_from) or [''])[0].split('@', 1)[0].lower()
        email_to = tools.decode_message_header(message, 'To')
        email_to_localpart = (tools.email_split(email_to) or [''])[0].split('@', 1)[0].lower()

        # Delivered-To is a safe bet in most modern MTAs, but we have to fallback on To + Cc values
        # for all the odd MTAs out there, as there is no standard header for the envelope's `rcpt_to` value.
        rcpt_tos = ','.join([
            tools.decode_message_header(message, 'Delivered-To'),
            tools.decode_message_header(message, 'To'),
            tools.decode_message_header(message, 'Cc'),
            tools.decode_message_header(message, 'Resent-To'),
            tools.decode_message_header(message, 'Resent-Cc')])
        rcpt_tos_localparts = [e.split('@')[0].lower() for e in tools.email_split(rcpt_tos)]

        # 0. Verify whether this is a bounced email and use it to collect bounce data and update notifications for customers
        if bounce_alias and bounce_alias in email_to_localpart:
            # Bounce regex: typical form of bounce is bounce_alias+128-crm.lead-34@domain
            # group(1) = the mail ID; group(2) = the model (if any); group(3) = the record ID
            bounce_re = re.compile("%s\+(\d+)-?([\w.]+)?-?(\d+)?" % re.escape(bounce_alias), re.UNICODE)
            bounce_match = bounce_re.search(email_to)

            if bounce_match:
                bounced_mail_id, bounced_model, bounced_thread_id = bounce_match.group(1), bounce_match.group(
                    2), bounce_match.group(3)

                email_part = next((part for part in message.walk() if part.get_content_type() == 'message/rfc822'),
                                  None)
                dsn_part = next(
                    (part for part in message.walk() if part.get_content_type() == 'message/delivery-status'), None)

                partners, partner_address = self.env['res.partner'], False
                if dsn_part and len(dsn_part.get_payload()) > 1:
                    dsn = dsn_part.get_payload()[1]
                    final_recipient_data = tools.decode_message_header(dsn, 'Final-Recipient')
                    partner_address = final_recipient_data.split(';', 1)[1].strip()
                    if partner_address:
                        partners = partners.sudo().search([('email', 'like', partner_address)])
                        for partner in partners:
                            partner.message_receive_bounce(partner_address, partner, mail_id=bounced_mail_id)

                mail_message = self.env['mail.message']
                if email_part:
                    email = email_part.get_payload()[0]
                    bounced_message_id = tools.mail_header_msgid_re.findall(
                        tools.decode_message_header(email, 'Message-Id'))
                    mail_message = MailMessage.sudo().search([('message_id', 'in', bounced_message_id)])

                if partners and mail_message:
                    notifications = self.env['mail.notification'].sudo().search([
                        ('mail_message_id', '=', mail_message.id),
                        ('res_partner_id', 'in', partners.ids)])
                    notifications.write({
                        'email_status': 'bounce'
                    })

                if bounced_model in self.env and hasattr(self.env[bounced_model],
                                                         'message_receive_bounce') and bounced_thread_id:
                    self.env[bounced_model].browse(int(bounced_thread_id)).message_receive_bounce(partner_address,
                                                                                                  partners,
                                                                                                  mail_id=bounced_mail_id)
                _logger.info(
                    'Routing mail from %s to %s with Message-Id %s: bounced mail from mail %s, model: %s, thread_id: %s: dest %s (partner %s)',
                    email_from, email_to, message_id, bounced_mail_id, bounced_model, bounced_thread_id,
                    partner_address, partners)
                return []

        # 0. First check if this is a bounce message or not.
        #    See http://datatracker.ietf.org/doc/rfc3462/?include_text=1
        #    As all MTA does not respect this RFC (googlemail is one of them),
        #    we also need to verify if the message come from "mailer-daemon"
        if message.get_content_type() == 'multipart/report' or email_from_localpart == 'mailer-daemon':
            _logger.info('Routing mail with Message-Id %s: not routing bounce email from %s to %s',
                         message_id, email_from, email_to)
            try:
                self.env['mail.return_processing'].create({
                    'body': message_dict.get('body'),
                    'subject': message._payload[1]._payload[0]._headers[7][1],
                    'email_from': message._payload[1]._payload[0]._headers[8][1],
                    'email_to': message._payload[1]._payload[0]._headers[10][1],
                    'message_id': message._payload[1]._payload[0]._headers[6][1],
                    'message_type': message_dict.get('message_type'),
                    'date_time': message_dict.get('date'),
                })
            except Exception as e:
                x_list, x_dict = message._payload[1]._payload[0]._payload.split('\r\n'), {}
                for x in x_list[::-1]:
                    value = x.split(': ')
                    if len(value) == 2:
                        if value[0] in ['From', 'Message-Id', 'Subject', 'To']:
                            x_dict.update({value[0]: value[1]})
                    x_list.remove(x)
                self.env['mail.return_processing'].create({
                    'body': message_dict.get('body'),
                    'subject': x_dict.get('Subject'),
                    'email_from': x_dict.get('From'),
                    'email_to': x_dict.get('To'),
                    'message_id': x_dict.get('Message-Id'),
                    'date_time': fields.datetime.now(),
                })
            return []

        # 1. Check if message is a reply on a thread
        msg_references = [ref for ref in tools.mail_header_msgid_re.findall(thread_references) if 'reply_to' not in ref]
        mail_messages = MailMessage.sudo().search([('message_id', 'in', msg_references)], limit=1)
        is_a_reply = bool(mail_messages)

        # 1.1 Handle forward to an alias with a different model: do not consider it as a reply
        if reply_model and reply_thread_id:
            other_alias = Alias.search([
                '&',
                ('alias_name', '!=', False),
                ('alias_name', '=', email_to_localpart)
            ])
            if other_alias and other_alias.alias_model_id.model != reply_model:
                is_a_reply = False

        if is_a_reply:
            model, thread_id = mail_messages.model, mail_messages.res_id
            if not reply_private:  # TDE note: not sure why private mode as no alias search, copying existing behavior
                dest_aliases = Alias.search([('alias_name', 'in', rcpt_tos_localparts)], limit=1)

            route = self.message_route_verify(
                message, message_dict,
                (model, thread_id, custom_values, self._uid, dest_aliases),
                update_author=True, assert_model=reply_private, create_fallback=True,
                allow_private=reply_private, drop_alias=True)
            if route:
                _logger.info(
                    'Routing mail from %s to %s with Message-Id %s: direct reply to msg: model: %s, thread_id: %s, custom_values: %s, uid: %s',
                    email_from, email_to, message_id, model, thread_id, custom_values, self._uid)
                return [route]
            elif route is False:
                return []

        # 2. Look for a matching mail.alias entry
        if rcpt_tos_localparts:
            # no route found for a matching reference (or reply), so parent is invalid
            message_dict.pop('parent_id', None)
            dest_aliases = Alias.search([('alias_name', 'in', rcpt_tos_localparts)])
            if dest_aliases:
                routes = []
                for alias in dest_aliases:
                    user_id = alias.alias_user_id.id
                    if not user_id:
                        # TDE note: this could cause crashes, because no clue that the user
                        # that send the email has the right to create or modify a new document
                        # Fallback on user_id = uid
                        # Note: recognized partners will be added as followers anyway
                        # user_id = self._message_find_user_id(message)
                        user_id = self._uid
                        _logger.info('No matching user_id for the alias %s', alias.alias_name)
                    route = (
                    alias.alias_model_id.model, alias.alias_force_thread_id, safe_eval(alias.alias_defaults), user_id,
                    alias)
                    route = self.message_route_verify(
                        message, message_dict, route,
                        update_author=True, assert_model=True, create_fallback=True)
                    if route:
                        _logger.info(
                            'Routing mail from %s to %s with Message-Id %s: direct alias match: %r',
                            email_from, email_to, message_id, route)
                        routes.append(route)
                return routes

        # 5. Fallback to the provided parameters, if they work
        if fallback_model:
            # no route found for a matching reference (or reply), so parent is invalid
            message_dict.pop('parent_id', None)
            route = self.message_route_verify(
                message, message_dict,
                (fallback_model, thread_id, custom_values, self._uid, None),
                update_author=True, assert_model=True)
            if route:
                _logger.info(
                    'Routing mail from %s to %s with Message-Id %s: fallback to model:%s, thread_id:%s, custom_values:%s, uid:%s',
                    email_from, email_to, message_id, fallback_model, thread_id, custom_values, self._uid)
                return [route]

        # ValueError if no routes found and if no bounce occured
        raise ValueError(
            'No possible route found for incoming message from %s to %s (Message-Id %s:). '
            'Create an appropriate mail.alias or force the destination model.' %
            (email_from, email_to, message_id)
        )
