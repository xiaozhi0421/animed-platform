<template>
  <div class="analysis-library page-container">
    <el-card>
      <template #header>
        <div class="flex-between">
          <span><el-icon><Folder /></el-icon> 分析库</span>
          <el-button size="small" @click="fetchLibrary">刷新</el-button>
        </div>
      </template>
      <el-table :data="libraryList" border stripe size="small" v-loading="libLoading" empty-text="暂无保存的分析记录">
        <el-table-column prop="datasetName" label="数据集名称" min-width="160" />
        <el-table-column prop="analysisTypeLabel" label="分析类型" width="120">
          <template #default="{row}">
            <el-tag size="small" :type="tv(row.analysisType)">{{ row.analysisTypeLabel }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="createdBy" label="创建人" width="100" />
        <el-table-column prop="createTime" label="创建时间" width="170" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{row}">
            <el-button size="small" type="primary" link @click="viewLibraryItem(row.id)"><el-icon><View /></el-icon> 查看</el-button>
            <el-button size="small" type="success" link @click="exportLibraryItem(row.id)"><el-icon><Download /></el-icon> 导出</el-button>
            <el-button size="small" type="danger" link @click="deleteLibraryItem(row.id)"><el-icon><Delete /></el-icon> 删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    <el-dialog v-model="detailDialogVisible" title="分析详情" width="80%" top="5vh" destroy-on-close>
      <template v-if="detailItem">
        <div style="margin-bottom:12px;">
          <el-tag style="margin-right:8px;">数据集: {{ detailItem.datasetName }}</el-tag>
          <el-tag type="info">分析类型: {{ detailItem.analysisTypeLabel }}</el-tag>
        </div>
        <pre style="max-height:500px;overflow:auto;background:rgba(0,0,0,0.3);padding:16px;border-radius:8px;font-size:13px;line-height:1.6;white-space:pre-wrap;">{{ detailItem.resultJson }}</pre>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue"
import { analysisLibraryApi } from "@/api"
import { ElMessage, ElMessageBox } from "element-plus"

const libraryList = ref<any[]>([])
const libLoading = ref(false)
const detailDialogVisible = ref(false)
const detailItem = ref<any>(null)

function tv(t: string) { return t === "descriptive" ? "primary" : t === "distribution" ? "success" : "warning" }

async function fetchLibrary() {
  libLoading.value = true
  try {
    const res: any = await analysisLibraryApi.getAnalysisList()
    libraryList.value = res.data || []
  } catch {
    libraryList.value = []
  } finally {
    libLoading.value = false
  }
}

async function viewLibraryItem(id: number) {
  try {
    const res: any = await analysisLibraryApi.getAnalysisDetail(id)
    detailItem.value = res.data
    detailDialogVisible.value = true
  } catch {
    ElMessage.error("获取详情失败")
  }
}

async function exportLibraryItem(id: number) {
  try {
    const res: any = await analysisLibraryApi.exportAnalysis(id)
    const blob = new Blob([res.data || "无数据"], { type: "text/plain" })
    const a = document.createElement("a")
    a.href = URL.createObjectURL(blob)
    a.download = "分析报告_" + id + ".txt"
    a.click()
    ElMessage.success("导出成功")
  } catch {
    ElMessage.error("导出失败")
  }
}

async function deleteLibraryItem(id: number) {
  try {
    await ElMessageBox.confirm("确定删除这条分析记录吗？", "删除确认", { type: "warning" })
    await analysisLibraryApi.deleteAnalysis(id)
    ElMessage.success("已删除")
    fetchLibrary()
  } catch {}
}

onMounted(fetchLibrary)
</script>

<style scoped>
.flex-between { display: flex; justify-content: space-between; align-items: center; }
</style>
