<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { createNews, deleteNews, fetchNewsList } from '@/api'
import type { NewsItem } from '@/api'

const router = useRouter()

const title = ref('')
const content = ref('')
const category = ref('')
const msg = ref('')
const msgType = ref<'success' | 'error'>('success')
const loading = ref(false)

const newsList = ref<NewsItem[]>([])
const listLoading = ref(true)

async function loadNews() {
  listLoading.value = true
  try {
    const res = await fetchNewsList()
    if (res.code === 200) newsList.value = res.data
  } finally {
    listLoading.value = false
  }
}

async function handlePublish() {
  if (!title.value || !content.value || !category.value) {
    msg.value = '标题、内容和分类不能为空'
    msgType.value = 'error'
    return
  }
  loading.value = true
  try {
    const res = await createNews({
      title: title.value,
      content: content.value,
      category: category.value,
    })
    if (res.code === 200) {
      msg.value = '发布成功！'
      msgType.value = 'success'
      title.value = ''
      content.value = ''
      category.value = ''
      await loadNews()
    } else {
      msg.value = res.msg || '发布失败'
      msgType.value = 'error'
    }
  } catch {
    msg.value = '网络错误，请登录后再试'
    msgType.value = 'error'
  } finally {
    loading.value = false
  }
}

async function handleDelete(id: number, newsTitle: string) {
  if (!confirm(`确定删除新闻「${newsTitle}」吗？`)) return
  try {
    const res = await deleteNews(id)
    if (res.code === 200) {
      msg.value = '删除成功'
      msgType.value = 'success'
      await loadNews()
    } else {
      msg.value = res.msg || '删除失败'
      msgType.value = 'error'
    }
  } catch {
    msg.value = '请登录后再试'
    msgType.value = 'error'
  }
}

function formatDate(iso: string) {
  if (!iso) return ''
  return iso.replace('T', ' ').substring(0, 19)
}

function handleLogout() {
  router.push('/')
}

onMounted(async () => {
  // 通过尝试获取新闻列表来判断是否已登录
  try {
    const res = await fetchNewsList()
    if (res.code === 200) {
      await loadNews()
      return
    }
  } catch { /* ignore */ }
  // 未登录则跳转到登录页
  router.push('/admin/login')
})
</script>

<template>
  <div class="max-w-6xl mx-auto px-6 py-10">
    <!-- Header -->
    <div class="flex items-center justify-between mb-8">
      <div>
        <h1 class="text-2xl font-bold text-white">管理后台</h1>
        <p class="text-dark-400 text-sm mt-1">发布和管理新闻内容</p>
      </div>
      <div class="flex items-center gap-3">
        <router-link to="/" class="text-sm text-dark-400 hover:text-white transition-colors">返回首页</router-link>
        <button @click="handleLogout" class="px-4 py-1.5 rounded-lg border border-dark-600 text-dark-300 hover:text-white hover:border-red-500/50 text-sm transition-all">
          退出登录
        </button>
      </div>
    </div>

    <!-- Message Toast -->
    <div v-if="msg" :class="msgType === 'success' ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400' : 'bg-red-500/10 border-red-500/20 text-red-400'"
         class="px-4 py-3 rounded-lg border text-sm mb-6 flex items-center justify-between">
      <span>{{ msg }}</span>
      <button @click="msg = ''" class="ml-4 opacity-60 hover:opacity-100">&times;</button>
    </div>

    <div class="grid lg:grid-cols-5 gap-8">
      <!-- Publish Form -->
      <div class="lg:col-span-2">
        <div class="card p-6 sticky top-24">
          <h2 class="text-lg font-semibold text-white mb-5 flex items-center gap-2">
            <svg class="w-5 h-5 text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            发布新闻
          </h2>
          <form class="space-y-4" @submit.prevent="handlePublish">
            <div>
              <label class="block text-xs font-medium text-dark-300 mb-1.5">标题</label>
              <input v-model="title" class="input-field" placeholder="请输入新闻标题" />
            </div>
            <div>
              <label class="block text-xs font-medium text-dark-300 mb-1.5">分类</label>
              <select v-model="category" class="input-field appearance-none cursor-pointer">
                <option value="" disabled>请选择分类</option>
                <option value="公司动态">公司动态</option>
                <option value="产品发布">产品发布</option>
                <option value="技术分享">技术分享</option>
                <option value="行业资讯">行业资讯</option>
                <option value="企业文化">企业文化</option>
              </select>
            </div>
            <div>
              <label class="block text-xs font-medium text-dark-300 mb-1.5">内容</label>
              <textarea v-model="content" rows="6" class="input-field resize-none" placeholder="请输入新闻内容" />
            </div>
            <button type="submit" :disabled="loading" class="btn-primary w-full">
              {{ loading ? '发布中...' : '立即发布' }}
            </button>
          </form>
        </div>
      </div>

      <!-- News Management List -->
      <div class="lg:col-span-3">
        <div class="card p-6">
          <h2 class="text-lg font-semibold text-white mb-5 flex items-center gap-2">
            <svg class="w-5 h-5 text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
            新闻管理 ({{ newsList.length }})
          </h2>

          <div v-if="listLoading" class="space-y-3">
            <div v-for="i in 4" :key="i" class="animate-pulse flex items-center gap-4 p-3">
              <div class="h-4 bg-dark-700 rounded flex-1" />
              <div class="h-4 bg-dark-700 rounded w-20" />
              <div class="h-4 bg-dark-700 rounded w-12" />
            </div>
          </div>

          <div v-else-if="newsList.length === 0" class="py-12 text-center text-dark-500 text-sm">
            暂无新闻，请发布第一篇新闻
          </div>

          <div v-else class="divide-y divide-dark-700/50">
            <div
              v-for="n in newsList" :key="n.id"
              class="flex items-center gap-4 py-3 px-2 hover:bg-dark-800/50 rounded-lg transition-colors group"
            >
              <div class="flex-1 min-w-0">
                <p class="text-sm text-white truncate font-medium">{{ n.title }}</p>
                <div class="flex items-center gap-2 mt-1">
                  <span class="text-xs px-2 py-0.5 rounded bg-primary-500/10 text-primary-400">{{ n.category }}</span>
                  <span class="text-xs text-dark-500 font-mono">{{ formatDate(n.publish_time) }}</span>
                </div>
              </div>
              <router-link :to="`/news/${n.id}`" class="text-xs text-dark-500 hover:text-primary-400 transition-colors shrink-0">查看</router-link>
              <button
                @click="handleDelete(n.id, n.title)"
                class="btn-danger text-xs !px-3 !py-1.5 shrink-0 opacity-0 group-hover:opacity-100 transition-opacity"
              >
                删除
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
