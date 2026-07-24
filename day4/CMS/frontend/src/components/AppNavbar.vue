<script setup lang="ts">
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()
const isMenuOpen = ref(false)

function isActive(path: string) {
  return route.path === path
}

function linkClass(path: string) {
  return isActive(path)
    ? 'text-primary-400 font-medium'
    : 'text-dark-300 hover:text-white transition-colors'
}
</script>

<template>
  <nav class="sticky top-0 z-50 bg-dark-950/80 backdrop-blur-md border-b border-dark-800/50">
    <div class="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
      <!-- Logo -->
      <router-link to="/" class="flex items-center gap-3 group">
        <div class="w-9 h-9 rounded-lg bg-gradient-to-br from-primary-500 to-accent-purple flex items-center justify-center font-bold text-white text-sm shadow-lg shadow-primary-500/20">
          A9
        </div>
        <span class="text-lg font-bold tracking-wide text-white group-hover:text-primary-400 transition-colors">
          阿里九九
        </span>
      </router-link>

      <!-- Desktop Links -->
      <div class="hidden md:flex items-center gap-8 text-sm">
        <router-link to="/" :class="linkClass('/')">首页</router-link>
        <router-link to="/news" :class="linkClass('/news')">新闻动态</router-link>
        <router-link
          to="/admin/login"
          class="px-4 py-1.5 rounded-full border border-dark-600 text-dark-300 hover:text-white hover:border-primary-500/50 transition-all text-xs"
        >
          管理后台
        </router-link>
      </div>

      <!-- Mobile Toggle -->
      <button class="md:hidden text-dark-300" @click="isMenuOpen = !isMenuOpen">
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path v-if="!isMenuOpen" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
          <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 6l12 12M18 6L6 18" />
        </svg>
      </button>
    </div>

    <!-- Mobile Menu -->
    <div v-if="isMenuOpen" class="md:hidden border-t border-dark-800/50 bg-dark-900/90 backdrop-blur-md">
      <div class="px-6 py-4 flex flex-col gap-4 text-sm">
        <router-link to="/" class="text-dark-300 hover:text-white" @click="isMenuOpen = false">首页</router-link>
        <router-link to="/news" class="text-dark-300 hover:text-white" @click="isMenuOpen = false">新闻动态</router-link>
        <router-link to="/admin/login" class="text-dark-300 hover:text-white" @click="isMenuOpen = false">管理后台</router-link>
      </div>
    </div>
  </nav>
</template>
