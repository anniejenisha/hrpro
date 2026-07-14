// Copyright (c) 2026, Jenisha and contributors
// For license information, please see license.txt

frappe.ui.form.on("Attendance Regularize", {
	attendance_date(frm) {
        frappe.db.get_value(
            "Attendance",
            {
                employee: frm.doc.employee,
                attendance_date: frm.doc.attendance_date,
                docstatus: ["!=", 2]
            },
            ["shift","in_time","out_time","name"]
        ).then(r => {
            if (r.message && r.message.shift) {
                frm.set_value("attendance_shift", r.message.shift);
                frm.set_value("first_in_time",r.message.in_time ? frappe.datetime.str_to_obj(r.message.in_time).toTimeString().split(" ")[0] : "");
                frm.set_value("last_out_time",r.message.out_time ? frappe.datetime.str_to_obj(r.message.out_time).toTimeString().split(" ")[0] : "");
                frm.set_value("attendance_marked",r.message.name)
            } 
            else{
                frm.set_value("attendance_shift", " ");
                frm.set_value("first_in_time"," ");
                frm.set_value("last_out_time"," ");
                frm.set_value("attendance_marked"," ")
            }
            
        });
	},
});
