# -*- coding: utf-8 -*-
from odoo import http, fields, models
import re
import hashlib
import mimetypes
from odoo.tools.mimetypes import guess_mimetype
import os
from odoo.http import request, STATIC_CACHE, content_disposition
import imghdr
from cStringIO import StringIO
from odoo.exceptions import AccessDenied, AccessError
from odoo.modules.module import get_resource_path, get_module_path

import babel.messages.pofile
import base64
import werkzeug
import werkzeug.utils
import werkzeug.wrappers
from odoo.addons.website.models.website import slug, unslug
import odoo
import odoo.modules.registry
from odoo import http
from odoo.http import content_disposition, dispatch_rpc, request

def binary_content(xmlid=None, model='ir.attachment', id=None, field='datas', unique=False, filename=None, filename_field='datas_fname', download=False, mimetype=None, default_mimetype='application/octet-stream', env=None):
    img_data = request.registry['ir.http'].cpo_binary_content(
        xmlid=xmlid, model=model, id=id, field=field, unique=unique, filename=filename, filename_field=filename_field,
        download=download, mimetype=mimetype, default_mimetype=default_mimetype, env=env)
    return img_data

class GenerateImageURL(http.Controller):
    """
    生成图片路由
    """

    @http.route(['/cpo/image',
        '/website/cpo_image_show/<cpo_model>/<id>'], type="http", auth='public', website=True)
    def website_image_cpo(self, model=None, id=None, **kw):
        id_data = unslug(id)
        id = id_data[len(id_data)-1]
        model = kw.get('cpo_model')
        status, headers, content, image_base64 = self.cpo_get_binary_content(model=model, id=id, unique=False, width=0, height=0)
        response = request.make_response(image_base64, headers)
        response.status_code = status
        return response

    def cpo_get_binary_content(self, model=None, id=None, unique=False, width=0, height=0):
        """
        解析图片，SVG转码更好请求头
        :param model:
        :param id:
        :param unique:
        :param width:
        :param height:
        :return:
        """
        status, headers, content = None, [], None
        content = request.registry['ir.http'].cpo_check_model_data(model, id)
        # cache
        etag = hasattr(request, 'httprequest') and request.httprequest.headers.get('If-None-Match')
        retag = '"%s"' % hashlib.md5(content).hexdigest()
        status = status or (304 if etag == retag else 200)
        headers.append(('ETag', retag))
        headers.append(('Cache-Control', 'max-age=%s' % (STATIC_CACHE if unique else 0)))
        # mimetype
        headers += [('X-Content-Type-Options', 'nosniff')]
        height = int(height or 0)
        width = int(width or 0)
        if content and (width or height):
            # resize maximum 500*500
            if width > 500:
                width = 500
            if height > 500:
                height = 500
            content = odoo.tools.image_resize_image(base64_source=content, size=(width or None, height or None),
                                                    encoding='base64', filetype='SVG')
            # resize force png as filetype
            headers = self.force_contenttype(headers, contenttype='image/png')

        if content:
            image_base64 = base64.b64decode(content)
            get_svg = re.search('svg', image_base64)
            if get_svg:
                headers.append(('Content-Type', u'image/svg+xml'))
            else:
                headers.append(('Content-Type', u'image/png'))
        else:
            image_base64 = self.placeholder(image='placeholder.png')  # could return (contenttype, content) in master
            headers = self.force_contenttype(headers, contenttype='image/png')
        headers.append(('Content-Length', len(image_base64)))
        return (status, headers, content, image_base64)

class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'
    _description = "HTTP routing"

    @classmethod
    def cpo_check_model_data(self, name, id):
        """
        检查并返回二进制编码
        :param name:
        :param id:
        :return:
        """
        content, get_data = None, None
        if name == 'cpo_banner':
            get_data = request.env['cpo_banner_image'].sudo().search([('id', '=', id)])
            content = get_data.cpo_banner_img
        elif name == 'pcba_condition':
            get_data = request.env['cpo_pcba_condition'].sudo().search([('id', '=', id)])
            content = get_data.condition_photo
        elif name == 'package_price':
            get_data = request.env['cpo_package_price'].sudo().search([('id', '=', id)])
            content = get_data.cpo_layer_photo
        elif name == 'products_advertage':
            get_data = request.env['cpo_advertage_products'].sudo().search([('id', '=', id)])
            content = get_data.cpo_ad_poto
        return content
