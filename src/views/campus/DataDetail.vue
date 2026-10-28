<template>
  <div class="data-detail page-container">
    <el-page-header @back="$router.back()" content="数据集详情" style="margin-bottom: 16px;" />
    <el-row :gutter="20">
      <el-col :span="24">
        <!-- 基本信息 -->
        <el-card v-loading="loading">
          <template #header>
            <div class="flex-between">
              <span>{{ detail.name || '数据集详情' }}</span>
              <el-tag :type="statusType" size="small">{{ statusLabel(detail.status) }}</el-tag>
            </div>
          </template>
          <el-descriptions :column="4" border size="small">
            <el-descriptions-item label="名称">{{ detail.name }}</el-descriptions-item>
            <el-descriptions-item label="分类">{{ detail.type || '未分类' }}</el-descriptions-item>
            <el-descriptions-item label="格式">{{ detail.fileFormat }}</el-descriptions-item>
            <el-descriptions-item label="大小">{{ formatSize(detail.fileSize) }}</el-descriptions-item>
            <el-descriptions-item label="行数">{{ detail.rowCount ?? '-' }}</el-descriptions-item>
            <el-descriptions-item label="列数">{{ detail.columnCount ?? '-' }}</el-descriptions-item>
            <el-descriptions-item label="清洗状态">
              <el-tag :type="detail.cleanStatus === '已清洗' ? 'success' : 'warning'" size="small">
                {{ cleanStatusLabel(detail.cleanStatus) }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="创建时间">{{ detail.createTime }}</el-descriptions-item>
          </el-descriptions>
          <div style="margin-top: 12px; display: flex; gap: 8px;">
            <el-button type="primary" size="small" @click="$router.push(`/campus/data/clean?datasetId=${id}`)">数据清洗</el-button>
            <el-button type="success" size="small" @click="$router.push('/campus/analysis')">数据分析</el-button>
          </div>
        </el-card>

        <!-- 数据表格 -->
        <el-card style="margin-top: 16px;">
          <template #header>
            <div class="flex-between">
              <span>数据表格</span>
              <div class="filter-bar">
                <el-select v-model="filterField" placeholder="筛选列" clearable size="small" style="width: 120px;">
                  <el-option v-for="col in columns" :key="col" :label="col" :value="col" />
                </el-select>
                <el-input v-model="filterValue" placeholder="筛选值" clearable size="small" style="width: 140px;" :disabled="!filterField" />
                <el-button type="primary" size="small" @click="loadRows">筛选</el-button>
                <el-button size="small" @click="resetFilter">重置</el-button>
              </div>
            </div>
          </template>

          <el-table
            :data="tableRows"
            stripe
            border
            size="small"
            style="width: 100%"
            @sort-change="handleSort"
            v-loading="tableLoading"
            :default-sort="{ prop: sortField, order: sortOrder }"
          >
            <el-table-column type="index" label="#" width="60" fixed />
            <el-table-column
              v-for="col in columns"
              :key="col"
              :prop="col"
              :label="col"
              :sortable="'custom'"
              min-width="120"
              show-overflow-tooltip
            />
          </el-table>

          <div class="pagination-bar">
            <span class="total-info">共 {{ totalRows }} 行</span>
            <el-pagination
              v-model:current-page="currentPage"
              v-model:page-size="pageSize"
              :page-sizes="[20, 50, 100]"
              :total="totalRows"
              layout="sizes, prev, pager, next"
              @size-change="loadRows"
              @current-change="loadRows"
            />
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { dataApi } from '@/api'
import { get } from '@/utils/request'
import { ElMessage } from 'element-plus'

const route = useRoute()
const id = Number(route.params.id)
const loading = ref(false)
const detail = ref<any>({})
const tableLoading = ref(false)
const tableRows = ref<any[]>([])
const columns = ref<string[]>([])
const totalRows = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const sortField = ref('')
const sortOrder = ref<'ascending' | 'descending' | ''>('')
const filterField = ref('')
const filterValue = ref('')

function statusLabel(s: string | undefined) {
  if (!s) return '未知'
  if (s === 'parsed' || s === '已解析') return '已解析'
  if (s === '已清洗' || s === 'cleaned') return '已清洗'
  if (s === '已上传') return '已上传'
  return s
}

function cleanStatusLabel(s: string | undefined) {
  if (!s) return '未清洗'
  if (s === 'cleaned' || s === '已清洗') return '已清洗'
  if (s === 'uncleaned') return '未清洗'
  return s
}

const statusType = computed(() => {
  const s = detail.value.status
  if (s === '已清洗' || s === '已分析' || s === 'cleaned') return 'success'
  if (s === '已上传' || s === 'parsed') return 'info'
  return 'warning'
})

async function fetchDetail() {
  loading.value = true
  try {
    const res: any = await dataApi.getDataset(id)
    detail.value = res.data || res
  } catch (e: any) {
    ElMessage.error('获取详情失败')
  } finally {
    loading.value = false
  }
}

async function loadRows() {
  tableLoading.value = true
  try {
    const params: any = {
      pageNum: currentPage.value,
      pageSize: pageSize.value
    }
    if (sortField.value) {
      params.sortField = sortField.value
      params.sortOrder = sortOrder.value === 'descending' ? 'desc' : 'asc'
    }
    if (filterField.value && filterValue.value) {
      params.filterField = filterField.value
      params.filterValue = filterValue.value
    }
    const res: any = await get(`/data/rows/${id}`, params)
    const data = res.data
    if (data) {
      tableRows.value = data.records || []
      totalRows.value = data.total || 0
      // 从第一行提取列名
      if (tableRows.value.length > 0 && columns.value.length === 0) {
        columns.value = Object.keys(tableRows.value[0])
      }
    }
  } catch (e: any) {
    // 如果data_row表没有数据，回退到文件预览
    try {
      const previewRes: any = await get(`/data/preview/${id}`)
      const preview = previewRes.data
      if (preview) {
        columns.value = preview.columns || []
        tableRows.value = preview.rows || []
        totalRows.value = preview.totalRows || 0
      }
    } catch {
      ElMessage.error('加载数据失败')
    }
  } finally {
    tableLoading.value = false
  }
}

function handleSort({ prop, order }: { prop: string; order: string }) {
  sortField.value = prop || ''
  sortOrder.value = (order as 'ascending' | 'descending' | '') || ''
  currentPage.value = 1
  loadRows()
}

function resetFilter() {
  filterField.value = ''
  filterValue.value = ''
  currentPage.value = 1
  loadRows()
}

function formatSize(size: number | undefined) {
  if (!size) return '-'
  if (size < 1024) return size + ' B'
  if (size < 1024 * 1024) return (size / 1024).toFixed(1) + ' KB'
  return (size / 1024 / 1024).toFixed(1) + ' MB'
}

onMounted(() => {
  fetchDetail()
  loadRows()
})
</script>

<style scoped lang="scss">
.flex-between { display: flex; justify-content: space-between; align-items: center; }
.filter-bar { display: flex; gap: 8px; align-items: center; }
.pagination-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
  .total-info { font-size: 13px; color: rgba(255,255,255,0.4); }
}
</style>
