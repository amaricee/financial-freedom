<script setup lang="ts">
import { computed } from 'vue'
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  LineElement,
  PointElement,
  CategoryScale,
  LinearScale,
} from 'chart.js'
import type { Transaction } from '@/types'

ChartJS.register(Title, Tooltip, Legend, LineElement, PointElement, CategoryScale, LinearScale)

const props = defineProps<{
  transactions: Transaction[]
}>()

function toDateKey(d: Date) {
  return d.toISOString().slice(0, 10)
}

// 30 hari terakhir (termasuk hari ini)
const last30Days = computed(() => {
  const today = new Date()
  const days: { key: string; label: string }[] = []
  for (let i = 29; i >= 0; i--) {
    const d = new Date(today)
    d.setDate(d.getDate() - i)
    days.push({
      key: toDateKey(d),
      label: d.toLocaleDateString('id-ID', { day: 'numeric', month: 'short' }),
    })
  }
  return days
})

const chartData = computed(() => {
  const incomeData = last30Days.value.map(({ key }) =>
    props.transactions
      .filter((t) => t.tipe === 'income' && t.tanggal === key)
      .reduce((sum, t) => sum + Number(t.jumlah), 0),
  )

  const expenseData = last30Days.value.map(({ key }) =>
    props.transactions
      .filter((t) => t.tipe === 'expense' && t.tanggal === key)
      .reduce((sum, t) => sum + Number(t.jumlah), 0),
  )

  return {
    labels: last30Days.value.map((d) => d.label),
    datasets: [
      {
        label: 'Pemasukan',
        data: incomeData,
        borderColor: '#16a34a',
        backgroundColor: '#16a34a',
        tension: 0, // garis tajam, gak dihaluskan
        fill: false,
        borderWidth: 1.5,
        pointRadius: 0,
        pointHoverRadius: 4,
      },
      {
        label: 'Pengeluaran',
        data: expenseData,
        borderColor: '#dc2626',
        backgroundColor: '#dc2626',
        tension: 0,
        fill: false,
        borderWidth: 1.5,
        pointRadius: 0,
        pointHoverRadius: 4,
      },
    ],
  }
})

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  interaction: {
    mode: 'index' as const,
    intersect: false,
  },
  plugins: {
    legend: {
      position: 'bottom' as const,
    },
  },
  scales: {
    x: {
      ticks: {
        maxTicksLimit: 8, // biar label tanggal gak numpuk
      },
      grid: {
        display: false,
      },
    },
    y: {
      beginAtZero: true,
      ticks: {
        callback: (value: number | string) => {
          const num = Number(value)
          if (num >= 1_000_000) return `${num / 1_000_000}jt`
          if (num >= 1_000) return `${num / 1_000}rb`
          return num
        },
      },
    },
  },
}
</script>

<template>
  <div class="h-72">
    <Line :data="chartData" :options="chartOptions" />
  </div>
</template>