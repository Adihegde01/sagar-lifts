"""Runtime doc_events for Sagar Lifts (wired in hooks.py)."""

import frappe
from frappe import _
from frappe.utils import cint, flt, getdate

from sagar_lifts.sagar_lifts.amc_calendar import get_pm_month, get_quarter


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
	total = sum(flt(doc.get(f"milestone_{i}_percent")) for i in range(1, 5))
	doc.milestone_percent_total = total
	if doc.grand_total and abs(total - 100) > 0.01:
		frappe.throw(_("Payment milestones must add up to 100% — currently {0}%").format(total))


def sales_order_propagate_outstanding_flag(doc, method=None):
	# "If a breakdown billing PI for any site is overdue: a flag is raised on
	# that specific site AND on all other active sites of the same developer.
	# This is not just for breakdown billing, it should be done for all
	# outstanding bills." (No-Code Guide 6.4/5.4) — fires whenever
	# Outstanding Flag turns on for this order, whoever/whatever set it
	# (this scheduled job, another job, or a person ticking it by hand).
	before = getattr(doc, "_doc_before_save", None)
	was_flagged = before.get("outstanding_flag") if before else 0
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
			frappe.db.set_value("Sales Order", name, "outstanding_flag", 1)


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


def maintenance_visit_set_quarter(doc, method=None):
	# Quarter/PM Month default from the visit date (Indian FY: Apr-Mar) but stay editable.
	if not doc.mntc_date:
		return
	if not doc.quarter:
		doc.quarter = get_quarter(doc.mntc_date)
	if not doc.pm_month:
		doc.pm_month = get_pm_month(doc.mntc_date)


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
