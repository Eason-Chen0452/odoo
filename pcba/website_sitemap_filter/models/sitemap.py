# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from itertools import islice
from odoo.exceptions import UserError
LOC_PER_SITEMAP = 45000


class CpoSiteMapUrl(models.Model):
    _name='cpo.sitemap.url'
    _description = 'CPO Web Site Map'

    name = fields.Char('Name')
    url = fields.Char('Url')
    title = fields.Char('Title')
    keywords = fields.Char('Keywords')
    description = fields.Char('Description')
    active = fields.Boolean("Active", default=True)
    robots_disable = fields.Boolean('Robots Disable')
    priority = fields.Char("Priority", default='0.5')
    changefreq = fields.Char("Changefreq", default="weekly")

    @api.constrains('url')
    def _check_url(self):
        if self.search_count([('url', '=', self.url)]) > 1:
            raise UserError(_('Find url repeat sitemap!'))

    @api.model
    def get_header_api(self, url):
        '''
            get api for url.
        '''
        row = self.search([('url','=', url)], limit=1)
        res = {
            'title': row.title or 'PCB & PCBA -- One Step Service',
            'keywords': row.keywords or 'PCB & PCBA -- One Step Service',
            'description': row.description or 'PCB & PCBA -- One Step Service',
        }
        return res

    @api.multi
    def add_sitemap_url(self, urls):
        for url in urls:
            if self.search([('url', '=', url),('active','=',False)]):
                self.search([('url', '=', url),('active', '=', False)]).write({'active':True})
            elif not self.search([('url','=',url)]):
                self.create({
                    'name':self.update_sitemap_name(url),
                    'url':url,
                })
        old_urls = list(set(self.search([]).mapped('url'))-set(urls))
        if old_urls:
            self.search([('url', 'in', old_urls)]).write({'active':False})

    @api.multi
    def update_sitemap_name(self, name):
        name = name.split('/')[-1] or 'index'
        if '_' in name:
            names = name.split('_')
            names = [x.capitalize() for x in names]
            return ' '.join(names)
        elif '-' in name:
            names = name.split('-')
            names = [x.capitalize() for x in names]
            return ' '.join(names)
        else:
            return name.capitalize()

class CpoSiteMapSetWizard(models.TransientModel):
    _name = 'cpo.sitemap.set.wizard'
    _description = 'Cpo Sitemap Set Wizard'

    update_sitemap = fields.Boolean('Update SiteMap')
    url_id  = fields.Many2one('cpo.sitemap.url', 'Url')
    name  = fields.Char('Name', related='url_id.name')
    url  = fields.Char('Url', related='url_id.url')
    title = fields.Char('Title', related='url_id.title')
    keywords = fields.Char('Keywords', related='url_id.keywords')
    description = fields.Char('Description', related='url_id.description')
    robots_disable = fields.Boolean('Robots Disable', related='url_id.robots_disable')
    priority = fields.Char("Priority", related='url_id.priority')
    changefreq = fields.Char("Changefreq", related='url_id.changefreq')

    @api.multi
    def act_confirm(self):
        '''
        to set header for url.
        '''
        self.update_sitemap_data()

    @api.onchange('update_sitemap')
    def update_sitemap_data(self):
        website_env = self.env['website']
        website = website_env.search([])[0]
        current_website = website
        Attachment = self.env['ir.attachment'].sudo()
        View = self.env['ir.ui.view'].sudo()
        mimetype = 'application/xml;charset=utf-8'
        content = None
        loc_url_list = []

        root_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url', default=False)

        def clear_sitemap():
            url = "/sitemap-%d.xml" % current_website.id
            atta_un_ids = Attachment.search([('name', '=', url),('url','=',url),('type','=','binary'),('mimetype','=',mimetype)])
            atta_un_ids.unlink()

        def create_sitemap(url, content):
            return Attachment.create({
                'res_model':'',
                'datas': content.encode('base64'),
                'mimetype': mimetype,
                'type': 'binary',
                'name': url,
                'url': url,
            })

        locs = website.with_context(use_public_user=True).enumerate_pages()
        locs = [x for x in locs]
        loc_url = []
        pages = 0
        for row_loc in locs:
            lloc = [row_loc['loc']]
            loc = lloc[0]
            if website.exclude_from_sitemap:
                cpo_check_ex = False
                exclude_from_sitemap = website.exclude_from_sitemap.splitlines()
                exclude_from_sitemap_new = filter(lambda x:x.endswith('*'), exclude_from_sitemap)
                for e_x in exclude_from_sitemap_new:
                    if e_x and loc.startswith(e_x[:-1]):
                        cpo_check_ex = True
                        break
                if cpo_check_ex or lloc[0] in exclude_from_sitemap:
                    continue
            loc_url.append(row_loc)
            loc_url_list.append(loc)
            pages = 0
        clear_sitemap()
        while True:

            start = pages * LOC_PER_SITEMAP
            values = {
                'locs': islice(loc_url, start, start + LOC_PER_SITEMAP),
                'url_root': root_url,
            }
            urls = View.render_template('website.sitemap_locs', values)
            if urls.strip():
                content = View.render_template('website.sitemap_xml', {'content': urls})
                pages += 1
                last_sitemap = create_sitemap('/sitemap-%d-%d.xml' % (current_website.id, pages), content)
            else:
                break

        if not pages:
            return 'error:no page'
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
                'url_root': root_url,
            })
            create_sitemap('/sitemap-%d.xml' % current_website.id, content)
        self.env['cpo.sitemap.url'].add_sitemap_url(loc_url_list)
        return {}
