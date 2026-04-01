import { useState } from 'react'
import { X, Save } from 'lucide-react'

export default function ScheduleEditModal({ isOpen, onClose, onSave, scheduleRow, currentUser }) {
    const [formData, setFormData] = useState({
        planned_production: scheduleRow?.planned_production || 0,
        capacity: scheduleRow?.capacity || 0,
        overtime_hours: scheduleRow?.overtime_hours || 0
    })

    const handleSave = () => {
        onSave(scheduleRow.id, {
            ...formData,
            updated_by: currentUser?.username || 'Admin'
        })
    }

    if (!isOpen) return null

    const demand = scheduleRow?.demand || 0
    const gap = demand - Math.min(formData.planned_production, formData.capacity)

    return (
        <div className="fixed inset-0 z-50 overflow-y-auto">
            <div className="fixed inset-0 bg-black bg-opacity-50" onClick={onClose} />
            <div className="flex min-h-full items-center justify-center p-4">
                <div className="relative w-full max-w-md bg-slate-900 rounded-lg shadow-xl p-6">
                    <div className="flex items-center justify-between mb-4">
                        <h2 className="text-xl font-bold">Edit Production Schedule</h2>
                        <button onClick={onClose} className="p-1 hover:bg-slate-700 rounded">
                            <X className="h-5 w-5" />
                        </button>
                    </div>

                    <div className="space-y-4">
                        <div className="p-3 bg-blue-50 rounded-lg">
                            <p className="text-sm text-slate-400">Week {scheduleRow?.week_number}</p>
                            <p className="font-semibold">Demand: {demand} units</p>
                        </div>

                        <div>
                            <label className="block text-sm font-medium mb-2">Planned Production</label>
                            <input
                                type="number"
                                value={formData.planned_production}
                                onChange={(e) => setFormData({ ...formData, planned_production: parseInt(e.target.value) || 0 })}
                                className="w-full px-4 py-2 border rounded-lg"
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium mb-2">Capacity</label>
                            <input
                                type="number"
                                value={formData.capacity}
                                onChange={(e) => setFormData({ ...formData, capacity: parseInt(e.target.value) || 0 })}
                                className="w-full px-4 py-2 border rounded-lg"
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium mb-2">Overtime Hours</label>
                            <input
                                type="number"
                                step="0.5"
                                value={formData.overtime_hours}
                                onChange={(e) => setFormData({ ...formData, overtime_hours: parseFloat(e.target.value) || 0 })}
                                className="w-full px-4 py-2 border rounded-lg"
                            />
                        </div>

                        <div className={`p-3 rounded-lg ${gap > 0 ? 'bg-red-50' : 'bg-green-50'}`}>
                            <p className="text-sm font-medium">Calculated Gap: {gap} units</p>
                            <p className="text-xs text-slate-400">
                                {gap > 0 ? 'Production below demand' : 'Production meets demand'}
                            </p>
                        </div>
                    </div>

                    <div className="flex justify-end gap-3 mt-6">
                        <button onClick={onClose} className="px-4 py-2 border rounded-lg">Cancel</button>
                        <button onClick={handleSave} className="px-4 py-2 bg-blue-600 text-white rounded-lg flex items-center gap-2">
                            <Save className="h-4 w-4" />
                            Save Changes
                        </button>
                    </div>
                </div>
            </div>
        </div>
    )
}
