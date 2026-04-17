import axios, { type AxiosInstance, type AxiosError } from 'axios'
import { useAuthStore } from '../stores/authStore'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

class ApiClient {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    // Request interceptor: Add authorization token
    this.client.interceptors.request.use((config) => {
      const { accessToken } = useAuthStore.getState()
      if (accessToken) {
        config.headers.Authorization = `Bearer ${accessToken}`
      }
      return config
    })

    // Response interceptor: Handle 401 and refresh token
    this.client.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        const { response, config } = error
        const originalRequest = config as any

        if (response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true
          const { refreshToken, setTokens, clearAuth } = useAuthStore.getState()

          if (refreshToken) {
            try {
              const res = await axios.post(`${API_BASE_URL}/auth/refresh`, {
                refresh_token: refreshToken,
              })
              const { access_token, refresh_token } = res.data
              setTokens(access_token, refresh_token)
              originalRequest.headers.Authorization = `Bearer ${access_token}`
              return this.client(originalRequest)
            } catch (err) {
              clearAuth()
            }
          }
        }

        return Promise.reject(error)
      }
    )
  }

  getClient() {
    return this.client
  }
}

export default new ApiClient().getClient()
