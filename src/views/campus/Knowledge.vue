<template>
  <div class="knowledge page-container">
    <el-row :gutter="20">
      <!-- Left: Search + Document List -->
      <el-col :span="16">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>📚 知识库文档</span>
              <el-button type="primary" size="small" @click="refreshDocList">刷新</el-button>
            </div>
          </template>

          <!-- Search Bar -->
          <el-form :inline="true" :model="searchForm" class="search-form">
            <el-form-item label="关键词" style="flex:1">
              <el-input v-model="searchForm.keyword" placeholder="搜索文档标题/内容/作者..." clearable
                @keyup.enter="doSearch" />
            </el-form-item>
            <el-form-item label="分类">
              <el-select v-model="searchForm.category" placeholder="全部分类" clearable style="width:160px"
                @change="doSearch">
                <el-option v-for="c in categories" :key="c" :label="c" :value="c" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :loading="searching" @click="doSearch">搜索</el-button>
            </el-form-item>
          </el-form>

          <!-- Document Table with Pagination -->
          <div v-if="docList.length" class="doc-table-wrap">
            <el-table :data="paginatedDocs" style="width:100%" stripe size="small" @row-click="viewDetail">
              <el-table-column prop="title" label="标题" min-width="180" show-overflow-tooltip />
              <el-table-column prop="author" label="作者" width="100" />
              <el-table-column prop="category" label="分类" width="120">
                <template #default="{ row }">
                  <el-tag :type="row.category === '未分类' ? 'info' : 'success'" size="small">{{ row.category }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column label="时间" width="150">
                <template #default="{ row }">
                  {{ formatTime(row.createTime) }}
                </template>
              </el-table-column>
              <el-table-column label="操作" width="80" fixed="right">
                <template #default="{ row }">
                  <el-button type="danger" size="small" link @click.stop="handleDeleteDoc(row.id)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>

            <div class="pagination-wrap">
              <el-pagination
                v-model:current-page="currentPage"
                :page-size="pageSize"
                :total="docList.length"
                layout="total, prev, pager, next"
                size="small" />
            </div>
          </div>
          <el-empty v-else description="暂无文档，请先在右侧上传" :image-size="80" />
        </el-card>

        <!-- AI Search Results -->
        <el-card v-if="searchResults.length" style="margin-top:16px">
          <template #header><span>🔍 RAG 搜索结果</span></template>
          <div v-for="item in searchResults" :key="item.documentId" class="result-item" @click="viewDetail(item.documentId)">
            <h4>{{ item.title }}</h4>
            <div class="result-meta">
              <span v-if="item.author">作者: {{ item.author }}</span>
              <el-tag v-if="item.category" size="small" type="info">{{ item.category }}</el-tag>
              <span v-if="item.score" class="score">相似度: {{ (item.score * 100).toFixed(1) }}%</span>
            </div>
            <p class="result-content">{{ item.content }}</p>
          </div>
        </el-card>
      </el-col>

      <!-- Right: Upload & Preview -->
      <el-col :span="8">
        <el-card>
          <template #header><span>📤 上传文档</span></template>
          <el-upload drag :auto-upload="false" accept=".txt,.doc,.docx,.pdf" :limit="1"
            :on-change="handleFileChange" :on-remove="handleFileRemove" :before-upload="beforeUpload">
            <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
            <div class="el-upload__text">拖拽或点击上传</div>
            <template #tip><div class="el-upload__tip">支持 TXT、Word(.doc/.docx)、PDF</div></template>
          </el-upload>
          <el-button type="primary" style="margin-top:12px;width:100%" :loading="uploading"
            :disabled="!uploadFile" @click="previewUpload">📄 预览文档</el-button>
        </el-card>

        <!-- Preview Card -->
        <el-card v-if="previewData" style="margin-top:16px">
          <template #header><span>📝 预览 <el-tag size="small" type="warning">待审核</el-tag></span></template>
          <el-form :model="editForm" label-width="60px" size="small">
            <el-form-item label="标题">
              <el-input v-model="editForm.title" placeholder="请输入文档标题" />
            </el-form-item>
            <el-form-item label="作者">
              <el-input v-model="editForm.author" placeholder="自动提取或手动输入" />
            </el-form-item>
            <el-form-item label="分类">
              <el-select v-model="editForm.category" style="width:100%">
                <el-option v-for="c in categories.filter(x => x !== '全部')" :key="c" :label="c" :value="c" />
              </el-select>
            </el-form-item>
          </el-form>
          <el-divider />
          <div class="preview-content" v-html="renderedContent"></div>
          <div style="margin-top:12px;display:flex;gap:8px">
            <el-button type="primary" :loading="confirming" @click="confirmUpload">确认入库</el-button>
            <el-button @click="cancelPreview">取消</el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>


        <!-- Document Detail Dialog -->
    <el-dialog v-model="detailVisible" title="文档详情" width="60%" destroy-on-close>
      <template v-if="detailDoc">
        <h3>{{ detailDoc.title }}</h3>
        <p style="color:#666;font-size:13px">
          作者: {{ detailDoc.author || '未知' }} |
          分类: <el-tag size="small">{{ detailDoc.category }}</el-tag> |
          时间: {{ detailDoc.createTime }}
        </p>
        <el-divider />
        <div class="detail-content" v-html="renderDocumentContent(detailDoc.content)"></div>
      </template>
      <template #footer>
        <el-button @click="detailVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from "vue"
import { analysisApi } from "@/api"
import { ElMessage, ElMessageBox } from "element-plus"
import type { UploadFile } from "element-plus"
import { User, Clock } from "@element-plus/icons-vue"

const DEFAULT_CATS = [
  "全部", "牛羊医学", "小动物医学", "宠物医学",
  "马医学", "家禽医学", "疾病诊断", "药物学",
  "外科学", "内科学", "用药指南", "常见病防治",
  "医疗操作规范", "实验室检验", "影像学诊断",
  "食品安全", "动物健康管理", "公共卫生", "未分类"
]

const searchForm = ref({ keyword: "", category: "" })
const searching = ref(false)
const docList = ref<any[]>([])
const searchResults = ref<any[]>([])
const categories = ref<string[]>([...DEFAULT_CATS])

const uploadFile = ref<File | null>(null)
const uploading = ref(false)
const confirming = ref(false)




const previewData = ref<any>(null)
const editForm = ref({ title: "", author: "", category: "" })

const detailVisible = ref(false)
const detailDoc = ref<any>(null)

const currentPage = ref(1)
const pageSize = ref(15)

const paginatedDocs = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return docList.value.slice(start, start + pageSize.value)
})

function formatTime(t: string) {
  if (!t) return ""
  return t.substring(0, 10)
}

function renderDocumentContent(content: string) {
  if (!content) return ""
  let html = content
    .replace(/</g, "&lt;").replace(/>/g, "&gt;")
    .replace(/\n/g, "<br>")
  html = html.replace(/!\[(.*?)\]\((.*?)\)/g, (_m: string, alt: string, src: string) => {
    const url = src.startsWith("http") ? src : (src.startsWith("/") ? src : "/" + src)
    return '<img src="' + url + '" alt="' + alt + '" class="doc-image" />'
  })
  return html
}

const renderedContent = computed(() => renderDocumentContent(previewData.value?.content || ""))

onMounted(() => {
  loadCategories()
  loadDocList()
})

async function loadCategories() {
  try {
    const res: any = await analysisApi.getKnowledgeCategories()
    if (res?.data?.length) categories.value = res.data
  } catch { }
}

async function loadDocList() {
  try {
    const res: any = await analysisApi.getKnowledgeDocs({})
    docList.value = res.data || []
    currentPage.value = 1
  } catch { docList.value = [] }
}

async function refreshDocList() {
  await loadDocList()
  ElMessage.success("已刷新")
}

function beforeUpload(file: File) {
  const ext = file.name.split(".").pop()?.toLowerCase()
  if (!["txt", "doc", "docx", "pdf"].includes(ext || "")) {
    ElMessage.error("仅支持 TXT、Word(.doc/.docx)、PDF 格式")
    return false
  }
  return true
}

function handleFileChange(obj: UploadFile) {
  const ext = obj.name?.split(".").pop()?.toLowerCase()
  if (!["txt", "doc", "docx", "pdf"].includes(ext || "")) {
    ElMessage.error("仅支持 TXT、Word(.doc/.docx)、PDF 格式")
    uploadFile.value = null
    return
  }
  uploadFile.value = obj.raw || null
}

function handleFileRemove() { uploadFile.value = null }

async function previewUpload() {
  if (!uploadFile.value) return
  uploading.value = true
  try {
    const fd = new FormData()
    fd.append("file", uploadFile.value)
    const res = await analysisApi.knowledgePreview(fd)
    previewData.value = res.data
    const detectedCategory = res.data?.category || "未分类"
    editForm.value = {
      title: res.data.title || "",
      author: res.data.author || "",
      category: detectedCategory
    }
    // 后端 previewFile 已经自动调用了 classifyContent，分类结果就在 res.data.category 中
    if (detectedCategory !== "未分类" && detectedCategory !== "其他") {
      ElMessage.success("AI建议分类: " + detectedCategory)
    }
  } catch (e) {
    ElMessage.error("预览失败: " + (e.message || "未知错误"))
  } finally { uploading.value = false }
}
async function confirmUpload() {
  if (!editForm.value.title) { ElMessage.warning("请输入标题"); return }
  confirming.value = true
  try {
    await analysisApi.knowledgeUpload({
      title: editForm.value.title,
      author: editForm.value.author,
      content: previewData.value.content,
      category: editForm.value.category,
      fileName: previewData.value.fileName
    })
    ElMessage.success("文档已入库")
    previewData.value = null
    uploadFile.value = null
    await loadDocList()
    await loadCategories()
  } catch (e: any) {
    ElMessage.error("入库失败: " + (e.message || "未知错误"))
  } finally { confirming.value = false }
}

function cancelPreview() { previewData.value = null }

async function doSearch() {
  searching.value = true
  searchResults.value = []

  if (searchForm.value.keyword) {
    try {
      const res: any = await analysisApi.knowledgeSearch({
        query: searchForm.value.keyword,
        category: searchForm.value.category === "全部" ? undefined : searchForm.value.category
      })
      if (res.data?.matches) searchResults.value = res.data.matches
    } catch {}
  }

  try {
    const params: any = {}
    if (searchForm.value.keyword) params.title = searchForm.value.keyword
    if (searchForm.value.category && searchForm.value.category !== "全部") params.category = searchForm.value.category
    const res: any = await analysisApi.getKnowledgeDocs(params)
    docList.value = res.data || []
    currentPage.value = 1
  } catch { }
  searching.value = false
}

async function viewDetail(doc: any) {
  const docId = typeof doc === "object" ? doc.id : doc
  try {
    const res: any = await analysisApi.getKnowledgeDoc(docId)
    detailDoc.value = res.data
    detailVisible.value = true
  } catch { ElMessage.error("获取文档详情失败") }
}

async function handleDeleteDoc(docId: number) {
  try {
    await ElMessageBox.confirm("确定删除该文档？同时删除所有分块数据。", "提示", { type: "warning" })
    await analysisApi.deleteKnowledgeDoc(docId)
    ElMessage.success("已删除")
    await loadDocList()
  } catch {}
}

</script>