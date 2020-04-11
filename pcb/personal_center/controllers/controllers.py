# -*- coding: utf-8 -*-

import logging, urllib, werkzeug, validators
from base64 import b64decode as d64
from odoo import http, _
from odoo.addons.auth_signup.models.res_users import SignupError
from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from odoo.addons.web.controllers.main import ensure_db, Home
from odoo.addons.personal_center.models.models import time_utc
from odoo.http import request

_logger = logging.getLogger(__name__)


# 登入时的情况
class ActivateLoginHome(Home):

    # 如果是账号没有激活需要进行提醒
    @http.route()
    def web_login(self, *args, **kw):
        ensure_db()
        response = super(ActivateLoginHome, self).web_login(*args, **kw)
        user_id = request.env['res.users'].sudo().search([('login', '=', kw.get('login')), ('active', '=', False)])
        # 这种情况应该就是没有账号激活
        if user_id and response.qcontext.get('error'):
            value = {
                'message': _('The account is not activated yet, please activate it in your email. If you not receive the email, please click the button below.'),
                'login': kw.get('login')
            }
            return request.render('personal_center.activation_and_resend', value)
        if response.qcontext.get('error') == _('Wrong login/password'):
            response.qcontext.update({'error': 'Email or password does not match. Please try again or <a href="/web/reset_password" style="text-decoration:underline">reset your password</a>.'})
        return response

    # 提醒激活账号 可以重新发送激活邮件
    @http.route('/web/email_resend', type='http', auth='public', website=True)
    def web_email_resend(self, **kw):
        user_id = request.env['res.users'].sudo().search([('login', '=', kw.get('login')), ('active', '=', False)])
        if user_id:
            user_id.Enrolment(('login', '=', kw.get('login')))
            return request.redirect('/web/email_prompt?login=%s' % kw.get('login'))
        return request.redirect('/web/email_prompt')

    @http.route('/web/change_mailbox', type='http', auth='public', website=True)
    def web_change_mailbox(self, **kw):
        value = {
            'message': 'Please enter your new email to replace your old email.'
        }
        if kw.get('login'):
            value.update({
                'old_login': kw.get('login'),
            })
        return request.render('personal_center.change_mailbox', value)

    @http.route('/web/client_email_reset', type='http', auth='public', website=True)
    def web_client_email_reset(self, **kw):
        user = request.env['res.users'].sudo().search([('login', '=', kw.get('old_login')), ('active', '=', False)])
        user.update({'login': kw.get('new_login'), 'email': kw.get('new_login')})
        user.Enrolment(kw.get('new_login'))
        return request.redirect('/web/email_prompt?login=%s' % kw.get('new_login'))


# 邮箱注册时的情况
class ActivateAccount(AuthSignupHome):

    def VerifyMailboxCorrectness(self, email):
        value = validators.email(email)
        if value is True:
            return True
        return {'error': _('Email is malformed'), 'invalid_token': True}

    # 注册时进行邮箱验证 只是增加两句话 修改了返回的路径
    @http.route('/web/signup', type='http', auth='public', website=True)
    def web_auth_signup(self, *args, **kw):
        if kw.get('login'):
            value = self.VerifyMailboxCorrectness(kw.get('login'))
            if type(value) is dict:
                return request.render('auth_signup.signup', value)
        qcontext = self.get_auth_signup_qcontext()
        if not qcontext.get('token') and not qcontext.get('signup_enabled'):
            raise werkzeug.exceptions.NotFound()
        if 'error' not in qcontext and request.httprequest.method == 'POST':
            try:
                self.do_signup(qcontext)
                request.env['res.users'].Enrolment(kw.get('login'), password=kw.get('password'))
                request.session.logout(keep_db=True)
                return request.redirect('/web/email_prompt?login=%s' % kw.get('login'))
            except (SignupError, AssertionError) as e:
                if request.env["res.users"].sudo().search([("login", "=", qcontext.get("login"))]):
                    qcontext["error"] = _("Another user is already registered using this email address.")
                elif 'res_users_login_key' in e.message:
                    _logger.error(e.message)
                    qcontext["error"] = _("Please activate your account in your registered email address.")
                else:
                    _logger.error(e.message)
                    qcontext['error'] = _("Could not create a new account.")
            except Exception as e:
                request.session.logout(keep_db=True)
                e = e.message if e.message else str(e)
                _logger.error(e)
                return request.redirect('/web/email_verification?error=%s' % e)
        response = request.render('auth_signup.signup', qcontext)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    @http.route('/web/reset_password', type='http', auth='public', website=True)
    def web_auth_reset_password(self, *args, **kw):
        qcontext = self.get_auth_signup_qcontext()
        if not kw.get('token'):
            qcontext.update({'message': "Enter your user account's verified email address and we will send you a password reset link."})
        if not qcontext.get('token') and not qcontext.get('reset_password_enabled'):
            raise werkzeug.exceptions.NotFound()
        if 'error' not in qcontext and request.httprequest.method == 'POST':
            try:
                if qcontext.get('token'):
                    self.do_reset(qcontext)
                    value = {
                        'message': "Account password changed successfully",
                        'login': kw.get('login'),
                        'reset_password_enabled': True,
                        'signup_enabled': True
                    }
                    return request.render('web.login', value)
                else:
                    login = qcontext.get('login')
                    assert login, "No login provided."
                    _logger.info("Password reset attempt for <%s> by user <%s> from %s", login, request.env.user.login, request.httprequest.remote_addr)
                    request.env['res.users'].sudo().reset_password(login)
                    qcontext['message'] = _("Check your email for a link to reset your password. If it doesn't appear within a few minutes, check your span folder.")
            except SignupError:
                qcontext['error'] = _("Could not reset your password")
                _logger.exception('error when resetting password')
            except Exception as e:
                qcontext['error'] = e.message or e.name
                if not kw.get('token'):
                    qcontext.pop('message')
                    qcontext.update({'error': "That email address either can't be used to reset your password or isn't associated with a user account."})
        response = request.render('auth_signup.reset_password', qcontext)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    # 新路由 提醒客户查收邮箱 1小时有效的链接 UTC 时间
    @http.route('/web/email_prompt', type='http', auth='public', website=True)
    def web_email_prompt(self, *args, **kw):
        value = {}
        user_id = request.env['res.users'].sudo().search([('login', '=', kw.get('login')), ('active', '=?', False)])
        if not user_id:
            value.update({
                'message': _('Please enter the email you registered with!!'),
            })
        else:
            value.update({
                'message': _("Before you can conribute on iCloudFactory, we need you to verify your email address. </br>"
                             "An email containing verfication instructions was send to %s." % kw.get('login')),
                'login': kw.get('login'),
            })
        return request.render('personal_center.activation_and_resend', value)

    # 新路由 邮件返回的路径 激活账号 一次有效 暂不自动登入 进入个人中心
    @http.route('/web/email_verification', type='http', auth='public', website=True)
    def web_email_verifictaion(self, error=None, *args, **kw):
        try:
            # db, login, password = self.get_activation(kw.get('token'))
            # request.env.cr.commit()
            # request.session.authenticate(db, login, password)
            # return request.redirect('/my/home')
            value = self.get_activation(kw.get('token'))
            if value:
                value = {"message": 'Thank you! Your email was verified. Would you like to create your first order?'}
                return request.render("personal_center.ActivatedSuccessfully", value)
            return request.render("personal_center.ActivatedSuccessfully")
        except Exception as e:
            context = {
                'error': _("URL link invalid") if not error else error,
                'invalid_token': True
            }
            return request.render('personal_center.invalid', context)

    # 激活账号
    def get_activation(self, token):
        token = urllib.unquote(token)
        token = token.split('&')
        cen = request.env['personal.center'].sudo().browse(int(token[1]))
        if cen.word and cen.partner_id.signup_expiration >= time_utc(hours=+0):
            password = d64(token[0][5:5+int(cen.word)])
            db = d64(token[2][:3] + token[2][4:])
            cen.user_id.write({'active': True})
            cen.partner_id.write({'active': True, 'signup_token': False, 'signup_type': False, 'signup_expiration': False})
            cen.write({'word': False})
            # return db, cen.user_id.login, password
            return cen.user_id.login
        else:
            raise SignupError("Signup token '%s' is not valid" % token)

    def do_reset(self, qcontext):
        """ Shared helper that creates a res.partner out of a token """
        values = {key: qcontext.get(key) for key in ('login', 'name', 'password') }
        assert values.values(), "The form was not properly filled in."
        assert values.get('password') == qcontext.get('confirm_password'), "Passwords do not match; please retype them."
        supported_langs = [lang['code'] for lang in request.env['res.lang'].sudo().search_read([], ['code'])]
        if request.lang in supported_langs:
            values['lang'] = request.lang
        self._signup_values(qcontext.get('token'), values)

    def _signup_values(self, token, values):
        db, login, password = request.env['res.users'].sudo().signup(values, token)
        return True

