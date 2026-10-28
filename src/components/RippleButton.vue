<template>
  <button
    ref="rippleButtonRef"
    :class="['ripple-button', customClass]"
    :style="{ '--duration': duration + 'ms' }"
    @click="handleClick"
  >
    <span class="ripple-content">
      <slot />
    </span>
    <span class="ripple-container">
      <span
        v-for="ripple in ripples"
        :key="ripple.key"
        class="ripple-animation"
        :style="{
          width: ripple.size + 'px',
          height: ripple.size + 'px',
          top: ripple.y + 'px',
          left: ripple.x + 'px',
          backgroundColor: rippleColor,
          animationDuration: duration + 'ms'
        }"
      />
    </span>
  </button>
</template>

<script setup lang="ts">
import { ref, watchEffect } from 'vue'

const props = withDefaults(defineProps<{
  customClass?: string
  rippleColor?: string
  duration?: number
}>(), {
  customClass: '',
  rippleColor: 'rgba(64,158,255,0.3)',
  duration: 600
})

const emit = defineEmits<{
  (e: 'click', event: MouseEvent): void
}>()

const rippleButtonRef = ref<HTMLButtonElement | null>(null)
const ripples = ref<Array<{ x: number; y: number; size: number; key: number }>>([])

function handleClick(event: MouseEvent) {
  createRipple(event)
  emit('click', event)
}

function createRipple(event: MouseEvent) {
  const button = rippleButtonRef.value
  if (!button) return

  const rect = button.getBoundingClientRect()
  const size = Math.max(rect.width, rect.height)
  const x = event.clientX - rect.left - size / 2
  const y = event.clientY - rect.top - size / 2

  ripples.value.push({ x, y, size, key: Date.now() })
}

watchEffect(() => {
  if (ripples.value.length > 0) {
    const lastRipple = ripples.value[ripples.value.length - 1]
    setTimeout(() => {
      ripples.value = ripples.value.filter(r => r.key !== lastRipple.key)
    }, props.duration)
  }
})
</script>

<style scoped>
.ripple-button {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  border-radius: 8px;
  border: 1px solid #dcdfe6;
  background: #fff;
  padding: 10px 20px;
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  overflow: hidden;
  transition: all 0.2s;
}

.ripple-button:hover {
  border-color: #409eff;
  color: #409eff;
}

.ripple-content {
  position: relative;
  z-index: 1;
}

.ripple-container {
  pointer-events: none;
  position: absolute;
  inset: 0;
}

.ripple-animation {
  position: absolute;
  border-radius: 50%;
  transform: scale(0);
  animation: ripple var(--duration) ease-out;
}

@keyframes ripple {
  0% {
    opacity: 1;
    transform: scale(0);
  }
  100% {
    opacity: 0;
    transform: scale(2);
  }
}
</style>
