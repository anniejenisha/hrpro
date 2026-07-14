from datetime import datetime, timedelta
import frappe
from frappe.model.document import Document
from hrpro.hrpro.doctype.mark_attendance import mark_wh
from hrpro.hrpro.doctype.mark_attendance import mark_att

class PermissionRequest(Document):

	@frappe.whitelist()
	def before_save(self):
		if frappe.db.exists("Permission Request",{"employee":self.employee,"attendance_date":self.attendance_date,"docstatus":("!=",2),"session":self.session,"name": ("!=", self.name)}):
			frappe.throw("You have already Applied your Permission")

	@frappe.whitelist()
	def on_submit(self):
		att = frappe.db.get_value("Attendance",{"employee":self.employee,"attendance_date":self.attendance_date,"docstatus":("!=",2)},["name"])
		if att:
			att_doc = frappe.get_doc("Attendance",att)
			att_doc.shift = self.shift
			att_doc.custom_permission_request = self.name
			att_doc.custom_permission_hour = self.permission_request_hours
			att_doc.save(ignore_permissions=True)
			mark_wh(self.attendance_date,self.attendance_date)

	
	@frappe.whitelist()
	def on_cancel(self):
		att = frappe.db.get_value("Attendance",{"employee":self.employee,"attendance_date":self.attendance_date,"docstatus":("!=",2)},["name"])
		if att:
			att_doc = frappe.get_doc("Attendance",att)
			att_doc.custom_permission_request = None
			att_doc.custom_permission_hour = None
			att_doc.save(ignore_permissions=True)
			mark_wh(self.attendance_date,self.attendance_date)



	@frappe.whitelist()
	def get_endtime1(self, start_time, hour):
		hour = float(hour)

		start_time = datetime.strptime(start_time, "%H:%M:%S")
		end_time = start_time + timedelta(hours=hour)

		return end_time.strftime("%H:%M:%S")


	@frappe.whitelist()
	def get_endtime2(self, end_time, hour):
		hour = float(hour)

		end_time = datetime.strptime(end_time, "%H:%M:%S")
		start_time = end_time - timedelta(hours=hour)

		return start_time.strftime("%H:%M:%S")
