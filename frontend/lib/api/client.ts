import axios, { AxiosInstance, AxiosRequestConfig } from 'axios'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

class ApiClient {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 30000,
    })

    // Request interceptor - add auth token
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('auth_token')
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }
        return config
      },
      (error) => {
        return Promise.reject(error)
      }
    )

    // Response interceptor - handle errors
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response) {
          const { status, data } = error.response

          switch (status) {
            case 401:
              // Unauthorized - clear token and redirect to login
              localStorage.removeItem('auth_token')
              break
            case 403:
              console.error('Access forbidden')
              break
            case 404:
              console.error('Resource not found')
              break
            case 422:
              console.error('Validation error:', data)
              break
            case 429:
              console.error('Rate limit exceeded')
              break
            case 500:
              console.error('Server error')
              break
          }
        } else if (error.request) {
          console.error('Network error - no response received')
        }

        return Promise.reject(error)
      }
    )
  }

  async get<T = any>(url: string, config?: AxiosRequestConfig) {
    return this.client.get<T>(url, config)
  }

  async post<T = any>(url: string, data?: any, config?: AxiosRequestConfig) {
    return this.client.post<T>(url, data, config)
  }

  async put<T = any>(url: string, data?: any, config?: AxiosRequestConfig) {
    return this.client.put<T>(url, data, config)
  }

  async delete<T = any>(url: string, config?: AxiosRequestConfig) {
    return this.client.delete<T>(url, config)
  }

  async patch<T = any>(url: string, data?: any, config?: AxiosRequestConfig) {
    return this.client.patch<T>(url, data, config)
  }
}

export const apiClient = new ApiClient()
