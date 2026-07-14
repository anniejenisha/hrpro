frappe.ui.form.on("Permission Request", {
    attendance_date(frm) {
        if (!frm.doc.employee || !frm.doc.attendance_date) return;

        frappe.db.get_value(
            "Attendance",
            {
                employee: frm.doc.employee,
                attendance_date: frm.doc.attendance_date,
                docstatus: ["!=", 2]
            },
            ["shift"]
        ).then(r => {
            if (r.message && r.message.shift) {
                frm.set_value("shift", r.message.shift);
                frm.trigger("set_permission_time");
            } else {
                frm.set_value("shift", "");
                frappe.msgprint(__("Attendance not found for the selected date."));
            }
        });
    },

    shift(frm) {
        frm.trigger("set_permission_time");
    },

    session(frm) {
        frm.trigger("set_permission_time");
    },

    permission_request_hours(frm) {
        frm.trigger("set_permission_time");
    },

    set_permission_time(frm) {

        if (!frm.doc.shift ||
            !frm.doc.session ||
            !frm.doc.permission_request_hours) {
            return;
        }

        frappe.db.get_doc("Shift Type", frm.doc.shift).then(shift => {

            if (frm.doc.session === "First Half") {

                frm.call("get_endtime1", {
                    start_time: shift.start_time,
                    hour: frm.doc.permission_request_hours
                }).then(r => {

                    frm.set_value("from_time", shift.start_time);
                    frm.set_value("to_time", r.message);

                });

            }

            if (frm.doc.session === "Second Half") {

                frm.call("get_endtime2", {
                    end_time: shift.end_time,
                    hour: frm.doc.permission_request_hours
                }).then(r => {

                    frm.set_value("from_time", r.message);
                    frm.set_value("to_time", shift.end_time);

                });

            }

        });

    }
});