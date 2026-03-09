import { type StateCreator } from 'zustand'

export interface ConsoleState {
  endpoint: 'agent-run' | 'chat-message' | 'chat-execute'
  mode: 'chat' | 'execute' | 'auto'
  conversationId: string | null
  traceId: string | null
}

export interface ConsoleActions {
  setEndpoint: (endpoint: ConsoleState['endpoint']) => void
  setMode: (mode: ConsoleState['mode']) => void
  setConversationId: (id: string | null) => void
  resetConsole: () => void
}

export type ConsoleSlice = ConsoleState & ConsoleActions

export const initialConsoleState: ConsoleState = {
  endpoint: 'chat-message',
  mode: 'auto',
  conversationId: null,
  traceId: null,
}

// Note: StoreState is defined in context.tsx and will be the full combined state
// Using 'any' for the state parameter to avoid circular dependency
// The actual type safety comes from the StoreState in context.tsx
export const createConsoleSlice: StateCreator<ConsoleSlice, [], [], ConsoleSlice> = (set) => ({
  ...initialConsoleState,
  setEndpoint: (endpoint) => set({ endpoint }),
  setMode: (mode) => set({ mode }),
  setConversationId: (conversationId) => set({ conversationId }),
  resetConsole: () => set(initialConsoleState),
})
