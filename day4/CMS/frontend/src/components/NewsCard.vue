<script setup lang="ts">
import type { NewsItem } from '@/api'

defineProps<{
  news: NewsItem
  compact?: boolean
}>()

function formatDate(iso: string): string {
  if (!iso) return ''
  return iso.replace('T', ' ').substring(0, 19)
}
</script>

<template>
  <router-link :to="`/news/${news.id}`" class="card block p-6 group cursor-pointer">
    <div class="flex items-start justify-between gap-4">
      <div class="flex-1 min-w-0">
        <span class="inline-block px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary-500/10 text-primary-400 border border-primary-500/20 mb-3">
          {{ news.category }}
        </span>
        <h3 class="text-base font-semibold text-white group-hover:text-primary-400 transition-colors line-clamp-2">
          {{ news.title }}
        </h3>
        <p v-if="!compact" class="mt-2 text-sm text-dark-400 line-clamp-2">
          {{ news.content }}
        </p>
      </div>
    </div>
    <div class="mt-4 pt-4 border-t border-dark-700/50 flex items-center justify-between text-xs text-dark-500">
      <span class="font-mono">{{ formatDate(news.publish_time) }}</span>
      <span class="text-primary-500 group-hover:translate-x-1 transition-transform inline-flex items-center gap-1">
        阅读详情
        <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
        </svg>
      </span>
    </div>
  </router-link>
</template>
