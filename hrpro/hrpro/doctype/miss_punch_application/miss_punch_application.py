# Copyright (c) 2026, Jenisha and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
# Copyright (c) 2024, TEAMPROO and contributors
# For license information, please see license.txt
from email import message
import frappe
import datetime
import math
from frappe.utils import (getdate, cint, add_months, date_diff, add_days,
    nowdate, get_datetime_str, cstr, get_datetime, now_datetime, format_datetime,format_date)
from frappe.utils import cstr, cint, getdate,get_first_day, get_last_day, today, time_diff_in_hours   
from datetime import date, timedelta,time,datetime
from frappe import _
from frappe.utils.background_jobs import enqueue
import frappe
from frappe.utils import time_diff_in_hours
from datetime import datetime, timedelta
from frappe.model.document import Document
from hrpro.hrpro.doctype.mark_attendance import mark_wh
from hrpro.hrpro.doctype.mark_attendance import mark_att

class MissPunchApplication(Document):
	def before_save(self):
		if frappe.db.exists("Miss Punch Application",{"employee":self.employee,"attendance_date":self.attendance_date,"docstatus":("!=",2),"name":("!=",self.name)}):
			frappe.throw("You have already Applied your Miss Punch")

	def on_submit(self):
		att = frappe.db.get_value("Attendance",{"employee":self.employee,"attendance_date":self.attendance_date,"docstatus":("!=",2)},["name"])
		if att:
			att_doc = frappe.get_doc("Attendance",att)
			att_doc.shift = self.shift
			att_doc.in_time = get_datetime(f"{self.attendance_date} {self.in_time}")
			att_doc.out_time = get_datetime(f"{self.attendance_date} {self.out_time}")
			att_doc.custom_miss_punch_application = self.name
			att_doc.save(ignore_permissions=True)
			mark_wh(self.attendance_date,self.attendance_date)

	
	def on_cancel(self):
		att = frappe.db.get_value("Attendance",{"employee":self.employee,"attendance_date":self.attendance_date,"docstatus":("!=",2)},["name"])
		if att:
			att_doc = frappe.get_doc("Attendance",att)
			att_doc.custom_miss_punch_application = None
			att_doc.save(ignore_permissions=True)
			mark_att(self.attendance_date,self.attendance_date)
			mark_wh(self.attendance_date,self.attendance_date)

			
