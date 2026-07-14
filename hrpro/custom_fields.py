
def get_custom_fields():
    return {

         "Attendance":[

            dict(
                fieldname="custom_miss_punch_application",
                label="Miss Punch Application",
                fieldtype="Data",
                insert_after="custom_section_break",
                module="HRPRO",
                read_only=1
            ),
            dict(
                fieldname="custom_section_break",
                label=" ",
                fieldtype="Section Break",
                insert_after="modify_half_day_status",
                module="HRPRO"
            ),
            dict(
                fieldname="custom_total_working_hours",
                label="Total Working Hours",
                fieldtype="Time",
                insert_after="custom_early_exit",
                read_only=1,
                module="HRPRO"
            ),
            dict(
                fieldname="custom_permission_request",
                label="Permission Request",
                fieldtype="Data",
                insert_after="custom_miss_punch_application",
                read_only=1,
                module="HRPRO"
            ),
            dict(
                fieldname="custom_permission_hour",
                label="Permission Hour",
                fieldtype="Data",
                insert_after="custom_permission_request",
                read_only=1,
                module="HRPRO"
            ),
            dict(
                fieldname="custom_attendance_regularize",
                label="Attendance Regularize",
                fieldtype="Data",
                insert_after="custom_permission_hour",
                read_only=1,
                module="HRPRO"
            ),
            dict(
                fieldname="custom_on_duty_application",
                label="On Duty Application",
                fieldtype="Data",
                insert_after="custom_attendance_regularize",
                read_only=1,
                module="HRPRO"
            ),
            dict(
                fieldname="custom_on_duty_hour",
                label="On Duty Hour",
                fieldtype="Float",
                insert_after="custom_on_duty_application",
                read_only=1,
                module="HRPRO"
            ),
            dict(
                fieldname="custom_late_entry",
                label="Late Entry Time",
                fieldtype="Time",
                insert_after="late_entry",
                read_only=1,
                depends_on="eval:doc.late_entry == 1",
                module="HRPRO"
            ),
            dict(
                fieldname="custom_early_exit",
                label="Early Rxit Time",
                fieldtype="Time",
                insert_after="early_exit",
                read_only=1,
                depends_on="eval:doc.early_exit == 1",
                module="HRPRO"
            ),

         ],  

    }
