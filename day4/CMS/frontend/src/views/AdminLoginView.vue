<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { adminLogin } from '@/api'

const router = useRouter()
const username = ref('')
const password = ref('')
const errorMsg = ref('')
const loading = ref(false)

async function handleLogin() {
  errorMsg.value = ''
  if (!username.value || !password.value) {
    errorMsg.value = '请输入用户名和密码'
    return
  }
  loading.value = true
  try {
    const res = await adminLogin(username.value, password.value)
    if (res.code === 200) {
      router.push('/admin')
    } else {
      errorMsg.value = res.msg || '登录失败'
    }
  } catch {
    errorMsg.value = '网络错误，请稍后重试'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-[calc(100vh-12rem)] flex items-center justify-center px-6">
    <div class="w-full max-w-md">
      <div class="text-center mb-8">
        <div class="w-16 h-16 rounded-2xl bg-gradient-to-br from-primary-500 to-accent-purple flex items-center justify-center font-bold text-white text-2xl mx-auto mb-4 shadow-xl shadow-primary-500/20">
          A9
        </div>
        <h1 class="text-2xl font-bold text-white">管理后台登录</h1>
        <p class="text-dark-400 text-sm mt-2">请输入管理员账号密码</p>
      </div>

      <form class="card p-8 space-y-5" @submit.prevent="handleLogin">
        <div>
          <label class="block text-xs font-medium text-dark-300 mb-1.5">用户名</label>
          <input
            v-model="username"
            type="text"
            class="input-field"
            placeholder="请输入用户名"
            autocomplete="username"
          />
        </div>
        <div>
          <label class="block text-xs font-medium text-dark-300 mb-1.5">密码</label>
          <input
            v-model="password"
            type="password"
            class="input-field"
            placeholder="请输入密码"
            autocomplete="current-password"
          />
        </div>

        <div v-if="errorMsg" class="px-4 py-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm">
          {{ errorMsg }}
        </div>

        <button
          type="submit"
          :disabled="loading"
          class="btn-primary w-full"
        >
          {{ loading ? '登录中...' : '登录' }}
        </button>

        <p class="text-center text-xs text-dark-500">
          默认账号: admin / admin123
        </p>
      </form>
    </div>
  </div>
</template>
