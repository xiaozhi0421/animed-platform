<template>
  <div class="data-screen">
    <div class="bg-canvas">
      <div class="bg-orb bg-orb-1"></div>
      <div class="bg-orb bg-orb-2"></div>
      <div class="bg-orb bg-orb-3"></div>
      <div class="bg-grid"></div>
    </div>

    <div class="screen-container">
      <header class="screen-header">
        <div class="header-left">
          <div class="header-badge">
            <span class="live-dot"></span>
            <span>LIVE</span>
          </div>
          <h1 class="screen-title">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18"/><path d="M9 21V9"/><path d="M15 21V9"/>
            </svg>
            校园数据驾驶舱
          </h1>
        </div>
        <div class="header-right">
          <div class="time-display">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>
            </svg>
            <span>{{ currentTime }}</span>
          </div>
          <button class="refresh-btn" :class="{ refreshing: loading }" @click="fetchData">
            <svg class="refresh-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
              <polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/>
            </svg>
            刷新数据
          </button>
        </div>
      </header>

      <section class="metrics-row" v-if="stats">
        <div class="metric-card" v-for="(card, idx) in metricCards" :key="idx" :style="{ '--card-hue': card.hue }">
          <div class="metric-glow"></div>
          <div class="metric-icon-wrap" :style="{ background: card.iconBg }">
            <span v-html="card.icon"></span>
          </div>
          <div class="metric-body">
            <div class="metric-label">{{ card.label }}</div>
            <div class="metric-value">{{ formatNum(card.value) }}</div>
            <div class="metric-footer">
              <span v-for="(item, i) in card.items" :key="i" class="metric-tag" :style="{ '--tag-color': item.color }">
                <span class="metric-dot"></span>
                {{ item.label }}{{ item.value }}
              </span>
            </div>
          </div>
        </div>
      </section>

      <section class="charts-section" v-if="stats">
        <div class="chart-panel chart-pie">
          <div class="panel-header">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>
            <span>设备状态分布</span>
          </div>
          <div ref="equipChartRef" class="chart-container"></div>
        </div>
        <div class="chart-panel chart-pie">
          <div class="panel-header">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4"/><path d="M8 2v4"/><path d="M3 10h18"/></svg>
            <span>预约状态分布</span>
          </div>
          <div ref="resChartRef" class="chart-container"></div>
        </div>
        <div class="chart-panel chart-trend">
          <div class="panel-header">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>
            <span>各实验室仪器分布</span>
          </div>
          <div ref="labEquipChartRef" class="chart-container"></div>
        </div>
      </section>

      <section class="bottom-section" v-if="stats">
        <div class="bottom-panel recent-panel">
          <div class="panel-header">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
            <span>最近预约记录</span>
          </div>
          <div class="table-wrap">
            <table class="screen-table">
              <thead><tr><th>用户</th><th>仪器</th><th>日期</th><th>时段</th><th>状态</th></tr></thead>
              <tbody>
                <tr v-for="r in (stats.recentReservations || [])" :key="r.id">
                  <td><span class="cell-primary">{{ r.userName }}</span></td>
                  <td>{{ r.equipmentName }}</td>
                  <td>{{ r.reserveDate }}</td>
                  <td>{{ r.timeSlot }}</td>
                  <td><span :class="['badge', r.status]">{{ statusLabel(r.status) }}</span></td>
                </tr>
                <tr v-if="!(stats.recentReservations || []).length"><td colspan="5" class="empty-cell">暂无预约数据</td></tr>
              </tbody>
            </table>
          </div>
        </div>
        <div class="bottom-panel summary-panel">
          <div class="panel-header">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12a9 9 0 1 1-9-9"/><path d="M21 3v6h-6"/><path d="M12 7v5l3 2"/></svg>
            <span>快速概览</span>
          </div>
          <div class="summary-grid">
            <div class="summary-item" v-for="(s, i) in summaries" :key="i">
              <div class="summary-dot" :style="{ background: s.color }"></div>
              <div class="summary-info">
                <span class="summary-label">{{ s.label }}</span>
                <span class="summary-value">{{ s.value }}</span>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from "vue";
import * as echarts from "echarts";
import { screenApi } from "@/api";

const stats = ref(null);
const loading = ref(false);
const currentTime = ref("");
let timeInterval = null;
const equipChartRef = ref(null);
const resChartRef = ref(null);
const trendChartRef = ref(null);
const labEquipChartRef = ref(null);
let equipChart = null, resChart = null, trendChart = null, labEquipChart = null;

function updateTime() {
  const now = new Date();
  currentTime.value = now.toLocaleTimeString("zh-CN", { hour12: false });
}

function formatNum(n) {
  if (n >= 10000) return (n / 10000).toFixed(1) + "w";
  return n?.toLocaleString() || "0";
}

const metricCards = computed(() => {
  if (!stats.value) return [];
  const s = stats.value;
  return [
    { label: "总用户数", value: s.users?.total || 0, hue: 250,
      iconBg: "linear-gradient(135deg,#6366f1,#8b5cf6)",
      icon: "<svg width=20 height=20 viewBox='0 0 24 24' fill='none' stroke='#fff' stroke-width='1.5'><path d='M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2'/><circle cx='9' cy='7' r='4'/><path d='M23 21v-2a4 4 0 0 0-3-3.87'/><path d='M16 3.13a4 4 0 0 1 0 7.75'/></svg>",
      items: [{ label: "学生 ", value: s.users?.students || 0, color: "#60a5fa" }, { label: "教师 ", value: s.users?.teachers || 0, color: "#4ade80" }] },
    { label: "实验室", value: s.labs?.total || 0, hue: 190,
      iconBg: "linear-gradient(135deg,#06b6d4,#0891b2)",
      icon: "<svg width=20 height=20 viewBox='0 0 24 24' fill='none' stroke='#fff' stroke-width='1.5'><path d='M22 12h-4l-3 9L9 3l-3 9H2'/></svg>",
      items: [{ label: "正常 ", value: s.labs?.normal || 0, color: "#4ade80" }, { label: "维修中 ", value: s.labs?.maintenance || 0, color: "#fbbf24" }] },
    { label: "仪器总数", value: s.equipment?.total || 0, hue: 40,
      iconBg: "linear-gradient(135deg,#f59e0b,#d97706)",
      icon: "<svg width=20 height=20 viewBox='0 0 24 24' fill='none' stroke='#fff' stroke-width='1.5'><rect x='2' y='2' width='20' height='8' rx='2'/><rect x='2' y='14' width='20' height='8' rx='2'/></svg>",
      items: [{ label: "正常 ", value: s.equipment?.normal || 0, color: "#4ade80" }, { label: "使用中 ", value: s.equipment?.in_use || 0, color: "#60a5fa" }] },
    { label: "预约总数", value: s.reservations?.total || 0, hue: 160,
      iconBg: "linear-gradient(135deg,#10b981,#059669)",
      icon: "<svg width=20 height=20 viewBox='0 0 24 24' fill='none' stroke='#fff' stroke-width='1.5'><rect x='3' y='4' width='18' height='18' rx='2'/><path d='M16 2v4'/><path d='M8 2v4'/><path d='M3 10h18'/></svg>",
      items: [{ label: "待审 ", value: s.reservations?.pending || 0, color: "#fbbf24" }, { label: "已批 ", value: s.reservations?.approved || 0, color: "#4ade80" }] },
    { label: "课题数", value: s.topics?.total || 0, hue: 330,
      iconBg: "linear-gradient(135deg,#ec4899,#db2777)",
      icon: "<svg width=20 height=20 viewBox='0 0 24 24' fill='none' stroke='#fff' stroke-width='1.5'><path d='M12 2L2 7l10 5 10-5-10-5z'/><path d='M2 17l10 5 10-5'/><path d='M2 12l10 5 10-5'/></svg>",
      items: [{ label: "待审阅 ", value: s.topics?.pending || 0, color: "#fbbf24" }, { label: "已通过 ", value: s.topics?.approved || 0, color: "#4ade80" }] },
    { label: "课程数", value: (typeof s.courses === "number" ? s.courses : s.courses?.total || 0), hue: 270,
      iconBg: "linear-gradient(135deg,#8b5cf6,#7c3aed)",
      icon: "<svg width=20 height=20 viewBox='0 0 24 24' fill='none' stroke='#fff' stroke-width='1.5'><path d='M4 19.5A2.5 2.5 0 0 1 6.5 17H20'/><path d='M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z'/></svg>",
      items: [{ label: "数据集 ", value: s.datasets || 0, color: "#818cf8" }] },
  ];
});

const summaries = computed(() => {
  if (!stats.value) return [];
  const s = stats.value;
  return [
    { label: "维修工单", value: s.maintenances?.total || 0, color: "#f59e0b" },
    { label: "待处理工单", value: s.maintenances?.pending || 0, color: "#ef4444" },
    { label: "数据集数", value: s.datasets || 0, color: "#06b6d4" },
    { label: "知识文档", value: s.knowledgeDocs || 0, color: "#10b981" },
    { label: "违规记录", value: s.violations || 0, color: "#8b5cf6" },
    { label: "系统消息", value: s.messages || 0, color: "#6366f1" },
  ];
});

function statusLabel(status) {
  const map = { pending: "待审批", approved: "已批准", in_use: "使用中", completed: "已完成", rejected: "已驳回" };
  return map[status] || status;
}

function getCT() {
  return { backgroundColor: "transparent", textStyle: { color: "rgba(255,255,255,0.6)", fontSize: 11 } };
}

function chartTooltip() {
  return { trigger: "item", backgroundColor: "rgba(15,15,30,0.9)", borderColor: "rgba(6,182,212,0.2)", borderWidth: 1, textStyle: { color: "#fff", fontSize: 12 } };
}

function renderCharts() {
  if (!stats.value) return;
  const p = (d) => d.filter((x) => x.v > 0);
  if (equipChartRef.value) {
    if (equipChart) equipChart.dispose();
    equipChart = echarts.init(equipChartRef.value);
    const eq = stats.value.equipment || {};
    const data = p([{ n: "正常", v: eq.normal || 0, c: "#10b981" }, { n: "使用中", v: eq.in_use || 0, c: "#06b6d4" }, { n: "维修中", v: eq.maintenance || 0, c: "#f59e0b" }, { n: "已报废", v: eq.scrapped || 0, c: "#ef4444" }]);
    if (!data.length) data.push({ n: "暂无数据", v: 1, c: "#374151" });
    equipChart.setOption({ ...getCT(), tooltip: chartTooltip(), series: [{ type: "pie", radius: ["48%", "72%"], center: ["50%", "52%"], avoidLabelOverlap: true, padAngle: 2, itemStyle: { borderRadius: 4, borderColor: "rgba(10,10,26,0.8)", borderWidth: 2 }, label: { color: "rgba(255,255,255,0.65)", fontSize: 11 }, emphasis: { itemStyle: { shadowBlur: 10 }, label: { fontSize: 13, color: "#fff" } }, data: data.map((d) => ({ name: d.n, value: d.v, itemStyle: { color: d.c } })) }] });
  }
  if (resChartRef.value) {
    if (resChart) resChart.dispose();
    resChart = echarts.init(resChartRef.value);
    const r = stats.value.reservations || {};
    const data = p([{ n: "待审批", v: r.pending || 0, c: "#f59e0b" }, { n: "已批准", v: r.approved || 0, c: "#10b981" }, { n: "使用中", v: r.in_use || 0, c: "#06b6d4" }, { n: "已完成", v: r.completed || 0, c: "#8b5cf6" }, { n: "已驳回", v: r.rejected || 0, c: "#ef4444" }]);
    if (!data.length) data.push({ n: "暂无数据", v: 1, c: "#374151" });
    resChart.setOption({ ...getCT(), tooltip: chartTooltip(), series: [{ type: "pie", radius: ["48%", "72%"], center: ["50%", "52%"], avoidLabelOverlap: true, padAngle: 2, itemStyle: { borderRadius: 4, borderColor: "rgba(10,10,26,0.8)", borderWidth: 2 }, label: { color: "rgba(255,255,255,0.65)", fontSize: 11 }, emphasis: { itemStyle: { shadowBlur: 10 }, label: { fontSize: 13, color: "#fff" } }, data: data.map((d) => ({ name: d.n, value: d.v, itemStyle: { color: d.c } })) }] });
  }
  if (labEquipChartRef.value) {
    if (labEquipChart) labEquipChart.dispose();
    labEquipChart = echarts.init(labEquipChartRef.value);
    const labs = stats.value.equipmentInLabs || [];
    const names = labs.map((d) => d.labName || "未知");
    const counts = labs.map((d) => d.cnt || 0);
    labEquipChart.setOption({ ...getCT(), tooltip: { trigger: "axis", backgroundColor: "rgba(15,15,30,0.9)", borderColor: "rgba(6,182,212,0.2)", borderWidth: 1, textStyle: { color: "#fff", fontSize: 12 } }, grid: { left: "3%", right: "8%", bottom: "3%", top: "8%", containLabel: true }, xAxis: { type: "value", axisLine: { show: false }, axisTick: { show: false }, axisLabel: { color: "rgba(255,255,255,0.4)", fontSize: 10 }, splitLine: { lineStyle: { color: "rgba(255,255,255,0.04)", type: "dashed" } } }, yAxis: { type: "category", data: names, axisLine: { lineStyle: { color: "rgba(255,255,255,0.08)" } }, axisLabel: { color: "rgba(255,255,255,0.6)", fontSize: 10 }, splitLine: { show: false } }, series: [{ type: "bar", data: counts.map((v, i) => ({ value: v, itemStyle: { color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [{ offset: 0, color: "#06b6d4" }, { offset: 1, color: "#6366f1" }]) } })), barWidth: 14, label: { show: true, position: "right", color: "rgba(255,255,255,0.6)", fontSize: 11 } }] });
  }
}

async function fetchData() {
  loading.value = true;
  try {
    const res = await screenApi.getStats();
    stats.value = res.data || res;
    await nextTick();
    renderCharts();
  } catch (e) { console.error(e); }
  finally { loading.value = false; }
}

function handleResize() { equipChart?.resize(); resChart?.resize(); trendChart?.resize(); labEquipChart?.resize(); }

onMounted(() => {
  updateTime();
  timeInterval = setInterval(updateTime, 1000);
  fetchData();
  window.addEventListener("resize", handleResize);
});
onUnmounted(() => {
  clearInterval(timeInterval);
  equipChart?.dispose(); resChart?.dispose(); trendChart?.dispose(); labEquipChart?.dispose();
  window.removeEventListener("resize", handleResize);
});
</script>

<style scoped>
.animate-pulse-slow{animation:pulseSlow 8s ease-in-out infinite}
@keyframes pulseSlow{0%,100%{transform:translate(0,0) scale(1);opacity:0.1}50%{transform:translate(40px,-50px) scale(1.2);opacity:0.15}}
.data-screen{position:relative;min-height:calc(100vh - 80px);background:#0a0a1a;color:#e2e8f0;padding:20px 24px 40px;overflow:hidden}
.bg-canvas{position:fixed;inset:0;pointer-events:none;z-index:0}
.bg-grid{position:absolute;inset:0;background-image:linear-gradient(rgba(6,182,212,0.03) 1px,transparent 1px),linear-gradient(90deg,rgba(6,182,212,0.03) 1px,transparent 1px);background-size:60px 60px}
.screen-container{position:relative;z-index:1;max-width:1400px;margin:0 auto}
.screen-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:24px;animation:fadeIn .6s ease-out}
.header-left{display:flex;align-items:center;gap:14px}
.header-badge{display:flex;align-items:center;gap:6px;background:rgba(6,182,212,.1);border:1px solid rgba(6,182,212,.2);border-radius:6px;padding:4px 10px;font-size:11px;font-weight:600;color:#22d3ee}
.live-dot{width:6px;height:6px;border-radius:50%;background:#22d3ee;animation:livePulse 1.5s ease-in-out infinite}
@keyframes livePulse{0%,100%{opacity:1;box-shadow:0 0 4px #22d3ee}50%{opacity:.4;box-shadow:0 0 8px #22d3ee}}
.screen-title{display:flex;align-items:center;gap:10px;font-size:22px;font-weight:700;background:linear-gradient(135deg,#e2e8f0,#94a3b8);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.header-right{display:flex;align-items:center;gap:12px}
.time-display{display:flex;align-items:center;gap:6px;font-size:13px;color:rgba(255,255,255,.5);font-variant-numeric:tabular-nums}
.refresh-btn{display:flex;align-items:center;gap:6px;background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.08);border-radius:8px;padding:7px 14px;font-size:12px;color:rgba(255,255,255,.6);cursor:pointer;transition:all .2s}
.refresh-btn:hover{background:rgba(6,182,212,.12);border-color:rgba(6,182,212,.25);color:#22d3ee}
.refreshing .refresh-icon{animation:spin 1s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
.metrics-row{display:grid;grid-template-columns:repeat(6,1fr);gap:14px;margin-bottom:20px;animation:fadeIn .6s ease-out}
.metric-card{position:relative;background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.06);border-radius:12px;padding:16px 14px;overflow:hidden;transition:all .25s}
.metric-card:hover{border-color:rgba(6,182,212,.2);transform:translateY(-2px);background:rgba(255,255,255,.05)}
.metric-icon-wrap{width:36px;height:36px;border-radius:10px;display:flex;align-items:center;justify-content:center;margin-bottom:10px}
.metric-label{font-size:11px;color:rgba(255,255,255,.5);font-weight:500;margin-bottom:4px}
.metric-value{font-size:24px;font-weight:700;background:linear-gradient(135deg,#fff,#94a3b8);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;margin-bottom:6px}
.metric-footer{display:flex;gap:8px;flex-wrap:wrap}
.metric-tag{display:flex;align-items:center;gap:4px;font-size:10px;padding:2px 8px;border-radius:4px;font-weight:500}
.metric-dot{width:5px;height:5px;border-radius:50%;background:var(--tag-color)}
.charts-section{display:grid;grid-template-columns:1fr 1fr 1.2fr;gap:14px;margin-bottom:20px;animation:fadeIn .6s ease-out .15s both}
.chart-panel{background:rgba(255,255,255,.02);border:1px solid rgba(255,255,255,.06);border-radius:12px;padding:16px}
.panel-header{display:flex;align-items:center;gap:8px;font-size:13px;font-weight:600;color:rgba(255,255,255,.7);margin-bottom:10px}
.chart-container{width:100%;height:220px}
.bottom-section{display:grid;grid-template-columns:1.6fr 1fr;gap:16px;animation:fadeIn .6s ease-out .3s both}
.bottom-panel{background:rgba(255,255,255,.02);border:1px solid rgba(255,255,255,.06);border-radius:12px;padding:18px}
.table-wrap{overflow-x:auto}
.screen-table{width:100%;border-collapse:collapse;font-size:12px}
.screen-table th{text-align:left;padding:8px 10px;color:rgba(255,255,255,.35);font-weight:500;border-bottom:1px solid rgba(255,255,255,.05);font-size:11px}
.screen-table td{padding:8px 10px;border-bottom:1px solid rgba(255,255,255,.03);color:rgba(255,255,255,.6)}
.cell-primary{color:rgba(255,255,255,.8);font-weight:500}
.empty-cell{text-align:center;color:rgba(255,255,255,.2);padding:24px}
.badge{display:inline-block;padding:2px 10px;border-radius:4px;font-size:11px;font-weight:500}
.badge.pending{background:rgba(245,158,11,.15);color:#fbbf24}
.badge.approved{background:rgba(16,185,129,.15);color:#4ade80}
.badge.in_use{background:rgba(6,182,212,.15);color:#22d3ee}
.badge.completed{background:rgba(139,92,246,.15);color:#a78bfa}
.badge.rejected{background:rgba(239,68,68,.15);color:#f87171}
.summary-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.summary-item{display:flex;align-items:center;gap:10px;padding:10px 12px;background:rgba(255,255,255,.02);border-radius:10px;border:1px solid rgba(255,255,255,.04)}
.summary-dot{width:8px;height:8px;border-radius:50%;flex-shrink:0}
.summary-info{display:flex;flex-direction:column;gap:2px}
.summary-label{font-size:11px;color:rgba(255,255,255,.4)}
.summary-value{font-size:16px;font-weight:700;color:rgba(255,255,255,.85)}
@keyframes fadeIn{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:translateY(0)}}
@media(max-width:1200px){.metrics-row{grid-template-columns:repeat(3,1fr)}.charts-section{grid-template-columns:1fr 1fr}.chart-trend{grid-column:1/-1}}
@media(max-width:768px){.metrics-row{grid-template-columns:repeat(2,1fr)}.charts-section{grid-template-columns:1fr}.bottom-section{grid-template-columns:1fr}}
</style>