/*
Invoice Manager - Vue 3 Project
Inspired by https://nightwatch.laravel.com/
- Upload and preview invoice images
- Process invoices via Lambda (mocked)
- CRUD operations
- Styled with TailwindCSS in a clean, modern dashboard UI
*/

<script setup>
import { ref, reactive, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'

const invoices = ref([])
const selectedFiles = ref([])
const previewImages = ref([])
const editing = ref(false)
const showModal = ref(false)
const modalImage = ref('')
const placeInputRef = ref(null)
const showInputs = ref(false)

// Toast notifications
const showToast = ref(false)
const toastMessage = ref('')
const toastType = ref('success') // 'success' or 'error'
const processing = ref(false)

const form = reactive({
  id: null,
  place: '',
  date: '',
  amount: '',
  image: ''
})

const editImage = ref('')

const hasFiles = computed(() => selectedFiles.value.length > 0)

function onFileChange(e) {
  selectedFiles.value = Array.from(e.target.files)
  previewImages.value = selectedFiles.value.map(file => URL.createObjectURL(file))
  showInputs.value = true
  editing.value = false
}

function clearImage(idx) {
  selectedFiles.value.splice(idx, 1)
  previewImages.value.splice(idx, 1)
  if (!selectedFiles.value.length) showInputs.value = false
}

async function processInvoiceWithAPI(file) {
  // Convert file to base64
  const base64 = await new Promise((resolve) => {
    const reader = new FileReader()
    reader.onload = () => {
      const base64String = reader.result.split(',')[1] // Remove data:image/xxx;base64, prefix
      resolve(base64String)
    }
    reader.readAsDataURL(file)
  })

  const response = await fetch('<aws-lambda-url>', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      image_base64: base64,
      media_type: file.type || 'image/jpeg'
    })
  })

  if (!response.ok) {
    throw new Error(`API request failed: ${response.status}`)
  }

  const result = await response.json()
  
  return {
    place: result.place,
    date: result.date,
    payment: result.payment,
    currency: result.currency
  }
}

async function uploadInvoice() {
  if (!selectedFiles.value.length) {
    showToastMessage('Please select at least one file', 'error')
    return
  }

  processing.value = true

  try {
    for (let i = 0; i < selectedFiles.value.length; i++) {
      const file = selectedFiles.value[i]
      
      // Basic file validation
      if (!file.type.startsWith('image/')) {
        showToastMessage(`File ${file.name} is not a valid image`, 'error')
        processing.value = false
        return
      }
      
      if (file.size > 5 * 1024 * 1024) { // 5MB limit
        showToastMessage(`File ${file.name} is too large (max 5MB)`, 'error')
        processing.value = false
        return
      }

      // Process invoice with API
      const apiData = await processInvoiceWithAPI(file)

      const newInvoice = {
        id: Date.now() + i,
        place: apiData.place,
        date: apiData.date,
        amount: apiData.payment.toString(),
        image: previewImages.value[i]
      }
      invoices.value.push(newInvoice)
    }
    
    const fileCount = selectedFiles.value.length
    showToastMessage(`Successfully processed ${fileCount} invoice${fileCount > 1 ? 's' : ''}!`, 'success')
    resetForm()
  } catch (error) {
    console.error('Upload error:', error)
    showToastMessage('Failed to process invoice. Please try again.', 'error')
  } finally {
    processing.value = false
  }
}

function resetForm() {
  selectedFiles.value = []
  previewImages.value = []
  form.place = ''
  form.date = ''
  form.amount = ''
  form.id = null
  editing.value = false
  showInputs.value = false
  editImage.value = ''
}

function editInvoice(inv) {
  Object.assign(form, inv)
  // show the invoice image in edit mode but clear upload previews
  editImage.value = inv.image || ''
  selectedFiles.value = []
  previewImages.value = []
  editing.value = true
  showInputs.value = true
  nextTick(() => {
    placeInputRef.value?.focus()
  })
}

function updateInvoice() {
  const idx = invoices.value.findIndex(i => i.id === form.id)
  if (idx !== -1) {
    // prefer a newly selected preview image, otherwise keep the original editImage
    const newImage = (previewImages.value && previewImages.value.length) ? previewImages.value[0] : editImage.value || invoices.value[idx].image
    invoices.value[idx] = { ...form, image: newImage }
    showToastMessage('Invoice updated successfully!', 'success')
    resetForm()
  } else {
    showToastMessage('Failed to update invoice', 'error')
  }
}

function deleteInvoice(id) {
  invoices.value = invoices.value.filter(i => i.id !== id)
  showToastMessage('Invoice deleted successfully!', 'success')
}

function openImage(imageUrl) {
  modalImage.value = imageUrl
  showModal.value = true
}

function showToastMessage(message, type = 'success') {
  toastMessage.value = message
  toastType.value = type
  showToast.value = true
  
  // Auto-hide toast after 4 seconds
  setTimeout(() => {
    showToast.value = false
  }, 4000)
}

function hideToast() {
  showToast.value = false
}

function handleEsc(e) {
  if (e.key === 'Escape') {
    showModal.value = false
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleEsc)
})

onBeforeUnmount(() => {
  window.removeEventListener('keydown', handleEsc)
})
</script>

<template>
  <div class="min-h-screen bg-[#1a1a2e] text-gray-100 font-sans">
    <div class="max-w-6xl mx-auto w-full">
      <header class="backdrop-blur-sm border-b border-purple-500/20 px-6 py-6 mb-12 -mx-6 transition-all duration-500 ease-out">
        <div class="max-w-6xl mx-auto flex items-center gap-4">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg flex items-center justify-center shadow-lg shadow-purple-500/25 hover:shadow-purple-500/40 transition-all duration-300 hover:scale-105">
              <svg class="w-6 h-6 text-white transition-transform duration-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
              </svg>
            </div>
            <div>
              <h1 class="text-2xl font-bold text-white hover:text-purple-200 transition-colors duration-300">AWS Invoice Manager</h1>
              <p class="text-sm text-purple-300">
                Powered by 
                <a href="https://github.com/poptin" target="_blank" rel="noopener noreferrer" class="text-purple-200 hover:text-white transition-all duration-200 underline underline-offset-2 hover:underline-offset-4">
                  ScaleUp SaaS
                </a>
              </p>
            </div>
          </div>
        </div>
      </header>

      <section class="border border-purple-500/20 rounded-xl p-6 md:p-8 shadow-xl mb-8 mx-6 backdrop-blur-sm hover:shadow-2xl hover:shadow-purple-500/10 transition-all duration-500 ease-out hover:border-purple-500/30">
        <h2 class="text-xl font-semibold mb-6 text-white transition-all duration-300">{{ editing ? 'Edit Invoice' : 'Upload Invoices' }}</h2>

        <!-- File chooser (only when NOT editing) -->
        <div class="text-center mb-4" v-if="!editing">
          <label for="fileInput" class="cursor-pointer bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white font-medium px-6 py-3 rounded-lg inline-block transition-all duration-300 text-sm shadow-lg hover:shadow-purple-500/40 hover:scale-105 transform hover:-translate-y-0.5">
            <svg class="w-5 h-5 inline-block mr-2 transition-transform duration-300 group-hover:scale-110" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path>
            </svg>
            Choose Files
          </label>
          <input id="fileInput" type="file" @change="onFileChange" class="hidden" multiple />
        </div>

        <!-- Preview images (only when files selected and NOT editing) -->
        <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 mb-6" v-if="previewImages.length && !editing">
          <div v-for="(image, idx) in previewImages" :key="idx" class="relative group">
            <div class="w-full h-40 md:h-48 rounded-lg overflow-hidden border border-purple-500/30 bg-[#252545] shadow-lg hover:shadow-purple-500/20 transition-all duration-500 ease-out hover:border-purple-500/50">
              <img :src="image" alt="preview" @click="openImage(image)" class="cursor-pointer object-cover w-full h-full transition-all duration-500 ease-out group-hover:scale-110" />
            </div>
            <button @click.stop.prevent="clearImage(idx)" class="absolute top-2 right-2 bg-red-500/80 hover:bg-red-500 text-white rounded-full p-1.5 text-xs font-medium shadow-lg transition-all duration-300 opacity-0 group-hover:opacity-100 hover:scale-110 hover:rotate-90">
              <svg class="w-4 h-4 transition-transform duration-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
            </button>
          </div>
        </div>

        <!-- Details are added later via Edit. Hide form inputs during initial file selection. -->
        <div class="mb-4 text-sm text-purple-300" v-if="previewImages.length && !editing">
          <div class="flex items-center gap-2">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path>
            </svg>
            Files will be processed automatically using AI to extract invoice data.
          </div>
        </div>

        <!-- Edit Mode: show image and inputs -->
        <div v-if="editing" class="mb-6 grid grid-cols-1 md:grid-cols-4 gap-4 items-center">
          <div class="col-span-1" v-if="editImage">
            <div class="w-28 h-28 rounded-lg overflow-hidden border border-purple-500/30 bg-[#252545]">
              <img :src="editImage" alt="Edit Preview" class="object-cover w-full h-full" />
            </div>
          </div>
          <div class="md:col-span-3 grid gap-4 md:grid-cols-3">
            <input ref="placeInputRef" v-model="form.place" placeholder="Place Name" class="bg-[#252545] border border-purple-500/30 text-white px-4 py-3 rounded-lg w-full placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all duration-200" />
            <input v-model="form.date" placeholder="Date" type="date" class="bg-[#252545] border border-purple-500/30 text-white px-4 py-3 rounded-lg w-full placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all duration-200" />
            <input v-model="form.amount" placeholder="Amount" type="number" class="bg-[#252545] border border-purple-500/30 text-white px-4 py-3 rounded-lg w-full placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all duration-200" />
          </div>
        </div>

        <!-- Action buttons: show when uploading (files selected) OR editing -->
        <div class="flex gap-3 justify-end" v-if="(previewImages.length && !editing) || editing">
          <button @click="editing ? updateInvoice() : uploadInvoice()" :disabled="processing" class="text-white px-6 py-3 rounded-lg font-medium transition-all duration-300 text-sm shadow-lg" :class="editing ? 'bg-gradient-to-r from-green-500 to-emerald-500 hover:from-green-600 hover:to-emerald-600 disabled:from-green-400 disabled:to-emerald-400 hover:shadow-green-500/25' : 'bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 disabled:from-purple-400 disabled:to-pink-400 hover:shadow-purple-500/25'">
            <span v-if="processing && !editing" class="flex items-center gap-2">
              <svg class="animate-spin h-4 w-4" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Processing with AI...
            </span>
            <span v-else>
              <svg class="w-4 h-4 inline-block mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path v-if="editing" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
              </svg>
              {{ editing ? 'Save Changes' : 'Process Invoice' }}
            </span>
          </button>
          <button v-if="editing" @click="resetForm" class="bg-[#252545] hover:bg-[#333366] text-gray-300 border border-purple-500/30 px-6 py-3 rounded-lg font-medium transition-all duration-300 text-sm">
            Cancel
          </button>
        </div>
      </section>

      <section class="border border-purple-500/20 rounded-xl shadow-xl mx-6 backdrop-blur-sm overflow-hidden hover:shadow-2xl hover:shadow-purple-500/10 transition-all duration-500 ease-out hover:border-purple-500/30">
        <div class="px-6 py-5 border-b border-purple-500/20 bg-gradient-to-r from-purple-500/5 to-pink-500/5 transition-all duration-300 hover:from-purple-500/10 hover:to-pink-500/10">
          <h2 class="text-xl font-semibold text-white flex items-center gap-2 transition-all duration-300">
            <svg class="w-5 h-5 text-purple-400 transition-all duration-300 hover:text-purple-300 hover:scale-110" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
            </svg>
            Invoices
          </h2>
        </div>

        <div class="overflow-x-auto">
          <table class="w-full text-left text-sm">
            <thead class="bg-[#252545]/50">
              <tr class="text-purple-300 border-b border-purple-500/20">
                <th class="py-4 px-6 font-medium">#</th>
                <th class="py-4 px-6 font-medium">Image</th>
                <th class="py-4 px-6 font-medium">Place</th>
                <th class="py-4 px-6 font-medium">Date</th>
                <th class="py-4 px-6 font-medium">Amount</th>
                <th class="py-4 px-6 font-medium">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(invoice, index) in invoices" :key="invoice.id" class="border-b border-purple-500/10 hover:bg-purple-500/5 transition-all duration-300 ease-out group">
                <td class="py-4 px-6 text-gray-300 group-hover:text-white transition-colors duration-300">{{ index + 1 }}</td>
                <td class="py-4 px-6">
                  <div class="w-10 h-10 rounded-lg overflow-hidden border border-purple-500/30 bg-[#252545] cursor-pointer hover:scale-110 hover:shadow-lg hover:shadow-purple-500/20 transition-all duration-300 ease-out hover:border-purple-500/50">
                    <img :src="invoice.image" @click="openImage(invoice.image)" alt="Invoice" class="object-cover w-full h-full transition-all duration-300" />
                  </div>
                </td>
                <td class="py-4 px-6 text-white font-medium group-hover:text-purple-200 transition-colors duration-300">{{ invoice.place }}</td>
                <td class="py-4 px-6 text-gray-300 group-hover:text-white transition-colors duration-300">{{ invoice.date }}</td>
                <td class="py-4 px-6 text-green-400 font-semibold group-hover:text-green-300 transition-colors duration-300">${{ invoice.amount }}</td>
                <td class="py-4 px-6">
                  <div class="flex gap-2">
                    <button @click="editInvoice(invoice)" class="bg-purple-500/20 hover:bg-purple-500/40 text-purple-300 border border-purple-500/30 px-3 py-1.5 rounded-lg text-sm font-medium transition-all duration-300 hover:text-white hover:scale-105 hover:shadow-lg hover:shadow-purple-500/20">
                      <svg class="w-4 h-4 inline-block mr-1 transition-transform duration-300 hover:scale-110" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                      </svg>
                      Edit
                    </button>
                    <button @click="deleteInvoice(invoice.id)" class="bg-red-500/20 hover:bg-red-500/80 text-red-300 hover:text-white px-3 py-1.5 rounded-lg text-sm font-medium transition-all duration-300 hover:scale-105 hover:shadow-lg hover:shadow-red-500/20">
                      <svg class="w-4 h-4 inline-block mr-1 transition-transform duration-300 hover:scale-110" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                      </svg>
                      Delete
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-if="invoices.length === 0" class="text-center text-gray-400 py-16 text-sm">
          <div class="text-purple-400/50 mb-4">
            <svg class="mx-auto h-16 w-16" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <p class="text-lg font-medium text-gray-300 mb-2">No invoices yet</p>
          <p class="text-gray-500">Upload your first invoice to get started</p>
        </div>
      </section>
    </div>

    <!-- Image Modal -->
    <transition name="fade">
      <div v-if="showModal" class="fixed inset-0 bg-black bg-opacity-80 flex items-center justify-center z-50">
        <div class="relative">
          <img :src="modalImage" class="max-w-full max-h-[80vh] rounded-lg shadow-xl" />
          <button @click="showModal = false" class="absolute top-2 right-2 bg-white text-black px-2 py-1 rounded font-bold shadow">X</button>
        </div>
      </div>
    </transition>

    <!-- Toast Notification -->
    <transition name="toast">
      <div v-if="showToast" class="fixed top-4 right-4 z-50 max-w-sm">
        <div class="flex items-center p-4 rounded-lg shadow-xl border backdrop-blur-sm" :class="toastType === 'success' ? 'bg-green-500/90 text-white border-green-400' : 'bg-red-500/90 text-white border-red-400'">
          <div class="flex-shrink-0">
            <svg v-if="toastType === 'success'" class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path>
            </svg>
            <svg v-else class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"></path>
            </svg>
          </div>
          <div class="ml-3 font-medium">{{ toastMessage }}</div>
        </div>
      </div>
    </transition>
  </div>
</template>

<style>
body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans', Helvetica, Arial, sans-serif;
  background: #1a1a2e;
  background-attachment: fixed;
}

/* Smooth scrolling */
html {
  scroll-behavior: smooth;
}

/* Enhanced fade transitions */
.fade-enter-active, .fade-leave-active {
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
  transform: scale(0.95);
}

/* Smooth toast animations */
.toast-enter-active {
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}
.toast-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.toast-enter-from {
  transform: translateX(100%) scale(0.95);
  opacity: 0;
}
.toast-leave-to {
  transform: translateX(100%) scale(0.95);
  opacity: 0;
}

/* Smooth focus outlines */
*:focus {
  outline: none;
  box-shadow: 0 0 0 3px rgb(168 85 247 / 0.3);
  transition: box-shadow 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Enhanced button hover states */
button {
  transform-origin: center;
}

/* Smooth loading animations */
@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.6;
  }
}

.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

/* Smooth background transitions */
* {
  transition-property: background-color, border-color, color, fill, stroke, opacity, box-shadow, transform;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
}
</style>
