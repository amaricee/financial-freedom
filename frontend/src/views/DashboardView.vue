<script setup lang="ts">
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
</script>

<template>
  <div class="p-6 space-y-4">
    <h1 class="text-2xl font-bold">Dashboard</h1>
    <Card>
      <CardHeader>
        <CardTitle>Test shadcn-vue</CardTitle>
      </CardHeader>
      <CardContent>
        <p class="text-muted-foreground mb-4">Kalau ini kelihatan rapi dengan card border dan shadow, berarti setup berhasil.</p>
        <Button>Klik saya</Button>
      </CardContent>
    </Card>
  </div>
</template>