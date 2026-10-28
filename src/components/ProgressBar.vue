<template>
  <div class="progress-bar-wrap">
    <div class="progress-steps">
      <div v-for="(step, i) in steps" :key="i" class="progress-step" :class="{ active: i <= currentStepIndex, done: i < currentStepIndex }">
        <div class="step-dot">
          <el-icon v-if="i < currentStepIndex" :size="10"><Check /></el-icon>
        </div>
        <div class="step-label">{{ step }}</div>
        <div v-if="i < steps.length - 1" class="step-line" :class="{ active: i < currentStepIndex }"></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue"

const props = defineProps<{ status: number }>()

const steps = ["已提交", "审阅中", "已通过"]

const statusMap: Record<number, number> = {
  1: 0, // 已提交
  2: 1, // 审阅中
  3: 2, // 已通过
  4: 0, // 需修改 → 回到已提交阶段（带修改状态）
  5: 2, // 已完成
}

const currentStepIndex = computed(() => {
  return statusMap[props.status] ?? 0
})
</script>

<style scoped>
.progress-bar-wrap { padding: 4px 0; }
.progress-steps { display: flex; align-items: center; gap: 0; }
.progress-step {
  display: flex; align-items: center; gap: 6px;
  position: relative;
}
.step-dot {
  width: 22px; height: 22px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  background: #e2e8f0; color: #94a3b8; font-size: 10px; font-weight: 600;
  flex-shrink: 0; transition: all 0.3s;
}
.progress-step.active .step-dot { background: #6366f1; color: #fff; box-shadow: 0 0 0 3px rgba(99,102,241,0.2); }
.progress-step.done .step-dot { background: #10b981; color: #fff; }
.step-label { font-size: 11px; color: #94a3b8; white-space: nowrap; }
.progress-step.active .step-label { color: #6366f1; font-weight: 600; }
.progress-step.done .step-label { color: #10b981; }
.step-line {
  width: 28px; height: 2px; background: #e2e8f0; margin: 0 4px;
  transition: background 0.3s;
}
.step-line.active { background: #10b981; }
</style>
