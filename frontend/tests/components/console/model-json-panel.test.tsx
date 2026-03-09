import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { AppStoreProvider } from '@/lib/stores/context'
import { ModelJsonPanel } from '@/components/console/model-json-panel'

describe('ModelJsonPanel (CONS-04)', () => {
  beforeEach(() => {
    vi.spyOn(console, 'error').mockImplementation(() => {})
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  const renderWithProvider = () => {
    return render(
      <AppStoreProvider>
        <ModelJsonPanel />
      </AppStoreProvider>
    )
  }

  it('renders checkbox for include model', () => {
    renderWithProvider()
    expect(screen.getByRole('checkbox', { name: /include model json/i })).toBeInTheDocument()
  })

  it('checking checkbox shows collapsible content', async () => {
    const user = userEvent.setup()
    renderWithProvider()

    // Initially, textarea should not be visible
    expect(screen.queryByRole('textbox', { name: /model json/i })).not.toBeInTheDocument()

    // Check the checkbox
    const checkbox = screen.getByRole('checkbox', { name: /include model json/i })
    await user.click(checkbox)

    // Now textarea should be visible
    expect(screen.getByRole('textbox', { name: /model json/i })).toBeInTheDocument()
  })

  it('collapsible expands and collapses', async () => {
    const user = userEvent.setup()
    renderWithProvider()

    // Check the checkbox first to enable the panel
    const checkbox = screen.getByRole('checkbox', { name: /include model json/i })
    await user.click(checkbox)

    // The textarea should be visible now
    const textarea = screen.getByRole('textbox', { name: /model json/i })
    expect(textarea).toBeVisible()
  })

  it('textarea uses monospace font', async () => {
    const user = userEvent.setup()
    renderWithProvider()

    // Check the checkbox
    const checkbox = screen.getByRole('checkbox', { name: /include model json/i })
    await user.click(checkbox)

    const textarea = screen.getByRole('textbox', { name: /model json/i })
    expect(textarea).toHaveClass('font-mono')
  })

  it('invalid JSON shows error message', async () => {
    const user = userEvent.setup()
    renderWithProvider()

    // Check the checkbox
    const checkbox = screen.getByRole('checkbox', { name: /include model json/i })
    await user.click(checkbox)

    // Type invalid JSON using fireEvent (curly braces are special in userEvent)
    const textarea = screen.getByRole('textbox', { name: /model json/i })
    fireEvent.change(textarea, { target: { value: '{invalid json}' } })

    // Error message should appear (look for role="alert")
    expect(screen.getByRole('alert')).toBeInTheDocument()
    expect(screen.getByRole('alert')).toHaveTextContent(/Invalid JSON/i)
  })

  it('typing updates store', async () => {
    const user = userEvent.setup()
    renderWithProvider()

    // Check the checkbox
    const checkbox = screen.getByRole('checkbox', { name: /include model json/i })
    await user.click(checkbox)

    // Type in textarea using fireEvent (curly braces are special in userEvent)
    const textarea = screen.getByRole('textbox', { name: /model json/i })
    fireEvent.change(textarea, { target: { value: '{"test": true}' } })

    // Verify value
    expect(textarea).toHaveValue('{"test": true}')
  })

  it('shows modelFormat hint text', async () => {
    const user = userEvent.setup()
    renderWithProvider()

    // Check the checkbox
    const checkbox = screen.getByRole('checkbox', { name: /include model json/i })
    await user.click(checkbox)

    // Hint should be visible
    expect(screen.getByText(/modelformat/i)).toBeInTheDocument()
  })

  it('valid JSON does not show error', async () => {
    const user = userEvent.setup()
    renderWithProvider()

    // Check the checkbox
    const checkbox = screen.getByRole('checkbox', { name: /include model json/i })
    await user.click(checkbox)

    // Type valid JSON using fireEvent
    const textarea = screen.getByRole('textbox', { name: /model json/i })
    fireEvent.change(textarea, { target: { value: '{"valid": "json"}' } })

    // No error message should appear
    expect(screen.queryByText(/invalid json/i)).not.toBeInTheDocument()
  })

  it('empty textarea does not show error', async () => {
    const user = userEvent.setup()
    renderWithProvider()

    // Check the checkbox
    const checkbox = screen.getByRole('checkbox', { name: /include model json/i })
    await user.click(checkbox)

    // No error message should appear initially
    expect(screen.queryByText(/invalid json/i)).not.toBeInTheDocument()
  })
})
