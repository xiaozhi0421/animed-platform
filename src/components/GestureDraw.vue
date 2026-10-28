<template>
  <div class="gesture-draw">
    <div class="gesture-grid-wrap">
      <svg class="gesture-lines" viewBox="0 0 296 296">
        <line
          v-for="(seg, idx) in lineSegments"
          :key="idx"
          :x1="seg.x1" :y1="seg.y1"
          :x2="seg.x2" :y2="seg.y2"
          stroke="#333333" stroke-width="3"
          stroke-linecap="round"
        />
      </svg>
      <div class="grid-container" ref="gridRef">
      <div
        v-for="i in 9"
        :key="i"
        class="grid-dot"
        :class="{ active: pattern.includes(i), current: i === currentDot }"
        @mousedown="startDraw(i)"
        @mouseenter="continueDraw(i)"
        @mouseup="endDraw"
        @touchstart.prevent="startDraw(i)"
        @touchmove.prevent="handleTouchMove"
        @touchend.prevent="endDraw"
      >
        <div class="dot-inner"></div>
      </div>
    </div>
    </div>
    <div class="gesture-info">
      <span v-if="pattern.length">已选择: {{ pattern.join(' → ') }}</span>
      <span v-else>请按顺序点击圆点绘制手势</span>
      <el-button size="small" @click="clearPattern" style="margin-left: 8px;">重置</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'

const emit = defineEmits(['update:modelValue'])
const props = defineProps<{ modelValue?: string }>()

const pattern = ref<number[]>([])
const currentDot = ref<number>(0)
const isDrawing = ref(false)
const gridRef = ref<HTMLElement>()

watch(() => props.modelValue, (val) => {
  if (val) {
    pattern.value = val.split('-').map(Number).filter(n => n >= 1 && n <= 9)
  } else {
    pattern.value = []
  }
}, { immediate: true })

watch(pattern, (val) => {
  emit('update:modelValue', val.length ? val.join('-') : '')
}, { deep: true })

function startDraw(dot: number) {
  isDrawing.value = true
  pattern.value = [dot]
  currentDot.value = dot
}

function continueDraw(dot: number) {
  if (!isDrawing.value) return
  if (pattern.value.includes(dot)) return
  pattern.value.push(dot)
  currentDot.value = dot
}

function endDraw() {
  isDrawing.value = false
  currentDot.value = 0
}

function handleTouchMove(e: TouchEvent) {
  if (!isDrawing.value) return
  const touch = e.touches[0]
  const el = document.elementFromPoint(touch.clientX, touch.clientY)
  if (el) {
    const dotEl = el.closest('.grid-dot')
    if (dotEl) {
      const index = Array.from(dotEl.parentElement?.children || []).indexOf(dotEl)
      if (index >= 0 && index < 9) {
        continueDraw(index + 1)
      }
    }
  }
}

function clearPattern() {
  pattern.value = []
  currentDot.value = 0
  emit('update:modelValue', '')
}

// 九宫格圆点中心坐标 (padding 16px, cell 80px, gap 12px)
const dotPositions = [
  { x: 56, y: 56 },   // 1
  { x: 148, y: 56 },  // 2
  { x: 240, y: 56 },  // 3
  { x: 56, y: 148 },  // 4
  { x: 148, y: 148 }, // 5
  { x: 240, y: 148 }, // 6
  { x: 56, y: 240 },  // 7
  { x: 148, y: 240 }, // 8
  { x: 240, y: 240 }, // 9
]

const lineSegments = computed(() => {
  const segs: { x1: number; y1: number; x2: number; y2: number }[] = []
  for (let i = 0; i < pattern.value.length - 1; i++) {
    const from = dotPositions[pattern.value[i] - 1]
    const to = dotPositions[pattern.value[i + 1] - 1]
    if (from && to) {
      segs.push({ x1: from.x, y1: from.y, x2: to.x, y2: to.y })
    }
  }
  return segs
})
</script>

<style scoped lang="scss">
.gesture-draw {
  .gesture-grid-wrap {
    position: relative;
    width: fit-content;
    margin: 0 auto;
  }
  .gesture-lines {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
    z-index: 1;
  }
  .grid-container {
    position: relative;
    z-index: 2;
    display: grid;
    grid-template-columns: repeat(3, 80px);
    grid-template-rows: repeat(3, 80px);
    gap: 12px;
    justify-content: center;
    padding: 16px;
    background: transparent;
    border-radius: 8px;
    user-select: none;
  }
  .grid-dot {
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    cursor: pointer;
    transition: all 0.2s;
    .dot-inner {
      width: 24px;
      height: 24px;
      border-radius: 50%;
      background: #1a1a1a;
      transition: all 0.2s;
    }
    &.active .dot-inner {
      background: #333333;
      box-shadow: 0 0 12px rgba(0, 0, 0, 0.5);
    }
    &.current .dot-inner {
      background: #555555;
      box-shadow: 0 0 12px rgba(0, 0, 0, 0.3);
      transform: scale(1.2);
    }
    &:hover {
      background: rgba(64, 158, 255, 0.1);
    }
  }

  .gesture-info {
    text-align: center;
    margin-top: 12px;
    font-size: 13px;
    color: #666;
  }
}
</style>
