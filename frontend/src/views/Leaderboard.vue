<template>
  <Layout>
    <div class="leaderboard-page">
      <el-card>
        <template #header>
          <div class="card-header">
            <div style="display: flex; align-items: center; gap: 12px">
              <el-icon :size="24"><TrophyBase /></el-icon>
              <span class="title">Leaderboard</span>
              <el-tag v-if="currentCompetition" type="primary" size="large">
                {{ currentCompetition.title }}
              </el-tag>
            </div>
            <el-button
              :icon="Refresh"
              circle
              @click="loadLeaderboard"
              :loading="loading"
            />
          </div>
        </template>
        
        <div v-if="loading && leaderboard.length === 0" class="loading-section">
          <el-skeleton :rows="10" animated />
        </div>
        
        <div v-else-if="leaderboard.length === 0" class="empty-section">
          <el-empty description="No data yet">
            <el-button type="primary" @click="router.push('/submit')">
              Submit Now
            </el-button>
          </el-empty>
        </div>
        
        <div v-else class="leaderboard-content">
          <!-- 前三名特殊展示 -->
          <div class="top-three" v-if="leaderboard.length > 0">
            <el-row :gutter="20">
              <!-- 第二名 -->
              <el-col :xs="24" :sm="8" v-if="leaderboard.length >= 2">
                <div class="podium-card rank-2">
                  <div class="medal">🥈</div>
                  <div class="rank-number">2</div>
                  <el-avatar :size="80">{{ leaderboard[1].username.charAt(0).toUpperCase() }}</el-avatar>
                  <div class="username">{{ leaderboard[1].username }}</div>
                  <div class="score">{{ leaderboard[1].best_score.toFixed(4) }}</div>
                  <div class="stats">
                    <span>F1: {{ leaderboard[1].best_f1_score.toFixed(4) }}</span>
                    <span>Submissions: {{ leaderboard[1].submission_count }}</span>
                  </div>
                </div>
              </el-col>
              
              <!-- 第一名 -->
              <el-col :xs="24" :sm="8" v-if="leaderboard.length >= 1">
                <div class="podium-card rank-1">
                  <div class="medal">🥇</div>
                  <div class="rank-number">1</div>
                  <el-avatar :size="100">{{ leaderboard[0].username.charAt(0).toUpperCase() }}</el-avatar>
                  <div class="username">{{ leaderboard[0].username }}</div>
                  <div class="score champion">{{ leaderboard[0].best_score.toFixed(4) }}</div>
                  <div class="stats">
                    <span>F1: {{ leaderboard[0].best_f1_score.toFixed(4) }}</span>
                    <span>Submissions: {{ leaderboard[0].submission_count }}</span>
                  </div>
                </div>
              </el-col>
              
              <!-- 第三名 -->
              <el-col :xs="24" :sm="8" v-if="leaderboard.length >= 3">
                <div class="podium-card rank-3">
                  <div class="medal">🥉</div>
                  <div class="rank-number">3</div>
                  <el-avatar :size="70">{{ leaderboard[2].username.charAt(0).toUpperCase() }}</el-avatar>
                  <div class="username">{{ leaderboard[2].username }}</div>
                  <div class="score">{{ leaderboard[2].best_score.toFixed(4) }}</div>
                  <div class="stats">
                    <span>F1: {{ leaderboard[2].best_f1_score.toFixed(4) }}</span>
                    <span>Submissions: {{ leaderboard[2].submission_count }}</span>
                  </div>
                </div>
              </el-col>
            </el-row>
          </div>
          
          <!-- 完整排行榜表格 -->
          <div class="leaderboard-table">
            <el-table
              :data="leaderboard"
              stripe
              :row-class-name="getRowClassName"
            >
              <el-table-column prop="rank" label="Rank" width="80" align="center">
                <template #default="scope">
                  <span :class="getRankClass(scope.row.rank)">
                    {{ scope.row.rank }}
                  </span>
                </template>
              </el-table-column>
              
              <el-table-column prop="username" label="Username" min-width="150">
                <template #default="scope">
                  <div class="user-cell">
                    <el-avatar :size="32">{{ scope.row.username.charAt(0).toUpperCase() }}</el-avatar>
                    <span>{{ scope.row.username }}</span>
                    <el-tag v-if="isCurrentUser(scope.row.user_id)" type="success" size="small">You</el-tag>
                  </div>
                </template>
              </el-table-column>
              
              <el-table-column prop="best_score" label="Best Score" width="140" align="center" sortable>
                <template #default="scope">
                  <span class="score-cell">{{ scope.row.best_score.toFixed(4) }}</span>
                </template>
              </el-table-column>
              
              <el-table-column prop="best_accuracy" label="Accuracy" width="120" align="center">
                <template #default="scope">
                  {{ scope.row.best_accuracy.toFixed(4) }}
                </template>
              </el-table-column>
              
              <el-table-column prop="best_f1_score" label="F1 Score" width="120" align="center">
                <template #default="scope">
                  {{ scope.row.best_f1_score.toFixed(4) }}
                </template>
              </el-table-column>
              
              <el-table-column prop="submission_count" label="Submissions" width="120" align="center" />
              
              <el-table-column prop="last_submission" label="Last Submission" width="180">
                <template #default="scope">
                  {{ formatDateTime(scope.row.last_submission) }}
                </template>
              </el-table-column>
            </el-table>
          </div>
        </div>
      </el-card>
    </div>
  </Layout>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import { useCompetitionStore } from '../stores/competition'
import { leaderboardAPI } from '../api'
import { ElMessage } from 'element-plus'
import { TrophyBase, Refresh } from '@element-plus/icons-vue'
import Layout from '../components/Layout.vue'

const router = useRouter()
const userStore = useUserStore()
const competitionStore = useCompetitionStore()
const loading = ref(false)
const leaderboard = ref([])

const currentCompetition = computed(() => competitionStore.selectedCompetition)

const loadLeaderboard = async () => {
  loading.value = true
  try {
    leaderboard.value = await leaderboardAPI.getLeaderboard(competitionStore.selectedCompetitionId)
  } catch (error) {
    ElMessage.error('Failed to load leaderboard')
    console.error('Failed to load leaderboard:', error)
  } finally {
    loading.value = false
  }
}

// 监听竞赛切换
watch(() => competitionStore.selectedCompetitionId, () => {
  loadLeaderboard()
})

const isCurrentUser = (userId) => {
  return userStore.user?.id === userId
}

const getRankClass = (rank) => {
  if (rank === 1) return 'rank-gold'
  if (rank === 2) return 'rank-silver'
  if (rank === 3) return 'rank-bronze'
  return ''
}

const getRowClassName = ({ row }) => {
  if (isCurrentUser(row.user_id)) return 'current-user-row'
  return ''
}

const formatDateTime = (dateStr) => {
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

onMounted(() => {
  competitionStore.loadCompetitions()
  loadLeaderboard()
})
</script>

<style scoped>
.leaderboard-page {
  max-width: 1200px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.card-header > div {
  display: flex;
  align-items: center;
  gap: 8px;
}

.title {
  font-size: 18px;
  font-weight: bold;
}

.loading-section,
.empty-section {
  padding: 40px 0;
}

.top-three {
  padding: 20px 0 40px;
  background: linear-gradient(to bottom, #f5f7fa 0%, white 100%);
  margin: -20px -20px 30px;
  padding: 40px 20px;
}

.podium-card {
  background: white;
  border-radius: 16px;
  padding: 30px 20px;
  text-align: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  position: relative;
  transition: transform 0.3s;
  margin-bottom: 20px;
}

.podium-card:hover {
  transform: translateY(-5px);
}

.rank-1 {
  border: 3px solid #ffd700;
  order: 2;
}

.rank-2 {
  border: 3px solid #c0c0c0;
  order: 1;
  margin-top: 30px;
}

.rank-3 {
  border: 3px solid #cd7f32;
  order: 3;
  margin-top: 30px;
}

@media (min-width: 768px) {
  .podium-card {
    margin-bottom: 0;
  }
}

.medal {
  font-size: 48px;
  margin-bottom: 8px;
}

.rank-number {
  position: absolute;
  top: 12px;
  right: 12px;
  background: #409eff;
  color: white;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
}

.rank-1 .rank-number {
  background: #ffd700;
  color: #333;
}

.rank-2 .rank-number {
  background: #c0c0c0;
  color: #333;
}

.rank-3 .rank-number {
  background: #cd7f32;
  color: white;
}

.username {
  font-size: 18px;
  font-weight: bold;
  margin: 16px 0 8px;
  color: #303133;
}

.score {
  font-size: 32px;
  font-weight: bold;
  color: #409eff;
  margin: 8px 0;
}

.score.champion {
  font-size: 40px;
  background: linear-gradient(135deg, #ffd700 0%, #ff8c00 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.stats {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-top: 12px;
  font-size: 14px;
  color: #909399;
}

.leaderboard-table {
  margin-top: 20px;
}

.user-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}

.score-cell {
  font-weight: bold;
  color: #67c23a;
  font-size: 16px;
}

.rank-gold {
  color: #ffd700;
  font-weight: bold;
  font-size: 18px;
}

.rank-silver {
  color: #c0c0c0;
  font-weight: bold;
  font-size: 18px;
}

.rank-bronze {
  color: #cd7f32;
  font-weight: bold;
  font-size: 18px;
}

:deep(.current-user-row) {
  background-color: #ecf5ff !important;
}
</style>

