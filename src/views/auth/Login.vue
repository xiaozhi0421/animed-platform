<template>
  <div class="login-page">
    <div class="aurora-bg" ref="auroraRef">
      <div class="aurora-layer aurora-1"></div>
      <div class="aurora-layer aurora-2"></div>
      <div class="aurora-layer aurora-3"></div>
    </div>
    <div class="grid-overlay"></div>
    <div class="particles">
      <span v-for="i in 30" :key="i" class="particle" :style="particleStyle(i)"></span>
    </div>

    <div class="login-container animate-scale-in">
      <!-- Left Brand -->
      <div class="login-left">
        <div class="brand-header">
          <div class="brand-icon-mini">
            <svg viewBox="0 0 500 500" fill="none" stroke="rgba(255,255,255,0.4)" stroke-width="4" stroke-linejoin="round" stroke-linecap="round">
              <path d="M399.686,108.48c-0.954-3.094-3.28-5.456-6.22-6.278c-10.102-2.854-18.566-10.162-23.222-20.083c-0.794-1.674-1.65-3.29-2.601-4.866c-4.041-6.689-10.037-11.731-17.064-14.42c-6.529-2.497-11.068-6.278-15.285-9.976c-0.453-8.863-2.294-33.415-9.322-50.212c-0.55-1.317-1.713-2.27-3.086-2.555c-1.408-0.291-2.846,0.139-3.879,1.124c-6.836,6.672-19.793,22.122-25.838,46.649c-26.691,12.207-34.69,38.237-34.69,56.239c0,5.59,1.16,10.882,2.828,15.963c-13.332,6.22-26.082,19.46-38.084,40.669l-61.662,74.175l0.033,0.015c-23.381,21.372-39.021,59.623-39.021,103.404c0,9.139,0.81,17.466,2.083,25.28c-0.272,0.386-0.69,0.615-0.936,1.034c-20.146,33.32-17.886,29.647-22.619,39.806c-9.44,25.241-4.175,51.998,10.583,67.34c20.15,20.949,41.785,25.031,49.638,24.561c15.998,0.271,13.009,0.273,98.143-28.422c5.637-1.9,8.854-7.901,7.236-13.682c-1.645-5.975-7.869-9.466-13.844-7.795c-85.793,24.045-83.326,24.738-97.273,21.055c-1.197-0.411-45.578-20.399-15.755-64.13c14.3,21.183,36.196,31.894,61.14,32.768v0.29h90.295c7.124,0,12.924-4.76,12.924-10.631c0-9.324-5.072-18.162-13.815-24.068c-4.069-2.763-8.788-4.677-13.749-5.835c6.383-11.108,10.795-24.6,12.637-40.53l24.559,76.741c0.888,2.588,3.33,4.324,6.062,4.324h42.058c8.207,0,14.865-4.768,14.865-10.624c0-9.332-5.83-18.155-15.898-24.076c-5.93-3.498-13.007-5.591-20.426-6.489l-10.645-39.49l-5.172-87.634c20.359-21.441,33.024-45.532,24.545-90.848c-3.945-20.971,10.631-30.634,13.346-32.243c2.456-0.848,4.91-1.787,7.367-2.529c3.814-1.154,7.662-2.795,11.325-5.281c2.218-1.514,10.132-7.225,16.79-19.803C399.521,114.595,400.606,111.559,399.686,108.48z">
                <animateTransform attributeName="transform" type="rotate" values="0 250 250;1 250 250;0 250 250;-1 250 250;0 250 250" dur="4s" repeatCount="indefinite"/>
              </path>
            </svg>
          </div>
          <h1 class="brand-title">AniMed</h1>
          <p class="brand-subtitle">动物医学数据协作平台</p>
          <div class="brand-divider"></div>
        </div>

        <!-- 3D Role Cards Stack -->
        <div class="role-stack">
          <div class="stack-cards">
            <div
              v-for="(role, index) in allRoles"
              :key="role.key"
              :class="['stack-card-wrapper', { 'stack-card-active': selectedRole === role.key }]"
              :style="{ '--delay': (index * 0.12) + 's' }"
              @click="selectedRole = role.key"
            >
              <Card3D :perspective="1000" :maxTilt="10" :scale="1.03">
                <div class="stack-card" :style="{ '--role-color': role.color }">
                  <div class="stack-card-bg"></div>
                  <div class="stack-card-content">
                    <div class="stack-icon" :style="{ '--role-color': role.color }">
                      <div class="stack-svg" v-html="role.svg"></div>
                    </div>
                    <div class="stack-info">
                      <div class="stack-name">{{ role.name }}</div>
                      <div class="stack-desc">{{ role.desc }}</div>
                    </div>
                  </div>
                  <div class="stack-indicator" :style="{ '--role-color': role.color }"></div>
                  <div class="stack-glow" :style="{ '--role-color': role.color }"></div>
                  <div class="stack-border" :style="{ '--role-color': role.color }"></div>
                </div>
              </Card3D>
            </div>
          </div>
        </div>

        <div class="floating-shapes">
          <div class="shape shape-1"></div>
          <div class="shape shape-2"></div>
          <div class="shape shape-3"></div>
          <div class="shape shape-4"></div>
        </div>

        <div class="brand-footer">
          <span class="footer-dot"></span>
          <span>智慧兽医 · 数据驱动</span>
          <span class="footer-dot"></span>
        </div>
      </div>

      <!-- Right Form -->
      <div class="login-right" :class="{ 'slide-out': cardFlipping, 'slide-in': cardSwapIn }" :style="{ '--accent-color': currentRoleColor }">
        <div class="login-form-wrapper">
          <div class="form-header">
            <div class="form-role-badge" :style="{ '--badge-color': currentRoleColor }">
              <span class="badge-dot"></span>
              {{ currentRoleName }}
            </div>
            <h2 class="form-title">欢迎登录</h2>
            <p class="form-subtitle">请输入您的账号信息以<span class="current-role-name">{{ currentRoleNameShort }}</span>身份进入系统</p>
          </div>

          <el-form ref="formRef" :model="form" :rules="rules" size="large" class="login-form">
            <div class="input-group">
              <label class="input-label">账号</label>
              <el-form-item prop="account">
                <el-input v-model="form.account" :placeholder="accountPlaceholder" prefix-icon="User" />
              </el-form-item>
            </div>
            <div class="input-group">
              <label class="input-label">密码</label>
              <el-form-item prop="password">
                <el-input v-model="form.password" type="password" placeholder="请输入密码" prefix-icon="Lock" show-password @keyup.enter="handleLogin" />
              </el-form-item>
            </div>
            <el-form-item>
              <RainbowButton tag="button" type="button" :disabled="loading" custom-class="submit-btn" @click="handleLogin">
                <span v-if="!loading">登 录</span>
                <span v-else class="loading-spinner"></span>
              </RainbowButton>
            </el-form-item>
          </el-form>

          <div class="register-links">
            <span>还没有账号？</span>
            <router-link to="/register">立即注册</router-link>
            <router-link to="/forgot-password" class="forgot-link">忘记密码？</router-link>
          </div>
          <div class="trust-badge">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2L2 7v6c0 5.25 3.83 10.28 10 12 6.17-1.72 10-6.75 10-12V7l-10-5z"/></svg>
            <span>安全加密 · 校园认证</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch, nextTick } from 'vue'
import { onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import RainbowButton from '@/components/RainbowButton.vue'
import Card3D from '@/components/inspira/Card3D.vue'
import type { FormInstance } from 'element-plus'

const router = useRouter()
const userStore = useUserStore()
const formRef = ref<FormInstance>()
const loading = ref(false)
const selectedRole = ref('campus_student')
const cardFlipping = ref(false)
const cardSwapIn = ref(false)
const auroraRef = ref<HTMLElement>()

const form = reactive({ account: '', password: '' })
const rules = {
  account: [{ required: true, message: '请输入账号', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

const allRoles = [
  {
    key: 'campus_student',
    name: '学生',
    desc: '课程学习 · 作业提交 · 签到考勤',
    endLabel: '校园端',
    color: '#6366f1',
    svg: `<svg viewBox="0 0 48 48" fill="none" class="role-anim student-anim">
        <path d="M24 6L4 16l20 10 20-10L24 6z" fill="currentColor" opacity="0.2" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/>
        <path d="M12 22v12c0 0 4 6 12 6s12-6 12-6V22" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
        <circle cx="40" cy="35" r="2" fill="currentColor" opacity="0.6"/>
      </svg>`
  },
  {
    key: 'campus_teacher',
    name: '教师',
    desc: '班级管理 · 签到发起 · 作业批改',
    endLabel: '校园端',
    color: '#0ea5e9',
    svg: `<svg viewBox="0 0 48 48" fill="none" class="role-anim teacher-anim">
        <rect x="6" y="8" width="24" height="18" rx="2" fill="currentColor" opacity="0.15" stroke="currentColor" stroke-width="1.5"/>
        <path d="M6 14h24" stroke="currentColor" stroke-width="1.5"/>
        <circle cx="36" cy="14" r="6" fill="currentColor" opacity="0.15" stroke="currentColor" stroke-width="1.5"/>
        <path d="M33 14l2 2 4-4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>`
  },
  {
    key: 'campus_admin',
    name: '校园管理员',
    desc: '学生管理 · 教师管理 · 系统运维',
    endLabel: '校园端',
    color: '#f59e0b',
    svg: `<svg viewBox="0 0 48 48" fill="none" class="role-anim admin-anim">
        <path d="M24 4l-16 8v16l16 8 16-8V12L24 4z" fill="currentColor" opacity="0.12" stroke="currentColor" stroke-width="1.5"/>
        <path d="M24 4v8" stroke="currentColor" stroke-width="0.8" opacity="0.2"/>
        <circle cx="24" cy="22" r="3" fill="currentColor" opacity="0.4"/>
      </svg>`
  }
]

const currentRoleName = computed(() => {
  const role = allRoles.find(r => r.key === selectedRole.value)
  return role ? `${role.endLabel} · ${role.name}` : ''
})

const currentRoleNameShort = computed(() => {
  const role = allRoles.find(r => r.key === selectedRole.value)
  return role ? role.name : ''
})

const currentRoleColor = computed(() => {
  const role = allRoles.find(r => r.key === selectedRole.value)
  return role ? role.color : '#409eff'
})

watch(selectedRole, () => {
  formRef.value?.clearValidate()
  if (cardFlipping.value) {
    cardFlipping.value = false
    cardSwapIn.value = false
    void nextTick()
  }
  cardFlipping.value = true
  cardSwapIn.value = false
  setTimeout(() => {
    cardFlipping.value = false
    cardSwapIn.value = true
    setTimeout(() => {
      cardSwapIn.value = false
    }, 400)
  }, 300)
})

const accountPlaceholder = computed(() => {
  const map: Record<string, string> = {
    campus_student: '请输入学号',
    campus_teacher: '请输入教师号',
    campus_admin: '请输入管理员账号'
  }
  return map[selectedRole.value] || '请输入账号'
})

function particleStyle(i: number) {
  const size = Math.random() * 4 + 1
  return {
    width: size + 'px',
    height: size + 'px',
    left: Math.random() * 100 + '%',
    top: Math.random() * 100 + '%',
    animationDelay: Math.random() * 6 + 's',
    animationDuration: Math.random() * 4 + 4 + 's'
  }
}

function handleMouseMove(e: MouseEvent) {
  const el = auroraRef.value?.parentElement
  if (!el) return
  const rect = el.getBoundingClientRect()
  if (auroraRef.value) {
    auroraRef.value.style.setProperty('--mouse-x', String((e.clientX - rect.left) / rect.width - 0.5))
    auroraRef.value.style.setProperty('--mouse-y', String((e.clientY - rect.top) / rect.height - 0.5))
  }
}

onMounted(() => {
  window.addEventListener('mousemove', handleMouseMove)
  setTimeout(() => {
    cardFlipping.value = false
  }, 200)
})

onUnmounted(() => {
  window.removeEventListener('mousemove', handleMouseMove)
})

watch(selectedRole, () => {
  form.account = ''
  form.password = ''
  formRef.value?.resetFields()
  localStorage.removeItem('lastLoginAccount')
})

async function handleLogin() {
  await formRef.value?.validate()
  loading.value = true
  try {
    const loginSystem = 'campus'
    await userStore.login({ account: form.account, password: form.password, system: loginSystem, role: selectedRole.value })
    if (userStore.userInfo && !userStore.userInfo.role) {
      userStore.userInfo.role = selectedRole.value
      localStorage.setItem('userInfo', JSON.stringify(userStore.userInfo))
    }
    ElMessage.success('登录成功')
    router.push(userStore.getDefaultRoute())
  } catch (e: any) {
  } finally {
    loading.value = false
  }
}
</script>

<style scoped lang="scss">
.login-page {
  width: 100%; height: 100vh; display: flex; align-items: center; justify-content: center;
  background: linear-gradient(135deg, #0f0c29 0%, #1d1e3a 30%, #0d7377 70%, #14b8a6 100%);
  position: relative; overflow: hidden;
}

.aurora-bg { position: absolute; inset: 0; pointer-events: none; overflow: hidden; }
.aurora-layer {
  position: absolute; width: 150%; height: 150%; top: -25%; left: -25%;
  border-radius: 50%; filter: blur(80px); opacity: 0.15;
}
.aurora-1 { background: radial-gradient(circle, #409eff, transparent 60%); animation: auroraMove1 15s ease-in-out infinite; }
.aurora-2 { background: radial-gradient(circle, #0d7377, transparent 60%); animation: auroraMove2 18s ease-in-out infinite; }
.aurora-3 { background: radial-gradient(circle, #e6a23c, transparent 60%); animation: auroraMove3 20s ease-in-out infinite; }

@keyframes auroraMove1 { 0%,100% { transform: translate(0,0) scale(1); } 50% { transform: translate(10%,-5%) scale(1.1); } }
@keyframes auroraMove2 { 0%,100% { transform: translate(0,0) scale(1); } 50% { transform: translate(-8%,8%) scale(1.15); } }
@keyframes auroraMove3 { 0%,100% { transform: translate(0,0) scale(1); } 50% { transform: translate(5%,-10%) scale(1.05); } }

.grid-overlay {
  position: absolute; inset: 0; pointer-events: none;
  background-image: linear-gradient(rgba(255,255,255,0.02) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px);
  background-size: 60px 60px;
}

.particles { position: absolute; inset: 0; pointer-events: none; }
.particle {
  position: absolute; border-radius: 50%; background: rgba(255,255,255,0.4);
  animation: particleFloat 6s ease-in-out infinite;
}
@keyframes particleFloat {
  0%, 100% { transform: translateY(0) scale(1); opacity: 0; }
  10% { opacity: 1; }
  90% { opacity: 0.8; }
  50% { transform: translateY(-60px) scale(1.3); }
}

.login-container {
  display: flex; width: 960px; min-height: 600px; border-radius: 24px; overflow: hidden;
  background: rgba(255,255,255,0.03); backdrop-filter: blur(24px);
  border: 1px solid rgba(255,255,255,0.1);
  box-shadow: 0 25px 60px -12px rgba(0,0,0,0.5), 0 0 0 1px rgba(255,255,255,0.05) inset;
  z-index: 1;
}

.login-left {
  flex: 1.2; flex-shrink: 0; padding: 36px 32px; display: flex; flex-direction: column;
  justify-content: space-between;
  background: rgba(255,255,255,0.04); border-right: 1px solid rgba(255,255,255,0.06);
  position: relative; overflow: hidden;
}

.brand-header {
  text-align: center; position: relative; z-index: 3; padding-bottom: 0;
}
.brand-icon-mini {
  width: 64px; height: 64px; margin: 0 auto 10px;
  animation: floatIcon 6s ease-in-out infinite;
  svg { width: 100%; height: 100%; }
}
@keyframes floatIcon { 0%,100% { transform: translateY(0); } 50% { transform: translateY(-6px); } }
.brand-title {
  color: #fff; font-size: 28px; font-weight: 800; letter-spacing: 4px; margin: 0;
  background: linear-gradient(135deg, #fff 60%, rgba(255,255,255,0.5));
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.brand-subtitle {
  color: rgba(255,255,255,0.45); font-size: 12px; letter-spacing: 5px; margin-top: 4px; font-weight: 300;
}
.brand-divider {
  width: 32px; height: 2px; margin: 14px auto 0;
  background: linear-gradient(90deg, #6366f1, #0ea5e9);
  border-radius: 1px; opacity: 0.5;
}

/* ============ 3D Role Stack ============ */
.role-stack {
  position: relative; z-index: 3;
  flex: 1; display: flex; align-items: center; justify-content: center;
  padding: 6px 0;
}

.stack-cards {
  display: flex; flex-direction: column; gap: 10px;
  width: 100%;
  max-width: 320px;
  position: relative;
}

.stack-card-wrapper {
  opacity: 0;
  animation: stackFadeIn 0.6s ease forwards;
  animation-delay: var(--delay, 0s);
  cursor: pointer;
  transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.stack-card-wrapper:hover {
  transform: translateX(6px);
}

@keyframes stackFadeIn {
  0% { opacity: 0; transform: translateX(-20px); }
  100% { opacity: 1; transform: translateX(0); }
}

.stack-card {
  position: relative;
  border-radius: 14px;
  padding: 11px 16px;
  display: flex;
  align-items: center;
  overflow: hidden;
}

.stack-card-bg {
  position: absolute; inset: 0; border-radius: 16px;
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.06);
  transition: all 0.35s ease;
}

.stack-card-active .stack-card-bg {
  background: rgba(255,255,255,0.08);
  border-color: color-mix(in srgb, var(--role-color) 50%, transparent);
  box-shadow: 0 0 40px color-mix(in srgb, var(--role-color) 12%, transparent),
              inset 0 1px 0 rgba(255,255,255,0.1);
}

.stack-card-content {
  display: flex; align-items: center; gap: 12px;
  position: relative; z-index: 1;
}

.stack-icon {
  width: 42px; height: 42px; border-radius: 12px;
  background: color-mix(in srgb, var(--role-color) 15%, transparent);
  border: 1.5px solid color-mix(in srgb, var(--role-color) 30%, transparent);
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
  transition: all 0.4s ease;
}
.stack-card-active .stack-icon {
  background: color-mix(in srgb, var(--role-color) 25%, transparent);
  border-color: var(--role-color);
  box-shadow: 0 0 20px color-mix(in srgb, var(--role-color) 30%, transparent);
}
.stack-svg { width: 22px; height: 22px; color: rgba(255,255,255,0.6); }
.stack-card-active .stack-svg { color: #fff; }

.stack-info { flex: 1; min-width: 0; }
.stack-name {
  font-size: 14px; font-weight: 700; color: rgba(255,255,255,0.7);
  letter-spacing: 1px; transition: color 0.3s;
}
.stack-card-active .stack-name { color: #fff; }
.stack-desc {
  font-size: 10px; color: rgba(255,255,255,0.3); margin-top: 1px;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.stack-card-active .stack-desc { color: rgba(255,255,255,0.5); }

.stack-indicator {
  position: absolute; right: 12px; top: 50%; transform: translateY(-50%);
  width: 8px; height: 8px; border-radius: 50%;
  background: var(--role-color);
  opacity: 0; transition: all 0.4s ease;
  box-shadow: 0 0 12px var(--role-color);
}
.stack-card-active .stack-indicator { opacity: 1; }

.stack-glow {
  position: absolute; top: 50%; right: -20px; width: 90px; height: 90px;
  transform: translateY(-50%); border-radius: 50%;
  background: radial-gradient(circle, color-mix(in srgb, var(--role-color) 10%, transparent) 0%, transparent 70%);
  opacity: 0; transition: opacity 0.6s ease; pointer-events: none;
}
.stack-card-active .stack-glow { opacity: 1; }

.stack-border {
  position: absolute; inset: 0; border-radius: 16px;
  border: 1.5px solid transparent;
  transition: all 0.4s ease; pointer-events: none;
}
.stack-card-active .stack-border {
  border-color: color-mix(in srgb, var(--role-color) 60%, transparent);
}

.floating-shapes { position: absolute; inset: 0; pointer-events: none; z-index: 0; }
.shape {
  position: absolute; border-radius: 50%;
  border: 1px solid rgba(255,255,255,0.06);
}
.shape-1 { width: 150px; height: 150px; top: -10%; left: -15%; animation: shapeDrift1 12s ease-in-out infinite; }
.shape-2 { width: 100px; height: 100px; bottom: 5%; right: -10%; animation: shapeDrift2 14s ease-in-out infinite reverse; }
.shape-3 { width: 60px; height: 60px; top: 40%; left: -8%; animation: shapeDrift3 10s ease-in-out infinite 2s; }
.shape-4 { width: 80px; height: 80px; bottom: 30%; right: -5%; animation: shapeDrift1 11s ease-in-out infinite 1s; }

@keyframes shapeDrift1 { 0%,100% { transform: translate(0,0) rotate(0deg); } 50% { transform: translate(20px,-20px) rotate(120deg); } }
@keyframes shapeDrift2 { 0%,100% { transform: translate(0,0) rotate(0deg); } 50% { transform: translate(-15px,15px) rotate(-90deg); } }
@keyframes shapeDrift3 { 0%,100% { transform: translate(0,0) scale(1); } 50% { transform: translate(10px,10px) scale(1.2); } }

.brand-footer {
  text-align: center; position: relative; z-index: 3;
  font-size: 10px; color: rgba(255,255,255,0.25); letter-spacing: 3px;
  display: flex; align-items: center; justify-content: center; gap: 8px;
}
.footer-dot { width: 3px; height: 3px; border-radius: 50%; background: rgba(255,255,255,0.2); }

/* Right Form */
.login-right {
  flex: 1; flex-shrink: 0; background: #fff; padding: 44px 40px 36px;
  display: flex; align-items: center; justify-content: center;
  position: relative; z-index: 1;
  transform-origin: left center;
  transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1), opacity 0.35s ease;
  will-change: transform, opacity;
  &.slide-out { transform: translateX(-100%) scale(0.96); opacity: 0; }
  &.slide-in { animation: slideInFromRight 0.5s cubic-bezier(0.16, 1, 0.3, 1) forwards; }
}

@keyframes slideInFromRight {
  0% { transform: translateX(-100%) scale(0.96); opacity: 0; }
  60% { transform: translateX(6px); opacity: 1; }
  80% { transform: translateX(-2px); }
  100% { transform: translateX(0); opacity: 1; }
}

.login-form-wrapper { width: 100%; max-width: 400px; }
.form-header { margin-bottom: 28px; }
.form-role-badge {
  display: inline-flex; align-items: center; gap: 5px;
  padding: 5px 14px; border-radius: 20px;
  background: color-mix(in srgb, var(--badge-color, #6366f1) 8%, transparent);
  border: 1px solid color-mix(in srgb, var(--badge-color, #6366f1) 20%, transparent);
  color: var(--badge-color, #6366f1);
  font-size: 11px; font-weight: 600;
}
.badge-dot {
  width: 6px; height: 6px; border-radius: 50%;
  background: var(--badge-color, #6366f1);
  animation: badgePulse 2s ease-in-out infinite;
}
@keyframes badgePulse { 0%,100% { opacity: 1; transform: scale(1); } 50% { opacity: 0.4; transform: scale(0.7); } }
.form-title { font-size: 26px; font-weight: 700; color: #1a1a2e; margin: 12px 0 6px; }
.form-subtitle { font-size: 13px; color: #94a3b8; line-height: 1.5; }
.current-role-name { color: var(--accent-color, #6366f1); font-weight: 600; }

.input-group { margin-bottom: 2px; }
.input-label { display: block; font-size: 12px; font-weight: 600; color: #475569; margin-bottom: 4px; letter-spacing: 0.5px; }

.login-form {
  :deep(.el-form-item) { margin-bottom: 18px; }
  :deep(.el-input__wrapper) {
    padding: 4px 14px; border-radius: 12px; height: 46px;
    box-shadow: 0 0 0 1px #e2e8f0; transition: all 0.3s ease;
    &:hover { box-shadow: 0 0 0 1px #cbd5e1; }
    &.is-focus { box-shadow: 0 0 0 2px color-mix(in srgb, var(--accent-color, #6366f1) 30%, transparent); }
  }
  :deep(.el-input__prefix) { color: #94a3b8; }
  :deep(.el-input__inner) { color: #000000 !important; }
}

:deep(.submit-btn) {
  width: 100%; height: 48px; font-size: 16px; font-weight: 600; letter-spacing: 4px;
  border-radius: 12px;
  &:disabled { opacity: 0.7; cursor: not-allowed; }
}

.loading-spinner {
  display: inline-block; width: 20px; height: 20px;
  border: 2.5px solid rgba(255,255,255,0.3); border-top-color: #fff; border-radius: 50%;
  animation: spin 0.6s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

.register-links {
  text-align: center; margin-top: 20px; font-size: 13px; color: #94a3b8;
  display: flex; align-items: center; justify-content: center; gap: 12px;
  a { color: #409eff; text-decoration: none; font-weight: 500; margin-left: 4px; &:hover { color: #337ecc; } }
  .forgot-link { color: #94a3b8; font-weight: 400; font-size: 12px; margin-left: 0; &:hover { color: #64748b; } }
}

.trust-badge { display: flex; align-items: center; justify-content: center; gap: 6px; margin-top: 18px; font-size: 11px; color: #94a3b8; opacity: 0.6; }

.animate-scale-in { animation: scaleIn 0.6s cubic-bezier(0.16,1,0.3,1); }
@keyframes scaleIn { from { opacity: 0; transform: scale(0.95); } to { opacity: 1; transform: scale(1); } }
</style>




