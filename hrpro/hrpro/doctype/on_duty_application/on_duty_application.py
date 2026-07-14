# Copyright (c) 2026, Jenisha and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
from datetime import datetime, timedelta
import frappe
from frappe.model.document import Document
from frappe.utils import cstr, cint, getdate,get_first_day, get_last_day, today, time_diff_in_hours
from hrpro.hrpro.doctype.mark_attendance import mark_wh
from hrpro.hrpro.doctype.mark_attendance import mark_att
from hrpro.hrpro.doctype.mark_attendance import get_dates

class OnDutyApplication(Document):
	pass

	@frappe.whitelist()
	def before_save(self):
		existing = frappe.db.exists(
			"On Duty Application",
			{
				"employee": self.employee,
				"docstatus": ("!=", 2),
				"session": self.session,
				"from_date": ("<=", self.to_date),
				"to_date": (">=", self.from_date),
				"name": ("!=", self.name)
			}
		)

		if existing:
			frappe.throw("You have already applied for On Duty during the selected date range.")

	def on_submit(self):
		if frappe.db.exists("Attendance",{"employee":self.employee,"attendance_date":("between",(self.from_date,self.to_date)),"docstatus":("!=",2)}):
			att = frappe.get_doc("Attendance",frappe.db.get_value("Attendance",{"employee":self.employee,"attendance_date":("between",(self.from_date,self.to_date)),"docstatus":("!=",2)},["name"]))
			att.custom_on_duty_application = self.name
			att.custom_on_duty_hour = self.od_time
			att.save(ignore_permissions = True)
		else:
			dates = get_dates(self.from_date, self.to_date)

			for att_date in dates:

				attendance = frappe.db.exists(
					"Attendance",
					{
						"employee": self.employee,
						"attendance_date": att_date,
						"docstatus": ("!=", 2)
					}
				)

				if attendance:
					att = frappe.get_doc("Attendance", attendance)
				else:
					att = frappe.new_doc("Attendance")
					att.employee = self.employee
					att.attendance_date = att_date
					att.shift = self.shift

				att.custom_on_duty_application = self.name
				att.custom_on_duty_hour = self.od_time

				att.save(ignore_permissions=True)
		mark_wh(self.from_date,self.to_date)

	def on_cancel(self):
		att_doc = frappe.db.get_value("Attendance",{"custom_on_duty_application":self.name,"docstatus":("!=",2)},["name"])
		att = frappe.get_doc("Attendance",att_doc)
		att.custom_on_duty_application = None
		att.custom_on_duty_hour = None
		att.save(ignore_permissions=True)
		mark_att(self.from_date,self.to_date)
		mark_wh(self.from_date,self.to_date)

	@frappe.whitelist()
	def get_endtime1(self, start_time):
		hour = float(
			frappe.db.get_value(
				"Shift Type",
				self.shift,
				"working_hours_threshold_for_absent"
			) or 0
		)

		start_dt = datetime.strptime(start_time, "%H:%M:%S")
		end_dt = start_dt + timedelta(hours=hour)

		end_time = end_dt.strftime("%H:%M:%S")
		od_time = time_diff_in_hours(end_time, start_time)

		return {
			"end_time": end_time,
			"od_time": od_time
		}


	@frappe.whitelist()
	def get_endtime2(self, end_time):
		hour = float(
			frappe.db.get_value(
				"Shift Type",
				self.shift,
				"working_hours_threshold_for_absent"
			) or 0
		)

		end_dt = datetime.strptime(end_time, "%H:%M:%S")
		start_dt = end_dt - timedelta(hours=hour)

		start_time = start_dt.strftime("%H:%M:%S")
		od_time = time_diff_in_hours(end_time, start_time)

		return {
			"start_time": start_time,
			"od_time": od_time
		}
