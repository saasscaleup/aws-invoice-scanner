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

  const response = await fetch('https://6zj5jxcstb5m7q2wr4izfcv54m0cbonf.lambda-url.us-east-1.on.aws/', {
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
  <div class="min-h-screen bg-[#0f172a] text-slate-100 px-6 py-10 font-sans">
    <div class="max-w-5xl mx-auto w-full">
      <header class="flex items-center mb-10 gap-4">
        <img src="/src/assets/invoice-manage-logo.svg" alt="ServerLess Invoice Manager" class="w-10 h-10" />
        <h1 class="text-3xl font-bold text-white">ServerLess Invoice Manager</h1>
      </header>

      <section class="bg-slate-900 border border-slate-700 rounded-2xl p-6 md:p-10 shadow-xl mb-10">
        <h2 class="text-xl font-semibold mb-6 text-center">{{ editing ? 'Edit Invoice' : 'Upload Invoices' }}</h2>

        <!-- File chooser (only when NOT editing) -->
        <div class="text-center mb-4" v-if="!editing">
          <label for="fileInput" class="cursor-pointer bg-indigo-500 hover:bg-indigo-400 text-white font-medium px-5 py-2 rounded inline-block transition-colors">Choose Files</label>
          <input id="fileInput" type="file" @change="onFileChange" class="hidden" multiple />
        </div>

        <!-- Preview images (only when files selected and NOT editing) -->
        <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 mb-6" v-if="previewImages.length && !editing">
          <div v-for="(image, idx) in previewImages" :key="idx" class="relative">
            <div class="w-full h-40 md:h-48 rounded-lg overflow-hidden border border-slate-700">
              <img :src="image" alt="preview" @click="openImage(image)" class="cursor-pointer object-cover w-full h-full" />
            </div>
            <button @click.stop.prevent="clearImage(idx)" class="absolute top-2 right-2 bg-white text-black border border-slate-300 rounded px-2 py-1 text-xs font-semibold">Remove</button>
          </div>
        </div>

        <!-- Details are added later via Edit. Hide form inputs during initial file selection. -->
        <div class="mb-4 text-sm text-slate-400" v-if="previewImages.length && !editing">
          You can upload files now — add place, date and amount later by editing the invoice.
        </div>

        <!-- Edit Mode: show image and inputs -->
        <div v-if="editing" class="mb-6 grid grid-cols-1 md:grid-cols-4 gap-4 items-center">
          <div class="col-span-1" v-if="editImage">
            <div class="w-28 h-28 rounded-lg overflow-hidden border border-slate-700">
              <img :src="editImage" alt="Edit Preview" class="object-cover w-full h-full" />
            </div>
          </div>
          <div class="md:col-span-3 grid gap-4 md:grid-cols-3">
            <input ref="placeInputRef" v-model="form.place" placeholder="Place Name" class="bg-slate-800 border border-slate-600 text-white px-4 py-2 rounded w-full placeholder:text-slate-400" />
            <input v-model="form.date" placeholder="Date" type="date" class="bg-slate-800 border border-slate-600 text-white px-4 py-2 rounded w-full placeholder:text-slate-400" />
            <input v-model="form.amount" placeholder="Amount" type="number" class="bg-slate-800 border border-slate-600 text-white px-4 py-2 rounded w-full placeholder:text-slate-400" />
          </div>
        </div>

        <!-- Action buttons: show when uploading (files selected) OR editing -->
        <div class="flex gap-3 justify-end" v-if="(previewImages.length && !editing) || editing">
          <button @click="editing ? updateInvoice() : uploadInvoice()" :disabled="processing" class="text-white px-6 py-2 rounded font-medium transition-colors" :class="editing ? 'bg-green-600 hover:bg-green-500 disabled:bg-green-400' : 'bg-purple-600 hover:bg-purple-500 disabled:bg-purple-400'">
            <span v-if="processing && !editing" class="flex items-center gap-2">
              <svg class="animate-spin h-4 w-4" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Processing...
            </span>
            <span v-else>{{ editing ? 'Save Changes' : 'Upload Invoice' }}</span>
          </button>
          <button v-if="editing" @click="resetForm" class="bg-gray-500 hover:bg-gray-400 text-white px-6 py-2 rounded font-medium transition-colors" style="background-color: #9da8a3;">
            Cancel
          </button>
        </div>
      </section>

      <section class="bg-slate-900 border border-slate-700 rounded-2xl p-6 md:p-10 shadow-xl">
        <h2 class="text-xl font-semibold mb-6 text-center">Invoices</h2>

        <table class="w-full text-left text-sm border-collapse">
          <thead>
            <tr class="text-slate-400 border-b border-slate-700">
              <th class="py-2 px-4">#</th>
              <th class="py-2 px-4">Image</th>
              <th class="py-2 px-4">Place</th>
              <th class="py-2 px-4">Date</th>
              <th class="py-2 px-4">Amount</th>
              <th class="py-2 px-4">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(invoice, index) in invoices" :key="invoice.id" class="border-b border-slate-800 hover:bg-slate-800">
              <td class="py-2 px-4">{{ index + 1 }}</td>
              <td class="py-2 px-4">
                <img :src="invoice.image" @click="openImage(invoice.image)" alt="Invoice" class="cursor-pointer object-cover rounded border border-slate-600" style="width: 32px; height: 32px;" />
              </td>
              <td class="py-2 px-4">{{ invoice.place }}</td>
              <td class="py-2 px-4">{{ invoice.date }}</td>
              <td class="py-2 px-4">${{ invoice.amount }}</td>
              <td class="py-2 px-4 flex gap-2">
                <button @click="editInvoice(invoice)" class="bg-indigo-600 hover:bg-indigo-500 text-white px-3 py-1 rounded text-sm font-medium transition-colors edit">Edit</button>
                <button @click="deleteInvoice(invoice.id)" class="bg-red-600 hover:bg-red-500 text-white px-3 py-1 rounded text-sm font-medium transition-colors delete">Delete</button>
              </td>
            </tr>
          </tbody>
        </table>

        <div v-if="invoices.length === 0" class="text-center text-slate-500 py-8 text-sm">No invoices uploaded yet.</div>
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
        <div class="flex items-center p-4 rounded-lg shadow-lg" :class="toastType === 'success' ? 'bg-green-600 text-white' : 'bg-red-600 text-white'">
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
  font-family: 'Inter', 'Segoe UI', sans-serif;
  background-color: #0f172a;
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.2s ease-in-out;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

.toast-enter-active {
  transition: all 0.3s ease-out;
}
.toast-leave-active {
  transition: all 0.3s ease-in;
}
.toast-enter-from {
  transform: translateX(100%);
  opacity: 0;
}
.toast-leave-to {
  transform: translateX(100%);
  opacity: 0;
}
</style>
