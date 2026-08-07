import { ref } from 'vue'
import { defineStore } from 'pinia'
import { api } from '@/lib/api'
import type { Transaction, TransactionCreatePayload } from '@/types'

export const useTransactionsStore = defineStore('transactions', () => {
  const transactions = ref<Transaction[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchTransactions() {
    loading.value = true
    error.value = null
    try {
      const { data } = await api.get<Transaction[]>('/transactions')
      transactions.value = data
    } catch (e) {
      error.value = 'Gagal memuat data transaksi'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function createTransaction(payload: TransactionCreatePayload) {
    const { data } = await api.post('/transactions', payload)
    await fetchTransactions()
    return data
  }

  async function updateTransaction(id: number, payload: Partial<TransactionCreatePayload>) {
    const { data } = await api.put(`/transactions/${id}`, payload)
    await fetchTransactions()
    return data
  }

  async function deleteTransaction(id: number) {
    await api.delete(`/transactions/${id}`)
    await fetchTransactions()
  }

  return {
    transactions,
    loading,
    error,
    fetchTransactions,
    createTransaction,
    updateTransaction,
    deleteTransaction,
  }
})