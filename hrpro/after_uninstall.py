import frappe
from hrpro.custom_fields import get_custom_fields


def delete_custom_fields():
    fields = get_custom_fields()

    for dt, field_list in fields.items():
        for field in field_list:
            fieldname = field["fieldname"]
            if frappe.db.exists("Custom Field", {"dt": dt, "fieldname": fieldname}):
                name = frappe.db.get_value("Custom Field", {"dt": dt, "fieldname": fieldname})
                frappe.logger("hrpro").info(f"Deleting Custom Field: {dt} - {fieldname}")
                frappe.delete_doc("Custom Field", name)

    frappe.db.commit()
    frappe.clear_cache()
