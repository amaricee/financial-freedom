<script setup lang="ts">
import { RouterLink } from 'vue-router'
</script>

<template>
  <div class="min-h-screen bg-background">
    <nav class="border-b px-6 py-3 flex gap-4">
      <RouterLink to="/" class="font-medium hover:underline">Dashboard</RouterLink>
      <RouterLink to="/accounts" class="font-medium hover:underline">Akun</RouterLink>
      <RouterLink to="/transactions" class="font-medium hover:underline">Transaksi</RouterLink>
    </nav>
    <router-view />
  </div>
</template>