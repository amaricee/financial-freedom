import { ref } from 'vue'
import { defineStore } from 'pinia'
import { api } from '@/lib/api'
import type { Category, CategoryCreatePayload } from '@/types'

export const useCategoriesStore = defineStore('categories', () => {
  const categories = ref<Category[]>([])
  const loading = ref(false)

  async function fetchCategories() {
    loading.value = true
    try {
      const { data } = await api.get<Category[]>('/categories')
      categories.value = data
    } finally {
      loading.value = false
    }
  }

  async function createCategory(payload: CategoryCreatePayload) {
    const { data } = await api.post('/categories', payload)
    await fetchCategories()
    return data
  }

  return { categories, loading, fetchCategories, createCategory }
})