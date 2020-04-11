# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api
from odoo.http import request

class Website(models.Model):
    _inherit = 'website'

    exclude_from_sitemap = fields.Text('Exclude from sitemap')

    @api.multi
    def enumerate_pages(self, query_string=None):
        """ Available pages in the website/CMS. This is mostly used for links
            generation and can be overridden by modules setting up new HTML
            controllers for dynamic pages (e.g. blog).
            By default, returns template views marked as pages.
            :param str query_string: a (user-provided) string, fetches pages
                                     matching the string
            :returns: a list of mappings with two keys: ``name`` is the displayable
                      name of the resource (page), ``url`` is the absolute URL
                      of the same.
            :rtype: list({name: str, url: str})
        """
        router = request.httprequest.app.get_db_router(request.db)
        # Force enumeration to be performed as public user
        url_set = set()
        sitemap_obj = self.env['cpo.sitemap.url'].sudo()
        for rule in router.iter_rules():
            if not self.rule_is_enumerable(rule):
                continue

            converters = rule._converters or {}
            if query_string and not converters and (query_string not in rule.build([{}], append_unknown=False)[1]):
                continue
            values = [{}]
            convitems = converters.items()
            # converters with a domain are processed after the other ones
            convitems.sort(key=lambda x: hasattr(x[1], 'domain') and (x[1].domain != '[]'))
            for (i, (name, converter)) in enumerate(convitems):
                newval = []
                for val in values:
                    query = i == len(convitems)-1 and query_string
                    for value_dict in converter.generate(uid=self.env.uid, query=query, args=val):
                        newval.append(val.copy())
                        value_dict[name] = value_dict['loc']
                        del value_dict['loc']
                        newval[-1].update(value_dict)
                values = newval

            for value in values:
                domain_part, url = rule.build(value, append_unknown=False)
                dis_list = sitemap_obj.search([('url', '=', url)]).mapped(lambda x:{'priority':x.priority,'changefreq':x.changefreq})
                if dis_list:
                    res_list = {
                        'priority':dis_list[0]['priority'],
                        'changefreq':dis_list[0]['changefreq']
                     }
                else:
                    res_list = {
                        'priority':0.5,
                        'changefreq':'weekly'
                    }
                page = {'loc': url, 'lastmod': fields.Date.today(), 'priority': res_list['priority'], 'changefreq':res_list['changefreq']}
                for key, val in value.items():
                    if key.startswith('__'):
                        page[key[2:]] = val
                if url in ('/sitemap.xml',):
                    continue
                if url in url_set:
                    continue
                url_set.add(url)

                yield page

class WebsiteConfigSettings(models.TransientModel):
    _inherit = 'website.config.settings'

    exclude_from_sitemap = fields.Text(related='website_id.exclude_from_sitemap',
                                               string='Exclude from sitemap',
                                               help="Enter the urls to be excluded from sitemap")
