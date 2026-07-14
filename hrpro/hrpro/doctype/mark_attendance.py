from __future__ import print_function
from pickle import TRUE
from time import strptime
from traceback import print_tb
import frappe
from frappe.utils.data import ceil, get_time, get_year_start
# import pandas as pd
import json
import datetime
from frappe.utils import (getdate, cint, add_months, date_diff, add_days,
	nowdate, get_datetime_str, cstr, get_datetime, now_datetime, format_datetime)
from datetime import datetime
from calendar import monthrange
from frappe import _, msgprint
from frappe.utils import flt
from frappe.utils import cstr, cint, getdate,get_first_day, get_last_day, today, time_diff_in_hours
import requests
from datetime import date, timedelta,time
from datetime import datetime, timedelta
from frappe.utils import get_url_to_form
import math
import dateutil.relativedelta
import datetime as dt
from datetime import datetime, timedelta

@frappe.whitelist()
def mark_att_process():
	from_date = add_days(today(),-2)  
	to_date = today()
	dates = get_dates(from_date,to_date)
	for date in dates:
		from_date = add_days(date,0)
		to_date = date
		mark_att(from_date,to_date)
		mark_wh(from_date,to_date)
		mark_late_early(from_date,to_date)

@frappe.whitelist()
def mark_att(from_date,to_date):
	checkins = frappe.db.sql("""select * from `tabEmployee Checkin` where date(time) between '%s' and '%s'  order by time ASC """%(from_date,to_date),as_dict=True)
	
	for c in checkins:
		employee = frappe.db.exists('Employee',{'status':'Active','date_of_joining':['<=',from_date],'name':c.employee})
		if employee:
			att = mark_attendance_from_checkin(c.employee,c.time,c.log_type)
			if att:
				frappe.db.set_value("Employee Checkin",c.name, "skip_auto_attendance", "1")


def mark_attendance_from_checkin(employee, time, log_type):
	att_date = time.date()

	# Get all IN checkins
	in_checkins = frappe.db.sql("""
		SELECT name, time
		FROM `tabEmployee Checkin`
		WHERE employee=%s
			AND log_type='IN'
			AND DATE(time)=%s
		ORDER BY time ASC
	""", (employee, att_date), as_dict=True)

	# Get all OUT checkins
	out_checkins = frappe.db.sql("""
		SELECT name, time
		FROM `tabEmployee Checkin`
		WHERE employee=%s
			AND log_type='OUT'
			AND DATE(time)=%s
		ORDER BY time ASC
	""", (employee, att_date), as_dict=True)

	# Get Shift
	shift_assignment = frappe.db.get_value(
		"Shift Assignment",
		{
			"employee": employee,
			"start_date": ["<=", att_date],
			"end_date": [">=", att_date],
			"docstatus": 1
		},
		"shift_type"
	)

	# Check Attendance
	att_name = frappe.db.exists(
		"Attendance",
		{
			"employee": employee,
			"attendance_date": att_date,
			"docstatus": ["!=", 2]
		}
	)

	if att_name:
		att = frappe.get_doc("Attendance", att_name)

		if att.docstatus != 0:
			return
	else:
		att = frappe.new_doc("Attendance")
		att.employee = employee
		att.attendance_date = att_date
		att.status = "Absent"

	# Set default empty values
	att.in_time = None
	att.out_time = None
	att.custom_total_working_hours = 0
	att.working_hours = 0
	att.shift = shift_assignment or ""

	# Miss Punch
	if att.custom_miss_punch_application:
		att_date_str = att.attendance_date.strftime("%Y-%m-%d")
		miss = frappe.get_doc(
			"Miss Punch Application",
			att.custom_miss_punch_application
		)

		att.in_time = get_datetime(f"{att_date_str} {miss.in_time}")
		att.out_time = get_datetime(f"{att_date_str} {miss.out_time}")
		att.shift = miss.shift or att.shift

	# Attendance Regularization
	elif att.custom_attendance_regularize:
		regu = frappe.get_doc(
			"Attendance Regularize",
			att.custom_attendance_regularize
		)

		att_date_str = regu.attendance_date.strftime("%Y-%m-%d")

		if regu.in_time == 1 and regu.corrected_in:
			att.in_time = get_datetime(f"{att_date_str} {regu.corrected_in}")
		else:
			att.in_time =in_checkins[0].time

		if regu.out_time == 1 and regu.corrected_out:
			att.out_time = get_datetime(f"{att_date_str} {regu.corrected_out}")
		else:
			att.out_time = out_checkins[-1].time

	# Normal Checkins
	else:
		if in_checkins:
			att.in_time = in_checkins[0].time

		if out_checkins:
			att.out_time = out_checkins[-1].time

	att.save(ignore_permissions=True)
	frappe.db.commit()

	# Link all checkins
	for c in in_checkins + out_checkins:
		frappe.db.set_value(
			"Employee Checkin",
			c.name,
			{
				"skip_auto_attendance": 1,
				"attendance": att.name
			}
		)

	frappe.db.commit()

	return att

def mark_wh(from_date,to_date):
	attendance = frappe.db.get_all('Attendance',{'attendance_date':('between',(from_date,to_date)),'docstatus':('!=','2'),"status":("!=","Holiday")},['*'])
	for att in attendance:
		if att.in_time and att.out_time and att.shift:
			in_time = att.in_time
			out_time = att.out_time
			if isinstance(in_time, str):
				in_time = datetime.strptime(in_time, '%Y-%m-%d %H:%M:%S')
			if isinstance(out_time, str):
				out_time = datetime.strptime(out_time, '%Y-%m-%d %H:%M:%S')
			wh = time_diff_in_hours(out_time,in_time)
			if wh:
				wh = round(wh,1)
				time_in_standard_format = time_diff_in_timedelta(in_time,out_time)
				frappe.db.set_value('Attendance', att.name, 'custom_total_working_hours', str(time_in_standard_format))
				frappe.db.set_value('Attendance', att.name, 'working_hours', str(wh))

				if att.shift and wh:
					absent = frappe.db.get_value("Shift Type",att.shift,"working_hours_threshold_for_absent")
					half = frappe.db.get_value("Shift Type",att.shift,"working_hours_threshold_for_half_day")
					if att.custom_permission_request:
						wh = float(wh) + float(att.custom_permission_hour)
					elif att.custom_on_duty_application:
						wh = float(wh) + float (att.custom_on_duty_hour)
					else:
						wh = wh
					if wh < absent:
						frappe.db.set_value("Attendance",att.name,"status","Absent")
					
					elif wh < half:
						frappe.db.set_value("Attendance",att.name,"status","Half Day")
					else:
						frappe.db.set_value("Attendance",att.name,"status","Present")
		else:
			if att.shift:
				absent = frappe.db.get_value("Shift Type",att.shift,"working_hours_threshold_for_absent")
				half = frappe.db.get_value("Shift Type",att.shift,"working_hours_threshold_for_half_day")
				if att.custom_on_duty_application:
					wh = float (att.custom_on_duty_hour)
				else:
					wh = 0 
				if wh < absent:
					frappe.db.set_value("Attendance",att.name,"status","Absent")
				
				elif wh < half:
					frappe.db.set_value("Attendance",att.name,"status","Half Day")
				else:
					frappe.db.set_value("Attendance",att.name,"status","Present")
			else:
				frappe.db.set_value("Attendance",att.name,"status","Absent")



def timedelta_to_time(td):
    """Convert timedelta to time object."""
    return (datetime.min + td).time()


def mark_late_early(from_date, to_date):
    attendance_list = frappe.get_all(
        "Attendance",
        filters={
            "attendance_date": ("between", (from_date, to_date)),
            "docstatus": 0
        },
        fields=["name", "in_time", "out_time", "shift"]
    )

    for att in attendance_list:

        # Default values
        late_entry = 0
        late_duration = "00:00:00"
        early_exit = 0
        early_duration = "00:00:00"

        if att.shift:
            start_time, end_time = frappe.db.get_value(
                "Shift Type",
                att.shift,
                ["start_time", "end_time"]
            )

            # ---------------- Late Entry ----------------
            if att.in_time and start_time:
                checkin_dt = get_datetime(att.in_time)

                shift_start_dt = datetime.combine(
                    checkin_dt.date(),
                    timedelta_to_time(start_time)
                )

                if checkin_dt > shift_start_dt:
                    late_td = checkin_dt - shift_start_dt

                    # Consider late only if >= 1 minute
                    if late_td.total_seconds() >= 60:
                        late_entry = 1
                        late_duration = str(late_td)

            # ---------------- Early Exit ----------------
            if att.out_time and end_time:
                checkout_dt = get_datetime(att.out_time)

                shift_end_dt = datetime.combine(
                    checkout_dt.date(),
                    timedelta_to_time(end_time)
                )

                if checkout_dt < shift_end_dt:
                    early_td = shift_end_dt - checkout_dt

                    # Consider early exit only if >= 1 minute
                    if early_td.total_seconds() >= 60:
                        early_exit = 1
                        early_duration = str(early_td)

        # Update Attendance once
        frappe.db.set_value(
            "Attendance",
            att.name,
            {
                "late_entry": late_entry,
                "custom_late_entry": late_duration,
                "early_exit": early_exit,
                "custom_early_exit": early_duration,
            },
            update_modified=False
        )

    frappe.db.commit()

def time_diff_in_timedelta(in_time, out_time):
	datetime_format = "%H:%M:%S"
	if out_time and in_time :
		return out_time - in_time

def get_dates(from_date,to_date):
	no_of_days = date_diff(add_days(to_date, 1), from_date)
	dates = [add_days(from_date, i) for i in range(0, no_of_days)]
	return dates