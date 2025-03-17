import axios from 'axios';

// Creamos una instancia de axios con la configuración base
const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para agregar el token de autenticación a todas las solicitudes
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Interceptor para manejar respuestas y errores
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // Si el error es 401 (no autorizado), podríamos redireccionar a login
    if (error.response && error.response.status === 401) {
      // Redirigir a la página de login o limpiar el token
      localStorage.removeItem('authToken');
      // Si estamos en el cliente, redireccionamos
      if (typeof window !== 'undefined') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

// Funciones para interactuar con los endpoints
export const api = {
  // Auth
  auth: {
    login: (credentials) => apiClient.post('/auth/token/', credentials),
    refreshToken: (refresh) => apiClient.post('/auth/token/refresh/', { refresh }),
  },
  
  // Categories
  categories: {
    getAll: (activeOnly = true) => apiClient.get(`/categories/?active_only=${activeOnly}`),
    getById: (id) => apiClient.get(`/categories/${id}/`),
    create: (data) => apiClient.post('/categories/', data),
    update: (id, data) => apiClient.put(`/categories/${id}/`, data),
    delete: (id) => apiClient.delete(`/categories/${id}/`),
  },
  
  // Dishes
  dishes: {
    getAll: (params = {}) => apiClient.get('/dishes/', { params }),
    getById: (id) => apiClient.get(`/dishes/${id}/`),
    getFeatured: () => apiClient.get('/dishes/featured/'),
    create: (data) => apiClient.post('/dishes/', data),
    update: (id, data) => apiClient.put(`/dishes/${id}/`, data),
    delete: (id) => apiClient.delete(`/dishes/${id}/`),
  },
  
  // Tables
  tables: {
    getAll: (activeOnly = true) => apiClient.get(`/tables/?active_only=${activeOnly}`),
    getAvailable: () => apiClient.get('/tables/available/'),
    getById: (id) => apiClient.get(`/tables/${id}/`),
    create: (data) => apiClient.post('/tables/', data),
    update: (id, data) => apiClient.put(`/tables/${id}/`, data),
    delete: (id) => apiClient.delete(`/tables/${id}/`),
  },
  
  // Customers
  customers: {
    getAll: () => apiClient.get('/customers/'),
    getById: (id) => apiClient.get(`/customers/${id}/`),
    getByDocument: (documentNumber) => apiClient.get(`/customers/by_document/?document_number=${documentNumber}`),
    create: (data) => apiClient.post('/customers/', data),
    update: (id, data) => apiClient.put(`/customers/${id}/`, data),
    updateLoyaltyPoints: (id, points) => apiClient.post(`/customers/${id}/update_loyalty_points/`, { points }),
    delete: (id) => apiClient.delete(`/customers/${id}/`),
  },
  
  // Orders
  orders: {
    getAll: (status = null) => {
      const params = status ? { status } : {};
      return apiClient.get('/orders/', { params });
    },
    getById: (id) => apiClient.get(`/orders/${id}/`),
    getByTable: (tableId) => apiClient.get(`/orders/by_table/?table_id=${tableId}`),
    getByCustomer: (customerId) => apiClient.get(`/orders/by_customer/?customer_id=${customerId}`),
    getDailySales: (date = null) => {
      const params = date ? { date: date.toISOString().split('T')[0] } : {};
      return apiClient.get('/orders/daily_sales/', { params });
    },
    create: (data) => apiClient.post('/orders/', data),
    updateStatus: (id, status) => apiClient.patch(`/orders/${id}/update_status/`, { status }),
  },
  
  // Order Items
  orderItems: {
    getById: (id) => apiClient.get(`/order-items/${id}/`),
    updateStatus: (id, status) => apiClient.patch(`/order-items/${id}/update_status/`, { status }),
  },
  
  // Payments
  payments: {
    getAll: () => apiClient.get('/payments/'),
    getById: (id) => apiClient.get(`/payments/${id}/`),
    getByOrder: (orderId) => apiClient.get(`/payments/by_order/?order_id=${orderId}`),
    create: (data) => apiClient.post('/payments/', data),
  },
};

export default apiClient;