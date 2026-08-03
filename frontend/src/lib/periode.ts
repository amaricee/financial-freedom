/**
 * Hitung periode "bulan ini" versi siklus gajian: tanggal 25 s/d tanggal 24 bulan berikutnya.
 * Contoh: kalau referenceDate = 3 Agustus 2026, periode = 25 Juli - 24 Agustus 2026.
 *         kalau referenceDate = 28 Agustus 2026, periode = 25 Agustus - 24 September 2026.
 */
export function getPeriodeGajian(referenceDate: Date, tanggalGajian = 25) {
  const tanggal = referenceDate.getDate()
  let startMonth = referenceDate.getMonth()
  let startYear = referenceDate.getFullYear()

  if (tanggal < tanggalGajian) {
    startMonth -= 1
    if (startMonth < 0) {
      startMonth = 11
      startYear -= 1
    }
  }

  const start = new Date(startYear, startMonth, tanggalGajian)
  const end = new Date(startYear, startMonth + 1, tanggalGajian - 1, 23, 59, 59)
  return { start, end }
}

/** Generate array tiap hari dari start s/d end (inklusif), buat sumbu-X chart harian. */
export function getDaysInRange(start: Date, end: Date) {
  const days: { key: string; label: string }[] = []
  const cursor = new Date(start)
  while (cursor <= end) {
    days.push({
      key: cursor.toISOString().slice(0, 10),
      label: cursor.toLocaleDateString('id-ID', { day: 'numeric', month: 'short' }),
    })
    cursor.setDate(cursor.getDate() + 1)
  }
  return days
}