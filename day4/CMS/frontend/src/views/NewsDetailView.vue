<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { fetchNewsDetail } from '@/api'
import type { NewsItem } from '@/api'

const route = useRoute()
const news = ref<NewsItem | null>(null)
const loading = ref(true)
const notFound = ref(false)

function formatDate(iso: string): string {
  if (!iso) return ''
  return iso.replace('T', ' ').substring(0, 19)
}

onMounted(async () => {
  try {
    const id = Number(route.params.id)
    const res = await fetchNewsDetail(id)
    if (res.code === 200) {
      news.value = res.data
    } else {
      notFound.value = true
    }
  } catch {
    notFound.value = true
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="max-w-3xl mx-auto px-6 py-12">
    <div v-if="loading" class="card p-8 animate-pulse space-y-4">
      <div class="h-4 bg-dark-700 rounded w-20" />
      <div class="h-8 bg-dark-700 rounded w-3/4" />
      <div class="h-4 bg-dark-700 rounded w-1/3" />
      <div class="h-32 bg-dark-700 rounded w-full mt-6" />
    </div>

    <div v-else-if="notFound" class="card p-12 text-center">
      <div class="text-5xl mb-4">404</div>
      <p class="text-dark-400 text-lg mb-6">新闻不存在或已被删除</p>
      <router-link to="/news" class="btn-primary inline-block">返回新闻列表</router-link>
    </div>

    <article v-else class="card p-8 md:p-12">
      <router-link to="/news" class="inline-flex items-center gap-1 text-sm text-dark-400 hover:text-primary-400 transition-colors mb-6">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
        返回列表
      </router-link>

      <div class="flex items-center gap-3 mb-4">
        <span class="px-3 py-1 rounded-full text-xs font-medium bg-primary-500/10 text-primary-400 border border-primary-500/20">
          {{ news.category }}
        </span>
        <span class="text-xs text-dark-500 font-mono">{{ formatDate(news.publish_time) }}</span>
      </div>

      <h1 class="text-2xl md:text-3xl font-bold text-white mb-8 leading-relaxed">
        {{ news.title }}
      </h1>

      <div class="prose prose-invert max-w-none">
        <p class="text-dark-200 leading-relaxed whitespace-pre-wrap text-base">
          {{ news.content }}
        </p>
      </div>
    </article>
  </div>
</template>
