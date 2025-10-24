<template>
  <div class="layout">
    <el-container>
      <!-- 顶部导航栏 -->
      <el-header class="header">
        <div class="header-content">
          <div class="logo">
            <el-icon :size="28"><Trophy /></el-icon>
            <span class="title">Bioinformatics Competition</span>
          </div>
          
          <div class="nav-section">
            <!-- 竞赛选择器 -->
            <el-select
              v-model="competitionStore.selectedCompetitionId"
              placeholder="Select Competition"
              class="competition-selector"
              @change="handleCompetitionChange"
            >
              <el-option
                v-for="comp in competitionStore.competitions"
                :key="comp.id"
                :label="comp.title"
                :value="comp.id"
              >
                <span style="float: left">{{ comp.title }}</span>
                <span style="float: right; color: #8492a6; font-size: 13px">ID: {{ comp.id }}</span>
              </el-option>
            </el-select>
            
            <el-menu
              mode="horizontal"
              :default-active="currentRoute"
              class="nav-menu"
              @select="handleMenuSelect"
            >
              <el-menu-item index="/home">
                <el-icon><HomeFilled /></el-icon>
                <span>Home</span>
              </el-menu-item>
              <el-menu-item index="/leaderboard">
                <el-icon><TrophyBase /></el-icon>
                <span>Leaderboard</span>
              </el-menu-item>
              <el-menu-item index="/submit" v-if="userStore.isLoggedIn">
                <el-icon><Upload /></el-icon>
                <span>Submit</span>
              </el-menu-item>
              <el-menu-item index="/profile" v-if="userStore.isLoggedIn">
                <el-icon><User /></el-icon>
                <span>Profile</span>
              </el-menu-item>
            </el-menu>
          </div>
          
          <div class="user-section">
            <template v-if="userStore.isLoggedIn">
              <el-dropdown @command="handleCommand">
                <span class="user-info">
                  <el-avatar :size="32">{{ userStore.user?.username?.charAt(0).toUpperCase() }}</el-avatar>
                  <span class="username">{{ userStore.user?.username }}</span>
                  <el-icon><ArrowDown /></el-icon>
                </span>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="profile">
                      <el-icon><User /></el-icon>
                      Profile
                    </el-dropdown-item>
                    <el-dropdown-item command="logout" divided>
                      <el-icon><SwitchButton /></el-icon>
                      Logout
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </template>
            <template v-else>
              <el-button @click="router.push('/login')">Login</el-button>
              <el-button type="primary" @click="router.push('/register')">Sign Up</el-button>
            </template>
          </div>
        </div>
      </el-header>
      
      <!-- 主内容区 -->
      <el-main class="main-content">
        <slot></slot>
      </el-main>
      
      <!-- 页脚 -->
      <el-footer class="footer">
        <div class="footer-content">
          <p>© 2024 Bioinformatics Competition Platform</p>
          <p class="footer-links">
            <a href="https://github.com" target="_blank">GitHub</a>
            <span class="separator">|</span>
            <a href="#" @click.prevent>Documentation</a>
            <span class="separator">|</span>
            <a href="#" @click.prevent>Contact Us</a>
          </p>
        </div>
      </el-footer>
    </el-container>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '../stores/user'
import { useCompetitionStore } from '../stores/competition'
import { ElMessage } from 'element-plus'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const competitionStore = useCompetitionStore()

onMounted(() => {
  competitionStore.loadCompetitions()
})

const currentRoute = computed(() => route.path)

const handleMenuSelect = (index) => {
  router.push(index)
}

const handleCompetitionChange = () => {
  ElMessage.success(`Switched to: ${competitionStore.selectedCompetition?.title}`)
  // 如果在排行榜页面，刷新排行榜
  if (route.path === '/leaderboard') {
    window.location.reload()
  }
}

const handleCommand = (command) => {
  if (command === 'logout') {
    userStore.logout()
    ElMessage.success('Logged out successfully')
    router.push('/home')
  } else if (command === 'profile') {
    router.push('/profile')
  }
}
</script>

<style scoped>
.layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  background: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 0;
  height: 60px;
}

.header-content {
  max-width: 1400px;
  margin: 0 auto;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #409eff;
  font-weight: bold;
  font-size: 18px;
  cursor: pointer;
}

.nav-section {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 20px;
  margin: 0 20px;
}

.competition-selector {
  width: 200px;
}

.nav-menu {
  flex: 1;
  border: none;
}

.user-section {
  display: flex;
  align-items: center;
  gap: 10px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 5px 10px;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.user-info:hover {
  background-color: #f5f7fa;
}

.username {
  font-size: 14px;
  color: #606266;
}

.main-content {
  flex: 1;
  padding: 20px;
  max-width: 1400px;
  width: 100%;
  margin: 0 auto;
}

.footer {
  background: white;
  border-top: 1px solid #e4e7ed;
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.footer-content {
  text-align: center;
  color: #909399;
  font-size: 14px;
}

.footer-links {
  margin-top: 8px;
}

.footer-links a {
  color: #409eff;
  text-decoration: none;
  transition: color 0.3s;
}

.footer-links a:hover {
  color: #66b1ff;
}

.separator {
  margin: 0 10px;
  color: #dcdfe6;
}
</style>
