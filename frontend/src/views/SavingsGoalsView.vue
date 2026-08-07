<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useSavingsGoalsStore } from '@/stores/savingsGoals'
import { useAccountsStore } from '@/stores/accounts'
import type { SavingsGoal } from '@/types'
import { formatRupiah, formatTanggal } from '@/lib/format'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Progress } from '@/components/ui/progress'
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
import { Trash2, PiggyBank } from 'lucide-vue-next'

const store = useSavingsGoalsStore()
const accountsStore = useAccountsStore()

// --- Dialog: tambah goal baru ---
const isCreateOpen = ref(false)
const emptyCreateForm = {
  nama: '',
  target_jumlah: '',
  target_tanggal: '',
  account_id: '' as unknown as number | null,
}
const createForm = ref({ ...emptyCreateForm })

async function handleCreate() {
  await store.createGoal({
    nama: createForm.value.nama,
    target_jumlah: createForm.value.target_jumlah,
    target_tanggal: createForm.value.target_tanggal || null,
    account_id: createForm.value.account_id || null,
  })
  isCreateOpen.value = false
  createForm.value = { ...emptyCreateForm }
}

// --- Dialog: kontribusi ---
const isContributeOpen = ref(false)
const activeGoal = ref<SavingsGoal | null>(null)
const contributeAmount = ref('')

function openContributeDialog(goal: SavingsGoal) {
  activeGoal.value = goal
  contributeAmount.value = ''
  isContributeOpen.value = true
}

async function handleContribute() {
  if (!activeGoal.value) return
  await store.contribute(activeGoal.value.id, contributeAmount.value)
  isContributeOpen.value = false
}

async function handleDelete(id: number) {
  if (confirm('Yakin hapus goal ini?')) {
    await store.deleteGoal(id)
  }
}

function progressPercent(goal: SavingsGoal) {
  const pct = (Number(goal.current_jumlah) / Number(goal.target_jumlah)) * 100
  return Math.min(100, Math.round(pct))
}

function isAchieved(goal: SavingsGoal) {
  return Number(goal.current_jumlah) >= Number(goal.target_jumlah)
}

function accountName(id: number | null) {
  if (!id) return null
  return accountsStore.accounts.find((a) => a.id === id)?.nama ?? null
}

const totalTarget = computed(() =>
  store.goals.reduce((sum, g) => sum + Number(g.target_jumlah), 0),
)
const totalCurrent = computed(() =>
  store.goals.reduce((sum, g) => sum + Number(g.current_jumlah), 0),
)

onMounted(() => {
  store.fetchGoals()
  accountsStore.fetchAccounts()
})
</script>

<template>
  <div class="p-6 space-y-6">
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-bold">Savings Goals</h1>

      <Dialog v-model:open="isCreateOpen">
        <DialogTrigger as-child>
          <Button>+ Tambah Goal</Button>
        </DialogTrigger>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Tambah Savings Goal</DialogTitle>
          </DialogHeader>
          <form class="space-y-4" @submit.prevent="handleCreate">
            <div class="space-y-2">
              <Label for="nama">Nama Goal</Label>
              <Input
                id="nama"
                v-model="createForm.nama"
                placeholder="Contoh: Dana Darurat, DP Rumah"
                required
              />
            </div>

            <div class="space-y-2">
              <Label for="target_jumlah">Target Jumlah</Label>
              <Input
                id="target_jumlah"
                v-model="createForm.target_jumlah"
                type="number"
                step="0.01"
                required
              />
            </div>

            <div class="space-y-2">
              <Label for="target_tanggal">Target Tanggal (opsional)</Label>
              <Input id="target_tanggal" v-model="createForm.target_tanggal" type="date" />
            </div>

            <div class="space-y-2">
              <Label>Kaitkan dengan Akun (opsional)</Label>
              <Select v-model="createForm.account_id">
                <SelectTrigger><SelectValue placeholder="Tidak ada" /></SelectTrigger>
                <SelectContent>
                  <SelectItem :value="null">Tidak ada</SelectItem>
                  <SelectItem v-for="acc in accountsStore.accounts" :key="acc.id" :value="acc.id">
                    {{ acc.nama }}
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

    <Card v-if="store.goals.length > 0">
      <CardHeader>
        <CardTitle class="text-sm font-medium text-muted-foreground">Total Progress</CardTitle>
      </CardHeader>
      <CardContent class="space-y-2">
        <div class="flex justify-between text-sm">
          <span class="font-semibold">{{ formatRupiah(totalCurrent) }}</span>
          <span class="text-muted-foreground">dari {{ formatRupiah(totalTarget) }}</span>
        </div>
        <Progress :model-value="totalTarget > 0 ? Math.min(100, (totalCurrent / totalTarget) * 100) : 0" />
      </CardContent>
    </Card>

    <div v-if="store.loading" class="text-muted-foreground">Memuat data...</div>
    <div v-else-if="store.error" class="text-destructive">{{ store.error }}</div>

    <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      <p v-if="store.goals.length === 0" class="text-sm text-muted-foreground col-span-full">
        Belum ada savings goal. Klik "+ Tambah Goal" buat mulai nabung.
      </p>

      <Card v-for="goal in store.goals" :key="goal.id" class="group">
        <CardContent class="space-y-3">
          <div class="flex items-start justify-between">
            <div class="flex items-center gap-2">
              <div class="rounded-full bg-muted p-2">
                <PiggyBank class="size-5 text-muted-foreground" />
              </div>
              <div>
                <p class="font-semibold">{{ goal.nama }}</p>
                <p v-if="accountName(goal.account_id)" class="text-xs text-muted-foreground">
                  {{ accountName(goal.account_id) }}
                </p>
              </div>
            </div>
            <Button
              variant="ghost"
              size="icon"
              class="opacity-0 group-hover:opacity-100 transition-opacity"
              @click="handleDelete(goal.id)"
            >
              <Trash2 class="size-4 text-muted-foreground" />
            </Button>
          </div>

          <div class="space-y-1">
            <div class="flex justify-between text-sm">
              <span class="font-semibold">{{ formatRupiah(goal.current_jumlah) }}</span>
              <span class="text-muted-foreground">dari {{ formatRupiah(goal.target_jumlah) }}</span>
            </div>
            <Progress
              :model-value="progressPercent(goal)"
              :class="isAchieved(goal) ? '[&>div]:bg-green-600' : ''"
            />
            <p class="text-xs text-muted-foreground">
              {{ progressPercent(goal) }}%
              <span v-if="goal.target_tanggal"> · Target {{ formatTanggal(goal.target_tanggal) }}</span>
            </p>
          </div>

          <p v-if="isAchieved(goal)" class="text-sm font-medium text-green-600">
            🎉 Target tercapai!
          </p>
          <Button v-else size="sm" variant="outline" @click="openContributeDialog(goal)">
            + Tambah Tabungan
          </Button>
        </CardContent>
      </Card>
    </div>

    <!-- Dialog kontribusi -->
    <Dialog v-model:open="isContributeOpen">
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Tambah Tabungan - {{ activeGoal?.nama }}</DialogTitle>
        </DialogHeader>
        <form v-if="activeGoal" class="space-y-4" @submit.prevent="handleContribute">
          <p class="text-sm text-muted-foreground">
            Progress saat ini: {{ formatRupiah(activeGoal.current_jumlah) }} dari
            {{ formatRupiah(activeGoal.target_jumlah) }}
          </p>

          <div class="space-y-2">
            <Label for="contribute_jumlah">Jumlah Tambahan</Label>
            <Input
              id="contribute_jumlah"
              v-model="contributeAmount"
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
</template>