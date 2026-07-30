<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useAccountsStore } from '@/stores/accounts'
import type { AccountType } from '@/types'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
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

const store = useAccountsStore()

const isDialogOpen = ref(false)
const form = ref({
  nama: '',
  tipe: 'bank' as AccountType,
  saldo_awal: '0',
})

const accountTypeLabels: Record<AccountType, string> = {
  bank: 'Bank',
  cash: 'Cash',
  e_wallet: 'E-Wallet',
  investasi: 'Investasi',
}

function formatRupiah(value: string) {
  const num = Number(value)
  return new Intl.NumberFormat('id-ID', {
    style: 'currency',
    currency: 'IDR',
    minimumFractionDigits: 0,
  }).format(num)
}

async function handleSubmit() {
  await store.createAccount(form.value)
  isDialogOpen.value = false
  form.value = { nama: '', tipe: 'bank', saldo_awal: '0' }
}

onMounted(() => {
  store.fetchAccounts()
})
</script>

<template>
  <div class="p-6 space-y-6">
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-bold">Akun</h1>

      <Dialog v-model:open="isDialogOpen">
        <DialogTrigger as-child>
          <Button>+ Tambah Akun</Button>
        </DialogTrigger>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Tambah Akun Baru</DialogTitle>
          </DialogHeader>
          <form class="space-y-4" @submit.prevent="handleSubmit">
            <div class="space-y-2">
              <Label for="nama">Nama Akun</Label>
              <Input id="nama" v-model="form.nama" placeholder="Contoh: BCA, Cash, GoPay" required />
            </div>
            <div class="space-y-2">
              <Label>Tipe Akun</Label>
              <Select v-model="form.tipe">
                <SelectTrigger>
                  <SelectValue placeholder="Pilih tipe akun" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem v-for="(label, value) in accountTypeLabels" :key="value" :value="value">
                    {{ label }}
                  </SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div class="space-y-2">
              <Label for="saldo_awal">Saldo Awal</Label>
              <Input id="saldo_awal" v-model="form.saldo_awal" type="number" step="0.01" />
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

    <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      <Card v-for="account in store.accounts" :key="account.id">
        <CardHeader>
          <CardTitle class="flex items-center justify-between">
            <span>{{ account.nama }}</span>
            <span class="text-xs font-normal text-muted-foreground">
              {{ accountTypeLabels[account.tipe] }}
            </span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p class="text-2xl font-bold">{{ formatRupiah(account.saldo_current) }}</p>
        </CardContent>
      </Card>

      <p v-if="store.accounts.length === 0" class="text-muted-foreground col-span-full">
        Belum ada akun. Klik "+ Tambah Akun" buat mulai.
      </p>
    </div>
  </div>
</template>