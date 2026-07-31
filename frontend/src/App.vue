<script setup lang="ts">
import AppSidebar from '@/components/AppSidebar.vue'
import AppBreadcrumb from '@/components/AppBreadcrumb.vue'
import { SidebarProvider, SidebarTrigger } from '@/components/ui/sidebar'
import { Separator } from '@/components/ui/separator'
import { Toaster } from '@/components/ui/sonner'
</script>

<template>
  
  <SidebarProvider>
    <AppSidebar />
    <main class="flex-1 min-w-0">
      <header class="flex items-center gap-2 border-b px-4 py-3">
        <SidebarTrigger />
        <Separator orientation="vertical" class="h-4" />
        <AppBreadcrumb />
      </header>
      <router-view />
    </main>
    <Toaster/>
  </SidebarProvider>
</template>