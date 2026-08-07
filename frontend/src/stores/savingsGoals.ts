import { ref } from 'vue'
import { defineStore } from 'pinia'
import { api } from '@/lib/api'
import type { SavingsGoal } from '@/types'

interface SavingsGoalCreatePayload {
  nama: string
  target_jumlah: string
  current_jumlah?: string
  target_tanggal?: string | null
  account_id?: number | null
}

export const useSavingsGoalsStore = defineStore('savingsGoals', () => {
  const goals = ref<SavingsGoal[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchGoals() {
    loading.value = true
    error.value = null
    try {
      const { data } = await api.get<SavingsGoal[]>('/savings-goals')
      goals.value = data
    } catch (e) {
      error.value = 'Gagal memuat data savings goal'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function createGoal(payload: SavingsGoalCreatePayload) {
    const { data } = await api.post('/savings-goals', payload)
    await fetchGoals()
    return data
  }

  async function contribute(id: number, jumlah: string) {
    const { data } = await api.post(`/savings-goals/${id}/contribute`, { jumlah })
    await fetchGoals()
    return data
  }

  async function deleteGoal(id: number) {
    await api.delete(`/savings-goals/${id}`)
    await fetchGoals()
  }

  return { goals, loading, error, fetchGoals, createGoal, contribute, deleteGoal }
})  