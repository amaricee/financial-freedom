import { ref } from 'vue'
import { defineStore } from 'pinia'
import { api } from '@/lib/api'
import type { Debt, DebtType, DebtStatus } from '@/types'

interface DebtCreatePayload {
  tipe: DebtType
  nama_pihak: string
  jumlah_total: string
  tanggal: string
  jatuh_tempo?: string | null
  notes?: string | null
}

interface DebtPaymentPayload {
  jumlah: string
  account_id: number
  tanggal: string
  deskripsi?: string | null
}

export const useDebtsStore = defineStore('debts', () => {
  const debts = ref<Debt[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchDebts() {
    loading.value = true
    error.value = null
    try {
      const { data } = await api.get<Debt[]>('/debts')
      debts.value = data
    } catch (e) {
      error.value = 'Gagal memuat data hutang/piutang'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function createDebt(payload: DebtCreatePayload) {
    const { data } = await api.post('/debts', payload)
    await fetchDebts()
    return data
  }

  async function payDebt(id: number, payload: DebtPaymentPayload) {
    const { data } = await api.post(`/debts/${id}/payments`, payload)
    await fetchDebts()
    return data
  }

  async function deleteDebt(id: number) {
    await api.delete(`/debts/${id}`)
    await fetchDebts()
  }

  return { debts, loading, error, fetchDebts, createDebt, payDebt, deleteDebt }
})