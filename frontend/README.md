# AIDEN Frontend

A modern, beautiful chat interface for the AIDEN AI Assistant, built with Next.js 14, TypeScript, and Tailwind CSS.

## ✨ Features

- **Modern UI/UX**: Beautiful glassmorphism design with smooth animations
- **Dark/Light Mode**: Toggle between dark and light themes
- **Real-time Chat**: Seamless conversation with AI assistant
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile
- **TypeScript**: Full type safety throughout the application
- **Performance Optimized**: Built with Next.js 14 App Router for optimal performance

## 🚀 Tech Stack

- **Next.js 14** - React framework with App Router
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first CSS framework
- **Radix UI** - Unstyled, accessible UI primitives
- **Shadcn/UI** - Re-usable UI components
- **Lucide Icons** - Beautiful, customizable icons
- **Inter Font** - Modern, readable typography

## 🛠️ Development

### Prerequisites

- Node.js 18+ 
- npm or yarn

### Getting Started

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

3. Open [http://localhost:3000](http://localhost:3000) in your browser.

### Build for Production

```bash
npm run build
npm start
```

## 🎨 Design System

The frontend uses a comprehensive design system with:

- **CSS Variables** for theming (light/dark mode)
- **Glassmorphism** effects for modern UI
- **Consistent spacing** and typography
- **Accessible color contrast**
- **Smooth animations** and transitions

## 📁 Project Structure

```
frontend/
├── app/                    # Next.js App Router
│   ├── globals.css        # Global styles and design system
│   ├── layout.tsx         # Root layout
│   └── page.tsx           # Main chat page
├── components/            # React components
│   ├── ui/               # Shadcn UI components
│   ├── chat-input.tsx    # Chat input component
│   ├── chat-message.tsx  # Message display component
│   └── typing-indicator.tsx # Typing animation
├── lib/                   # Utilities
│   └── utils.ts          # Tailwind merge utility
└── public/               # Static assets
```

## 🔧 Configuration

- **Tailwind CSS**: Configured with custom design tokens
- **TypeScript**: Strict mode enabled
- **ESLint**: Next.js recommended configuration
- **Next.js**: Optimized for performance and SEO

## 🌟 Features in Detail

### Chat Interface
- Real-time messaging with the AI
- Message timestamps
- Typing indicators
- Auto-scroll to latest messages
- Error handling and user feedback

### Accessibility
- Keyboard navigation support
- Screen reader friendly
- High contrast mode support
- Focus management

### Performance
- Optimized bundle size
- Lazy loading
- Image optimization
- Fast refresh during development

## 🤝 Contributing

1. Follow the existing code style
2. Use TypeScript strictly
3. Write accessible components
4. Test thoroughly before submitting

---

**Built with ❤️ by the AIDEN Team**
