import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { createElement } from 'react'
import { StatusIndicator } from '@/components/console/status-indicator'
import type { ConnectionState } from '@/lib/api/contracts/agent'

describe('StatusIndicator (CONS-13)', () => {
  const states: ConnectionState[] = ['disconnected', 'connecting', 'connected', 'error']

  it('renders each state correctly', () => {
    states.forEach((state) => {
      const { container } = render(createElement(StatusIndicator, { state }))
      expect(container.firstChild).toBeInTheDocument()
    })
  })

  it('shows correct icon for disconnected state', () => {
    render(createElement(StatusIndicator, { state: 'disconnected' }))
    // Radio icon for idle/disconnected
    expect(screen.getByLabelText(/idle/i)).toBeInTheDocument()
  })

  it('shows correct icon for connecting state', () => {
    render(createElement(StatusIndicator, { state: 'connecting' }))
    // Loader2 spinner for connecting
    expect(screen.getByLabelText(/connecting/i)).toBeInTheDocument()
  })

  it('shows correct icon for connected state', () => {
    render(createElement(StatusIndicator, { state: 'connected' }))
    // CheckCircle2 for connected/complete
    expect(screen.getByLabelText(/connected/i)).toBeInTheDocument()
  })

  it('shows correct icon for error state', () => {
    render(createElement(StatusIndicator, { state: 'error' }))
    // XCircle for error
    expect(screen.getByLabelText(/error/i)).toBeInTheDocument()
  })

  it('shows correct label for disconnected state', () => {
    render(createElement(StatusIndicator, { state: 'disconnected' }))
    expect(screen.getByText('Idle')).toBeInTheDocument()
  })

  it('shows correct label for connecting state', () => {
    render(createElement(StatusIndicator, { state: 'connecting' }))
    expect(screen.getByText('Connecting...')).toBeInTheDocument()
  })

  it('shows correct label for connected state', () => {
    render(createElement(StatusIndicator, { state: 'connected' }))
    expect(screen.getByText('Connected')).toBeInTheDocument()
  })

  it('shows correct label for error state', () => {
    render(createElement(StatusIndicator, { state: 'error' }))
    expect(screen.getByText('Error')).toBeInTheDocument()
  })

  it('animate-spin applied to connecting state', () => {
    const { container } = render(createElement(StatusIndicator, { state: 'connecting' }))
    const spinnerIcon = container.querySelector('.animate-spin')
    expect(spinnerIcon).toBeInTheDocument()
  })

  it('animate-spin not applied to disconnected state', () => {
    const { container } = render(createElement(StatusIndicator, { state: 'disconnected' }))
    const animatedElement = container.querySelector('.animate-spin')
    expect(animatedElement).not.toBeInTheDocument()
  })

  it('applies custom className', () => {
    const { container } = render(
      createElement(StatusIndicator, { state: 'disconnected', className: 'custom-class' })
    )
    expect(container.firstChild).toHaveClass('custom-class')
  })
})
