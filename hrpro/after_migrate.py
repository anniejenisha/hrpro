import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from hrpro.custom_fields import get_custom_fields


def create_fields():
	fields = get_custom_fields()

	for dt, field_list in fields.items():
		for field in field_list:
			frappe.logger("hrpro").info(f"Ensuring field exists: {dt} - {field['fieldname']}")

	create_custom_fields(fields, update=True)

	frappe.logger("hrpro").info("Custom field sync completed")