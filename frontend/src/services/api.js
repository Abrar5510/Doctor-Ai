import axios from 'axios'

// For Vercel deployment, use same-domain API (empty baseURL means relative to current domain)
// For local development, use localhost backend
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || (import.meta.env.DEV ? 'http://localhost:8000' : ''),
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor for adding auth tokens if needed
apiClient.interceptors.request.use(
  (config) => {
    // Add auth token here if needed
    // const token = localStorage.getItem('token')
    // if (token) {
    //   config.headers.Authorization = `Bearer ${token}`
    // }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor for handling errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access - redirect to login or show message
      // In production, this would trigger a redirect to login page or refresh token flow
      if (import.meta.env.DEV) {
        console.error('Unauthorized access - authentication required')
      }
      // Could dispatch to a global error handler or redirect here
    }
    return Promise.reject(error)
  }
)

export default apiClient
