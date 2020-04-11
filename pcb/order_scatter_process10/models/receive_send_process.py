# -*- coding: utf-8 -*-

import odoorpc, logging, xmlrpclib
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

_logger = logging.getLogger(__name__)


class SendProcessServer(models.Model):
    _name = 'send.process.server'
    _description = 'Send Process Server'

    name = fields.Char('Key Value', size=64, default='Send Server', translate=True)
    send_host = fields.Char('HOST')
    send_port = fields.Char('PORT')
    send_login = fields.Char('Login Account')
    send_pwd = fields.Char('Password')
    send_db = fields.Char('Database')

    def SortOutValue(self):
        return {
            'model': 'receive.process.server',  # 检查 对方接收处理的对象
            'fun': 'odoo_connection',  # 测试连接调用的函数名
            'host': self.send_host,
            'port': self.send_port,
            'login': self.send_login,
            'db': self.send_db,
            'pwd': self.send_pwd,
            'conn': False,  # 表示最简单的连接通信有没有成功
        }

    # 这一步先通过 odoorpc获取 uid
    def ConnErp(self, value):
        erp = odoorpc.ODOO(host=value.get('host'), port=value.get('port'))
        erp.login(value.get('db'), value.get('login'), value.get('pwd'))
        value.update({'uid': erp.env._context.get('uid'), 'conn': True, 'install': False})
        erp.logout()
        return value

    # 先测试能不能通信
    @api.multi
    def CheckConnection(self):
        message, value = self.get_connection()
        if value:
            raise UserError(message)
        else:
            raise ValidationError(message)

    def get_connection(self):
        value = self.SortOutValue()
        try:
            value = self.ConnErp(value)
            sock = xmlrpclib.ServerProxy('http://%s:%s/xmlrpc/object' % (value.get('host'), value.get('port')))
            sock = sock.execute(value.get('db'), value.get('uid'), value.get('pwd'), value.get('model'), value.get('fun'), [])
            value.update({'install': sock})
            return _("Connection Test Succeeded! Everything seems properly set up!"), True
        except Exception as e:
            e = e.message if e.message else str(e)
            _logger.error(e)
            if value.get('conn') is False:
                return _('Test connection error, please determine whether the target host server is running normally; or the port number and target address are correct. The error is as follows: \n%s' % e), False
            elif value.get('install') is False:
                return _('The communication connection is successful, but the other party may not have the required module installed. The error is as follows: \n%s' % e), False
            else:
                return (e), False



