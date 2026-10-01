<script setup>
import { computed, onMounted, ref } from 'vue'

const API_URL = 'http://localhost:8000/sessions'
const sessions = ref([])
const search = ref('')
const page = ref(1)
const limit = ref(5)
const total = ref(0)
const loading = ref(false)
const error = ref('')
const formError = ref('')
const isSubmitting = ref(false)
const deletingId = ref(null)

const form = ref({
  route_name: '',
  driver_name: '',
  departure_time: '',
  passenger_name: '',
  destination: '',
  seat_count: 2,
  status: 'scheduled',
})

const totalPages = computed(() => Math.max(1, Math.ceil(total.value / limit.value)))

const viewState = computed(() => {
  if (loading.value) return 'loading'
  if (error.value) return 'error'
  if (!sessions.value.length) return 'empty'
  return 'list'
})

async function fetchSessions() {
  loading.value = true
  error.value = ''

  try {
    const url = new URL(API_URL)
    url.searchParams.set('page', String(page.value))
    url.searchParams.set('limit', String(limit.value))

    if (search.value.trim()) {
      url.searchParams.set('search', search.value.trim())
    }

    const response = await fetch(url)
    if (!response.ok) {
      throw new Error(`Request failed with status ${response.status}`)
    }

    const payload = await response.json()
    sessions.value = payload.items || []
    total.value = payload.total || 0
    page.value = payload.page || 1
  } catch (err) {
    sessions.value = []
    error.value = err instanceof Error ? err.message : 'Failed to load sessions.'
  } finally {
    loading.value = false
  }
}

async function onSearch() {
  page.value = 1
  await fetchSessions()
}

function resetForm() {
  form.value = {
    route_name: '',
    driver_name: '',
    departure_time: '',
    passenger_name: '',
    destination: '',
    seat_count: 2,
    status: 'scheduled',
  }
}

async function submitForm() {
  const requiredFields = Object.entries(form.value).filter(([key]) => key !== 'status')
  const missing = requiredFields.some(([, value]) => !String(value || '').trim())

  if (missing) {
    formError.value = 'Please complete all required fields before saving.'
    return
  }

  const seatCount = Number(form.value.seat_count)
  if (!Number.isInteger(seatCount) || seatCount < 1 || seatCount > 20) {
    formError.value = 'Seat count must be between 1 and 20.'
    return
  }

  isSubmitting.value = true
  formError.value = ''

  try {
    const response = await fetch(API_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        ...form.value,
        seat_count: seatCount,
      }),
    })

    if (!response.ok) {
      const payload = await response.json().catch(() => ({}))
      throw new Error(payload.detail || 'Failed to create session.')
    }

    resetForm()
    page.value = 1
    await fetchSessions()
  } catch (err) {
    formError.value = err instanceof Error ? err.message : 'Something went wrong.'
  } finally {
    isSubmitting.value = false
  }
}

async function deleteSession(id) {
  const confirmed = window.confirm('Are you sure you want to delete this shuttle session?')
  if (!confirmed) return

  deletingId.value = id

  try {
    const response = await fetch(`${API_URL}/${id}`, { method: 'DELETE' })
    if (!response.ok) {
      throw new Error('Delete request failed.')
    }

    if (sessions.value.length === 1 && page.value > 1) {
      page.value -= 1
    }

    await fetchSessions()
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Deletion failed.'
  } finally {
    deletingId.value = null
  }
}

onMounted(() => {
  fetchSessions()
})
</script>

<template>
  <div class="page-shell">
    <header class="topbar">
      <div>
        <p class="eyebrow">Campus Transport</p>
        <h1>Shuttle Session Dashboard</h1>
      </div>
    </header>

    <main class="content-grid">
      <section class="panel form-panel">
        <h2>New shuttle booking</h2>

        <form class="session-form" @submit.prevent="submitForm">
          <label>
            Route name
            <input v-model="form.route_name" type="text" placeholder="Kampus - Terminal Baru" />
          </label>

          <label>
            Driver name
            <input v-model="form.driver_name" type="text" placeholder="Andi Pratama" />
          </label>

          <label>
            Departure time
            <input v-model="form.departure_time" type="time" />
          </label>

          <label>
            Passenger name
            <input v-model="form.passenger_name" type="text" placeholder="Rina Sari" />
          </label>

          <label>
            Destination
            <input v-model="form.destination" type="text" placeholder="Terminal Baru" />
          </label>

          <div class="inline-fields">
            <label>
              Seat count
              <input v-model.number="form.seat_count" type="number" min="1" max="20" />
            </label>

            <label>
              Status
              <select v-model="form.status">
                <option value="scheduled">Scheduled</option>
                <option value="on_route">On Route</option>
                <option value="completed">Completed</option>
              </select>
            </label>
          </div>

          <button type="submit" :disabled="isSubmitting">
            {{ isSubmitting ? 'Saving...' : 'Create session' }}
          </button>

          <p v-if="formError" class="error-text">{{ formError }}</p>
        </form>
      </section>

      <section class="panel table-panel">
        <div class="table-header">
          <h2>Session list</h2>
          <div class="search-wrap">
            <input v-model="search" type="search" placeholder="Search route or passenger" @input="onSearch" />
          </div>
        </div>

        <div v-if="viewState === 'loading'" class="state-box">
          <p>Loading sessions...</p>
        </div>

        <div v-else-if="viewState === 'error'" class="state-box error-box">
          <p>{{ error }}</p>
          <button type="button" class="secondary" @click="fetchSessions">Retry</button>
        </div>

        <div v-else-if="viewState === 'empty'" class="state-box">
          <p>No sessions found.</p>
        </div>

        <div v-else class="table-scroll">
          <table>
            <thead>
              <tr>
                <th>Route</th>
                <th>Driver</th>
                <th>Passenger</th>
                <th>Departure</th>
                <th>Seats</th>
                <th>Status</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="session in sessions" :key="session.id">
                <td>{{ session.route_name }}</td>
                <td>{{ session.driver_name }}</td>
                <td>{{ session.passenger_name }}</td>
                <td>{{ session.departure_time }}</td>
                <td>{{ session.seat_count }}</td>
                <td>
                  <span class="badge" :class="session.status">{{ session.status }}</span>
                </td>
                <td>
                  <button type="button" class="danger" :disabled="deletingId === session.id" @click="deleteSession(session.id)">
                    {{ deletingId === session.id ? 'Deleting...' : 'Delete' }}
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-if="sessions.length" class="pagination">
          <button type="button" :disabled="page <= 1" @click="page -= 1; fetchSessions()">Prev</button>
          <span>Page {{ page }} of {{ totalPages }}</span>
          <button type="button" :disabled="page >= totalPages" @click="page += 1; fetchSessions()">Next</button>
        </div>
      </section>
    </main>
  </div>
</template>

