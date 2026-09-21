"""Self-check for amc_calendar.py.

Run: bench --site <site> execute sagar_lifts.sagar_lifts.test_amc_calendar.demo
"""

from frappe.utils import getdate

from sagar_lifts.sagar_lifts.amc_calendar import (
	get_last_completed_quarter,
	get_pi_deadline,
	get_pm_month,
	get_quarter,
	get_quarter_end,
)


def demo():
	# every month lands in the right quarter/position, per the AMC Billing Calendar
	assert get_quarter("2026-04-01") == "Q1"
	assert get_quarter("2026-06-30") == "Q1"
	assert get_quarter("2026-07-01") == "Q2"
	assert get_quarter("2026-09-30") == "Q2"
	assert get_quarter("2026-10-01") == "Q3"
	assert get_quarter("2026-12-31") == "Q3"
	assert get_quarter("2027-01-01") == "Q4"
	assert get_quarter("2027-03-31") == "Q4"
	assert get_pm_month("2026-04-01") == "Month 1"
	assert get_pm_month("2026-05-15") == "Month 2"
	assert get_pm_month("2026-06-30") == "Month 3"

	# quarter ends and PI deadlines match the table exactly
	assert get_quarter_end("2026-05-01") == getdate("2026-06-30")
	assert get_quarter_end("2026-12-15") == getdate("2026-12-31")
	assert get_pi_deadline("2026-05-01") == getdate("2026-07-05")
	assert get_pi_deadline("2026-12-15") == getdate("2027-01-05")

	# deadline day itself is not yet overdue; the day after is
	q, qend, deadline = get_last_completed_quarter("2026-07-05")
	assert (q, qend, deadline) == ("Q1", getdate("2026-06-30"), getdate("2026-07-05"))
	q, qend, deadline = get_last_completed_quarter("2026-07-06")
	assert (q, qend, deadline) == ("Q1", getdate("2026-06-30"), getdate("2026-07-05"))

	# FY year rollover: Q3 (Oct-Dec) deadline falls in January of the next year
	q, qend, deadline = get_last_completed_quarter("2027-01-06")
	assert (q, qend, deadline) == ("Q3", getdate("2026-12-31"), getdate("2027-01-05"))

	print("amc_calendar: all checks passed")


if __name__ == "__main__":
	demo()
