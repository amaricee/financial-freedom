<script setup lang="ts">
import { computed } from 'vue'
import { Doughnut } from 'vue-chartjs'
import { Chart as ChartJS, Title, Tooltip, Legend, ArcElement } from 'chart.js'
import type { Transaction, Category } from '@/types'

ChartJS.register(Title, Tooltip, Legend, ArcElement)

const props = defineProps<{
  transactions: Transaction[]
  categories: Category[]
}>()

const palette = [
  '#dc2626',
  '#ea580c',
  '#d97706',
  '#65a30d',
  '#0d9488',
  '#0284c7',
  '#4f46e5',
  '#9333ea',
  '#db2777',
  '#78716c',
]

const now = new Date()
const bulanIni = now.getMonth() + 1
const tahunIni = now.getFullYear()

const breakdown = computed(() => {
  const expenseThisMonth = props.transactions.filter((t) => {
    const d = new Date(t.tanggal)
    return t.tipe === 'expense' && d.getMonth() + 1 === bulanIni && d.getFullYear() === tahunIni
  })

  const map = new Map<string, number>()
  for (const trx of expenseThisMonth) {
    const catName = props.categories.find((c) => c.id === trx.category_id)?.nama ?? 'Lainnya'
    map.set(catName, (map.get(catName) ?? 0) + Number(trx.jumlah))
  }

  return [...map.entries()]
    .sort((a, b) => b[1] - a[1])
    .map(([nama, total], i) => ({ nama, total, color: palette[i % palette.length] }))
})

const chartData = computed(() => ({
  labels: breakdown.value.map((b) => b.nama),
  datasets: [
    {
      data: breakdown.value.map((b) => b.total),
      backgroundColor: breakdown.value.map((b) => b.color),
      borderWidth: 0,
    },
  ],
}))

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'right' as const,
      labels: {
        boxWidth: 12,
        font: { size: 12 },
      },
    },
  },
}
</script>

<template>
  <div class="h-72">
    <Doughnut v-if="breakdown.length > 0" :data="chartData" :options="chartOptions" />
    <div v-else class="h-full flex items-center justify-center text-sm text-muted-foreground">
      Belum ada pengeluaran bulan ini
    </div>
  </div>
</template>