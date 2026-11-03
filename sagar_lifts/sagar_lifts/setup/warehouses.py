"""Sagar Lifts warehouses — the two godowns (Bhiwandi, Andheri office) plus
Finished Goods. Created under the company's root group warehouse.
"""

import frappe

WAREHOUSES = ["Bhiwandi Godown", "Andheri Office Godown", "Sagar Lifts Finished Goods"]

# The first names given to the two godowns, renamed to what Sagar Lifts calls them.
RENAMED = {"Sagar Lifts Main Store": "Bhiwandi Godown", "Sagar Lifts WIP": "Andheri Office Godown"}


def setup_warehouses():
	company = frappe.db.get_value("Company", {}, ["name", "abbr"], as_dict=True)
	if not company:
		return
	parent = frappe.db.get_value("Warehouse", {"company": company.name, "is_group": 1, "parent_warehouse": ["in", ["", None]]})
	for old, new in RENAMED.items():
		old, new = f"{old} - {company.abbr}", f"{new} - {company.abbr}"
		if frappe.db.exists("Warehouse", old) and not frappe.db.exists("Warehouse", new):
			frappe.rename_doc("Warehouse", old, new, force=True)
			frappe.db.set_value("Warehouse", new, "warehouse_name", new.rsplit(" - ", 1)[0])
	for warehouse_name in WAREHOUSES:
		if frappe.db.exists("Warehouse", f"{warehouse_name} - {company.abbr}"):
			continue
		frappe.get_doc(
			{
				"doctype": "Warehouse",
				"warehouse_name": warehouse_name,
				"company": company.name,
				"parent_warehouse": parent,
			}
		).insert(ignore_permissions=True)
