<script setup lang="ts">
import { cn } from '@/utils/cn'
interface Props {
  class?: string
}
const props = defineProps<Props>()
</script>

<template>
  <div :class="cn('aurora-container', props.class)">
    <div class="aurora-beam aurora-beam-1"></div>
    <div class="aurora-beam aurora-beam-2"></div>
    <div class="aurora-beam aurora-beam-3"></div>
    <div class="aurora-beam aurora-beam-4"></div>
    <div class="aurora-overlay"></div>
  </div>
</template>

<style scoped>
.aurora-container {
  position: fixed;
  inset: 0;
  overflow: hidden;
  z-index: 0;
  background: #0b0f1a;
}
.aurora-beam {
  position: absolute;
  border-radius: 50%;
  filter: blur(100px);
  opacity: 0.3;
  mix-blend-mode: screen;
}
.aurora-beam-1 {
  width: 700px;
  height: 700px;
  background: radial-gradient(circle, rgba(99,102,241,0.4) 0%, transparent 70%);
  top: -20%;
  left: -10%;
  animation: auroraDrift1 20s ease-in-out infinite;
}
.aurora-beam-2 {
  width: 600px;
  height: 600px;
  background: radial-gradient(circle, rgba(6,182,212,0.3) 0%, transparent 70%);
  bottom: -15%;
  right: -10%;
  animation: auroraDrift2 25s ease-in-out infinite reverse;
}
.aurora-beam-3 {
  width: 500px;
  height: 500px;
  background: radial-gradient(circle, rgba(139,92,246,0.25) 0%, transparent 70%);
  top: 30%;
  left: 40%;
  animation: auroraDrift3 22s ease-in-out infinite 3s;
}
.aurora-beam-4 {
  width: 400px;
  height: 400px;
  background: radial-gradient(circle, rgba(236,72,153,0.15) 0%, transparent 70%);
  top: 50%;
  left: 60%;
  animation: auroraDrift4 18s ease-in-out infinite 5s;
}
.aurora-overlay {
  position: absolute;
  inset: 0;
  background: 
    radial-gradient(ellipse at 20% 50%, rgba(99,102,241,0.03) 0%, transparent 50%),
    radial-gradient(ellipse at 80% 50%, rgba(6,182,212,0.03) 0%, transparent 50%);
}

@keyframes auroraDrift1 {
  0%, 100% { transform: translate(0, 0) scale(1); }
  33% { transform: translate(80px, -60px) scale(1.15); }
  66% { transform: translate(-40px, 50px) scale(0.9); }
}
@keyframes auroraDrift2 {
  0%, 100% { transform: translate(0, 0) scale(1); }
  33% { transform: translate(-70px, 40px) scale(1.1); }
  66% { transform: translate(50px, -50px) scale(0.95); }
}
@keyframes auroraDrift3 {
  0%, 100% { transform: translate(0, 0) scale(1); opacity: 0.3; }
  50% { transform: translate(40px, 30px) scale(1.2); opacity: 0.5; }
}
@keyframes auroraDrift4 {
  0%, 100% { transform: translate(0, 0) scale(1); opacity: 0.2; }
  50% { transform: translate(-50px, -30px) scale(1.3); opacity: 0.4; }
}
</style>
