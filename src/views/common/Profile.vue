<template>
  <div class="page-container">
    <el-row :gutter="20">
      <el-col :span="8" :xs="24">
        <el-card class="profile-card">
          <div class="profile-header">
            <div class="avatar-upload-wrap" @click="triggerUpload">
              <el-avatar :size="100" :src="avatarUrl" class="profile-avatar">{{ userStore.userName?.charAt(0) }}</el-avatar>
              <div class="avatar-overlay">
                <el-icon :size="24"><Camera /></el-icon>
                <span>个人资料</span>
              </div>
            </div>
            <input ref="fileInputRef" type="file" accept="image/*" style="display:none" @change="handleFileChange" />
            <h3>{{ userStore.userName }}</h3>
            <el-tag size="small">{{ userStore.roleName }}</el-tag>
          </div>
          <el-descriptions :column="1" class="profile-info" border>
            <el-descriptions-item label="账号">{{ userStore.userInfo?.account || userStore.userInfo?.username }}</el-descriptions-item>
            <el-descriptions-item label="姓名">{{ userStore.userInfo?.realName || userStore.userName }}</el-descriptions-item>
            <el-descriptions-item :label="userStore.userRole === 'campus_teacher' ? '教师号' : '学号'">{{ userStore.userRole === 'campus_teacher' ? (userStore.userInfo?.username || '-') : (userStore.userInfo?.studentNo || '-') }}</el-descriptions-item>
            <el-descriptions-item label="性别">{{ userStore.userInfo?.gender || '-' }}</el-descriptions-item>
            <el-descriptions-item v-if="userStore.userRole !== 'campus_teacher'" label="专业">{{ userStore.userInfo?.majorName || '-' }}</el-descriptions-item>
            <el-descriptions-item label="角色">{{ userStore.roleName }}</el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
      <el-col :span="16" :xs="24">
        <el-card class="page-card">
          <template #header><span>个人资料</span></template>
          <el-form :model="form" label-width="100px" style="max-width:500px">
            <el-form-item label="姓名">
              <el-input v-model="form.name" />
            </el-form-item>
            <el-form-item :label="userStore.userRole === 'campus_teacher' ? '教师号' : '学号'">
              <el-input :model-value="userStore.userRole === 'campus_teacher' ? (userStore.userInfo?.username || '-') : form.studentNo" disabled />
            </el-form-item>
            <el-form-item label="性别">
              <el-select v-model="form.gender" style="width:100%">
                <el-option label="男" value="男" />
                <el-option label="女" value="女" />
              </el-select>
            </el-form-item>
            <el-form-item v-if="userStore.userRole !== 'campus_teacher'" label="专业">
              <el-input v-model="form.majorName" disabled />
            </el-form-item>
            <el-form-item label="手机号">
              <el-input v-model="form.phone" />
            </el-form-item>
            <el-form-item label="个人简介">
              <el-input v-model="form.bio" type="textarea" :rows="3" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleSave" :loading="saving">保存修改</el-button>
            </el-form-item>
          </el-form>
        </el-card>
        <el-card class="page-card" style="margin-top:20px">
          <template #header><span>密码修改</span></template>
          <el-form :model="pwdForm" label-width="100px" style="max-width:500px">
            <el-form-item label="原密码">
              <el-input v-model="pwdForm.oldPwd" type="password" show-password />
            </el-form-item>
            <el-form-item label="新密码">
              <el-input v-model="pwdForm.newPwd" type="password" show-password />
            </el-form-item>
            <el-form-item label="确认密码">
              <el-input v-model="pwdForm.confirmPwd" type="password" show-password />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleChangePwd">保存修改</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
    </el-row>
    <el-dialog v-model="cropperVisible" title="裁剪头像" width="540px" top="5vh" :close-on-click-modal="false" destroy-on-close append-to-body>
      <div class="cropper-wrapper">
        <VueCropper ref="cropperRef" :img="cropImg" :output-size="1" :output-type="'png'"
          :auto-crop="true" :can-scale="true" :can-move="true" :can-move-box="true"
          :fixed="true" :fixed-number="[1,1]"
          :auto-crop-width="200" :auto-crop-height="200" :center-box="true"
          style="height:100%;width:100%" />
      </div>
      <template #footer>
        <div class="crop-actions">
          <el-button @click="cropperVisible = false">取消</el-button>
          <el-button type="primary" @click="confirmCrop" :loading="uploading">保存修改</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { fileApi, userApi } from '@/api'
import { ElMessage } from 'element-plus'
import { VueCropper } from 'vue-cropper'
import 'vue-cropper/dist/index.css'

const userStore = useUserStore()

const pwdForm = reactive({ oldPwd: '', newPwd: '', confirmPwd: '' })

const form = ref({
  name: '',
  studentNo: '',
  gender: '',
  majorName: '',
  phone: '',
  bio: ''
})

function loadProfile() {
  const info = userStore.userInfo
  if (!info) {
    userStore.initFromStorage()
  }
  const data = userStore.userInfo || {}
  form.value = {
    name: data.realName || userStore.userName || '',
    studentNo: data.studentNo || '',
    gender: data.gender || '',
    majorName: data.majorName || '',
    phone: data.phone || '',
    bio: data.bio || ''
  }
}

const avatarUrl = ref(userStore.userInfo?.avatar || '')
const fileInputRef = ref<HTMLInputElement>()
const cropperVisible = ref(false)
const cropImg = ref('')
const cropperRef = ref()
const uploading = ref(false)
const saving = ref(false)

function triggerUpload() { fileInputRef.value?.click() }

function handleFileChange(e: Event) {
  const input = e.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  const reader = new FileReader()
  reader.onload = () => { cropImg.value = reader.result as string; cropperVisible.value = true }
  reader.readAsDataURL(file)
  input.value = ''
}

async function confirmCrop() {
  uploading.value = true
  try {
    const blob = await cropperRef.value?.getCropBlob()
    if (!blob) { ElMessage.error('获取裁剪图像失败'); return }
    const formData = new FormData()
    formData.append('file', blob, 'avatar.png')
    const res = await fileApi.upload(formData)
    const url = res?.data?.url || res?.data?.fileUrl || ''
    if (url) { avatarUrl.value = url; await handleSave(); cropperVisible.value = false }
  } catch { ElMessage.error('上传失败') }
  finally { uploading.value = false }
}

async function handleSave() {
  saving.value = true
  try {
    await userApi.updateProfile({ realName: form.value.name, gender: form.value.gender, phone: form.value.phone, bio: form.value.bio, avatar: avatarUrl.value }, userStore.userRole)
    const info = userStore.userInfo
    if (info) {
      Object.assign(info, { avatar: avatarUrl.value, realName: form.value.name, phone: form.value.phone, email: form.value.email, bio: form.value.bio })
      localStorage.setItem('userInfo', JSON.stringify(info))
    }
    ElMessage.success('保存成功')
  } catch { ElMessage.error('上传失败') }
  finally { saving.value = false }
}

function handleChangePwd() {
  if (pwdForm.newPwd !== pwdForm.confirmPwd) { ElMessage.error('两次密码输入不一致'); return }
  ElMessage.success('密码修改成功')
}

onMounted(() => {
  loadProfile()
  avatarUrl.value = userStore.userInfo?.avatar || ''
})
</script>

<style scoped lang="scss">
.profile-card { border-radius: 12px; }
.page-card { border-radius: 12px; }
.profile-header {
  display: flex; flex-direction: column; align-items: center; padding: 20px 0;
  h3 { margin: 12px 0 8px; font-size: 18px; }
}
.profile-info { margin-top: 16px; }
.avatar-upload-wrap {
  position: relative; cursor: pointer; margin-bottom: 12px;
  &:hover .avatar-overlay { opacity: 1; }
  .profile-avatar { background: linear-gradient(135deg, #409eff, #337ecc); font-size: 32px; width: 100px; height: 100px; line-height: 100px; }
}
.avatar-overlay {
  position: absolute; top: 0; left: 50%; transform: translateX(-50%);
  width: 100px; height: 100px; border-radius: 50%;
  background: rgba(0,0,0,0.45);
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  color: #fff; font-size: 12px; gap: 2px;
  opacity: 0; transition: opacity 0.25s; cursor: pointer;
}
.cropper-wrapper { height: 420px; display: flex; align-items: center; justify-content: center; }
.crop-actions { display: flex; justify-content: center; gap: 12px; margin-top: 16px; }
</style>
