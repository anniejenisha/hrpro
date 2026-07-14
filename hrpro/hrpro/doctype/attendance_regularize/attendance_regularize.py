# Copyright (c) 2026, Jenisha and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
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

class AttendanceRegularize(Document):
	def before_save(self):
		if frappe.db.exists("Attendance Regularize",{"employee":self.employee,"attendance_date":self.attendance_date,"docstatus":("!=",2),"name":("!=",self.name)}):
			frappe.throw("You have already Applied your Regularize")

	def on_submit(self):
		attendance = frappe.db.exists(
			"Attendance",
			{
				"employee": self.employee,
				"attendance_date": self.attendance_date
			}
		)

		if attendance:
			att = frappe.get_doc("Attendance", attendance)
		else:
			att = frappe.new_doc("Attendance")
			att.employee = self.employee
			att.attendance_date = self.attendance_date
		att.shift = frappe.db.get_value(
			"Shift Assignment",
			{
				"employee": self.employee,
				"start_date": ["<=", self.attendance_date],
				"end_date": [">=", self.attendance_date],
				"docstatus": 1
			},
			"shift_type"
		)
		# Link Regularization document
		att.custom_attendance_regularize = self.name

		if self.in_time == 1 and self.corrected_in:
			att.in_time = get_datetime(f"{self.attendance_date} {self.corrected_in}")

		if self.out_time == 1 and self.corrected_out:
			att.out_time = get_datetime(f"{self.attendance_date} {self.corrected_out}")

		att.save(ignore_permissions=True)
		self.db_set("attendance_marked", att.name)

		mark_att(self.attendance_date, self.attendance_date)
		# Recalculate working hours
		mark_wh(self.attendance_date, self.attendance_date)


	def on_cancel(self):
		attendance = frappe.db.exists(
			"Attendance",
			{
				"employee": self.employee,
				"attendance_date": self.attendance_date
			}
		)

		if attendance:
			att = frappe.get_doc("Attendance", attendance)
			att.in_time = None
			att.out_time = None
			att.shift = None
			att.custom_attendance_regularize = None
			att.status = "Absent"
			att.custom_total_working_hours = None
			att.save(ignore_permissions=True)

			self.db_set("attendance_marked", None)

			mark_att(self.attendance_date, self.attendance_date)
			# Recalculate working hours
			mark_wh(self.attendance_date, self.attendance_date)
