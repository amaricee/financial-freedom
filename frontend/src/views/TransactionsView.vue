<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useTransactionsStore } from '@/stores/transactions'
import { useAccountsStore } from '@/stores/accounts'
import { useCategoriesStore } from '@/stores/categories'
import type { TransactionType } from '@/types'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
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

const trxStore = useTransactionsStore()
const accountsStore = useAccountsStore()
const categoriesStore = useCategoriesStore()

const isDialogOpen = ref(false)

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

// Kategori difilter sesuai tipe transaksi yang dipilih (income/expense)
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

function formatRupiah(value: string) {
  return new Intl.NumberFormat('id-ID', {
    style: 'currency',
    currency: 'IDR',
    minimumFractionDigits: 0,
  }).format(Number(value))
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
  await trxStore.createTransaction(payload)
  isDialogOpen.value = false
  form.value = { ...emptyForm }
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
      <h1 class="text-2xl font-bold">Transaksi</h1>

      <Dialog v-model:open="isDialogOpen">
        <DialogTrigger as-child>
          <Button>+ Tambah Transaksi</Button>
        </DialogTrigger>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Tambah Transaksi</DialogTitle>
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

    <Table v-else>
      <TableHeader>
        <TableRow>
          <TableHead>Tanggal</TableHead>
          <TableHead>Tipe</TableHead>
          <TableHead>Akun</TableHead>
          <TableHead>Kategori</TableHead>
          <TableHead>Deskripsi</TableHead>
          <TableHead class="text-right">Jumlah</TableHead>
          <TableHead></TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        <TableRow v-for="trx in trxStore.transactions" :key="trx.id">
          <TableCell>{{ trx.tanggal }}</TableCell>
          <TableCell>{{ tipeLabels[trx.tipe] }}</TableCell>
          <TableCell>
            {{ accountName(trx.account_id) }}
            <span v-if="trx.tipe === 'transfer'"> → {{ accountName(trx.account_id_tujuan!) }}</span>
          </TableCell>
          <TableCell>{{ categoryName(trx.category_id) }}</TableCell>
          <TableCell class="text-muted-foreground">{{ trx.deskripsi || '-' }}</TableCell>
          <TableCell class="text-right font-medium">{{ formatRupiah(trx.jumlah) }}</TableCell>
          <TableCell>
            <Button variant="ghost" size="sm" @click="handleDelete(trx.id)">Hapus</Button>
          </TableCell>
        </TableRow>
        <TableRow v-if="trxStore.transactions.length === 0">
          <TableCell colspan="7" class="text-center text-muted-foreground">
            Belum ada transaksi
          </TableCell>
        </TableRow>
      </TableBody>
    </Table>
  </div>
</template>