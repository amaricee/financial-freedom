<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useDebtsStore } from '@/stores/debts'
import { useAccountsStore } from '@/stores/accounts'
import type { Debt, DebtType } from '@/types'
import { formatRupiah, formatTanggal } from '@/lib/format'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
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
import { Trash2 } from 'lucide-vue-next'

const debtsStore = useDebtsStore()
const accountsStore = useAccountsStore()

// --- Dialog: tambah hutang/piutang baru ---
const isCreateOpen = ref(false)
const emptyCreateForm = {
  tipe: 'piutang' as DebtType,
  nama_pihak: '',
  jumlah_total: '',
  tanggal: new Date().toISOString().slice(0, 10),
  jatuh_tempo: '',
  notes: '',
}
const createForm = ref({ ...emptyCreateForm })

async function handleCreate() {
  await debtsStore.createDebt({
    tipe: createForm.value.tipe,
    nama_pihak: createForm.value.nama_pihak,
    jumlah_total: createForm.value.jumlah_total,
    tanggal: createForm.value.tanggal,
    jatuh_tempo: createForm.value.jatuh_tempo || null,
    notes: createForm.value.notes || null,
  })
  isCreateOpen.value = false
  createForm.value = { ...emptyCreateForm }
}

// --- Dialog: bayar cicilan ---
const isPayOpen = ref(false)
const activeDebt = ref<Debt | null>(null)
const emptyPayForm = {
  jumlah: '',
  account_id: '' as unknown as number,
  tanggal: new Date().toISOString().slice(0, 10),
  deskripsi: '',
}
const payForm = ref({ ...emptyPayForm })

function openPayDialog(debt: Debt) {
  activeDebt.value = debt
  payForm.value = { ...emptyPayForm }
  isPayOpen.value = true
}

const sisaTagihan = computed(() => {
  if (!activeDebt.value) return 0
  return Number(activeDebt.value.jumlah_total) - Number(activeDebt.value.jumlah_terbayar)
})

async function handlePay() {
  if (!activeDebt.value) return
  try {
    await debtsStore.payDebt(activeDebt.value.id, {
      jumlah: payForm.value.jumlah,
      account_id: Number(payForm.value.account_id),
      tanggal: payForm.value.tanggal,
      deskripsi: payForm.value.deskripsi || null,
    })
    isPayOpen.value = false
  } catch (e: any) {
    alert(e?.response?.data?.detail || 'Gagal mencatat pembayaran')
  }
}

async function handleDelete(id: number) {
  if (confirm('Yakin hapus data ini?')) {
    try {
      await debtsStore.deleteDebt(id)
    } catch (e: any) {
      alert(e?.response?.data?.detail || 'Gagal menghapus')
    }
  }
}

function progressPercent(debt: Debt) {
  const pct = (Number(debt.jumlah_terbayar) / Number(debt.jumlah_total)) * 100
  return Math.min(100, Math.round(pct))
}

const hutangList = computed(() => debtsStore.debts.filter((d) => d.tipe === 'hutang'))
const piutangList = computed(() => debtsStore.debts.filter((d) => d.tipe === 'piutang'))

const totalHutangBelumLunas = computed(() =>
  hutangList.value
    .filter((d) => d.status === 'belum_lunas')
    .reduce((sum, d) => sum + (Number(d.jumlah_total) - Number(d.jumlah_terbayar)), 0),
)

const totalPiutangBelumLunas = computed(() =>
  piutangList.value
    .filter((d) => d.status === 'belum_lunas')
    .reduce((sum, d) => sum + (Number(d.jumlah_total) - Number(d.jumlah_terbayar)), 0),
)

onMounted(() => {
  debtsStore.fetchDebts()
  accountsStore.fetchAccounts()
})
</script>

<template>
  <div class="p-6 space-y-6">
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-bold">Hutang/Piutang</h1>

      <Dialog v-model:open="isCreateOpen">
        <DialogTrigger as-child>
          <Button>+ Tambah</Button>
        </DialogTrigger>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Tambah Hutang/Piutang</DialogTitle>
          </DialogHeader>
          <form class="space-y-4" @submit.prevent="handleCreate">
            <div class="space-y-2">
              <Label>Tipe</Label>
              <Select v-model="createForm.tipe">
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="piutang">Piutang (Orang berhutang ke saya)</SelectItem>
                  <SelectItem value="hutang">Hutang (Saya berhutang ke orang)</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div class="space-y-2">
              <Label for="nama_pihak">Nama Pihak</Label>
              <Input
                id="nama_pihak"
                v-model="createForm.nama_pihak"
                placeholder="Nama orang/instansi"
                required
              />
            </div>

            <div class="space-y-2">
              <Label for="jumlah_total">Jumlah Total</Label>
              <Input
                id="jumlah_total"
                v-model="createForm.jumlah_total"
                type="number"
                step="0.01"
                required
              />
            </div>

            <div class="space-y-2">
              <Label for="tanggal">Tanggal</Label>
              <Input id="tanggal" v-model="createForm.tanggal" type="date" required />
            </div>

            <div class="space-y-2">
              <Label for="jatuh_tempo">Jatuh Tempo (opsional)</Label>
              <Input id="jatuh_tempo" v-model="createForm.jatuh_tempo" type="date" />
            </div>

            <div class="space-y-2">
              <Label for="notes">Catatan (opsional)</Label>
              <Textarea id="notes" v-model="createForm.notes" rows="2" />
            </div>

            <DialogFooter>
              <Button type="submit">Simpan</Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>

    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
      <Card>
        <CardHeader>
          <CardTitle class="text-sm font-medium text-muted-foreground">
            Sisa Piutang (Belum Lunas)
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p class="text-2xl font-bold text-green-600">{{ formatRupiah(totalPiutangBelumLunas) }}</p>
        </CardContent>
      </Card>
      <Card>
        <CardHeader>
          <CardTitle class="text-sm font-medium text-muted-foreground">
            Sisa Hutang (Belum Lunas)
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p class="text-2xl font-bold text-red-600">{{ formatRupiah(totalHutangBelumLunas) }}</p>
        </CardContent>
      </Card>
    </div>

    <div v-if="debtsStore.loading" class="text-muted-foreground">Memuat data...</div>
    <div v-else-if="debtsStore.error" class="text-destructive">{{ debtsStore.error }}</div>

    <Tabs v-else default-value="piutang">
      <TabsList>
        <TabsTrigger value="piutang">Piutang ({{ piutangList.length }})</TabsTrigger>
        <TabsTrigger value="hutang">Hutang ({{ hutangList.length }})</TabsTrigger>
      </TabsList>

      <TabsContent value="piutang" class="space-y-3 mt-4">
        <p v-if="piutangList.length === 0" class="text-sm text-muted-foreground">
          Belum ada data piutang
        </p>
        <Card v-for="debt in piutangList" :key="debt.id" class="group">
          <CardContent class="space-y-3">
            <div class="flex items-start justify-between">
              <div>
                <p class="font-semibold">{{ debt.nama_pihak }}</p>
                <p class="text-sm text-muted-foreground">
                  {{ formatTanggal(debt.tanggal) }}
                  <span v-if="debt.jatuh_tempo"> · Jatuh tempo {{ formatTanggal(debt.jatuh_tempo) }}</span>
                </p>
                <p v-if="debt.notes" class="text-sm text-muted-foreground mt-1">{{ debt.notes }}</p>
              </div>
              <div class="flex items-center gap-2">
                <Badge :class="debt.status === 'lunas' ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'">
                  {{ debt.status === 'lunas' ? 'Lunas' : 'Belum Lunas' }}
                </Badge>
                <Button
                  variant="ghost"
                  size="icon"
                  class="opacity-0 group-hover:opacity-100 transition-opacity"
                  @click="handleDelete(debt.id)"
                >
                  <Trash2 class="size-4 text-muted-foreground" />
                </Button>
              </div>
            </div>

            <div class="space-y-1">
              <div class="flex justify-between text-sm">
                <span>{{ formatRupiah(debt.jumlah_terbayar) }} terbayar</span>
                <span class="text-muted-foreground">dari {{ formatRupiah(debt.jumlah_total) }}</span>
              </div>
              <Progress :model-value="progressPercent(debt)" />
            </div>

            <Button
              v-if="debt.status !== 'lunas'"
              size="sm"
              variant="outline"
              @click="openPayDialog(debt)"
            >
              Terima Pembayaran
            </Button>
          </CardContent>
        </Card>
      </TabsContent>

      <TabsContent value="hutang" class="space-y-3 mt-4">
        <p v-if="hutangList.length === 0" class="text-sm text-muted-foreground">
          Belum ada data hutang
        </p>
        <Card v-for="debt in hutangList" :key="debt.id" class="group">
          <CardContent class="space-y-3">
            <div class="flex items-start justify-between">
              <div>
                <p class="font-semibold">{{ debt.nama_pihak }}</p>
                <p class="text-sm text-muted-foreground">
                  {{ formatTanggal(debt.tanggal) }}
                  <span v-if="debt.jatuh_tempo"> · Jatuh tempo {{ formatTanggal(debt.jatuh_tempo) }}</span>
                </p>
                <p v-if="debt.notes" class="text-sm text-muted-foreground mt-1">{{ debt.notes }}</p>
              </div>
              <div class="flex items-center gap-2">
                <Badge :class="debt.status === 'lunas' ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'">
                  {{ debt.status === 'lunas' ? 'Lunas' : 'Belum Lunas' }}
                </Badge>
                <Button
                  variant="ghost"
                  size="icon"
                  class="opacity-0 group-hover:opacity-100 transition-opacity"
                  @click="handleDelete(debt.id)"
                >
                  <Trash2 class="size-4 text-muted-foreground" />
                </Button>
              </div>
            </div>

            <div class="space-y-1">
              <div class="flex justify-between text-sm">
                <span>{{ formatRupiah(debt.jumlah_terbayar) }} terbayar</span>
                <span class="text-muted-foreground">dari {{ formatRupiah(debt.jumlah_total) }}</span>
              </div>
              <Progress :model-value="progressPercent(debt)" />
            </div>

            <Button
              v-if="debt.status !== 'lunas'"
              size="sm"
              variant="outline"
              @click="openPayDialog(debt)"
            >
              Bayar
            </Button>
          </CardContent>
        </Card>
      </TabsContent>
    </Tabs>

    <!-- Dialog bayar cicilan -->
    <Dialog v-model:open="isPayOpen">
      <DialogContent>
        <DialogHeader>
          <DialogTitle>
            {{ activeDebt?.tipe === 'hutang' ? 'Bayar Hutang' : 'Terima Pembayaran Piutang' }}
          </DialogTitle>
        </DialogHeader>
        <form v-if="activeDebt" class="space-y-4" @submit.prevent="handlePay">
          <p class="text-sm text-muted-foreground">
            {{ activeDebt.nama_pihak }} — sisa {{ formatRupiah(sisaTagihan) }}
          </p>

          <div class="space-y-2">
            <Label for="pay_jumlah">Jumlah</Label>
            <Input
              id="pay_jumlah"
              v-model="payForm.jumlah"
              type="number"
              step="0.01"
              :max="sisaTagihan"
              required
            />
          </div>

          <div class="space-y-2">
            <Label>{{ activeDebt.tipe === 'hutang' ? 'Bayar dari Akun' : 'Terima ke Akun' }}</Label>
            <Select v-model="payForm.account_id">
              <SelectTrigger><SelectValue placeholder="Pilih akun" /></SelectTrigger>
              <SelectContent>
                <SelectItem v-for="acc in accountsStore.accounts" :key="acc.id" :value="acc.id">
                  {{ acc.nama }}
                </SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div class="space-y-2">
            <Label for="pay_tanggal">Tanggal</Label>
            <Input id="pay_tanggal" v-model="payForm.tanggal" type="date" required />
          </div>

          <div class="space-y-2">
            <Label for="pay_deskripsi">Catatan (opsional)</Label>
            <Textarea id="pay_deskripsi" v-model="payForm.deskripsi" rows="2" />
          </div>

          <DialogFooter>
            <Button type="submit">Catat Pembayaran</Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  </div>
</template>