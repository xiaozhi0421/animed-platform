import { get, post, put, del } from '@/utils/request'

export const authApi = {
  login: (data: { account: string; password: string; system: string }) => post('/auth/login', data),
  studentRegister: (data: any) => post('/auth/campus/register/student', data),
  teacherRegister: (data: any) => post('/auth/campus/register/teacher', data),
  sendSmsCode: (data: { phone: string }) => post('/auth/sms/send', data),
  getBindStatus: () => get('/auth/bind/status'),
  bindAccount: (data: any) => post('/auth/bind', data),
}

export const userApi = {
  getUserInfo: () => get('/user/info'),
  updateProfile: (data: any, role?: string) => {
    if (role === 'campus_student') return put('/user/campus/student/profile', data)
    if (role === 'campus_teacher') return put('/user/campus/teacher/profile', data)
    return put('/user/profile', data)
  },
  updatePassword: (data: any) => put('/user/password', data)
}

export const dataApi = {
  getDatasets: (params: any) => get('/data/dataset/list', params),
  getDataset: (id: number) => get(`/data/dataset/${id}`),
  getDataRows: (id: number, pageNum: number, pageSize: number) => get('/data/rows/' + id + '?pageNum=' + pageNum + '&pageSize=' + pageSize),
  uploadDataset: (data: any) => post('/data/dataset/upload', data),
  deleteDataset: (id: number) => del(`/data/dataset/${id}`),
  collectDataset: (id: number) => post(`/data/dataset/${id}/collect`),
  uncollectDataset: (id: number) => del(`/data/dataset/${id}/collect`),
  getCleanTasks: (params: any) => get('/data/clean/task/list', params),
  createCleanTask: (data: any) => post('/data/clean/task', data),
  startCleanTask: (id: number) => post(`/data/clean/task/${id}/start`),
  deleteCleanTask: (id: number) => del(`/data/clean/task/${id}`),
  getCleanPreview: (id: number) => get(`/data/clean/task/${id}/preview`),
  confirmCleanTask: (id: number) => post(`/data/clean/task/${id}/confirm`),
  discardCleanTask: (id: number) => post(`/data/clean/task/${id}/discard`),
  describeDataSet: (id: number) => get(`/data/analysis/describe/${id}`),
  distributionAnalysis: (id: number, column: string, bins?: number) => get(`/data/analysis/distribution/${id}`, { column, bins }),
  visualizationAggregate: (params: any) => post('/data/visualization/aggregate', params),

  correlationAnalysis: (id: number) => get(`/data/analysis/correlation/${id}`)
}

export const analysisApi = {
  chat: (data: { message: string; sessionId?: string; type?: string }) => post('/ai/chat', data),
  chatStream: (data: { message: string; sessionId?: string; type?: string }) => post('/ai/chat/stream', data),
  getConversations: () => get('/ai/conversations'),
  getMessages: (id: number) => get('/ai/conversations/' + id + '/messages'),
  deleteConversation: (id: number) => del('/ai/conversations/' + id),
  updateConversationTitle: (id: number, title: string) => put('/ai/conversations/' + id + '/title', { title }),
  diagnosis: (data: any) => post('/ai/diagnosis', data),
  getHealthReport: (data: any) => post('/ai/health-report', data),
  knowledgeUpload: (data: any) => post('/ai/knowledge/upload', data),
  knowledgePreview: (formData: FormData) => post('/ai/knowledge/preview', formData, { timeout: 60000 }),
  knowledgeConfirm: (data: any) => post('/ai/knowledge/confirm', data),
  knowledgeUpdateDoc: (id: number, data: any) => put(`/ai/knowledge/document/${id}`, data),
  knowledgeSearch: (data: { query?: string; title?: string; author?: string; category?: string; topK?: number }) => post('/ai/knowledge/search', data),
  getKnowledgeDoc: (id: number) => get(`/ai/knowledge/document/${id}`),
  knowledgeDocSearch: (params: any) => get('/ai/knowledge/document-search', params),
  getKnowledgeDocs: (params: any) => get('/ai/knowledge/documents', params),
  deleteKnowledgeDoc: (id: number) => del(`/ai/knowledge/${id}`),
  getKnowledgeCategories: () => get('/ai/knowledge/categories'),
  knowledgeClassify: (content: string) => post('/ai/knowledge/classify', { content }),
  knowledgeAsk: (data: any) => post('/ai/knowledge/ask', data),
  getAnalysisReports: (params: any) => get('/ai/analysis/reports', params),
  getReport: (id: number) => get(`/ai/analysis/report/${id}`),
  startAnalysis: (data: any) => post('/ai/analysis', data),

  // === 5个智能体API ===
  agentStudent: (data: any) => post('/ai/agent/student', data),
  agentTeacher: (data: any) => post('/ai/agent/teacher', data),
  agentAdmin: (data: any) => post('/ai/agent/admin', data),
  agentEquipmentRecommend: (data: any) => post('/ai/agent/equipment-recommend', data),
  agentTopicReview: (data: any) => post('/ai/agent/topic-review', data),
  agentSubmissionReview: (data: any) => post('/ai/agent/submission-review', data),
  agentGeneral: (data: any) => post('/ai/agent/general', data),
  experimentRecommend: (data: any) => post('/ai/agent/experiment-recommend', data),
  recommendByTopic: (data: any) => post('/ai/agent/experiment-recommend-by-topic', data),
  saveExperiments: (topicId: number, data: any) => post('/user/submission/topic/' + topicId + '/save-experiments', data),
  recommendEquipmentByExperiments: (data: any) => post('/ai/agent/experiment-equipment-recommend', data),
  dataMining: (data: any) => post('/ai/agent/data-mining', data),
  chartGeneration: (data: any) => post('/ai/agent/chart-generation', data),
  extractText: (data: any) => post('/ai/agent/extract-text', data, { timeout: 60000 }),
  batchSubmitReservations: (data: any) => post('/reservation/batch-submit', data),
  autoReviewSubmission: (data: any) => post('/ai/agent/submission-auto-review', data),
  agentAnalysisRecommend: (data: { message: string }) => post('/ai/agent/analysis-recommend', data),
}

export const chatApi = {
  createConversation: (data: any) => post('/chat/conversation', data),
  getConversations: () => get('/chat/conversation/list'),
  getConversation: (id: number) => get(`/chat/conversation/${id}`),
  sendMessage: (data: any) => post('/chat/message', data),
  getMessages: (params: any) => get('/chat/message/list', params),
  markAsRead: (conversationId: number) => put(`/chat/conversation/${conversationId}/read`),
  getUnreadCount: () => get('/chat/unread-count'),
  deleteConversation: (id: number, deleteMessages?: boolean) => del(`/chat/conversation/${id}`, { params: { deleteMessages } })
}

export const fileApi = {
  upload: (formData: FormData) => post('/file/upload', formData)
}

export const classApi = {
  createClass: (data: any) => post('/user/class', data),
  getTeacherClasses: () => get('/user/class/teacher'),
  getStudentClasses: () => get('/user/class/student'),
  getClassDetail: (classId: number) => get(`/user/class/${classId}`),
  joinClass: (classCode: string) => post('/user/class/join', null, { params: { classCode } }),
  removeMember: (classId: number, userId: number) => del(`/user/class/${classId}/member/${userId}`),
  getClassMembers: (classId: number) => get(`/user/class/${classId}/members`),
  createHomework: (data: any) => post('/user/class/homework', data),
  getHomeworkList: (classId: number) => get(`/user/class/${classId}/homework`),
  getStudentHomeworkList: (classId: number) => get(`/user/class/${classId}/homework/student`),
  submitHomework: (data: any) => post('/user/class/homework/submit', data),
  gradeHomework: (data: any) => post('/user/class/homework/grade', data),
  getHomeworkSubmissions: (homeworkId: number) => get(`/user/class/homework/${homeworkId}/submissions`),
  createSignIn: (data: any) => post('/user/class/sign-in', data),
  getSignInList: (classId: number) => get(`/user/class/${classId}/sign-in`),
  doSignIn: (data: any) => post('/user/class/sign-in/do', data),
  getSignInRecords: (signInId: number) => get(`/user/class/sign-in/${signInId}/records`),
  endSignIn: (signInId: number) => post(`/user/class/sign-in/${signInId}/end`)
}

export const notificationApi = {
  getNotifications: (params: any) => get('/notification/list', params),
  getUnreadCount: () => get('/notification/unread-count'),
  markAsRead: (id: number) => put(`/notification/${id}/read`),
  markAllAsRead: () => put('/notification/read-all'),
  deleteNotification: (id: number) => del(`/notification/${id}`)
}

export const screenApi = {
  getStats: () => get('/dashboard/screen/stats'),
}

export const dashboardApi = {
  getStudentStats: () => get('/dashboard/student/stats'),
  getTeacherStats: () => get('/dashboard/teacher/stats'),
  getCampusAdminStats: () => get('/dashboard/campus-admin/stats'),
  getTrendData: (params?: any) => get('/dashboard/trend', params),
}

export const adminApi = {
  getStats: () => get('/auth/admin/stats'),
  getStudentList: (params?: any) => get('/auth/admin/student/list', params),
  getTeacherList: (params?: any) => get('/auth/admin/teacher/list', params),
  getLogList: (params?: any) => get('/auth/admin/log/list', params),
  getTrend: () => get('/auth/admin/trend'),
  getUserDetail: (id: number) => get(`/auth/admin/user/${id}`),
  updateUserStatus: (id: number, status: number) => put(`/auth/admin/user/${id}/status`, { status }),
}


export const analysisLibraryApi = {
  saveAnalysis: (data: any) => post('/analysis/library/save', data),
  getAnalysisList: () => get('/analysis/library/list'),
  getAnalysisDetail: (id: number) => get(`/analysis/library/${id}`),
  deleteAnalysis: (id: number) => del(`/analysis/library/${id}`),
  exportAnalysis: (id: number) => get(`/analysis/library/${id}/export`),
  getTodaySaveCount: () => get('/analysis/library/today-count'),
  getWeekTrend: () => get('/analysis/library/week-trend'),
}

export const submissionApi = {
  // AI Config (via data service at /data/** route)
  saveAiConfig: (topicId: number, data: any) => post('/user/submission/topic/' + topicId + '/ai-config', data),
  getAiConfig: (topicId: number) => get('/user/submission/topic/' + topicId + '/ai-config'),
  updateAiConfig: (topicId: number, data: any) => put('/user/submission/topic/' + topicId + '/ai-config', data),
  // Teachers
  getTeachers: (params?: any) => get('/user/campus/teacher/list', params),
  // AI
  aiSuggestTopic: (description: string) => post('/ai/topic/suggest', { description }),
  // Topics
  createTopic: (data: any) => post('/user/submission/topic', data),
  getMyTopics: () => get('/user/submission/topic/my'),
  getMySubmittedTopics: () => get('/user/submission/topic/my-submitted'),
  getPendingTopics: () => get('/user/submission/topic/pending'),
  getTopic: (id: number) => get(`/user/submission/topic/${id}`),
  approveTopic: (id: number) => put(`/user/submission/topic/${id}/approve`),
  rejectTopic: (id: number, reason: string) => put(`/user/submission/topic/${id}/reject`, { reason }),
  resubmitTopic: (id: number, data: any) => put(`/user/submission/topic/${id}/resubmit`, data),
  confirmTopic: (id: number) => post(`/user/submission/topic/${id}/confirm`),
  getTopicDetail: (topicId: number) => get('/user/submission/topic/' + topicId + '/detail'),
  // Submissions (file upload)
  submitFiles: (topicId: number, data: any) => post(`/user/submission/${topicId}/submit-files`, data),
  getMySubmission: (topicId: number) => get(`/user/submission/topic/${topicId}/my-submission`),
  getStudentSubmission: (topicId: number) => get(`/user/submission/topic/${topicId}/student-submission`),
  getSubmission: (recordId: number) => get(`/user/submission/submission/${recordId}`),
  // Files
  getFiles: (recordId: number) => get(`/user/submission/${recordId}/files`),
  saveFile: (data: any) => post('/user/submission/file', null, { params: data }),
  uploadSubmissionFile: (submissionId: number, formData: FormData) => post('/user/submission/file/upload?submissionId=' + submissionId, formData, { headers: { 'Content-Type': 'multipart/form-data' } }),
  deleteFile: (fileId: number) => del(`/user/submission/file/${fileId}`),
  // Reviews
  review: (topicId: number, data: any) => post(`/user/submission/${topicId}/review`, data),
  getLatestReview: (recordId: number) => get(`/user/submission/review/${recordId}/latest`),
  getReviewHistory: (recordId: number) => get(`/user/submission/review/${recordId}/history`),
  // New Topic Flow
  getAvailableTopics: () => get('/user/submission/topic/available'),
  getConfirmedTopics: () => get('/user/submission/topic/confirmed'),
  getCompletedTopics: () => get('/user/submission/topic/completed'),
  getSubmittedRecords: () => get('/user/submission/record/submitted'),
  getTeacherSubmissions: () => get('/user/submission/teacher/submissions'),
  passSubmission: (id: number, score: number, comment: string) => post(`/user/submission/record/${id}/pass?score=${score}&comment=${encodeURIComponent(comment)}`),
  rejectSubmission: (id: number, reason: string) => post(`/user/submission/record/${id}/reject`, { reason }),
  getSubmissionFiles: (recordId: number) => get(`/user/submission/${recordId}/files`),
  getAiConfig: (topicId: number) => get('/user/submission/topic/' + topicId + '/ai-config'),
}
export const labApi = {
  getLabList: () => get('/lab/list'),
  getLab: (id: number) => get('/lab/' + id),
  saveLab: (data: any) => post('/lab/save', data),
  updateLab: (data: any) => put('/lab/update', data),
  deleteLab: (id: number) => del('/lab/' + id),

  getEquipmentList: (labId?: number) => get('/equipment/list', { params: { labId } }),
  getEquipment: (id: number) => get('/equipment/' + id),
  searchEquipment: (keyword: string) => get('/equipment/search', { keyword }),
  saveEquipment: (data: any) => post('/equipment/save', data),
  updateEquipment: (data: any) => put('/equipment/update', data),
  deleteEquipment: (id: number) => del('/equipment/' + id),

  getTimeSlots: (equipmentId: number, date: string) => get('/reservation/slots', { equipmentId, date }),
  submitReservation: (data: any) => post('/reservation/submit', data),
  getMyReservations: () => get('/reservation/my'),
  getPendingReservations: () => get('/reservation/pending'),
  getAllReservations: () => get('/reservation/all'),
  approveReservation: (id: number) => post('/reservation/approve', { id }),
  rejectReservation: (id: number, reason: string) => post('/reservation/reject', { id, reason }),
  startUse: (id: number, password: string) => post('/reservation/start-use', { id, password }),
  endUse: (id: number, password: string) => post('/reservation/end-use', { id, password }),

  getMyViolations: () => get('/violation/my'),
  getAllViolations: () => get('/violation/all'),
  checkBan: () => get('/violation/check-ban'),

  reportMaintenance: (data: any) => post('/maintenance/report', data),
  getMaintenanceList: (status?: string) => get('/maintenance/list', { status }),
  getMyMaintenance: () => get('/maintenance/my'),
  reviewMaintenance: (id: number, action: string, remark: string) => post('/maintenance/review', { id, action, remark }),
  completeMaintenance: (id: number, remark: string) => post('/maintenance/complete', { id, remark }),
}

