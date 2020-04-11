# -*- coding: utf-8 -*-

"""
    工程中的规格
"""

from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
import odoo.addons.decimal_precision as dp
from odoo.exceptions import ValidationError

AVAILABLE_PRICE_TYPE = [
    ('item', 'Item'),
    ('csize', 'Size(cm²)'),
    ('msize', 'Size(㎡)'),
    ('pcs', 'PCS'),
    ('set', 'SET'),
]


# 主表 - 只是将用户关联起来
class pcb_quotation_pricelist(models.Model):

    _name = "pcb.quotation.pricelist"
    _description = "PCB Price List"
    _order = 'name desc'

    partner_id = fields.Many2one('res.partner', 'Partner', change_default=False, index=True)
    name = fields.Char('Price List Number', size=64, required=True, translate=True, default='/')
    pricelist_type = fields.Selection([('sales', 'Sales Price List'),
                                       ('purchase', 'Purchase Price List'),
                                       ], 'Price List Type', required=False, default='sales')
    general_price = fields.Boolean('General Price List',
                                   help='If Checked this option, it will allow you to all PCB Quotation without partner ID', default=False)
    cost_price = fields.Boolean('Cost Price List', default=False)
    version_id = fields.One2many('pcb.quotation.pricelist.version', 'pricelist_id', 'Price List Versions')
    currency_id = fields.Many2one('res.currency', 'Currency', compute='_get_currency', required=True)
    date_created = fields.Date('Created Date', required=True, readonly=True, default=fields.Datetime.now)
    date_updated = fields.Date('Updated Date', required=True, readonly=True, default=fields.Datetime.now)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.user.company_id.id)
    memo = fields.Text('Memo')
    active = fields.Boolean('Active', help="If unchecked, it will allow you to hide the pricelist without removing it.", default=True)

    def _get_currency(self):
        comp = self.env['res.users'].search([('id', '=', self.env.uid)]).company_id
        if not comp:
            comp_id = self.env['res.company'].search([])[0]
            comp = self.env['res.company'].browse(comp_id)
        return comp.currency_id.id

    def _check_cost_general_price(self):
        quotation_price_row = self.env['pcb.quotation.pricelist'].browse()

        if not quotation_price_row.active:
            return True
        if not (quotation_price_row.general_price or quotation_price_row.cost_price):
            return True
        if quotation_price_row.general_price and quotation_price_row.cost_price:
            return False
        if quotation_price_row.general_price:
            self.env.cr.execute('SELECT count(id) FROM pcb_quotation_pricelist WHERE general_price=True and active=True')
        else:
            self.env.cr.execute('SELECT count(id) FROM pcb_quotation_pricelist WHERE cost_price=True and active=True')
        quotation_price_count = self.env.cr.fetchone()[0]

        if quotation_price_count > 1:
            return False
        return True

    def _check_partner_uniq(self):
        quotation_pricelist_row = self.env['pcb.quotation.pricelist'].browse()

        if not quotation_pricelist_row.active:
            return True
        if quotation_pricelist_row.general_price or quotation_pricelist_row.cost_price:
            return True
        if not quotation_pricelist_row.partner_id:
            return False
        else:
            partner_id = quotation_pricelist_row.partner_id.id
        self.env.cr.execute(
            'SELECT count(id) FROM pcb_quotation_pricelist WHERE active = True and partner_id = %s' % (partner_id,))

        quotation_pricelist_count = self.env.cr.fetchone()[0]

        if quotation_pricelist_count > 1:
            return False
        return True

    _constraints = [
        (_check_cost_general_price, 'General Price or Cost Price must be unique in active price list.',
         ['name', 'pricelist_type']),
        (_check_partner_uniq, 'Every partner price list be unique in active price list.', ['partner_id', ]),
    ]

    _sql_constraints = [
        ('pricelist_uniq', 'unique(partner_id,pricelist_type,general_price,cost_price,active)',
        'price list must be unique per partner!'),
    ]

    @api.model
    def create(self, vals):
        if vals.get('name') == '/':
            if vals.get('pricelist_type', 'sales') == 'sales':
                vals['name'] = self.env['ir.sequence'].get('pcb.quotation.pricelist.sales') or '/'
            else:
                vals['name'] = self.env['ir.sequence'].get('pcb.quotation.pricelist.purchase') or '/'
        partner_id = False
        if vals.get('partner_id'):
            partner_id = self.env['res.partner'].search([('id', '=', vals.get('partner_id'))])
        if 'version_id' in vals and self.env.context.get('copy'):
            for l in vals['version_id']:
                if not l[0]:
                    date_start = datetime.now()
                    date_end = date_start + relativedelta(months=6)
                    l[2].update({'date_start': fields.Date.context_today(self, timestamp=date_start),
                                 'date_end': fields.Date.context_today(self, timestamp=date_end)})
        pricelist_id = super(pcb_quotation_pricelist, self).create(vals)
        if partner_id:
            self.env['res.partner'].search([('id', '=', partner_id.id)]).write({
                'property_pcb_quotation_pricelist': pricelist_id
            })
        return pricelist_id

    @api.multi
    def copy(self, default=None):
        default = {} if default is None else default.copy()
        default.update({
            'date_created': fields.datetime.now(),
            'date_updated': fields.datetime.now(),
            'partner_id': False,
            'name': '/',
            'active': False,
        })
        return super(pcb_quotation_pricelist, self).copy(self.env.id, default=default)

    @api.multi
    def write(self, vals):
        if isinstance(self.ids, (int, long)):
            ids = [self.ids]
        vals['date_updated'] = fields.datetime.now()
        if vals.get('name') == '/':
            pricetype_lists = self.read(self.ids, ['pricelist_type'])
            if pricetype_lists[0]['pricelist_type'] == 'sales':
                vals['name'] = self.env['ir.sequence'].get('pcb.quotation.pricelist.sales') or '/'
            else:
                vals['name'] = self.env['ir.sequence'].get('pcb.quotation.pricelist.purchase') or '/'
        if not vals.get('name'):
            pricetype_lists = self.read(['name', 'pricelist_type'])
            if pricetype_lists[0]['name'] == '/':
                if pricetype_lists[0]['pricelist_type'] == 'sales':
                    vals['name'] = self.env['ir.sequence'].get('pcb.quotation.pricelist.sales') or '/'
                else:
                    vals['name'] = self.env['ir.sequence'].get('pcb.quotation.pricelist.purchase') or '/'
        if vals.get('partner_id'):
            for pricelist in self.browse(self.ids):
                partner_ids = self.env['res.partner'].search([('id', '=', pricelist.partner_id.id)])
                self.env['res.partner'].write(partner_ids, {'property_pcb_quotation_pricelist': None, })
                self.env['res.partner'].write([vals['partner_id']],
                                                   {'property_pcb_quotation_pricelist': pricelist.id, })
        else:
            for pricelist in self.browse(self.ids):
                if pricelist.partner_id:
                    partner_ids = self.env['res.partner'].search([('id', '=', pricelist.partner_id.id)])
                    self.env['res.partner'].search([('id', '=', partner_ids.id)]).write({'property_pcb_quotation_pricelist': None})

        result = super(pcb_quotation_pricelist, self).write(vals)
        return result

    @api.onchange('general_price', 'pricelist_type')
    def onchange_check_pricelist(self):
        if self.general_price and self.pricelist_type == 'sales':
            pricelist_ids = self.search([('general_price', '=', True), ('pricelist_type', '=', 'sales')])
            if len(pricelist_ids) >= 1:
                self.general_price = False
                self.pricelist_type = ''
                return {
                    'warning': {
                        'title': _("Incorrect 'General Price List and Prict List Type' value"),
                        'message': _("The general price sales table already exists and no longer create"),
                    },
                }


# 操作中心
class pcb_quotation_pricelist_version(models.Model):
    _name = "pcb.quotation.pricelist.version"
    _description = "Price List Versions"

    pricelist_id = fields.Many2one('pcb.quotation.pricelist', 'Price List', required=True, index=True, ondelete='cascade')
    name = fields.Char('Name', size=64, required=True, translate=True)
    currency_id = fields.Many2one('res.currency', 'Currency', required=True)  # compute='_get_currency')
    tax = fields.Boolean('Include Tax', required=False, default=False)
    tax_id = fields.Many2one('account.tax', 'Taxes')
    active = fields.Boolean('Active',
                            help="When a version is duplicated it is set to non active, so that the " \
                                 "dates do not overlaps with original version. You should change the dates " \
                                 "and reactivate the pricelist", default=True)
    items_id = fields.One2many('pcb.quotation.pricelist.layer.item', 'price_version_id',
                               'Price List of Board Material', required=True)
    textcolor_ids = fields.One2many('pcb.quotation.pricelist.text.color', 'price_version_id',
                                    'Price List of Text Color')
    silkscreencolor_ids = fields.One2many('pcb.quotation.pricelist.silkscreen.color', 'price_version_id',
                                          'Price List of Silkscreen Color')
    surfaceprocess_ids = fields.One2many('pcb.quotation.pricelist.surface.process', 'price_version_id',
                                         'Price List of Surface Process')
    smaterial_ids = fields.One2many('pcb.quotation.pricelist.special.material', 'price_version_id',
                                    'Price List of Special Material')
    sprocess_ids = fields.One2many('pcb.quotation.pricelist.special.process', 'price_version_id',
                                   'Price List of Special Process')
    tooling_ids = fields.One2many('pcb.quotation.pricelist.tooling', 'price_version_id',
                                  'Price List of Test Tooling')
    etest_ids = fields.One2many('pcb.quotation.pricelist.etest', 'price_version_id', 'Price List of ETest')
    film_ids = fields.One2many('pcb.quotation.pricelist.film', 'price_version_id', 'Price List of Film')
    other_ids = fields.One2many('pcb.quotation.pricelist.other', 'price_version_id', 'Price List of Other Fee')
    date_start = fields.Date('Start Date', required=True, help="First valid date for the version.", default=fields.Datetime.now)
    date_end = fields.Date('End Date', required=True, help="Last valid date for the version.",
                           default=(datetime.today() + relativedelta(weekday=0, days=0, months=6)).strftime('%Y-%m-%d'))
    combine_number = fields.Integer('Combine Number', default=1)
    combine_fee = fields.Float('Combine Fee', default=100)
    combine_fee_number = fields.Integer('Combine Fee Number', default=1)
    memo = fields.Text('Memo')
    company_id = fields.Many2one('res.company', related='pricelist_id.company_id',
                                 readonly=True, store=True)

    # def _get_currency(self):
    #     comp = self.env['res.users'].search([('id', '=', self.env.uid)]).company_id
    #     if not comp:
    #         comp_id = self.env['res.company'].search([])[0]
    #         comp = self.env['res.company'].browse(comp_id)
    #     return comp.currency_id.id

    _sql_constraints = [
        ('partner_currency_uniq', 'unique(pricelist_id, currency_id, tax, date_start, date_end, active)',
         'Please make sure of currency, tax, date start and date end in every active price lsit version!'),
    ]

    def _check_date(self):
        for pricelist_version in self.browse(self.ids):
            if not pricelist_version.active:
                continue
            if not pricelist_version.date_start or not pricelist_version.date_end:
                return False
            if pricelist_version.date_start >= pricelist_version.date_end:
                return False
            where = ''
            if pricelist_version.date_start and pricelist_version.date_end:
                where = "((tax = '%s') and (date_end>='%s') and (date_start<='%s'))" % (
                pricelist_version.tax, pricelist_version.date_start, pricelist_version.date_end,)
            else:
                return False

            self.env.cr.execute('SELECT id '\
                                'FROM pcb_quotation_pricelist_version '\
                                'WHERE ' + where + ' and ' +
                                'pricelist_id = %s '\
                                'AND active = True '\
                                'AND currency_id = %s '\
                                'AND id <> %s', (
                                pricelist_version.pricelist_id.id,
                                pricelist_version.currency_id.id,
                                pricelist_version.id))
            if self.env.cr.fetchall():
                return False
        return True
    _constraints = [
        (_check_date,
         'Error!\nThis version End Date less than Start Date or Don\'t have 2 pricelist versions that overlap!',
         ['date_start', 'date_end'])
    ]
    # We desactivate duplicated pricelists, so that dates do not overlap

    @api.multi
    def copy(self, default=None):
        default = {} if default is None else default.copy()
        default.update({
            'active': False,
        })
        return super(pcb_quotation_pricelist_version, self).copy(default)


class pcb_quotation_pricelist_special_material(models.Model):
    _name = "pcb.quotation.pricelist.special.material"
    _description = "Price List of Special Material"
    _order = "price_version_id, smaterial, max_size"

    # name = fields.Char('Special Material Name', size=64, required=True, translate=True)  # Special Material Name
    price_version_id = fields.Many2one('pcb.quotation.pricelist.version', 'Price List Versions', required=True,
                                       index=True, ondelete='cascade')
    smaterial = fields.Many2one('cam.special.material', 'Special Material')
    max_size = fields.Float('Max Size', required=True, digits=dp.get_precision('size'), default=1.0)
    price_type = fields.Selection(AVAILABLE_PRICE_TYPE, 'Price Type', required=True, default='item')
    price = fields.Float(string='Price', required=True, digits=dp.get_precision('Product Price'), default=0.0)

    _sql_constraints = [
        ('smaterial_maxsize_uniq', 'unique(price_version_id, smaterial, max_size)',
         'Special Material and Max Size must be unique per price list for every customer!'),
    ]


class pcb_quotation_pricelist_special_process(models.Model):
    _name = "pcb.quotation.pricelist.special.process"
    _description = "Price List of Special Process"
    _order = "price_version_id, sprocess, max_size"

    # 'name': fields.char('Special Process Name', size=64, help="Special Process name for this pricelist line."),
    price_version_id = fields.Many2one('pcb.quotation.pricelist.version', 'Price List Versions', required=True,
                                       index=True, ondelete='cascade')
    sprocess = fields.Many2one('cam.special.process', 'Special Process', domain=[('cpo_boolean', '=', False)])
    max_size = fields.Float('Max Size', required=True, digits=dp.get_precision('size'), default=1.0)
    price_type = fields.Selection(AVAILABLE_PRICE_TYPE, 'Price Type', required=True, default='item')
    price = fields.Float(string='Price', required=True, digits=dp.get_precision('Product Price'), default=0.0)

    _sql_constraints = [
        ('sprocess_maxsize_uniq', 'unique(price_version_id, sprocess, max_size)',
         'Special Process and Max Size must be unique per pricelist for every customer!'),
    ]


class pcb_quotation_pricelist_text_color(models.Model):
    _name = "pcb.quotation.pricelist.text.color"
    _description = "Price List of Text Color"
    _order = "price_version_id, text_color, max_size"

    # name = fields.Char('Text Color Name', size=64, required=True, translate=True)
    price_version_id = fields.Many2one('pcb.quotation.pricelist.version', 'Price List Versions', required=True,
                                       index=True, ondelete='cascade')
    text_color = fields.Many2one('cam.ink.color', 'Text Color')
    max_size = fields.Float('Max Size', required=True, digits=dp.get_precision('size'), default=1.0)
    price_type = fields.Selection(AVAILABLE_PRICE_TYPE, 'Price Type', required=True, default='item')
    price = fields.Float('Price', required=True, digits=dp.get_precision('Product Price'), default=0.0)

    _sql_constraints = [
        ('textcolor_maxsize_uniq', 'unique(price_version_id, text_color, max_size)',
         'Text Color and Max Size must be unique per pricelist for every customer!'),
    ]


class pcb_quotation_pricelist_silkscreen_color(models.Model):
    _name = "pcb.quotation.pricelist.silkscreen.color"
    _description = "Price List of Silkscreen Color"
    _order = "price_version_id, silkscreen_color, max_size"

    # name = fields.Char('Silkscreen Color Name', size=64, required=True, translate=True)
    price_version_id = fields.Many2one('pcb.quotation.pricelist.version', 'Price List Versions', required=True,
                                       index=True, ondelete='cascade')
    silkscreen_color = fields.Many2one('cam.ink.color', 'SilkScreen Color')
    max_size = fields.Float('Max Size', required=True, digits=dp.get_precision('size'), default=1.0)
    price_type = fields.Selection(AVAILABLE_PRICE_TYPE, 'Price Type', required=True, default='item')
    price = fields.Float('Price', required=True, digits=dp.get_precision('Product Price'), default=0.0)

    _sql_constraints = [
        ('silkscreen_maxsize_uniq', 'unique(price_version_id, silkscreen_color, max_size)',
         'Silkscreen Color and Max Size must be unique per customer!'),
    ]


class pcb_quotation_pricelist_surface_process(models.Model):
    _name = "pcb.quotation.pricelist.surface.process"
    _description = "Price List of Surface Process"
    _order = "price_version_id, surface, max_size"

    # name = fields.Char('Surface Process Name', size=64, required=True, translate=True)
    price_version_id = fields.Many2one('pcb.quotation.pricelist.version', 'Price List Versions', required=True,
                                       index=True, ondelete='cascade')
    surface = fields.Many2one('cam.surface.process', 'Surface Process')
    max_size = fields.Float('Max Size', required=True, digits=dp.get_precision('size'), default=1.0)
    price_type = fields.Selection(AVAILABLE_PRICE_TYPE, 'Price Type', required=True, default='item')
    price = fields.Float('Price', required=True, digits=dp.get_precision('Product Price'), default=0.0)

    # _sql_constraints = [
    #     ('surface_maxsize_uniq', 'unique(price_version_id, surface, max_size)',
    #      'Surface Process and Max Size must be unique per pricelist!'),
    # ]


class pcb_quotation_pricelist_film(models.Model):
    _name = "pcb.quotation.pricelist.film"
    _description = "Price List of Film"
    _order = "price_version_id, min_size, max_size"

    # name = fields.Char('Rule Name', size=64, required=True, translate=True)
    price_version_id = fields.Many2one('pcb.quotation.pricelist.version', 'Price List Versions', required=True,
                                       index=True, ondelete='cascade')
    min_size = fields.Float('Min Size', required=True, digits=dp.get_precision('size'), default=0.0)
    max_size = fields.Float('Max Size', required=True, digits=dp.get_precision('size'), default=100.0)
    film_fee_type = fields.Selection(AVAILABLE_PRICE_TYPE, 'Film Fee Type', required=False, default='item')
    film_fee = fields.Float('Film Fee', required=False, digits=dp.get_precision('Product Price'), default=0.0)

    def _check_film_size(self):
        obj_film = self.env['pcb.quotation.pricelist.film'].browse(self.ids[0])
        if obj_film.min_size > obj_film.max_size:
            return False
        version_id = obj_film.price_version_id.id
        min_size = obj_film.min_size
        max_size = obj_film.max_size
        self.env.cr.execute('SELECT count(id) FROM pcb_quotation_pricelist_film WHERE price_version_id=%s AND max_size>%f AND min_size<%f AND id != %s' % (
                            version_id, min_size, max_size, obj_film.id))
        eline_rows = self.env.cr.fetchone()[0] or 0.0
        if eline_rows:
            return False
        return True

    _constraints = [
        (_check_film_size, 'Error!\nThe row film min size and max size overlap other rows.', ['min_size', 'max_size'])
    ]

    _sql_constraints = [
        ('version_film_uniq', 'unique(price_version_id, min_size, max_size)',
         'Film size must be unique in active version of pcb price list!'),
    ]


class pcb_quotation_pricelist_layer_item(models.Model):
    _name = "pcb.quotation.pricelist.layer.item"
    _description = "Price List of Board Material"
    _order = "price_version_id, layer_number"

    price_version_id = fields.Many2one('pcb.quotation.pricelist.version', 'Price List Versions', required=True,
                                       index=True, ondelete='cascade')
    layer_number = fields.Many2one('cam.layer.number', 'Layer Number', required=True, index=True)
    min_size = fields.Float('Min Size', required=True, digits=dp.get_precision('size'), default=0.0)
    max_size = fields.Float('Max Size', required=True, digits=dp.get_precision('size'), default=100.0)
    combine_number = fields.Integer('Combine Number', default=1)
    combine_fee = fields.Float('Combine Fee', default=100)
    combine_fee_number = fields.Integer('Combine Fee Number', default=1)
    min_thickness = fields.Float('Min Thickness', required=True, digits=dp.get_precision('size'), default=0.1)
    max_thickness = fields.Float('Max Thickness', required=True, digits=dp.get_precision('size'), default=10.0)
    min_inner_copper = fields.Float('Min Inner Copper', required=False, digits=dp.get_precision('size'), default=0.5)
    max_inner_copper = fields.Float('Max Inner Copper', required=False, digits=dp.get_precision('size'), default=4.0)
    min_outer_copper = fields.Float('Min Outer Copper', required=False, digits=dp.get_precision('size'), default=0.5)
    max_outer_copper = fields.Float('Max Outer Copper', required=False, digits=dp.get_precision('size'), default=10.0)
    item_size_ids = fields.One2many('pcb.quotation.pricelist.layer.size', 'layer_item_id',
                                    'Price List of Board Size')
    item_thickness_ids = fields.One2many('pcb.quotation.pricelist.layer.thickness', 'layer_item_id',
                                         'Price List of Board Thickness')
    item_outer_copper_ids = fields.One2many('pcb.quotation.pricelist.layer.outer.copper', 'layer_item_id',
                                            'Price List of Outer Copper')
    item_inner_copper_ids = fields.One2many('pcb.quotation.pricelist.layer.inner.copper', 'layer_item_id',
                                            'Price List of Inner Copper')

    _sql_constraints = [
        ('version_layernumber_uniq', 'unique(price_version_id, layer_number)',
         'Layer Number must be unique in Price List of Board Material for every version of price list!'),
    ]


class pcb_quotation_pricelist_layer_thickness(models.Model):
    _name = "pcb.quotation.pricelist.layer.thickness"
    _description = "Price List of Board Thickness"
    _order = "layer_item_id,min_thickness, max_thickness"

    layer_item_id = fields.Many2one('pcb.quotation.pricelist.layer.item', 'Price List of Board Material', ondelete='cascade')
    min_thickness = fields.Float('Min Thickness', required=True, digits=dp.get_precision('size'), default=0.0)
    max_thickness = fields.Float('Max Thickness', required=True, digits=dp.get_precision('size'), default=0.0)
    add_fee_type = fields.Selection(AVAILABLE_PRICE_TYPE, 'Add Fee Type', required=True, default='item')
    add_fee = fields.Float('Add Fee', required=True, digits=dp.get_precision('Product Price'), default=0.0)

    def _check_thickness(self):
        obj_thickness = self.env['pcb.quotation.pricelist.layer.thickness'].browse(self.ids[0])
        # thickness_lst = self.read(self, ids[0])
        if obj_thickness.min_thickness > obj_thickness.max_thickness:
            return False
        layer_item_id = obj_thickness.layer_item_id.id
        min_thickness = obj_thickness.min_thickness
        max_thickness = obj_thickness.max_thickness
        self.env.cr.execute('SELECT count(id) FROM pcb_quotation_pricelist_layer_thickness WHERE layer_item_id=%s AND max_thickness>%f  AND min_thickness<%f AND id != %s' % (
                            layer_item_id, min_thickness, max_thickness, obj_thickness.id))
        eline_rows = self.env.cr.fetchone()[0] or 0.0
        if eline_rows:
            return False
        return True

    _constraints = [
        (_check_thickness, 'Error!\nThe row min thickness and max thickness overlap other rows.',
         ['min_thickness', 'max_thickness'])
    ]

    _sql_constraints = [
        ('layer_thickness_uniq', 'unique(layer_item_id, min_thickness, max_thickness)',
         'PCB Board Thickness must be unique per price list!')
    ]

    @api.multi
    def write(self, vals):
        if 'max_thickness' in vals or 'min_thickness' in vals:
            pcb_thickness_item = self.browse(self.ids[0])
            layer_item_id = pcb_thickness_item.layer_item_id.id
            old_min_thickness = pcb_thickness_item.min_thickness
            old_max_thickness = pcb_thickness_item.max_thickness
            if 'min_thickness' in vals:
                min_thickness = vals['min_thickness']
                if old_min_thickness != min_thickness:
                    self.env.cr.execute('UPDATE pcb_quotation_pricelist_layer_thickness SET max_thickness=%f WHERE layer_item_id=%s AND max_thickness=%f' % (
                                        min_thickness, layer_item_id, old_min_thickness))
            if 'max_thickness' in vals:
                max_thickness = vals['max_thickness']
                if old_max_thickness != max_thickness:
                    self.env.cr.execute('UPDATE pcb_quotation_pricelist_layer_thickness SET min_thickness=%f WHERE layer_item_id=%s AND min_thickness=%f' % (
                                        max_thickness, layer_item_id, old_max_thickness))
        return super(pcb_quotation_pricelist_layer_thickness, self).write(vals)


class pcb_quotation_pricelist_layer_outer_copper(models.Model):
    _name = "pcb.quotation.pricelist.layer.outer.copper"
    _description = "Price List of Outer Copper"
    _order = "layer_item_id,min_outer_copper, max_outer_copper"

    layer_item_id = fields.Many2one('pcb.quotation.pricelist.layer.item', 'Price List of Board Material', ondelete='cascade')
    min_outer_copper = fields.Float('Min Outer Copper', required=True, digits=dp.get_precision('size'), default=0.0)
    max_outer_copper = fields.Float('Max Outer Copper', required=True, digits=dp.get_precision('size'), default=0.0)
    add_fee_type = fields.Selection(AVAILABLE_PRICE_TYPE, 'Add Fee Type', required=True, default='item')
    add_fee = fields.Float('Add Fee', required=True, digits=dp.get_precision('Product Price'), default=0.0)

    def _check_outer_copper(self):
        obj_outer_copper = self.env['pcb.quotation.pricelist.layer.outer.copper'].browse(self.ids[0])
        if obj_outer_copper.min_outer_copper > obj_outer_copper.max_outer_copper:
            return False
        layer_item_id = obj_outer_copper.layer_item_id.id
        min_outer_copper = obj_outer_copper.min_outer_copper
        max_outer_copper = obj_outer_copper.max_outer_copper
        self.env.cr.execute('SELECT count(id) FROM pcb_quotation_pricelist_layer_outer_copper WHERE layer_item_id=%s AND max_outer_copper>%f AND min_outer_copper<%f AND id != %s' % (
                            layer_item_id, min_outer_copper, max_outer_copper, obj_outer_copper.id))
        eline_rows = self.env.cr.fetchone()[0] or 0.0
        if eline_rows:
            return False
        return True

    _constraints = [
        (_check_outer_copper, 'Error!\nThe row min outer copper and max outer copper overlap other rows.',
         ['min_outer_copper', 'max_outer_copper'])
    ]

    _sql_constraints = [
        ('layer_inner_copper_uniq', 'unique(layer_item_id, min_outer_copper, max_outer_copper)',
         'PCB Board Outer Copper must be unique per price list!')
    ]

    @api.multi
    def write(self, vals):
        if 'max_outer_copper' in vals or 'min_outer_copper' in vals:
            outer_copper_item = self.browse(self.ids[0])
            layer_item_id = outer_copper_item.layer_item_id.id
            old_min_outer_copper = outer_copper_item.min_outer_copper
            old_max_outer_copper = outer_copper_item.max_outer_copper
            if 'min_outer_copper' in vals:
                min_outer_copper = vals['min_outer_copper']
                if old_min_outer_copper != min_outer_copper:
                    self.env.cr.execute('UPDATE pcb_quotation_pricelist_layer_outer_copper SET max_outer_copper=%f WHERE layer_item_id=%s AND max_outer_copper=%f' % (
                                        min_outer_copper, layer_item_id, old_min_outer_copper))
            if 'max_outer_copper' in vals:
                max_outer_copper = vals['max_outer_copper']
                if old_max_outer_copper != max_outer_copper:
                    self.env.cr.execute('UPDATE pcb_quotation_pricelist_layer_outer_copper SET min_outer_copper=%f WHERE layer_item_id=%s AND min_outer_copper=%f' % (
                                        max_outer_copper, layer_item_id, old_max_outer_copper))
        return super(pcb_quotation_pricelist_layer_outer_copper, self).write(vals)


class pcb_quotation_pricelist_layer_inner_copper(models.Model):
    _name = "pcb.quotation.pricelist.layer.inner.copper"
    _description = "Price List of Inner Copper"
    _order = "layer_item_id,min_inner_copper, max_inner_copper"

    layer_item_id = fields.Many2one('pcb.quotation.pricelist.layer.item', 'Price List of Board Material', ondelete='cascade')
    min_inner_copper = fields.Float('Min Inner Copper', required=True, digits=dp.get_precision('size'), default=0.0)
    max_inner_copper = fields.Float('Max Inner Copper', required=True, digits=dp.get_precision('size'), default=0.0)
    add_fee_type = fields.Selection(AVAILABLE_PRICE_TYPE, 'Add Fee Type', required=True, default='item')
    add_fee = fields.Float('Add Fee', required=True, digits=dp.get_precision('Product Price'), default=0.0)

    def _check_inner_copper(self):
        obj_inner_copper = self.env['pcb.quotation.pricelist.layer.inner.copper'].browse(self.ids[0])
        if obj_inner_copper.min_inner_copper > obj_inner_copper.max_inner_copper:
            return False
        layer_item_id = obj_inner_copper.layer_item_id.id
        min_inner_copper = obj_inner_copper.min_inner_copper
        max_inner_copper = obj_inner_copper.max_inner_copper
        self.env.cr.execute('SELECT count(id) FROM pcb_quotation_pricelist_layer_inner_copper WHERE layer_item_id=%s AND max_inner_copper>%f AND min_inner_copper<%f AND id != %s' % (
                            layer_item_id, min_inner_copper, max_inner_copper, obj_inner_copper.id))
        eline_rows = self.env.cr.fetchone()[0] or 0.0
        if eline_rows:
            return False
        return True

    _constraints = [
        (_check_inner_copper, 'Error!\nThe row min inner copper and max inner copper overlap other rows.',
         ['min_inner_copper', 'max_inner_copper'])
    ]

    _sql_constraints = [
        ('layer_inner_copper_uniq', 'unique(layer_item_id, min_inner_copper, max_inner_copper)',
         'PCB Board Inner Copper must be unique per price list!')
    ]

    @api.multi
    def write(self, vals):
        if 'max_inner_copper' in vals or 'min_inner_copper' in vals:
            inner_copper_item = self.browse(self.ids[0])
            layer_item_id = inner_copper_item.layer_item_id.id
            old_min_inner_copper = inner_copper_item.min_inner_copper
            old_max_inner_copper = inner_copper_item.max_inner_copper
            if 'min_inner_copper' in vals:
                min_inner_copper = vals['min_inner_copper']
                if old_min_inner_copper != min_inner_copper:
                    self.env.cr.execute('UPDATE pcb_quotation_pricelist_layer_inner_copper SET max_inner_copper=%f WHERE layer_item_id=%s AND max_inner_copper=%f' % (
                                        min_inner_copper, layer_item_id, old_min_inner_copper))
            if 'max_inner_copper' in vals:
                max_inner_copper = vals['max_inner_copper']
                if old_max_inner_copper != max_inner_copper:
                    self.env.cr.execute('UPDATE pcb_quotation_pricelist_layer_inner_copper SET min_inner_copper=%f WHERE layer_item_id=%s AND min_inner_copper=%f' % (
                                        max_inner_copper, layer_item_id, old_max_inner_copper))
        return super(pcb_quotation_pricelist_layer_inner_copper, self).write(vals)


class pcb_quotation_pricelist_layer_size(models.Model):
    _name = "pcb.quotation.pricelist.layer.size"
    _description = "Price List of Board Size"
    _order = "layer_item_id, max_size"

    sequence = fields.Integer('Sequence', required=True,
                              help="Gives the order in which the pricelist size items will be checked. The evaluation gives highest priority to lowest sequence and stops as soon as a matching item is found.", default=lambda a: 5)
    layer_item_id = fields.Many2one('pcb.quotation.pricelist.layer.item', 'Price List of Board Material', ondelete='cascade')
    # 'name = fields.char('Size Name', size=64, help="Size name for this pricelist size line."),
    max_size = fields.Float('Max Size', required=True, digits=dp.get_precision('size'), default=0.0)
    volume_type = fields.Selection([('prototype', 'Prototype'),
                                    ('small', 'Small Volume'),
                                    ('medium', 'Medium Volume'),
                                    ('large', 'Large Volume'),
                                    ('larger', 'Larger Volume'),
                                    ], 'Volume Type')
    material_fee_type = fields.Selection(AVAILABLE_PRICE_TYPE, 'Material Fee Type', required=False, default='item')
    material_fee = fields.Float(string='Material Unit Price', required=False,
                                digits=dp.get_precision('Product Price'), default=0.0)
    engineering_fee_type = fields.Selection(AVAILABLE_PRICE_TYPE, 'Engineering Fee Type', required=True, default='item')
    engineering_fee = fields.Float('Engineering Fee', required=False,
                                   digits=dp.get_precision('Product Price'), default=0.0)
    etest_fee_type = fields.Selection(AVAILABLE_PRICE_TYPE, 'ETest Fee Type', required=False, default='item')
    etest_fee = fields.Float('ETest Fee', required=False, digits=dp.get_precision('Product Price'), default=0.0)
    film_fee_type = fields.Selection(AVAILABLE_PRICE_TYPE, 'Film Fee Type', required=False, default='item')
    film_fee = fields.Float('Film Fee', required=False, digits=dp.get_precision('Product Price'), default=0.0)
    min_delay_hours = fields.Integer('Min Delay Hours', required=False,
                                     help="This is the min delay in days between the sales order confirmation and the  reception of goods for this PCB and for the customer. It is used by the scheduler to order requests based on reordering delays.", default=24.0)
    max_delay_hours = fields.Integer('Max Delay Hours', required=False,
                                     help="This is the max delay in days between the sales order confirmation and the  reception of goods for this PCB and for the customer. It is used by the scheduler to order requests based on reordering delays.", default=0.0)
    quick_time = fields.Integer('Quick Time(H)', required=False, default=24)
    quick_fee = fields.Integer('Quick Fee(%)', required=False, default=10)
    type_item_ids = fields.One2many('pcb.quotation.pricelist.size.type', 'size_item_id',
                                    'Price List of Copper Base')

    _sql_constraints = [
        ('version_layer_size_uniq', 'unique(layer_item_id, max_size)',
         'Layer size must be unique for per partner in Price List of Board Size!'),
    ]


class pcb_quotation_pricelist_size_type(models.Model):
    _name = "pcb.quotation.pricelist.size.type"
    _description = "Price List of Copper Base"
    _order = "size_item_id, base_type"

    # 'name': fields.char('Size Name', size=64, help="Copper Base Type for this pricelist size line."),
    size_item_id = fields.Many2one('pcb.quotation.pricelist.layer.size', 'Price List of Board Size', ondelete='cascade')
    base_type = fields.Many2one('cam.base.type', 'Copper Base Tye', required=False, index=True)
    material_fee_type = fields.Selection(AVAILABLE_PRICE_TYPE, 'Material Fee Type', required=False, default='item')
    material_fee = fields.Float('Material Unit Price', required=False,
                                digits=dp.get_precision('Product Price'), default=0.0)
    engineering_fee_type = fields.Selection(AVAILABLE_PRICE_TYPE, 'Engineering Fee Type', required=False, default='item')
    engineering_fee = fields.Float('Engineering Fee', required=False,
                                   digits=dp.get_precision('Product Price'), default=0.0)
    etest_fee_type = fields.Selection(AVAILABLE_PRICE_TYPE, 'ETest Fee Type', required=False, default='item')
    etest_fee = fields.Float('ETest Fee', required=False, digits=dp.get_precision('Product Price'), default=0.0)
    film_fee_type = fields.Selection(AVAILABLE_PRICE_TYPE, 'Film Fee Type', required=False, default='item')
    film_fee = fields.Float('Film Fee', required=False, digits=dp.get_precision('Product Price'), default=0.0)
    min_delay_hours = fields.Integer('Min Delay Hours', required=False,
                                     help="This is the min delay in days between the sales order confirmation and the  reception of goods for this PCB and for the customer. It is used by the scheduler to order requests based on reordering delays.", default=24.0)
    max_delay_hours = fields.Integer('Max Delay Hours', required=False,
                                     help="This is the max delay in days between the sales order confirmation and the  reception of goods for this PCB and for the customer. It is used by the scheduler to order requests based on reordering delays.",default=0.0)
    quick_time = fields.Integer('Quick Time(H)', required=False, defaultl=24)  # 默认是24小时
    quick_fee = fields.Integer('Quick Fee(%)', required=False, default=10)

    _sql_constraints = [
        ('size_type_base_uniq', 'unique(size_item_id, base_type)',
         'Copper Base Tye must be unique in Price List of Copper Base for every verson of price list!'),
    ]


class pcb_quotation_pricelist_tooling(models.Model):
    _name = "pcb.quotation.pricelist.tooling"
    _description = "Price List of Test Tooling"
    _order = "price_version_id, min_test_points"

    # 'name': fields.char('Rule Name', size=64, help="Explicit rule name for this pricelist line."),
    price_version_id = fields.Many2one('pcb.quotation.pricelist.version', 'Price List Versions', required=True,
                                       index=True, ondelete='cascade')
    min_test_points = fields.Integer('Min Test Points', default=0.0)
    max_test_points = fields.Integer('Max Test Points', default=0.0)
    price_type = fields.Selection([('item', 'Item'),
                                   ('point', 'Point'), ], 'Price Type', required=True, default='item')
    price = fields.Float('Price', required=True, default=0.0, digits=(16, 5))

    def _check_test_points(self):
        obj_etest = self.env['pcb.quotation.pricelist.tooling'].browse(self.ids[0])
        if obj_etest.min_test_points > obj_etest.max_test_points:
            return False
        version_id = obj_etest.price_version_id.id
        min_point = obj_etest.min_test_points
        max_point = obj_etest.max_test_points
        self.env.cr.execute('SELECT count(id) FROM pcb_quotation_pricelist_tooling WHERE price_version_id=%s AND max_test_points>%f AND min_test_points<%f AND id != %s' % (
                            version_id, min_point, max_point, obj_etest.id))
        etest_rows = self.env.cr.fetchone()[0] or 0.0
        if etest_rows:
            return False
        return True

    _constraints = [
        (_check_test_points, 'Error!\nThe row test points overlap other rows.', ['min_test_points', 'max_test_points'])
    ]

    _sql_constraints = [
        ('version_points_uniq', 'unique(price_version_id, min_test_points, max_test_points)',
         'Min Test Points and Max Test Points must be unique per Price List verson!'),
    ]


class pcb_quotation_pricelist_etest(models.Model):
    _name = "pcb.quotation.pricelist.etest"
    _description = "Price List of ETest"
    _order = "price_version_id, min_test_points"

    # 'name': fields.char('Rule Name', size=64, help="Explicit rule name for this pricelist line."),
    price_version_id = fields.Many2one('pcb.quotation.pricelist.version', 'Price List Versions', required=True,
                                       index=True, ondelete='cascade')
    min_test_points = fields.Integer('Min Test Points', defaultl=0.0)
    max_test_points = fields.Integer('Max Test Points', defaultl=0.0)
    price_type = fields.Selection([('item', 'Item'),
                                   ('point', 'Point'), ], 'Price Type', required=True, defaultl='point')
    price = fields.Float('Price', required=True, defaultl=0.0)

    _sql_constraints = [
        ('version_points_uniq', 'unique(price_version_id, min_test_points, max_test_points)',
         'Min Test Points and Max Test Points must be unique per Price List verson!!'),
    ]

    def _check_test_points(self):
        obj_etest = self.env['pcb.quotation.pricelist.etest'].browse(self.ids[0])
        if obj_etest.min_test_points > obj_etest.max_test_points:
            return False
        version_id = obj_etest.price_version_id.id
        min_point = obj_etest.min_test_points
        max_point = obj_etest.max_test_points
        self.env.cr.execute('SELECT count(id) FROM pcb_quotation_pricelist_etest WHERE price_version_id=%s AND max_test_points>%f AND min_test_points<%f AND id != %s' % (
                            version_id, min_point, max_point, obj_etest.id))
        etest_rows = self.env.cr.fetchone()[0] or 0.0
        if etest_rows:
            return False
        return True

    _constraints = [
        (_check_test_points, 'Error!\nThe row test points overlap other rows.', ['min_test_points', 'max_test_points'])
    ]


class pcb_quotation_pricelist_other(models.Model):
    _name = "pcb.quotation.pricelist.other"
    _description = "Price List of Other Fee"
    _order = "price_version_id, min_size, max_size"

    # 'name': fields.char('Rule Name', size=64, help="Explicit rule name for this pricelist line."),
    price_version_id = fields.Many2one('pcb.quotation.pricelist.version', 'Price List Versions', required=True,
                                       index=True, ondelete='cascade')
    min_size = fields.Float('Min Size', required=True, digits=dp.get_precision('size'), default=0.0)
    max_size = fields.Float('Max Size', required=True, digits=dp.get_precision('size'), default=0.0)
    other_line_ids = fields.One2many('pcb.quotation.pricelist.other.line', 'price_other_fee_id',
                                     'Price List of Line cpo_width and Distance')
    other_hole_ids = fields.One2many('pcb.quotation.pricelist.other.hole', 'price_other_fee_id',
                                     'Price List of Hole Density')

    def _check_size(self):
        obj_other = self.env['pcb.quotation.pricelist.other'].browse(self.ids[0])
        if obj_other.min_size > obj_other.max_size:
            return False
        version_id = obj_other.price_version_id.id
        min_size = obj_other.min_size
        max_size = obj_other.max_size
        self.env.cr.execute('SELECT count(id) FROM pcb_quotation_pricelist_other WHERE price_version_id=%s AND max_size>%f AND min_size<%f AND id != %s' % (
                            version_id, min_size, max_size, obj_other.id))
        eline_rows = self.env.cr.fetchone()[0] or 0.0
        if eline_rows:
            return False
        return True

    _constraints = [
        (_check_size, 'Error!\nThe row other fee size overlap other rows.', ['min_size', 'max_size'])
    ]
    _sql_constraints = [
        ('version_other_fee_uniq', 'unique(price_version_id, min_size, max_size)',
         'min size and max size of the Other fee must be unique per Price List verson!!'),
    ]


class pcb_quotation_pricelist_other_line(models.Model):
    _name = "pcb.quotation.pricelist.other.line"
    _description = "Price List of Line cpo_width and Distance"
    _order = "price_other_fee_id, min_line_cpo_width, max_line_cpo_width"

    price_other_fee_id = fields.Many2one('pcb.quotation.pricelist.other', 'Other Fee of Price List', required=True,
                                         index=True, ondelete='cascade')
    min_line_cpo_width = fields.Float('Min Line cpo_Width and Distance', required=True,
                                  digits=dp.get_precision('size'), default=0.0)
    max_line_cpo_width = fields.Float('Max Line cpo_Width and Distance', required=True,
                                  digits=dp.get_precision('size'), default=0.0)
    price_type = fields.Selection(AVAILABLE_PRICE_TYPE, 'Price Type', required=True, default='item')
    price = fields.Float('Price', required=True, digits=dp.get_precision('Product Price'), default=0.0)
    price_class = fields.Selection([('l', 'L'), ('%', '%')], 'Price Class', default='l')

    def _check_line_cpo_width(self):
        obj_line = self.env['pcb.quotation.pricelist.other.line'].browse(self.ids[0])
        if obj_line.min_line_cpo_width > obj_line.max_line_cpo_width:
            return False
        other_fee_id = obj_line.price_other_fee_id.id
        min_line_cpo_width = obj_line.min_line_cpo_width
        max_line_cpo_width = obj_line.max_line_cpo_width
        self.env.cr.execute('SELECT count(id) FROM pcb_quotation_pricelist_other_line WHERE price_other_fee_id=%s AND max_line_cpo_width>%f AND max_line_cpo_width<%f AND id != %s' % (
                            other_fee_id, min_line_cpo_width, max_line_cpo_width, obj_line.id))
        eline_rows = self.env.cr.fetchone()[0] or 0.0
        if eline_rows:
            return False
        return True

    _constraints = [
        (_check_line_cpo_width, 'Error!\nThe row Line cpo_width and distance overlap other rows.',
         ['min_line_cpo_width', 'max_line_cpo_width'])
    ]
    _sql_constraints = [
        ('price_other_line_uniq', 'unique(price_other_fee_id, min_line_cpo_width, max_line_cpo_width)',
         'Min Line cpo_Width and Max Line cpo_Width must be unique per Price List verson!!'),
    ]


class pcb_quotation_pricelist_other_hole(models.Model):
    _name = "pcb.quotation.pricelist.other.hole"
    _description = "Price List of Hole Density"
    _order = "price_other_fee_id, min_hole, max_hole"

    price_other_fee_id = fields.Many2one('pcb.quotation.pricelist.other', 'Other Fee of Price List', required=True,
                                         index=True, ondelete='cascade')
    min_hole = fields.Float('Min Hole', required=True, digits=dp.get_precision('size'), default=0.0)
    max_hole = fields.Float('Max Hole', required=True, digits=dp.get_precision('size'), default=0.0)
    price_type = fields.Selection(AVAILABLE_PRICE_TYPE, 'Price Type', required=True, default='item')
    price = fields.Float('Price', required=True, digits=dp.get_precision('Product Price'), default=0.0)
    price_class = fields.Selection([('l', 'L'), ('%', '%')], 'Price Class', default='l')

    def _check_hole_size(self):
        obj_hole = self.env['pcb.quotation.pricelist.other.hole'].browse(self.ids[0])
        if obj_hole.min_hole > obj_hole.max_hole:
            return False
        other_fee_id = obj_hole.price_other_fee_id.id
        min_hole = obj_hole.min_hole
        max_hole = obj_hole.max_hole
        self.env.cr.execute('SELECT count(id) FROM pcb_quotation_pricelist_other_hole WHERE price_other_fee_id=%s AND max_hole>%f AND min_hole<%f AND id != %s' % (
                            other_fee_id, min_hole, max_hole, obj_hole.id))
        eline_rows = self.env.cr.fetchone()[0] or 0.0
        if eline_rows:
            return False
        return True

    _constraints = [
        (_check_hole_size, 'Error!\nThe row min hole and max hole overlap other rows.', ['min_hole', 'max_hole'])
    ]
    _sql_constraints = [
        ('price_other_hole_uniq', 'unique(price_other_fee_id, min_hole, max_hole)',
         'Min Hole and Max Hole must be unique per Price List verson!!'),
    ]
