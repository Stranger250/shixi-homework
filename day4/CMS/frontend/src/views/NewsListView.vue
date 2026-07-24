<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { fetchNewsList } from '@/api'
import type { NewsItem } from '@/api'
import NewsCard from '@/components/NewsCard.vue'

const newsList = ref<NewsItem[]>([])
const loading = ref(true)

onMounted(async () => {
  try {
    const res = await fetchNewsList()
    if (res.code === 200) {
      newsList.value = res.data
    }
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="max-w-4xl mx-auto px-6 py-12">
    <div class="mb-10">
      <h1 class="text-3xl font-bold text-white mb-2">新闻动态</h1>
      <p class="text-dark-400 text-sm">了解阿里九九的最新资讯与动态</p>
    </div>

    <div v-if="loading" class="space-y-4">
      <div v-for="i in 5" :key="i" class="card p-6 animate-pulse">
        <div class="h-4 bg-dark-700 rounded w-16 mb-3" />
        <div class="h-5 bg-dark-700 rounded w-2/3 mb-2" />
        <div class="h-4 bg-dark-700 rounded w-full" />
      </div>
    </div>

    <div v-else-if="newsList.length === 0" class="card p-12 text-center text-dark-400">
      <p>暂无新闻</p>
    </div>

    <div v-else class="space-y-4">
      <NewsCard v-for="n in newsList" :key="n.id" :news="n" compact />
    </div>
  </div>
</template>
