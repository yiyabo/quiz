<template>
  <Layout>
    <div class="home-page">
      <!-- Hero Section -->
      <div class="hero-section">
        <div class="hero-content">
          <h1 class="hero-title">{{ currentCompetition?.title || 'Machine Learning Competition Platform' }}</h1>
          <p class="hero-subtitle">{{ currentCompetition?.description || 'Select a competition to start' }}</p>
          <div class="hero-actions">
            <el-button type="primary" size="large" @click="downloadDataset">
              <el-icon><Download /></el-icon>
              Download Dataset
            </el-button>
            <el-button size="large" @click="router.push('/leaderboard')">
              <el-icon><TrophyBase /></el-icon>
              View Leaderboard
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
                  <div class="stat-label">Participants</div>
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
                  <div class="stat-label">Submissions</div>
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
                  <div class="stat-label">Best Score</div>
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
                  <div class="stat-label">Average Score</div>
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
                  <span>Project Overview</span>
                </div>
              </template>
              <div class="info-content">
                <p><strong>Task Type:</strong> {{ competitionDetails.taskType }}</p>
                <p><strong>Input:</strong> {{ competitionDetails.input }}</p>
                <p><strong>Output:</strong> {{ competitionDetails.output }}</p>
                <p><strong>Dataset Size:</strong></p>
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
                  <span>Scoring Criteria</span>
                </div>
              </template>
              <div class="info-content">
                <p>Final score uses <strong>weighted multi-metric</strong> scoring:</p>
                <ul>
                  <li><strong>Accuracy</strong>: Weight 30%</li>
                  <li><strong>Precision</strong>: Weight 20%</li>
                  <li><strong>Recall</strong>: Weight 20%</li>
                  <li><strong>F1-Score</strong>: Weight 30%</li>
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
              <span>Quick Start</span>
            </div>
          </template>
          <el-steps :active="userStore.isLoggedIn ? 1 : 0" finish-status="success">
            <el-step title="Sign Up" description="Create your competition account" />
            <el-step title="Download Data" description="Get training and test datasets" />
            <el-step title="Train Model" description="Train your model with training set" />
            <el-step title="Submit Results" description="Upload prediction results CSV file" />
            <el-step title="View Ranking" description="Check your score on leaderboard" />
          </el-steps>
          
          <div class="action-buttons">
            <template v-if="!userStore.isLoggedIn">
              <el-button type="primary" size="large" @click="router.push('/register')">
                Register Now
              </el-button>
            </template>
            <template v-else>
              <el-button type="primary" size="large" @click="router.push('/submit')">
                Submit Predictions
              </el-button>
            </template>
          </div>
        </el-card>
      </div>
    </div>
  </Layout>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
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

const currentCompetition = computed(() => competitionStore.selectedCompetition)

const loadStatistics = async () => {
  try {
    stats.value = await statisticsAPI.getStatistics(competitionStore.selectedCompetitionId)
  } catch (error) {
    console.error('Failed to load statistics:', error)
  }
}

const competitionInfoMap = {
  ppi: {
    taskType: 'Protein Pair Binary Classification',
    input: 'Amino acid sequence features of two proteins',
    output: 'prediction column: 0 or 1, indicating interaction',
    dataset: [
      { label: 'Training Set', value: '11,436 samples' },
      { label: 'Validation Set', value: '2,287 samples' },
      { label: 'Test Set', value: '1,525 samples' }
    ]
  },
  cci: {
    taskType: 'Cell Pair Binary Classification',
    input: 'Cell pairs (source, target) in spatial transcriptomics',
    output: 'label column: 0 or 1, indicating cell-cell interaction',
    dataset: [
      { label: 'Training Set', value: '12,000 edges' },
      { label: 'Validation Set', value: '4,000 edges' },
      { label: 'Test Set', value: '4,000 edges' }
    ]
  }
}

const defaultCompetitionInfo = {
  taskType: 'Binary Classification Task',
  input: 'Prepare features according to competition data format',
  output: 'Output 0 or 1 prediction results',
  dataset: [
    { label: 'Training Set', value: 'See competition description' },
    { label: 'Validation Set', value: 'See competition description' },
    { label: 'Test Set', value: 'See competition description' }
  ]
}

const competitionDetails = computed(() => {
  const name = currentCompetition.value?.name
  return competitionInfoMap[name] || defaultCompetitionInfo
})

const downloadDataset = () => {
  if (!competitionStore.selectedCompetitionId) {
    ElMessage.warning('Please select a competition first')
    return
  }
  const url = downloadAPI.getDatasetUrl(competitionStore.selectedCompetitionId)
  window.open(url, '_blank')
  ElMessage.success(`Downloading ${currentCompetition.value?.title} dataset`)
}

// 监听竞赛切换
watch(() => competitionStore.selectedCompetitionId, () => {
  loadStatistics()
})

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
