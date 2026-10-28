# -*- coding: utf-8 -*-
content = open(r'C:\Users\14195\Documents\bishe\animed-platform\animed-frontend\src\views\campus\ClassDetail.vue', 'r', encoding='utf-8').read()

# Find and replace the old dialog
old_start = content.find('showSignInRecordsDialog')
old_end = content.find('</el-dialog>', old_start) + len('</el-dialog>')

new_dialog = '''    <el-dialog v-model="showSignInRecordsDialog" :title="isTeacher ? \'\u7b7e\u5230\u72b6\u6001\' : \'\u7b7e\u5230\u8bb0\u5f55\'" width="720px">
      <template v-if="isTeacher">
        <el-alert :title="\'\u5df2\u7b7e\u5230: \' + signInStatus.filter((s:any) => s.status === \'\u5df2\u7b7e\u5230\').length + \' / \u672a\u7b7e\u5230: \' + signInStatus.filter((s:any) => s.status === \'\u672a\u7b7e\u5230\').length + \' / \u5931\u8d25: \' + signInStatus.filter((s:any) => s.status === \'\u5931\u8d25\').length" type="info" :closable="false" style="margin-bottom:12px;" />
        <el-table :data="signInStatus" stripe>
          <el-table-column prop="studentNo" label="\u5b66\u53f7" width="120" />
          <el-table-column prop="studentName" label="\u59d3\u540d" width="100" />
          <el-table-column prop="status" label="\u72b6\u6001" width="80">
            <template #default="{ row }">
              <el-tag :type="row.status === \'\u5df2\u7b7e\u5230\' ? \'success\' : row.status === \'\u5931\u8d25\' ? \'danger\' : \'info\'" size="small">{{ row.status }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="\u7b7e\u5230\u65f6\u95f4" width="160">
            <template #default="{ row }">{{ row.signTime || \'-\' }}</template>
          </el-table-column>
          <el-table-column prop="failReason" label="\u5907\u6ce8" min-width="120">
            <template #default="{ row }">{{ row.failReason || \'-\' }}</template>
          </el-table-column>
          <el-table-column label="\u64cd\u4f5c" width="100" fixed="right">
            <template #default="{ row }">
              <el-button v-if="row.status === \'\u672a\u7b7e\u5230\'" size="small" type="warning" @click="handleProxySignIn(row.studentId)" :loading="proxyLoadingId === row.studentId">\u4ee3\u7b7e\u5230</el-button>
            </template>
          </el-table-column>
        </el-table>
      </template>
      <template v-else>
        <el-table :data="signInRecords" stripe>
          <el-table-column prop="studentName" label="\u59d3\u540d" width="120" />
          <el-table-column label="\u7b7e\u5230\u65f6\u95f4" width="160">
            <template #default="{ row }">{{ row.signTime ? row.signTime.replace(\'T\', \' \').substring(0,19) : \'\' }}</template>
          </el-table-column>
          <el-table-column prop="result" label="\u7ed3\u679c" width="80">
            <template #default="{ row }">
              <el-tag :type="row.result === \'\u6210\u529f\' ? \'success\' : \'danger\'" size="small">{{ row.result }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="failReason" label="\u5931\u8d25\u539f\u56e0" />
        </el-table>
      </template>
    </el-dialog>'''

# Check if we found the dialog
find_str = 'showSignInRecordsDialog'
start_idx = content.find(find_str)
# Find the actual start of the el-dialog
dialog_start = content.rfind('<el-dialog', 0, start_idx)
dialog_end = content.find('</el-dialog>', start_idx) + len('</el-dialog>')

if dialog_start >= 0 and dialog_end > dialog_start:
    content = content[:dialog_start] + new_dialog + content[dialog_end:]
    print('Dialog replaced successfully')
else:
    print('Could not find dialog bounds')

open(r'C:\Users\14195\Documents\bishe\animed-platform\animed-frontend\src\views\campus\ClassDetail.vue', 'w', encoding='utf-8').write(content)
print('File written')
