# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Vue 3 invoice management application built with Vite, TailwindCSS, and single-file components. The app allows users to upload invoice images, manage invoice data through CRUD operations, and view invoices in a clean dashboard interface.

## Development Commands

- `npm run dev` - Start development server with hot reloading
- `npm run build` - Build the application for production
- `npm run preview` - Preview the production build locally

## Tech Stack

- **Framework**: Vue 3 with Composition API and `<script setup>` syntax
- **Build Tool**: Vite for fast development and building
- **Styling**: TailwindCSS v4 with dark theme design
- **State Management**: Local component state using Vue 3 reactive references

## Application Architecture

### Single Page Application Structure
The app is built as a single-page application with all functionality contained in `src/App.vue`. This approach was chosen for simplicity and demonstration purposes.

### Key Components
- **Main App (`src/App.vue`)**: Contains all application logic and UI
- **HelloWorld Component**: Standard Vue template component (unused in actual app)

### Data Flow
- Local reactive state manages invoices array, form data, and UI state
- File uploads create blob URLs for immediate preview
- No external API integration - all data is stored in memory

### Styling Approach
- Custom dark theme using TailwindCSS classes
- Responsive design with mobile-first approach
- Consistent color scheme using slate and indigo colors
- Modal overlay for image preview functionality

## Key Features Implementation

### Invoice Management
- Upload multiple invoice images simultaneously
- Edit existing invoice details (place, date, amount)
- Delete invoices with confirmation
- Preview images in full-size modal

### File Handling
- Multiple file selection with preview generation
- Blob URL creation for immediate image display
- File cleanup when removing images

### UI/UX Features
- Keyboard navigation (ESC to close modal)
- Focus management for form inputs
- Responsive grid layouts
- Smooth transitions and hover effects

## Code Patterns

### Vue 3 Composition API
All reactive state is managed using Vue 3's Composition API:
- `ref()` for simple reactive values
- `reactive()` for complex objects
- `computed()` for derived values
- Lifecycle hooks for event management

### Component Structure
Components follow the `<script setup>` pattern with:
- Template-first approach
- Scoped CSS when needed
- Props definition using `defineProps()`

## File Structure Notes

- `src/main.js` - Application entry point
- `src/App.vue` - Main application component
- `src/style.css` - Global styles with TailwindCSS imports
- `src/assets/` - Static assets including custom logo
- `vite.config.js` - Vite configuration with Vue and TailwindCSS plugins