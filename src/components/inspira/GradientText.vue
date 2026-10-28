<template>
  <span :class="['bg-gradient-to-r bg-clip-text text-transparent', gradientClass, className]">
    <slot />
  </span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  gradient: { type: String, default: 'blue' },
  className: { type: String, default: '' }
})

const gradients = {
  blue: 'from-blue-400 via-indigo-500 to-purple-600',
  green: 'from-emerald-400 via-teal-500 to-cyan-600',
  orange: 'from-orange-400 via-amber-500 to-yellow-600',
  pink: 'from-pink-400 via-rose-500 to-purple-600',
  rainbow: 'from-red-400 via-yellow-500 via-green-500 to-blue-600',
  cyber: 'from-cyan-400 via-blue-500 to-violet-600'
}

const gradientClass = computed(() => {
  return gradients[props.gradient] || gradients.blue
})
</script>
