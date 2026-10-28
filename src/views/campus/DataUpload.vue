<template>
  <div class="data-upload page-container">
    <el-row :gutter="20">
      <el-col :span="14">
        <el-card>
          <template #header><span><el-icon><Upload /></el-icon> 上传数据集</span></template>
          <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
            <el-form-item label="数据集名称" prop="name">
              <el-input v-model="form.name" placeholder="输入数据集名称，如“犬细小病毒临床数据”" />
            </el-form-item>
            <el-form-item label="数据分类" prop="category">
              <el-select v-model="form.category" placeholder="选择数据分类" style="width:100%">
                <el-option v-for="t in typeOptions" :key="t.value" :label="t.label" :value="t.value" />
              </el-select>
            </el-form-item>
            <el-form-item label="数据描述">
              <el-input v-model="form.description" type="textarea" :rows="4" placeholder="输入数据集的描述信息，包括数据来源、采集时间、样本数量等" />
            </el-form-item>
            <el-form-item label="数据文件" prop="file">
              <el-upload drag :auto-upload="false" :limit="1" accept=".csv,.xlsx,.xls,.json"
                :on-change="handleFileChange" :on-remove="()=>file=null">
                <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
                <div class="el-upload__text">拖拽文件到此处或<em>点击上传</em></div>
                <template #tip>
                  <div class="el-upload__tip">支持 CSV、Excel、JSON 格式，单文件不超过 100MB</div>
                </template>
              </el-upload>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :loading="uploading" @click="handleUpload" size="large">
                <el-icon><Upload /></el-icon> 开始上传
              </el-button>
              <el-button @click="$router.back()">取消</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
      <el-col :span="10">
        <el-card>
          <template #header><span>💡 上传说明</span></template>
          <div class="tips">
            <h4>支持的文件格式</h4>
            <ul>
              <li><b>CSV</b> — 逗号分隔的表格数据</li>
              <li><b>Excel</b> (.xlsx/.xls) — 多工作表支持</li>
              <li><b>JSON</b> — 结构化数据文件</li>
            </ul>
            <h4>数据分类说明</h4>
            <ul>
              <li><b>血液检测</b> — 血常规、生化检测等</li>
              <li><b>流行病学</b> — 疾病分布、传播调查</li>
              <li><b>寄生虫</b> — 寄生虫感染检测数据</li>
              <li><b>影像诊断</b> — X光、B超、MRI等</li>
              <li><b>病理分析</b> — 组织切片、病理报告</li>
            </ul>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { dataApi } from '@/api'
import { ElMessage } from 'element-plus'
import type { FormInstance, UploadFile } from 'element-plus'

const router = useRouter()
const formRef = ref<FormInstance>()
const uploading = ref(false)
const file = ref<File | null>(null)

const form = reactive({ name: '', category: '', description: '' })
const rules = {
  name: [{ required: true, message: '请输入数据集名称', trigger: 'blur' }],
  category: [{ required: true, message: '请选择分类', trigger: 'change' }]
}

const typeOptions = [
  { label: '血液检测', value: 'blood' },
  { label: '流行病学', value: 'epidemiology' },
  { label: '寄生虫', value: 'parasite' },
  { label: '影像诊断', value: 'imaging' },
  { label: '病理分析', value: 'pathology' }
]

function handleFileChange(uploadFile: UploadFile) {
  file.value = uploadFile.raw || null
}

async function handleUpload() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  if (!file.value) { ElMessage.warning('请选择文件'); return }
  uploading.value = true
  try {
    const formData = new FormData()
    formData.append('file', file.value)
    formData.append('name', form.name)
    formData.append('category', form.category)
    formData.append('description', form.description)
    await dataApi.uploadDataset(formData)
    ElMessage.success('上传成功，服务器正在解析数据...')
    router.push('/campus/data')
  } catch { ElMessage.error('上传失败') }
  finally { uploading.value = false }
}
</script>

<style scoped>
.tips { font-size: 13px; color: rgba(255,255,255,0.6); line-height: 1.8; }
.tips h4 { margin: 12px 0 6px; color: rgba(255,255,255,0.7); }
.tips ul { padding-left: 20px; }
.tips li { margin-bottom: 4px; }
</style>
