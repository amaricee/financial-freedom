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

// "This month" based on payday cycle: the 25th through the 24th of the next month
const { start: periodStart, end: periodEnd } = getPeriodeGajian(new Date())

function formatPeriodLabel(d: Date) {
  return d.toLocaleDateString('en-US', { day: 'numeric', month: 'short' })
}

const totalBalance = computed(() =>
  accountsStore.accounts.reduce((sum, acc) => sum + Number(acc.saldo_current), 0),
)

const transactionsThisPeriod = computed(() =>
  trxStore.transactions.filter((t) => {
    const d = new Date(t.tanggal)
    return d >= periodStart && d <= periodEnd
  }),
)

const totalIncomeThisPeriod = computed(() =>
  transactionsThisPeriod.value
    .filter((t) => t.tipe === 'income')
    .reduce((sum, t) => sum + Number(t.jumlah), 0),
)

const totalExpenseThisPeriod = computed(() =>
  transactionsThisPeriod.value
    .filter((t) => t.tipe === 'expense')
    .reduce((sum, t) => sum + Number(t.jumlah), 0),
)

const recentTransactions = computed(() =>
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
    <h1 class="text-2xl font-bold">Dashboard</h1>

    <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
      <Card>
        <CardHeader>
          <CardTitle class="text-sm font-medium text-muted-foreground">Total Balance</CardTitle>
        </CardHeader>
        <CardContent>
          <p class="text-2xl font-bold">{{ formatRupiah(totalBalance) }}</p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle class="text-sm font-medium text-muted-foreground">
            Income This Period
            <span class="block text-xs font-normal mt-0.5">
              {{ formatPeriodLabel(periodStart) }} - {{ formatPeriodLabel(periodEnd) }}
            </span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p class="text-2xl font-bold text-green-600">{{ formatRupiah(totalIncomeThisPeriod) }}</p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle class="text-sm font-medium text-muted-foreground">
            Expenses This Period
            <span class="block text-xs font-normal mt-0.5">
              {{ formatPeriodLabel(periodStart) }} - {{ formatPeriodLabel(periodEnd) }}
            </span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p class="text-2xl font-bold text-red-600">{{ formatRupiah(totalExpenseThisPeriod) }}</p>
        </CardContent>
      </Card>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
      <Card>
        <CardHeader>
          <CardTitle>
            Income vs Expenses
            <span class="block text-xs font-normal text-muted-foreground mt-0.5">
              Period {{ formatPeriodLabel(periodStart) }} - {{ formatPeriodLabel(periodEnd) }}
            </span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <IncomeExpenseChart
            :transactions="trxStore.transactions"
            :periode-start="periodStart"
            :periode-end="periodEnd"
          />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>
            Expenses by Category
            <span class="block text-xs font-normal text-muted-foreground mt-0.5">
              Period {{ formatPeriodLabel(periodStart) }} - {{ formatPeriodLabel(periodEnd) }}
            </span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <ExpenseByCategoryChart
            :transactions="trxStore.transactions"
            :categories="categoriesStore.categories"
            :periode-start="periodStart"
            :periode-end="periodEnd"
          />
        </CardContent>
      </Card>
    </div>

    <Card>
      <CardHeader>
        <CardTitle>Recent Transactions</CardTitle>
      </CardHeader>
      <CardContent>
        <div v-if="recentTransactions.length === 0" class="text-muted-foreground text-sm">
          No transactions yet
        </div>
        <div v-else class="space-y-3">
          <div
            v-for="trx in recentTransactions"
            :key="trx.id"
            class="flex items-center justify-between border-b pb-2 last:border-0"
          >
            <div>
              <p class="font-medium flex items-center gap-1.5">
                {{ trx.deskripsi || '(No description)' }}
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