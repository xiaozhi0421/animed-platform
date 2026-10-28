<template>
  <div class="class-detail-page">
    <el-page-header @back="$router.push('/campus/my-class')" :content="classInfo.className || '班级详情'" />

    <div class="class-hero">
      <div class="hero-left">
        <div class="hero-icon">{{ classInfo.className?.charAt(0) || 'B' }}</div>
        <div class="hero-info">
          <h2>{{ classInfo.className }}</h2>
          <p class="hero-meta">{{ classInfo.teacherName }} | {{ classInfo.academicYear }} {{ classInfo.semester }}</p>
          <div class="hero-code">
            班级码<el-tag class="code-val">{{ classInfo.classCode }}</el-tag>
            <el-button text size="small" @click="copyCode(classInfo.classCode)"><el-icon><CopyDocument /></el-icon></el-button>
          </div>
        </div>
      </div>
      <div class="hero-right">
        <div class="stat-item"><span class="stat-num">{{ members.length }}</span><span class="stat-label">成员</span></div>
        <div class="stat-item"><span class="stat-num">{{ homeworkList.length }}</span><span class="stat-label">作业</span></div>
        <div class="stat-item"><span class="stat-num">{{ signInList.length }}</span><span class="stat-label">签到</span></div>
      </div>
    </div>

    <el-tabs v-model="activeTab" class="main-tabs">
      <!-- ===== 签到 ===== -->
      <el-tab-pane label="签到" name="signin">
        <div class="tab-toolbar">
          <span class="tab-title">签到列表</span>
          <el-button v-if="isTeacher" type="primary" size="small" @click="showSignInDialog = true">
            <el-icon><Plus /></el-icon>发起签到
          </el-button>
        </div>
        <el-table :data="signInList" stripe class="data-table">
          <el-table-column prop="title" label="签到标题" min-width="140" />
          <el-table-column prop="signType" label="类型" width="100">
            <template #default="{ row }">
              <el-tag :type="row.signType === '普通签到' ? 'default' : row.signType === '手势签到' ? 'warning' : row.signType === '密码签到' ? 'primary' : 'success'" size="small">{{ row.signType }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="发起时间" width="160">
            <template #default="{ row }">{{ row.createTime ? row.createTime.replace('T', ' ').substring(0,16) : '' }}</template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="80">
            <template #default="{ row }">
              <el-tag :type="row.status === '进行中' ? 'success' : 'info'" size="small">{{ row.status }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="200" fixed="right">
            <template #default="{ row }">
              <el-button v-if="!isTeacher && row.status === '进行中'" size="small" type="primary" @click="openSignInDialog(row)">签到</el-button>
              <el-button v-if="isTeacher && row.status === '进行中'" size="small" type="danger" @click="handleEndSignIn(row.id)">结束</el-button>
              <el-button size="small" @click="viewSignInRecords(row.id, classId.value)">记录</el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-empty v-if="!signInList.length" description="暂无签到活动" />
      </el-tab-pane>

      <!-- ===== 作业 ===== -->
      <el-tab-pane label="作业" name="homework">
        <div class="tab-toolbar">
          <span class="tab-title">作业列表</span>
          <el-button v-if="isTeacher" type="primary" size="small" @click="showHomeworkDialog = true">
            <el-icon><Plus /></el-icon>布置作业
          </el-button>
        </div>
        <el-table :data="homeworkList" stripe class="data-table">
          <el-table-column prop="title" label="作业标题" min-width="160" />
          <el-table-column prop="deadline" label="截止时间" width="160">
            <template #default="{ row }">{{ row.deadline ? row.deadline.replace('T', ' ').substring(0,16) : '暂无截止' }}</template>
          </el-table-column>
          <el-table-column label="状态" width="90">
            <template #default="{ row }">
              <el-tag :type="row.status === '进行中' ? 'success' : 'info'" size="small">{{ row.status || '进行中' }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="160" fixed="right">
            <template #default="{ row }">
              <el-button v-if="!isTeacher" size="small" type="primary" @click="openSubmitDialog(row)">提交作业</el-button>
              <el-button v-if="isTeacher" size="small" @click="viewSubmissions(row.id)">查看提交</el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-empty v-if="!homeworkList.length" description="暂无作业" />
      </el-tab-pane>

      <!-- ===== 成员 ===== -->
      <el-tab-pane label="成员" name="members">
        <div class="tab-toolbar">
          <span class="tab-title">班级成员</span>
          <span class="member-count">共 {{ members.length }} 人</span>
        </div>
        <div class="member-grid">
          <div v-for="m in members" :key="m.id" class="member-item">
            <el-avatar :size="40" style="background: #409eff;">{{ m.userName?.charAt(0) }}</el-avatar>
            <div class="member-info">
              <span class="member-name">{{ m.userName }}</span>
              <span style="font-size:12px;color:#999;">{{ m.role }} | {{ m.studentNo || '' }}</span>
            </div>
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- ===== 发起签到对话框 ===== -->
    <el-dialog v-model="showSignInDialog" title="发起签到" width="500px">
      <el-form ref="signInFormRef" :model="signInForm" :rules="signInRules" label-width="100px">
        <el-form-item label="签到标题" prop="title">
          <el-input v-model="signInForm.title" placeholder="请输入签到标题" />
        </el-form-item>
        <el-form-item label="签到方式" prop="signType">
          <el-select v-model="signInForm.signType" style="width:100%">
            <el-option label="普通签到" value="普通签到" />
            <el-option label="手势签到" value="手势签到" />
            <el-option label="密码签到" value="密码签到" />
            <el-option label="位置签到" value="位置签到" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="signInForm.signType === '手势签到'" label="手势图案">
          <el-input v-model="signInForm.gesturePattern" placeholder="请输入手势密码" />
        </el-form-item>
        <el-form-item v-if="signInForm.signType === '密码签到'" label="签到密码">
          <el-input v-model="signInForm.signPassword" placeholder="请输入签到密码" />
        </el-form-item>
        <el-form-item v-if="signInForm.signType === '位置签到'" label="签到位置">
          <el-input v-model="signInForm.locationDesc" placeholder="请输入签到地点名称" />
        </el-form-item>
        <el-form-item label="持续时长">
          <el-input-number v-model="signInForm.duration" :min="1" :max="60" /> 分钟
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showSignInDialog = false">取消</el-button>
        <el-button type="primary" :loading="signInLoading" @click="handleCreateSignIn">发起</el-button>
      </template>
    </el-dialog>

    <!-- ===== 学生签到对话框 ===== -->
        <!-- ===== 学生签到对话框（增强版） ===== -->
    <el-dialog v-model="showDoSignInDialog" title="学生签到" width="440px">
      <div class="do-signin-center">
        <div style="font-size:18px;font-weight:600;text-align:center;">{{ currentSignIn?.title }}</div>
        <div style="color:#999;margin-bottom:12px;text-align:center;">{{ currentSignIn?.signType }}</div>

        <!-- 普通签到 -->
        <template v-if="currentSignIn?.signType === '普通签到'">
          <el-icon class="signin-icon" :size="48"><Finished /></el-icon>
          <div style="margin:12px 0;">
            <el-button type="primary" size="large" :loading="doSignInLoading" @click="handleDoSignIn" style="width:200px;">
              一键签到
            </el-button>
          </div>
        </template>

        <!-- 手势签到 -->
        <template v-if="currentSignIn?.signType === '手势签到'">
          <div class="gesture-container">
            <div class="gesture-grid" ref="gestureGridRef">
              <div v-for="i in 9" :key="i" class="gesture-dot"
                :class="{ active: gesturePath.includes(i) }"
                @pointerdown.prevent="gestureStart(i)"
                @pointerenter="gestureMove(i)"
                @pointerup="gestureEnd()">
                <div class="dot-inner"></div>
              </div>
            </div>
            <svg class="gesture-lines-svg" width="240" height="240" style="position:absolute;top:0;left:0;pointer-events:none;">
              <line v-for="(ln, idx) in gestureLines" :key="idx" :x1="ln.x1" :y1="ln.y1" :x2="ln.x2" :y2="ln.y2" stroke="#409eff" stroke-width="4" stroke-linecap="round" />
            </svg>
          </div>
          <div style="font-size:12px;color:#999;margin-top:4px;">请画出与老师设置相同的图案</div>
          <div v-if="gesturePath.length" style="font-size:12px;color:#409eff;margin-top:4px;">
            已连接 {{ gesturePath.length }} 个点
            <el-button text size="small" @click="clearGesture">重置</el-button>
          </div>
          <div style="margin-top:12px;">
            <el-button type="primary" size="large" :loading="doSignInLoading" @click="handleDoSignIn" style="width:200px;" :disabled="!gesturePath.length">
              确认签到
            </el-button>
          </div>
        </template>

        <!-- 密码签到 -->
        <template v-if="currentSignIn?.signType === '密码签到'">
          <el-icon class="signin-icon" :size="48"><Lock /></el-icon>
          <div style="margin:12px 0;">
            <el-input v-model="signInPassword" type="password" placeholder="请输入签到密码" size="large" style="width:220px;" show-password @keyup.enter="handleDoSignIn" />
          </div>
          <div>
            <el-button type="primary" size="large" :loading="doSignInLoading" @click="handleDoSignIn" style="width:200px;" :disabled="!signInPassword">
              确认签到
            </el-button>
          </div>
        </template>

        <!-- 位置签到 -->
        <template v-if="currentSignIn?.signType === '位置签到'">
          <el-icon class="signin-icon" :size="48" :style="{color: locationLoaded ? '#67c23a' : '#999'}"><LocationFilled /></el-icon>
          <div style="margin:12px 0;text-align:center;">
            <div v-if="!locationLoaded">
              <el-button type="primary" :loading="loadingLocation" @click="getLocation">获取当前位置</el-button>
            </div>
            <div v-else>
              <div style="color:#67c23a;margin-bottom:8px;"><el-icon :size="16"><SuccessFilled /></el-icon> 已获取位置</div>
              <div style="font-size:12px;color:#999;margin-bottom:8px;">经度: {{ locationData.lng?.toFixed(4) }}, 纬度: {{ locationData.lat?.toFixed(4) }}</div>
              <el-button type="primary" size="large" :loading="doSignInLoading" @click="handleDoSignIn" style="width:200px;">确认签到</el-button>
            </div>
          </div>
        </template>
      </div>
      <template #footer>
        <el-button @click="showDoSignInDialog = false">取消</el-button>
      </template>
    </el-dialog>

    <!-- ===== 签到记录对话框 ===== -->
        <!-- ===== 签到记录/状态对话框 ===== -->
    <el-dialog v-model="showSignInRecordsDialog" :title="isTeacher ? '签到状态' : '签到记录'" width="720px">
      <template v-if="isTeacher">
        <el-alert :title="'已签到: ' + signInStatus.filter(s=>s.status==='已签到').length + ' / 未签到: ' + signInStatus.filter(s=>s.status==='未签到').length + ' / 失败: ' + signInStatus.filter(s=>s.status==='失败').length" type="info" :closable="false" style="margin-bottom:12px;" />
        <el-table :data="signInStatus" stripe>
          <el-table-column prop="studentNo" label="学号" width="120" />
          <el-table-column prop="studentName" label="姓名" width="100" />
          <el-table-column prop="status" label="状态" width="80">
            <template #default="{ row }"><el-tag :type="row.status==='已签到'?'success':row.status==='失败'?'danger':'info'" size="small">{{ row.status }}</el-tag></template>
          </el-table-column>
          <el-table-column label="签到时间" width="160">
            <template #default="{ row }">{{ row.signTime || '-' }}</template>
          </el-table-column>
          <el-table-column prop="failReason" label="备注" min-width="120">
            <template #default="{ row }">{{ row.failReason || '-' }}</template>
          </el-table-column>
          <el-table-column label="操作" width="100" fixed="right">
            <template #default="{ row }">
              <el-button v-if="row.status==='未签到' && currentSignInStatus?.status==='进行中'" size="small" type="warning" @click="handleProxySignIn(row.studentId)" :loading="proxyLoadingId===row.studentId">代签到</el-button>
            </template>
          </el-table-column>
        </el-table>
      </template>
      <template v-else>
        <el-table :data="signInRecords" stripe>
          <el-table-column prop="studentName" label="姓名" width="120" />
          <el-table-column label="签到时间" width="160"><template #default="{ row }">{{ row.signTime?.replace('T',' ').substring(0,19) }}</template></el-table-column>
          <el-table-column prop="result" label="结果" width="80"><template #default="{ row }"><el-tag :type="row.result==='成功'?'success':'danger'" size="small">{{ row.result }}</el-tag></template></el-table-column>
          <el-table-column prop="failReason" label="失败原因" />
        </el-table>
      </template>
      <template #footer>
        <el-button @click="showSignInRecordsDialog = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- ===== 布置作业对话框 ===== -->
    <el-dialog v-model="showHomeworkDialog" title="布置作业" width="500px">
      <el-form ref="hwFormRef" :model="hwForm" :rules="hwRules" label-width="90px">
        <el-form-item label="作业标题" prop="title">
          <el-input v-model="hwForm.title" placeholder="请输入作业标题" />
        </el-form-item>
        <el-form-item label="截止时间" prop="deadline">
          <el-date-picker v-model="hwForm.deadline" type="datetime" placeholder="选择截止时间" style="width:100%" value-format="YYYY-MM-DDTHH:mm:ss" />
        </el-form-item>
        <el-form-item label="作业说明">
          <el-input v-model="hwForm.description" type="textarea" :rows="4" placeholder="请输入作业说明" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showHomeworkDialog = false">取消</el-button>
        <el-button type="primary" :loading="hwLoading" @click="handleCreateHomework">发布</el-button>
      </template>
    </el-dialog>

    <!-- ===== 提交作业对话框 ===== -->
    <el-dialog v-model="showSubmitDialog" title="提交作业" width="500px">
      <el-input v-model="submitContent" type="textarea" :rows="6" placeholder="请输入作业内容" />
      <template #footer>
        <el-button @click="showSubmitDialog = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmitHomework">提交</el-button>
      </template>
    </el-dialog>

    <!-- ===== 查看提交对话框 ===== -->
    <el-dialog v-model="showSubmissionsDialog" title="学生提交" width="700px">
      <el-table :data="submissions" stripe>
        <el-table-column prop="studentName" label="学生" width="120" />
        <el-table-column prop="content" label="提交内容" min-width="200" />
        <el-table-column prop="submitTime" label="提交时间" width="160">
          <template #default="{ row }">{{ row.submitTime?.replace('T',' ').substring(0,16) }}</template>
        </el-table-column>
        <el-table-column prop="score" label="成绩" width="80">
          <template #default="{ row }">{{ row.score ?? '-' }}</template>
        </el-table-column>
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button v-if="isTeacher && row.score == null" size="small" @click="openGradeDialog(row)">评分</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>

    <!-- ===== 评分对话框 ===== -->
