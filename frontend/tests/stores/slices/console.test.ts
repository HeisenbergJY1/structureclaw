import { describe, it, expect } from 'vitest'
import { createConsoleSlice, initialConsoleState, type ConsoleSlice } from '@/lib/stores/slices/console'
import { createStore } from 'zustand/vanilla'

describe('Console Slice (STAT-01)', () => {
  const createTestStore = () => {
    return createStore<ConsoleSlice>()((...args) => ({
      ...createConsoleSlice(...args),
    }))
  }

  it('returns initial state with correct defaults', () => {
    const store = createTestStore()
    const state = store.getState()

    expect(state.endpoint).toBe('chat-message')
    expect(state.mode).toBe('auto')
    expect(state.conversationId).toBeNull()
    expect(state.traceId).toBeNull()
  })

  it('setEndpoint action updates endpoint value', () => {
    const store = createTestStore()

    store.getState().setEndpoint('agent-run')
    expect(store.getState().endpoint).toBe('agent-run')

    store.getState().setEndpoint('chat-execute')
    expect(store.getState().endpoint).toBe('chat-execute')

    store.getState().setEndpoint('chat-message')
    expect(store.getState().endpoint).toBe('chat-message')
  })

  it('setMode action updates mode value', () => {
    const store = createTestStore()

    store.getState().setMode('chat')
    expect(store.getState().mode).toBe('chat')

    store.getState().setMode('execute')
    expect(store.getState().mode).toBe('execute')

    store.getState().setMode('auto')
    expect(store.getState().mode).toBe('auto')
  })

  it('setConversationId action updates conversationId', () => {
    const store = createTestStore()

    store.getState().setConversationId('conv-123')
    expect(store.getState().conversationId).toBe('conv-123')

    store.getState().setConversationId('conv-456')
    expect(store.getState().conversationId).toBe('conv-456')

    store.getState().setConversationId(null)
    expect(store.getState().conversationId).toBeNull()
  })

  it('resetConsole action restores initial state', () => {
    const store = createTestStore()

    // Modify all state
    store.getState().setEndpoint('agent-run')
    store.getState().setMode('execute')
    store.getState().setConversationId('conv-123')

    // Verify modified state
    expect(store.getState().endpoint).toBe('agent-run')
    expect(store.getState().mode).toBe('execute')
    expect(store.getState().conversationId).toBe('conv-123')

    // Reset
    store.getState().resetConsole()

    // Verify reset
    expect(store.getState().endpoint).toBe('chat-message')
    expect(store.getState().mode).toBe('auto')
    expect(store.getState().conversationId).toBeNull()
    expect(store.getState().traceId).toBeNull()
  })
})
