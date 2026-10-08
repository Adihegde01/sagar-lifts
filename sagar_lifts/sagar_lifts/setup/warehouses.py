"""Sagar Lifts warehouses — Main Store (Bhiwandi godown), WIP (office store),
Finished Goods. Created under the company's root group warehouse.
"""

import frappe

WAREHOUSES = ["Sagar Lifts Main Store", "Sagar Lifts WIP", "Sagar Lifts Finished Goods"]


def setup_warehouses():
	company = frappe.db.get_value("Company", {}, ["name", "abbr"], as_dict=True)
	if not company:
		return
	parent = frappe.db.get_value("Warehouse", {"company": company.name, "is_group": 1, "parent_warehouse": ["in", ["", None]]})
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
