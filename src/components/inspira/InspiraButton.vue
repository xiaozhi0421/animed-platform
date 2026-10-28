<template>
  <button
    :class="[
      'inspira-button relative inline-flex items-center justify-center overflow-hidden rounded-lg px-6 py-3 text-sm font-medium transition-all duration-300',
      variant === 'primary' ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white hover:shadow-lg hover:shadow-blue-500/25' : '',
      variant === 'secondary' ? 'bg-gradient-to-r from-emerald-500 to-teal-600 text-white hover:shadow-lg hover:shadow-emerald-500/25' : '',
      variant === 'outline' ? 'border border-white/20 bg-white/5 text-white hover:bg-white/10' : '',
      variant === 'ghost' ? 'text-foreground hover:bg-accent' : '',
      size === 'sm' ? 'px-3 py-1.5 text-xs' : '',
      size === 'lg' ? 'px-8 py-4 text-base' : '',
      loading ? 'cursor-not-allowed opacity-70' : 'cursor-pointer',
      disabled ? 'cursor-not-allowed opacity-50' : '',
      className
    ]"
    :disabled="disabled || loading"
    @click="$emit('click', $event)"
  >
    <!-- Shimmer effect on hover -->
    <span v-if="variant !== 'ghost'" class="shimmer-overlay absolute inset-0 -translate-x-full animate-shimmer bg-gradient-to-r from-transparent via-white/10 to-transparent group-hover:translate-x-full"></span>
    
    <!-- Loading spinner -->
    <svg v-if="loading" class="mr-2 h-4 w-4 animate-spin" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
    </svg>
    
    <slot />
  </button>
</template>

<script setup>
defineProps({
  variant: { type: String, default: 'primary' },
  size: { type: String, default: 'md' },
  loading: { type: Boolean, default: false },
  disabled: { type: Boolean, default: false },
  className: { type: String, default: '' }
})

defineEmits(['click'])
</script>

<style scoped>
.inspira-button {
  position: relative;
  isolation: isolate;
}
.inspira-button::before {
  content: '';
  position: absolute;
  inset: -1px;
  border-radius: inherit;
  padding: 1px;
  background: conic-gradient(from var(--angle), transparent 0%, hsl(var(--primary) / 0.3) 50%, transparent 100%);
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  opacity: 0;
  transition: opacity 0.3s;
}
.inspira-button:hover::before {
  opacity: 1;
  animation: spin 3s linear infinite;
}
@property --angle {
  syntax: '<angle>';
  initial-value: 0deg;
  inherits: false;
}
@keyframes spin {
  to { --angle: 360deg; }
}
</style>
