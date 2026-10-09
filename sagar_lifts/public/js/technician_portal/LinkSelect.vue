<template>
	<div class="ls-wrap">
		<input
			class="ls-input"
			:class="{ 'ls-input--invalid': invalid }"
			type="text"
			:placeholder="placeholder"
			v-model="query"
			@focus="onFocus"
			@input="onInput"
			@blur="onBlur"
		/>
		<div v-if="open && results.length" class="ls-menu">
			<button
				v-for="r in results"
				:key="r.value"
				type="button"
				class="ls-option"
				@mousedown.prevent="select(r)"
			>
				<span class="ls-option__title">{{ r.label }}</span>
				<span v-if="r.sub" class="ls-option__sub">{{ r.sub }}</span>
			</button>
		</div>
		<div v-else-if="open && searched && !loading" class="ls-menu ls-menu--empty">No matches</div>
	</div>
</template>

<script setup>
// Frappe's own Link field is a jQuery/awesomplete widget bound to a real
// <input> Desk creates for the form — not something a Vue component can
// reach into from outside the form it builds, so this re-implements just
// the "search as you type, pick one" behaviour against the same
// frappe.client.get_list search API the native control itself calls.
import { ref, watch } from "vue";

const props = defineProps({
	doctype: { type: String, required: true },
	titleField: { type: String, default: "name" },
	subField: { type: String, default: "" },
	filters: { type: Object, default: () => ({}) },
	modelValue: { type: String, default: "" },
	modelLabel: { type: String, default: "" },
	placeholder: { type: String, default: "Search…" },
	invalid: { type: Boolean, default: false },
});
const emit = defineEmits(["update:modelValue", "update:modelLabel"]);

const query = ref(props.modelLabel || props.modelValue || "");
const results = ref([]);
const open = ref(false);
const loading = ref(false);
const searched = ref(false);
let debounceTimer = null;

watch(
	() => props.modelLabel,
	(v) => {
		if (v !== undefined && v !== query.value) query.value = v || "";
	}
);

async function search(text) {
	loading.value = true;
	try {
		const fields = ["name"];
		if (props.titleField !== "name") fields.push(props.titleField);
		if (props.subField) fields.push(props.subField);
		const filters = { ...props.filters };
		if (text) {
			filters[props.titleField] = ["like", `%${text}%`];
		}
		const r = await frappe.call({
			method: "frappe.client.get_list",
			args: { doctype: props.doctype, fields, filters, limit_page_length: 20 },
		});
		results.value = (r.message || []).map((row) => ({
			value: row.name,
			label: row[props.titleField] || row.name,
			sub: props.subField ? row[props.subField] : "",
		}));
	} finally {
		loading.value = false;
		searched.value = true;
	}
}

function onFocus() {
	open.value = true;
	search(query.value);
}

function onInput() {
	emit("update:modelValue", "");
	clearTimeout(debounceTimer);
	debounceTimer = setTimeout(() => search(query.value), 250);
}

function onBlur() {
	// Let a mousedown on an option register (it fires before blur's click
	// would've closed the menu) before actually closing it.
	setTimeout(() => (open.value = false), 120);
}

function select(r) {
	query.value = r.label;
	open.value = false;
	emit("update:modelValue", r.value);
	emit("update:modelLabel", r.label);
}
</script>

<style scoped>
.ls-wrap { position: relative; }
.ls-input {
	width: 100%;
	font: inherit;
	padding: 11px 13px;
	border-radius: 10px;
	border: 1.5px solid var(--tp-border, #e6e8ec);
	background: #fff;
	color: var(--tp-ink, #16181d);
}
.ls-input:focus { outline: none; border-color: var(--tp-accent, #2f6fe4); }
.ls-input--invalid { border-color: #d9432f; }
.ls-menu {
	position: absolute;
	z-index: 20;
	top: calc(100% + 4px);
	left: 0;
	right: 0;
	max-height: 240px;
	overflow-y: auto;
	background: #fff;
	border: 1px solid var(--tp-border, #e6e8ec);
	border-radius: 10px;
	box-shadow: 0 10px 28px -10px rgba(20, 22, 30, 0.25);
	padding: 4px;
}
.ls-menu--empty {
	padding: 10px 12px;
	font-size: 13px;
	color: var(--tp-ink-soft, #6b7280);
}
.ls-option {
	display: flex;
	flex-direction: column;
	width: 100%;
	text-align: left;
	background: none;
	border: none;
	padding: 8px 10px;
	border-radius: 7px;
	cursor: pointer;
	font: inherit;
}
.ls-option:hover { background: var(--tp-accent-soft, #eaf1ff); }
.ls-option__title { font-size: 13.5px; font-weight: 500; }
.ls-option__sub { font-size: 11.5px; color: var(--tp-ink-soft, #6b7280); }
</style>
