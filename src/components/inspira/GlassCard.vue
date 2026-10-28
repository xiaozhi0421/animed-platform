<template>
  <div :class="['glass-card relative overflow-hidden rounded-2xl border p-6 backdrop-blur-xl transition-all duration-500', className]" :style="cardStyle">
    <!-- Glass gradient overlay -->
    <div class="pointer-events-none absolute inset-0 bg-gradient-to-br from-white/5 to-white/[0.02]"></div>
    
    <!-- Subtle border glow -->
    <div class="pointer-events-none absolute -inset-[1px] rounded-2xl bg-gradient-to-br from-white/10 via-transparent to-white/5 opacity-0 transition-opacity duration-500 group-hover:opacity-100"></div>
    
    <!-- Content -->
    <div class="relative z-10">
      <slot />
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  className: { type: String, default: '' },
  gradient: { type: String, default: '' },
  hover: { type: Boolean, default: true }
})

const cardStyle = computed(() => {
  const style = {}
  if (props.gradient) {
    style.background = props.gradient
  }
  return style
})
</script>

<style scoped>
.glass-card {
  background: hsl(var(--card) / 0.8);
  border-color: hsl(var(--border) / 0.5);
  box-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.04), 0 1px 2px -1px rgb(0 0 0 / 0.04);
}
.glass-card:hover {
  box-shadow: 0 4px 20px 0 rgb(0 0 0 / 0.08), 0 2px 8px -2px rgb(0 0 0 / 0.04);
  transform: translateY(-2px);
  border-color: hsl(var(--primary) / 0.3);
}
</style>
