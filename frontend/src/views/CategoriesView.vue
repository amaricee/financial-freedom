<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useCategoriesStore } from '@/stores/categories'
import type { Category, CategoryType } from '@/types'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
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
import { Trash2, CornerDownRight } from 'lucide-vue-next'

const store = useCategoriesStore()

const isDialogOpen = ref(false)
const emptyForm = {
  nama: '',
  tipe: 'expense' as CategoryType,
  parent_id: null as number | null,
}
const form = ref({ ...emptyForm })

// Kategori top-level (calon induk) buat pilihan parent, difilter sesuai tipe yang dipilih
const possibleParents = computed(() =>
  store.categories.filter((c) => c.tipe === form.value.tipe && c.parent_id === null),
)

function groupedByType(tipe: CategoryType) {
  const topLevel = store.categories.filter((c) => c.tipe === tipe && c.parent_id === null)
  return topLevel.map((parent) => ({
    ...parent,
    children: store.categories.filter((c) => c.parent_id === parent.id),
  }))
}

const incomeCategories = computed(() => groupedByType('income'))
const expenseCategories = computed(() => groupedByType('expense'))

async function handleSubmit() {
  await store.createCategory({
    nama: form.value.nama,
    tipe: form.value.tipe,
    parent_id: form.value.parent_id,
  })
  isDialogOpen.value = false
  form.value = { ...emptyForm }
}

async function handleDelete(id: number) {
  if (confirm('Yakin hapus kategori ini?')) {
    try {
      await store.deleteCategory(id)
    } catch {
      alert('Kategori tidak bisa dihapus — masih punya sub-kategori atau dipakai transaksi')
    }
  }
}

function openAddSubcategory(parent: Category) {
  form.value = { nama: '', tipe: parent.tipe, parent_id: parent.id }
  isDialogOpen.value = true
}

onMounted(() => {
  store.fetchCategories()
})
</script>

<template>
  <div class="p-6 space-y-6">
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-bold">Kategori</h1>

      <Dialog v-model:open="isDialogOpen">
        <DialogTrigger as-child>
          <Button @click="form = { ...emptyForm }">+ Tambah Kategori</Button>
        </DialogTrigger>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Tambah Kategori</DialogTitle>
          </DialogHeader>
          <form class="space-y-4" @submit.prevent="handleSubmit">
            <div class="space-y-2">
              <Label for="nama">Nama Kategori</Label>
              <Input id="nama" v-model="form.nama" placeholder="Contoh: Makan, Gaji" required />
            </div>

            <div class="space-y-2">
              <Label>Tipe</Label>
              <Select v-model="form.tipe">
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="income">Pemasukan</SelectItem>
                  <SelectItem value="expense">Pengeluaran</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div class="space-y-2">
              <Label>Sub-kategori dari (opsional)</Label>
              <Select v-model="form.parent_id">
                <SelectTrigger><SelectValue placeholder="Tidak ada (kategori utama)" /></SelectTrigger>
                <SelectContent>
                  <SelectItem :value="null">Tidak ada (kategori utama)</SelectItem>
                  <SelectItem v-for="p in possibleParents" :key="p.id" :value="p.id">
                    {{ p.nama }}
                  </SelectItem>
                </SelectContent>
              </Select>
            </div>

            <DialogFooter>
              <Button type="submit">Simpan</Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>

    <div v-if="store.loading" class="text-muted-foreground">Memuat data...</div>
    <div v-else-if="store.error" class="text-destructive">{{ store.error }}</div>

    <div v-else class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <Card>
        <CardHeader>
          <CardTitle class="flex items-center gap-2">
            Pemasukan
            <Badge class="bg-green-100 text-green-700 hover:bg-green-100">
              {{ incomeCategories.length }}
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent class="space-y-1">
          <p v-if="incomeCategories.length === 0" class="text-sm text-muted-foreground">
            Belum ada kategori pemasukan
          </p>
          <div v-for="cat in incomeCategories" :key="cat.id">
            <div class="group flex items-center justify-between py-2 border-b last:border-0">
              <span class="font-medium">{{ cat.nama }}</span>
              <div class="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                <Button variant="ghost" size="sm" @click="openAddSubcategory(cat)">+ Sub</Button>
                <Button variant="ghost" size="icon" @click="handleDelete(cat.id)">
                  <Trash2 class="size-4 text-muted-foreground" />
                </Button>
              </div>
            </div>
            <div
              v-for="child in cat.children"
              :key="child.id"
              class="group flex items-center justify-between py-2 pl-6 border-b last:border-0 text-sm text-muted-foreground"
            >
              <span class="flex items-center gap-1">
                <CornerDownRight class="size-3.5" />
                {{ child.nama }}
              </span>
              <Button
                variant="ghost"
                size="icon"
                class="opacity-0 group-hover:opacity-100 transition-opacity"
                @click="handleDelete(child.id)"
              >
                <Trash2 class="size-4" />
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle class="flex items-center gap-2">
            Pengeluaran
            <Badge class="bg-red-100 text-red-700 hover:bg-red-100">
              {{ expenseCategories.length }}
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent class="space-y-1">
          <p v-if="expenseCategories.length === 0" class="text-sm text-muted-foreground">
            Belum ada kategori pengeluaran
          </p>
          <div v-for="cat in expenseCategories" :key="cat.id">
            <div class="group flex items-center justify-between py-2 border-b last:border-0">
              <span class="font-medium">{{ cat.nama }}</span>
              <div class="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                <Button variant="ghost" size="sm" @click="openAddSubcategory(cat)">+ Sub</Button>
                <Button variant="ghost" size="icon" @click="handleDelete(cat.id)">
                  <Trash2 class="size-4 text-muted-foreground" />
                </Button>
              </div>
            </div>
            <div
              v-for="child in cat.children"
              :key="child.id"
              class="group flex items-center justify-between py-2 pl-6 border-b last:border-0 text-sm text-muted-foreground"
            >
              <span class="flex items-center gap-1">
                <CornerDownRight class="size-3.5" />
                {{ child.nama }}
              </span>
              <Button
                variant="ghost"
                size="icon"
                class="opacity-0 group-hover:opacity-100 transition-opacity"
                @click="handleDelete(child.id)"
              >
                <Trash2 class="size-4" />
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  </div>
</template>