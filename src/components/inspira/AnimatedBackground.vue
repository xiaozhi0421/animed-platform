<script setup>
const props = defineProps({
  variant: { type: String, default: 'grid' },
  className: { type: String, default: '' }
})
</script>

<template>
  <div :class="['pointer-events-none fixed inset-0 -z-10 overflow-hidden', className]" aria-hidden="true">
    <!-- Grid pattern via CSS -->
    <div v-if="variant === 'grid'" 
      class="absolute inset-0 opacity-[0.03] dark:opacity-[0.05]"
      style="background-image: url(&quot;data:image/svg+xml,%3Csvg width='40' height='40' viewBox='0 0 40 40' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M0 0h40v40H0z' fill='none' stroke='%23409eff' stroke-width='0.5'/%3E%3C/svg%3E&quot;)">
    </div>
    
    <!-- Dot pattern -->
    <div v-else-if="variant === 'dots'"
      class="absolute inset-0 opacity-[0.03] dark:opacity-[0.05]"
      style="background-image: radial-gradient(circle, currentColor 1px, transparent 1px); background-size: 30px 30px">
    </div>
    
    <!-- Gradient orbs -->
    <div v-else-if="variant === 'orbs'">
      <div class="absolute -top-40 -right-40 h-80 w-80 rounded-full bg-gradient-to-br from-blue-400/20 to-purple-600/20 blur-3xl"></div>
      <div class="absolute -bottom-40 -left-40 h-80 w-80 rounded-full bg-gradient-to-tr from-emerald-400/20 to-teal-600/20 blur-3xl"></div>
    </div>
  </div>
</template>
