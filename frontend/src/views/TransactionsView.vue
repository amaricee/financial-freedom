<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useTransactionsStore } from '@/stores/transactions'
import { useAccountsStore } from '@/stores/accounts'
import { useCategoriesStore } from '@/stores/categories'
import type { Transaction, TransactionType } from '@/types'
import { formatRupiah, formatTanggal } from '@/lib/format'
import { checkAndNotifySpending } from '@/lib/spending-alert'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
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
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Trash2, Pencil } from 'lucide-vue-next'

const trxStore = useTransactionsStore()
const accountsStore = useAccountsStore()
const categoriesStore = useCategoriesStore()

const isDialogOpen = ref(false)
const editingId = ref<number | null>(null) // null = create, ada isinya = edit

const emptyForm = {
  account_id: '' as unknown as number,
  category_id: '' as unknown as number | null,
  tipe: 'expense' as TransactionType,
  jumlah: '',
  tanggal: new Date().toISOString().slice(0, 10),
  deskripsi: '',
  account_id_tujuan: '' as unknown as number | null,
}
const form = ref({ ...emptyForm })

const tipeLabels: Record<TransactionType, string> = {
  income: 'Pemasukan',
  expense: 'Pengeluaran',
  transfer: 'Transfer',
}

const tipeBadgeClass: Record<TransactionType, string> = {
  income: 'bg-green-100 text-green-700 hover:bg-green-100',
  expense: 'bg-red-100 text-red-700 hover:bg-red-100',
  transfer: 'bg-blue-100 text-blue-700 hover:bg-blue-100',
}

const filteredCategories = computed(() =>
  categoriesStore.categories.filter((c) => c.tipe === form.value.tipe),
)

function accountName(id: number) {
  return accountsStore.accounts.find((a) => a.id === id)?.nama ?? '-'
}

function categoryName(id: number | null) {
  if (!id) return '-'
  return categoriesStore.categories.find((c) => c.id === id)?.nama ?? '-'
}

function amountPrefix(tipe: TransactionType) {
  if (tipe === 'income') return '+ '
  if (tipe === 'expense') return '- '
  return ''
}

const sortedTransactions = computed(() =>
  [...trxStore.transactions].sort(
    (a, b) => new Date(b.tanggal).getTime() - new Date(a.tanggal).getTime() || b.id - a.id,
  ),
)

function openCreateDialog() {
  editingId.value = null
  form.value = { ...emptyForm }
  isDialogOpen.value = true
}

function openEditDialog(trx: Transaction) {
  editingId.value = trx.id
  form.value = {
    account_id: trx.account_id,
    category_id: trx.category_id,
    tipe: trx.tipe,
    jumlah: trx.jumlah,
    tanggal: trx.tanggal,
    deskripsi: trx.deskripsi ?? '',
    account_id_tujuan: trx.account_id_tujuan,
  }
  isDialogOpen.value = true
}

async function handleSubmit() {
  const payload = {
    account_id: Number(form.value.account_id),
    category_id: form.value.tipe === 'transfer' ? null : Number(form.value.category_id),
    tipe: form.value.tipe,
    jumlah: form.value.jumlah,
    tanggal: form.value.tanggal,
    deskripsi: form.value.deskripsi || null,
    account_id_tujuan:
      form.value.tipe === 'transfer' ? Number(form.value.account_id_tujuan) : null,
  }

  if (editingId.value) {
    // Mode edit: gak perlu cek spending alert, itu cuma relevan buat transaksi baru
    await trxStore.updateTransaction(editingId.value, payload)
  } else {
    const catName = categoryName(payload.category_id)
    checkAndNotifySpending({
      newTransaction: payload,
      categoryName: catName,
      allTransactions: trxStore.transactions,
    })
    await trxStore.createTransaction(payload)
  }

  isDialogOpen.value = false
  form.value = { ...emptyForm }
  editingId.value = null
}

async function handleDelete(id: number) {
  if (confirm('Yakin hapus transaksi ini?')) {
    await trxStore.deleteTransaction(id)
  }
}

onMounted(() => {
  trxStore.fetchTransactions()
  accountsStore.fetchAccounts()
  categoriesStore.fetchCategories()
})
</script>

<template>
  <div class="p-6 space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold">Transaksi</h1>
        <p class="text-sm text-muted-foreground">
          {{ sortedTransactions.length }} transaksi tercatat
        </p>
      </div>

      <Dialog v-model:open="isDialogOpen">
        <DialogTrigger as-child>
          <Button @click="openCreateDialog">+ Tambah Transaksi</Button>
        </DialogTrigger>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{{ editingId ? 'Edit Transaksi' : 'Tambah Transaksi' }}</DialogTitle>
          </DialogHeader>
          <form class="space-y-4" @submit.prevent="handleSubmit">
            <div class="space-y-2">
              <Label>Tipe</Label>
              <Select v-model="form.tipe">
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem v-for="(label, value) in tipeLabels" :key="value" :value="value">
                    {{ label }}
                  </SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div class="space-y-2">
              <Label>{{ form.tipe === 'transfer' ? 'Dari Akun' : 'Akun' }}</Label>
              <Select v-model="form.account_id">
                <SelectTrigger><SelectValue placeholder="Pilih akun" /></SelectTrigger>
                <SelectContent>
                  <SelectItem
                    v-for="acc in accountsStore.accounts"
                    :key="acc.id"
                    :value="acc.id"
                  >
                    {{ acc.nama }}
                  </SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div v-if="form.tipe === 'transfer'" class="space-y-2">
              <Label>Ke Akun</Label>
              <Select v-model="form.account_id_tujuan">
                <SelectTrigger><SelectValue placeholder="Pilih akun tujuan" /></SelectTrigger>
                <SelectContent>
                  <SelectItem
                    v-for="acc in accountsStore.accounts"
                    :key="acc.id"
                    :value="acc.id"
                  >
                    {{ acc.nama }}
                  </SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div v-else class="space-y-2">
              <Label>Kategori</Label>
              <Select v-model="form.category_id">
                <SelectTrigger><SelectValue placeholder="Pilih kategori" /></SelectTrigger>
                <SelectContent>
                  <SelectItem v-for="cat in filteredCategories" :key="cat.id" :value="cat.id">
                    {{ cat.nama }}
                  </SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div class="space-y-2">
              <Label for="jumlah">Jumlah</Label>
              <Input id="jumlah" v-model="form.jumlah" type="number" step="0.01" required />
            </div>

            <div class="space-y-2">
              <Label for="tanggal">Tanggal</Label>
              <Input id="tanggal" v-model="form.tanggal" type="date" required />
            </div>

            <div class="space-y-2">
              <Label for="deskripsi">Deskripsi (opsional)</Label>
              <Textarea id="deskripsi" v-model="form.deskripsi" rows="2" />
            </div>

            <DialogFooter>
              <Button type="submit">Simpan</Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>

    <div v-if="trxStore.loading" class="text-muted-foreground">Memuat data...</div>
    <div v-else-if="trxStore.error" class="text-destructive">{{ trxStore.error }}</div>

    <Card v-else class="py-0 overflow-hidden gap-0">
      <Table>
        <TableHeader>
          <TableRow class="bg-muted/50 hover:bg-muted/50">
            <TableHead class="pl-6">Tanggal</TableHead>
            <TableHead>Tipe</TableHead>
            <TableHead>Akun</TableHead>
            <TableHead>Kategori</TableHead>
            <TableHead>Deskripsi</TableHead>
            <TableHead class="text-right">Jumlah</TableHead>
            <TableHead class="pr-6 w-20"></TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          <TableRow
            v-for="trx in sortedTransactions"
            :key="trx.id"
            class="group hover:bg-muted/40"
          >
            <TableCell class="pl-6 text-muted-foreground whitespace-nowrap">
              {{ formatTanggal(trx.tanggal) }}
            </TableCell>
            <TableCell>
              <Badge :class="tipeBadgeClass[trx.tipe]" class="font-medium">
                {{ tipeLabels[trx.tipe] }}
              </Badge>
            </TableCell>
            <TableCell>
              {{ accountName(trx.account_id) }}
              <span v-if="trx.tipe === 'transfer'" class="text-muted-foreground">
                → {{ accountName(trx.account_id_tujuan!) }}
              </span>
            </TableCell>
            <TableCell class="text-muted-foreground">{{ categoryName(trx.category_id) }}</TableCell>
            <TableCell class="text-muted-foreground max-w-[200px] truncate">
              {{ trx.deskripsi || '-' }}
            </TableCell>
            <TableCell
              class="text-right font-semibold whitespace-nowrap"
              :class="{
                'text-green-600': trx.tipe === 'income',
                'text-red-600': trx.tipe === 'expense',
              }"
            >
              {{ amountPrefix(trx.tipe) }}{{ formatRupiah(trx.jumlah) }}
            </TableCell>
            <TableCell class="pr-6">
              <div class="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                <Button variant="ghost" size="icon" @click="openEditDialog(trx)">
                  <Pencil class="size-4 text-muted-foreground" />
                </Button>
                <Button variant="ghost" size="icon" @click="handleDelete(trx.id)">
                  <Trash2 class="size-4 text-muted-foreground" />
                </Button>
              </div>
            </TableCell>
          </TableRow>
          <TableRow v-if="sortedTransactions.length === 0">
            <TableCell colspan="7" class="text-center text-muted-foreground py-10">
              Belum ada transaksi
            </TableCell>
          </TableRow>
        </TableBody>
      </Table>
    </Card>
  </div>
</template>