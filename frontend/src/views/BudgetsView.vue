<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useBudgetsStore } from '@/stores/budgets'
import { useCategoriesStore } from '@/stores/categories'
import { formatRupiah } from '@/lib/format'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Progress } from '@/components/ui/progress'
import { Card, CardContent } from '@/components/ui/card'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogFooter,
} from '@/components/ui/dialog'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { ChevronLeft, ChevronRight, Trash2 } from 'lucide-vue-next'

const store = useBudgetsStore()
const categoriesStore = useCategoriesStore()

const bulanLabel = [
  'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
  'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember',
]

const now = new Date()
const activeMonth = ref(now.getMonth() + 1)
const activeYear = ref(now.getFullYear())

function goToPrevMonth() {
  if (activeMonth.value === 1) {
    activeMonth.value = 12
    activeYear.value -= 1
  } else {
    activeMonth.value -= 1
  }
}

function goToNextMonth() {
  if (activeMonth.value === 12) {
    activeMonth.value = 1
    activeYear.value += 1
  } else {
    activeMonth.value += 1
  }
}

// Kategori expense yang belum punya budget di bulan/tahun aktif
const availableCategories = computed(() => {
  const usedIds = new Set(store.budgets.map((b) => b.category_id))
  return categoriesStore.categories.filter((c) => c.tipe === 'expense' && !usedIds.has(c.id))
})

function categoryName(id: number) {
  return categoriesStore.categories.find((c) => c.id === id)?.nama ?? '-'
}

function progressColorClass(persentase: number) {
  if (persentase >= 100) return 'text-red-600'
  if (persentase >= 80) return 'text-yellow-600'
  return 'text-green-600'
}

function progressBarClass(persentase: number) {
  if (persentase >= 100) return '[&>div]:bg-red-600'
  if (persentase >= 80) return '[&>div]:bg-yellow-500'
  return '[&>div]:bg-green-600'
}

// --- Dialog tambah budget ---
const isDialogOpen = ref(false)
const emptyForm = {
  category_id: '' as unknown as number,
  jumlah_budget: '',
}
const form = ref({ ...emptyForm })

async function handleSubmit() {
  await store.createBudget({
    category_id: Number(form.value.category_id),
    bulan: activeMonth.value,
    tahun: activeYear.value,
    jumlah_budget: form.value.jumlah_budget,
  })
  isDialogOpen.value = false
  form.value = { ...emptyForm }
}

async function handleDelete(id: number) {
  if (confirm('Yakin hapus budget ini?')) {
    await store.deleteBudget(id, activeMonth.value, activeYear.value)
  }
}

function fetchCurrentMonth() {
  store.fetchBudgets(activeMonth.value, activeYear.value)
}

watch([activeMonth, activeYear], fetchCurrentMonth)

onMounted(() => {
  fetchCurrentMonth()
  categoriesStore.fetchCategories()
})
</script>

<template>
  <div class="p-6 space-y-6">
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-bold">Budget</h1>

      <Dialog v-model:open="isDialogOpen">
        <DialogTrigger as-child>
          <Button :disabled="availableCategories.length === 0">+ Tambah Budget</Button>
        </DialogTrigger>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Tambah Budget - {{ bulanLabel[activeMonth - 1] }} {{ activeYear }}</DialogTitle>
          </DialogHeader>
          <form class="space-y-4" @submit.prevent="handleSubmit">
            <div class="space-y-2">
              <Label>Kategori</Label>
              <Select v-model="form.category_id">
                <SelectTrigger><SelectValue placeholder="Pilih kategori pengeluaran" /></SelectTrigger>
                <SelectContent>
                  <SelectItem v-for="cat in availableCategories" :key="cat.id" :value="cat.id">
                    {{ cat.nama }}
                  </SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div class="space-y-2">
              <Label for="jumlah_budget">Jumlah Budget</Label>
              <Input
                id="jumlah_budget"
                v-model="form.jumlah_budget"
                type="number"
                step="0.01"
                required
              />
            </div>

            <DialogFooter>
              <Button type="submit">Simpan</Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>

    <!-- Navigasi bulan -->
    <div class="flex items-center gap-3">
      <Button variant="outline" size="icon" @click="goToPrevMonth">
        <ChevronLeft class="size-4" />
      </Button>
      <p class="font-medium min-w-[160px] text-center">
        {{ bulanLabel[activeMonth - 1] }} {{ activeYear }}
      </p>
      <Button variant="outline" size="icon" @click="goToNextMonth">
        <ChevronRight class="size-4" />
      </Button>
    </div>

    <div v-if="store.loading" class="text-muted-foreground">Memuat data...</div>
    <div v-else-if="store.error" class="text-destructive">{{ store.error }}</div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <p v-if="store.budgets.length === 0" class="text-sm text-muted-foreground col-span-full">
        Belum ada budget di bulan ini. Klik "+ Tambah Budget" buat mulai.
      </p>

      <Card v-for="budget in store.budgets" :key="budget.id" class="group">
        <CardContent class="space-y-3">
          <div class="flex items-start justify-between">
            <div>
              <p class="font-semibold">{{ categoryName(budget.category_id) }}</p>
              <p class="text-sm text-muted-foreground">
                {{ formatRupiah(budget.realisasi) }} dari {{ formatRupiah(budget.jumlah_budget) }}
              </p>
            </div>
            <div class="flex items-center gap-2">
              <span :class="['text-sm font-semibold', progressColorClass(budget.persentase)]">
                {{ budget.persentase }}%
              </span>
              <Button
                variant="ghost"
                size="icon"
                class="opacity-0 group-hover:opacity-100 transition-opacity"
                @click="handleDelete(budget.id)"
              >
                <Trash2 class="size-4 text-muted-foreground" />
              </Button>
            </div>
          </div>

          <Progress :model-value="Math.min(100, budget.persentase)" :class="progressBarClass(budget.persentase)" />

          <p
            class="text-sm"
            :class="Number(budget.sisa) < 0 ? 'text-red-600' : 'text-muted-foreground'"
          >
            <template v-if="Number(budget.sisa) < 0">
              Over budget {{ formatRupiah(Math.abs(Number(budget.sisa))) }}
            </template>
            <template v-else> Sisa {{ formatRupiah(budget.sisa) }} </template>
          </p>
        </CardContent>
      </Card>
    </div>
  </div>
</template>