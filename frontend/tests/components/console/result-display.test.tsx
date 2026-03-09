import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { StatusHeader } from '@/components/console/result-display/status-header'
import type { AgentResult } from '@/lib/stores/slices/console'

describe('StatusHeader (CONS-08)', () => {
  it('shows "idle" when no result', () => {
    render(<StatusHeader result={null} />)
    expect(screen.getByText('idle')).toBeInTheDocument()
  })

  it('shows "success" badge when result.success is true', () => {
    const result: AgentResult = {
      response: 'test',
      success: true,
    }
    render(<StatusHeader result={result} />)
    expect(screen.getByText('success')).toBeInTheDocument()
  })

  it('shows "failed" badge when result.success is false', () => {
    const result: AgentResult = {
      response: '',
      success: false,
    }
    render(<StatusHeader result={result} />)
    expect(screen.getByText('failed')).toBeInTheDocument()
  })

  it('displays traceId when present', () => {
    const result: AgentResult = {
      response: 'test',
      success: true,
      traceId: 'trace-12345',
    }
    render(<StatusHeader result={result} />)
    expect(screen.getByText('trace-12345')).toBeInTheDocument()
  })

  it('uses monospace font for traceId', () => {
    const result: AgentResult = {
      response: 'test',
      success: true,
      traceId: 'trace-abc',
    }
    const { container } = render(<StatusHeader result={result} />)
    const traceIdElement = screen.getByText('trace-abc')
    expect(traceIdElement.className).toMatch(/font-mono|mono/)
  })
})
