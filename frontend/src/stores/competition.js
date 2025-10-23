import { defineStore } from 'pinia'
import { competitionAPI } from '../api'

export const useCompetitionStore = defineStore('competition', {
  state: () => ({
    competitions: [],
    selectedCompetitionId: 1, // 默认选择第一个竞赛(PPI)
    loading: false
  }),

  getters: {
    selectedCompetition: (state) => {
      return state.competitions.find(c => c.id === state.selectedCompetitionId) || null
    }
  },

  actions: {
    async loadCompetitions() {
      if (this.competitions.length > 0) return // 已加载
      
      this.loading = true
      try {
        this.competitions = await competitionAPI.getCompetitions()
        if (this.competitions.length > 0 && !this.selectedCompetitionId) {
          this.selectedCompetitionId = this.competitions[0].id
        }
      } catch (error) {
        console.error('Failed to load competitions:', error)
      } finally {
        this.loading = false
      }
    },

    selectCompetition(competitionId) {
      this.selectedCompetitionId = competitionId
    }
  }
})

