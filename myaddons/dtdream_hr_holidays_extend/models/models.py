# -*- coding: utf-8 -*-
import openerp
from openerp import models, fields, api
from datetime import datetime,time
from openerp.osv import fields, osv
from openerp import models,fields
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from dateutil.relativedelta import relativedelta
from openerp.exceptions import ValidationError
from openerp.exceptions import UserError, AccessError
from openerp import tools
import math


class dtdream_hr_holidays_extend(models.Model):
    # _name = "dtdream.hr.holidays.extend"
    _inherit = "hr.holidays"
    # number_of_days_temp=fields.float('Allocation',default=123,required=1)
    attachment=fields.Binary(string="附件",store=True)
    attachment_name=fields.Char(string="附件名")
    create_type=fields.Char(string="创建类型")
    shenqingren=fields.Char( string="申请人",default=lambda self:self.env['hr.employee'].search([('login','=',self.env.user.login)]).name,readonly=1)
    @api.one
    def _compute_gonghao(self):
        self.gonghao=self.employee_id.job_number
    gonghao=fields.Char(string="工号",compute=_compute_gonghao,readonly=1)
    bumen=fields.Char(string="部门",default=lambda self:self.env['hr.employee'].search([('login','=',self.env.user.login)]).department_id.name,readonly=1)
    create_time= fields.Char(string='申请时间',default=lambda self: datetime.now().strftime("%Y-%m-%d %H:%M:%S"),readonly=1)
    # create_time=openerp.fields.Datetime.now()
    # approver1_auto = fields.Many2one("hr.employee",string="第一审批人(只用于显示)",compute=_compute_approver1)


    shenpiren1=fields.Many2one('hr.employee',string="第一审批人")

    shenpiren2=fields.Many2one('hr.employee',string="第二审批人")
    shenpiren3=fields.Many2one('hr.employee',string="第三审批人")
    shenpiren4=fields.Many2one('hr.employee',string="第四审批人")
    shenpiren5=fields.Many2one('hr.employee',string="第五审批人")
    shenpiren_his1=fields.Integer('历史审批人1')
    shenpiren_his2=fields.Integer('历史审批人2')
    shenpiren_his3=fields.Integer('历史审批人3')
    shenpiren_his4=fields.Integer('历史审批人4')
    shenpiren_his5=fields.Integer('历史审批人5')
    is_confirm2approved=fields.Boolean(default=False,string="一级审批后直接通过")
    is_confirm22approved=fields.Boolean(default=False,string="二级审批后直接通过")
    is_confirm32approved=fields.Boolean(default=False,string="三级审批后直接通过")
    is_confirm42approved=fields.Boolean(default=False,string="四审批后直接通过")

    year= fields.Selection([
        ('0',datetime.strftime(datetime.today()+relativedelta(years=1),"%Y")),
        ('1',datetime.strftime(datetime.today(),"%Y")),
        ('2',datetime.strftime(datetime.today()-relativedelta(years=1),"%Y")),
        ('3',datetime.strftime(datetime.today()-relativedelta(years=2),"%Y")),
        ('4',datetime.strftime(datetime.today()-relativedelta(years=3),"%Y")),
        ('5',datetime.strftime(datetime.today()-relativedelta(years=4),"%Y")),
        ('6',datetime.strftime(datetime.today()-relativedelta(years=5),"%Y")),

    ],string="年休假年份")

    @api.constrains('shenpiren1','shenpiren2','shenpiren3','shenpiren4','shenpiren5','employee_id','holiday_status_id','number_of_days_temp')
    def change(self):

        nianjia=self.env['hr.holidays'].search([('employee_id','=',self.employee_id.id),('holiday_status_id','=',5),('state','!=','draft')],order="id desc")
        length=len(nianjia)
        remain_nianjia_days=0
        for record in nianjia:
            if record.type=="add":
                remain_nianjia_days +=record.number_of_days_temp
            elif record.type=="remove":
                remain_nianjia_days -=record.number_of_days_temp
        if remain_nianjia_days>0 and self.holiday_status_id.id==6:
            raise ValidationError("还有年休假余额，不能休事假！")

        if not self.shenpiren2:
            self.is_confirm2approved=self.is_confirm22approved=self.is_confirm32approved=self.is_confirm42approved=False
            self.is_confirm2approved=True
        elif not self.shenpiren3:
            self.is_confirm2approved=self.is_confirm22approved=self.is_confirm32approved=self.is_confirm42approved=False
            self.is_confirm22approved=True
        elif not self.shenpiren4:
            self.is_confirm2approved=self.is_confirm22approved=self.is_confirm32approved=self.is_confirm42approved=False
            self.is_confirm32approved=True
        elif not self.shenpiren5:
            self.is_confirm2approved=self.is_confirm22approved=self.is_confirm32approved=self.is_confirm42approved=False
            self.is_confirm42approved=True
        else:
            self.is_confirm2approved=self.is_confirm22approved=self.is_confirm32approved=self.is_confirm42approved=False

        if (self.shenpiren3 or self.shenpiren4 or self.shenpiren5) and not self.shenpiren2:
            raise ValidationError('请先填写第二审批人')
        if (self.shenpiren4 or self.shenpiren5) and not self.shenpiren3:
            raise ValidationError('请先填写第三审批人')
        if self.shenpiren5 and not self.shenpiren4:
            raise ValidationError('请先填写第四审批人')
        if self.number_of_days_temp<=0:
            raise ValidationError('天数必须大于0')



    @api.onchange('employee_id')
    def onchange_employee1(self):

        if self.employee_id:
            self.gonghao=self.env['hr.employee'].search([('id','=',self.employee_id.id)]).job_number
            self.department_id=self.env['hr.employee'].search([('id','=',self.employee_id.id)]).department_id.id
            if not self.create_type:
                self.shenpiren1=self.env['hr.employee'].search([('id','=',self.employee_id.id)]).department_id.assitant_id
                self.shenpiren2=self.env['hr.holidays'].search([('employee_id','=',self.employee_id.id),('create_type','=',False)],order="id desc",limit=1).shenpiren2
                self.shenpiren3=self.env['hr.holidays'].search([('employee_id','=',self.employee_id.id),('create_type','=',False)],order="id desc",limit=1).shenpiren3
                self.shenpiren4=self.env['hr.holidays'].search([('employee_id','=',self.employee_id.id),('create_type','=',False)],order="id desc",limit=1).shenpiren4
                self.shenpiren5=self.env['hr.holidays'].search([('employee_id','=',self.employee_id.id),('create_type','=',False)],order="id desc",limit=1).shenpiren5
            elif self.create_type:
                self.shenpiren1=self.env['hr.holidays'].search([('employee_id','=',self.employee_id.id),('create_type','=','manage')],order="id desc",limit=1).shenpiren1
                self.shenpiren2=self.env['hr.holidays'].search([('employee_id','=',self.employee_id.id),('create_type','=','manage')],order="id desc",limit=1).shenpiren2
                self.shenpiren3=self.env['hr.holidays'].search([('employee_id','=',self.employee_id.id),('create_type','=','manage')],order="id desc",limit=1).shenpiren3
                self.shenpiren4=self.env['hr.holidays'].search([('employee_id','=',self.employee_id.id),('create_type','=','manage')],order="id desc",limit=1).shenpiren4
                self.shenpiren5=self.env['hr.holidays'].search([('employee_id','=',self.employee_id.id),('create_type','=','manage')],order="id desc",limit=1).shenpiren5




    current_shenpiren=fields.Many2one('hr.employee',string='当前审批人')
    state=fields.Selection([('draft', '草稿'), ('cancel', 'Cancelled'),('confirm', '一级审批'),
                            ('confirm2', '二级审批'),('confirm3', '三级审批'),('confirm4', '四级审批'),
                            ('confirm5', '五级审批'), ('refuse', 'Refused'), ('validate1', 'Second Approval'), ('validate', '完成')],
                           'Status', readonly=True, track_visibility='onchange',default='draft')

    @api.one
    def _compute_is_shenpiren(self):
        if (self.shenpiren1.user_id.id==self.env.user.id) and self.state=='confirm':
            self.is_shenpiren=True
        elif (self.shenpiren2.user_id.id==self.env.user.id) and self.state=='confirm2':
            self.is_shenpiren=True

        elif (self.shenpiren3.user_id.id==self.env.user.id) and self.state=='confirm3':
            self.is_shenpiren=True

        elif (self.shenpiren4.user_id.id==self.env.user.id) and self.state=='confirm4':
            self.is_shenpiren=True

        elif (self.shenpiren5.user_id.id==self.env.user.id) and self.state=='confirm5':
            self.is_shenpiren=True

        else:
            self.is_shenpiren=False

    is_shenpiren=fields.Boolean(compute=_compute_is_shenpiren,string="是否审批人")


    def _check_state_access_right(self, cr, uid, vals, context=None):#重写hr_holidays里面的 _check_state_access_right，将权限开放到base.group_user
        if vals.get('state') and vals['state'] not in ['draft', 'confirm', 'confirm2' ,'confirm3','confirm4','confirm5', 'cancel'] and not self.pool['res.users'].has_group(cr, uid, 'base.group_user'):
            return False
        return True


    def get_base_url(self,cr,uid):
        base_url = self.pool.get('ir.config_parameter').get_param(cr, uid, 'web.base.url')
        return base_url
    @api.multi
    def holidays_confirm(self):

        self.shenpiren_his1=self.shenpiren1.user_id
        self.write({'state':'confirm','current_shenpiren':self.shenpiren1.id})

        # 邮件通知
        link='/web?#id=%s&view_type=form&model=hr.holidays'%self.id
        url=self.get_base_url()+link
        if self.create_type==False:
            self.env['mail.mail'].create({
                 'subject': u'%s 请假'%self.employee_id.name,
                'body_html': u'<p>%s</p><p>您有一个请假单待审批,点击<a href="%s">此处查看</p>'%(self.shenpiren1.name,url),
                'email_from': 'postmaster-odoo@dtdream.com',

                'email_to': self.shenpiren1.work_email,
            }).send()

            self.env['mail.mail'].create({
                 'subject': u'%s 请假'%self.employee_id.name,
                'body_html': u'<p>%s</p><p>您提交了一个请假单,点击<a href="%s">此处查看</p>'%(self.shenpiren1.name,url),
                'email_from': 'postmaster-odoo@dtdream.com',

                'email_to': self.employee_id.work_email,
            }).send()




    @api.multi
    def holidays_confirm2(self):
            if self.shenpiren2==False and self.create_type==False:
                raise ValidationError('请先填写第二审批人')
            else:
                self.shenpiren_his2=self.shenpiren2.user_id
                self.write({'state':'confirm2','current_shenpiren':self.shenpiren2.id})

            # 邮件通知
            link='/web?#id=%s&view_type=form&model=hr.holidays'%self.id
            url=self.get_base_url()+link

            self.env['mail.mail'].create({
                     'subject': u'%s 请假'%self.employee_id.name,
                    'body_html': u'<p>%s</p><p>您有一个请假单待审批,点击<a href="%s">此处</a>查看</p>'%(self.shenpiren2.name,url),
                    'email_from': 'postmaster-odoo@dtdream.com',

                    'email_to': self.shenpiren2.work_email,
                }).send()

            self.env['mail.mail'].create({
                    'subject': u'%s 请假'%self.employee_id.name,
                    'body_html': u'<p>%s</p><p>您的请假单状态：一级审批 -> 二级审批,点击<a href="%s">此处</a>查看</p>'%(self.employee_id.name,url),
                    'email_from': 'postmaster-odoo@dtdream.com',

                    'email_to': self.employee_id.work_email,
                }).send()

    @api.multi
    def holidays_confirm3(self):
            self.shenpiren_his3=self.shenpiren3.user_id
            self.write({'state':'confirm3','current_shenpiren':self.shenpiren3.id})

            # 邮件通知
            link='/web?#id=%s&view_type=form&model=hr.holidays'%self.id
            url=self.get_base_url()+link

            self.env['mail.mail'].create({
                     'subject': u'%s 请假'%self.employee_id.name,
                    'body_html': u'<p>%s</p><p>您有一个请假单待审批,点击<a href="%s">此处</a>查看</p>'%(self.shenpiren3.name,url),
                    'email_from': 'postmaster-odoo@dtdream.com',

                    'email_to': self.shenpiren3.work_email,
                }).send()

            self.env['mail.mail'].create({
                    'subject': u'%s 请假'%self.employee_id.name,
                    'body_html': u'<p>%s</p><p>您的请假单状态：二级审批 -> 三级审批,点击<a href="%s">此处</a>查看</p>'%(self.employee_id.name,url),
                    'email_from': 'postmaster-odoo@dtdream.com',

                    'email_to': self.employee_id.work_email,
                }).send()

    @api.multi
    def holidays_confirm4(self):

            self.shenpiren_his4=self.shenpiren4.user_id
            self.write({'state':'confirm4','current_shenpiren':self.shenpiren4.id})

            # 邮件通知
            link='/web?#id=%s&view_type=form&model=hr.holidays'%self.id
            url=self.get_base_url()+link

            self.env['mail.mail'].create({
                     'subject': u'%s 请假'%self.employee_id.name,
                    'body_html': u'<p>%s</p><p>您有一个请假单待审批,点击<a href="%s">此处</a>查看</p>'%(self.shenpiren4.name,url),
                    'email_from': 'postmaster-odoo@dtdream.com',

                    'email_to': self.shenpiren2.work_email,
                }).send()

            self.env['mail.mail'].create({
                    'subject': u'%s 请假'%self.employee_id.name,
                    'body_html': u'<p>%s</p><p>您的请假单状态：三级审批 -> 四级审批,点击<a href="%s">此处</a>查看</p>'%(self.employee_id.name,url),
                    'email_from': 'postmaster-odoo@dtdream.com',

                    'email_to': self.employee_id.work_email,
                }).send()

    @api.multi
    def holidays_confirm5(self):

            self.shenpiren_his5=self.shenpiren5.user_id
            self.write({'state':'confirm5','current_shenpiren':self.shenpiren5.id})

            # 邮件通知
            link='/web?#id=%s&view_type=form&model=hr.holidays'%self.id
            url=self.get_base_url()+link

            self.env['mail.mail'].create({
                     'subject': u'%s 请假'%self.employee_id.name,
                    'body_html': u'<p>%s</p><p>您有一个请假单待审批,点击<a href="%s">此处</a>查看</p>'%(self.shenpiren5.name,url),
                    'email_from': 'postmaster-odoo@dtdream.com',

                    'email_to': self.shenpiren2.work_email,
                }).send()

            self.env['mail.mail'].create({
                    'subject': u'%s 请假'%self.employee_id.name,
                    'body_html': u'<p>%s</p><p>您的请假单状态：四级审批 -> 五级审批,点击<a href="%s">此处</a>查看</p>'%(self.employee_id.name,url),
                    'email_from': 'postmaster-odoo@dtdream.com',

                    'email_to': self.employee_id.work_email,
                }).send()



    def holidays_reset(self, cr, uid, ids, context=None):#重写该方法，开放重置按钮权限

        self.write(cr, uid, ids, {
            'state': 'draft',
            'manager_id': False,
            'manager_id2': False,
            'current_shenpiren':""
        })
        to_unlink = []
        for record in self.browse(cr, uid, ids, context=context):
            for record2 in record.linked_request_ids:
                self.holidays_reset(cr, uid, [record2.id], context=context)
                to_unlink.append(record2.id)
        if to_unlink:
            self.unlink(cr, uid, to_unlink, context=context)
        return True

    @api.multi
    def holidays_refuse(self):

        # 邮件通知
        link='/web?#id=%s&view_type=form&model=hr.holidays'%self.id
        url=self.get_base_url()+link
        state=dict(self.env['hr.holidays']._columns['state'].selection)[self.state]
        state_code=unicode(state,'utf-8')
        if self.create_type==False:
            self.env['mail.mail'].create({
                    'subject': u'%s 请假'%self.employee_id.name,
                    'body_html': u'<p>%s</p><p>您的请假单状态：%s -> 驳回,点击<a href="%s">此处</a>查看</p>'%(self.employee_id.name,state_code,url),
                    'email_from': 'postmaster-odoo@dtdream.com',

                    'email_to': self.employee_id.work_email,
                }).send()



        self.write({'state':'refuse','current_shenpiren':""})

    def holidays_validate(self, cr, uid, ids, context=None):
        this_self=''
        for id in ids:
            this_self=self.pool.get('hr.holidays').browse(cr, uid,id)
            if self.pool.get('hr.holidays').browse(cr, uid,id).state=='confirm' and self.pool.get('hr.holidays').browse(cr, uid,id).shenpiren2.id==False and self.pool.get('hr.holidays').browse(cr, uid,id).create_type==False:
                raise ValidationError('请先填写第二审批人')


        # 邮件通知
        link='/web?#id=%s&view_type=form&model=hr.holidays'%this_self.id
        url=this_self.get_base_url()+link
        state=dict(this_self.env['hr.holidays']._columns['state'].selection)[this_self.state]
        state_code=unicode(state,'utf-8')
        if this_self.create_type==False:
            this_self.env['mail.mail'].create({
                    'subject': u'%s 请假'%this_self.employee_id.name,
                    'body_html': u'<p>%s</p><p>您的请假单状态：%s -> 完成,点击<a href="%s">此处</a>查看</p>'%(this_self.employee_id.name,state_code,url),
                    'email_from': 'postmaster-odoo@dtdream.com',

                    'email_to': this_self.employee_id.work_email,
                }).send()
        elif this_self.create_type=='manage':
            this_self.env['mail.mail'].create({
                    'subject': u'%s 年休假分配'%this_self.employee_id.name,
                    'body_html': u'<p>%s</p><p>您有新的年休假分配,点击<a href="%s">此处</a>查看</p>'%(this_self.employee_id.name,url),
                    'email_from': 'postmaster-odoo@dtdream.com',

                    'email_to': this_self.employee_id.work_email,
                }).send()


        obj_emp = self.pool.get('hr.employee')
        ids2 = obj_emp.search(cr, uid, [('user_id', '=', uid)])
        manager = ids2 and ids2[0] or False
        self.write(cr, uid, ids, {'state': 'validate','current_shenpiren':""}, context=context)
        data_holiday = self.browse(cr, uid, ids)
        for record in data_holiday:
            if record.double_validation:
                self.write(cr, uid, [record.id], {'manager_id2': manager})
            else:
                self.write(cr, openerp.SUPERUSER_ID, [record.id], {'manager_id': manager})

            if record.holiday_type == 'employee' and record.type == 'remove':

                meeting_obj = self.pool.get('calendar.event')
                meeting_vals = {
                    'name': record.display_name,
                    'categ_ids': record.holiday_status_id.categ_id and [(6,0,[record.holiday_status_id.categ_id.id])] or [],
                    'duration': record.number_of_days_temp * 8,
                    'description': record.notes,
                    'user_id': record.user_id.id,
                    'start': record.date_from,
                    'stop': record.date_to,
                    'allday': False,
                    'state': 'open',            # to block that meeting date in the calendar
                    'class': 'confidential'
                }
                #Add the partner_id (if exist) as an attendee
                if record.user_id and record.user_id.partner_id:

                    meeting_vals['partner_ids'] = [(4,record.user_id.partner_id.id)]


                ctx_no_email = dict(context or {}, no_email=True)

                # meeting_id = meeting_obj.create(cr, uid, meeting_vals, context=ctx_no_email)


                self._create_resource_leave(cr, openerp.SUPERUSER_ID, [record], context=context)

                # self.write(cr, openerp.SUPERUSER_ID, ids, {'meeting_id': meeting_id})

            elif record.holiday_type == 'category':
                emp_ids = record.category_id.employee_ids.ids
                leave_ids = []
                batch_context = dict(context, mail_notify_force_send=False)
                for emp in obj_emp.browse(cr, uid, emp_ids, context=context):
                    vals = {
                        'name': record.name,
                        'type': record.type,
                        'holiday_type': 'employee',
                        'holiday_status_id': record.holiday_status_id.id,
                        'date_from': record.date_from,
                        'date_to': record.date_to,
                        'notes': record.notes,
                        'number_of_days_temp': record.number_of_days_temp,
                        'parent_id': record.id,
                        'employee_id': emp.id
                    }
                    leave_ids.append(self.create(cr, uid, vals, context=batch_context))
                for leave_id in leave_ids:
                    # TODO is it necessary to interleave the calls?
                    for sig in ('confirm', 'validate', 'second_validate'):
                        self.signal_workflow(cr, uid, [leave_id], sig)
        return True








    def unlink(self, cr, uid, ids, context=None):

        for rec in self.browse(cr, uid, ids, context=context):
            if rec.state not in ['draft', 'cancel', 'confirm','confirm1','confirm2','confirm3','confirm4','confirm5','refuse']:
                # raise UserError(_('You cannot delete a leave which is in %s state.') % (rec.state,))
                print "pass"

        return models.Model.unlink(self, cr, uid, ids, context=None)

    def onchange_date_from(self, cr, uid, ids, date_to, date_from):
        """
        If there are no date set for date_to, automatically set one 8 hours later than
        the date_from.
        Also update the number_of_days.
        """
        # date_to has to be greater than date_from


        result = {'value': {}}



        # Compute and update the number of days
        if (date_to and date_from) and (date_from <= date_to):
            diff_day = self._get_number_of_days(date_from, date_to)
            result['value']['number_of_days_temp'] = round(math.floor(diff_day))+1
        else:
            result['value']['number_of_days_temp'] = 0

        return result

    def onchange_date_to(self, cr, uid, ids, date_to, date_from):
        """
        Update the number_of_days.
        """
        # date_to has to be greater than date_from


        result = {'value': {}}

        # Compute and update the number of days
        if (date_to and date_from) and (date_from <= date_to):
            diff_day = self._get_number_of_days(date_from, date_to)
            result['value']['number_of_days_temp'] = round(math.floor(diff_day))+1
        else:
            result['value']['number_of_days_temp'] = 0
        return result



class dtdream_nianjia(models.Model):
    _name = "dtdream.nianjia"

    employee = fields.Many2one('hr.employee',string="选择员工")
    number_of_days = fields.Integer(string="分配的天数")
    year = fields.Integer(string="年休假年份")

    @api.model
    def create(self, vals):

        nianjia=self.env['hr.holidays']

        tec =  nianjia.create({'employee_id':vals['employee'],'state':'validate','type':'add','year':vals['year'],'holiday_status_id':5,'number_of_days_temp':vals['number_of_days']})

        tec.write({'state':'validate'})

        return super(dtdream_nianjia,self).create(vals)

    @api.multi
    def unlink(self):


        employee=self.env['dtdream.nianjia'].search([('id','=',self.id)]).employee
        year=self.env['dtdream.nianjia'].search([('id','=',self.id)]).year
        nianjia=self.env['hr.holidays'].search([('employee_id','=',employee.id),('year','=',year)])

        nianjia.write({'number_of_days_temp':0})
        return super(dtdream_nianjia,self).unlink()


class batch_approval(models.Model):
    _name = "batch.approval"

    @api.multi
    def batch_approval(self):

        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []

        for record in self.env['hr.holidays'].browse(active_ids):
            if record.create_type=="manage":
                if record.state in ('draft'):
                    record.signal_workflow('confirm')
                elif record.state in ('confirm'):
                    record.signal_workflow('validate')
            else:
                raise ValidationError('只有年休假才具备该功能')
        return {'type': 'ir.actions.act_window_close'}

class hr_holidays_wizard(models.TransientModel):
     _name = "hr.holidays.wizard"
     deny_reason=fields.Text("拒绝理由",required=True)

     @api.one
     def btn_confirm(self):
          #send the reason to chatter
          current_qingjiadan=self.env['hr.holidays'].browse(self._context['active_id'])
          current_qingjiadan.message_post(body=self.deny_reason)
          current_qingjiadan.signal_workflow('refuse')

class hr_holidays_status_extend(osv.osv):
    _inherit = "hr.holidays.status"

    def get_days(self, cr, uid, ids, employee_id, context=None):

        result = dict((id, dict(max_leaves=0, leaves_taken=0, remaining_leaves=0,
                                virtual_remaining_leaves=0)) for id in ids)
        holiday_ids = self.pool['hr.holidays'].search(cr, uid, [('employee_id', '=', employee_id),
                                                                ('state', 'in', ['confirm', 'validate1','confirm2','confirm3','confirm4','confirm5', 'validate']),
                                                                ('holiday_status_id', 'in', ids)
                                                                ], context=context)
        for holiday in self.pool['hr.holidays'].browse(cr, uid, holiday_ids, context=context):
            status_dict = result[holiday.holiday_status_id.id]
            if holiday.type == 'add':
                if holiday.state == 'validate':
                    # note: add only validated allocation even for the virtual
                    # count; otherwise pending then refused allocation allow
                    # the employee to create more leaves than possible
                    status_dict['virtual_remaining_leaves'] += holiday.number_of_days_temp
                    status_dict['max_leaves'] += holiday.number_of_days_temp
                    status_dict['remaining_leaves'] += holiday.number_of_days_temp
            elif holiday.type == 'remove':  # number of days is negative
                status_dict['virtual_remaining_leaves'] -= holiday.number_of_days_temp
                if holiday.state == 'validate':
                    status_dict['leaves_taken'] += holiday.number_of_days_temp
                    status_dict['remaining_leaves'] -= holiday.number_of_days_temp
        return result




