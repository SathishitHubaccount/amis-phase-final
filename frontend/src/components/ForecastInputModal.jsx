import { useState, useEffect } from 'react'
import { X, TrendingUp, AlertCircle } from 'lucide-react'

export default function ForecastInputModal({ isOpen, onClose, onSubmit, productId, aiSuggestion }) {
    const [formData, setFormData] = useState({
        week_number: '',
        forecast_date: '',
        optimistic: '',
        base_case: '',
        pessimistic: '',
    })

    const [errors, setErrors] = useState({})

    // Pre-fill with AI suggestion when available
    useEffect(() => {
        if (aiSuggestion && aiSuggestion.base_case) {
            setFormData(prev => ({
                ...prev,
                base_case: aiSuggestion.base_case.toString(),
                optimistic: aiSuggestion.optimistic?.toString() || '',
                pessimistic: aiSuggestion.pessimistic?.toString() || ''
            }))
        }
    }, [aiSuggestion])

    const validate = () => {
        const newErrors = {}
        if (!formData.week_number) newErrors.week_number = 'Week number required'
        if (!formData.forecast_date) newErrors.forecast_date = 'Date required'
        if (!formData.base_case) newErrors.base_case = 'Base case required'

        const base = parseInt(formData.base_case)
        const optimistic = parseInt(formData.optimistic)
        const pessimistic = parseInt(formData.pessimistic)

        if (optimistic && optimistic < base) newErrors.optimistic = 'Must be >= base case'
        if (pessimistic && pessimistic > base) newErrors.pessimistic = 'Must be <= base case'

        setErrors(newErrors)
        return Object.keys(newErrors).length === 0
    }

    const handleSubmit = (e) => {
        e.preventDefault()
        if (!validate()) return

        onSubmit({
            product_id: productId,
            week_number: parseInt(formData.week_number),
            forecast_date: formData.forecast_date,
            optimistic: parseInt(formData.optimistic) || parseInt(formData.base_case),
            base_case: parseInt(formData.base_case),
            pessimistic: parseInt(formData.pessimistic) || parseInt(formData.base_case),
        })

        setFormData({ week_number: '', forecast_date: '', optimistic: '', base_case: '', pessimistic: '' })
        setErrors({})
        onClose()
    }

    if (!isOpen) return null

    return (
        <div className="fixed inset-0 z-50 overflow-y-auto">
            <div className="fixed inset-0 bg-black bg-opacity-50" onClick={onClose} />
            <div className="flex min-h-full items-center justify-center p-4">
                <div className="relative w-full max-w-md bg-slate-900 rounded-lg shadow-xl p-6">
                    <div className="flex items-center justify-between mb-4">
                        <h2 className="text-xl font-bold">Add Demand Forecast</h2>
                        <button onClick={onClose} className="p-1 hover:bg-slate-700 rounded">
                            <X className="h-5 w-5" />
                        </button>
                    </div>

                    {/* AI Suggestion Badge */}
                    {aiSuggestion && aiSuggestion.base_case && (
                        <div className="mb-4 p-3 bg-purple-50 border border-purple-200 rounded-lg">
                            <div className="flex items-center gap-2 mb-1">
                                <TrendingUp className="h-4 w-4 text-purple-600" />
                                <p className="text-xs text-purple-900 font-medium">🤖 AI-Assisted Forecast</p>
                            </div>
                            <p className="text-xs text-purple-800">
                                Values pre-filled from latest AI analysis. You can adjust them before saving.
                            </p>
                        </div>
                    )}

                    {/* Help Text */}
                    <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                        <p className="text-xs text-blue-900 font-medium mb-1">📘 How to Create a Forecast</p>
                        <ul className="text-xs text-blue-800 space-y-0.5">
                            <li>• <strong>Base Case</strong>: Your most likely demand estimate (55% probability)</li>
                            <li>• <strong>Optimistic</strong>: Best-case scenario if things go well (+20% typically)</li>
                            <li>• <strong>Conservative</strong>: Worst-case if demand drops (-20% typically)</li>
                        </ul>
                    </div>

                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium mb-1">
                                Week Start Date <span className="text-red-500">*</span>
                            </label>
                            <input
                                type="date"
                                value={formData.forecast_date}
                                onChange={(e) => {
                                    setFormData({ ...formData, forecast_date: e.target.value })
                                    // Auto-calculate week number from date
                                    if (e.target.value) {
                                        const date = new Date(e.target.value)
                                        const weekNum = Math.ceil((date - new Date(date.getFullYear(), 0, 1)) / 604800000)
                                        setFormData(prev => ({ ...prev, week_number: weekNum.toString(), forecast_date: e.target.value }))
                                    }
                                }}
                                className={`w-full px-3 py-2 border rounded-lg ${errors.forecast_date ? 'border-red-500' : ''}`}
                                placeholder="Select week start date"
                            />
                            {formData.forecast_date && (
                                <p className="text-xs text-slate-500 mt-1">Week {formData.week_number} of 2026</p>
                            )}
                            {errors.forecast_date && <p className="text-red-500 text-sm">{errors.forecast_date}</p>}
                        </div>

                        <div>
                            <label className="block text-sm font-medium mb-1">
                                Base Case Demand <span className="text-red-500">*</span>
                                <span className="text-xs text-slate-500 ml-2">(Most likely scenario - 55% probability)</span>
                            </label>
                            <div className="relative">
                                <input
                                    type="number"
                                    value={formData.base_case}
                                    onChange={(e) => {
                                        const baseValue = e.target.value
                                        setFormData({
                                            ...formData,
                                            base_case: baseValue,
                                            // Auto-suggest optimistic (+20%) and pessimistic (-20%)
                                            optimistic: baseValue ? Math.round(parseInt(baseValue) * 1.2).toString() : '',
                                            pessimistic: baseValue ? Math.round(parseInt(baseValue) * 0.8).toString() : ''
                                        })
                                    }}
                                    className={`w-full px-3 py-2 border rounded-lg ${errors.base_case ? 'border-red-500' : ''}`}
                                    placeholder="e.g., 1400"
                                />
                                <span className="absolute right-3 top-2.5 text-slate-500 text-sm">units</span>
                            </div>
                            {errors.base_case && <p className="text-red-500 text-sm">{errors.base_case}</p>}
                        </div>

                        <div className="grid grid-cols-2 gap-3">
                            <div>
                                <label className="block text-sm font-medium mb-1">
                                    Optimistic Scenario
                                    <span className="text-xs text-slate-500 block">(20% probability)</span>
                                </label>
                                <div className="relative">
                                    <input
                                        type="number"
                                        value={formData.optimistic}
                                        onChange={(e) => setFormData({ ...formData, optimistic: e.target.value })}
                                        className={`w-full px-3 py-2 border rounded-lg ${errors.optimistic ? 'border-red-500' : ''}`}
                                        placeholder="Auto-filled"
                                    />
                                    <span className="absolute right-3 top-2.5 text-slate-500 text-xs">units</span>
                                </div>
                                {errors.optimistic && <p className="text-red-500 text-xs">{errors.optimistic}</p>}
                            </div>

                            <div>
                                <label className="block text-sm font-medium mb-1">
                                    Conservative Scenario
                                    <span className="text-xs text-slate-500 block">(25% probability)</span>
                                </label>
                                <div className="relative">
                                    <input
                                        type="number"
                                        value={formData.pessimistic}
                                        onChange={(e) => setFormData({ ...formData, pessimistic: e.target.value })}
                                        className={`w-full px-3 py-2 border rounded-lg ${errors.pessimistic ? 'border-red-500' : ''}`}
                                        placeholder="Auto-filled"
                                    />
                                    <span className="absolute right-3 top-2.5 text-slate-500 text-xs">units</span>
                                </div>
                                {errors.pessimistic && <p className="text-red-500 text-xs">{errors.pessimistic}</p>}
                            </div>
                        </div>

                        {formData.base_case && (
                            <div className="p-3 bg-slate-800 rounded-lg border border-slate-800">
                                <p className="text-xs font-medium text-slate-300 mb-2">📊 Forecast Range Preview</p>
                                <div className="flex justify-between text-xs text-slate-400">
                                    <div className="text-center">
                                        <p className="text-red-600 font-semibold">{formData.pessimistic || '-'}</p>
                                        <p className="text-slate-500">Conservative</p>
                                    </div>
                                    <div className="text-center">
                                        <p className="text-blue-600 font-semibold text-base">{formData.base_case}</p>
                                        <p className="text-slate-500">Base Case</p>
                                    </div>
                                    <div className="text-center">
                                        <p className="text-green-600 font-semibold">{formData.optimistic || '-'}</p>
                                        <p className="text-slate-500">Optimistic</p>
                                    </div>
                                </div>
                            </div>
                        )}

                        <div className="flex justify-end gap-3 pt-4">
                            <button type="button" onClick={onClose} className="px-4 py-2 border rounded-lg">Cancel</button>
                            <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded-lg">Add Forecast</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    )
}
