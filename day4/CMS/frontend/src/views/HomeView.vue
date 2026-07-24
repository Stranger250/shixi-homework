<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { fetchHome } from '@/api'
import type { CompanyInfo, NewsItem } from '@/api'
import NewsCard from '@/components/NewsCard.vue'

const company = ref<CompanyInfo | null>(null)
const newsList = ref<NewsItem[]>([])
const loading = ref(true)

onMounted(async () => {
  try {
    const res = await fetchHome()
    if (res.code === 200) {
      company.value = res.data.jianjie
      newsList.value = res.data.news_list
    }
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div>
    <!-- Hero -->
    <section class="relative py-20 px-6 overflow-hidden">
      <div class="absolute inset-0 bg-gradient-to-b from-primary-900/20 via-transparent to-transparent pointer-events-none" />
      <div class="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[400px] bg-primary-500/5 blur-[120px] rounded-full pointer-events-none" />
      <div class="max-w-6xl mx-auto text-center relative z-10">
        <div class="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-primary-500/20 bg-primary-500/5 text-primary-400 text-xs font-medium mb-6">
          <span class="w-1.5 h-1.5 rounded-full bg-primary-400 animate-pulse" />
          阿里九九科技官方平台
        </div>
        <h1 class="text-4xl md:text-5xl lg:text-6xl font-black tracking-tight text-white mb-6">
          <span class="bg-gradient-to-r from-primary-400 via-primary-300 to-accent-purple bg-clip-text text-transparent">
            {{ company?.name || '加载中...' }}
          </span>
        </h1>
        <p class="text-lg text-dark-300 max-w-2xl mx-auto leading-relaxed">
          {{ company?.description }}
        </p>
      </div>
    </section>

    <!-- Company Info -->
    <section v-if="company" class="max-w-6xl mx-auto px-6 pb-12">
      <div class="card p-8">
        <h2 class="text-xl font-bold text-white mb-6 flex items-center gap-2">
          <svg class="w-5 h-5 text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
          </svg>
          公司简介
        </h2>
        <div class="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
          <div v-for="item in [
            { label: '创世时间', value: company.history, icon: 'M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z' },
            { label: '公司地址', value: company.address, icon: 'M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z' },
            { label: '电子邮箱', value: company.email, icon: 'M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z' },
            { label: '联系电话', value: company.phone, icon: 'M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z' },
          ]" :key="item.label" class="flex items-start gap-4 p-4 rounded-xl bg-dark-900/50 border border-dark-700/30">
            <div class="w-10 h-10 rounded-lg bg-primary-500/10 flex items-center justify-center flex-shrink-0">
              <svg class="w-5 h-5 text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" :d="item.icon" />
              </svg>
            </div>
            <div class="min-w-0">
              <p class="text-xs text-dark-400 mb-0.5">{{ item.label }}</p>
              <p class="text-sm text-dark-200 truncate">{{ item.value }}</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Latest News -->
    <section class="max-w-6xl mx-auto px-6 pb-20">
      <div class="flex items-center justify-between mb-8">
        <h2 class="text-xl font-bold text-white flex items-center gap-2">
          <svg class="w-5 h-5 text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
          </svg>
          最新动态
        </h2>
        <router-link to="/news" class="text-sm text-primary-400 hover:text-primary-300 transition-colors flex items-center gap-1">
          查看全部
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3" />
          </svg>
        </router-link>
      </div>

      <!-- Loading skeleton -->
      <div v-if="loading" class="grid md:grid-cols-3 gap-6">
        <div v-for="i in 3" :key="i" class="card p-6 animate-pulse">
          <div class="h-4 bg-dark-700 rounded w-20 mb-3" />
          <div class="h-5 bg-dark-700 rounded w-3/4 mb-2" />
          <div class="h-4 bg-dark-700 rounded w-full mb-4" />
          <div class="h-3 bg-dark-700 rounded w-1/2" />
        </div>
      </div>

      <!-- Empty -->
      <div v-else-if="newsList.length === 0" class="card p-12 text-center text-dark-400">
        <p>暂无新闻</p>
      </div>

      <!-- News Grid -->
      <div v-else class="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        <NewsCard v-for="n in newsList" :key="n.id" :news="n" />
      </div>
    </section>
  </div>
</template>
