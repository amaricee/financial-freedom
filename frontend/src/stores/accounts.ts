import { ref } from 'vue'
import { defineStore } from 'pinia'
import { api } from '@/lib/api'
import type { AccountWithBalance, AccountCreatePayload } from '@/types'

export const useAccountsStore = defineStore('accounts', () => {
  const accounts = ref<AccountWithBalance[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchAccounts() {
    loading.value = true
    error.value = null
    try {
      const { data } = await api.get<AccountWithBalance[]>('/accounts')
      accounts.value = data
    } catch (e) {
      error.value = 'Gagal memuat data akun'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function createAccount(payload: AccountCreatePayload) {
    const { data } = await api.post('/accounts', payload)
    await fetchAccounts() // refresh list biar saldo_current ikut ke-update
    return data
  }

  async function updateAccount(id: number, payload: Partial<AccountCreatePayload>) {
    const { data } = await api.put(`/accounts/${id}`, payload)
    await fetchAccounts()
    return data
  }

  async function deleteAccount(id: number) {
    await api.delete(`/accounts/${id}`)
    await fetchAccounts()
  }

  return { accounts, loading, error, fetchAccounts, createAccount, updateAccount, deleteAccount }
})