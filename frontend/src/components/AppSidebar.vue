<script setup lang="ts">
import { RouterLink, useRoute } from 'vue-router'
import { LayoutDashboard, Wallet, ArrowLeftRight, PiggyBank, HandCoins, Tags, Target } from 'lucide-vue-next'
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarHeader,
} from '@/components/ui/sidebar'

const route = useRoute()

const menuItems = [
  { title: 'Dashboard', url: '/', icon: LayoutDashboard },
  { title: 'Akun', url: '/accounts', icon: Wallet },
  { title: 'Transaksi', url: '/transactions', icon: ArrowLeftRight },
  { title: 'Kategori', url: '/categories', icon: Tags },
  { title: 'Budget', url: '/budgets', icon: Target },
  { title: 'Savings Goals', url: '/savings-goals', icon: PiggyBank },
  { title: 'Hutang/Piutang', url: '/debts', icon: HandCoins },
]
</script>

<template>
  <Sidebar>
    <SidebarHeader class="px-4 py-3">
      <p class="font-bold text-lg">Finance App</p>
    </SidebarHeader>
    <SidebarContent>
      <SidebarGroup>
        <SidebarGroupLabel>Menu</SidebarGroupLabel>
        <SidebarGroupContent>
          <SidebarMenu>
            <SidebarMenuItem v-for="item in menuItems" :key="item.title">
              <SidebarMenuButton as-child :is-active="route.path === item.url">
                <RouterLink :to="item.url">
                  <component :is="item.icon" />
                  <span>{{ item.title }}</span>
                </RouterLink>
              </SidebarMenuButton>
            </SidebarMenuItem>
          </SidebarMenu>
        </SidebarGroupContent>
      </SidebarGroup>
    </SidebarContent>
  </Sidebar>
</template>