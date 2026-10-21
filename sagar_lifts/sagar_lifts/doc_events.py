"""Runtime doc_events for Sagar Lifts (wired in hooks.py)."""

import re

import frappe
from frappe import _
from frappe.utils import cint, flt, getdate, to_timedelta, today
from frappe.utils.user import get_users_with_role

from sagar_lifts.sagar_lifts.amc_calendar import get_pm_month, get_quarter, get_quarter_end


def _depends_on_holds(doc, expression):
	"""Evaluate a form depends-on expression server-side: a bare fieldname, or
	eval:<JS> limited to the ==, !=, &&, ||, ! forms used in this app's setup."""
	if not expression.startswith("eval:"):
		return bool(doc.get(expression))
	js = expression[len("eval:") :]
	py = re.sub(r"!(?!=)", " not ", js.replace("&&", " and ").replace("||", " or "))
	return bool(frappe.safe_eval(py, None, {"doc": doc}))


def validate_conditional_mandatory(doc, method=None):
	# Frappe enforces mandatory_depends_on only in the desk form; this makes the
	# same rules hold for API/portal saves too. Checks are skipped — Frappe
	# never treats an unticked box as missing.
	missing = [
		df.label
		for df in doc.meta.fields
		if df.mandatory_depends_on
		and not df.reqd
		and df.fieldtype != "Check"
		and doc.get(df.fieldname) in (None, "", [])
		and _depends_on_holds(doc, df.mandatory_depends_on)
	]
	if missing:
		frappe.throw(_("Value missing for: {0}").format(", ".join(_(label) for label in missing)), frappe.MandatoryError)


def sales_order_set_job_number(doc, method=None):
	# Default Job Number to the Sales Order's own name (JOB-.####.) but leave it
	# editable — only fill when blank. autoname has already run by validate.
	if not doc.job_number and doc.name:
		doc.job_number = doc.name


def sales_order_validate_contract_value(doc, method=None):
	# "Contract Value" (No-Code Guide 9.1) is the order's own grand total —
	# no separate field, so it can never drift from the actual line items.
	# Required + non-zero, same as any other mandatory field.
	if not doc.grand_total:
		frappe.throw(_("Contract Value (the order total) cannot be zero"))


def sales_order_set_collection_lead(doc, method=None):
	# fetch_from (customer.collection_lead) handles this in the Desk UI, but
	# that's client-side only — this covers script/API-created orders too.
	if doc.customer and not doc.collection_lead:
		doc.collection_lead = frappe.db.get_value("Customer", doc.customer, "collection_lead")


def sales_order_validate_same_collection_lead(doc, method=None):
	# "All lifts under particular developer should be assigned to same CL"
	# (No-Code Guide 2.1 MUST). Customer.collection_lead is the single source
	# of truth (set once the first order under that developer establishes
	# it) — a later order can't silently assign a different CL.
	if not doc.customer or not doc.collection_lead:
		return
	customer_cl = frappe.db.get_value("Customer", doc.customer, "collection_lead")
	if not customer_cl:
		frappe.db.set_value("Customer", doc.customer, "collection_lead", doc.collection_lead)
	elif customer_cl != doc.collection_lead:
		frappe.throw(
			_(
				"Collection Lead for {0} is already {1} — every order under one developer must share "
				"the same Collection Lead."
			).format(frappe.bold(doc.customer), frappe.bold(customer_cl))
		)


def sales_order_validate_milestone_total(doc, method=None):
	# "Payment milestones must add up to 100%. System validates total before
	# saving." (No-Code Guide 2.1 MUST). Auto-calculates Milestone % Total
	# either way, but only blocks save once the order actually carries a
	# contract value to bill against.
	from sagar_lifts.sagar_lifts.setup.sales_order import MILESTONE_COUNT

	doc.contract_value = doc.grand_total
	doc.contract_value_in_words = frappe.utils.money_in_words(doc.contract_value) if doc.contract_value else ""
	total = 0
	for i in range(1, MILESTONE_COUNT + 1):
		percent = flt(doc.get(f"milestone_{i}_percent"))
		doc.set(f"milestone_{i}_amount", flt(doc.contract_value) * percent / 100)
		total += percent
	doc.milestone_percent_total = total
	if doc.grand_total and abs(total - 100) > 0.01:
		frappe.throw(_("Payment milestones must add up to 100% — currently {0}%").format(total))


def sales_order_set_dispatch_cleared(doc, method=None):
	# Same rule the Deployment workflow's Active -> Dispatched transition uses.
	doc.dispatch_cleared = 1 if (doc.advance_received or doc.dispatch_override_approved) else 0
	if doc.dispatch_override_approved and not doc.dispatch_override_by:
		doc.dispatch_override_by = frappe.session.user
		doc.dispatch_override_date = today()


def sales_order_stamp_deployment_status(doc, method=None):
	if doc.has_value_changed("deployment_status"):
		doc.status_last_updated = today()
		doc.status_updated_by = frappe.session.user


def sales_order_set_total_outstanding(doc, method=None):
	doc.total_outstanding = flt(doc.total_billed_to_date) - flt(doc.total_received_to_date)


def sales_order_propagate_outstanding_flag(doc, method=None):
	# "If a breakdown billing PI for any site is overdue: a flag is raised on
	# that specific site AND on all other active sites of the same developer.
	# This is not just for breakdown billing, it should be done for all
	# outstanding bills." (No-Code Guide 6.4/5.4) — fires whenever
	# Outstanding Flag turns on for this order, whoever/whatever set it
	# (this scheduled job, another job, or a person ticking it by hand).
	before = getattr(doc, "_doc_before_save", None)
	was_flagged = before.get("outstanding_flag") if before else 0
	if doc.outstanding_flag and not was_flagged:
		doc.outstanding_flag_date = doc.outstanding_flag_date or today()
	if doc.outstanding_flag and not was_flagged and doc.customer:
		siblings = frappe.get_all(
			"Sales Order",
			filters={
				"customer": doc.customer,
				"name": ["!=", doc.name],
				"deployment_status": ["not in", ("Dismantled", "")],
				"outstanding_flag": 0,
			},
			pluck="name",
		)
		for name in siblings:
			frappe.db.set_value("Sales Order", name, {"outstanding_flag": 1, "outstanding_flag_date": today()})


PRODUCTION_STAGES = [
	"Design & BOM",
	"Frame Fabrication",
	"Cage Assembly",
	"Electrical",
	"Testing",
	"QC Check",
	"Ready for Dispatch",
]


def sales_order_create_project(doc, method=None):
	# Auto-create a Project + one Task per production stage (No-Code Guide
	# Section 3.1) when the order is confirmed. Every order gets one — only
	# New Install gets an actual production order in the guide's own text,
	# but a Project to track the deployment end to end is useful regardless
	# of lift type. Only ever creates one, even across amendments.
	if doc.project:
		return

	project = frappe.get_doc(
		{
			"doctype": "Project",
			# Project.project_name has a native unique constraint — job_name
			# alone isn't guaranteed unique (two orders can share a name), so
			# fold in the Sales Order's own name to guarantee it. Confirmed
			# live: without this, a second order with a matching job_name
			# crashes on submit with an uncaught UniqueValidationError.
			"project_name": f"{doc.job_name} ({doc.name})" if doc.job_name else doc.name,
			"customer": doc.customer,
			"sales_order": doc.name,
			"company": doc.company,
			"expected_start_date": frappe.utils.today(),
		}
	)
	project.insert(ignore_permissions=True)

	for stage in PRODUCTION_STAGES:
		frappe.get_doc(
			{"doctype": "Task", "project": project.name, "subject": stage, "status": "Open"}
		).insert(ignore_permissions=True)

	frappe.db.set_value("Sales Order", doc.name, "project", project.name)


def sales_order_create_bom_skeleton(doc, method=None):
	# New Install only (No-Code Guide 2.4: production order is for New Install
	# only). One BOM per lift model, not per order — orders reusing a model
	# share it, so this only creates one the first time that model is built.
	# BOM.items is a mandatory table, so a components-not-decided-yet shell
	# needs ignore_mandatory to save at all; stays in Draft for someone to
	# fill in and submit once the actual bill of materials is known.
	if doc.lift_type != "Construction" or not doc.lift_model:
		return
	if frappe.db.exists("BOM", {"item": doc.lift_model}):
		return

	bom = frappe.get_doc(
		{
			"doctype": "BOM",
			"item": doc.lift_model,
			"quantity": 1,
			"company": doc.company,
		}
	)
	# Two independent checks both reject an empty items table: the generic
	# framework mandatory-table check (_validate_mandatory, runs regardless
	# of the controller), and BOM's own controller validate() which
	# hard-throws "Raw Materials cannot be blank." Both need bypassing to
	# save a truly-empty shell; this BOM is not production-usable until
	# someone adds items and submits it themselves.
	bom.flags.ignore_validate = True
	bom.insert(ignore_permissions=True, ignore_mandatory=True)


def sales_order_set_amc_start_date(doc, method=None):
	# "Free period starts" at handover: AMC Start Date = Handover Date +
	# Free Maintenance Months. Only fill when blank, and only once Handover
	# Date is actually known — stays editable/overridable either way.
	if doc.handover_date and not doc.amc_start_date:
		doc.amc_start_date = frappe.utils.add_months(doc.handover_date, cint(doc.free_maintenance_months))


DEFAULT_SERVICE_PERSON = "Default Technician"  # created by setup_maintenance_visit_customization


def maintenance_visit_add_purpose(doc, method=None):
	# ERPNext refuses a visit with an empty Purposes table, and the Technician
	# Portal (or any API caller) never sends one — derive the row from the
	# visit itself. before_validate, so it lands before ERPNext's own check.
	if doc.get("purposes"):
		return
	doc.append(
		"purposes",
		{
			"item_code": frappe.db.get_value("Sales Order", doc.job_id, "lift_model") if doc.job_id else None,
			"service_person": DEFAULT_SERVICE_PERSON,
			# Work Done Details is itself mandatory; "-" only keeps ERPNext's
			# row check from masking that clearer error.
			"work_done": doc.work_done_details or "-",
		},
	)


def maintenance_visit_set_quarter(doc, method=None):
	# Quarter/PM Month default from the visit date (Indian FY: Apr-Mar) but stay editable.
	if not doc.mntc_date:
		return
	if not doc.quarter:
		doc.quarter = get_quarter(doc.mntc_date)
	if not doc.pm_month:
		doc.pm_month = get_pm_month(doc.mntc_date)


def maintenance_visit_set_total_hours(doc, method=None):
	if not (doc.mntc_time and doc.visit_time_out):
		doc.total_hours_on_site = 0
		return
	seconds = (to_timedelta(doc.visit_time_out) - to_timedelta(doc.mntc_time)).total_seconds()
	if seconds < 0:  # visit ran past midnight
		seconds += 24 * 3600
	doc.total_hours_on_site = round(seconds / 3600, 2)


def maintenance_visit_set_schedule_variance(doc, method=None):
	doc.variance_from_schedule_days = (
		frappe.utils.date_diff(doc.mntc_date, doc.scheduled_visit_date)
		if doc.mntc_date and doc.scheduled_visit_date
		else 0
	)


def maintenance_visit_set_signature_received(doc, method=None):
	doc.customer_signature_received = 1 if doc.customer_signature else 0


def maintenance_visit_set_breakdown_times(doc, method=None):
	def at(date, time):
		return frappe.utils.get_datetime(f"{date} {time}") if date and time else None

	reported = at(doc.breakdown_reported_date, doc.breakdown_reported_time)
	reached = at(doc.technician_reached_date, doc.technician_reached_time)
	resolved = at(doc.breakdown_resolved_date, doc.breakdown_resolved_time)
	hours = lambda end: round((end - reported).total_seconds() / 3600, 2) if reported and end else 0
	doc.response_time_hours = hours(reached)
	doc.resolution_time_hours = hours(resolved)


def maintenance_visit_validate_date(doc, method=None):
	# "Cannot be a future date" (No-Code Guide 9.2).
	if doc.mntc_date and getdate(doc.mntc_date) > getdate():
		frappe.throw(_("Visit Date cannot be in the future"))


def maintenance_visit_validate_technician(doc, method=None):
	# "Must select from registered technician list" (No-Code Guide 9.2) — the
	# Link field alone doesn't restrict to technicians, so enforce it here.
	if doc.senior_technician and "SL Technician" not in frappe.get_roles(doc.senior_technician):
		frappe.throw(
			_("{0} is not a registered technician (missing the SL Technician role)").format(
				frappe.bold(doc.senior_technician)
			)
		)


def purchase_invoice_set_difference_amount(doc, method=None):
	doc.difference_amount = flt(doc.bill_amount_as_per_contractor) - flt(doc.bill_amount_agreed)


def _submitted_labour_bills(job_id, exclude=None):
	filters = {"bill_type": "Contractor", "job_id": job_id, "docstatus": 1}
	if exclude:
		filters["name"] = ["!=", exclude]
	return sum(flt(v) for v in frappe.get_all("Purchase Invoice", filters=filters, pluck="grand_total"))


def purchase_invoice_set_labour_bill_tracking(doc, method=None):
	if doc.bill_type != "Contractor" or not doc.job_id:
		doc.labour_bill_percent = doc.cumulative_labour_bills_percent = 0
		doc.labour_bill_within_limit = 1
		return
	contract_value = flt(frappe.db.get_value("Sales Order", doc.job_id, "grand_total"))
	others = _submitted_labour_bills(doc.job_id, exclude=doc.name)
	percent = lambda amount: round(amount / contract_value * 100, 2) if contract_value else 0
	doc.labour_bill_percent = percent(flt(doc.grand_total))
	doc.cumulative_labour_bills_percent = percent(others + flt(doc.grand_total))
	doc.labour_bill_within_limit = 1 if doc.cumulative_labour_bills_percent <= 100 else 0


def purchase_invoice_update_order_labour_bills(doc, method=None):
	# Keep the Sales Order's running total in step on submit / cancel.
	if doc.bill_type != "Contractor" or not doc.job_id:
		return
	total = _submitted_labour_bills(doc.job_id)
	contract_value = flt(frappe.db.get_value("Sales Order", doc.job_id, "grand_total"))
	frappe.db.set_value(
		"Sales Order",
		doc.job_id,
		{
			"contractor_labour_bills_amount": total,
			"contractor_labour_bills_percent": round(total / contract_value * 100, 2) if contract_value else 0,
		},
	)


def sales_invoice_set_naming_series(doc, method=None):
	# Invoice Type decides the series — a PI can never pick up an SL number.
	if doc.is_return:
		return
	doc.naming_series = "SL/.###./.SL_FY." if doc.pi_type == "Tax Invoice" else "PI/.###./.SL_FY."


def sales_invoice_set_collection_defaults(doc, method=None):
	if not doc.accounts_caller:
		callers = get_users_with_role("SL Accounts Caller")
		if len(callers) == 1:
			doc.accounts_caller = callers[0]
	if doc.escalated_to_management and not doc.escalation_date:
		doc.escalation_date = today()


def sales_invoice_fill_milestone(doc, method=None):
	# Milestone Name / % default from the Sales Order's Payment Milestones tab.
	if doc.billing_trigger_type != "Milestone" or not (doc.job_id and doc.milestone_number):
		return
	n = doc.milestone_number
	name, percent = frappe.db.get_value("Sales Order", doc.job_id, [f"milestone_{n}_name", f"milestone_{n}_percent"])
	doc.milestone_name = doc.milestone_name or name
	doc.milestone_percent = doc.milestone_percent or percent


def sales_invoice_set_amc_period(doc, method=None):
	if doc.billing_trigger_type != "AMC Quarterly" or not doc.amc_period_from:
		doc.amc_months_billed = 0
		return
	doc.amc_quarter = get_quarter(doc.amc_period_from)
	doc.amc_period_to = doc.amc_period_to or get_quarter_end(doc.amc_period_from)
	start, end = getdate(doc.amc_period_from), getdate(doc.amc_period_to)
	doc.amc_months_billed = max((end.year - start.year) * 12 + end.month - start.month + 1, 0)


def sales_invoice_validate_pi_to_ti(doc, method=None):
	if doc.pi_type != "Tax Invoice":
		return
	if doc.ti_raised_against_full_pi and doc.part_payment_ti:
		frappe.throw(_("A Tax Invoice is either against the full PI or a part payment — not both"))
	if doc.original_pi_number and not doc.pi_date:
		doc.pi_date = frappe.db.get_value(
			"Sales Invoice", {"name": doc.original_pi_number, "pi_type": "Proforma Invoice"}, "posting_date"
		)


def get_outstanding_escalation(due_date, outstanding_amount):
	"""(days past due, escalation level) — mirrors the overdue notification ladder."""
	days = max(frappe.utils.date_diff(today(), due_date), 0) if due_date and flt(outstanding_amount) > 0 else 0
	if days >= 90:
		return days, "Level 4 — Bad Debt"
	if days >= 15:
		return days, "Level 3 — Management"
	if days >= 7:
		return days, "Level 2 — Billing"
	if days >= 1:
		return days, "Level 1 — CL"
	return days, "None"


def sales_invoice_set_outstanding_tracking(doc, method=None):
	if doc.customer:
		amounts = frappe.get_all(
			"Sales Invoice",
			filters={"customer": doc.customer, "docstatus": 1, "outstanding_amount": [">", 0], "name": ["!=", doc.name]},
			pluck="outstanding_amount",
		)
		doc.previous_outstanding_amount = sum(flt(a) for a in amounts)
		doc.previous_pi_outstanding = 1 if amounts else 0
	if doc.outstanding_warning_acknowledged and not doc.outstanding_warning_acknowledged_by:
		doc.outstanding_warning_acknowledged_by = frappe.session.user
	doc.days_outstanding, doc.escalation_level = get_outstanding_escalation(doc.due_date, doc.outstanding_amount)


def sales_invoice_require_outstanding_acknowledgement(doc, method=None):
	if doc.previous_pi_outstanding and not doc.outstanding_warning_acknowledged:
		frappe.throw(
			_("This developer has {0} outstanding on earlier invoices — tick Outstanding Warning Acknowledged to submit").format(
				frappe.format_value(doc.previous_outstanding_amount, {"fieldtype": "Currency"})
			)
		)


def purchase_order_stamp_approval(doc, method=None):
	if doc.po_approval_status == "Approved" and not doc.po_approved_by:
		doc.po_approved_by = frappe.session.user
		doc.po_approval_date = today()


def purchase_receipt_set_job_id(doc, method=None):
	if doc.job_id:
		return
	for po in {row.purchase_order for row in doc.get("items") or [] if row.purchase_order}:
		if job_id := frappe.db.get_value("Purchase Order", po, "job_id"):
			doc.job_id = job_id
			return


def purchase_invoice_set_manufacturing_approval(doc, method=None):
	# Stamp who/when approved a contractor bill the first time it's ticked.
	is_contractor_bill = doc.bill_type == "Contractor"
	if is_contractor_bill and doc.sent_to_manufacturing and not doc.sent_to_manufacturing_date:
		doc.sent_to_manufacturing_date = today()
	if doc.approved_by_manufacturing and doc.manufacturing_rejected:
		frappe.throw(_("A bill can't be both approved and rejected by Manufacturing"))
	if is_contractor_bill and doc.approved_by_manufacturing and not doc.manufacturing_approval_by:
		doc.manufacturing_approval_by = frappe.session.user
		doc.manufacturing_approval_date = today()


def quotation_mark_request_generated(doc, method=None):
	# Sales guide 7.3 last step: SL Quotation Request -> Quotation Generated = Yes, Quotation Number.
	if not doc.get("quotation_request"):
		return
	frappe.db.set_value("SL Quotation Request", doc.quotation_request, {
		"quotation_generated": 1,
		"quotation_reference": doc.name,
		"quotation_date": doc.transaction_date,
		"quotation_valid_till": doc.valid_till,
	})
	if doc.quotation_to == "Lead" and doc.party_name:
		frappe.db.set_value("Lead", doc.party_name, "quotation_number", doc.name)
