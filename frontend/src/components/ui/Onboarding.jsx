import React, { useState } from "react"
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from "./card"
import { Button } from "./button"
import { Input } from "./input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./select"

const QUESTIONS = [
  { key: "name", label: "What is your name?", type: "text", placeholder: "Enter your name" },
  { key: "age", label: "How old are you?", type: "number", placeholder: "Enter your age" },
  { key: "gender", label: "What is your gender?", type: "select", options: ["Male", "Female"] }
]

export default function Onboarding({ onComplete }) {
  const [step, setStep] = useState(0)
  const [answers, setAnswers] = useState({})
  const [error, setError] = useState("")

  const q = QUESTIONS[step]

  const handleNext = (e) => {
    e.preventDefault()
    const val = answers[q.key]
    if (!val || (typeof val === "string" && !val.trim())) {
      setError("Please answer the question.")
      return
    }
    setError("")
    if (step < QUESTIONS.length - 1) {
      setStep(step + 1)
    } else {
      onComplete(answers)
    }
  }

  const handlePrev = () => {
    if (step > 0) {
      setError("")
      setStep(step - 1)
    }
  }

  const handleValueChange = (key, value) => {
    setAnswers((prev) => ({ ...prev, [key]: value }))
    setError("")
  }

  return (
    <div className="fixed inset-0 flex items-center justify-center bg-black/50 z-50">
      <Card className="w-96 p-4">
        <form onSubmit={handleNext}>
          <CardHeader className="p-2">
            <CardTitle className="text-xl">Onboarding</CardTitle>
            <div className="text-xs text-muted-foreground">
              Question {step + 1} of {QUESTIONS.length}
            </div>
          </CardHeader>
          <CardContent className="p-2 py-4 space-y-4">
            <div className="font-medium text-sm">{q.label}</div>
            {q.type === "select" ? (
              <Select
                value={answers[q.key] || ""}
                onValueChange={(val) => handleValueChange(q.key, val)}
              >
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Select gender" />
                </SelectTrigger>
                <SelectContent>
                  {q.options.map((opt) => (
                    <SelectItem key={opt} value={opt}>
                      {opt}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            ) : (
              <Input
                type={q.type}
                placeholder={q.placeholder}
                value={answers[q.key] || ""}
                onChange={(e) => handleValueChange(q.key, e.target.value)}
                autoFocus
              />
            )}
            {error && <div className="text-xs text-destructive">{error}</div>}
          </CardContent>
          <CardFooter className="p-2 flex justify-between">
            {step > 0 && (
              <Button type="button" variant="outline" onClick={handlePrev}>
                Back
              </Button>
            )}
            <Button type="submit" className="ml-auto">
              {step === QUESTIONS.length - 1 ? "Finish" : "Next"}
            </Button>
          </CardFooter>
        </form>
      </Card>
    </div>
  )
}
