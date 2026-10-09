<template>
	<div class="sp-wrap">
		<canvas
			ref="canvasEl"
			class="sp-canvas"
			@pointerdown="start"
			@pointermove="move"
			@pointerup="end"
			@pointerleave="end"
			@pointercancel="end"
		></canvas>
		<div v-if="empty" class="sp-hint">Sign here</div>
		<button type="button" class="sp-clear" @click="clear" :disabled="empty">Clear</button>
	</div>
</template>

<script setup>
// Hand-rolled — there's no drop-in signature-pad library in this bench's
// node_modules, and pulling one in for ~40 lines of canvas pointer-event
// handling isn't worth the new dependency. Exposes clear()/isEmpty()/
// toDataURL() so the parent form can read the result on submit, matching
// how the native "Signature" fieldtype stores a PNG data URI.
import { ref, onMounted, onBeforeUnmount } from "vue";

const canvasEl = ref(null);
const empty = ref(true);
let ctx = null;
let drawing = false;
let lastX = 0;
let lastY = 0;

function resize() {
	const canvas = canvasEl.value;
	if (!canvas) return;
	const ratio = window.devicePixelRatio || 1;
	const rect = canvas.getBoundingClientRect();
	const prev = empty.value ? null : canvas.toDataURL();
	canvas.width = rect.width * ratio;
	canvas.height = rect.height * ratio;
	ctx = canvas.getContext("2d");
	ctx.scale(ratio, ratio);
	ctx.lineWidth = 2.2;
	ctx.lineCap = "round";
	ctx.lineJoin = "round";
	ctx.strokeStyle = "#16181d";
	if (prev) {
		const img = new Image();
		img.onload = () => ctx.drawImage(img, 0, 0, rect.width, rect.height);
		img.src = prev;
	}
}

function pos(e) {
	const rect = canvasEl.value.getBoundingClientRect();
	return { x: e.clientX - rect.left, y: e.clientY - rect.top };
}

function start(e) {
	drawing = true;
	empty.value = false;
	const p = pos(e);
	lastX = p.x;
	lastY = p.y;
	canvasEl.value.setPointerCapture(e.pointerId);
}

function move(e) {
	if (!drawing) return;
	const p = pos(e);
	ctx.beginPath();
	ctx.moveTo(lastX, lastY);
	ctx.lineTo(p.x, p.y);
	ctx.stroke();
	lastX = p.x;
	lastY = p.y;
}

function end() {
	drawing = false;
}

function clear() {
	const canvas = canvasEl.value;
	const rect = canvas.getBoundingClientRect();
	ctx.clearRect(0, 0, rect.width, rect.height);
	empty.value = true;
}

function isEmpty() {
	return empty.value;
}

function toDataURL() {
	return canvasEl.value.toDataURL("image/png");
}

onMounted(() => {
	resize();
	window.addEventListener("resize", resize);
});
onBeforeUnmount(() => window.removeEventListener("resize", resize));

defineExpose({ clear, isEmpty, toDataURL });
</script>

<style scoped>
.sp-wrap {
	position: relative;
	border: 1.5px dashed var(--tp-border, #e6e8ec);
	border-radius: 14px;
	background: #fff;
	touch-action: none;
}
.sp-canvas {
	width: 100%;
	height: 160px;
	display: block;
	border-radius: 14px;
	touch-action: none;
	cursor: crosshair;
}
.sp-hint {
	position: absolute;
	inset: 0;
	display: flex;
	align-items: center;
	justify-content: center;
	color: var(--tp-ink-soft, #6b7280);
	font-size: 13px;
	pointer-events: none;
}
.sp-clear {
	position: absolute;
	top: 8px;
	right: 8px;
	font-size: 12px;
	font-weight: 600;
	color: var(--tp-ink-soft, #6b7280);
	background: #fff;
	border: 1px solid var(--tp-border, #e6e8ec);
	border-radius: 8px;
	padding: 4px 9px;
	cursor: pointer;
}
.sp-clear:disabled { opacity: 0.4; cursor: default; }
</style>
