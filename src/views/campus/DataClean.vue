<template>
  <div class="data-clean page-container">
    <el-card>
      <template #header>
        <div class="flex-between">
          <span><el-icon><Filter /></el-icon> 数据清洗任务</span>
          <el-button type="primary" @click="showCreateDialog = true"><el-icon><Plus /></el-icon>新建清洗任务</el-button>
        </div>
      </template>
      <el-table :data="tasks" stripe v-loading="loading" empty-text="暂无清洗任务">
        <el-table-column prop="taskName" label="任务名称" min-width="180" />
        <el-table-column prop="dataSetName" label="数据集" width="160" />
        <el-table-column prop="rules" label="清洗规则" width="200">
          <template #default="{ row }">
            <el-tag v-for="r in (row.rules||'').split(',')" :key="r" size="small" style="margin-right:4px;margin-bottom:2px">
              {{ ruleLabel(r) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" size="small">{{ row.status || '未知' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="progress" label="进度" width="150">
          <template #default="{ row }">
            <el-progress :percentage="row.progress || 0" :status="row.status === '已完成' ? 'success' : row.status === '已失败' ? 'exception' : ''" />
          </template>
        </el-table-column>
        <el-table-column prop="createTime" label="创建时间" width="170" />
        <el-table-column label="操作" width="240" fixed="right">
          <template #default="{ row }">
            <el-button v-if="row.status === '等待中'" link type="primary" size="small" @click="startTask(row)">启动</el-button>
            <el-button v-if="row.status === '待确认'" link type="warning" size="small" @click="previewTask(row)">查看对比</el-button>
            <el-button v-if="row.status === '待确认'" link type="success" size="small" @click="confirmTask(row)">采纳保存</el-button>
            <el-button v-if="row.status === '待确认'" link type="info" size="small" @click="discardTask(row)">放弃</el-button>
            <el-button v-if="row.status === '已完成' || row.status === '已放弃' || row.status === '已失败'" link type="primary" size="small" @click="previewTask(row)">查看结果</el-button>
            <el-button link type="danger" size="small" :disabled="row.status === '清洗中'" @click="deleteTask(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新建任务对话框 -->
    <el-dialog v-model="showCreateDialog" title="新建清洗任务" width="500px">
      <el-form :model="taskForm" label-width="100px">
        <el-form-item label="任务名称">
          <el-input v-model="taskForm.taskName" placeholder="请输入任务名称" />
        </el-form-item>
        <el-form-item label="数据集">
          <el-select v-model="taskForm.datasetId" placeholder="请选择数据集" style="width:100%">
            <el-option v-for="ds in datasets" :key="ds.id" :label="ds.name" :value="ds.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="清洗规则">
          <div style="display:flex;flex-direction:column;gap:8px;width:100%">
            <div style="display:flex;gap:10px;align-items:center;flex-wrap:wrap">
              <el-checkbox v-model="enableMissingValue" @change="onMissingValueChange">缺失值处理</el-checkbox>
              <el-select v-model="missingValueMethod" :disabled="!enableMissingValue" placeholder="选择填充方式" style="width:150px" size="small">
                <el-option value="mean" label="均值填充" />
                <el-option value="median" label="中位数填充" />
                <el-option value="mode" label="众数填充" />
                <el-option value="delete" label="删除缺失行" />
                <el-option value="custom" label="自定义值填充" />
              </el-select>
              <el-input v-if="missingValueMethod === 'custom'" v-model="customFillValue" placeholder="输入自定义值" style="width:130px" size="small" />
            </div>
            <div style="display:flex;gap:10px;align-items:center;flex-wrap:wrap">
              <el-checkbox v-model="enableOutlier" @change="onOutlierChange">异常值检测</el-checkbox>
              <el-select v-model="outlierMethod" :disabled="!enableOutlier" placeholder="选择检测方式" style="width:150px" size="small">
                <el-option value="iqr" label="IQR截断" />
                <el-option value="ai" label="AI异常值检测" />
              </el-select>
            </div>
            <div>
              <el-checkbox value="duplicate" v-model="enableDuplicate">重复数据去除</el-checkbox>
            </div>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="createTask">创建</el-button>
      </template>
    </el-dialog>

    <!-- 清洗对比预览对话框 -->
        <el-dialog v-model="showPreviewDialog" title="清洗结果对比" width="90%" top="5vh">
      <template v-if="previewData">
        <el-alert title="清洗完成，请检查以下对比结果" type="info" :closable="false" show-icon style="margin-bottom:16px;" />
        
        <el-descriptions :column="4" border size="small" style="margin-bottom:16px;">
          <el-descriptions-item label="清洗前行数">
            <span style="font-size:18px;font-weight:bold;color:#409eff">{{ previewData.beforeRows }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="清洗后行数">
            <span style="font-size:18px;font-weight:bold;color:#67c23a">{{ previewData.afterRows }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="移除行数">
            <span style="font-size:18px;font-weight:bold;color:#fbbf24">{{ previewData.removedRows }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="数据列数">
            <span style="font-size:18px;font-weight:bold;color:rgba(255,255,255,0.45)">{{ previewData.columns?.length || 0 }}</span>
          </el-descriptions-item>
        </el-descriptions>
        
        <p v-if="previewRules" style="margin:0 0 12px;font-size:13px;color:#666;">
          已应用规则：{{ previewRules }}
        </p>

        <el-tabs type="border-card">
          <el-tab-pane label="清洗前数据">
            <el-table :data="previewData.beforeSample || []" border stripe size="small" max-height="400" style="width:100%">
              <el-table-column type="index" label="#" width="50" fixed />
              <el-table-column v-for="col in previewData.columns || []" :key="col" :prop="col" :label="col" min-width="130" show-overflow-tooltip />
            </el-table>
            <div style="text-align:right;margin-top:8px;font-size:12px;color:#999;">
              共 {{ previewData.beforeRows }} 行，显示前 {{ (previewData.beforeRows || 0) > 20 ? 20 : (previewData.beforeRows || 0) }} 行
            </div>
          </el-tab-pane>
          <el-tab-pane label="清洗后数据">
            <el-table :data="previewData.afterSample || []" border stripe size="small" max-height="400" style="width:100%">
              <el-table-column type="index" label="#" width="50" fixed />
              <el-table-column v-for="col in previewData.columns || []" :key="col" :prop="col" :label="col" min-width="130" show-overflow-tooltip />
            </el-table>
            <div style="text-align:right;margin-top:8px;font-size:12px;color:#999;">
              共 {{ previewData.afterRows }} 行，显示前 {{ (previewData.afterRows || 0) > 20 ? 20 : (previewData.afterRows || 0) }} 行
            </div>
          </el-tab-pane>
        </el-tabs>
      </template>
      <el-empty v-else description="暂无对比数据" />
      <template #footer>
        <div style="display:flex;justify-content:center;gap:12px;">
          <el-button v-if="currentTask?.status === '待确认'" type="success" @click="doConfirm">
            <el-icon><Check /></el-icon> 采纳保存
          </el-button>
          <el-button v-if="currentTask?.status === '待确认'" @click="doDiscard">
            <el-icon><Close /></el-icon> 放弃结果
          </el-button>
          <el-button @click="showPreviewDialog = false">关闭</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { dataApi } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import { get } from '@/utils/request'

const loading = ref(false)
const tasks = ref<any[]>([])
const datasets = ref<any[]>([])
const showCreateDialog = ref(false)
const showPreviewDialog = ref(false)
const previewData = ref<any>(null)
const previewRules = ref('')
const currentTask = ref<any>(null)
const enableMissingValue = ref(false)
const missingValueMethod = ref('mean')
const customFillValue = ref('')
const enableOutlier = ref(false)
const outlierMethod = ref("iqr")
const enableDuplicate = ref(false)
const taskForm = reactive({ taskName: '', datasetId: null as number | null, rules: [] as string[] })

function ruleLabel(r: string) {
  const methodMap: Record<string, string> = { mean: '均值填充', median: '中位数填充', mode: '众数填充', delete: '删除缺失行', custom: '自定义值填充' }
  const parts = r.trim().split(':')
  if (parts[0] === 'missing_value' && parts[1]) {
    return '缺失值处理(' + (methodMap[parts[1]] || parts[1]) + ')'
  }
  if (parts[0] === 'outlier' && parts[1]) {
    const outlierMap: Record<string, string> = { iqr: 'IQR截断', ai: 'AI检测' }
    return '异常值检测(' + (outlierMap[parts[1]] || parts[1]) + ')'
  }
  const map: Record<string, string> = { missing_value: '缺失值处理', outlier: '异常值检测', duplicate: '去重', format: '格式化' }
  return map[r.trim()] || r.trim()
}

function statusType(s: string) {
  if (s === '已完成') return 'success'
  if (s === '清洗中') return 'warning'
  if (s === '已失败') return 'danger'
  if (s === '已放弃') return 'info'
  if (s === '待确认') return 'warning'
  return 'info'
}

async function fetchTasks() {
  loading.value = true
  try {
    const res: any = await dataApi.getCleanTasks({ pageNum: 1, pageSize: 50 })
    tasks.value = res.data?.records || res.data || []
  } catch {} finally { loading.value = false }
}

async function fetchDatasets() {
  try {
    const res: any = await dataApi.getDatasets({ pageNum: 1, pageSize: 100 })
    datasets.value = res.data?.records || []
  } catch {}
}

async function onOutlierChange(val: boolean) {
  if (!val) outlierMethod.value = 'iqr'
}

async function onMissingValueChange(val: boolean) {
  if (!val) { missingValueMethod.value = 'mean'; customFillValue.value = '' }
}

function buildRules(): string[] {
  const rules: string[] = []
  if (enableMissingValue.value) {
    const method = missingValueMethod.value === 'custom' && customFillValue.value
      ? 'custom:' + customFillValue.value : missingValueMethod.value
    rules.push('missing_value:' + method)
  }
  if (enableOutlier.value) rules.push('outlier:' + outlierMethod.value)
  if (enableDuplicate.value) rules.push('duplicate')
  return rules
}

async function createTask() {
  const rules = buildRules()
  if (!taskForm.taskName || !taskForm.datasetId) { ElMessage.warning('请填写完整信息'); return }
  if (rules.length === 0) { ElMessage.warning('请至少选择一个清洗规则'); return }
  try {
    await dataApi.createCleanTask({
      taskName: taskForm.taskName,
      datasetId: taskForm.datasetId,
      rules: rules
    })
    ElMessage.success('任务创建成功')
    showCreateDialog.value = false
    taskForm.taskName = ''
    taskForm.datasetId = null
    taskForm.rules = []
    enableMissingValue.value = false
    missingValueMethod.value = 'mean'
    customFillValue.value = ''
    enableOutlier.value = false
    outlierMethod.value = 'iqr'
    enableDuplicate.value = false
    fetchTasks()
  } catch { ElMessage.error('创建失败') }
}

async function startTask(row: any) {
  try {
    await dataApi.startCleanTask(row.id)
    ElMessage.success('清洗任务已启动，正在进行数据清洗...')
    fetchTasks()
  } catch (e: any) { ElMessage.error(e.message || '启动失败') }
}

async function previewTask(row: any) {
  currentTask.value = row
  previewData.value = null
  previewRules.value = ''
  showPreviewDialog.value = true
  try {
    const res: any = await dataApi.getCleanPreview(row.id)
    previewData.value = res.data
    previewRules.value = (row.rules || '').split(',').map((r: string) => ruleLabel(r)).join('、')
  } catch { ElMessage.warning('获取对比数据失败'); showPreviewDialog.value = false }
}

async function doConfirm() {
  if (!currentTask.value) return
  try {
    await ElMessageBox.confirm('确定采纳清洗后的数据并保存到数据集？', '确认', { type: 'info' })
    await dataApi.confirmCleanTask(currentTask.value.id)
    ElMessage.success('清洗结果已保存，数据集已更新')
    showPreviewDialog.value = false
    fetchTasks()
  } catch (e: any) {
    if (e !== 'cancel') ElMessage.error('保存失败')
  }
}

async function doDiscard() {
  if (!currentTask.value) return
  try {
    await ElMessageBox.confirm('确定放弃本次清洗结果？原始数据将保持不变。', '确认', { type: 'warning' })
    await dataApi.discardCleanTask(currentTask.value.id)
    ElMessage.success('已放弃本次清洗结果')
    showPreviewDialog.value = false
    fetchTasks()
  } catch (e: any) {
    if (e !== 'cancel') ElMessage.error('操作失败')
  }
}

async function confirmTask(row: any) {
  currentTask.value = row
  await doConfirm()
}

async function discardTask(row: any) {
  currentTask.value = row
  await doDiscard()
}

async function deleteTask(row: any) {
  try {
    await ElMessageBox.confirm('确定删除该清洗任务？', '提示', { type: 'warning' })
    await dataApi.deleteCleanTask(row.id)
    ElMessage.success('任务已删除')
    fetchTasks()
  } catch {}
}

onMounted(() => { fetchTasks(); fetchDatasets() })
</script>

<style scoped>
.flex-between { display: flex; justify-content: space-between; align-items: center; }
</style>

