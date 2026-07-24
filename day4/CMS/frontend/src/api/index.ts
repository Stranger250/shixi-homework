const BASE_URL = ''

interface ApiResponse<T> {
  code: number
  msg: string
  data: T
}

interface CompanyInfo {
  name: string
  description: string
  history: string
  address: string
  email: string
  phone: string
}

interface NewsItem {
  id: number
  title: string
  content: string
  category: string
  publish_time: string
}

interface HomeData {
  jianjie: CompanyInfo
  news_list: NewsItem[]
}

async function request<T>(url: string, options?: RequestInit): Promise<ApiResponse<T>> {
  try {
    const res = await fetch(`${BASE_URL}${url}`, {
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      ...options,
    })
    if (!res.ok) {
      return { code: res.status, msg: '请求失败', data: null as T }
    }
    return res.json()
  } catch {
    return { code: 500, msg: '后端服务未启动，请先运行 Flask 服务器', data: null as T }
  }
}

export function fetchHome(): Promise<ApiResponse<HomeData>> {
  return request<HomeData>('/api/home')
}

export function fetchNewsList(): Promise<ApiResponse<NewsItem[]>> {
  return request<NewsItem[]>('/api/news')
}

export function fetchNewsDetail(id: number): Promise<ApiResponse<NewsItem>> {
  return request<NewsItem>(`/api/news/${id}`)
}

export function adminLogin(username: string, password: string): Promise<ApiResponse<null>> {
  return request<null>('/admin/login', {
    method: 'POST',
    body: JSON.stringify({ username, password }),
  })
}

export function createNews(data: {
  title: string
  content: string
  category: string
}): Promise<ApiResponse<NewsItem>> {
  return request<NewsItem>('/admin/news', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export function deleteNews(id: number): Promise<ApiResponse<null>> {
  return request<null>(`/admin/news/${id}`, {
    method: 'DELETE',
  })
}

export type { ApiResponse, CompanyInfo, NewsItem, HomeData }
