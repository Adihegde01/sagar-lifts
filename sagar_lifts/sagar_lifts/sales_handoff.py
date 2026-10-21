"""Sales -> Operations handoff (sales guide Section 10).

Quotation -> Sales Order pre-fills the job's developer/site/lift details from
the CRM Lead, its Scout Report and the Opportunity, so the order isn't
re-typed. Submitting the Sales Order ticks Order Confirmed on the Opportunity.
"""

import frappe
from erpnext.selling.doctype.quotation.quotation import make_sales_order as erpnext_make_sales_order
from frappe.utils import today


@frappe.whitelist()
def make_sales_order(source_name: str, target_doc=None, args=None):
	# hooks.override_whitelisted_methods — the Quotation's Create -> Sales Order button
	so = erpnext_make_sales_order(source_name, target_doc, args)
	fill_from_crm(so, source_name)
	return so


def crm_sources(quotation):
	"""(lead, opportunity) names behind a Quotation — either may be None."""
	q = frappe.db.get_value("Quotation", quotation, ["quotation_to", "party_name", "opportunity"], as_dict=True)
	if not q:
		return None, None
	lead = q.party_name if q.quotation_to == "Lead" else frappe.db.get_value("Customer", q.party_name, "lead_name")
	opportunity = q.opportunity
	if not opportunity and lead:
		opportunity = frappe.db.get_value(
			"Opportunity", {"opportunity_from": "Lead", "party_name": lead, "status": ("!=", "Lost")}, "name",
			order_by="creation desc",
		)
	if not lead and opportunity:
		opp = frappe.db.get_value("Opportunity", opportunity, ["opportunity_from", "party_name"], as_dict=True)
		lead = opp.party_name if opp.opportunity_from == "Lead" else None
	return lead, opportunity


def fill_from_crm(so, quotation):
	lead, opportunity = crm_sources(quotation)
	values = {}
	if lead:
		ld = frappe.db.get_value(
			"Lead", lead,
			["company_name", "lead_name", "mobile_no", "email_id", "city", "site_name", "site_city",
			 "estimated_height_m", "scout_report_reference"],
			as_dict=True,
		)
		values.update({
			"developer_name": ld.company_name or ld.lead_name,
			"developer_contact_person": ld.lead_name,
			"developer_contact_number": ld.mobile_no,
			"developer_email": ld.email_id,
			"site_name": ld.site_name,
			"site_city": ld.site_city or ld.city,
			"lift_height": ld.estimated_height_m,
		})
		if ld.scout_report_reference:
			sr = frappe.get_doc("SL Scout Report", ld.scout_report_reference)
			values.update({
				"site_address_line_1": sr.site_address_line_1,
				"site_address_line_2": sr.site_address_line_2,
				"site_pin_code": sr.site_pin_code,
				"site_city": values["site_city"] or sr.site_city,
				"site_engineer_name": sr.site_engineer_name,
				"site_engineer_number": sr.site_engineer_contact,
				"site_contact_person": sr.site_supervisor_name,
				"site_contact_number": sr.site_supervisor_contact,
				"capacity_kg": sr.estimated_capacity_needed,
				"number_of_floors": sr.proposed_building_height,
				"lift_height": values["lift_height"] or sr.estimated_height_needed,
			})
	if opportunity:
		opp = frappe.db.get_value("Opportunity", opportunity, ["site_name", "lift_type", "estimated_height_m"], as_dict=True)
		lift_types = (frappe.get_meta("Sales Order").get_field("lift_type").options or "").split("\n")
		values.update({
			"site_name": opp.site_name or values.get("site_name"),
			"lift_type": opp.lift_type if opp.lift_type in lift_types else None,
			"lift_height": opp.estimated_height_m or values.get("lift_height"),
		})
	# Lift Model: the quotation's lift item, when it is one (setup/lift_models.py)
	for item in so.get("items") or []:
		if frappe.db.get_value("Item", item.item_code, "item_group") in lift_model_groups():
			values["lift_model"] = item.item_code
			break
	if not so.get("job_name") and values.get("developer_name"):
		values["job_name"] = " — ".join(filter(None, [values["developer_name"], values.get("site_city"), values.get("lift_model")]))

	for field, value in values.items():
		if value and not so.get(field):
			so.set(field, value)


def lift_model_groups():
	lft, rgt = frappe.db.get_value("Item Group", "Lift Models", ["lft", "rgt"]) or (0, 0)
	return frappe.get_all("Item Group", filters={"lft": (">=", lft), "rgt": ("<=", rgt)}, pluck="name")


def _quotations(so):
	return {i.prevdoc_docname for i in so.get("items") or [] if i.get("prevdoc_docname")}


def sales_order_confirm_opportunity(doc, method=None):
	# Sales guide 1.2 step 9: order confirmed -> Opportunity Order Confirmed, Sales Order Number.
	for quotation in _quotations(doc):
		_, opportunity = crm_sources(quotation)
		if opportunity:
			frappe.db.set_value("Opportunity", opportunity, {
				"order_confirmed": 1, "sales_order_number": doc.name, "order_confirmed_date": doc.transaction_date or today(),
			})


def sales_order_unconfirm_opportunity(doc, method=None):
	for opportunity in frappe.get_all("Opportunity", {"sales_order_number": doc.name}, pluck="name"):
		frappe.db.set_value("Opportunity", opportunity, {
			"order_confirmed": 0, "sales_order_number": None, "order_confirmed_date": None,
		})
