1�������ֶ�
    model��electron.base
    �ֶΣ�
        p_type = fields.Many2one('electron.electronic', string="Type")  #�����ֶ�
        name = fields.Char(string="PDF Explain")                        #PDF ˵����
        pcb_number = fields.Char(string="ChinaPCBONE P/N")              #�����Ϣ ������
        dash_number = fields.Char(string="Manufacturer P/N")            #������ ������
        mini_quantity = fields.Char(string="Minimum Order Quantity")    #��Ͷ�������
        QOH = fields.Char(string="Existing Number")                     #������������棩
        price = fields.Char(string="Price")                             #����
        description = fields.Char(string="Description")                 #����
        series = fields.Char(string="Series")                           #ϵ��
        manufacture = fields.Char(string="Manufacturer")                #������
        tolerance = fields.Char(string="Tolerance")                     #�ݲ�
        size = fields.Char(string="Size")                               #��С/�ߴ�
        encapsulation = fields.Char(string="Encapsulation")             #��װ/���
        inst_type = fields.Char(string="Install Type")                  #��װ����
        packaging = fields.Char(strin="Packaging")                      #��װ
        character = fields.Char(string="Character")                     #����
        parts_state = fields.Char(string="Parts State")                 #���״̬
        
2����λ��-�ɱ����
    model��electron.potentiometer
    �ֶΣ�
        
