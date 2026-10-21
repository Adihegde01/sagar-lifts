# Copyright (c) 2026, Sagar Lifts and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class SLScoutReport(Document):
	def on_submit(self):
		# Sales guide 1.2 step 2: every submitted scout report becomes a CRM Lead.
		# An amended report takes over its cancelled original's Lead instead of
		# creating a duplicate.
		lead = self.lead_reference or (
			self.amended_from and frappe.db.get_value("Lead", {"scout_report_reference": self.amended_from})
		)
		if lead:
			frappe.db.set_value("Lead", lead, "scout_report_reference", self.name)
		else:
			lead = frappe.get_doc({"doctype": "Lead", **self.lead_values()}).insert(ignore_permissions=True).name
			frappe.msgprint(
				frappe._("Lead {0} created").format(frappe.utils.get_link_to_form("Lead", lead)), alert=True
			)
		self.db_set({"lead_created": 1, "lead_reference": lead})

	def lead_values(self):
		# "A — Hot Lead" -> "A Hot" (Lead's Lead Quality options)
		grade, _, label = (self.lead_quality_rating or "").partition(" — ")
		return {
			"company_name": self.developer_builder_name,
			"first_name": self.decision_maker_name or self.developer_builder_name,
			"mobile_no": self.decision_maker_contact or self.site_supervisor_contact,
			"email_id": self.decision_maker_email,
			"city": self.site_city,
			"utm_source": "Scouting",
			"scout_report_reference": self.name,
			"assigned_caller": self.assigned_to_caller,
			"lead_quality": f"{grade} {label.split()[0]}" if label else None,
			"site_name": self.site_name,
			"site_city": self.site_city,
			"proposed_building_height_floors": self.proposed_building_height,
			"estimated_lifts_required": self.estimated_number_of_lifts,
			"estimated_height_m": self.estimated_height_needed,
			"competitor_at_site": self.competitor_lift_present_on_site,
			"competitor_name": self.competitor_name,
			"caller_remarks": self.special_notes_for_calling_team,
		}
