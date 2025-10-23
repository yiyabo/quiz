<template>
  <Layout>
    <div class="home-page">
      <!-- Hero Section -->
      <div class="hero-section">
        <div class="hero-content">
          <h1 class="hero-title">{{ currentCompetition?.title || '机器学习竞赛平台' }}</h1>
          <p class="hero-subtitle">{{ currentCompetition?.description || '选择竞赛开始挑战' }}</p>
          <div class="hero-actions">
            <el-button type="primary" size="large" @click="downloadDataset">
              <el-icon><Download /></el-icon>
              下载数据集
            </el-button>
            <el-button size="large" @click="router.push('/leaderboard')">
              <el-icon><TrophyBase /></el-icon>
              查看排行榜
            </el-button>
          </div>
        </div>
      </div>
      
      <!-- Stats Section -->
      <div class="stats-section">
        <el-row :gutter="20">
          <el-col :xs="24" :sm="12" :md="6">
            <el-card class="stat-card">
              <div class="stat-content">
                <el-icon :size="40" color="#409eff"><User /></el-icon>
                <div class="stat-info">
                  <div class="stat-value">{{ stats.total_users }}</div>
                  <div class="stat-label">参赛用户</div>
                </div>
              </div>
            </el-card>
          </el-col>
          
          <el-col :xs="24" :sm="12" :md="6">
            <el-card class="stat-card">
              <div class="stat-content">
                <el-icon :size="40" color="#67c23a"><Upload /></el-icon>
                <div class="stat-info">
                  <div class="stat-value">{{ stats.total_submissions }}</div>
                  <div class="stat-label">提交次数</div>
                </div>
              </div>
            </el-card>
          </el-col>
          
          <el-col :xs="24" :sm="12" :md="6">
            <el-card class="stat-card">
              <div class="stat-content">
                <el-icon :size="40" color="#e6a23c"><TrophyBase /></el-icon>
                <div class="stat-info">
                  <div class="stat-value">{{ stats.best_score.toFixed(4) }}</div>
                  <div class="stat-label">最高分数</div>
                </div>
              </div>
            </el-card>
          </el-col>
          
          <el-col :xs="24" :sm="12" :md="6">
            <el-card class="stat-card">
              <div class="stat-content">
                <el-icon :size="40" color="#f56c6c"><DataAnalysis /></el-icon>
                <div class="stat-info">
                  <div class="stat-value">{{ stats.avg_score.toFixed(4) }}</div>
                  <div class="stat-label">平均分数</div>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>
      
      <!-- Info Section -->
      <div class="info-section">
        <el-row :gutter="30">
          <el-col :xs="24" :md="12">
            <el-card class="info-card">
              <template #header>
                <div class="card-header">
                  <el-icon><Document /></el-icon>
                  <span>项目简介</span>
                </div>
              </template>
              <div class="info-content">
                <p><strong>任务类型：</strong>{{ competitionDetails.taskType }}</p>
                <p><strong>输入：</strong>{{ competitionDetails.input }}</p>
                <p><strong>输出：</strong>{{ competitionDetails.output }}</p>
                <p><strong>数据集规模：</strong></p>
                <ul>
                  <li v-for="item in competitionDetails.dataset" :key="item.label">
                    {{ item.label }}：{{ item.value }}
                  </li>
                </ul>
              </div>
            </el-card>
          </el-col>
          
          <el-col :xs="24" :md="12">
            <el-card class="info-card">
              <template #header>
                <div class="card-header">
                  <el-icon><Medal /></el-icon>
                  <span>评分标准</span>
                </div>
              </template>
              <div class="info-content">
                <p>最终得分采用<strong>加权多指标</strong>评分：</p>
                <ul>
                  <li><strong>Accuracy</strong> (准确率)：权重 30%</li>
                  <li><strong>Precision</strong> (精确率)：权重 20%</li>
                  <li><strong>Recall</strong> (召回率)：权重 20%</li>
                  <li><strong>F1-Score</strong>：权重 30%</li>
                </ul>
                <p class="formula">
                  <strong>Final Score = </strong>
                  Accuracy × 0.3 + Precision × 0.2 + Recall × 0.2 + F1 × 0.3
                </p>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>
      
      <!-- Quick Start -->
      <div class="quickstart-section">
        <el-card>
          <template #header>
            <div class="card-header">
              <el-icon><Guide /></el-icon>
              <span>快速开始</span>
            </div>
          </template>
          <el-steps :active="userStore.isLoggedIn ? 1 : 0" finish-status="success">
            <el-step title="注册账号" description="创建你的竞赛账号" />
            <el-step title="下载数据" description="获取训练和测试数据集" />
            <el-step title="训练模型" description="使用训练集训练你的模型" />
            <el-step title="提交结果" description="上传预测结果CSV文件" />
            <el-step title="查看排名" description="在排行榜上查看你的成绩" />
          </el-steps>
          
          <div class="action-buttons">
            <template v-if="!userStore.isLoggedIn">
              <el-button type="primary" size="large" @click="router.push('/register')">
                立即注册参赛
              </el-button>
            </template>
            <template v-else>
              <el-button type="primary" size="large" @click="router.push('/submit')">
                提交预测结果
              </el-button>
            </template>
          </div>
        </el-card>
      </div>
    </div>
  </Layout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import { useCompetitionStore } from '../stores/competition'
import { statisticsAPI, downloadAPI } from '../api'
import { ElMessage } from 'element-plus'
import Layout from '../components/Layout.vue'

const router = useRouter()
const userStore = useUserStore()
const competitionStore = useCompetitionStore()

const stats = ref({
  total_users: 0,
  total_submissions: 0,
  avg_score: 0,
  best_score: 0
})

const loadStatistics = async () => {
  try {
    stats.value = await statisticsAPI.getStatistics()
  } catch (error) {
    console.error('Failed to load statistics:', error)
  }
}

const currentCompetition = computed(() => competitionStore.selectedCompetition)

const competitionInfoMap = {
  ppi: {
    taskType: '蛋白质对二分类',
    input: '两个蛋白质的氨基酸序列特征',
    output: 'prediction 列为 0 或 1，表示是否发生相互作用',
    dataset: [
      { label: '训练集', value: '11,436 条样本' },
      { label: '验证集', value: '2,287 条样本' },
      { label: '测试集', value: '1,525 条样本' }
    ]
  },
  cci: {
    taskType: '细胞对二分类',
    input: '空间转录组图中的细胞对 (source, target)',
    output: 'label 列为 0 或 1，表示是否存在细胞间相互作用',
    dataset: [
      { label: '训练集', value: '12,000 条边' },
      { label: '验证集', value: '4,000 条边' },
      { label: '测试集', value: '4,000 条边' }
    ]
  }
}

const defaultCompetitionInfo = {
  taskType: '二分类任务',
  input: '根据所选竞赛的数据格式准备特征',
  output: '输出 0 或 1 的预测结果',
  dataset: [
    { label: '训练集', value: '请查看竞赛说明' },
    { label: '验证集', value: '请查看竞赛说明' },
    { label: '测试集', value: '请查看竞赛说明' }
  ]
}

const competitionDetails = computed(() => {
  const name = currentCompetition.value?.name
  return competitionInfoMap[name] || defaultCompetitionInfo
})

const downloadDataset = () => {
  if (!competitionStore.selectedCompetitionId) {
    ElMessage.warning('请先选择竞赛')
    return
  }
  const url = downloadAPI.getDatasetUrl(competitionStore.selectedCompetitionId)
  window.open(url, '_blank')
  ElMessage.success(`正在下载 ${currentCompetition.value?.title} 数据集`)
}

onMounted(() => {
  competitionStore.loadCompetitions()
  loadStatistics()
})
</script>

<style scoped>
.home-page {
  padding-bottom: 40px;
}

.hero-section {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  padding: 80px 40px;
  text-align: center;
  color: white;
  margin-bottom: 30px;
}

.hero-title {
  font-size: 42px;
  font-weight: bold;
  margin-bottom: 16px;
}

.hero-subtitle {
  font-size: 18px;
  margin-bottom: 32px;
  opacity: 0.9;
}

.hero-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
  flex-wrap: wrap;
}

.stats-section {
  margin-bottom: 30px;
}

.stat-card {
  text-align: center;
  margin-bottom: 20px;
}

.stat-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  padding: 10px;
}

.stat-info {
  text-align: left;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 4px;
}

.info-section {
  margin-bottom: 30px;
}

.info-card {
  margin-bottom: 20px;
  height: 100%;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: bold;
  font-size: 16px;
}

.info-content {
  font-size: 14px;
  line-height: 1.8;
}

.info-content p {
  margin-bottom: 12px;
}

.info-content ul {
  margin-left: 20px;
  margin-bottom: 12px;
}

.info-content li {
  margin-bottom: 6px;
}

.formula {
  background: #f5f7fa;
  padding: 12px;
  border-radius: 4px;
  border-left: 4px solid #409eff;
  font-family: monospace;
}

.quickstart-section {
  margin-bottom: 30px;
}

.action-buttons {
  margin-top: 40px;
  text-align: center;
}

@media (max-width: 768px) {
  .hero-title {
    font-size: 28px;
  }
  
  .hero-subtitle {
    font-size: 16px;
  }
  
  .hero-section {
    padding: 40px 20px;
  }
}
</style>
