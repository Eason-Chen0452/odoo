# -*- coding: utf-8 -*-
from odoo import http, tools, _
from odoo.http import request
from odoo.addons.website_cpo_seo.controllers.cpo_setting_seo import Website
from odoo.addons.web.controllers.main import ensure_db, Home
from odoo.addons.auth_signup.models.res_users import SignupError
from odoo.addons.website_cpo_index.controllers.cpo_quotation_record_code import CpoQuotationRecordCode
import urlparse
from odoo.addons.website.models.website import slug,unslug
import werkzeug
import base64
import logging
_logger = logging.getLogger(__name__)


class CpoWebsiteHelp(http.Controller):

    @http.route('/page/help', type="http", auth="public", website=True)
    def page_help(self, type=None, **kw):
        """
        Help 的路由
        :param type:
        :param kw:
        :return:
        """
        values, help_obj, ho = {}, None, True
        if not type:
            type = 'default'
        help_pool = request.env['cpo_help.help'].sudo()
        help_obj = help_pool.getHelpData(type)
        if not help_obj:
            ho = False
        values.update({
            'type': type,
            'help_obj': help_obj,
            'ho': ho,
        })
        return request.render("website_cpo_sale.cpo_page_help", values)

    @http.route('/help/search', type="json", auth="public", website=True)
    def cpo_help_search(self, **kw):
        """
        help页面的搜索
        :param kw:
        :return:
        """
        search_data = kw.get('search')
        help_pool = request.env['cpo_help.help'].sudo()
        search = help_pool.help_search(search_data.strip())
        if not search:
            kw.update({
                'error': 'No related content!'
            })
            return kw
        if search.type == 'default':
            url = '/page/help'
        else:
            url = '/page/help?type=' + str(search.type)
        kw.update({
            'url': url,
        })
        return kw
