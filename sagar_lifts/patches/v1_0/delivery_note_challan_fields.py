from sagar_lifts.sagar_lifts.setup.job_id import setup_job_id_links
from sagar_lifts.sagar_lifts.setup.delivery_note import setup_delivery_note_customization


def execute():
	setup_job_id_links()
	setup_delivery_note_customization()
