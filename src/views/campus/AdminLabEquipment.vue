<template>
  <div class="admin-equip page-container">
    <el-card><template #header><div class="flex-between"><span><el-icon><Monitor /></el-icon> 仪器管理</span><el-button type="primary" size="small" @click="showEdit(null)">新增仪器</el-button></div></template>
      <el-table :data="list" border stripe size="small" v-loading="loading" empty-text="暂无仪器">
        <el-table-column prop="name" label="名称" min-width="140" />
        <el-table-column prop="model" label="型号" width="130" />
        <el-table-column label="所属实验室" width="140"><template #default="{row}">{{ getLabName(row.labId) }}</template></el-table-column>
        <el-table-column label="状态" width="90">
          <template #default="{row}"><el-tag :type="statusType(row.status)" size="small">{{ statusLabel(row.status) }}</el-tag></template>
        </el-table-column>
        <el-table-column prop="price" label="价格" width="110">
          <template #default="{row}">¥{{ row.price?row.price.toLocaleString():'-' }}</template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{row}">
            <el-button size="small" link @click="showEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" link @click="del(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    <el-dialog v-model="dialogVisible" :title="isEdit?'编辑仪器':'新增仪器'" width="650px">
      <el-form :model="form" label-width="110px">
        <el-form-item label="名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="型号"><el-input v-model="form.model" /></el-form-item>
        <el-form-item label="所属实验室"><el-select v-model="form.labId" filterable style="width:100%"><el-option v-for="l in labs" :key="l.id" :label="l.name" :value="l.id" /></el-select></el-form-item>
        <el-form-item label="生产厂家"><el-input v-model="form.manufacturer" /></el-form-item>
        <el-form-item label="出厂编号"><el-input v-model="form.serialNumber" /></el-form-item>
        <el-row :gutter="12"><el-col :span="12"><el-form-item label="生产日期"><el-date-picker v-model="form.productionDate" type="date" style="width:100%" /></el-form-item></el-col><el-col :span="12"><el-form-item label="购买日期"><el-date-picker v-model="form.purchaseDate" type="date" style="width:100%" /></el-form-item></el-col></el-row>
        <el-row :gutter="12"><el-col :span="12"><el-form-item label="参考价格"><el-input v-model="form.price" type="number" /></el-form-item></el-col><el-col :span="12"><el-form-item label="赔偿价格"><el-input v-model="form.compensationPrice" type="number" /></el-form-item></el-col></el-row>
        <el-form-item label="技术规格"><el-input v-model="form.specifications" type="textarea" :rows="2" /></el-form-item>
        <el-form-item label="使用注意事项"><el-input v-model="form.usageNotes" type="textarea" :rows="2" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="dialogVisible=false">取消</el-button><el-button type="primary" @click="saveEquip">保存</el-button></template>
    </el-dialog>
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { labApi } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Monitor } from '@element-plus/icons-vue'
const list = ref<any[]>([]); const labs = ref<any[]>([]); const loading = ref(false)
const dialogVisible = ref(false); const isEdit = ref(false)
const form = ref<any>({ labId: null, name: '', model: '', manufacturer: '', serialNumber: '', productionDate: null, purchaseDate: null, price: null, compensationPrice: null, specifications: '', usageNotes: '' })
function getLabName(id: number) { const l = labs.value.find((x: any) => x.id === id); return l ? l.name : '-' }
function statusType(s: string) { return { normal: 'success', in_use: 'warning', pending_review: 'info', repairing: 'danger', damaged: 'danger' }[s] || 'info' }
function statusLabel(s: string) { return { normal: '正常', in_use: '使用中', pending_review: '待审查', repairing: '维修中', damaged: '损坏' }[s] || s }
async function loadData() { loading.value = true; try { const [r1, r2] = await Promise.all([labApi.getEquipmentList(), labApi.getLabList()]); list.value = r1.data || []; labs.value = r2.data || [] } catch {} finally { loading.value = false } }
function showEdit(row: any) { isEdit.value = !!row; form.value = row ? { ...row, productionDate: row.productionDate||null, purchaseDate: row.purchaseDate||null } : { labId: null, name: '', model: '', manufacturer: '', serialNumber: '', productionDate: null, purchaseDate: null, price: null, compensationPrice: null, specifications: '', usageNotes: '' }; dialogVisible.value = true }
async function saveEquip() { try { if (isEdit.value) await labApi.updateEquipment(form.value); else await labApi.saveEquipment(form.value); ElMessage.success('保存成功'); dialogVisible.value = false; await loadData() } catch { ElMessage.error('保存失败') } }
async function del(id: number) { try { await ElMessageBox.confirm('确定删除?'); await labApi.deleteEquipment(id); ElMessage.success('已删除'); await loadData() } catch {} }
onMounted(loadData)
</script>
<style scoped>.flex-between { display: flex; justify-content: space-between; align-items: center; }</style>
