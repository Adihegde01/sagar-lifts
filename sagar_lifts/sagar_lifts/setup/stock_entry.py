"""Stock Entry — Job traceability for Material Transfer.

Implementation plan, Phase 2: "Set Linked Production Order / Maintenance Job
as a Required field on Material Transfer, so every stock issue from stores
stays traceable to a job." Only Material Transfer gets it — a Manufacture,
Repack or subcontracting Stock Entry already traces back to its own Work
Order/Subcontracting Order via native fields.
"""

from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

IS_MATERIAL_TRANSFER = 'eval:doc.purpose=="Material Transfer"'

CUSTOM_FIELDS = {
	"Stock Entry": [
		{
			"fieldname": "job_id",
			"label": "Job ID",
			"fieldtype": "Link",
			"options": "Sales Order",
			"depends_on": IS_MATERIAL_TRANSFER,
			"mandatory_depends_on": IS_MATERIAL_TRANSFER,
			"in_standard_filter": 1,
			"description": "The deployment this stock issue is for — blank and irrelevant for Manufacture/Repack/other entries",
			"insert_after": "purpose",
		},
		{
			"fieldname": "job_number",
			"label": "Job Number",
			"fieldtype": "Data",
			"fetch_from": "job_id.job_number",
			"read_only": 1,
			"depends_on": IS_MATERIAL_TRANSFER,
			"insert_after": "job_id",
		},
		{
			"fieldname": "job_name",
			"label": "Job Name",
			"fieldtype": "Data",
			"fetch_from": "job_id.job_name",
			"read_only": 1,
			"depends_on": IS_MATERIAL_TRANSFER,
			"insert_after": "job_number",
		},
	]
}


def setup_stock_entry_customization():
	create_custom_fields(CUSTOM_FIELDS, ignore_validate=True)
