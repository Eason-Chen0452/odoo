# -*- coding: utf-8 -*-
import logging
from odoo import api, models, fields, tools, _
from odoo.http import request
from odoo.exceptions import UserError, ValidationError
from  decimal import Decimal
from  decimal import getcontext
import re
from odoo.addons.cpo_offer_base.models.cpo_offer_bom import get_digi_data

ELECTRON_FILE_TYPE = [
            {'id': '1','text': 'BOM File'},
            {'id': '2','text': 'SMT File'},
            {'id': '3','text': 'Gerber File'},
        ]

PCB_ELECTRON_FILE_TYPE = [
            {'id': '1','text': 'Gerber File'},
        ]

PCBA_ELECTRON_FILE_TYPE = [
            {'id': '1','text': 'BOM File'},
            {'id': '2','text': 'SMT File'},
            {'id': '3','text': 'Gerber File'},
        ]

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = "sale.order"

    express_order = fields.One2many('sale_order.express_waybill', 'order_number', string="Express Order")
    cpo_customer_id = fields.Integer(string='Customer Id')
    cpo_lock_bool = fields.Boolean(string='Customer Id', default=False)
    express_bool = fields.Boolean('Express Order', compute='_depends_express_order', store=True)
    po_number = fields.Char(string="PO Nunber")
    part_no = fields.Char(string="Part No.")

    @api.depends('express_bool')
    def _depends_express_order(self):
        for x_id in self:
            if x_id.express_order:
                x_id.express_bool = True

    @api.multi
    def _website_product_id_change(self, order_id, product_id, qty=0):
        order = self.sudo().browse(order_id)
        product_context = dict(self.env.context)
        product_context.setdefault('lang', order.partner_id.lang)
        product_context.update({
            'partner': order.partner_id.id,
            'quantity': qty,
            'date': order.date_order,
            'pricelist': order.pricelist_id.id,
        })
        product = self.env['product.product'].with_context(product_context).browse(product_id)
        pu = product.price
        if order.pricelist_id and order.partner_id:
            order_line = order._cart_find_product_line(product.id)
            if order_line:
                pu = self.env['account.tax']._fix_tax_included_price_company(pu, product.taxes_id, order_line[0].tax_id, self.company_id)

        return {
            'product_id': product_id,
            'product_uom_qty': qty,
            'order_id': order_id,
            'product_uom': product.uom_id.id,
            'price_unit': pu,
        }

    @api.multi
    def _cart_find_product_line(self, product_id=None, line_id=None, **kwargs):
        self.ensure_one()
        product = self.env['product.product'].browse(product_id)

        # split lines with the same product if it has untracked attributes
        if product and product.mapped('attribute_line_ids').filtered(lambda r: not r.attribute_id.create_variant) and not line_id:
            return self.env['sale.order.line']

        order_ids = request.session.get('sale_order_ids')
        domain = [('order_id', 'in', order_ids), ('product_id', '=', product_id)]
        if line_id:
            domain += [('id', '=', line_id)]
        else:
            return self.env['sale.order.line']
        return self.env['sale.order.line'].sudo().search(domain)

    @api.model
    def set_update_seq_prefix(self):
        sequence_obj = self.env['ir.sequence'].search([('code', '=', 'sale.order')])
        sequence_obj.write({'prefix': 'SO%(y)s%(month)s%(day)s'})

    @api.multi
    def _cart_update(self, product_id=None, line_id=None, add_qty=0, set_qty=0, attributes=None, **kwargs):
        """ Add or set product quantity, add_qty can be negative """
        self.ensure_one()
        SaleOrderLineSudo = self.env['sale.order.line'].sudo()

        try:
            if add_qty:
                add_qty = float(add_qty)
        except ValueError:
            add_qty = 1
        try:
            if set_qty:
                set_qty = float(set_qty)
        except ValueError:
            set_qty = 0
        quantity = 0
        order_line = False
        if self.state != 'draft':
            request.session['sale_order_id'] = None
            raise UserError(_('It is forbidden to modify a sales order which is not in draft status'))
        if line_id is not False:
            order_lines = self._cart_find_product_line(product_id, line_id, **kwargs)
            order_line = order_lines and order_lines[0]

        # Create line if no line with product_id can be located
        if not order_line:
            set_smt = kwargs.get('set_smt')
            set_pcb_awh = kwargs.get('set_pcb_awh')
            set_bw = kwargs.get('set_bw')
            set_sided = kwargs.get('set_sided')
            set_length = kwargs.get('set_length')
            set_breadth = kwargs.get('set_breadth')
            set_text = kwargs.get('set_text')
            cpo_bom_supply = kwargs.get('cpo_bom_supply')
            cpo_pcb_supply = kwargs.get('cpo_pcb_supply')
            set_pcb_thickness = kwargs.get('set_pcb_thickness')
            set_pcb_copper = kwargs.get('set_pcb_copper')
            set_pcb_special = kwargs.get('set_pcb_special')
            bom_id = kwargs.get('bom_id')


            values = self._website_product_id_change(self.id, product_id, qty=1)
            values['name'] = self._get_line_description(self.id, product_id, attributes=attributes)
            # values['bom_material_type'] = int(set_bom) if set_bom else 0
            values['smt_component_qty'] = get_digi_data(set_smt) if set_smt else 0
            # values['smt_ic_qty'] = int(set_ic) if set_ic else 0
            # values['backhand_welding_qty'] = int(set_bw) if set_bw else 0
            values['smt_plug_qty'] = get_digi_data(set_pcb_awh) if set_pcb_awh else 0
            values['layer_pcb'] = get_digi_data(set_sided) if set_sided else 0
            values['pcb_length'] = get_digi_data(set_length, float) if set_length else 0
            values['pcb_width'] = get_digi_data(set_breadth, float) if set_breadth else 0
            values['pcb_thickness'] = get_digi_data(set_pcb_thickness, float) if set_pcb_thickness else 0
            values['copper_foil'] = get_digi_data(set_pcb_copper, float) if set_pcb_copper else 0
            values['cpo_note'] = set_text
            values['pcb_special'] = set_pcb_special
            if bom_id:
                bom_sudo = self.env['cpo_offer_bom.bom'].sudo()
                bom_obj = bom_sudo.search([('id', '=', bom_id)])
                values['bom_rootfile'] = bom_obj.id
            # values['smt_plug_backhand_welding_qty'] = int(set_bom) if set_bom else 0

            order_line = SaleOrderLineSudo.create(values)
            if bom_id:
                atta_sudo = self.env['ir.attachment'].sudo()
                atta_row = atta_sudo.search([('res_id', '=', bom_obj.id), ('res_model', '=', 'cpo_offer_bom.bom'), ('description', '=', 'BOM File')])
                if atta_row:
                    atta_sudo.create({
                        'name':atta_row.name,
                        'description':'BOM File',
                        'res_model':'sale.order',
                        'type': 'binary',
                        'public': True,
                        'datas':atta_row.datas,
                        'res_id':order_line.order_id.id,
                        'datas_fname':atta_row.name,
                    })
            order_line.order_id.bom_supply = cpo_bom_supply
            order_line.order_id.pcb_supply = cpo_pcb_supply

            try:
                order_line._compute_tax_id()
            except ValidationError as e:
                # The validation may occur in backend (eg: taxcloud) but should fail silently in frontend
                _logger.debug("ValidationError occurs during tax compute. %s" % (e))
            if add_qty:
                add_qty -= 1

        # compute new quantity
        if set_qty:
            quantity = set_qty
        elif add_qty is not None:
            quantity = order_line.product_uom_qty + (add_qty or 0)

        # Remove zero of negative lines
        if quantity <= 0:
            old_order_id = order_line.order_id.id
            order_line.unlink()
            #order_line.order_id.unlink()
            request.session['sale_order_ids'] = list(set(request.session['sale_order_ids']) - set([old_order_id]))
        else:
            # update line
            values = self._website_product_id_change(self.id, product_id, qty=quantity)
            values.pop('order_id')
            if self.pricelist_id.discount_policy == 'with_discount' and not self.env.context.get('fixed_price'):
                order = self.sudo().browse(self.id)
                product_context = dict(self.env.context)
                product_context.setdefault('lang', order.partner_id.lang)
                product_context.update({
                    'partner': order.partner_id.id,
                    'quantity': quantity,
                    'date': order.date_order,
                    'pricelist': order.pricelist_id.id,
                })
                product = self.env['product.product'].with_context(product_context).browse(product_id)
                values['price_unit'] = self.env['account.tax']._fix_tax_included_price_company(
                    order_line._get_display_price(product),
                    order_line.product_id.taxes_id,
                    order_line.tax_id,
                    self.company_id
                )
            order_line.write(values)

        return {'line_id': order_line.id, 'quantity': quantity}

    @api.model
    def get_all_att_list(self):
        atta = self.env['ir.attachment']
        att_ids = atta.search([('res_model', '=', 'sale.order'), ('res_id', '=', self.id),('description', 'in', ('BOM File', 'SMT File', 'Gerber File'))])
        return att_ids

    @api.model
    def get_electron_atta_type(self):
        return ELECTRON_FILE_TYPE

    @api.multi
    def check_cart_quantity(self):
        return sum(self.mapped("cart_quantity"))

    @api.multi
    def cpo_clear_checkout_session(self):
        for order in self:
            checkout_order_ids = request.session['checkout_order_ids']
            sale_order_ids = request.session['sale_order_ids']
            if order.id in checkout_order_ids:
                order.order_line.write({'cpo_checked': 'false'})
                request.session['checkout_order_ids'] = list(set([x for x in checkout_order_ids if x in sale_order_ids]) - set([order.id]))
            if order.id in sale_order_ids:
                request.session['sale_order_ids'] = list(set(sale_order_ids) - set([order.id]))
            if request.env.user.partner_id.id not in order.message_partner_ids.ids:
                order.message_subscribe([request.env.user.partner_id.id])
        if not request.session.get('sale_order_ids'):
            request.session['sale_order_id'] = False
        return True


class Website(models.Model):
    _inherit = 'website'

    @api.multi
    def sale_get_checked_order(self, **post):
        order_ids = request.session.get('sale_order_ids')
        return self.env['sale.order'].sudo().search([('id', 'in', order_ids)]).filtered(lambda x:x.order_line.filtered(lambda y:y.cpo_checked=='true'))

    @api.multi
    def sale_get_checkout_order(self, **post):
        order_ids = request.session.get('checkout_order_ids')
        return self.env['sale.order'].sudo().search([('id', 'in', order_ids)]).filtered(lambda x:x.order_line.filtered(lambda y:y.cpo_checked=='true'))

    @api.multi
    def old_sale_get_order(self, force_create=False, code=None, update_pricelist=False, force_pricelist=False):
        self.ensure_one()
        partner = self.env.user.partner_id
        if request.session.get('sale_order_ids'):
            sale_order_id = request.session['sale_order_ids'][-1]
        else:
            sale_order_id = request.session.get('sale_order_id')
        request.session['sale_order_id'] = sale_order_id
        sale_order_id = False
        if not sale_order_id:
            last_order = partner.last_website_so_id
            available_pricelists = self.get_pricelist_available()
            # Do not reload the cart of this user last visit if the cart is no longer draft or uses a pricelist no longer available.
            sale_order_id = last_order.state == 'draft' and last_order.pricelist_id in available_pricelists and last_order.id

        pricelist_id = request.session.get('website_sale_current_pl') or self.get_current_pricelist().id

        if self.env['product.pricelist'].browse(force_pricelist).exists():
            pricelist_id = force_pricelist
            request.session['website_sale_current_pl'] = pricelist_id
            update_pricelist = True

        if not self._context.get('pricelist'):
            self = self.with_context(pricelist=pricelist_id)

        # Test validity of the sale_order_id
        sale_order = False#self.env['sale.order'].sudo().browse(sale_order_id).exists() if sale_order_id else None

        # create so if needed
        if not sale_order and (force_create or code):
            # TODO cache partner_id session
            pricelist = self.env['product.pricelist'].browse(pricelist_id).sudo()
            so_data = self._prepare_sale_order_values(partner, pricelist)
            sale_order = self.env['sale.order'].sudo().create(so_data)

            # set fiscal position
            if request.website.partner_id.id != partner.id:
                sale_order.onchange_partner_shipping_id()
            else: # For public user, fiscal position based on geolocation
                country_code = request.session['geoip'].get('country_code')
                if country_code:
                    country_id = request.env['res.country'].search([('code', '=', country_code)], limit=1).id
                    fp_id = request.env['account.fiscal.position'].sudo()._get_fpos_by_region(country_id)
                    sale_order.fiscal_position_id = fp_id
                else:
                    # if no geolocation, use the public user fp
                    sale_order.onchange_partner_shipping_id()

            request.session['sale_order_id'] = sale_order.id

            if request.website.partner_id.id != partner.id:
                partner.write({'last_website_so_id': sale_order.id})

        if sale_order:
            # case when user emptied the cart
            if not request.session.get('sale_order_id'):
                request.session['sale_order_id'] = sale_order.id

            # check for change of pricelist with a coupon
            pricelist_id = pricelist_id or partner.property_product_pricelist.id

            # check for change of partner_id ie after signup
            if sale_order.partner_id.id != partner.id and request.website.partner_id.id != partner.id:
                flag_pricelist = False
                if pricelist_id != sale_order.pricelist_id.id:
                    flag_pricelist = True
                fiscal_position = sale_order.fiscal_position_id.id

                # change the partner, and trigger the onchange
                sale_order.write({'partner_id': partner.id})
                sale_order.onchange_partner_id()
                sale_order.onchange_partner_shipping_id() # fiscal position
                sale_order['payment_term_id'] = self.sale_get_payment_term(partner)

                # check the pricelist : update it if the pricelist is not the 'forced' one
                values = {}
                if sale_order.pricelist_id:
                    if sale_order.pricelist_id.id != pricelist_id:
                        values['pricelist_id'] = pricelist_id
                        update_pricelist = True

                # if fiscal position, update the order lines taxes
                if sale_order.fiscal_position_id:
                    sale_order._compute_tax_id()

                # if values, then make the SO update
                if values:
                    sale_order.write(values)

                # check if the fiscal position has changed with the partner_id update
                recent_fiscal_position = sale_order.fiscal_position_id.id
                if flag_pricelist or recent_fiscal_position != fiscal_position:
                    update_pricelist = True

            if code and code != sale_order.pricelist_id.code:
                code_pricelist = self.env['product.pricelist'].sudo().search([('code', '=', code)], limit=1)
                if code_pricelist:
                    pricelist_id = code_pricelist.id
                    update_pricelist = True
            elif code is not None and sale_order.pricelist_id.code:
                # code is not None when user removes code and click on "Apply"
                pricelist_id = partner.property_product_pricelist.id
                update_pricelist = True

            # update the pricelist
            if update_pricelist:
                request.session['website_sale_current_pl'] = pricelist_id
                values = {'pricelist_id': pricelist_id}
                sale_order.write(values)
                for line in sale_order.order_line:
                    if line.exists():
                        sale_order._cart_update(product_id=line.product_id.id, line_id=line.id, add_qty=0)

        else:
            request.session['sale_order_id'] = None
            return self.env['sale.order']

        return sale_order

    @api.multi
    def sale_get_order(self, force_create=False, code=None, update_pricelist=False, force_pricelist=False, **post):
        """ Return the current sales order after mofications specified by params.
        :param bool force_create: Create sales order if not already existing
        :param str code: Code to force a pricelist (promo code)
                         If empty, it's a special case to reset the pricelist with the first available else the default.
        :param bool update_pricelist: Force to recompute all the lines from sales order to adapt the price with the current pricelist.
        :param int force_pricelist: pricelist_id - if set,  we change the pricelist with this one
        :returns: browse record for the current sales order
        """
        #if post.get('create_order'):
            #request.session['sale_order_id'] = None
            #request.session['sale_order_id'] = request.session['sale_order_ids'][-1]
            #self.env.user.last_website_so_id = None
        #sale_order = request.env['sale.order'].search([('id', '=', request.session['sale_order_id'])])
        sale_order = self.old_sale_get_order(
            force_create=force_create,
            code=code,
            update_pricelist=update_pricelist,
            force_pricelist=force_pricelist
            )

        if sale_order:
            #init sale_order_ids
            sale_order_id = request.session.get('sale_order_id')
            if request.session.get('sale_order_ids'):
                sale_order_ids = request.session.get('sale_order_ids')
            elif sale_order_id:
                sale_order_ids = [sale_order.id]

            #update sale_order_ids
            if sale_order_id not in sale_order_ids:# and request.session['sale_last_order_id'] != request.session['sale_order_id']:
                sale_order_ids.append(sale_order_id)
            order_pool = request.env['sale.order'].sudo()
            checked_ids = order_pool.search([('id', 'in', sale_order_ids), ('state', '=', 'draft')]).mapped("id")
            if checked_ids != sale_order_ids:
                request.session['sale_order_ids'] = checked_ids
            else:
                last_order = [request.session.get('sale_last_order_id')]
                sale_order_ids = list(set(sale_order_ids) - set(last_order))
                request.session['sale_order_ids'] = sale_order_ids
        return sale_order

    @api.multi
    def sale_get_order_ids(self):
        order_ids = request.session.get('sale_order_ids')
        order_pool = request.env['sale.order'].sudo()
        # order_db = order_pool.browse(order_ids)
        if order_ids:
            order_db = order_pool.search([('id', 'in', order_ids)])
            order_db = order_db.filtered(lambda sale_id: not sale_id.cpo_customer_id)
            if order_db and request.session.get('login'):
                order_db.update_cpo_customer_id(x_uid=request.session.get('uid'))
        session_ids = request.session
        if not order_ids:
            order_ids = order_pool.search([
                ('cpo_customer_id', '=', request.env.uid),
                ('state', '=', 'draft'),
            ])
            # 设置 session
            session_ids['sale_order_ids'] = order_ids.ids
            return order_ids
        # 和上面的order_ids合并
        id_list = order_pool.search([
            ('cpo_customer_id', '=', request.env.uid),
            ('state', '=', 'draft'),
            ('id', 'not in', order_ids)
        ])
        order_id = order_pool.search([('id','in',order_ids)])
        order_ids = id_list+order_id
        #设置 session
        session_ids['sale_order_ids'] = order_ids.ids
        return order_ids

    @api.multi
    def sale_get_checkout_order_ids(self):
        order_ids = request.session.get('checkout_order_ids')
        if not order_ids:
            return []
        order_pool = request.env['sale.order'].sudo()
        order_ids = order_pool.search([('id','in',order_ids)])
        return order_ids

    def sale_reset(self):
        request.session.update({
            'sale_order_id': False,
            'sale_transaction_id': False,
            'website_sale_current_pl': False,
            'sale_order_ids': False,
            'checkout_order_ids': False,
        })

    @api.multi
    def cpo_login_and_signup_coupon(self):
        # 增加优惠显示
        cpo_coupon = request.env['preferential.cpo_time_and_money'].sudo()
        coupon_obj = cpo_coupon.GetWebRegistered()
        return coupon_obj

class Express_waybill(models.Model):
    _name = 'sale_order.express_waybill'

    order_number = fields.Many2one('sale.order', string="Order Number", required=True, ondelete='cascade', index=True, copy=False)
    express_provider = fields.Char(string="Express Provider")
    express_number = fields.Char(string="Express Number")

    _sql_constraints = [
        ('express_number_unique',
         'UNIQUE(express_number)',
         "The express number must be unique"),
    ]
