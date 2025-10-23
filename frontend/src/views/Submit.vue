<template>
  <Layout>
    <div class="submit-page">
      <el-card class="submit-card">
        <template #header>
          <div class="card-header">
            <div>
              <el-icon :size="24"><Upload /></el-icon>
              <span class="title">提交预测结果</span>
            </div>
            <el-tag v-if="currentCompetition" type="primary" size="large">
              {{ currentCompetition.title }}
            </el-tag>
          </div>
        </template>
        
        <el-alert
          title="提交说明"
          type="info"
          :closable="false"
          style="margin-bottom: 24px"
        >
          <ul class="submit-instructions">
            <li>请上传 CSV 格式的预测结果文件</li>
            <li>
              文件必须包含以下列：
              <span class="columns">
                <template v-for="(col, index) in submissionGuide.columns" :key="col">
                  <code>{{ col }}</code><span v-if="index < submissionGuide.columns.length - 1">, </span>
                </template>
              </span>
            </li>
            <li><code>{{ submissionGuide.predictionColumn }}</code> 列的值必须是 0 或 1</li>
            <li>必须包含测试集的所有 {{ submissionGuide.sampleCount }} 个样本</li>
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
              将CSV文件拖到此处，或<em>点击上传</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                只能上传CSV文件
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
            提交评分
          </el-button>
          <el-button size="large" @click="resetForm">
            <el-icon><Refresh /></el-icon>
            重置
          </el-button>
        </div>
      </el-card>
      
      <!-- 最近提交 -->
      <el-card class="recent-submissions" v-if="recentSubmissions.length > 0">
        <template #header>
          <div class="card-header">
            <span class="title">最近提交</span>
          </div>
        </template>
        
        <el-table :data="recentSubmissions" style="width: 100%">
          <el-table-column prop="submitted_at" label="提交时间" width="180">
            <template #default="scope">
              {{ formatDateTime(scope.row.submitted_at) }}
            </template>
          </el-table-column>
          
          <el-table-column prop="filename" label="文件名" min-width="200" />
          
          <el-table-column prop="status" label="状态" width="100">
            <template #default="scope">
              <el-tag v-if="scope.row.status === 'success'" type="success">成功</el-tag>
              <el-tag v-else-if="scope.row.status === 'error'" type="danger">失败</el-tag>
              <el-tag v-else type="info">处理中</el-tag>
            </template>
          </el-table-column>
          
          <el-table-column prop="final_score" label="得分" width="120">
            <template #default="scope">
              <span v-if="scope.row.final_score !== null" class="score">
                {{ scope.row.final_score.toFixed(4) }}
              </span>
              <span v-else>-</span>
            </template>
          </el-table-column>
          
          <el-table-column label="操作" width="120">
            <template #default="scope">
              <el-button
                type="primary"
                link
                @click="viewDetail(scope.row)"
              >
                查看详情
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
      
      <!-- 详情对话框 -->
      <el-dialog
        v-model="detailDialogVisible"
        title="提交详情"
        width="600px"
      >
        <div v-if="selectedSubmission" class="submission-detail">
          <el-descriptions :column="1" border>
            <el-descriptions-item label="文件名">
              {{ selectedSubmission.filename }}
            </el-descriptions-item>
            <el-descriptions-item label="提交时间">
              {{ formatDateTime(selectedSubmission.submitted_at) }}
            </el-descriptions-item>
            <el-descriptions-item label="状态">
              <el-tag v-if="selectedSubmission.status === 'success'" type="success">成功</el-tag>
              <el-tag v-else-if="selectedSubmission.status === 'error'" type="danger">失败</el-tag>
              <el-tag v-else type="info">处理中</el-tag>
            </el-descriptions-item>
          </el-descriptions>
          
          <div v-if="selectedSubmission.status === 'success'" class="metrics">
            <h3>评分指标</h3>
            <el-row :gutter="16">
              <el-col :span="12">
                <div class="metric-item">
                  <div class="metric-label">准确率 (Accuracy)</div>
                  <div class="metric-value">{{ selectedSubmission.accuracy?.toFixed(4) }}</div>
                </div>
              </el-col>
              <el-col :span="12">
                <div class="metric-item">
                  <div class="metric-label">精确率 (Precision)</div>
                  <div class="metric-value">{{ selectedSubmission.precision?.toFixed(4) }}</div>
                </div>
              </el-col>
              <el-col :span="12">
                <div class="metric-item">
                  <div class="metric-label">召回率 (Recall)</div>
                  <div class="metric-value">{{ selectedSubmission.recall?.toFixed(4) }}</div>
                </div>
              </el-col>
              <el-col :span="12">
                <div class="metric-item">
                  <div class="metric-label">F1分数 (F1-Score)</div>
                  <div class="metric-value">{{ selectedSubmission.f1_score?.toFixed(4) }}</div>
                </div>
              </el-col>
            </el-row>
            
            <div class="final-score">
              <div class="final-score-label">最终得分</div>
              <div class="final-score-value">{{ selectedSubmission.final_score?.toFixed(4) }}</div>
            </div>
            
            <h3>混淆矩阵</h3>
            <el-table :data="confusionMatrixData" border style="width: 100%">
              <el-table-column prop="label" label="" width="150" />
              <el-table-column prop="tp" label="预测为正" align="center" />
              <el-table-column prop="fp" label="预测为负" align="center" />
            </el-table>
          </div>
          
          <div v-else-if="selectedSubmission.status === 'error'" class="error-message">
            <el-alert
              title="评分失败"
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
      label: '实际为正',
      tp: selectedSubmission.value.tp,
      fp: selectedSubmission.value.fn
    },
    {
      label: '实际为负',
      tp: selectedSubmission.value.fp,
      fp: selectedSubmission.value.tn
    }
  ]
})

const handleFileChange = (file) => {
  selectedFile.value = file.raw
}

const handleExceed = () => {
  ElMessage.warning('一次只能上传一个文件')
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
    ElMessage.warning('请先选择文件')
    return
  }
  
  if (!competitionStore.selectedCompetitionId) {
    ElMessage.warning('请先选择竞赛')
    return
  }
  
  submitting.value = true
  
  try {
    const result = await submissionAPI.submit(competitionStore.selectedCompetitionId, selectedFile.value)
    
    if (result.status === 'success') {
      ElMessage.success('提交成功！评分已完成')
      resetForm()
      loadRecentSubmissions()
      
      // 显示详情
      selectedSubmission.value = result
      detailDialogVisible.value = true
    } else {
      ElMessage.error(result.error_message || '提交失败')
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '提交失败，请稍后重试')
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
    sampleHint: '参考 kaggle_dataset/sample_submission.csv 文件格式'
  },
  cci: {
    columns: ['source', 'target', 'label'],
    predictionColumn: 'label',
    sampleCount: 4000,
    sampleHint: '请保持 test_edges.csv 的列顺序，label 列填写预测结果'
  }
}

const defaultSubmissionGuide = {
  columns: ['id', 'feature_1', 'prediction'],
  predictionColumn: 'prediction',
  sampleCount: '全部测试样本',
  sampleHint: '请按照竞赛说明准备提交文件'
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
