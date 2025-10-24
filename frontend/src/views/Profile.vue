<template>
  <Layout>
    <div class="profile-page">
      <el-row :gutter="20">
        <!-- 左侧：用户信息 -->
        <el-col :xs="24" :md="8">
          <el-card class="user-card">
            <div class="user-info">
              <el-avatar :size="100">{{ userStore.user?.username?.charAt(0).toUpperCase() }}</el-avatar>
              <h2>{{ userStore.user?.username }}</h2>
              <p class="email">{{ userStore.user?.email }}</p>
              <p class="join-date">
                Joined: {{ formatDate(userStore.user?.created_at) }}
              </p>
            </div>
          </el-card>
          
          <el-card class="stats-card">
            <template #header>
              <div class="card-header">
                <el-icon><DataAnalysis /></el-icon>
                <span>My Statistics</span>
              </div>
            </template>
            <div class="stat-item">
              <div class="stat-label">Total Submissions</div>
              <div class="stat-value">{{ myStats.totalSubmissions }}</div>
            </div>
            <div class="stat-item">
              <div class="stat-label">Successful</div>
              <div class="stat-value success">{{ myStats.successSubmissions }}</div>
            </div>
            <div class="stat-item">
              <div class="stat-label">Best Score</div>
              <div class="stat-value best">
                {{ myStats.bestScore !== null ? myStats.bestScore.toFixed(4) : '-' }}
              </div>
            </div>
            <div class="stat-item" v-if="myStats.rank">
              <div class="stat-label">Current Rank</div>
              <div class="stat-value rank">
                #{{ myStats.rank }}
              </div>
            </div>
          </el-card>
        </el-col>
        
        <!-- 右侧：提交历史 -->
        <el-col :xs="24" :md="16">
          <el-card class="history-card">
            <template #header>
              <div class="card-header">
                <div>
                  <el-icon><Document /></el-icon>
                  <span>Submission History</span>
                </div>
                <el-button
                  :icon="Refresh"
                  circle
                  size="small"
                  @click="loadSubmissions"
                  :loading="loading"
                />
              </div>
            </template>
            
            <div v-if="loading" class="loading-section">
              <el-skeleton :rows="5" animated />
            </div>
            
            <div v-else-if="submissions.length === 0" class="empty-section">
              <el-empty description="No submissions yet">
                <el-button type="primary" @click="router.push('/submit')">
                  Submit Now
                </el-button>
              </el-empty>
            </div>
            
            <div v-else>
              <!-- 得分趋势图 -->
              <div class="score-chart" v-if="chartData.length > 0">
                <h3>Score Trend</h3>
                <div class="chart-container">
                  <div
                    v-for="(item, index) in chartData"
                    :key="index"
                    class="chart-bar"
                    :style="{ height: (item.score * 100) + '%' }"
                    :title="`${item.date}: ${item.score.toFixed(4)}`"
                  >
                    <div class="bar-fill"></div>
                  </div>
                </div>
              </div>
              
              <!-- Submission list -->
              <div class="submissions-list">
                <el-timeline>
                  <el-timeline-item
                    v-for="submission in submissions"
                    :key="submission.id"
                    :timestamp="formatDateTime(submission.submitted_at)"
                    placement="top"
                    :color="getStatusColor(submission.status)"
                  >
                    <el-card>
                      <div class="submission-item">
                        <div class="submission-header">
                          <div class="submission-title">
                            <el-icon v-if="submission.status === 'success'"><SuccessFilled /></el-icon>
                            <el-icon v-else-if="submission.status === 'error'"><CircleCloseFilled /></el-icon>
                            <el-icon v-else><Loading /></el-icon>
                            <span>{{ submission.filename }}</span>
                          </div>
                          <el-tag
                            v-if="submission.final_score === myStats.bestScore && submission.status === 'success'"
                            type="success"
                            effect="dark"
                          >
                            Best
                          </el-tag>
                        </div>
                        
                        <div v-if="submission.status === 'success'" class="submission-metrics">
                          <div class="metric">
                            <span class="metric-label">Score:</span>
                            <span class="metric-value">{{ submission.final_score.toFixed(4) }}</span>
                          </div>
                          <div class="metric">
                            <span class="metric-label">Accuracy:</span>
                            <span class="metric-value">{{ submission.accuracy.toFixed(4) }}</span>
                          </div>
                          <div class="metric">
                            <span class="metric-label">F1:</span>
                            <span class="metric-value">{{ submission.f1_score.toFixed(4) }}</span>
                          </div>
                        </div>
                        
                        <div v-else-if="submission.status === 'error'" class="submission-error">
                          <el-alert
                            type="error"
                            :description="submission.error_message"
                            :closable="false"
                          />
                        </div>
                        
                        <div v-else class="submission-pending">
                          <el-tag type="info">Processing...</el-tag>
                        </div>
                      </div>
                    </el-card>
                  </el-timeline-item>
                </el-timeline>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </Layout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import { submissionAPI, leaderboardAPI } from '../api'
import { ElMessage } from 'element-plus'
import {
  DataAnalysis, Document, Refresh,
  SuccessFilled, CircleCloseFilled, Loading
} from '@element-plus/icons-vue'
import Layout from '../components/Layout.vue'

const router = useRouter()
const userStore = useUserStore()
const loading = ref(false)
const submissions = ref([])
const leaderboard = ref([])

const myStats = computed(() => {
  const totalSubmissions = submissions.value.length
  const successSubmissions = submissions.value.filter(s => s.status === 'success').length
  const scores = submissions.value
    .filter(s => s.status === 'success' && s.final_score !== null)
    .map(s => s.final_score)
  const bestScore = scores.length > 0 ? Math.max(...scores) : null
  
  // 查找排名
  let rank = null
  if (bestScore !== null) {
    const myEntry = leaderboard.value.find(entry => entry.user_id === userStore.user?.id)
    if (myEntry) {
      rank = myEntry.rank
    }
  }
  
  return {
    totalSubmissions,
    successSubmissions,
    bestScore,
    rank
  }
})

const chartData = computed(() => {
  return submissions.value
    .filter(s => s.status === 'success' && s.final_score !== null)
    .slice(0, 20)
    .reverse()
    .map(s => ({
      date: formatDate(s.submitted_at),
      score: s.final_score
    }))
})

const loadSubmissions = async () => {
  loading.value = true
  try {
    submissions.value = await submissionAPI.getMySubmissions(50)
  } catch (error) {
    ElMessage.error('Failed to load submission history')
    console.error('Failed to load submissions:', error)
  } finally {
    loading.value = false
  }
}

const loadLeaderboard = async () => {
  try {
    leaderboard.value = await leaderboardAPI.getLeaderboard()
  } catch (error) {
    console.error('Failed to load leaderboard:', error)
  }
}

const getStatusColor = (status) => {
  if (status === 'success') return '#67c23a'
  if (status === 'error') return '#f56c6c'
  return '#909399'
}

const formatDate = (dateStr) => {
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN')
}

const formatDateTime = (dateStr) => {
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

onMounted(() => {
  loadSubmissions()
  loadLeaderboard()
})
</script>

<style scoped>
.profile-page {
  max-width: 1200px;
  margin: 0 auto;
}

.user-card {
  margin-bottom: 20px;
}

.user-info {
  text-align: center;
  padding: 20px 0;
}

.user-info h2 {
  margin: 16px 0 8px;
  font-size: 24px;
  color: #303133;
}

.email {
  color: #909399;
  font-size: 14px;
  margin-bottom: 8px;
}

.join-date {
  color: #909399;
  font-size: 13px;
}

.stats-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: bold;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 0;
  border-bottom: 1px solid #f0f0f0;
}

.stat-item:last-child {
  border-bottom: none;
}

.stat-label {
  color: #606266;
  font-size: 14px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #409eff;
}

.stat-value.success {
  color: #67c23a;
}

.stat-value.best {
  color: #e6a23c;
}

.stat-value.rank {
  color: #f56c6c;
}

.history-card {
  margin-bottom: 20px;
}

.loading-section,
.empty-section {
  padding: 40px 0;
  text-align: center;
}

.score-chart {
  margin-bottom: 30px;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
}

.score-chart h3 {
  margin: 0 0 16px;
  font-size: 16px;
  color: #303133;
}

.chart-container {
  display: flex;
  align-items: flex-end;
  gap: 4px;
  height: 120px;
  padding: 10px 0;
}

.chart-bar {
  flex: 1;
  min-height: 20px;
  position: relative;
  cursor: pointer;
}

.bar-fill {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 100%;
  background: linear-gradient(to top, #409eff, #66b1ff);
  border-radius: 4px 4px 0 0;
  transition: all 0.3s;
}

.chart-bar:hover .bar-fill {
  background: linear-gradient(to top, #66b1ff, #a0cfff);
}

.submissions-list {
  margin-top: 20px;
}

.submission-item {
  padding: 8px 0;
}

.submission-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.submission-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
  color: #303133;
}

.submission-metrics {
  display: flex;
  gap: 24px;
  flex-wrap: wrap;
}

.metric {
  display: flex;
  gap: 6px;
  font-size: 14px;
}

.metric-label {
  color: #909399;
}

.metric-value {
  font-weight: bold;
  color: #409eff;
}

.submission-error {
  margin-top: 8px;
}

.submission-pending {
  margin-top: 8px;
}
</style>

