import { toast } from 'vue-sonner'
import type { Transaction } from '@/types'

interface SpendingCheckParams {
  newTransaction: {
    category_id: number | null
    jumlah: string
    tipe: string
  }
  categoryName: string
  allTransactions: Transaction[]
}

export function checkAndNotifySpending({
  newTransaction,
  categoryName,
  allTransactions,
}: SpendingCheckParams) {
  if (newTransaction.tipe !== 'expense' || !newTransaction.category_id) return

  const jumlahBaru = Number(newTransaction.jumlah)

  const historis = allTransactions.filter(
    (t) => t.tipe === 'expense' && t.category_id === newTransaction.category_id,
  )

  if (historis.length < 3) return

  const rataRata = historis.reduce((sum, t) => sum + Number(t.jumlah), 0) / historis.length
  const rasio = jumlahBaru / rataRata

  if (rasio >= 3) {
    toast.error(`Wah, boros banget hari ini! 🔥💸`, {
      description: `Pengeluaran "${categoryName}" kamu ${rasio.toFixed(1)}x lipat dari rata-rata biasanya. Dompet nangis 😭`,
    })
  } else if (rasio >= 1.75) {
    toast.error(`Hari ini kamu boros nih! 😅`, {
      description: `Pengeluaran "${categoryName}" lebih tinggi dari biasanya (${rasio.toFixed(1)}x rata-rata). Santai aja, sesekali boleh 😌`,
    })
  } else if (rasio <= 0.5) {
    toast.success(`Hemat banget hari ini! 👏`, {
      description: `Pengeluaran "${categoryName}" jauh di bawah rata-rata biasanya. Mantap! 💪`,
    })
  }
}

export interface SpendingLabel {
  text: string
  emoji: string
  colorClass: string
}

/**
 * Versi non-toast: cuma return label buat ditampilin inline di UI (misal di list transaksi).
 * Dihitung berdasarkan histori kategori yang sama, TERMASUK transaksi itu sendiri sebagai bagian histori.
 */
export function getSpendingLabel(
  transaction: Transaction,
  allTransactions: Transaction[],
): SpendingLabel | null {
  if (transaction.tipe !== 'expense' || !transaction.category_id) return null

  const historis = allTransactions.filter(
    (t) =>
      t.tipe === 'expense' && t.category_id === transaction.category_id && t.id !== transaction.id,
  )

  if (historis.length < 3) return null

  const rataRata = historis.reduce((sum, t) => sum + Number(t.jumlah), 0) / historis.length
  const rasio = Number(transaction.jumlah) / rataRata

  if (rasio >= 3) {
    return { text: 'Boros banget', emoji: '🔥', colorClass: 'text-red-600' }
  }
  if (rasio >= 1.75) {
    return { text: 'Agak boros', emoji: '😅', colorClass: 'text-orange-600' }
  }
  if (rasio <= 0.5) {
    return { text: 'Hemat', emoji: '👏', colorClass: 'text-green-600' }
  }
  return null
}