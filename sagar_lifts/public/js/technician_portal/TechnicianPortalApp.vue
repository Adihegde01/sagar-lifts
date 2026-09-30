<template>
	<div class="tp-page">
		<header class="tp-header">
			<div>
				<p class="tp-eyebrow">{{ todayLabel }}</p>
				<h1>{{ greeting }}, {{ firstName }}</h1>
			</div>
			<div class="tp-avatar">{{ initials }}</div>
		</header>

		<div class="tp-stats">
			<div class="tp-stat">
				<span class="tp-stat__value">{{ stats.total }}</span>
				<span class="tp-stat__label">Total visits</span>
			</div>
			<div class="tp-stat">
				<span class="tp-stat__value">{{ stats.thisMonth }}</span>
				<span class="tp-stat__label">This month</span>
			</div>
			<div class="tp-stat">
				<span class="tp-stat__value">{{ stats.drafts }}</span>
				<span class="tp-stat__label">Drafts</span>
			</div>
		</div>

		<button class="tp-cta" @click="newVisit">
			<span class="tp-cta__icon">+</span>
			Log a new visit
		</button>

		<section class="tp-section">
			<h2>Recent visits</h2>

			<div v-if="loading" class="tp-skeleton-list">
				<div class="tp-skeleton" v-for="i in 3" :key="i"></div>
			</div>

			<div v-else-if="!visits.length" class="tp-empty">
				<div class="tp-empty__icon">
					<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
						<path d="M9 11l3 3L22 4" />
						<path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11" />
					</svg>
				</div>
				<p class="tp-empty__title">No visits logged yet</p>
				<p class="tp-empty__body">Once you log a PM visit, breakdown call or inspection, it'll show up here.</p>
			</div>

			<ul v-else class="tp-list">
				<li v-for="v in visits" :key="v.name" class="tp-row" @click="openVisit(v.name)">
					<div class="tp-row__icon" :class="iconClass(v.visit_type)">
						<svg v-if="v.visit_type === 'Breakdown'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M13 2 3 14h7l-1 8 10-12h-7l1-8z"/></svg>
						<svg v-else-if="v.visit_type === 'Inspection'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="7"/><path d="m21 21-4.35-4.35"/></svg>
						<svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M14.7 6.3a4 4 0 0 1-5.6 5.6L4 17l3 3 5.1-5.1a4 4 0 0 1 5.6-5.6l-3-3z"/></svg>
					</div>
					<div class="tp-row__body">
						<p class="tp-row__title">{{ v.job_name || v.customer_name || v.name }}</p>
						<p class="tp-row__meta">{{ formatDate(v.mntc_date) }} · {{ v.visit_type || "Visit" }}</p>
					</div>
					<span class="tp-pill" :class="v.docstatus === 1 ? 'tp-pill--done' : 'tp-pill--draft'">
						{{ v.docstatus === 1 ? "Submitted" : "Draft" }}
					</span>
				</li>
			</ul>
		</section>
	</div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from "vue";

const loading = ref(true);
const visits = ref([]);

const fullName = frappe.boot?.user?.full_name || frappe.session.user;
const firstName = computed(() => fullName.split(" ")[0]);
const initials = computed(() =>
	fullName
		.split(" ")
		.map((p) => p[0])
		.slice(0, 2)
		.join("")
		.toUpperCase()
);

const greeting = computed(() => {
	const h = new Date().getHours();
	if (h < 12) return "Good morning";
	if (h < 17) return "Good afternoon";
	return "Good evening";
});

const todayLabel = computed(() =>
	new Date().toLocaleDateString(undefined, { weekday: "long", day: "numeric", month: "long" })
);

const stats = reactive({ total: 0, thisMonth: 0, drafts: 0 });

function computeStats() {
	const now = new Date();
	stats.total = visits.value.length;
	stats.drafts = visits.value.filter((v) => v.docstatus !== 1).length;
	stats.thisMonth = visits.value.filter((v) => {
		if (!v.mntc_date) return false;
		const d = new Date(v.mntc_date);
		return d.getMonth() === now.getMonth() && d.getFullYear() === now.getFullYear();
	}).length;
}

function iconClass(type) {
	if (type === "Breakdown") return "tp-row__icon--breakdown";
	if (type === "Inspection") return "tp-row__icon--inspection";
	return "tp-row__icon--pm";
}

function formatDate(d) {
	if (!d) return "No date";
	return frappe.datetime.str_to_user(d);
}

function newVisit() {
	frappe.new_doc("Maintenance Visit");
}

function openVisit(name) {
	frappe.set_route("maintenance-visit", name);
}

async function loadVisits() {
	loading.value = true;
	try {
		const r = await frappe.call({
			method: "frappe.client.get_list",
			args: {
				doctype: "Maintenance Visit",
				fields: ["name", "mntc_date", "customer_name", "visit_type", "docstatus", "job_name"],
				order_by: "mntc_date desc",
				limit_page_length: 50,
			},
		});
		visits.value = r.message || [];
		computeStats();
	} finally {
		loading.value = false;
	}
}

onMounted(loadVisits);
</script>

<style scoped>
.tp-page {
	--tp-bg: #f5f6f8;
	--tp-surface: #ffffff;
	--tp-border: #e6e8ec;
	--tp-ink: #16181d;
	--tp-ink-soft: #6b7280;
	--tp-accent: #2f6fe4;
	--tp-accent-soft: #eaf1ff;
	--tp-amber: #dd8a1f;
	--tp-amber-soft: #fbf0dc;
	--tp-green: #1f9d63;
	--tp-green-soft: #e6f7ee;
	--tp-radius: 16px;
	--tp-shadow: 0 1px 2px rgba(20, 22, 30, 0.04), 0 8px 24px -14px rgba(20, 22, 30, 0.18);

	font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
	background: var(--tp-bg);
	color: var(--tp-ink);
	min-height: 100vh;
	max-width: 560px;
	margin: 0 auto;
	padding: 24px 18px 60px;
	box-sizing: border-box;
}
.tp-page * { box-sizing: border-box; }

.tp-header {
	display: flex;
	align-items: flex-start;
	justify-content: space-between;
	margin-bottom: 22px;
}
.tp-eyebrow {
	margin: 0 0 4px;
	font-size: 12px;
	font-weight: 600;
	letter-spacing: 0.06em;
	text-transform: uppercase;
	color: var(--tp-ink-soft);
}
.tp-header h1 {
	margin: 0;
	font-size: 22px;
	font-weight: 700;
	letter-spacing: -0.01em;
}
.tp-avatar {
	width: 44px;
	height: 44px;
	border-radius: 50%;
	background: var(--tp-accent);
	color: #fff;
	display: flex;
	align-items: center;
	justify-content: center;
	font-weight: 600;
	font-size: 14px;
	flex-shrink: 0;
	box-shadow: var(--tp-shadow);
}

.tp-stats {
	display: grid;
	grid-template-columns: repeat(3, 1fr);
	gap: 10px;
	margin-bottom: 20px;
}
.tp-stat {
	background: var(--tp-surface);
	border: 1px solid var(--tp-border);
	border-radius: var(--tp-radius);
	padding: 14px 10px;
	text-align: center;
}
.tp-stat__value {
	display: block;
	font-size: 22px;
	font-weight: 700;
	font-variant-numeric: tabular-nums;
}
.tp-stat__label {
	display: block;
	font-size: 11px;
	color: var(--tp-ink-soft);
	margin-top: 2px;
}

.tp-cta {
	width: 100%;
	display: flex;
	align-items: center;
	justify-content: center;
	gap: 8px;
	background: var(--tp-ink);
	color: #fff;
	border: none;
	border-radius: 14px;
	padding: 16px;
	font-size: 15px;
	font-weight: 600;
	cursor: pointer;
	box-shadow: var(--tp-shadow);
	transition: transform 0.15s ease, opacity 0.15s ease;
	margin-bottom: 28px;
}
.tp-cta:active {
	transform: scale(0.98);
	opacity: 0.9;
}
.tp-cta__icon {
	font-size: 18px;
	line-height: 1;
}

.tp-section h2 {
	font-size: 14px;
	font-weight: 600;
	color: var(--tp-ink-soft);
	text-transform: uppercase;
	letter-spacing: 0.04em;
	margin: 0 0 12px;
}

.tp-list {
	list-style: none;
	margin: 0;
	padding: 0;
	display: flex;
	flex-direction: column;
	gap: 10px;
}
.tp-row {
	display: flex;
	align-items: center;
	gap: 12px;
	background: var(--tp-surface);
	border: 1px solid var(--tp-border);
	border-radius: var(--tp-radius);
	padding: 12px 14px;
	cursor: pointer;
	transition: border-color 0.15s ease, transform 0.15s ease;
}
.tp-row:active {
	transform: scale(0.99);
	border-color: var(--tp-accent);
}
.tp-row__icon {
	width: 38px;
	height: 38px;
	border-radius: 10px;
	display: flex;
	align-items: center;
	justify-content: center;
	flex-shrink: 0;
}
.tp-row__icon svg { width: 18px; height: 18px; }
.tp-row__icon--pm { background: var(--tp-accent-soft); color: var(--tp-accent); }
.tp-row__icon--breakdown { background: #fdeceb; color: #d9432f; }
.tp-row__icon--inspection { background: var(--tp-amber-soft); color: var(--tp-amber); }

.tp-row__body { flex: 1; min-width: 0; }
.tp-row__title {
	margin: 0;
	font-size: 14.5px;
	font-weight: 600;
	white-space: nowrap;
	overflow: hidden;
	text-overflow: ellipsis;
}
.tp-row__meta {
	margin: 2px 0 0;
	font-size: 12.5px;
	color: var(--tp-ink-soft);
}

.tp-pill {
	flex-shrink: 0;
	font-size: 11px;
	font-weight: 600;
	padding: 4px 9px;
	border-radius: 999px;
}
.tp-pill--draft { background: var(--tp-amber-soft); color: var(--tp-amber); }
.tp-pill--done { background: var(--tp-green-soft); color: var(--tp-green); }

.tp-empty {
	background: var(--tp-surface);
	border: 1px dashed var(--tp-border);
	border-radius: var(--tp-radius);
	padding: 36px 20px;
	text-align: center;
}
.tp-empty__icon {
	width: 44px;
	height: 44px;
	margin: 0 auto 12px;
	border-radius: 50%;
	background: var(--tp-accent-soft);
	color: var(--tp-accent);
	display: flex;
	align-items: center;
	justify-content: center;
}
.tp-empty__icon svg { width: 20px; height: 20px; }
.tp-empty__title { margin: 0 0 4px; font-weight: 600; font-size: 14.5px; }
.tp-empty__body { margin: 0; font-size: 13px; color: var(--tp-ink-soft); max-width: 32ch; margin-inline: auto; }

.tp-skeleton-list { display: flex; flex-direction: column; gap: 10px; }
.tp-skeleton {
	height: 64px;
	border-radius: var(--tp-radius);
	background: linear-gradient(90deg, var(--tp-surface) 25%, #eef0f3 37%, var(--tp-surface) 63%);
	background-size: 400% 100%;
	animation: tp-shimmer 1.4s ease infinite;
	border: 1px solid var(--tp-border);
}
@keyframes tp-shimmer {
	0% { background-position: 100% 50%; }
	100% { background-position: 0 50%; }
}
</style>
