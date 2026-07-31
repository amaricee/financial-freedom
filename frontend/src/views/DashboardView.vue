<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useAccountsStore } from '@/stores/accounts'
import { useTransactionsStore } from '@/stores/transactions'
import { formatRupiah, formatTanggal } from '@/lib/format'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { useCategoriesStore } from '@/stores/categories'
import IncomeExpenseChart from '@/components/IncomeExpenseChart.vue'
import ExpenseByCategoryChart from '@/components/ExpenseByCategoryChart.vue'
import { getSpendingLabel } from '@/lib/spending-alert'

const accountsStore = useAccountsStore()
const trxStore = useTransactionsStore()
const categoriesStore = useCategoriesStore()

const totalSaldo = computed(() =>
  accountsStore.accounts.reduce((sum, acc) => sum + Number(acc.saldo_current), 0),
)

const now = new Date()
const bulanIni = now.getMonth() + 1
const tahunIni = now.getFullYear()

const transaksiBulanIni = computed(() =>
  trxStore.transactions.filter((t) => {
    const d = new Date(t.tanggal)
    return d.getMonth() + 1 === bulanIni && d.getFullYear() === tahunIni
  }),
)

const totalIncomeBulanIni = computed(() =>
  transaksiBulanIni.value
    .filter((t) => t.tipe === 'income')
    .reduce((sum, t) => sum + Number(t.jumlah), 0),
)

const totalExpenseBulanIni = computed(() =>
  transaksiBulanIni.value
    .filter((t) => t.tipe === 'expense')
    .reduce((sum, t) => sum + Number(t.jumlah), 0),
)

const transaksiTerbaru = computed(() =>
  [...trxStore.transactions]
    .sort((a, b) => new Date(b.tanggal).getTime() - new Date(a.tanggal).getTime())
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
    <h1 class="text-2xl font-bold">Dashboard</h1>

    <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
      <Card>
        <CardHeader>
          <CardTitle class="text-sm font-medium text-muted-foreground">Total Saldo</CardTitle>
        </CardHeader>
        <CardContent>
          <p class="text-2xl font-bold">{{ formatRupiah(totalSaldo) }}</p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle class="text-sm font-medium text-muted-foreground">
            Pemasukan Bulan Ini
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p class="text-2xl font-bold text-green-600">{{ formatRupiah(totalIncomeBulanIni) }}</p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle class="text-sm font-medium text-muted-foreground">
            Pengeluaran Bulan Ini
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p class="text-2xl font-bold text-red-600">{{ formatRupiah(totalExpenseBulanIni) }}</p>
        </CardContent>
      </Card>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
      <Card>
        <CardHeader>
          <CardTitle>Pemasukan vs Pengeluaran (30 Hari Terakhir)</CardTitle>
        </CardHeader>
        <CardContent>
          <IncomeExpenseChart :transactions="trxStore.transactions" />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Pengeluaran per Kategori (Bulan Ini)</CardTitle>
        </CardHeader>
        <CardContent>
          <ExpenseByCategoryChart
            :transactions="trxStore.transactions"
            :categories="categoriesStore.categories"
          />
        </CardContent>
      </Card>
    </div>

    <Card>
      <CardHeader>
        <CardTitle>Transaksi Terbaru</CardTitle>
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
              class="font-medium"
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