# -*- coding: utf-8 -*-

from random import sample
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


CPO_TYPE_CONTINENT = [
    ('Asia', 'Asia'),
    ('Europe', 'Europe'),
    ('North_America', 'North_America'),
    ('South_America', 'South_America'),
    ('Africa', 'Africa'),
    ('Oceania', 'Oceania'),
    ('Antarctica', 'Antarctica')
]


# 洲与国家的分配
class cpo_sale_continent(models.Model):
    _name = 'cpo_sale_continent.continent'
    _order = 'continent_name, number_name'

    number_name = fields.Integer('number', readonly=True, index=True)
    continent_name = fields.Selection(CPO_TYPE_CONTINENT, string='continent', translate=True, index=True, required=True)
    cpo_country_continent = fields.Many2many('res.country')

    def function_yield1(self, certain_parameter):
        number = len(certain_parameter)
        while number - 1 >= 0:
            yield certain_parameter[number - 1]
            number -= 1

    def function_yield2(self, certain_parameter):
        number = len(certain_parameter)
        while number - 1 >= 0:
            yield certain_parameter[number - 1]
            number -= 1

    # 检查 洲与洲之间国家有没有重复
    @api.onchange('continent_name', 'cpo_country_continent')
    def onchange_country_continent(self):
        cpo_country_continent = self.cpo_country_continent
        if cpo_country_continent:
            continent_continent = self.search([])  # 洲与洲之间
            if continent_continent:
                # 当前数据 - 新创建时为空 - 旧数据增加时 有值
                continent_country = self.search([('continent_name', '=', self.continent_name),
                                                 ('number_name', '=', self.number_name)])
                # 销售 单纯国家管理
                cpo_country = self.env['cpo_sale_allocations.allocations'].search([])
                # 先检查 洲与洲 之间国家有没有重复 如 亚洲 与 欧洲 之间国家不可重叠
                for continent in self.function_yield1(continent_continent):
                    if continent.id != continent_country.id:  # 当不是当前操作对象时
                        country_ids = continent.cpo_country_continent.ids
                        if country_ids:
                            for country in self.function_yield2(cpo_country_continent):
                                if country.id in country_ids:
                                    raise ValidationError(_('current number {number_name1} {continent1} among {country1} and '
                                                            'number {number_name2} {continent2} among {country2} repeat').format
                                                          (continent1=self.continent_name,
                                                           number_name1=self.number_name,
                                                           country1=country.name,
                                                           continent2=continent.continent_name,
                                                           number_name2=continent.number_name,
                                                           country2=country.name))
                # 检查 洲 与 销售人员单纯管理国家
                for country_id in self.function_yield1(cpo_country):
                    country = country_id.cpo_country_id.ids
                    for country_continent_ids in self.function_yield2(cpo_country_continent):
                        if country_continent_ids.id in country:
                            raise ValidationError(_(
                                'current number {number_name1} {continent1} among {country1} and'
                                ' salesperson {salesperson1} have jurisdiction over {country2} repeat'
                            ).format(
                                number_name1=self.number_name,
                                continent1=self.continent_name,
                                country1=country_continent_ids.name,
                                salesperson1=country_id.name.name,
                                country2=country_continent_ids.name
                            ))

    # 进行自动编号
    @api.onchange('continent_name')
    def onchange_number_name(self):
        continent_name = self.search([('continent_name', '=', self.continent_name)])
        if len(continent_name) >= 1:
            continent = continent_name.ids
            continent_id = max(continent)
            continent_name = continent_name.browse(continent_id)
            number = continent_name.number_name
            self.number_name = number + 1
        else:
            self.number_name = 1


# 销售人员与洲的分配
class cpo_sale_allocations(models.Model):
    _name = 'cpo_sale_allocations.allocations'
    _order = 'name, cpo_continent_id, cpo_country_id, cpo_partner_id'
    _description = 'Sale Staff Assignments'

    name = fields.Many2one('res.users', string='Salesperson', index=True, required=True)
    cpo_continent_id = fields.Many2many('cpo_sale_continent.continent', 'continent_name', string='Management area type')
    cpo_country_id = fields.Many2many('res.country', string='country')
    cpo_partner_id = fields.Many2many('personal.center', string='partner')
    web_code = fields.Char('Seller Code', compute='_get_web_code', store=True)
    seller_code = fields.Char('Board Factory Seller Code')
    email = fields.Char(string='E-mail')
    phone = fields.Char(string='Phone')
    seller_name = fields.Char(related='name.name')
    image = fields.Binary("Image", attachment=True,
                          help="This field holds the image used as avatar for this contact, limited to 1024x1024px",
                          related='name.image')
    image_medium = fields.Binary("Medium-sized image", attachment=True, related='name.image_medium',
                                 help="Medium-sized image of this contact. It is automatically "
                                      "resized as a 128x128px image, with aspect ratio preserved. "
                                      "Use this field in form views or some kanban views.")
    image_small = fields.Binary("Small-sized image", attachment=True, related='name.image_small',
                                help="Small-sized image of this contact. It is automatically "
                                     "resized as a 64x64px image, with aspect ratio preserved. "
                                     "Use this field anywhere a small image is required.")

    @api.depends('name')
    def _get_web_code(self):
        x_str = "CPO000"
        for x_id in self:
            if type(x_id.id) is not int:
                continue
            x_id.web_code = x_str[:-len(str(x_id.id))] + str(x_id.id)

    def function_yield1(self, certain_parameter):
        number = len(certain_parameter)
        while number - 1 >= 0:
            yield certain_parameter[number - 1]
            number -= 1

    def function_yield2(self, certain_parameter):
        number = len(certain_parameter)
        while number - 1 >= 0:
            yield certain_parameter[number - 1]
            number -= 1

    # 检查 每个销售人员 先解决管辖的洲不能重复 - 完成
    @api.onchange('cpo_continent_id')
    def onchange_check_up_continent_id(self):
        if self.cpo_continent_id:
            users_ids = self.env['res.users'].search([]).ids
            for id in self.function_yield1(users_ids):
                allocations_id = self.search([('name.id', '=', id)])
                cpo_continent = allocations_id.cpo_continent_id.ids
                if allocations_id.name.id !=self.name.id:
                    if cpo_continent:
                        for continent in self.function_yield2(self.cpo_continent_id):
                            continent_id = continent.id
                            if continent_id in cpo_continent:
                                raise ValidationError(
                                    _('current salesperson {salesperson1} have jurisdiction over {number1} {continent1}'
                                      ' and salesperson {salesperson2} have jurisdiction over {number2} {continent2} repeat').format
                                    (salesperson1=self.name.name,
                                     number1=continent.number_name,
                                     continent1=continent.continent_name,
                                     salesperson2=allocations_id.name.name,
                                     number2=continent.number_name,
                                     continent2=continent.continent_name,)
                                )

    # 检查 每个销售人员 管辖的国家与 分区好的洲 是否有重复
    @api.onchange('cpo_country_id')
    def onchange_check_up_country_id(self):
        # 销售人员的id号
        if self.cpo_country_id:
            users_ids = self.env['res.users'].search([]).ids
            continent_ids = self.env['cpo_sale_continent.continent'].search([])  # 大洲
            for id in self.function_yield1(users_ids):
                allocations_id = self.search([('name.id', '=', id)])
                cpo_country = allocations_id.cpo_country_id.ids  # 国家
                if allocations_id.name.id != self.name.id:
                    if cpo_country:
                        for country in self.function_yield2(self.cpo_country_id):
                            country_id = country.id
                            if country_id in cpo_country:
                                # 销售人员xxx直接管辖的xx国家与销售人员xxx直接管辖的xx国家重复
                                raise ValidationError(
                                    _('current salesperson {salesperson1} have jurisdiction over {country1} and '
                                      'salesperson {salesperson2} have jurisdiction over {country2} repeat'
                                      ).format
                                    (salesperson1=self.name.name,
                                     country1=country.name,
                                     salesperson2=allocations_id.name.name,
                                     country2=country.name))
            for continent in self.function_yield1(continent_ids):
                country_continent_ids = continent.cpo_country_continent.ids
                for country_id in self.function_yield2(self.cpo_country_id):
                    if country_id.id in country_continent_ids:
                        raise ValidationError(_(
                            'current salesperson {salesperson1} have jurisdiction over {country1} and '
                            '{number_name} {continent_name} among {country2} repeat'
                        ).format(
                            salesperson1=self.name.name,
                            country1=country_id.name,
                            number_name=continent.number_name,
                            continent_name=continent.continent_name,
                            country2=country_id.name,
                        ))

    # 检查客户 之间不能重复
    @api.onchange('cpo_partner_id')
    def onchange_check_up_partner_id(self):
        if self.cpo_partner_id:
            users_ids = self.env['res.users'].search([]).ids
            for id in self.function_yield1(users_ids):
                allocations_id = self.search([('name.id', '=', id)])
                cpo_partner = allocations_id.cpo_partner_id.ids  # 客户
                if allocations_id.name.id != self.name.id:
                    if cpo_partner:
                        for partner in self.function_yield2(self.cpo_partner_id):
                            partner_id = partner.id
                            if partner_id in cpo_partner:
                                # 销售人员xxx管理的xx客户与销售人员xxx管理的xx客户重复
                                raise ValidationError(_('current salesperson {salesperson1} have jurisdiction over {partner1} and '
                                                      'salesperson {salesperson2} have jurisdiction over {partner2} repeat').format
                                                      (salesperson1=self.name.name,
                                                       partner1=partner.name,
                                                       salesperson2=allocations_id.name.name,
                                                       partner2=partner.name))

    # 销售人员不能重复出现 - 算是完成
    @api.onchange('name')
    def onchange_check_up_name(self):
        name_ids = self.search([('name', '=', self.name.id)]).ids
        if len(name_ids) >= 1:
            raise ValidationError(_('{name} The salesperson to exist does not need to be created').format(name=self.name.name))
        return self.update({'phone': self.name.phone, 'email': self.name.email})

    # 销售人员分配客户
    @api.multi
    def cpo_create_salesperson(self, partner_id):
        # 销售人员分配客户
        partner_country_id = self.env['res.partner'].search([('id', '=', partner_id)]).country_id  # 客户国家
        allocations_ids = self.env['cpo_sale_allocations.allocations'].search([])
        for x_id in self.function_yield1(allocations_ids):
            # 从小到大 客户 国家 洲
            cpo_partner_id = x_id.cpo_partner_id.ids
            cpo_country_id = x_id.cpo_country_id.ids
            cpo_continent_id = x_id.cpo_continent_id
            if partner_id in cpo_partner_id:  # 客户
                return x_id.name.id
            elif partner_country_id.id in cpo_country_id:  # 国家
                return x_id.name.id
            elif cpo_continent_id:  # 大洲
                for continent in self.function_yield2(cpo_continent_id):
                    if partner_country_id.id in continent.cpo_country_continent.ids:
                        return x_id.name.id
        # 都没有管理的情况 - 有主管 决定 谁来跟踪
        else:
            return None

    # 此方法是将客户分配到指定的销售员身上 - 往后可以用于前端调用
    def GetAssignSalesperson(self, client_id, seller_id):
        seller = self.search([('cpo_partner_id', '=', client_id)])
        if seller:
            self.RemoveClient(seller, client_id)
        if seller_id:
            self.UpdateClient(seller_id, client_id)
        return True

    # 移除管理的客户
    def RemoveClient(self, seller, client_id):
        client_ids = seller.cpo_partner_id.ids
        client_ids.remove(client_id)
        seller.update({'cpo_partner_id': [(6, 0, client_ids)]})
        return True

    # 更新客户
    def UpdateClient(self, seller_id, client_id):
        client_ids = seller_id.cpo_partner_id.ids
        client_ids.append(client_id)
        seller_id.update({'cpo_partner_id': [(6, 0, client_ids)]})
        return True

    # 随机分配
    def RandomlyAssigned(self):
        seller = self.search([])
        if not seller:
            return False
        seller = sample(seller, 1)
        return seller[0]


class sale_allocations_inherit_sale_order(models.Model):
    _inherit = 'sale.order'

    def write(self, vals):
        if vals.get('state') == 'wait_confirm':
            cpo_user_id = self.association_partner_seller()
            vals.update({'user_id': cpo_user_id})
        return super(sale_allocations_inherit_sale_order, self).write(vals)

    # 客户关联销售员
    def association_partner_seller(self):
        for x_id in self:
            partner_id = x_id.partner_id.id  # 客户
            allocations_function = self.env['cpo_sale_allocations.allocations']
            cpo_user_id = allocations_function.cpo_create_salesperson(partner_id)
            if self.quotation_line and cpo_user_id:
                self.update_quotation_user_id_for_order(user_id=cpo_user_id)
            return cpo_user_id


class InheritPersonalCenter(models.Model):
    _inherit = 'personal.center'

    seller_id = fields.Many2one('cpo_sale_allocations.allocations', 'Responsible Salesperson')

    @api.model
    def create(self, vals):
        allocations = self.env['cpo_sale_allocations.allocations']
        seller_id = allocations.RandomlyAssigned()
        if not seller_id:
            return super(InheritPersonalCenter, self).create(vals)
        vals.update({'seller_id': seller_id.id})
        res = super(InheritPersonalCenter, self).create(vals)
        allocations.GetAssignSalesperson(res.id, seller_id)
        return res

    @api.multi
    def write(self, vals):
        res = super(InheritPersonalCenter, self).write(vals)
        if 'seller_id' in vals.keys():
            self.env['cpo_sale_allocations.allocations'].GetAssignSalesperson(self.id, self.seller_id)
        return res


# 勿删 权限中需要引用
class ResUsers(models.Model):
    _inherit = 'res.users'

