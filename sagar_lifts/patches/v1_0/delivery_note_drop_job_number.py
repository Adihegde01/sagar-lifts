from sagar_lifts.sagar_lifts.setup.job_id import setup_job_id_links


def execute():
	# Re-run setup_job_id_links() to drop Delivery Note's redundant Job
	# Number field on sites where the original job_id_links patch already
	# ran (before this field was dropped).
	setup_job_id_links()
