import { ref } from 'vue'
import { defineStore } from 'pinia'
import { api } from '@/lib/api'
import type { BudgetWithRealisasi } from '@/types'

interface BudgetCreatePayload {
  category_id: number
  bulan: number
  tahun: number
  jumlah_budget: string
}

export const useBudgetsStore = defineStore('budgets', () => {
  const budgets = ref<BudgetWithRealisasi[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchBudgets(bulan: number, tahun: number) {
    loading.value = true
    error.value = null
    try {
      const { data } = await api.get<BudgetWithRealisasi[]>('/budgets', {
        params: { bulan, tahun },
      })
      budgets.value = data
    } catch (e) {
      error.value = 'Gagal memuat data budget'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function createBudget(payload: BudgetCreatePayload) {
    const { data } = await api.post('/budgets', payload)
    await fetchBudgets(payload.bulan, payload.tahun)
    return data
  }

  async function deleteBudget(id: number, bulan: number, tahun: number) {
    await api.delete(`/budgets/${id}`)
    await fetchBudgets(bulan, tahun)
  }

  return { budgets, loading, error, fetchBudgets, createBudget, deleteBudget }
})