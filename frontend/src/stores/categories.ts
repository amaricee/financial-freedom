import { ref } from 'vue'
import { defineStore } from 'pinia'
import { api } from '@/lib/api'
import type { Category, CategoryCreatePayload } from '@/types'

export const useCategoriesStore = defineStore('categories', () => {
  const categories = ref<Category[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchCategories() {
    loading.value = true
    error.value = null
    try {
      const { data } = await api.get<Category[]>('/categories')
      categories.value = data
    } catch (e) {
      error.value = 'Gagal memuat data kategori'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function createCategory(payload: CategoryCreatePayload) {
    const { data } = await api.post('/categories', payload)
    await fetchCategories()
    return data
  }

  async function deleteCategory(id: number) {
    await api.delete(`/categories/${id}`)
    await fetchCategories()
  }

  return { categories, loading, error, fetchCategories, createCategory, deleteCategory }
})