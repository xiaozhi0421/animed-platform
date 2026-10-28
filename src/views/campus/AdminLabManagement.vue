<template>
  <div class="admin-labs page-container">
    <el-card><template #header><div class="flex-between"><span><el-icon><OfficeBuilding /></el-icon> 实验室管理</span><el-button type="primary" size="small" @click="showEdit(null)">新增实验室</el-button></div></template>
      <el-table :data="list" border stripe size="small" v-loading="loading" empty-text="暂无实验室">
        <el-table-column prop="name" label="名称" min-width="150" />
        <el-table-column prop="building" label="楼栋" width="100" />
        <el-table-column prop="room" label="房间" width="80" />
        <el-table-column prop="equipmentCount" label="仪器数" width="80" align="center" />
        <el-table-column label="状态" width="90">
          <template #default="{row}"><el-tag :type="row.status==='normal'?'success':'warning'" size="small">{{ row.status==='normal'?'正常':'维护中' }}</el-tag></template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{row}">
            <el-button size="small" link @click="showEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" link @click="del(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    <el-dialog v-model="dialogVisible" :title="isEdit?'编辑实验室':'新增实验室'" width="500px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="楼栋"><el-input v-model="form.building" /></el-form-item>
        <el-form-item label="楼层/房间"><el-input v-model="form.room" placeholder="如: 3层301" /></el-form-item>
        <el-form-item label="状态"><el-select v-model="form.status"><el-option label="正常" value="normal" /><el-option label="维护" value="maintenance" /></el-select></el-form-item>
        <el-form-item label="描述"><el-input v-model="form.description" type="textarea" :rows="3" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="dialogVisible=false">取消</el-button><el-button type="primary" @click="saveLab">保存</el-button></template>
    </el-dialog>
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { labApi } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import { OfficeBuilding } from '@element-plus/icons-vue'
const list = ref<any[]>([]); const loading = ref(false); const dialogVisible = ref(false); const isEdit = ref(false)
const form = ref<any>({ name: '', building: '', room: '', status: 'normal', description: '' })
async function loadData() { loading.value = true; try { const r: any = await labApi.getLabList(); list.value = r.data || [] } catch {} finally { loading.value = false } }
function showEdit(row: any) { isEdit.value = !!row; form.value = row ? { ...row } : { name: '', building: '', room: '', status: 'normal', description: '' }; dialogVisible.value = true }
async function saveLab() { try { if (isEdit.value) await labApi.updateLab(form.value); else await labApi.saveLab(form.value); ElMessage.success('保存成功'); dialogVisible.value = false; await loadData() } catch (e: any) { ElMessage.error('保存失败') } }
async function del(id: number) { try { await ElMessageBox.confirm('确定删除?'); await labApi.deleteLab(id); ElMessage.success('已删除'); await loadData() } catch {} }
onMounted(loadData)
</script>
<style scoped>.flex-between { display: flex; justify-content: space-between; align-items: center; }</style>
