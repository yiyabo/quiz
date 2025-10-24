<template>
  <Layout>
    <div class="submit-page">
      <el-card class="submit-card">
        <template #header>
          <div class="card-header">
            <div>
              <el-icon :size="24"><Upload /></el-icon>
              <span class="title">Submit Predictions</span>
            </div>
            <el-tag v-if="currentCompetition" type="primary" size="large">
              {{ currentCompetition.title }}
            </el-tag>
          </div>
        </template>
        
        <el-alert
          title="Submission Instructions"
          type="info"
          :closable="false"
          style="margin-bottom: 24px"
        >
          <ul class="submit-instructions">
            <li>Please upload prediction results in CSV format</li>
            <li>
              File must contain the following columns:
              <span class="columns">
                <template v-for="(col, index) in submissionGuide.columns" :key="col">
                  <code>{{ col }}</code><span v-if="index < submissionGuide.columns.length - 1">, </span>
                </template>
              </span>
            </li>
            <li><code>{{ submissionGuide.predictionColumn }}</code> column values must be 0 or 1</li>
            <li>Must include all {{ submissionGuide.sampleCount }} test samples</li>
            <li>{{ submissionGuide.sampleHint }}</li>
          </ul>
        </el-alert>
        
        <div class="upload-section">
          <el-upload
            ref="uploadRef"
            :auto-upload="false"
            :limit="1"
            :on-change="handleFileChange"
            :on-exceed="handleExceed"
            :on-remove="handleRemove"
            accept=".csv"
            drag
          >
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="el-upload__text">
              Drop CSV file here or <em>click to upload</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                Only CSV files are allowed
              </div>
            </template>
          </el-upload>
        </div>
        
        <div class="submit-actions">
          <el-button
            type="primary"
            size="large"
            :loading="submitting"
            :disabled="!selectedFile"
            @click="handleSubmit"
          >
            <el-icon><Check /></el-icon>
            Submit for Scoring
          </el-button>
          <el-button size="large" @click="resetForm">
            <el-icon><Refresh /></el-icon>
            Reset
          </el-button>
        </div>
      </el-card>
      
      <!-- 最近提交 -->
      <el-card class="recent-submissions" v-if="recentSubmissions.length > 0">
        <template #header>
          <div class="card-header">
            <span class="title">Recent Submissions</span>
          </div>
        </template>
        
        <el-table :data="recentSubmissions" style="width: 100%">
          <el-table-column prop="submitted_at" label="Submitted At" width="180">
            <template #default="scope">
              {{ formatDateTime(scope.row.submitted_at) }}
            </template>
          </el-table-column>
          
          <el-table-column prop="filename" label="Filename" min-width="200" />
          
          <el-table-column prop="status" label="Status" width="100">
            <template #default="scope">
              <el-tag v-if="scope.row.status === 'success'" type="success">Success</el-tag>
              <el-tag v-else-if="scope.row.status === 'error'" type="danger">Failed</el-tag>
              <el-tag v-else type="info">Processing</el-tag>
            </template>
          </el-table-column>
          
          <el-table-column prop="final_score" label="Score" width="120">
            <template #default="scope">
              <span v-if="scope.row.final_score !== null" class="score">
                {{ scope.row.final_score.toFixed(4) }}
              </span>
              <span v-else>-</span>
            </template>
          </el-table-column>
          
          <el-table-column label="Actions" width="120">
            <template #default="scope">
              <el-button
                type="primary"
                link
                @click="viewDetail(scope.row)"
              >
                View Details
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
      
      <!-- 详情对话框 -->
      <el-dialog
        v-model="detailDialogVisible"
        title="Submission Details"
        width="600px"
      >
        <div v-if="selectedSubmission" class="submission-detail">
          <el-descriptions :column="1" border>
            <el-descriptions-item label="Filename">
              {{ selectedSubmission.filename }}
            </el-descriptions-item>
            <el-descriptions-item label="Submitted At">
              {{ formatDateTime(selectedSubmission.submitted_at) }}
            </el-descriptions-item>
            <el-descriptions-item label="Status">
              <el-tag v-if="selectedSubmission.status === 'success'" type="success">Success</el-tag>
              <el-tag v-else-if="selectedSubmission.status === 'error'" type="danger">Failed</el-tag>
              <el-tag v-else type="info">Processing</el-tag>
            </el-descriptions-item>
          </el-descriptions>
          
          <div v-if="selectedSubmission.status === 'success'" class="metrics">
            <h3>Scoring Metrics</h3>
            <el-row :gutter="16">
              <el-col :span="12">
                <div class="metric-item">
                  <div class="metric-label">Accuracy</div>
                  <div class="metric-value">{{ selectedSubmission.accuracy?.toFixed(4) }}</div>
                </div>
              </el-col>
              <el-col :span="12">
                <div class="metric-item">
                  <div class="metric-label">Precision</div>
                  <div class="metric-value">{{ selectedSubmission.precision?.toFixed(4) }}</div>
                </div>
              </el-col>
              <el-col :span="12">
                <div class="metric-item">
                  <div class="metric-label">Recall</div>
                  <div class="metric-value">{{ selectedSubmission.recall?.toFixed(4) }}</div>
                </div>
              </el-col>
              <el-col :span="12">
                <div class="metric-item">
                  <div class="metric-label">F1-Score</div>
                  <div class="metric-value">{{ selectedSubmission.f1_score?.toFixed(4) }}</div>
                </div>
              </el-col>
            </el-row>
            
            <div class="final-score">
              <div class="final-score-label">Final Score</div>
              <div class="final-score-value">{{ selectedSubmission.final_score?.toFixed(4) }}</div>
            </div>
            
            <h3>Confusion Matrix</h3>
            <el-table :data="confusionMatrixData" border style="width: 100%">
              <el-table-column prop="label" label="" width="150" />
              <el-table-column prop="tp" label="Predicted Positive" align="center" />
              <el-table-column prop="fp" label="Predicted Negative" align="center" />
            </el-table>
          </div>
          
          <div v-else-if="selectedSubmission.status === 'error'" class="error-message">
            <el-alert
              title="Scoring Failed"
              type="error"
              :description="selectedSubmission.error_message"
              :closable="false"
            />
          </div>
        </div>
      </el-dialog>
    </div>
  </Layout>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useCompetitionStore } from '../stores/competition'
import { submissionAPI } from '../api'
import { ElMessage } from 'element-plus'
import { UploadFilled, Upload, Check, Refresh } from '@element-plus/icons-vue'
import Layout from '../components/Layout.vue'

const router = useRouter()
const competitionStore = useCompetitionStore()
const uploadRef = ref()
const selectedFile = ref(null)
const submitting = ref(false)
const recentSubmissions = ref([])
const detailDialogVisible = ref(false)
const selectedSubmission = ref(null)

const confusionMatrixData = computed(() => {
  if (!selectedSubmission.value) return []
  return [
    {
      label: 'Actual Positive',
      tp: selectedSubmission.value.tp,
      fp: selectedSubmission.value.fn
    },
    {
      label: 'Actual Negative',
      tp: selectedSubmission.value.fp,
      fp: selectedSubmission.value.tn
    }
  ]
})

const handleFileChange = (file) => {
  selectedFile.value = file.raw
}

const handleExceed = () => {
  ElMessage.warning('Only one file can be uploaded at a time')
}

const handleRemove = () => {
  selectedFile.value = null
}

const resetForm = () => {
  uploadRef.value.clearFiles()
  selectedFile.value = null
}

const handleSubmit = async () => {
  if (!selectedFile.value) {
    ElMessage.warning('Please select a file first')
    return
  }
  
  if (!competitionStore.selectedCompetitionId) {
    ElMessage.warning('Please select a competition first')
    return
  }
  
  submitting.value = true
  
  try {
    const result = await submissionAPI.submit(competitionStore.selectedCompetitionId, selectedFile.value)
    
    if (result.status === 'success') {
      ElMessage.success('Submission successful! Scoring completed')
      resetForm()
      loadRecentSubmissions()
      
      // 显示详情
      selectedSubmission.value = result
      detailDialogVisible.value = true
    } else {
      ElMessage.error(result.error_message || 'Submission failed')
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || 'Submission failed, please try again')
  } finally {
    submitting.value = false
  }
}

const loadRecentSubmissions = async () => {
  try {
    recentSubmissions.value = await submissionAPI.getMySubmissions(10)
  } catch (error) {
    console.error('Failed to load submissions:', error)
  }
}

const viewDetail = (submission) => {
  selectedSubmission.value = submission
  detailDialogVisible.value = true
}

const formatDateTime = (dateStr) => {
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

onMounted(() => {
  competitionStore.loadCompetitions()
  loadRecentSubmissions()
})

const currentCompetition = computed(() => competitionStore.selectedCompetition)

const submissionGuideMap = {
  ppi: {
    columns: ['protein_A', 'protein_B', 'prediction'],
    predictionColumn: 'prediction',
    sampleCount: 1525,
    sampleHint: 'Refer to kaggle_dataset/sample_submission.csv for format'
  },
  cci: {
    columns: ['source', 'target', 'label'],
    predictionColumn: 'label',
    sampleCount: 4000,
    sampleHint: 'Keep test_edges.csv column order, fill label column with predictions'
  }
}

const defaultSubmissionGuide = {
  columns: ['id', 'feature_1', 'prediction'],
  predictionColumn: 'prediction',
  sampleCount: 'All test samples',
  sampleHint: 'Prepare submission file according to competition instructions'
}

const submissionGuide = computed(() => {
  const name = currentCompetition.value?.name
  return submissionGuideMap[name] || defaultSubmissionGuide
})
</script>

<style scoped>
.submit-page {
  max-width: 900px;
  margin: 0 auto;
}

.submit-card {
  margin-bottom: 24px;
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

.submit-instructions {
  margin-left: 20px;
  line-height: 1.8;
}

.submit-instructions code {
  background: #f5f7fa;
  padding: 2px 6px;
  border-radius: 3px;
  color: #e6a23c;
  font-family: monospace;
}

.upload-section {
  margin: 24px 0;
}

.submit-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
  margin-top: 24px;
}

.recent-submissions {
  margin-bottom: 24px;
}

.score {
  font-weight: bold;
  color: #67c23a;
}

.submission-detail {
  padding: 16px 0;
}

.metrics {
  margin-top: 24px;
}

.metrics h3 {
  margin: 20px 0 12px;
  font-size: 16px;
  color: #303133;
}

.metric-item {
  background: #f5f7fa;
  padding: 16px;
  border-radius: 8px;
  text-align: center;
  margin-bottom: 16px;
}

.metric-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 8px;
}

.metric-value {
  font-size: 24px;
  font-weight: bold;
  color: #409eff;
}

.final-score {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 24px;
  border-radius: 12px;
  text-align: center;
  color: white;
  margin: 24px 0;
}

.final-score-label {
  font-size: 16px;
  margin-bottom: 8px;
  opacity: 0.9;
}

.final-score-value {
  font-size: 48px;
  font-weight: bold;
}

.error-message {
  margin-top: 16px;
}
</style>
