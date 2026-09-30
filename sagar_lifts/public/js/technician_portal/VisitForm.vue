<template>
	<div class="vf">
		<header class="vf-header">
			<button type="button" class="vf-back" @click="emit('cancel')">← My visits</button>
			<h1>Log a visit</h1>
		</header>

		<section class="vf-section">
			<p class="vf-label">Job</p>
			<LinkSelect
				doctype="Sales Order"
				title-field="job_name"
				sub-field="name"
				placeholder="Search job / Sales Order…"
				:filters="{ docstatus: 1 }"
				v-model="doc.job_id"
				v-model:model-label="labels.job_id"
				:invalid="!!errors.job_id"
				@update:model-value="onJobPicked"
			/>
			<p v-if="errors.job_id" class="vf-error">{{ errors.job_id }}</p>
		</section>

		<section class="vf-section vf-grid2">
			<div>
				<p class="vf-label">Customer</p>
				<LinkSelect
					doctype="Customer"
					title-field="customer_name"
					placeholder="Search customer…"
					v-model="doc.customer"
					v-model:model-label="labels.customer"
					:invalid="!!errors.customer"
				/>
				<p v-if="errors.customer" class="vf-error">{{ errors.customer }}</p>
			</div>
			<div>
				<p class="vf-label">Company</p>
				<LinkSelect
					doctype="Company"
					title-field="name"
					placeholder="Search company…"
					v-model="doc.company"
					v-model:model-label="labels.company"
					:invalid="!!errors.company"
				/>
				<p v-if="errors.company" class="vf-error">{{ errors.company }}</p>
			</div>
		</section>

		<section class="vf-section vf-grid2">
			<div>
				<p class="vf-label">Maintenance date</p>
				<input type="date" class="vf-input" v-model="doc.mntc_date" @change="onDateChange" />
			</div>
			<div>
				<p class="vf-label">Maintenance time</p>
				<input type="time" class="vf-input" v-model="doc.mntc_time" />
			</div>
		</section>

		<section class="vf-section vf-grid2">
			<div>
				<p class="vf-label">Completion status</p>
				<select class="vf-input" :class="{ 'vf-input--invalid': errors.completion_status }" v-model="doc.completion_status">
					<option value="">Select…</option>
					<option value="Partially Completed">Partially Completed</option>
					<option value="Fully Completed">Fully Completed</option>
				</select>
				<p v-if="errors.completion_status" class="vf-error">{{ errors.completion_status }}</p>
			</div>
			<div>
				<p class="vf-label">Maintenance type</p>
				<select class="vf-input" v-model="doc.maintenance_type">
					<option value="Scheduled">Scheduled</option>
					<option value="Unscheduled">Unscheduled</option>
					<option value="Breakdown">Breakdown</option>
				</select>
			</div>
		</section>

		<div class="vf-divider">PM Visit</div>

		<section class="vf-section">
			<p class="vf-label">Visit type</p>
			<div class="vf-segment">
				<button
					v-for="opt in visitTypes"
					:key="opt"
					type="button"
					class="vf-segment__btn"
					:class="{ active: doc.visit_type === opt }"
					@click="doc.visit_type = opt"
				>
					{{ opt }}
				</button>
			</div>
			<p v-if="errors.visit_type" class="vf-error">{{ errors.visit_type }}</p>
		</section>

		<section class="vf-section">
			<p class="vf-label">Senior technician</p>
			<LinkSelect
				doctype="User"
				title-field="full_name"
				sub-field="name"
				placeholder="Search technician…"
				v-model="doc.senior_technician"
				v-model:model-label="labels.senior_technician"
				:invalid="!!errors.senior_technician"
			/>
			<p v-if="errors.senior_technician" class="vf-error">{{ errors.senior_technician }}</p>
		</section>

		<section class="vf-section vf-grid2">
			<div>
				<p class="vf-label">Spares used</p>
				<select class="vf-input" v-model="doc.spares_used">
					<option value="No Spares Used">No Spares Used</option>
					<option value="Spares Used">Spares Used</option>
				</select>
			</div>
			<div class="vf-check-row">
				<label class="vf-check">
					<input type="checkbox" v-model="doc.chargeable_visit" />
					Chargeable visit
				</label>
			</div>
		</section>

		<section class="vf-section vf-grid2">
			<div>
				<p class="vf-label">Quarter</p>
				<select class="vf-input" v-model="doc.quarter">
					<option value="">—</option>
					<option v-for="q in ['Q1', 'Q2', 'Q3', 'Q4']" :key="q" :value="q">{{ q }}</option>
				</select>
			</div>
			<div>
				<p class="vf-label">PM month</p>
				<select class="vf-input" v-model="doc.pm_month">
					<option value="">—</option>
					<option v-for="m in ['Month 1', 'Month 2', 'Month 3']" :key="m" :value="m">{{ m }}</option>
				</select>
			</div>
		</section>

		<section class="vf-section">
			<p class="vf-label">Findings and remarks</p>
			<textarea
				class="vf-input vf-textarea"
				:class="{ 'vf-input--invalid': errors.findings_and_remarks }"
				placeholder='"All OK" still needs to be typed — can&rsquo;t be left blank'
				v-model="doc.findings_and_remarks"
			></textarea>
			<p v-if="errors.findings_and_remarks" class="vf-error">{{ errors.findings_and_remarks }}</p>
		</section>

		<section class="vf-section">
			<p class="vf-label">Customer signature</p>
			<SignaturePad ref="padRef" />
			<p v-if="errors.customer_signature" class="vf-error">{{ errors.customer_signature }}</p>
		</section>

		<p v-if="submitError" class="vf-submit-error">{{ submitError }}</p>

		<div class="vf-actions">
			<button type="button" class="vf-btn vf-btn--ghost" :disabled="saving" @click="save(false)">Save draft</button>
			<button type="button" class="vf-btn vf-btn--primary" :disabled="saving" @click="save(true)">
				{{ saving ? "Submitting…" : "Submit visit" }}
			</button>
		</div>
	</div>
</template>

<script setup>
import { reactive, ref } from "vue";
import LinkSelect from "./LinkSelect.vue";
import SignaturePad from "./SignaturePad.vue";

const emit = defineEmits(["cancel", "saved"]);

const visitTypes = ["Preventive Maintenance", "Breakdown", "Inspection"];

function todayISO() {
	const d = new Date();
	return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
}

// Indian FY (Apr-Mar), matching doc_events.maintenance_visit_set_quarter on
// the server — mirrored here just so it's already filled in before save,
// not because the server doesn't also set it.
function quarterFor(dateStr) {
	if (!dateStr) return { quarter: "", pm_month: "" };
	const m = new Date(dateStr).getMonth(); // 0-11
	const fyMonth = (m + 9) % 12; // 0 = April
	const qIndex = Math.floor(fyMonth / 3); // 0-3
	const monthInQuarter = (fyMonth % 3) + 1; // 1-3
	return { quarter: `Q${qIndex + 1}`, pm_month: `Month ${monthInQuarter}` };
}

const doc = reactive({
	job_id: "",
	customer: "",
	company: "",
	mntc_date: todayISO(),
	mntc_time: "",
	completion_status: "",
	maintenance_type: "Unscheduled",
	visit_type: "",
	senior_technician: "",
	spares_used: "No Spares Used",
	chargeable_visit: false,
	quarter: "",
	pm_month: "",
	findings_and_remarks: "",
});
const labels = reactive({ job_id: "", customer: "", company: "", senior_technician: "" });
const errors = reactive({});
const saving = ref(false);
const submitError = ref("");
const padRef = ref(null);

// Prefill quarter/PM month from today's date on first load.
Object.assign(doc, quarterFor(doc.mntc_date));

function onDateChange() {
	Object.assign(doc, quarterFor(doc.mntc_date));
}

async function onJobPicked(jobId) {
	if (!jobId) return;
	try {
		const r = await frappe.db.get_value("Sales Order", jobId, ["customer", "company"]);
		const v = r.message || {};
		if (v.customer && !doc.customer) {
			doc.customer = v.customer;
			const cr = await frappe.db.get_value("Customer", v.customer, "customer_name");
			labels.customer = cr.message?.customer_name || v.customer;
		}
		if (v.company && !doc.company) {
			doc.company = v.company;
			labels.company = v.company;
		}
	} catch (e) {
		// Non-fatal — technician can still fill Customer/Company by hand.
	}
}

function validate() {
	Object.keys(errors).forEach((k) => delete errors[k]);
	if (!doc.job_id) errors.job_id = "Pick the job this visit is for.";
	if (!doc.customer) errors.customer = "Required.";
	if (!doc.company) errors.company = "Required.";
	if (!doc.completion_status) errors.completion_status = "Required.";
	if (!doc.visit_type) errors.visit_type = "Pick a visit type.";
	if (!doc.senior_technician) errors.senior_technician = "Required.";
	if (!doc.findings_and_remarks || !doc.findings_and_remarks.trim())
		errors.findings_and_remarks = '"All OK" still needs to be typed — can\'t be blank.';
	if (!padRef.value || padRef.value.isEmpty())
		errors.customer_signature = "Customer signature is required.";
	return Object.keys(errors).length === 0;
}

async function save(submit) {
	submitError.value = "";
	if (!validate()) {
		submitError.value = "Fix the highlighted fields before saving.";
		return;
	}
	saving.value = true;
	try {
		const payload = {
			doctype: "Maintenance Visit",
			naming_series: "MAT-MVS-.YYYY.-",
			status: "Draft",
			...doc,
			customer_signature: padRef.value.toDataURL(),
		};
		const r = await frappe.call({ method: "frappe.client.insert", args: { doc: payload } });
		const name = r.message.name;
		if (submit) {
			await frappe.call({ method: "frappe.client.submit", args: { doc: r.message } });
		}
		emit("saved", { name });
	} catch (e) {
		submitError.value = (e.responseJSON && e.responseJSON.exception) || e.message || "Could not save the visit.";
	} finally {
		saving.value = false;
	}
}
</script>

<style scoped>
.vf { padding-bottom: 40px; }
.vf-header {
	display: flex;
	flex-direction: column;
	align-items: flex-start;
	gap: 6px;
	margin-bottom: 22px;
}
.vf-back {
	background: none;
	border: none;
	padding: 0;
	font-size: 13px;
	font-weight: 600;
	color: var(--tp-ink-soft, #6b7280);
	cursor: pointer;
}
.vf-header h1 { margin: 0; font-size: 21px; font-weight: 700; letter-spacing: -0.01em; }

.vf-section { margin-bottom: 18px; }
.vf-grid2 { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
@media (max-width: 480px) {
	.vf-grid2 { grid-template-columns: 1fr; }
}

.vf-label {
	margin: 0 0 6px;
	font-size: 12.5px;
	font-weight: 600;
	color: var(--tp-ink-soft, #6b7280);
}
.vf-input {
	width: 100%;
	font: inherit;
	font-size: 14.5px;
	padding: 11px 13px;
	border-radius: 10px;
	border: 1.5px solid var(--tp-border, #e6e8ec);
	background: #fff;
	color: var(--tp-ink, #16181d);
	appearance: none;
}
.vf-input:focus { outline: none; border-color: var(--tp-accent, #2f6fe4); }
.vf-input--invalid { border-color: #d9432f; }
.vf-textarea { min-height: 110px; resize: vertical; }

.vf-error { margin: 6px 0 0; font-size: 12px; color: #d9432f; }
.vf-submit-error {
	margin: 0 0 14px;
	padding: 10px 13px;
	border-radius: 10px;
	background: #fdeceb;
	color: #d9432f;
	font-size: 13px;
}

.vf-divider {
	margin: 26px 0 16px;
	font-size: 12px;
	font-weight: 700;
	letter-spacing: 0.06em;
	text-transform: uppercase;
	color: var(--tp-ink-soft, #6b7280);
	border-top: 1px solid var(--tp-border, #e6e8ec);
	padding-top: 16px;
}

.vf-segment { display: flex; gap: 8px; flex-wrap: wrap; }
.vf-segment__btn {
	flex: 1 1 auto;
	padding: 10px 12px;
	border-radius: 10px;
	border: 1.5px solid var(--tp-border, #e6e8ec);
	background: #fff;
	color: var(--tp-ink, #16181d);
	font: inherit;
	font-size: 13.5px;
	font-weight: 500;
	cursor: pointer;
}
.vf-segment__btn.active {
	background: var(--tp-ink, #16181d);
	border-color: var(--tp-ink, #16181d);
	color: #fff;
}

.vf-check-row { display: flex; align-items: flex-end; padding-bottom: 2px; }
.vf-check { display: flex; align-items: center; gap: 8px; font-size: 13.5px; cursor: pointer; }

.vf-actions {
	display: flex;
	gap: 10px;
	margin-top: 26px;
	position: sticky;
	bottom: 12px;
}
.vf-btn {
	flex: 1;
	padding: 14px;
	border-radius: 12px;
	font-size: 14.5px;
	font-weight: 600;
	border: none;
	cursor: pointer;
}
.vf-btn:disabled { opacity: 0.6; cursor: default; }
.vf-btn--ghost {
	background: #fff;
	border: 1.5px solid var(--tp-border, #e6e8ec);
	color: var(--tp-ink, #16181d);
}
.vf-btn--primary {
	background: var(--tp-ink, #16181d);
	color: #fff;
	box-shadow: 0 8px 20px -10px rgba(20, 22, 30, 0.5);
}
</style>
