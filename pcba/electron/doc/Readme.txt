1、基本字段
    model：electron.base
    字段：
        p_type = fields.Many2one('electron.electronic', string="Type")  #关联字段
        name = fields.Char(string="PDF Explain")                        #PDF 说明书
        pcb_number = fields.Char(string="ChinaPCBONE P/N")              #瑞邦信息 零件编号
        dash_number = fields.Char(string="Manufacturer P/N")            #制造商 零件编号
        mini_quantity = fields.Char(string="Minimum Order Quantity")    #最低订购数量
        QOH = fields.Char(string="Existing Number")                     #现有数量（库存）
        price = fields.Char(string="Price")                             #单价
        description = fields.Char(string="Description")                 #描述
        series = fields.Char(string="Series")                           #系列
        manufacture = fields.Char(string="Manufacturer")                #制造商
        tolerance = fields.Char(string="Tolerance")                     #容差
        size = fields.Char(string="Size")                               #大小/尺寸
        encapsulation = fields.Char(string="Encapsulation")             #封装/外壳
        inst_type = fields.Char(string="Install Type")                  #安装类型
        packaging = fields.Char(strin="Packaging")                      #包装
        character = fields.Char(string="Character")                     #特性
        parts_state = fields.Char(string="Parts State")                 #零件状态
        
2、电位计-可变电阻
    model：electron.potentiometer
    字段：
        
