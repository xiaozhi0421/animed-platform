<template>
  <div class="data-manage page-container">
    <el-card>
      <template #header>
        <div class="flex-between">
          <span><el-icon><DataAnalysis /></el-icon> 数据集管理</span>
          <el-button type="primary" @click="$router.push('/campus/data/upload')">
            <el-icon><Plus /></el-icon>上传数据
          </el-button>
        </div>
      </template>

      <!-- Search -->
      <el-form :inline="true" :model="query" class="search-form">
        <el-form-item label="关键词" style="flex:1">
          <el-input v-model="query.name" placeholder="搜索数据集名称..." clearable @keyup.enter="fetchData" />
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="query.type" placeholder="全部分类" clearable style="width:160px" @change="fetchData">
            <el-option v-for="t in typeOptions" :key="t.value" :label="t.label" :value="t.value" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchData">搜索</el-button>
          <el-button @click="resetQuery">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- Table -->
      <el-table :data="tableData" stripe v-loading="loading" empty-text="暂无数据，请先上传">
        <el-table-column type="index" label="#" width="50" />
        <el-table-column prop="name" label="数据集名称" min-width="200" show-overflow-tooltip />
        <el-table-column prop="type" label="分类" width="120">
          <template #default="{ row }">
            <el-tag :type="tagType(row.type)" size="small">{{ typeLabel(row.type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="rowCount" label="数据行数" width="100" align="center">
          <template #default="{ row }">{{ row.rowCount ?? '-' }}</template>
        </el-table-column>
        <el-table-column label="格式" width="80" align="center">
          <template #default="{ row }">{{ row.fileFormat || '-' }}</template>
        </el-table-column>
        <el-table-column prop="cleanStatus" label="清洗状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.cleanStatus === 'cleaned' || row.cleanStatus === '已清洗' ? 'success' : 'warning'" size="small">
              {{ row.cleanStatus === 'cleaned' || row.cleanStatus === '已清洗' ? '已清洗' : '未清洗' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="createTime" label="创建时间" width="170" />
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="handleView(row)">查看</el-button>
            <el-button link type="success" size="small" @click="$router.push('/campus/data/clean?dataset_id=' + row.id)">清洗</el-button>
            <el-button link type="danger" size="small" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- Pagination -->
      <el-pagination
        v-model:current-page="query.pageNum" v-model:page-size="query.pageSize"
        :total="total" :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next"
        @change="fetchData" style="margin-top:16px;justify-content:flex-end" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { dataApi } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()
const loading = ref(false)
const tableData = ref<any[]>([])
const total = ref(0)

const typeOptions = [
  { label: '血液检测', value: 'blood' },
  { label: '流行病学', value: 'epidemiology' },
  { label: '寄生虫', value: 'parasite' },
  { label: '影像诊断', value: 'imaging' },
  { label: '病理分析', value: 'pathology' },
  { label: '临床数据', value: 'clinical' },
  { label: '实验数据', value: 'experiment' },
  { label: '调研数据', value: 'survey' },
  { label: '研究数据', value: 'research' },
  { label: '未分类', value: 'general' }
]

const typeLabels: Record<string, string> = {
  blood: '血液检测', epidemiology: '流行病学', parasite: '寄生虫',
  imaging: '影像诊断', pathology: '病理分析', clinical: '临床数据',
  experiment: '实验数据', survey: '调研数据', research: '研究数据',
  general: '未分类'
}
const tagColors: Record<string, string> = {
  blood: 'danger', epidemiology: 'warning', parasite: '',
  imaging: 'success', pathology: '', clinical: 'danger',
  experiment: 'warning', survey: 'info', research: 'primary'
}
function typeLabel(v: string) { return typeLabels[v] || v || '未分类' }
function tagType(v: string) { return tagColors[v] || 'info' }

const query = reactive({ name: '', type: '', pageNum: 1, pageSize: 10 })

function resetQuery() {
  query.name = ''
  query.type = ''
  query.pageNum = 1
  fetchData()
}

async function fetchData() {
  loading.value = true
  try {
    const params: any = { pageNum: query.pageNum, pageSize: query.pageSize }
    if (query.name) params.name = query.name
    if (query.type) params.type = query.type
    const res: any = await dataApi.getDatasets(params)
    tableData.value = res.data?.records || []
    total.value = res.data?.total || 0
  } catch (e: any) {
    tableData.value = []
    total.value = 0
    ElMessage.error('获取数据集列表失败')
  } finally {
    loading.value = false
  }
}

function handleView(row: any) {
  router.push('/campus/data/detail/' + row.id)
}

async function handleDelete(row: any) {
  try {
    await ElMessageBox.confirm('确定删除数据集「' + row.name + '」？此操作不可恢复。', '提示', { type: 'warning' })
    await dataApi.deleteDataset(row.id)
    ElMessage.success('已删除')
    fetchData()
  } catch (e: any) {
    if (e !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

onMounted(fetchData)
</script>

<style scoped>
.search-form { margin-bottom: 16px; display: flex; flex-wrap: wrap; gap: 8px; }
.flex-between { display: flex; justify-content: space-between; align-items: center; }
</style>


