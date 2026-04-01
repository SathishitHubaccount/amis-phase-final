import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { Package, CheckCircle, Loader2, Plus, Minus } from 'lucide-react'
import Modal from './Modal'
import { apiClient } from '../lib/api'

export default function InventoryAdjustmentModal({ isOpen, onClose, productId, productName, currentStock }) {
  const queryClient = useQueryClient()
  const [formData, setFormData] = useState({
    adjustmentType: 'add',
    quantity: '',
    reason: '',
    user: 'Inventory Manager',
  })

  const [submitted, setSubmitted] = useState(false)

  const adjustInventoryMutation = useMutation({
    mutationFn: (adjustmentData) => {
      const finalQuantity = adjustmentData.adjustmentType === 'add'
        ? parseInt(adjustmentData.quantity)
        : -parseInt(adjustmentData.quantity)

      return apiClient.adjustInventory(
        productId,
        finalQuantity,
        adjustmentData.reason,
        adjustmentData.user
      )
    },
    onSuccess: () => {
      // Invalidate inventory cache to refresh the data
      queryClient.invalidateQueries({ queryKey: ['inventory', productId] })
      queryClient.invalidateQueries({ queryKey: ['inventory-history', productId] })
      setSubmitted(true)

      // Reset after 2 seconds
      setTimeout(() => {
        setSubmitted(false)
        setFormData({
          adjustmentType: 'add',
          quantity: '',
          reason: '',
          user: 'Inventory Manager',
        })
        onClose()
      }, 2000)
    },
    onError: (error) => {
      console.error('Error adjusting inventory:', error)
      alert('Failed to adjust inventory. Please check the quantity and try again.')
    },
  })

  const handleSubmit = (e) => {
    e.preventDefault()
    adjustInventoryMutation.mutate(formData)
  }

  const previewNewStock = () => {
    if (!formData.quantity) return currentStock
    const adjustment = formData.adjustmentType === 'add'
      ? parseInt(formData.quantity)
      : -parseInt(formData.quantity)
    return currentStock + adjustment
  }

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Adjust Inventory" size="md">
      {submitted ? (
        <div className="text-center py-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-green-100 rounded-full mb-4">
            <CheckCircle className="h-8 w-8 text-green-600" />
          </div>
          <h3 className="text-lg font-semibold text-white mb-2">Inventory Adjusted!</h3>
          <p className="text-sm text-slate-400">
            Inventory for {productName} has been successfully updated.
          </p>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Product Info */}
          <div className="p-4 bg-slate-800 rounded-lg">
            <h4 className="font-semibold text-white mb-2">Product Information</h4>
            <div className="grid grid-cols-2 gap-3 text-sm">
              <div>
                <span className="text-slate-400">Product ID:</span>
                <span className="ml-2 font-medium">{productId}</span>
              </div>
              <div>
                <span className="text-slate-400">Product Name:</span>
                <span className="ml-2 font-medium">{productName}</span>
              </div>
              <div>
                <span className="text-slate-400">Current Stock:</span>
                <span className="ml-2 font-medium text-blue-600">{currentStock} units</span>
              </div>
              <div>
                <span className="text-slate-400">New Stock:</span>
                <span className={`ml-2 font-medium ${
                  previewNewStock() < currentStock ? 'text-red-600' : 'text-green-600'
                }`}>
                  {previewNewStock()} units
                </span>
              </div>
            </div>
          </div>

          {/* Adjustment Type */}
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              Adjustment Type
            </label>
            <div className="grid grid-cols-2 gap-3">
              <button
                type="button"
                onClick={() => setFormData({ ...formData, adjustmentType: 'add' })}
                className={`px-4 py-3 border-2 rounded-lg font-medium transition-all flex items-center justify-center gap-2 ${
                  formData.adjustmentType === 'add'
                    ? 'bg-green-50 border-green-500 text-green-700'
                    : 'bg-slate-900 border-slate-800 text-slate-300 hover:border-slate-700'
                }`}
              >
                <Plus className="h-5 w-5" />
                Add Stock
              </button>
              <button
                type="button"
                onClick={() => setFormData({ ...formData, adjustmentType: 'remove' })}
                className={`px-4 py-3 border-2 rounded-lg font-medium transition-all flex items-center justify-center gap-2 ${
                  formData.adjustmentType === 'remove'
                    ? 'bg-red-50 border-red-500 text-red-700'
                    : 'bg-slate-900 border-slate-800 text-slate-300 hover:border-slate-700'
                }`}
              >
                <Minus className="h-5 w-5" />
                Remove Stock
              </button>
            </div>
          </div>

          {/* Quantity */}
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              Quantity
            </label>
            <input
              type="number"
              value={formData.quantity}
              onChange={(e) => setFormData({ ...formData, quantity: e.target.value })}
              placeholder="Enter quantity"
              min="1"
              className="w-full px-3 py-2 border border-slate-700 bg-slate-800 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              required
            />
            <p className="text-xs text-slate-500 mt-1">
              {formData.adjustmentType === 'add' ? 'Stock will increase by' : 'Stock will decrease by'} this amount
            </p>
          </div>

          {/* Reason */}
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              Reason for Adjustment
            </label>
            <select
              value={formData.reason}
              onChange={(e) => setFormData({ ...formData, reason: e.target.value })}
              className="w-full px-3 py-2 border border-slate-700 bg-slate-800 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 mb-2"
              required
            >
              <option value="">Select a reason</option>
              <option value="Cycle Count Adjustment">Cycle Count Adjustment</option>
              <option value="Received Shipment">Received Shipment</option>
              <option value="Production Return">Production Return</option>
              <option value="Damaged Goods">Damaged Goods</option>
              <option value="Quality Rejection">Quality Rejection</option>
              <option value="Lost/Stolen">Lost/Stolen</option>
              <option value="Transfer to Another Location">Transfer to Another Location</option>
              <option value="Other">Other</option>
            </select>
            {formData.reason === 'Other' && (
              <textarea
                placeholder="Please specify the reason..."
                rows={3}
                className="w-full px-3 py-2 border border-slate-700 bg-slate-800 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 resize-none"
                onChange={(e) => setFormData({ ...formData, reason: e.target.value })}
                required
              />
            )}
          </div>

          {/* User */}
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              Adjusted By
            </label>
            <input
              type="text"
              value={formData.user}
              onChange={(e) => setFormData({ ...formData, user: e.target.value })}
              className="w-full px-3 py-2 border border-slate-700 bg-slate-800 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              required
            />
          </div>

          {/* Warning for large removals */}
          {formData.adjustmentType === 'remove' && formData.quantity && parseInt(formData.quantity) > currentStock && (
            <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-sm text-red-800 font-medium">
                ⚠️ Warning: You are trying to remove more stock than is currently available. This operation will fail.
              </p>
            </div>
          )}

          {/* Actions */}
          <div className="flex gap-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              disabled={adjustInventoryMutation.isPending}
              className="flex-1 px-4 py-2.5 border border-slate-700 text-slate-300 rounded-lg font-medium hover:bg-slate-800 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={adjustInventoryMutation.isPending}
              className="flex-1 px-4 py-2.5 bg-gradient-to-r from-primary-600 to-accent-600 text-white rounded-lg font-medium hover:from-primary-700 hover:to-accent-700 transition-all shadow-lg shadow-primary-500/30 flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {adjustInventoryMutation.isPending ? (
                <>
                  <Loader2 className="h-5 w-5 animate-spin" />
                  Adjusting...
                </>
              ) : (
                <>
                  <Package className="h-5 w-5" />
                  Adjust Inventory
                </>
              )}
            </button>
          </div>
        </form>
      )}
    </Modal>
  )
}
