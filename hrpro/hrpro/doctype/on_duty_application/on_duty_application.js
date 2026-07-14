// Copyright (c) 2026, Jenisha and contributors
// For license information, please see license.txt

frappe.ui.form.on("On Duty Application", {
	to_date(frm) {
        frappe.db.get_value(
            "Shift Assignment",
            {
                employee: frm.doc.employee,
                start_date: ["<=", frm.doc.from_date],
                end_date: [">=", frm.doc.to_date],
                docstatus: 1
            },
            ["shift_type"]
        ).then(r => {
            if (r.message && r.message.shift_type) {
                frm.set_value("shift", r.message.shift_type);
            } else {
                frm.set_value("shift", "");
            }
        });
	},
    session(frm){
        frm.trigger("set_duty_hours")
    },
    set_duty_hours(frm) {

        if (!frm.doc.shift ||
            !frm.doc.session 
            ) {
            return;
        }

        frappe.db.get_doc("Shift Type", frm.doc.shift).then(shift => {

            if (frm.doc.session === "First Half") {

                frm.call("get_endtime1", {
                    start_time: shift.start_time,
                }).then(r => {

                    frm.set_value("from_time", shift.start_time);
                    frm.set_value("to_time", r.message.end_time);
                    frm.set_value("od_time",r.message.od_time)

                });

            }

            if (frm.doc.session === "Second Half") {

                frm.call("get_endtime2", {
                    end_time: shift.end_time,
                }).then(r => {

                    frm.set_value("from_time", r.message.start_time);
                    frm.set_value("to_time", shift.end_time);
                    frm.set_value("od_time",r.message.od_time)

                });

            }

            if (frm.doc.session === "Full Day") {

                frm.set_value("from_time",shift.start_time);
                frm.set_value("to_time", shift.end_time);
                frm.set_value("od_time","9.0")

            }
            
        });

    }
});
