# Copyright (c) 2026, Sagar Lifts and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class SLQuotationRequest(Document):
	def on_submit(self):
		if self.lead_reference:
			frappe.db.set_value("Lead", self.lead_reference, "quotation_request_submitted", 1)


@frappe.whitelist()
def get_lead_values(lead):
	"""Quotation Request fields pre-filled from the Lead and its Scout Report
	(sales guide 1.2 step 4) — the form only fills the ones still empty."""
	frappe.has_permission("Lead", "read", lead, throw=True)
	ld = frappe.get_doc("Lead", lead)
	values = {
		"developer_name": ld.company_name or ld.lead_name,
		"developer_company": ld.company_name,
		"developer_contact_name": ld.lead_name,
		"developer_contact_number": ld.mobile_no or ld.phone,
		"developer_email": ld.email_id,
		"site_name": ld.get("site_name"),
		"site_city": ld.get("site_city") or ld.city,
		"number_of_lifts": ld.get("estimated_lifts_required"),
		"required_height": ld.get("estimated_height_m"),
		"approximate_budget": ld.get("estimated_contract_value"),
		"number_of_follow_up_calls_done": ld.get("follow_up_count"),
		"previous_interactions_summary": ld.get("caller_remarks"),
		"scout_report_reference": ld.get("scout_report_reference"),
		"caller_involved": 1 if ld.get("assigned_caller") else 0,
		"caller_name": ld.get("assigned_caller"),
		"senior_involved": 1 if ld.get("assigned_senior") else 0,
		"senior_name": ld.get("assigned_senior"),
	}
	if values["scout_report_reference"]:
		sr = frappe.get_doc("SL Scout Report", values["scout_report_reference"])
		values.update({
			"site_address": "\n".join(filter(None, [sr.site_address_line_1, sr.site_address_line_2, sr.site_city, sr.site_pin_code])),
			"developer_office_address": sr.developer_office_address,
			"required_capacity": sr.estimated_capacity_needed,
			"budget_discussed": sr.budget_discussed,
			"competitor_rates_known": 1 if sr.competitor_rate else 0,
			"competitor_rate": sr.competitor_rate,
			"scouter_involved": 1,
			"scouter_name": sr.scouter_name,
		})
		values["number_of_lifts"] = values["number_of_lifts"] or sr.estimated_number_of_lifts
		values["required_height"] = values["required_height"] or sr.estimated_height_needed
		values["approximate_budget"] = values["approximate_budget"] or sr.approximate_budget
	return {k: v for k, v in values.items() if v}
