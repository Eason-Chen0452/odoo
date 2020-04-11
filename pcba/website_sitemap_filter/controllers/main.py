import datetime
from itertools import islice
import logging


import odoo
from odoo import http
from odoo import fields
from odoo.http import request
from odoo.addons.web.controllers.main import WebClient, Binary, Home
LOC_PER_SITEMAP = 45000
SITEMAP_CACHE_TIME = datetime.timedelta(hours=12)

_logger = logging.getLogger(__name__)


class Website(Home):

    @http.route('/sitemap.xml', type='http', auth="public", website=True)
    def sitemap_xml_index(self):
        current_website = request.website
        Attachment = request.env['ir.attachment'].sudo()
        View = request.env['ir.ui.view'].sudo()
        mimetype = 'application/xml;charset=utf-8'
        content = None

        def create_sitemap(url, content):
            return Attachment.create({
                'datas': content.encode('base64'),
                'mimetype': mimetype,
                'type': 'binary',
                'name': url,
                'url': url,
            })
        dom = [('url', '=' , '/sitemap-%d.xml' % current_website.id), ('type', '=', 'binary')]
        sitemap = Attachment.search(dom, limit=1)
        if sitemap:
            # Check if stored version is still valid
            create_date = fields.Datetime.from_string(sitemap.create_date)
            delta = datetime.datetime.now() - create_date
            if delta < SITEMAP_CACHE_TIME:
                content = sitemap.datas.decode('base64')

        if not content:
            # Remove all sitemaps in ir.attachments as we're going to regenerated them
            dom = [('type', '=', 'binary'), '|', ('url', '=like' , '/sitemap-%d-%%.xml' % current_website.id),
                   ('url', '=' , '/sitemap-%d.xml' % current_website.id)]
            sitemaps = Attachment.search(dom)
            sitemaps.unlink()

            pages = 0
            locs = request.website.with_context(use_public_user=True).enumerate_pages()

            # if handled in model, it won't show urls when searched for linking.
            if request.website.exclude_from_sitemap:
                exclude_from_sitemap = request.website.exclude_from_sitemap.splitlines()

                raw_locs = locs;
                locs = []

                for loc in raw_locs:
                    lloc = loc.values()
                    cpo_check_ex = False
                    exclude_from_sitemap_new = filter(lambda x:x.endswith('*'), exclude_from_sitemap)
                    for e_x in exclude_from_sitemap_new:
                        if e_x and loc.startswith(e_x[:-1]):
                            cpo_check_ex = True
                            break
                    if cpo_check_ex or lloc[0] in exclude_from_sitemap:
                    #if lloc[0] in exclude_from_sitemap:
                        _logger.info("Sitemap url Excluding: %s" % lloc[0])
                    else:
                        locs.append(loc)
            while True:
                start = pages * LOC_PER_SITEMAP
                values = {
                    'locs': islice(locs, start, start + LOC_PER_SITEMAP),
                    'url_root': request.httprequest.url_root[:-1],
                }
                urls = View.render_template('website.sitemap_locs', values)
                if urls.strip():
                    content = View.render_template('website.sitemap_xml', {'content': urls})
                    pages += 1
                    last_sitemap = create_sitemap('/sitemap-%d-%d.xml' % (current_website.id, pages), content)
                else:
                    break

            if not pages:
                return request.not_found()
            elif pages == 1:
                # rename the -id-page.xml => -id.xml
                last_sitemap.write({
                    'url': "/sitemap-%d.xml" % current_website.id,
                    'name': "/sitemap-%d.xml" % current_website.id,
                })
            else:
                # TODO: in master/saas-15, move current_website_id in template directly
                pages_with_website = map(lambda p: "%d-%d" % (current_website.id, p), range(1, pages + 1))

                # Sitemaps must be split in several smaller files with a sitemap index
                content = View.render_template('website.sitemap_index_xml', {
                    'pages': pages_with_website,
                    'url_root': request.httprequest.url_root,
                })
                create_sitemap('/sitemap-%d.xml' % current_website.id, content)

        return request.make_response(content, [('Content-Type', mimetype)])

    @http.route(['/robots.txt'], type='http', auth="public")
    def robots(self):
        sitemap_obj = request.env['cpo.sitemap.url'].sudo()
        dis_list = sitemap_obj.search([('robots_disable', '=', 'True')]).mapped("url")
        return request.render('website_sitemap_filter.robots', {'url_root': request.httprequest.url_root,'dis_list':dis_list}, mimetype='text/plain')
