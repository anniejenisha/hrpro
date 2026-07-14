// Copyright (c) 2026, Jenisha and contributors
// For license information, please see license.txt

frappe.ui.form.on("Miss Punch Application", {
    refresh(frm){
         if (frm.doc.employee && frm.doc.attendance_date) {
            frappe.db.get_value(
                "Attendance",
                {
                    employee: frm.doc.employee,
                    attendance_date: frm.doc.attendance_date,
                    docstatus: ["!=", 2]
                },
                ["in_time", "out_time","shift"]
            ).then(r => {
                if(r.message.in_time){
                    frm.set_df_property('in_time', 'read_only', 1);
                }
                if(r.message.out_time){
                    frm.set_df_property('out_time', 'read_only', 1);
                }
            });
        }
    },
    attendance_date(frm) {
        if (frm.doc.employee && frm.doc.attendance_date) {
            frappe.db.get_value(
                "Attendance",
                {
                    employee: frm.doc.employee,
                    attendance_date: frm.doc.attendance_date,
                    docstatus: ["!=", 2]
                },
                ["in_time", "out_time", "shift"]
            ).then(r => {
                if (r.message) {

                    frm.set_value(
                        "in_time",
                        r.message.in_time ? frappe.datetime.str_to_obj(r.message.in_time).toTimeString().split(" ")[0] : ""
                    );

                    frm.set_value(
                        "out_time",
                        r.message.out_time ? frappe.datetime.str_to_obj(r.message.out_time).toTimeString().split(" ")[0] : ""
                    );

                    frm.set_value("shift", r.message.shift);

                    frm.set_df_property("in_time", "read_only", !!r.message.in_time);
                    frm.set_df_property("out_time", "read_only", !!r.message.out_time);

                } else {
                    frm.set_value("in_time", "");
                    frm.set_value("out_time", "");
                    frm.set_value("shift", "");

                    frm.set_df_property("in_time", "read_only", 0);
                    frm.set_df_property("out_time", "read_only", 0);

                    frappe.msgprint(__("Attendance not found for the selected date."));
                }
            });
        }
    }
});
