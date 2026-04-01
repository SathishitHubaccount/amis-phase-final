import { useState, useEffect } from 'react'
import { X, Wrench, AlertCircle } from 'lucide-react'

export default function WorkOrderModal({ isOpen, onClose, onSubmit, machines: machinesProp, currentUser }) {
  const [machines, setMachines] = useState(machinesProp || [])

  useEffect(() => {
    if (isOpen) {
      if (machinesProp && machinesProp.length > 0) {
        setMachines(machinesProp)
      } else {
        fetch('/api/machines')
          .then(r => r.json())
          .then(d => setMachines(d.machines || []))
          .catch(() => {})
      }
    }
  }, [isOpen, machinesProp])
  const [formData, setFormData] = useState({
    machine_id: '',
    type: 'preventive',
    priority: 'medium',
    assigned_to: '',
    scheduled_date: '',
    estimated_duration: '',
    description: '',
    created_by: currentUser?.username || 'Admin'
  })

  const [errors, setErrors] = useState({})

  const workOrderTypes = [
    { value: 'preventive', label: 'Preventive Maintenance' },
    { value: 'corrective', label: 'Corrective Maintenance' },
    { value: 'inspection', label: 'Inspection' },
    { value: 'calibration', label: 'Calibration' },
    { value: 'emergency', label: 'Emergency Repair' }
  ]

  const priorityLevels = [
    { value: 'low', label: 'Low', color: 'text-green-600' },
    { value: 'medium', label: 'Medium', color: 'text-yellow-600' },
    { value: 'high', label: 'High', color: 'text-orange-600' },
    { value: 'critical', label: 'Critical', color: 'text-red-600' }
  ]

  const techniciansList = [
    'John Martinez',
    'Sarah Chen',
    'Mike Johnson',
    'Emily Davis',
    'Robert Kim',
    'Unassigned'
  ]

  const validate = () => {
    const newErrors = {}

    if (!formData.machine_id) newErrors.machine_id = 'Machine is required'
    if (!formData.type) newErrors.type = 'Type is required'
    if (!formData.priority) newErrors.priority = 'Priority is required'
    if (!formData.scheduled_date) newErrors.scheduled_date = 'Scheduled date is required'
    if (!formData.description || formData.description.trim().length < 10) {
      newErrors.description = 'Description must be at least 10 characters'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = (e) => {
    e.preventDefault()

    if (!validate()) return

    // Convert estimated_duration to number
    const submitData = {
      ...formData,
      estimated_duration: formData.estimated_duration ? parseFloat(formData.estimated_duration) : null
    }

    onSubmit(submitData)
    handleClose()
  }

  const handleClose = () => {
    setFormData({
      machine_id: '',
      type: 'preventive',
      priority: 'medium',
      assigned_to: '',
      scheduled_date: '',
      estimated_duration: '',
      description: '',
      created_by: currentUser?.username || 'Admin'
    })
    setErrors({})
    onClose()
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      {/* Backdrop */}
      <div className="fixed inset-0 bg-black bg-opacity-50 transition-opacity" onClick={handleClose} />

      {/* Modal */}
      <div className="flex min-h-full items-center justify-center p-4">
        <div className="relative w-full max-w-2xl bg-slate-900 rounded-lg shadow-xl">
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-slate-800">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-500/15 rounded-lg border border-blue-500/20">
                <Wrench className="h-6 w-6 text-blue-400" />
              </div>
              <div>
                <h2 className="text-xl font-bold text-white">Create Work Order</h2>
                <p className="text-sm text-slate-500">Schedule maintenance or repair work</p>
              </div>
            </div>
            <button
              onClick={handleClose}
              className="p-2 hover:bg-slate-700 rounded-lg transition-colors"
            >
              <X className="h-5 w-5 text-slate-500" />
            </button>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="p-6">
            <div className="grid grid-cols-2 gap-6">
              {/* Machine Selection */}
              <div className="col-span-2">
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Machine *
                </label>
                <select
                  value={formData.machine_id}
                  onChange={(e) => setFormData({ ...formData, machine_id: e.target.value })}
                  className={`w-full px-4 py-2 border rounded-lg bg-slate-800 text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                    errors.machine_id ? 'border-red-500' : 'border-slate-700'
                  }`}
                >
                  <option value="">Select a machine...</option>
                  {machines?.map((machine) => (
                    <option key={machine.id} value={machine.id}>
                      {machine.id} - {machine.name}
                    </option>
                  ))}
                </select>
                {errors.machine_id && (
                  <p className="mt-1 text-sm text-red-600 flex items-center gap-1">
                    <AlertCircle className="h-4 w-4" />
                    {errors.machine_id}
                  </p>
                )}
              </div>

              {/* Work Order Type */}
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Type *
                </label>
                <select
                  value={formData.type}
                  onChange={(e) => setFormData({ ...formData, type: e.target.value })}
                  className="w-full px-4 py-2 border border-slate-700 bg-slate-800 text-white rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  {workOrderTypes.map((type) => (
                    <option key={type.value} value={type.value}>
                      {type.label}
                    </option>
                  ))}
                </select>
              </div>

              {/* Priority */}
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Priority *
                </label>
                <select
                  value={formData.priority}
                  onChange={(e) => setFormData({ ...formData, priority: e.target.value })}
                  className="w-full px-4 py-2 border border-slate-700 bg-slate-800 text-white rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  {priorityLevels.map((priority) => (
                    <option key={priority.value} value={priority.value}>
                      {priority.label}
                    </option>
                  ))}
                </select>
              </div>

              {/* Assigned To */}
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Assigned To
                </label>
                <select
                  value={formData.assigned_to}
                  onChange={(e) => setFormData({ ...formData, assigned_to: e.target.value })}
                  className="w-full px-4 py-2 border border-slate-700 bg-slate-800 text-white rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">Select technician...</option>
                  {techniciansList.map((tech) => (
                    <option key={tech} value={tech}>
                      {tech}
                    </option>
                  ))}
                </select>
              </div>

              {/* Scheduled Date */}
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Scheduled Date *
                </label>
                <input
                  type="date"
                  value={formData.scheduled_date}
                  onChange={(e) => setFormData({ ...formData, scheduled_date: e.target.value })}
                  min={new Date().toISOString().split('T')[0]}
                  className={`w-full px-4 py-2 border rounded-lg bg-slate-800 text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                    errors.scheduled_date ? 'border-red-500' : 'border-slate-700'
                  }`}
                />
                {errors.scheduled_date && (
                  <p className="mt-1 text-sm text-red-600">{errors.scheduled_date}</p>
                )}
              </div>

              {/* Estimated Duration */}
              <div className="col-span-2">
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Estimated Duration (hours)
                </label>
                <input
                  type="number"
                  step="0.5"
                  min="0"
                  value={formData.estimated_duration}
                  onChange={(e) => setFormData({ ...formData, estimated_duration: e.target.value })}
                  placeholder="e.g., 2.5"
                  className="w-full px-4 py-2 border border-slate-700 bg-slate-800 text-white rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              {/* Description */}
              <div className="col-span-2">
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Description *
                </label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  rows={4}
                  placeholder="Describe the work to be performed, parts needed, safety precautions, etc."
                  className={`w-full px-4 py-2 border rounded-lg bg-slate-800 text-white placeholder-slate-500 focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                    errors.description ? 'border-red-500' : 'border-slate-700'
                  }`}
                />
                <div className="flex justify-between items-center mt-1">
                  {errors.description && (
                    <p className="text-sm text-red-600 flex items-center gap-1">
                      <AlertCircle className="h-4 w-4" />
                      {errors.description}
                    </p>
                  )}
                  <p className="text-sm text-slate-500 ml-auto">
                    {formData.description.length} characters
                  </p>
                </div>
              </div>
            </div>

            {/* Actions */}
            <div className="flex justify-end gap-3 mt-6 pt-6 border-t border-slate-800">
              <button
                type="button"
                onClick={handleClose}
                className="px-6 py-2 border border-slate-700 bg-slate-800 text-white rounded-lg text-slate-300 hover:bg-slate-800 transition-colors"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
              >
                <Wrench className="h-4 w-4" />
                Create Work Order
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}
