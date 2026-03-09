'use client'

import { useState } from 'react'
import { useStore } from '@/lib/stores/context'
import { Checkbox } from '@/components/ui/checkbox'
import { Textarea } from '@/components/ui/textarea'
import { Button } from '@/components/ui/button'
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from '@/components/ui/collapsible'
import { ChevronDown, ChevronRight } from 'lucide-react'
import { cn } from '@/lib/utils'

/**
 * ModelJsonPanel - Collapsible JSON input for model configuration
 *
 * CONS-04: User can optionally expand JSON model input area
 * - Checkbox to enable/include model JSON
 * - Collapsible panel with textarea
 * - JSON validation with inline error display
 * - Monospace font for code readability
 */
export function ModelJsonPanel() {
  const includeModel = useStore((state) => state.includeModel)
  const modelText = useStore((state) => state.modelText)
  const setIncludeModel = useStore((state) => state.setIncludeModel)
  const setModelText = useStore((state) => state.setModelText)

  const [isOpen, setIsOpen] = useState(true)
  const [jsonError, setJsonError] = useState<string | null>(null)

  const validateJson = (value: string) => {
    if (!value.trim()) {
      setJsonError(null)
      return
    }

    try {
      JSON.parse(value)
      setJsonError(null)
    } catch (e) {
      setJsonError('Invalid JSON: ' + (e as Error).message)
    }
  }

  const handleModelTextChange = (value: string) => {
    setModelText(value)
    validateJson(value)
  }

  return (
    <div className="space-y-3">
      {/* Include Model Checkbox */}
      <div className="flex items-center space-x-2">
        <Checkbox
          id="include-model"
          aria-label="Include Model JSON"
          checked={includeModel}
          onCheckedChange={(checked) => setIncludeModel(checked === true)}
        />
        <label
          htmlFor="include-model"
          className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 cursor-pointer"
        >
          Include Model JSON
        </label>
      </div>

      {/* Collapsible JSON Panel */}
      {includeModel && (
        <Collapsible open={isOpen} onOpenChange={setIsOpen} className="space-y-2">
          <CollapsibleTrigger asChild>
            <Button
              variant="ghost"
              size="sm"
              className="flex items-center gap-1 px-2 h-7"
            >
              {isOpen ? (
                <ChevronDown className="h-4 w-4" />
              ) : (
                <ChevronRight className="h-4 w-4" />
              )}
              <span className="text-sm">Model JSON</span>
            </Button>
          </CollapsibleTrigger>

          <CollapsibleContent className="space-y-2">
            <Textarea
              aria-label="Model JSON"
              placeholder='{"modelFormat": "structuremodel-v1", ...}'
              rows={6}
              value={modelText}
              onChange={(e) => handleModelTextChange(e.target.value)}
              className={cn(
                'font-mono text-sm',
                jsonError && 'border-destructive'
              )}
            />

            {/* Hint Text */}
            <p className="text-xs text-muted-foreground">
              modelFormat: structuremodel-v1
            </p>

            {/* Error Message */}
            {jsonError && (
              <p className="text-xs text-destructive" role="alert">
                {jsonError}
              </p>
            )}
          </CollapsibleContent>
        </Collapsible>
      )}
    </div>
  )
}
