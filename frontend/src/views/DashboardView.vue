<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useAccountsStore } from '@/stores/accounts'
import { useTransactionsStore } from '@/stores/transactions'
import { useCategoriesStore } from '@/stores/categories'
import { formatRupiah, formatTanggal } from '@/lib/format'
import { getPeriodeGajian } from '@/lib/periode'
import { getSpendingLabel } from '@/lib/spending-alert'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import IncomeExpenseChart from '@/components/IncomeExpenseChart.vue'
import ExpenseByCategoryChart from '@/components/ExpenseByCategoryChart.vue'

const accountsStore = useAccountsStore()
const trxStore = useTransactionsStore()
const categoriesStore = useCategoriesStore()

const { start: periodeStart, end: periodeEnd } = getPeriodeGajian(new Date())

function formatPeriodeLabel(d: Date) {
  return d.toLocaleDateString('id-ID', { day: 'numeric', month: 'short' })
}

const totalSaldo = computed(() =>
  accountsStore.accounts.reduce((sum, acc) => sum + Number(acc.saldo_current), 0),
)

const transaksiPeriodeIni = computed(() =>
  trxStore.transactions.filter((t) => {
    const d = new Date(t.tanggal)
    return d >= periodeStart && d <= periodeEnd
  }),
)

const totalIncomePeriodeIni = computed(() =>
  transaksiPeriodeIni.value
    .filter((t) => t.tipe === 'income')
    .reduce((sum, t) => sum + Number(t.jumlah), 0),
)

const totalExpensePeriodeIni = computed(() =>
  transaksiPeriodeIni.value
    .filter((t) => t.tipe === 'expense')
    .reduce((sum, t) => sum + Number(t.jumlah), 0),
)

const netPeriodeIni = computed(() => totalIncomePeriodeIni.value - totalExpensePeriodeIni.value)

const transaksiTerbaru = computed(() =>
  [...trxStore.transactions]
    .sort((a, b) => new Date(b.tanggal).getTime() - new Date(a.tanggal).getTime() || b.id - a.id)
    .slice(0, 5),
)

onMounted(() => {
  accountsStore.fetchAccounts()
  trxStore.fetchTransactions()
  categoriesStore.fetchCategories()
})
</script>

<template>
  <div class="p-6 space-y-6">
    <div>
      <h1 class="text-2xl font-heading font-semibold tracking-tight">Dashboard</h1>
      <p class="text-sm text-muted-foreground">Ringkasan keuangan periode berjalan</p>
    </div>

    <!-- Hero: Total Saldo dengan tekstur ledger halus -->
    <Card class="relative overflow-hidden border-none bg-primary text-primary-foreground py-8">
      <div
        class="pointer-events-none absolute inset-0 opacity-[0.07]"
        style="background-image: repeating-linear-gradient(0deg, currentColor 0px, currentColor 1px, transparent 1px, transparent 28px); background-position: 0 -10px"
      />
      <CardContent class="relative space-y-1">
        <p class="text-sm font-medium opacity-70">Total Saldo</p>
        <p class="font-mono text-4xl sm:text-5xl font-semibold tabular-nums tracking-tight">
          {{ formatRupiah(totalSaldo) }}
        </p>
        <p class="text-sm opacity-70 pt-1">
          <span :class="netPeriodeIni >= 0 ? 'text-emerald-300' : 'text-red-300'">
            {{ netPeriodeIni >= 0 ? '+' : '' }}{{ formatRupiah(netPeriodeIni) }}
          </span>
          periode {{ formatPeriodeLabel(periodeStart) }} - {{ formatPeriodeLabel(periodeEnd) }}
        </p>
      </CardContent>
    </Card>

    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
      <Card>
        <CardHeader>
          <CardTitle class="text-sm font-medium text-muted-foreground">
            Pemasukan Periode Ini
            <span class="block text-xs font-normal mt-0.5">
              {{ formatPeriodeLabel(periodeStart) }} - {{ formatPeriodeLabel(periodeEnd) }}
            </span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p class="font-mono text-2xl font-semibold tabular-nums text-green-600">
            {{ formatRupiah(totalIncomePeriodeIni) }}
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle class="text-sm font-medium text-muted-foreground">
            Pengeluaran Periode Ini
            <span class="block text-xs font-normal mt-0.5">
              {{ formatPeriodeLabel(periodeStart) }} - {{ formatPeriodeLabel(periodeEnd) }}
            </span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p class="font-mono text-2xl font-semibold tabular-nums text-red-600">
            {{ formatRupiah(totalExpensePeriodeIni) }}
          </p>
        </CardContent>
      </Card>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
      <Card>
        <CardHeader>
          <CardTitle class="font-heading">
            Pemasukan vs Pengeluaran
            <span class="block text-xs font-normal text-muted-foreground mt-0.5">
              Periode {{ formatPeriodeLabel(periodeStart) }} - {{ formatPeriodeLabel(periodeEnd) }}
            </span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <IncomeExpenseChart
            :transactions="trxStore.transactions"
            :periode-start="periodeStart"
            :periode-end="periodeEnd"
          />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle class="font-heading">
            Pengeluaran per Kategori
            <span class="block text-xs font-normal text-muted-foreground mt-0.5">
              Periode {{ formatPeriodeLabel(periodeStart) }} - {{ formatPeriodeLabel(periodeEnd) }}
            </span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <ExpenseByCategoryChart
            :transactions="trxStore.transactions"
            :categories="categoriesStore.categories"
            :periode-start="periodeStart"
            :periode-end="periodeEnd"
          />
        </CardContent>
      </Card>
    </div>

    <Card>
      <CardHeader>
        <CardTitle class="font-heading">Transaksi Terbaru</CardTitle>
      </CardHeader>
      <CardContent>
        <div v-if="transaksiTerbaru.length === 0" class="text-muted-foreground text-sm">
          Belum ada transaksi
        </div>
        <div v-else class="space-y-3">
          <div
            v-for="trx in transaksiTerbaru"
            :key="trx.id"
            class="flex items-center justify-between border-b pb-2 last:border-0"
          >
            <div>
              <p class="font-medium flex items-center gap-1.5">
                {{ trx.deskripsi || '(Tanpa deskripsi)' }}
                <span
                  v-if="getSpendingLabel(trx, trxStore.transactions)"
                  :class="['text-xs font-normal', getSpendingLabel(trx, trxStore.transactions)!.colorClass]"
                >
                  {{ getSpendingLabel(trx, trxStore.transactions)!.emoji }}
                  {{ getSpendingLabel(trx, trxStore.transactions)!.text }}
                </span>
              </p>
              <p class="text-sm text-muted-foreground">{{ formatTanggal(trx.tanggal) }}</p>
            </div>
            <p
              class="font-mono font-medium tabular-nums"
              :class="{
                'text-green-600': trx.tipe === 'income',
                'text-red-600': trx.tipe === 'expense',
              }"
            >
              {{ trx.tipe === 'income' ? '+' : trx.tipe === 'expense' ? '-' : '' }}
              {{ formatRupiah(trx.jumlah) }}
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  </div>
</template>