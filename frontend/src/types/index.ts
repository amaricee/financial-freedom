// --- Account ---
export type AccountType = 'bank' | 'cash' | 'e_wallet' | 'investasi'

export interface Account {
  id: number
  nama: string
  tipe: AccountType
  saldo_awal: string // Decimal dari backend dikirim sebagai string
  currency: string
  created_at: string
  updated_at: string | null
}

export interface AccountWithBalance extends Account {
  saldo_current: string
}

export interface AccountCreatePayload {
  nama: string
  tipe: AccountType
  saldo_awal: string
  currency?: string
}

// --- Category ---
export type CategoryType = 'income' | 'expense'

export interface Category {
  id: number
  nama: string
  tipe: CategoryType
  parent_id: number | null
  icon: string | null
  color: string | null
  created_at: string
}

export interface CategoryTree extends Category {
  children: CategoryTree[]
}

export interface CategoryCreatePayload {
  nama: string
  tipe: CategoryType
  parent_id?: number | null
  icon?: string | null
  color?: string | null
}

// --- Transaction ---
export type TransactionType = 'income' | 'expense' | 'transfer'

export interface Transaction {
  id: number
  account_id: number
  category_id: number | null
  tipe: TransactionType
  jumlah: string
  tanggal: string
  deskripsi: string | null
  account_id_tujuan: number | null
  created_at: string
  updated_at: string | null
}

export interface TransactionCreatePayload {
  account_id: number
  category_id?: number | null
  tipe: TransactionType
  jumlah: string
  tanggal: string
  deskripsi?: string | null
  account_id_tujuan?: number | null
}

// --- Budget ---
export interface Budget {
  id: number
  category_id: number
  bulan: number
  tahun: number
  jumlah_budget: string
  created_at: string
  updated_at: string | null
}

export interface BudgetWithRealisasi extends Budget {
  realisasi: string
  sisa: string
  persentase: number
}

// --- Savings Goal ---
export interface SavingsGoal {
  id: number
  nama: string
  target_jumlah: string
  current_jumlah: string
  target_tanggal: string | null
  account_id: number | null
  created_at: string
  updated_at: string | null
}

// --- Debt ---
export type DebtType = 'hutang' | 'piutang'
export type DebtStatus = 'belum_lunas' | 'lunas'

export interface Debt {
  id: number
  tipe: DebtType
  nama_pihak: string
  jumlah_total: string
  jumlah_terbayar: string
  tanggal: string
  jatuh_tempo: string | null
  status: DebtStatus
  notes: string | null
  created_at: string
  updated_at: string | null
}