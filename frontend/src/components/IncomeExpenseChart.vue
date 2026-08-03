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
import { getDaysInRange } from '@/lib/periode'

ChartJS.register(Title, Tooltip, Legend, LineElement, PointElement, CategoryScale, LinearScale)

const props = defineProps<{
  transactions: Transaction[]
  periodeStart: Date
  periodeEnd: Date
}>()

const daysInPeriode = computed(() => getDaysInRange(props.periodeStart, props.periodeEnd))

const chartData = computed(() => {
  const incomeData = daysInPeriode.value.map(({ key }) =>
    props.transactions
      .filter((t) => t.tipe === 'income' && t.tanggal === key)
      .reduce((sum, t) => sum + Number(t.jumlah), 0),
  )

  const expenseData = daysInPeriode.value.map(({ key }) =>
    props.transactions
      .filter((t) => t.tipe === 'expense' && t.tanggal === key)
      .reduce((sum, t) => sum + Number(t.jumlah), 0),
  )

  return {
    labels: daysInPeriode.value.map((d) => d.label),
    datasets: [
      {
        label: 'Pemasukan',
        data: incomeData,
        borderColor: '#16a34a',
        backgroundColor: '#16a34a',
        tension: 0,
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
        maxTicksLimit: 8,
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