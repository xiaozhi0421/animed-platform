<template>
  <div class="submission-center page-container">
    <!-- Student View -->
    <template v-if="!isTeacher">
      <el-tabs v-model="studentTab" type="border-card">
        <!-- Tab 1: 可选择课题 -->
        <el-tab-pane label="可选择课题" name="available">
        <!-- AI 智能推荐课题 -->
        <el-card v-if="topicLoading" style="margin-bottom:16px;background:linear-gradient(135deg,#667eea,#764ba2)">
          <div style="text-align:center;padding:20px 0">
            <el-icon class="is-loading" :size="28" style="color:rgba(255,255,255,0.9)"><Loading /></el-icon>
            <p style="margin-top:8px;color:rgba(255,255,255,0.8);font-size:14px">AI 正在分析你的专业和可用课题...</p>
            <p style="margin-top:4px;color:rgba(255,255,255,0.5);font-size:12px">正在拼命思考中，请稍候...</p>
          </div>
        </el-card>
        <el-card v-else-if="topicRecommendations" style="margin-bottom:16px;background:linear-gradient(135deg,#667eea,#764ba2)">
          <template #header>
            <div style="display:flex;justify-content:space-between;align-items:center">
              <span style="color:#fff;font-weight:500">🧠 AI 智能推荐课题</span>
              <el-button size="small" :loading="topicLoading" text @click="fetchTopicRecommendations" style="color:rgba(255,255,255,0.8)">刷新</el-button>
            </div>
          </template>
          <div style="white-space:pre-wrap;line-height:1.6;font-size:14px;color:rgba(255,255,255,0.9)">{{ topicRecommendations }}</div>
        </el-card>
        <el-card v-else style="margin-bottom:16px;background:linear-gradient(135deg,#667eea,#764ba2);cursor:pointer" @click="fetchTopicRecommendations">
          <div style="text-align:center;padding:12px 0;color:rgba(255,255,255,0.9)">
            <span style="font-size:15px">🧠 点击让 AI 根据你的专业推荐课题</span>
          </div>
        </el-card>
          <el-table :data="paginatedAvailable" stripe v-loading="loading" empty-text="暂无可选择课题">
            <el-table-column prop="title" label="课题名称" min-width="200" />
            <el-table-column prop="teacherName" label="发布教师" width="130" />
            <el-table-column prop="experiments" label="已选实验" min-width="250" show-overflow-tooltip>
              <template #default="{ row }">
                <span v-if="row.experiments" style="font-size:12px;color:#94a3b8;">{{ row.experiments }}</span>
                <span v-else style="font-size:12px;color:#94a3b8;">-</span>
              </template>
            </el-table-column>
            <el-table-column prop="createTime" label="发布时间" width="170" />
            <el-table-column label="操作" width="120" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" size="small" @click="confirmAvailableTopic(row)">确认选择</el-button>
              </template>
            </el-table-column>
          </el-table>
          <div style="display:flex;justify-content:flex-end;margin-top:12px">
            <el-pagination v-model:current-page="availablePage" :page-size="10" :total="availableTopics.length" layout="prev, pager, next" size="small" background @current-change="updatePaginatedMyTopics" />
          </div>        </el-tab-pane>
        <!-- Tab 2: 待完成课题 -->
        <el-tab-pane label="待完成课题" name="pending">
          <el-table :data="paginatedPending" stripe v-loading="loading2" empty-text="暂无待完成课题">
            <el-table-column prop="title" label="课题名称" min-width="200" />
            <el-table-column prop="teacherName" label="指导老师" width="130" />
            <el-table-column prop="description" label="描述" min-width="250" show-overflow-tooltip />
            <el-table-column label="提交状态" width="110" align="center">
              <template #default="{ row }">
                <el-tag v-if="row.status === 1" type="info">未提交</el-tag>
                <el-tag v-else-if="row.status === 2" type="warning">已提交</el-tag>
                <el-tag v-else-if="row.status === 3" type="danger">已打回</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="260" fixed="right">
              <template #default="{ row }">
                <el-button v-if="row.status % 2 === 1" type="success" size="small" @click="openSubmitDialog(row)">提交成果</el-button>
                <el-button v-else type="success" size="small" disabled>已提交</el-button>
                <el-button size="small" type="info" plain @click="viewTopic(row)">查看详情</el-button>
              </template>
            </el-table-column>
          </el-table>
          <div style="display:flex;justify-content:flex-end;margin-top:12px">
            <el-pagination v-model:current-page="pendingPage" :page-size="10" :total="pendingTopics.length" layout="prev, pager, next" size="small" background @current-change="updatePaginatedPending" />
          </div>        </el-tab-pane>
        <!-- Tab 3: 已完成课题 -->
        <el-tab-pane label="已完成课题" name="completed">
          <el-table :data="paginatedCompleted" stripe v-loading="loading3" empty-text="暂无已完成课题">
            <el-table-column prop="title" label="课题名称" min-width="200" />
            <el-table-column prop="teacherName" label="指导老师" width="130" />
            <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
            <el-table-column label="评分" width="80" align="center">
              <template #default="{ row }">
                <el-tag type="success">已通过</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="状态" width="100" align="center">
              <template #default="{ row }">
                <el-tag type="success">已通过</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="120" fixed="right">
              <template #default="{ row }">
                <el-button size="small" type="primary" @click="viewSubmissionDetail(row)">查看详情</el-button>
              </template>
            </el-table-column>
          </el-table>
          <div style="display:flex;justify-content:flex-end;margin-top:12px">
            <el-pagination v-model:current-page="completedPage" :page-size="10" :total="completedTopics.length" layout="prev, pager, next" size="small" background @current-change="updatePaginatedCompleted" />
          </div>        </el-tab-pane>
      </el-tabs>
    </template>
    <!-- Teacher View -->
    <template v-else>
      <el-tabs v-model="teacherTab" type="border-card">
        <!-- Tab 1: 我发布课题 -->
        <el-tab-pane label="我发布课题" name="myTopics">
          <el-button type="primary" style="margin-bottom:12px" @click="showCreateDialog = true">
            <el-icon><Plus /></el-icon> 创建新课题
          </el-button>
          <el-table :data="paginatedMyTopics" stripe v-loading="loading" empty-text="暂无已发布课题">
            <el-table-column prop="title" label="课题名称" min-width="220" />
            <el-table-column prop="description" label="描述" min-width="250" show-overflow-tooltip />
            <el-table-column prop="createTime" label="发布时间" width="170" />
            <el-table-column label="确认人数" width="100" align="center">
              <template #default="{ row }">
                {{ getConfirmedCount(row.id) }}
              </template>
            </el-table-column>
            <el-table-column label="AI阈值" width="100" align="center">
              <template #default="{ row }">
                <el-tag size="small" @click="openThresholdEdit(row)" style="cursor:pointer">{{ row.reviewThreshold ?? 70 }}%</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100" fixed="right">
              <template #default="{ row }">
                <el-button size="small" type="warning" plain @click="openThresholdEdit(row)">修改阈值</el-button>
              </template>
            </el-table-column>
          </el-table>
          <div style="display:flex;justify-content:flex-end;margin-top:12px">
            <el-pagination v-model:current-page="teacherPage" :page-size="10" :total="myPublishedTopics.length" layout="prev, pager, next" size="small" background @current-change="updatePaginatedMyTopics" />
          </div>        </el-tab-pane>
        <!-- Tab 2: 学生提交课题 -->
        <el-tab-pane label="学生提交课题" name="submissions">
          <el-table :data="paginatedTeacherSubmissions" stripe v-loading="loading4" empty-text="暂无学生提交">
            <el-table-column prop="topicTitle" label="课题名称" min-width="180" />
            <el-table-column prop="studentName" label="学生" width="100" />
            <el-table-column label="版本" width="70" align="center">
              <template #default="{ row }">
                <el-tag size="small">v{{ row.version || 1 }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="createTime" label="提交时间" width="160" />
            <el-table-column label="状态" width="80" align="center">
              <template #default="{ row }">
                <el-tag v-if="row.status === 4" type="success">已通过</el-tag>
                <el-tag v-else-if="row.status === 3" type="danger">已打回</el-tag>
                <el-tag v-else type="warning">待审批</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="220" fixed="right">
              <template #default="{ row }">
                <el-button size="small" type="primary" @click="viewStudentSubmission(row)">查看详情</el-button>
                <el-button v-if="row.status === 2" size="small" type="success" @click="showPassDialog(row)">通过</el-button>
                <el-button v-if="row.status === 2" size="small" type="danger" @click="showRejectDialog(row)">打回</el-button>
              </template>
            </el-table-column>
          </el-table>
          <div style="display:flex;justify-content:flex-end;margin-top:12px">
            <el-pagination v-model:current-page="teacherSubmissionPage" :page-size="10" :total="teacherSubmissions.length" layout="prev, pager, next" size="small" background @current-change="updatePaginatedTeacherSubmissions" />
          </div>        </el-tab-pane>
      </el-tabs>
    </template>
    <!-- Create Topic Dialog -->
    <el-dialog v-model="showCreateDialog" title="创建新课题" width="600px">
      <el-form :model="createForm" label-position="top">
        <el-form-item label="课题名称">
          <el-input v-model="createForm.title" placeholder="请输入课题名称" />
        </el-form-item>
        <el-form-item label="课题描述">
          <el-input v-model="createForm.description" type="textarea" :rows="4" placeholder="请描述课题内容、要求等" />
        </el-form-item>
        <el-form-item label="AI智能推荐">
          <div style="display:flex;gap:8px;margin-bottom:8px;">
            <el-input v-model="aiInput" placeholder="输入关键词获取推荐课题" />
            <el-button type="primary" @click="fetchAiSuggestions" :loading="aiLoading">推荐</el-button>
          </div>
          <div v-if="aiSuggestions.length" style="display:flex;flex-wrap:wrap;gap:6px;">
            <el-tag v-for="(s, i) in aiSuggestions" :key="i" closable @close="aiSuggestions.splice(i,1)" style="cursor:pointer;max-width:100%;white-space:normal;height:auto;padding:4px 8px;line-height:1.4" @click="createForm.title = s">
              {{ s }}
            </el-tag>
          </div>
        </el-form-item>
      
        <el-form-item label="AI 审阅阈值">
          <div style="display:flex;align-items:center;gap:12px">
            <el-slider v-model="reviewThreshold" :min="0" :max="100" :step="1" style="flex:1;min-width:200px" />
            <el-tag>{{ reviewThreshold }}%</el-tag>
          </div>
          <div style="font-size:12px;color:#94a3b8;margin-top:4px">AI 审阅阈值：学生提交成果时，关联度高于此值才能提交给教师审批</div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="handleCreateTopic" :loading="submitting">创建</el-button>
      </template>
    </el-dialog>
    <!-- Threshold Edit Dialog -->
    <el-dialog v-model="showThresholdEdit" title="修改 AI 审阅阈值" width="450px">
      <el-form label-position="top">
        <el-form-item label="课题名称">
          <el-input :model-value="editingTopic?.title" disabled />
        </el-form-item>
        <el-form-item label="AI 审阅阈值">
          <div style="display:flex;align-items:center;gap:12px">
            <el-slider v-model="editThresholdValue" :min="0" :max="100" :step="1" style="flex:1;min-width:200px" />
            <el-tag>{{ editThresholdValue }}%</el-tag>
          </div>
          <div style="font-size:12px;color:#94a3b8;margin-top:4px">学生提交成果时，关联度高于此值才能提交给教师审批</div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showThresholdEdit = false">取消</el-button>
        <el-button type="primary" @click="handleSaveThreshold" :loading="submitting">保存</el-button>
      </template>
    </el-dialog>
    <!-- Submit Dialog -->
    <el-dialog v-model="showSubmitDialog" :title="'提交成果 - ' + (currentSubmitTopic?.title || '')" width="700px" destroy-on-close>
      <el-form :model="submitForm" label-position="top">
        <el-form-item label="课题描述">
          <el-input v-model="submitForm.description" type="textarea" :rows="3" placeholder="描述你的研究成果..." />
        </el-form-item>
        <el-form-item label="上传文件">
          <el-upload ref="uploadRef" :auto-upload="false" :limit="10" :on-change="handleFileChange" :before-upload="()=>false" :file-list="uploadFileList" multiple drag>
            <el-icon class="el-icon--upload" :size="48"><UploadFilled /></el-icon>
            <div class="el-upload__text">拖拽文件到此处 <em>点击上传</em></div>
            <template #tip><div style="font-size:12px;color:#999;">支持常见文件格式，单个不超过50MB</div></template>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showSubmitDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSubmitWithAIReview" :loading="submitting">AI 审阅后提交</el-button>
      </template>
    </el-dialog>
    <!-- View Detail Dialog -->
    <el-dialog v-model="showDetailDialog" :title="'提交详情'" width="800px" destroy-on-close>
      <template v-if="detailData">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="课题名称">{{ detailData.title || detailData.topicTitle }}</el-descriptions-item>
          <el-descriptions-item label="提交学生">{{ detailData.studentName || '我' }}</el-descriptions-item>
          <el-descriptions-item label="评分">{{ detailData.score ?? '未评分' }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="detailData.status === 4 ? 'success' : detailData.status === 3 ? 'danger' : 'warning'">
              {{ detailData.status === 4 ? '已通过' : detailData.status === 3 ? '已打回' : '待审批' }}
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>
        <div style="margin-top:16px;">
          <h4 style="margin-bottom:8px;">提交内容</h4>
          <div v-if="detailData.description && detailData.description !== '无'" style="background:rgba(255,255,255,0.05);border-radius:8px;padding:16px;font-size:13px;line-height:1.7;white-space:pre-wrap;max-height:400px;overflow-y:auto;color:#e2e8f0">
            {{ detailData.description }}
          </div>
          <div v-else style="color:#94a3b8;font-size:13px;">无提交内容</div>
        </div>
        <div v-if="detailFiles.length" style="margin-top:16px;">
          <h4 style="margin-bottom:8px;">上传文件</h4>
          <div v-for="f in detailFiles" :key="f.id" style="margin:6px 0;display:flex;align-items:center;gap:10px;padding:8px 12px;background:rgba(255,255,255,0.03);border-radius:6px;border:1px solid rgba(255,255,255,0.06)">
            <el-icon><Document /></el-icon>
            <span style="flex:1">{{ f.fileName }}</span>
            <span style="color:#94a3b8;font-size:12px;">{{ formatSize(f.fileSize) }}</span>
            <el-button size="small" type="primary" @click="downloadFile(f)">下载</el-button>
          </div>
        </div>
        <!-- AI score if available -->
        <div v-if="detailData.aiScore !== undefined && detailData.aiScore !== null" style="margin-top:12px;">
          <el-tag :type="(detailData.aiScore ?? 0) >= 70 ? 'success' : 'danger'">
            AI 审阅得分: {{ detailData.aiScore }}/100
          </el-tag>
        </div>
      </template>
    </el-dialog>
    <!-- Teacher Pass Dialog -->
    <el-dialog v-model="showPassDialogFlag" title="通过评分" width="450px">
      <el-form :model="reviewForm" label-position="top">
        <el-form-item label="评分">
          <el-input-number v-model="reviewForm.score" :min="0" :max="100" />
        </el-form-item>
        <el-form-item label="评语">
          <el-input v-model="reviewForm.comment" type="textarea" :rows="3" placeholder="可选评语" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showPassDialogFlag = false">取消</el-button>
        <el-button type="success" @click="handlePass" :loading="submitting">确认通过</el-button>
      </template>
    </el-dialog>
    <!-- Teacher Reject Dialog -->
    <el-dialog v-model="showRejectDialogFlag" title="打回原因" width="450px">
      <el-form :model="rejectForm" label-position="top">
        <el-form-item label="打回原因">
          <el-input v-model="rejectForm.reason" type="textarea" :rows="3" placeholder="请说明打回原因" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showRejectDialogFlag = false">取消</el-button>
        <el-button type="danger" @click="handleReject" :loading="submitting">确认打回</el-button>
      </template>
    </el-dialog>
    <!-- View Topic Dialog -->
    <el-dialog v-model="showViewTopic" title="课题详情" width="700px" destroy-on-close>
      <div v-if="viewingTopic" style="padding:8px 0">
        <p><strong>课题名称：</strong>{{ viewingTopic.title }}</p>
        <p><strong>描述：</strong>{{ viewingTopic.description || '暂无描述' }}</p>
        <p><strong>发布教师：</strong>{{ viewingTopic.teacherName || '-' }}</p>
        <div style="margin-top:16px">
          <h4 style="margin-bottom:8px;font-size:14px">已选实验</h4>
          <el-table :data="topicExperiments" stripe size="small" v-loading="topicDetailLoading" empty-text="暂无实验数据">
            <el-table-column prop="experimentName" label="实验名称" min-width="200" />
            <el-table-column prop="isCustom" label="来源" width="80">
              <template #default="{ row }">
                <el-tag v-if="row.isCustom" size="small" type="warning">自定义</el-tag>
                <el-tag v-else size="small" type="success">推荐</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
      <template #footer>
        <el-button @click="showViewTopic = false">关闭</el-button>
      </template>
    </el-dialog>
    <!-- AI Experiment Dialog -->
    <el-dialog v-model="showExperimentDialog" title="AI 推荐实验" width="800px" destroy-on-close :close-on-click-modal="false">
      <div v-if="experimentLoading" style="text-align:center;padding:40px">
        <el-icon class="is-loading" :size="32"><Loading /></el-icon>
        <p style="margin-top:12px;color:#94a3b8;">AI 正在分析课题，推荐相关实验...</p>
      </div>
      <template v-else>
        <div v-if="recommendedExperiments.length === 0" style="text-align:center;padding:20px;color:#94a3b8;">
          暂无推荐实验，请手动添加
        </div>
        <div v-else style="max-height:400px;overflow-y:auto;padding:4px 0">
          <div v-for="exp in recommendedExperiments" :key="exp.id || exp.name"
               style="display:flex;align-items:flex-start;padding:10px 12px;margin-bottom:8px;border-radius:8px;cursor:pointer;transition:all 0.2s;border:1px solid rgba(255,255,255,0.08);background:rgba(255,255,255,0.03)"
               :style="selectedExperiments.has(exp.name) ? 'background:rgba(64,158,255,0.15);border:1px solid rgba(64,158,255,0.3)' : ''"
               @click="toggleExperiment(exp.name)">
            <span style="display:inline-flex;width:16px;height:16px;border-radius:3px;margin-right:12px;flex-shrink:0;align-items:center;justify-content:center;font-size:12px;transition:all 0.2s;cursor:pointer" :style="selectedExperiments.has(exp.name) ? 'background:#409eff;border:1px solid #409eff;color:#fff' : 'border:1px solid #aaa;color:transparent'" @click.stop="toggleExperiment(exp.name)">?</span>
            <div style="flex:1">
              <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap">
                <span style="font-weight:600;font-size:14px;color:#fff">{{ exp.name }}</span>
                <el-tag v-if="exp.category" size="small" effect="plain" style="background:rgba(255,255,255,0.1);color:rgba(255,255,255,0.7);border:none">{{ exp.category }}</el-tag>
                <el-tag v-if="exp.estimatedDuration" size="small" effect="plain" style="background:rgba(255,255,255,0.1);color:rgba(255,255,255,0.7);border:none">约 {{ exp.estimatedDuration }}</el-tag>
              </div>
              <p style="font-size:12px;color:rgba(255,255,255,0.5);margin-top:4px">{{ exp.description }}</p>
            </div>
          </div>
        </div>
        <div style="display:flex;gap:8px;margin-top:12px;padding:0 12px">
          <el-input v-model="customExperimentInput" placeholder="输入自定义实验名称..." style="flex:1" size="small" @keyup.enter="addCustomExperiment" />
          <el-button size="small" @click="addCustomExperiment">添加</el-button>
        </div>
        <div v-if="customExperiments.length > 0" style="margin-top:8px;padding:0 12px">
          <span style="font-size:12px;color:rgba(255,255,255,0.5)">自定义实验：</span>
          <el-tag v-for="(ce, idx) in customExperiments" :key="idx" closable style="margin:2px" @close="removeCustomExperiment(idx)">{{ ce }}</el-tag>
        </div>
      </template>
      <template #footer>
        <el-button @click="showExperimentDialog = false">取消</el-button>
        <el-button type="primary" :loading="confirming" :disabled="selectedExperiments.size === 0 && customExperiments.length === 0" @click="confirmExperimentSelection">确认选择（已选 {{ selectedExperiments.size + customExperiments.length }} 项）</el-button>
      </template>
    </el-dialog>
    <!-- AI Equipment Dialog -->
    <el-dialog v-model="showEquipDialog" title="AI 推荐仪器预约" width="800px" destroy-on-close :close-on-click-modal="false">
      <div v-if="equipLoading" style="text-align:center;padding:40px">
        <el-icon class="is-loading" :size="32"><Loading /></el-icon>
        <p style="margin-top:12px;color:#94a3b8;">AI 正在根据实验推荐仪器...</p>
      </div>
      <template v-else>
        <div v-if="recommendedEquipments.length === 0" style="text-align:center;padding:20px;color:#94a3b8;">
          暂无推荐仪器
        </div>
        <div v-else style="max-height:400px;overflow-y:auto">
          <div v-for="eq in recommendedEquipments" :key="eq.equipmentId" style="padding:12px 14px;margin-bottom:8px;background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.06);border-radius:10px">
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px">
              <el-icon><Monitor /></el-icon>
              <span style="font-weight:600;font-size:14px;color:#e2e8f0">{{ eq.name }}</span>
              <el-tag v-if="eq.experimentName" size="small" type="success" style="margin-right:4px">{{ eq.experimentName }}</el-tag>
              <el-tag v-if="eq.reason" size="small">{{ eq.reason }}</el-tag>
              <el-date-picker v-model="equipDates[eq.equipmentId]" type="date" placeholder="选择日期" :disabled-date="d => d < new Date()" style="width:160px" @change="(d) => loadEquipSlots(eq.equipmentId, d)" />
              <div v-if="equipSlots[eq.equipmentId] && equipSlots[eq.equipmentId].length > 0" style="display:flex;gap:4px;flex-wrap:wrap">
                <div v-for="s in equipSlots[eq.equipmentId]" :key="s.timeSlot"
                     style="padding:4px 10px;border-radius:6px;border:1px solid rgba(255,255,255,0.12);cursor:pointer;font-size:12px;color:#f1f5f9;transition:all 0.2s"
                     :style="equipSelectedSlots[eq.equipmentId] && equipSelectedSlots[eq.equipmentId].includes(s.timeSlot) ? 'background:rgba(99,102,241,0.2);border-color:#818cf8' : (s.available ? '' : 'opacity:0.35;cursor:not-allowed')"
                     @click="selectEquipSlot(eq.equipmentId, s)">
                  {{ s.timeSlot }}
                  <el-tag v-if="!s.available" size="small" type="danger">满</el-tag>
                </div>
              </div>
            </div>
          </div>
        </div>
      </template>
      <template #footer>
        <el-button @click="showEquipDialog = false">跳过预约</el-button>
        <el-button type="primary" :loading="aiReserving" @click="batchReserveAll">一键预约全部</el-button>
      </template>
    </el-dialog>
    <!-- AI Review Dialog -->
    <el-dialog v-model="showReviewDialog" title="AI 自动审阅" width="500px" :close-on-click-modal="false">
      <div v-if="reviewLoading" style="text-align:center;padding:40px">
        <el-icon class="is-loading" :size="32"><Loading /></el-icon>
        <p style="margin-top:12px;color:#94a3b8;">AI 正在审阅你的提交内容...</p>
      </div>
      <div v-else-if="reviewResult" style="padding:8px 0">
        <div style="text-align:center;margin-bottom:16px">
          <el-tag :type="reviewResult.passed ? 'success' : 'danger'" size="large" style="font-size:16px;padding:8px 20px">
            {{ reviewResult.passed ? '审阅通过' : '审阅未通过' }}
          </el-tag>
        </div>
        <div style="text-align:center;margin-bottom:16px">
          <span style="font-size:14px;color:#94a3b8">关联度评分：</span>
          <span style="font-size:24px;font-weight:700" :style="{color: reviewResult.passed ? '#22c55e' : '#ef4444'}">{{ reviewResult.score || 0 }}</span>
          <span style="color:#94a3b8">/100</span>
        </div>
        <div v-if="reviewResult.reason" style="padding:12px;background:rgba(255,255,255,0.05);border-radius:8px;font-size:13px;color:#e2e8f0;line-height:1.6;white-space:pre-wrap">{{ reviewResult.reason }}</div>
      </div>
      <template #footer>
        <el-button v-if="reviewResult && !reviewResult.passed" @click="showReviewDialog = false; showSubmitDialog = true">修改后重新提交</el-button>
        <el-button v-if="reviewResult && reviewResult.passed" type="primary" @click="showReviewDialog = false">知道了</el-button>
      </template>
    </el-dialog>
  </div>
</template>
<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { submissionApi, analysisApi } from '@/api'
import { get, post } from '@/utils/request'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/stores/user'
import * as pdfjsLib from 'pdfjs-dist'
import mammoth from 'mammoth'
import * as XLSX from 'xlsx'
const userStore = useUserStore()
const isTeacher = computed(() => userStore.userRole === 'campus_teacher')
const loading = ref(false)
const loading2 = ref(false)
const loading3 = ref(false)
const loading4 = ref(false)
const submitting = ref(false)
const aiLoading = ref(false)
// Student tabs
const studentTab = ref('available')
const availableTopics = ref<any[]>([])
const confirmedTopics = ref<any[]>([])
const completedTopics = ref<any[]>([])
// Pagination
const availablePage = ref(1)
const pendingPage = ref(1)
const completedPage = ref(1)
const teacherPage = ref(1)
const teacherSubmissionPage = ref(1)
const pageSize = 10
// Computed: merge confirmedTopics with submission status, filter out approved (status=1)
// Backend status: 0=pending review(已提交待审阅), 1=approved(已通过), 2=rejected(已打回)
// Frontend _status: 0=未提交, 1=已提交, 2=已打回
const pendingTopics = computed(() => {
  return confirmedTopics.value.filter((t: any) => {
    return t.status === 1 || t.status === 2 || t.status === 3
  }).map((t: any) => {
    return t
  })
})
const paginatedAvailable = ref<any[]>([])
const paginatedPending = ref<any[]>([])
const paginatedCompleted = ref<any[]>([])
const paginatedMyTopics = ref<any[]>([])
const paginatedTeacherSubmissions = ref<any[]>([])
function updatePaginatedAvailable() {
  const start = (availablePage.value - 1) * pageSize
  paginatedAvailable.value = availableTopics.value.slice(start, start + pageSize)
}
function updatePaginatedPending() {
  const start = (pendingPage.value - 1) * pageSize
  paginatedPending.value = pendingTopics.value.slice(start, start + pageSize)
}
function updatePaginatedCompleted() {
  const start = (completedPage.value - 1) * pageSize
  paginatedCompleted.value = completedTopics.value.slice(start, start + pageSize)
}
function updatePaginatedMyTopics() {
  const start = (teacherPage.value - 1) * pageSize
  paginatedMyTopics.value = myPublishedTopics.value.slice(start, start + pageSize)
}
function updatePaginatedTeacherSubmissions() {
  const start = (teacherSubmissionPage.value - 1) * pageSize
  paginatedTeacherSubmissions.value = teacherSubmissions.value.slice(start, start + pageSize)
}
watch(availableTopics, () => { availablePage.value = 1; updatePaginatedAvailable() }, { immediate: true })
const myPublishedTopics = ref<any[]>([])
const teacherSubmissions = ref<any[]>([])
watch(availablePage, updatePaginatedAvailable)
watch(pendingTopics, () => { pendingPage.value = 1; updatePaginatedPending() }, { immediate: true })
watch(pendingPage, updatePaginatedPending)
watch(completedTopics, () => { completedPage.value = 1; updatePaginatedCompleted() }, { immediate: true })
watch(completedPage, updatePaginatedCompleted)
watch(myPublishedTopics, () => { teacherPage.value = 1; updatePaginatedMyTopics() }, { immediate: true })
watch(teacherPage, updatePaginatedMyTopics)
watch(teacherSubmissions, () => { teacherSubmissionPage.value = 1; updatePaginatedTeacherSubmissions() }, { immediate: true })
watch(teacherSubmissionPage, updatePaginatedTeacherSubmissions)
const teacherTab = ref('myTopics')
const showCreateDialog = ref(false)
const showSubmitDialog = ref(false)
const showDetailDialog = ref(false)
const showPassDialogFlag = ref(false)
const showRejectDialogFlag = ref(false)
const currentSubmitTopic = ref<any>(null)
const currentReviewRecord = ref<any>(null)
const detailData = ref<any>(null)
const detailFiles = ref<any[]>([])
// Forms
const createForm = reactive({ title: '', description: '' })
const submitForm = reactive({ description: '' })
const reviewForm = reactive({ score: 80, comment: '' })
const rejectForm = reactive({ reason: '' })
const aiInput = ref('')
const aiSuggestions = ref<string[]>([])
const topicRecommendations = ref<string | null>(null)
const topicLoading = ref(false)
const uploadFileList = ref<any[]>([])
const showViewTopic = ref(false)
const viewingTopic = ref<any>(null)
const topicExperiments = ref<any[]>([])
const topicReservations = ref<any[]>([])
const topicDetailLoading = ref(false)
// AI Experiment Dialog
const showExperimentDialog = ref(false)
const experimentLoading = ref(false)
const recommendedExperiments = ref<any[]>([])
const selectedExperiments = ref<Set<string>>(new Set())
const customExperiments = ref<string[]>([])
const customExperimentInput = ref('')
const confirming = ref(false)
const currentTopic = ref<any>(null)
// AI Equipment Dialog
const showEquipDialog = ref(false)
const equipLoading = ref(false)
const recommendedEquipments = ref<any[]>([])
const selectedEquipments = ref<Set<number>>(new Set())
const equipDates = ref<Record<number, any>>({})
const equipSlots = ref<Record<number, any[]>>({})
const equipSelectedSlots = ref<Record<number, string[]>>({})
const equipSlotsLoading = ref<Record<number, boolean>>({})
const aiReserving = ref(false)
// AI Review Dialog
const showReviewDialog = ref(false)
const reviewLoading = ref(false)
const reviewResult = ref<any>(null)
const reviewData = ref<any>(null)
// Publish Dialog AI config
const reviewThreshold = ref(70)
const showThresholdEdit = ref(false)
const editingTopic = ref<any>(null)
const editThresholdValue = ref(70)
// Import labApi
import { labApi } from '@/api'
import { ElMessageBox } from 'element-plus'
// ========== File Text Extraction Helpers ==========
async function extractFileText(file: File): Promise<string> {
  const name = file.name.toLowerCase()
  // PDF
  if (name.endsWith('.pdf')) {
    return extractPdfTextJs(file)
  }
  // Word .docx
  if (name.endsWith('.docx')) {
    return extractDocxText(file)
  }
  // Word .doc (old format)
  if (name.endsWith('.doc')) {
    return extractDocText(file)
  }
  // Images
  if (name.endsWith('.jpg') || name.endsWith('.jpeg') || name.endsWith('.png') ||
      name.endsWith('.gif') || name.endsWith('.bmp') || name.endsWith('.webp')) {
    return extractImageInfo(file)
  }
  // Excel .xlsx / .xls
  if (name.endsWith('.xlsx') || name.endsWith('.xls')) {
    return extractExcelText(file)
  }
  // For text-based files (.txt, .csv, etc.), use built-in text() method
  try {
    return await file.text()
  } catch {
    return '[' + file.name + ' - \u65e0\u6cd5\u89e3\u6790\u6587\u672c\u5185\u5bb9]'
  }
}
async function extractPdfTextJs(file: File): Promise<string> {
  const arrayBuffer = await file.arrayBuffer()
  const loadingTask = pdfjsLib.getDocument({ data: arrayBuffer })
  const pdf = await loadingTask.promise
  let fullText = ''
  for (let i = 1; i <= pdf.numPages; i++) {
    const page = await pdf.getPage(i)
    const textContent = await page.getTextContent()
    const pageText = textContent.items.map((item: any) => item.str).join(' ')
    fullText += pageText + '\n'
  }
  return fullText
}
async function extractDocxText(file: File): Promise<string> {
  try {
    const arrayBuffer = await file.arrayBuffer()
    const result = await mammoth.extractRawText({ arrayBuffer: arrayBuffer })
    const text = result.value || ''
    return text.length > 0 ? text : '[' + file.name + ' - \u63d0\u53d6\u6587\u672c\u4e3a\u7a7a]'
  } catch (e: any) {
    return '[' + file.name + ' - \u89e3\u6790docx\u5931\u8d25: ' + (e.message || '\u672a\u77e5\u9519\u8bef') + ']'
  }
}
async function extractDocText(file: File): Promise<string> {
  // Try mammoth first (some .doc files are actually docx-compatible)
  try {
    const arrayBuffer = await file.arrayBuffer()
    const result = await mammoth.extractRawText({ arrayBuffer: arrayBuffer })
    const text = result.value || ''
    if (text.trim().length > 0) {
      return text
    }
  } catch {}
  // Fallback: upload to backend for server-side extraction (Apache POI)
  try {
    const fd = new FormData()
    fd.append('file', file)
    const res = await post('/ai/agent/extract-text', fd, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 30000
    })
    if (res?.data && typeof res.data === 'string' && res.data.length > 10) {
      return res.data
    }
  } catch (e) {
    console.warn('Server-side extraction failed:', e)
  }
  return '[' + file.name + ' - \u65e7\u7248Word\u6587\u6863\uff0c\u65e0\u6cd5\u63d0\u53d6\u6587\u672c\u5185\u5bb9]'
}
async function extractImageInfo(file: File): Promise<string> {
  return new Promise((resolve) => {
    const img = new Image()
    const url = URL.createObjectURL(file)
    img.onload = () => {
      URL.revokeObjectURL(url)
      const sizeStr = formatBytes(file.size)
      resolve('[\u56fe\u7247\u6587\u4ef6: ' + file.name + '] \u7c7b\u578b: ' + (file.type || 'image') + ', \u5c3a\u5bf8: ' + img.width + 'x' + img.height + ', \u5927\u5c0f: ' + sizeStr)
    }
    img.onerror = () => {
      URL.revokeObjectURL(url)
      resolve('[\u56fe\u7247\u6587\u4ef6: ' + file.name + ' - \u65e0\u6cd5\u52a0\u8f7d]')
    }
    img.src = url
  })
}
async function extractExcelText(file: File): Promise<string> {
  try {
    const arrayBuffer = await file.arrayBuffer()
    const workbook = XLSX.read(arrayBuffer, { type: 'array' })
    let allText = ''
    for (const sheetName of workbook.SheetNames) {
      const sheet = workbook.Sheets[sheetName]
      const jsonData = XLSX.utils.sheet_to_json(sheet, { header: 1 }) as any[][]
      if (jsonData.length > 0) {
        allText += '=== ' + sheetName + ' ===\n'
        for (const row of jsonData) {
          const cells = row.filter((c: any) => c !== undefined && c !== null).map(String)
          if (cells.length > 0) {
            allText += cells.join(' | ') + '\n'
          }
        }
        allText += '\n'
      }
    }
    return allText.length > 0 ? allText : '[' + file.name + ' - \u8868\u683c\u5185\u5bb9\u4e3a\u7a7a]'
  } catch (e: any) {
    return '[' + file.name + ' - \u89e3\u6790xlsx\u5931\u8d25: ' + (e.message || '\u672a\u77e5\u9519\u8bef') + ']'
  }
}
const uploadRef = ref()
// ========== Data Fetching ==========
async function fetchAvailableTopics() {
  loading.value = true
  try { const res: any = await submissionApi.getAvailableTopics?.() || await get('/user/submission/topic/available'); availableTopics.value = res?.data || [] } catch { availableTopics.value = [] } finally { loading.value = false }
}
async function fetchConfirmedTopics() {
  loading2.value = true
  try {
    const res: any = await submissionApi.getConfirmedTopics?.() || await get('/user/submission/topic/confirmed')
    confirmedTopics.value = res?.data || []
  } catch {
    confirmedTopics.value = []
  } finally {
    loading2.value = false
  }
}
async function fetchCompletedTopics() {
  try {
    const res: any = await submissionApi.getCompletedTopics?.() || await get('/user/submission/topic/completed')
    completedTopics.value = res?.data || []
  } catch {
    completedTopics.value = []
  }
}
async function fetchMyPublishedTopics() {
  loading.value = true
  try { const res: any = await submissionApi.getMyTopics(); myPublishedTopics.value = res?.data || [] } catch { myPublishedTopics.value = [] } finally { loading.value = false }
}
async function fetchTeacherSubmissions() {
  loading4.value = true
  try { const res: any = await submissionApi.getTeacherSubmissions?.() || await get('/user/submission/teacher/submissions'); teacherSubmissions.value = res?.data || [] } catch { teacherSubmissions.value = [] } finally { loading4.value = false }
}
function getConfirmedCount(topicId: number) {
  return teacherSubmissions.value.filter((s: any) => s.topicId === topicId).length
}
// ========== Student Actions ==========
async function viewTopic(topic: any) {
  viewingTopic.value = topic
  topicExperiments.value = []
  topicDetailLoading.value = true
  showViewTopic.value = true
  try {
    const res = await submissionApi.getTopicDetail(topic.id)
    const data = res?.data || {}
    topicExperiments.value = data.experiments || []
  } catch (e: any) {
    console.error('viewTopic error:', e)
    ElMessage.error('加载详情失败: ' + (e.message || '未知错误'))
    topicExperiments.value = []
  } finally {
    topicDetailLoading.value = false
  }
}
async function confirmAvailableTopic(topic: any) {
  await confirmWithExperiments(topic)
}
function openSubmitDialog(topic: any) {
  currentSubmitTopic.value = topic
  submitForm.description = ''
  uploadFileList.value = []
  showSubmitDialog.value = true
}
function handleFileChange(file: any) { uploadFileList.value = [...uploadFileList.value, file] }
async function handleSubmitFiles() {
  if (!currentSubmitTopic.value?.id) return
  submitting.value = true
  try {
    // Read file contents and include in description
    let fileContentText = ''
    for (const f of uploadFileList.value) {
      const fileName = f.name || f.raw?.name || ''
      if (f.raw) {
        try {
          const text = await extractFileText(f.raw)
          const snippet = text.substring(0, 2000)
          fileContentText += '\n--- ' + fileName + ' ---\n' + snippet + '\n'
        } catch {
          fileContentText += '\n--- ' + fileName + ' ---\n[无法提取文本内容]\n'
        }
      } else {
        fileContentText += '\n--- ' + fileName + ' ---\n'
      }
    }
    const fullDesc = submitForm.description + (fileContentText ? '\n\n=== 提交文件内容 ===' + fileContentText : '')
    const submitRes = await submissionApi.submitFiles(currentSubmitTopic.value.id, { description: fullDesc, content: fullDesc })
    const recordId = submitRes?.data?.id || submitRes?.data
    // Upload actual files to the submission record
    if (recordId) {
      for (const f of uploadFileList.value) {
        if (f.raw) {
          try {
            const fd = new FormData()
            fd.append('file', f.raw)
            await submissionApi.uploadSubmissionFile(recordId, fd)
          } catch (e) {
            console.warn('Failed to upload file:', f.name, e)
          }
        }
      }
    }
    ElMessage.success('提交成功')
    showSubmitDialog.value = false
    submitForm.description = ''
    uploadFileList.value = []
    await fetchConfirmedTopics()
      await fetchCompletedTopics()
    await fetchCompletedTopics()
  } catch (e: any) { ElMessage.error('操作失败: ' + (e.message || '')) } finally { submitting.value = false }
}
async function viewSubmissionDetail(record: any) {
  detailData.value = record
  detailFiles.value = []
  showDetailDialog.value = true
  try {
    const subRes = await submissionApi.getMySubmission(record.id)
    const subRecord = subRes?.data
    if (subRecord && subRecord.id) {
      detailData.value = { ...record, ...subRecord }
      const fileRes = await submissionApi.getFiles(subRecord.id)
      detailFiles.value = fileRes?.data || []
    }
  } catch (e: any) {
    console.error('viewSubmissionDetail error:', e)
  }
}
function resubmitSubmission(topic: any) {
  if (topic) openSubmitDialog(topic)
  else ElMessage.warning('未找到对应课题')
}
// ========== Teacher Actions ==========
function showPassDialog(record: any) {
  currentReviewRecord.value = record
  reviewForm.score = 80
  reviewForm.comment = ''
  showPassDialogFlag.value = true
}
function showRejectDialog(record: any) {
  currentReviewRecord.value = record
  rejectForm.reason = ''
  showRejectDialogFlag.value = true
}
async function handlePass() {
  if (!currentReviewRecord.value) return
  submitting.value = true
  try {
    const recordId = currentReviewRecord.value.recordId
    if (!recordId) { ElMessage.error('未找到提交记录'); return }
    await submissionApi.passSubmission?.(recordId, reviewForm.score, reviewForm.comment) ||
      await (await get('/user/submission/record/' + recordId + '/pass?score=' + reviewForm.score + '&comment=' + encodeURIComponent(reviewForm.comment), {}, { method: 'POST' }))
    ElMessage.success('已通过')
    showPassDialogFlag.value = false
    fetchTeacherSubmissions()
    fetchMyPublishedTopics()
  } catch (e: any) { ElMessage.error('操作失败') } finally { submitting.value = false }
}
async function handleReject() {
  if (!currentReviewRecord.value) return
  if (!rejectForm.reason) { ElMessage.warning('请填写打回原因'); return }
  submitting.value = true
  try {
    const recordId = currentReviewRecord.value.recordId
    if (!recordId) { ElMessage.error('未找到提交记录'); return }
    await submissionApi.rejectSubmission?.(recordId, rejectForm.reason) ||
      await (await get('/user/submission/record/' + recordId + '/reject', { reason: rejectForm.reason }, { method: 'POST' }))
    ElMessage.success('已打回')
    showRejectDialogFlag.value = false
    fetchTeacherSubmissions()
    fetchMyPublishedTopics()
  } catch (e: any) { ElMessage.error('操作失败') } finally { submitting.value = false }
}
async function viewStudentSubmission(record: any) {
  detailData.value = record
  const fileRecordId = record.recordId || record.id
  try { const res: any = await submissionApi.getFiles(fileRecordId); detailFiles.value = res?.data || [] } catch { detailFiles.value = [] }
  // Fetch full submission record to get complete description
  try {
    const fullRes: any = await submissionApi.getSubmission(record.recordId || record.id)
    if (fullRes?.data) {
      detailData.value = { ...record, ...fullRes.data }
    }
  } catch {}
  showDetailDialog.value = true
}
async function openThresholdEdit(topic: any) {
  editingTopic.value = topic
  editThresholdValue.value = topic.reviewThreshold ?? 70
  showThresholdEdit.value = true
}
async function handleSaveThreshold() {
  const topic = editingTopic.value
  if (!topic) return
  submitting.value = true
  try {
    await submissionApi.updateAiConfig(topic.id, { reviewThreshold: editThresholdValue.value })
    // Update local state
    topic.reviewThreshold = editThresholdValue.value
    ElMessage.success('阈值已更新')
    showThresholdEdit.value = false
  } catch (e: any) {
    ElMessage.error('保存失败: ' + (e.message || ''))
  } finally {
    submitting.value = false
  }
}
async function handleCreateTopic() {
  if (!createForm.title) { ElMessage.warning('请输入课题名称'); return }
  submitting.value = true
  try {
    const res = await submissionApi.createTopic({ title: createForm.title, description: createForm.description, source: 'teacher', reviewThreshold: reviewThreshold.value })
    const newTopicId = res?.data?.id || res?.data?.topicId
    ElMessage.success('课题创建成功')
    showCreateDialog.value = false
    createForm.title = ''
    createForm.description = ''
    fetchMyPublishedTopics()
  } catch (e: any) { ElMessage.error('创建失败') } finally { submitting.value = false }
}
// ========== AI Experiment Recommendation ==========
async function fetchAiSuggestions() {
  if (!aiInput.value) { ElMessage.warning('请输入关键词'); return }
  aiLoading.value = true
  try {
    const res = await analysisApi.agentAnalysisRecommend({ message: aiInput.value })
    const chatVO = res?.data
    const content = chatVO?.content || (typeof chatVO === 'string' ? chatVO : '')
    aiSuggestions.value = content.split('\n').map((s: string) => s.trim().replace(/^\d+\.\s*/, '')).filter((s: string) => s)
  } catch {
    ElMessage.error('提示失败')
  } finally {
    aiLoading.value = false
  }
}
async function fetchTopicRecommendations() {
  topicLoading.value = true
  try {
    const major = userStore.userInfo?.majorName || userStore.userInfo?.major || ''
    const topicNames = availableTopics.value.map((t: any) => t.title).join('、')
    if (!topicNames) {
      topicRecommendations.value = '暂无可推荐的课题'
      return
    }
    const message = '我是' + (major || '动物医学') + '专业的学生，请从以下课题中推荐适合我的课题，并说明推荐理由：\n' + topicNames
    const res = await analysisApi.agentAnalysisRecommend({ message })
    topicRecommendations.value = res?.data?.content || '暂无推荐'
  } catch {
    topicRecommendations.value = '推荐服务暂时不可用'
  } finally {
    topicLoading.value = false
  }
}
async function confirmWithExperiments(topic: any) {
  currentTopic.value = topic
  selectedExperiments.value = new Set()
  customExperiments.value = []
  customExperimentInput.value = ''
  showExperimentDialog.value = true
  experimentLoading.value = true
  try {
    const msg = topic.title + '|' + (topic.description || '')
    const res = await analysisApi.recommendByTopic({ message: msg })
    recommendedExperiments.value = res?.data || []
    if (recommendedExperiments.value.length === 0) {
      ElMessage.warning('AI 未找到相关实验推荐，你可以手动输入实验名称')
    }
  } catch {
    recommendedExperiments.value = []
  } finally {
    experimentLoading.value = false
  }
}
function toggleExperiment(name: string) {
  const s = new Set(selectedExperiments.value)
  if (s.has(name)) s.delete(name)
  else s.add(name)
  selectedExperiments.value = s
}
function addCustomExperiment() {
  const name = customExperimentInput.value.trim()
  if (!name) { ElMessage.warning('请输入实验名称'); return }
  if (selectedExperiments.value.has(name) || customExperiments.value.includes(name)) {
    ElMessage.warning('该实验已存在'); return
  }
  customExperiments.value = [...customExperiments.value, name]
  customExperimentInput.value = ''
}
function removeCustomExperiment(idx: number) {
  customExperiments.value = customExperiments.value.filter((_: any, i: number) => i !== idx)
}
async function confirmExperimentSelection() {
  confirming.value = true
  try {
    const topic = currentTopic.value
    if (!topic) return
    const allExperiments = [...Array.from(selectedExperiments.value), ...customExperiments.value]
    // Save experiments
    await analysisApi.saveExperiments(topic.id, {
      experiments: Array.from(selectedExperiments.value),
      customExperiments: customExperiments.value
    })
    // Confirm topic
    await submissionApi.confirmTopic(topic.id)
    showExperimentDialog.value = false
    ElMessage.success('已确认选择课题，共选择 ' + allExperiments.length + ' 个实验')
    await fetchAvailableTopics()
    await fetchConfirmedTopics()
    if (allExperiments.length > 0) {
      await loadEquipRecommendations(allExperiments)
    }
  } catch (e: any) {
    ElMessage.error('确认失败: ' + (e.message || '未知错误'))
  } finally {
    confirming.value = false
  }
}
async function loadEquipRecommendations(experiments: string[]) {
  showEquipDialog.value = true
  equipLoading.value = true
  equipSelectedSlots.value = {}
  equipDates.value = {}
  try {
    const res = await analysisApi.recommendEquipmentByExperiments({ message: JSON.stringify(experiments) })
    const data = res?.data || []
    recommendedEquipments.value = Array.isArray(data) ? data : (data.recommendations || [])
    if (recommendedEquipments.value.length === 0) {
      ElMessage.warning('未找到相关仪器推荐')
    }
  } catch {
    recommendedEquipments.value = []
  } finally {
    equipLoading.value = false
  }
}
function getEquipName(eqId: number): string {
  const eq = recommendedEquipments.value.find((r: any) => r.equipmentId === eqId)
  return eq ? eq.name : ''
}
async function loadEquipSlots(eqId: number, date: any) {
  if (!date) {
    equipSlots.value = { ...equipSlots.value, [eqId]: [] }
    equipSelectedSlots.value = { ...equipSelectedSlots.value, [eqId]: [] }
    return
  }
  equipSlotsLoading.value = { ...equipSlotsLoading.value, [eqId]: true }
  try {
    const d = new Date(date).toISOString().split('T')[0]
    const r: any = await labApi.getTimeSlots(eqId, d)
    equipSlots.value = { ...equipSlots.value, [eqId]: r.data || [] }
    equipSelectedSlots.value = { ...equipSelectedSlots.value, [eqId]: [] }
  } catch {
    equipSlots.value = { ...equipSlots.value, [eqId]: [] }
  } finally {
    equipSlotsLoading.value = { ...equipSlotsLoading.value, [eqId]: false }
  }
}
function selectEquipSlot(eqId: number, s: any) {
  if (!s.available) return
  const current = equipSelectedSlots.value[eqId] || []
  const idx = current.indexOf(s.timeSlot)
  if (idx >= 0) {
    current.splice(idx, 1)
  } else {
    current.push(s.timeSlot)
  }
  equipSelectedSlots.value = { ...equipSelectedSlots.value, [eqId]: [...current] }
}
async function batchReserveAll() {
  const toReserve: { eqId: number; date: string; slots: string[]; name: string; labId: number }[] = []
  for (const eq of recommendedEquipments.value) {
    const eqId = eq.equipmentId
    const d = equipDates.value[eqId]
    const slots = equipSelectedSlots.value[eqId] || []
    if (d && slots.length > 0) {
      toReserve.push({
        eqId,
        date: new Date(d).toISOString().split('T')[0],
        slots,
        name: eq.name,
        labId: eq.labId || 0,
        topicId: currentTopic.value?.id || 0,
        purpose: (currentTopic.value?.title || "课题") + " - " + (eq.experimentName || "通用实验")
      })
    }
  }
  if (toReserve.length === 0) { ElMessage.warning('请先选择仪器和预约时间'); return }
  aiReserving.value = true
  try {
    const res = await analysisApi.batchSubmitReservations({ reservations: toReserve })
    ElMessage.success('预约提交成功，等待管理员审批')
    showEquipDialog.value = false
  } catch (e: any) {
    ElMessage.error('预约失败: ' + (e.message || '未知错误'))
  } finally {
    aiReserving.value = false
  }
}
// ========== AI Auto Review ==========
async function handleSubmitWithAIReview() {
  const topic = currentSubmitTopic.value
  if (!topic) return
  if (!submitForm.description && uploadFileList.value.length === 0) {
    ElMessage.warning('请填写描述或上传文件')
    return
  }
  submitting.value = true
  reviewLoading.value = true
  showReviewDialog.value = true
  reviewResult.value = null
  try {
    // Step 0: Read file contents from browser so AI can analyze them
    let fileContentText = ''
    for (const f of uploadFileList.value) {
      const fileName = f.name || f.raw?.name || ''
      if (f.raw) {
        try {
          const text = await extractFileText(f.raw)
          const snippet = text.substring(0, 3000)
          fileContentText += `\n--- File: ${fileName} ---\n${snippet}\n`
        } catch {
          fileContentText += `\n--- File: ${fileName} ---\n[binary file - content preview not available]\n`
        }
      }
    }
    // Append file contents to submission description so AI sees them
    const fullDescription = submitForm.description + fileContentText
    
    // Step 1: Fetch actual threshold from DB (via data service)
    let actualThreshold = topic.reviewThreshold ?? 70
    try {
      const configRes = await submissionApi.getAiConfig(topic.id)
      if (configRes?.data?.reviewThreshold !== undefined && configRes?.data?.reviewThreshold !== null) {
        actualThreshold = Number(configRes.data.reviewThreshold)
      }
    } catch (e) { /* use default */ }
    
    // Step 2: AI Review with actual file content included
    const res = await analysisApi.autoReviewSubmission({
      message: JSON.stringify({
        topicTitle: topic.title,
        topicDescription: topic.description || '',
        submissionDescription: fullDescription || '',
        fileNames: uploadFileList.value.map((f) => f.name || f.raw?.name || ''),
        threshold: actualThreshold
      })
    })
    reviewResult.value = res?.data || { score: 0, passed: false, reason: '审阅服务异常' }
    // Step 3: Only submit to backend if AI review passes
    if (reviewResult.value && reviewResult.value.passed) {
      // Build description with file content included
      let fullSubmitDesc = submitForm.description || ''
      if (fileContentText) {
        fullSubmitDesc += '\n\n=== 提交文件内容 ===\n' + fileContentText
      }
      const submitRes = await submissionApi.submitFiles(topic.id, {
        title: topic.title,
        content: fullSubmitDesc,
        description: fullSubmitDesc
      })
      const recordId = submitRes?.data?.id || submitRes?.data
      // Upload actual files to the submission record
      if (recordId) {
        for (const f of uploadFileList.value) {
          if (f.raw) {
            try {
              const fd = new FormData()
              fd.append('file', f.raw)
              await submissionApi.uploadSubmissionFile(recordId, fd)
            } catch (e) {
              console.warn('Failed to upload file:', f.name, e)
            }
          }
        }
      }
      ElMessage.success('AI 审阅通过，已提交给教师审批')
      showSubmitDialog.value = false
      showReviewDialog.value = false
      submitForm.description = ''
      uploadFileList.value = []
      await fetchConfirmedTopics()
      await fetchCompletedTopics()
    }
  } catch (e: any) {
    console.error('AI Review Error:', e?.response?.config?.url, e?.response?.status, e?.response?.data)
    reviewResult.value = { score: 0, passed: false, reason: e?.response?.data?.msg || e?.response?.data?.message || e.message || '审阅服务异常' }
  } finally {
    submitting.value = false
    reviewLoading.value = false
  }
}
function formatSize(bytes: number) {
  if (!bytes) return '0B'
  const units = ['B', 'KB', 'MB', 'GB']
  let i = 0; let size = bytes
  while (size >= 1024 && i < units.length - 1) { size /= 1024; i++ }
  return size.toFixed(1) + units[i]
}
async function downloadFile(file: any) {
  try {
    const res = await fetch('/api/user/submission/file/' + file.id + '/download', {
      headers: { 'Authorization': localStorage.getItem('token') || '' }
    })
    if (!res.ok) { ElMessage.error('下载失败'); return }
    const blob = await res.blob()
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url; a.download = file.fileName || '文件'
    document.body.appendChild(a); a.click()
    document.body.removeChild(a); URL.revokeObjectURL(url)
  } catch { ElMessage.error('下载失败') }
}
// ========== Init ==========
onMounted(() => {
  if (isTeacher.value) {
    fetchMyPublishedTopics()
    fetchTeacherSubmissions()
  } else {
    fetchAvailableTopics()
    fetchConfirmedTopics()
    fetchCompletedTopics()
  }
})
</script>
<style scoped>
.page-container { padding: 24px; }
</style>
<style>
/* Fix date picker text color in dark dialogs */
.el-picker__popper,
.el-picker-panel {
  background: #fff !important;
  border: 1px solid #e4e7ed !important;
  box-shadow: 0 2px 12px rgba(0,0,0,0.12) !important;
}
.el-picker-panel,
.el-date-picker .el-picker-panel,
.el-date-table td .el-date-table-cell .el-date-table-cell__text {
  color: #303133 !important;
}
.el-date-picker__header-label,
.el-date-picker__header .el-date-picker__header-label,
.el-date-table th,
.el-year-table td .el-year-table-cell__text,
.el-month-table td .el-month-table-cell__text {
  color: #303133 !important;
}
.el-date-table td .el-date-table-cell:hover .el-date-table-cell__text {
  color: #409eff !important;
}
.el-date-table td.today .el-date-table-cell {
  color: #409eff;
}
.el-date-table td.today .el-date-table-cell__text {
  color: #409eff !important;
  font-weight: 700;
}
.el-date-table td.next-month .el-date-table-cell__text,
.el-date-table td.prev-month .el-date-table-cell__text {
  color: #c0c4cc !important;
}
.el-date-table td.disabled .el-date-table-cell__text {
  color: #c0c4cc !important;
}
</style>
