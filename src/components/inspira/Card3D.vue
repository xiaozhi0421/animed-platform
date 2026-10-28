<template>
  <div
    ref="cardRef"
    class="card-3d-wrapper"
    :style="{ perspective: perspective + 'px' }"
    @mousemove="handleMouseMove"
    @mouseleave="handleMouseLeave"
    @touchmove.prevent="handleTouchMove"
    @touchend="handleMouseLeave"
  >
    <div
      class="card-3d-inner"
      :style="{
        transform: `rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale3d(${scale},${scale},${scale})`,
        transition: isHovering ? 'transform 0.1s ease-out' : 'transform 0.5s ease-out'
      }"
    >
      <!-- Glare / Shine effect -->
      <div
        class="card-3d-glare"
        :style="{
          background: `radial-gradient(circle at ${glareX}% ${glareY}%, rgba(255,255,255,0.15) 0%, transparent 60%)`,
          opacity: isHovering ? 1 : 0
        }"
      ></div>

      <!-- Border shine -->
      <div
        class="card-3d-border-shine"
        :style="{
          background: `radial-gradient(circle at ${glareX}% ${glareY}%, rgba(255,255,255,0.2) 0%, transparent 50%)`,
          opacity: isHovering ? 1 : 0
        }"
      ></div>

      <!-- Content -->
      <div class="card-3d-content">
        <slot />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const props = withDefaults(defineProps<{
  perspective?: number
  maxTilt?: number
  scale?: number
  glareOpacity?: number
}>(), {
  perspective: 800,
  maxTilt: 12,
  scale: 1.04,
  glareOpacity: 0.6
})

const cardRef = ref<HTMLElement | null>(null)
const rotateX = ref(0)
const rotateY = ref(0)
const glareX = ref(50)
const glareY = ref(50)
const isHovering = ref(false)

function handleMouseMove(e: MouseEvent) {
  const card = cardRef.value
  if (!card) return

  const rect = card.getBoundingClientRect()
  const centerX = rect.left + rect.width / 2
  const centerY = rect.top + rect.height / 2
  const mouseX = e.clientX - centerX
  const mouseY = e.clientY - centerY

  // Calculate rotation: normalize mouse position to [-1, 1] range
  const rotateXVal = (-mouseY / (rect.height / 2)) * props.maxTilt
  const rotateYVal = (mouseX / (rect.width / 2)) * props.maxTilt

  rotateX.value = rotateXVal
  rotateY.value = rotateYVal

  // Calculate glare position (0-100%)
  glareX.value = ((e.clientX - rect.left) / rect.width) * 100
  glareY.value = ((e.clientY - rect.top) / rect.height) * 100

  isHovering.value = true
}

function handleTouchMove(e: TouchEvent) {
  const touch = e.touches[0]
  if (!touch) return

  const card = cardRef.value
  if (!card) return

  const rect = card.getBoundingClientRect()
  const centerX = rect.left + rect.width / 2
  const centerY = rect.top + rect.height / 2
  const touchX = touch.clientX - centerX
  const touchY = touch.clientY - centerY

  const rotateXVal = (-touchY / (rect.height / 2)) * props.maxTilt
  const rotateYVal = (touchX / (rect.width / 2)) * props.maxTilt

  rotateX.value = rotateXVal
  rotateY.value = rotateYVal

  glareX.value = ((touch.clientX - rect.left) / rect.width) * 100
  glareY.value = ((touch.clientY - rect.top) / rect.height) * 100

  isHovering.value = true
}

function handleMouseLeave() {
  rotateX.value = 0
  rotateY.value = 0
  glareX.value = 50
  glareY.value = 50
  isHovering.value = false
}
</script>

<style scoped>
.card-3d-wrapper {
  width: 100%;
  perspective: 800px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.card-3d-inner {
  width: 100%;
  position: relative;
  transform-style: preserve-3d;
  will-change: transform;
}

.card-3d-glare {
  position: absolute;
  inset: 0;
  border-radius: inherit;
  pointer-events: none;
  z-index: 2;
  transition: opacity 0.3s ease;
}

.card-3d-border-shine {
  position: absolute;
  inset: -1px;
  border-radius: inherit;
  pointer-events: none;
  z-index: 1;
  transition: opacity 0.3s ease;
}

.card-3d-content {
  position: relative;
  z-index: 3;
  transform: translateZ(20px);
}
</style>
