"""Customer (Developer) — Collection Lead assignment.

The guide (Section 4.1) describes assigning a CL to a developer via the
native Sales Team tab, but that resolves to a Sales Person record, not a
User — and Sales Order's Collection Lead is a Link -> User. Simpler and
more direct: put the CL assignment on the Customer itself and fetch it onto
Sales Order (setup/sales_order.py's collection_lead has fetch_from wired to
this field) — same "auto-fill from developer, stays overridable" behaviour,
one hop instead of two.
"""

from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

CUSTOM_FIELDS = {
	"Customer": [
		{
			"fieldname": "collection_lead",
			"label": "Collection Lead",
			"fieldtype": "Link",
			"options": "User",
			"description": "Default Collection Lead for orders under this developer — drives their "
			"billing alerts and account visibility",
			"insert_after": "customer_name",
		},
	]
}


def setup_customer_customization():
	create_custom_fields(CUSTOM_FIELDS, ignore_validate=True)
