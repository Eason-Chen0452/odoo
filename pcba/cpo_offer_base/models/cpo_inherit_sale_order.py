# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo import _
import xlrd
import xlwt
import base64,time
BOM_SELECTION_STATE = [('draft', 'Draft'),('check', 'Checking'),('complete', 'Complete')]
CPO_BOM_SUPPLY_SELECT = [
    ('chinapcbone', 'ChinaPCBOne'),
    ('customer', 'Customer'),
    ('part-customer', 'Part-Customer')
]
CPO_PCB_SUPPLY_SELECT = [
    ('chinapcbone', 'ChinaPCBOne'),
    ('customer', 'Customer'),
]

JUDGE_SECLECTION = [('true_t', 'True'), ('false_f', 'False')]

CHECK_BOM_SELECTION = [('check_on', 'Checked'),
                       ('check_off', 'No Checked')]


class SaleOrder(models.Model):
    _name = 'sale.order'
    _inherit = 'sale.order'

    @api.depends('order_line.price_total', 'first_order_partner')
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        # self.freight_function_transfer()
        for order in self:
            amount_untaxed = amount_tax = 0.0
            discount = 0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
            if order.first_order_partner:
                discount_rule = self.env['cpo_smt_price.smt'].search([('type_selection', '=', 'discount')])
                discount = order.pricelist_id.currency_id.round(amount_untaxed * discount_rule.price)
            amount_untaxed += order.shipping_fee
            order.update({
                'amount_untaxed': order.pricelist_id.currency_id.round(amount_untaxed),
                'amount_tax': order.pricelist_id.currency_id.round(amount_tax),
                'amount_total': amount_untaxed + amount_tax - discount,
                'discount_total': discount,
            })

    bom_supply_line = fields.One2many('cpo_bom_supply.list', 'order_id', string="BOM Supply")
    bom_fields_line = fields.One2many("cpo_bom_fields.line", 'order_id', string="BOM Fields Ref")
    bom_data_line = fields.One2many('cpo_bom_data.line', 'order_id', string="Client Data Abnormal")
    supply_bool = fields.Boolean('BOM Supply', compute='_show_content', store=True)
    fields_bool = fields.Boolean('BOM Fields Ref', compute='_show_content', store=True)
    data_bool = fields.Boolean('Client Data Abnormal', compute='_show_content', store=True)
    bom_supply = fields.Selection(CPO_BOM_SUPPLY_SELECT, string='Bom Supply')
    bom_state = fields.Selection(BOM_SELECTION_STATE, string="Bom State")
    pcb_supply = fields.Selection(CPO_PCB_SUPPLY_SELECT, string="PCB Supply")
    express_provider = fields.Char(string="Express Service Provider")
    express_number = fields.Char(string="Express Number")
    pcb_spec = fields.Char(string="PCB Spec")
    pcb_cost = fields.Char(string="PCB Cost")

    judge_state = fields.Selection(JUDGE_SECLECTION, default="false_f", realonly=True)
    check_state = fields.Selection(CHECK_BOM_SELECTION, default="check_off", string="Check BOM")

    shipping_fee = fields.Float(string="Shipping fee")
    first_order_partner = fields.Boolean(string="First Order Partner")

    discount_total = fields.Float(string="Discount Total", store=True, readonly=True, compute='_amount_all', track_visibility='always')

    state = fields.Selection([
        ('draft', 'Quotation'),
        ('wait_confirm', 'Wait Confirm'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
        ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')

    @api.depends('bom_supply_line', 'bom_fields_line', 'bom_data_line')
    def _show_content(self):
        for x_id in self:
            if x_id.bom_supply_line:
                x_id.supply_bool = True
            if x_id.bom_fields_line:
                x_id.fields_bool = True
            if x_id.bom_data_line:
                x_id.data_bool = True

    #@api.onchange('first_order_partner')
    #def _onchange_first_order_partner(self):
    #    for row in self:
    #        pcba = row.order_line.filtered(lambda x:x.name=='PCBA')
    #        pcba._compute_amount()
    #    return
    # @api.multi
    # def freight_function_transfer(self):
    #     return

    @api.model
    def create(self, vals):
        old_ids = self.search([], order='id desc', limit=1)
        if old_ids:
            old_seq_date = old_ids.name[2:8]
            cu_date = time.strftime('%y%m%d',time.localtime())
            if old_seq_date != cu_date:
                self.env.ref('sale.seq_sale_order').sudo().number_next_actual = 1
        else:
            self.env.ref('sale.seq_sale_order').sudo().number_next_actual = 1
        return super(SaleOrder, self).create(vals)

    def get_bom_file_name_datas(self):
        cpo_bom_file = self.env['ir.attachment'].search([('res_id', '=', self.id),('res_model', '=', 'sale.order'),('description', '=', 'BOM File')])
        if not cpo_bom_file:
            return False
        bom_file_data = base64.b64encode(cpo_bom_file.datas)
        name = cpo_bom_file.name
        if name and name[-4:].lower() == '.xls':
            bom_file_name = name[:-4]
        elif name and name[-5:].lower() == '.xlsx':
            bom_file_name = name[:-5]
        else:
            bom_file_name = name
        return {'bom_file_name':bom_file_name, 'bom_datas':bom_file_data, 'bom_atta_obj':cpo_bom_file}

    def create_new_bom_for_saleorder(self, partner_id):
        atta_pool = self.env['ir.attachment']
        bom_row = self.env['cpo_offer_bom.bom'].create({'partner_id':partner_id})
        order_pcba_line = self.order_line.only_pcba_order_line()
        bom_file_name_bom_datas = self.get_bom_file_name_datas()
        bom_atta_obj = bom_file_name_bom_datas.get('bom_atta_obj')
        order_pcba_line.bom_rootfile.unlink()
        order_pcba_line.write({
            'bom_rootfile':bom_row.id,
            'bom_file_name':bom_file_name_bom_datas.get('bom_file_name'),
        })
        bom_row.write({
            'bom_file_name':bom_file_name_bom_datas.get('bom_file_name'),
            'bom_file':base64.decodestring(bom_file_name_bom_datas.get('bom_datas')),
            'pcs_number': order_pcba_line.product_uom_qty,
        })
        atta_obj = atta_pool.create({
            'description': 'BOM File',
            'name':bom_atta_obj.name,
            'type': 'binary',
            'public': True,
            'res_id': bom_row.id,
            'res_model': 'cpo_offer_bom.bom',
            'datas':bom_atta_obj.datas,
            'datas_fname':bom_atta_obj.name,
        })
        return {'bom_obj':bom_row, 'atta_obj':atta_obj}

    def bom_order_line(self):
        product_bom = self.env['product.product'].search([('name', '=', 'BOM')])
        cpo_bom_file = self.env['ir.attachment'].search([('res_id', '=', self.id),('description', '=', 'BOM File')])
        if cpo_bom_file :
            bom_file_data = base64.b64encode(cpo_bom_file.datas)
            root_bom_file = self.env['cpo_offer_bom.bom'].search([('bom_file', '=', bom_file_data)])
            self.env['sale.order.line'].search([('order_id', '=', self.id)]).update({'bom_rootfile' : root_bom_file.id})
        return True

    @api.model
    def get_usd_currency_rate(self):
        rate_pool = self.env['res.currency.rate']
        usd_currency = self.env.ref("base.USD")
        res = rate_pool.search([('currency_id', '=', usd_currency.id)])[0]
        return res


    def analyze_bom(self):
        ctx = {}
        for row in self :
            cpo_bom_file = self.env['ir.attachment'].search([('res_id', '=', row.id),('res_model', '=', 'sale.order'),('description', '=', 'BOM File')])
            if not cpo_bom_file:
                return False
            bom_file_data = base64.b64encode(cpo_bom_file.datas)
            for l_row in row.order_line.only_pcba_order_line():
                #bom_vals = {'bom_file': cpo_bom_file.datas}
                name = cpo_bom_file.name
                if name and name[-4:].lower() == '.xls':
                    bom_file_name = name[:-4]
                elif name and name[-5:].lower() == '.xlsx':
                    bom_file_name = name[:-5]
                else:
                    bom_file_name = name
                    bom_vals = {'bom_file_name':bom_file_name}
                if l_row.bom_rootfile:
                    if l_row.bom_rootfile.state != 'draft':
                        raise ValidationError(_("BOM State checking,Please Waite,state is {state}.".format(state=l_row.bom_rootfile.state)))
                    l_row.bom_rootfile.write(bom_vals)
                else:
                    bom_id = l_row.bom_rootfile.create(bom_vals)
                    l_row.bom_rootfile = bom_id
                ctx = {
                    'default_model': 'cpo_offer_bom.bom',
                    'default_res_id': l_row.bom_rootfile.id,
                }
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'cpo_bom_wizard.wizard',
            'target': 'new',
            'context': ctx,
        }

    @api.multi
    def action_confirm(self):
        self.check_bom_file_state()
        res = super(SaleOrder, self).action_confirm()
        return res

    @api.multi
    def check_bom_file_state(self):
        for row in self:
            ob = row.order_line.only_pcba_order_line()
            if ob.bom_rootfile and ob.bom_rootfile.state != 'complete' :
                raise ValidationError(_("BOM not is done,please Click analyze bom button! state is : "+ob.bom_rootfile.state))
        return True

    @api.multi
    def cpo_pcba_sync_po_to_quo(self):
        atta = self.env['ir.attachment']
        for order in self:
            order.quotation_line.customer_file_name = atta.cpo_get_customer_file_name(order.id)
        return True

    @api.multi
    def unlink(self):
        for row in self:
            for ob in row.order_line :
                ob.bom_rootfile.unlink()
        res = super(SaleOrder, self).unlink()
        return res

    @api.multi
    def calculate_price(self):
        self.check_bom_file_state()
        self.order_line.smt_price()
        return True

    #@api.multi
    #def do_await(self):
    #    if self.state == "draft" or self.state == "sent" :
    #        self.state = "await"
    #    else :
    #        raise ValidationError(_("State has changed !"))
    #    return True

    @api.multi
    def act_wait_confirm(self):
        if self.state == "draft" or self.state == "sent" :
            self.state = "wait_confirm"

    @api.multi
    def print_quotation(self):
        self.check_bom_file_state()
        return super(SaleOrder, self).print_quotation()

    @api.multi
    def action_quotation_send(self):
        '''
        This function opens a window to compose an email, with the edi sale template message loaded by default
        '''
        self.ensure_one()
        self.check_bom_file_state()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('sale', 'email_template_edi_sale')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        IrMailServer = self.env['ir.mail_server'].sudo()
        mail_smtp_user = self.env.user.email
        #mail_server_cpo_id = IrMailServer.search([('smtp_user', '=', mail_smtp_user)])
        mail_server_cpo_id = IrMailServer.search([('smtp_user', '!=', False)], limit=1)
        ctx = {
            'default_model': 'sale.order',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            #'default_composition_mode': 'comment',
            'default_composition_mode': 'mass_mail',
            #'default_email_from': '{name}<{email}>'.format(name=self.env.user.name,email=self.env.user.email),
            'default_mail_server_id': mail_server_cpo_id.id,
            'mark_so_as_sent': True,
            'custom_layout': "sale.mail_template_data_notification_email_sale_order",
            'proforma': self.env.context.get('proforma', False)
        }
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    def create_atta_for_saleorder(self, order_id, name, tag_val, datas):
        atta_pool = self.env['ir.attachment'].sudo()
        has_atta = atta_pool.search([('datas','=',datas),('name','=',name),('res_id', '=', order_id),('res_model', '=', 'sale.order')])
        error = ''
        if has_atta:
            if has_atta.description != tag_val:
                has_atta.description = tag_val
            else:
                error = 'already has atta file'
        else:
            vals = {
                'name':name,
                'description':tag_val,
                'res_model':'sale.order',
                'type': 'binary',
                'public': True,
                'datas':datas,
                'res_id':order_id,
                'datas_fname':name,
            }
            self.sudo().write({'bom_fields_line': [(2,x.id) for x in self.bom_fields_line]})
            pcba_order_line = self.order_line.only_pcba_order_line().sudo()#[x for x in self.order_line.sudo() if x.product_id.name == 'PCBA']
            pcb_order_line = self.order_line.only_pcb_order_line().sudo()
            if tag_val == 'BOM File' and pcba_order_line:
                if name and name[-4:].lower() == '.xls':
                    bom_file_name = name[:-4]
                elif name and name[-5:].lower() == '.xlsx':
                    bom_file_name = name[:-5]
                else:
                    bom_file_name = name
                pcba_order_line[0].write({'bom_file_name': bom_file_name})
            if tag_val == 'Gerber File' and pcb_order_line:
                n_ls = name.split('.')
                n_ls.pop()
                g_name = ''.join(x for x in n_ls)
                if not self.part_no:
                    self.sudo().write({
                        'part_no': g_name,
                    })
            atta_pool.create(vals)
        if not error and tag_val == 'BOM File':
            self.sudo().write({'check_state': 'check_off'})
        return {'error': error}


class SaleOrderLine(models.Model):
    _name = 'sale.order.line'
    _inherit = 'sale.order.line'

    @api.depends('bom_material_fee', 'product_uom_qty', 'update_bom_manage_fee')
    def _get_bom_material_manage_fee(self):
        for line in self:
            smt_price = line.env['cpo_smt_price.smt']
            plug_in_rule = smt_price.search([('type_selection', '=', 'bom_service'),('qty', '>', line.product_uom_qty)])
            if plug_in_rule:
                plug_in_rule = plug_in_rule.sorted(lambda x:x.qty)[:1]
                line.bom_material_manage_fee = line.bom_material_fee * plug_in_rule.price

    bom_rootfile = fields.Many2one('cpo_offer_bom.bom', string="BOM source")
    bom_material_type = fields.Integer(string="BOM material type")
    bom_material_price = fields.Float(string="BOM material Price")
    bom_material_fee = fields.Float(string="BOM material fee")
    bom_material_manage_fee = fields.Float(string="BOM material Manage fee", compute=_get_bom_material_manage_fee, store=True)
    update_bom_manage_fee = fields.Boolean("Update Bom Manage Fee")
    bom_file_name = fields.Char(string="Bom File Name")
    customer_file_name = fields.Char(string="Customer File Name")
    special_fee = fields.Float(string="Special Cost")

    #process_price = fields.Float(string="process")
    pcb_plate_fee = fields.Float(string="PCB plate fee", readonly=False)
    #smt_make_fee = fields.Float(string="SMT make fee")

    smt_assembly_fee = fields.Float(string="SMT Assembly fee")
    test_tool_fee = fields.Float(string="Test Tool fee")
    jig_tool_fee = fields.Float(string="Jig Tool fee")
    stencil_fee = fields.Float(string="Stencil fee")

    cpo_smt_assembly_fee = fields.Float(string="CPO SMT Assembly fee")
    cpo_test_tool_fee = fields.Float(string="CPO Test Tool fee")
    cpo_jig_tool_fee = fields.Float(string="CPO Jig Tool fee")
    cpo_stencil_fee = fields.Float(string="CPO Stencil fee")

    pcb_length = fields.Float(string="PCB Length")
    pcb_width = fields.Float(string="PCB Width")
    save_rate = fields.Float(string="Currency Rate", readonly=True)

    smt_component_qty = fields.Integer(string="SMT Component Quantity")
    smt_plug_qty = fields.Integer(string="Plug-in Pin quantity")
    #backhand_welding_qty = fields.Integer(string="backhand welding quantity")
    smt_ic_qty = fields.Integer(string="IC Quantity")
    layer_pcb = fields.Integer(string="Layer")

    cpo_note = fields.Text(string="Note")
    reset_price_total = fields.Boolean("Reset Price Total")

    etdel = fields.Float(string="Estimated time of delivery")

    single_pcb_weight = fields.Float(string="Single PCB Weight", compute='calculated_weight')
    pcb_total_weight  = fields.Float(string="PCB Total Weight", compute='calculated_weight')
    bom_sigle_weight = fields.Float(string="Single Board Material Weight")
    bom_total_weight = fields.Float(string="BOM Total Weight")
    pcba_single_weight = fields.Float(string="PCBA Single Weight", compute='calculated_weight')
    pcba_total_weight = fields.Float(string="PCBA Total Weight", compute='calculated_weight')
    pcb_thickness = fields.Float(string="PCB Thickness")
    copper_foil = fields.Float(string="Copper Foil")
    pcb_special = fields.Char(string="Special request", help="Test fee is zero when Special request is No!")

    cpo_checked = fields.Selection([('false', 'Check False'),
                                    ('true', 'Check True'),
                                    ], default="false", string="Order selection")

    @api.model
    def create(self, vals):
        res = super(SaleOrderLine, self).create(vals)
        for x_id in res:
            if x_id.product_id.name in ['PCBA', 'PCB', 'Stencil']:
                if len(x_id.order_id.order_line) > 1:
                    raise ValidationError(_("Create Order Line Length Error, Order Line Length must is one!"))
        return res

    @api.multi
    def write(self, vals):
        res = super(SaleOrderLine, self).write(vals)
        if 'product_uom_qty' in vals.keys():
            for line in self:
                if line.only_pcba_order_line().bom_rootfile:
                    line.only_pcba_order_line().bom_rootfile.write({'pcs_number': line.product_uom_qty})
        return res

    @api.multi
    def update_sale_customer_file_name(self, customer_file_name):
        for line in self:
            line.customer_file_name = customer_file_name
        return True

    @api.multi
    def update_quo_customer_file_name(self, customer_file_name):
        for line in self:
            if line.order_id.quotation_line:
                line.order_id.quotation_line.customer_file_name = customer_file_name
        return True

    @api.multi
    def update_customer_file_name(self, customer_file_name):
        for line in self.only_pcba_order_line()+self.only_pcb_order_line():
            line.customer_file_name = customer_file_name
        for line in self.only_pcb_order_line():
            if line.order_id.quotation_line:
                line.order_id.quotation_line.customer_file_name = customer_file_name
        return True

    @api.multi
    def only_pcba_order_line(self):
        return self.filtered(lambda x:x.product_id.name == 'PCBA')

    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id', 'reset_price_total', 'pcb_plate_fee', 'stencil_fee', 'special_fee', 'bom_material_manage_fee')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self.only_pcba_order_line():
            line.save_rate
            line.update_bom_manage_fee = False if line.update_bom_manage_fee else True
            #price = (line.bom_material_fee + line.process_price + line.pcb_plate_fee + line.smt_make_fee + line.stencil_fee)# * (1 - (line.discount or 0.0) / 100.0)
            #price = (line.pcb_plate_fee + line.bom_material_fee + line.smt_assembly_fee + line.test_tool_fee + line.jig_tool_fee + line.stencil_fee + line.special_fee + line.bom_material_manage_fee)# * (1 - (line.discount or 0.0) / 100.0)
            price = (line.pcb_plate_fee + line.bom_material_fee + line.smt_assembly_fee + line.test_tool_fee + line.jig_tool_fee + line.stencil_fee + line.special_fee + line.bom_material_manage_fee)# * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.tax_id.compute_all(
                price,
                line.order_id.currency_id,
                #line.product_uom_qty,
                1,
                product=line.product_id,
                partner=line.order_id.partner_shipping_id)
            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })
        #return line.price_total

    @api.multi
    def smt_price(self):
        smt_price=self.env['cpo_smt_price.smt']

        #if self.order_id.judge_state == "false_f" :
        #self.buttton_check_pcba_data()
        for row in self.only_pcba_order_line():
            if row.order_id.quotation_line:
                row.pcb_plate_fee = row.order_id.quotation_line.subtotal
            pcba_make_fee_no_bom = smt_price.get_pcba_make_fee_no_bom(
                layer_pcb = row.layer_pcb,
                pcs_number = row.product_uom_qty,
                smt_component_qty = row.smt_component_qty,
                pin_qty = row.smt_plug_qty,
                #backhand_weld_qty = row.backhand_welding_qty,
                pcb_length = row.pcb_length,
                pcb_width = row.pcb_width,
                pcb_special = row.pcb_special
            )
            if pcba_make_fee_no_bom:
                #row.smt_make_fee = pcba_make_fee_no_bom.get('smt_make_fee')
                #row.process_price = pcba_make_fee_no_bom.get('process_price')

                row.smt_assembly_fee = pcba_make_fee_no_bom.get('smt_assembly_fee')
                row.test_tool_fee = pcba_make_fee_no_bom.get('test_tool_fee')
                row.jig_tool_fee = pcba_make_fee_no_bom.get('jig_tool_fee')
                row.stencil_fee = pcba_make_fee_no_bom.get('stencil_fee')

                row.reset_price_total = False if row.reset_price_total else True
            if row.bom_rootfile and row.bom_rootfile.bom_prices:
                row.bom_material_price = row.bom_rootfile.bom_prices
                row.bom_material_fee = row.bom_rootfile.bom_prices * row.product_uom_qty
            if not row.order_id.currency_id.rate_ids:
                row.order_id.currency_id.rate_ids.create({'rate': 6.6})
            rate = row.order_id.currency_id.rate_ids[0].rate
            row.save_rate = rate

            #msg = _("Currency Rate is {rate},time:{time}").format(rate=rate,time=time.strftime("%Y-%m-%d %H:%M:%S"))
            #row.order_id.message_post(body=msg)
        return True

    @api.depends('bom_sigle_weight', 'bom_total_weight', 'pcb_thickness', 'copper_foil')
    def calculated_weight(self):
        for row in self.only_pcba_order_line():
            pcb_area = (row.pcb_length * 10**(-3)) * (row.pcb_width * 10**(-3)) #pcb板面积，最后换算成平方米
            pcb_weight = (row.pcb_thickness * 1.1875 * round(pcb_area, 6)) + (row.copper_foil * 0.31 * round(pcb_area, 6)) #pcb板重量
            row.single_pcb_weight = round(pcb_weight, 2) #一个板重量
            total_weight = row.product_uom_qty * round(pcb_weight, 2) #订购数量板的总重量
            row.pcb_total_weight = total_weight

            row.pcba_single_weight = row.bom_sigle_weight + round(pcb_weight, 2) #一个pcba的重量
            row.pcba_total_weight = row.bom_total_weight + total_weight #订购数量pcba的总重量

        return True
    #板厚(1.6mm)*1.1875(3公斤/m2)*1(平米数)
    #铜箔(1OZ)*0.31(0.31kg/1OZ)*1(平米数)

    def buttton_check_pcba_data(self):
        #check smt component qty
        for row in self.only_pcba_order_line():
            #bom_len = len(row.bom_rootfile.base_table_bom)
            bom_len = sum([x.cpo_qty for x in row.bom_rootfile.base_table_bom])
            if row.smt_component_qty != bom_len :
                line_data = {'order_id' : row.order_id.id,
                             'p_type': 'smt_component_qty',
                             'client_input_qty' : row.smt_component_qty,
                             'original_bom_qty' : bom_len}
                bom_data_check_list = [(0,0,line_data)] + [(2, x.id) for x in row.order_id.bom_data_line if x.p_type in (False,'smt_component_qty')]
                row.order_id.write({'bom_data_line' : bom_data_check_list})
                row.smt_component_qty = bom_len
                #row.order_id.judge_state = "true_t"
        #check plug pin qty

        #cpo_bom_file = self.env['ir.attachment'].search([('res_id', '=', self.order_id.id),('description', '=', 'BOM File')])
        #order_id_id = self.order_id.search([('id', '=', self.order_id.id)])
        #if not cpo_bom_file:
            #return False
        #workbook = xlrd.open_workbook(file_contents=base64.decodestring(cpo_bom_file.datas))
        #if len(workbook._sheet_list) >= 1:
        #    workbook_content = workbook.sheet_by_index(0)
        #    for x_row in range(workbook_content.nrows-1) :
        #        bom_row += 1

        #    line_data = {'order_id' : self.order_id.id,
        #                 'p_type': 'smt_number',
        #                 'client_input_qty' : self.smt_component_qty,
        #                 'original_bom_qty' : bom_row}

        #    if self.smt_component_qty != bom_row :
        #        order_id_id.write({'bom_data_line' : [(0,0,line_data)]})

        #    self.smt_component_qty = bom_row
        #    self.order_id.judge_state = "true_t"

        return True

