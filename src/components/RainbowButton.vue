<template>
  <component
    :is="tag"
    :class="['rainbow-button', customClass]"
    :style="{ '--speed': speedInSeconds }"
    v-bind="$attrs"
  >
    <span class="rainbow-btn-text"><slot /></span>
  </component>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(defineProps<{
  customClass?: string
  tag?: string
  speed?: number
}>(), {
  customClass: '',
  tag: 'button',
  speed: 2
})

const speedInSeconds = computed(() => `${props.speed}s`)
</script>

<style scoped>
.rainbow-button {
  --color-1: hsl(0 100% 63%);
  --color-2: hsl(270 100% 63%);
  --color-3: hsl(210 100% 63%);
  --color-4: hsl(195 100% 63%);
  --color-5: hsl(90 100% 63%);
  --speed: 2s;

  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  border-radius: 12px;
  border: none;
  padding: 10px 32px;
  font-size: 14px;
  font-weight: 600;
  color: #fff;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
  transition: transform 0.2s, box-shadow 0.2s;
  overflow: hidden;
}

.rainbow-button::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg, var(--color-1), var(--color-5), var(--color-3), var(--color-4), var(--color-2), var(--color-1));
  background-size: 200% 100%;
  animation: rainbow var(--speed) linear infinite;
  z-index: 0;
}

.rainbow-btn-text {
  position: relative;
  z-index: 1;
  color: #fff;
  font-weight: 600;
  text-shadow: 0 1px 2px rgba(0,0,0,0.3);
}

.rainbow-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
}

.rainbow-button:active {
  transform: translateY(0);
}

.rainbow-button::after {
  content: '';
  position: absolute;
  bottom: -20%;
  left: 50%;
  width: 60%;
  height: 20%;
  transform: translateX(-50%);
  background: linear-gradient(90deg, var(--color-5), var(--color-3), var(--color-4));
  filter: blur(12px);
  opacity: 0.5;
  animation: rainbow var(--speed) linear infinite;
  z-index: -1;
}

@keyframes rainbow {
  0% { background-position: 0; }
  100% { background-position: 200%; }
}
</style>
