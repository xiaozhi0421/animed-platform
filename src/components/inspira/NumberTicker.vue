<template>
  <span :class="['inline-block', className]" ref="elRef">
    {{ displayValue }}
  </span>
</template>

<script setup>
import { ref, watch, onMounted, computed } from 'vue'

const props = defineProps({
  from: { type: Number, default: 0 },
  to: { type: Number, default: 100 },
  duration: { type: Number, default: 2 },
  prefix: { type: String, default: '' },
  suffix: { type: String, default: '' },
  decimals: { type: Number, default: 0 },
  autoStart: { type: Boolean, default: true },
  className: { type: String, default: '' }
})

const emit = defineEmits(['complete'])
const displayValue = ref(props.from)
const elRef = ref(null)

function animate() {
  const start = props.from
  const end = props.to
  const range = end - start
  const startTime = performance.now()
  
  function step(currentTime) {
    const elapsed = (currentTime - startTime) / 1000
    const progress = Math.min(elapsed / props.duration, 1)
    // Ease out cubic
    const eased = 1 - Math.pow(1 - progress, 3)
    displayValue.value = (start + range * eased).toFixed(props.decimals)
    
    if (progress < 1) {
      requestAnimationFrame(step)
    } else {
      displayValue.value = end.toFixed(props.decimals)
      emit('complete')
    }
  }
  
  requestAnimationFrame(step)
}

onMounted(() => {
  if (props.autoStart) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          animate()
          observer.unobserve(entry.target)
        }
      })
    }, { threshold: 0.1 })
    if (elRef.value) observer.observe(elRef.value)
  }
})
</script>
