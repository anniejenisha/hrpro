// Copyright (c) 2026, Jenisha and contributors
// For license information, please see license.txt

frappe.ui.form.on("Attendance Setting", {
	refresh(frm) {
        frm.disable_save();
	},
    attendance(frm){
        if(frm.doc.from_date && frm.doc.to_date){
            frappe.call({
                method:"hrpro.hrpro.doctype.mark_attendance.attendance_settings",
                args:{
                    from_date:frm.doc.from_date,
                    to_date:frm.doc.to_date
                },
                callback(r){
                    frappe.msgprint("Please wait a few minutes. Your attendance will be updated shortly")
                }
            })
        }
    }
});
