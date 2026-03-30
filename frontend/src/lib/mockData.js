// Enhanced Mock Data for Multiple Products
// In real production, this would come from ERP/MES databases

export const PRODUCTS = {
  'PROD-A': {
    id: 'PROD-A',
    name: 'Automotive Sensor Unit',
    category: 'Electronics',
    status: 'active',
    inventory: {
      currentStock: 1850,
      safetyStock: 500,
      reorderPoint: 800,
      avgDailyUsage: 120,
      leadTime: 7,
      stockoutRisk: 18,
    },
    bom: [
      { id: 'PCB-001', name: 'Main Circuit Board', quantity: 1, stock: 2400, supplier: 'SUP-001', cost: 12.50 },
      { id: 'SEN-002', name: 'Temperature Sensor', quantity: 2, stock: 4200, supplier: 'SUP-003', cost: 3.20 },
      { id: 'RES-003', name: 'Resistor Pack (10pc)', quantity: 1, stock: 15000, supplier: 'SUP-001', cost: 0.85 },
      { id: 'CAP-004', name: 'Capacitor Set', quantity: 1, stock: 8900, supplier: 'SUP-001', cost: 1.40 },
      { id: 'CASE-005', name: 'Plastic Housing', quantity: 1, stock: 1200, supplier: 'SUP-002', cost: 2.80 },
    ],
    demand: {
      historical: [1650, 1720, 1680, 1750, 1820, 1900, 1950],
      forecast: {
        optimistic: [2200, 2350, 2400, 2500],
        base: [2000, 2050, 2100, 2150],
        pessimistic: [1800, 1850, 1900, 1950],
      },
    },
  },
  'PROD-B': {
    id: 'PROD-B',
    name: 'Industrial Motor Assembly',
    category: 'Mechanical',
    status: 'active',
    inventory: {
      currentStock: 450,
      safetyStock: 150,
      reorderPoint: 250,
      avgDailyUsage: 35,
      leadTime: 14,
      stockoutRisk: 12,
    },
    bom: [
      { id: 'MOT-101', name: 'AC Motor 5HP', quantity: 1, stock: 520, supplier: 'SUP-003', cost: 245.00 },
      { id: 'BEAR-102', name: 'Ball Bearing Set', quantity: 4, stock: 2800, supplier: 'SUP-001', cost: 18.50 },
      { id: 'SHAFT-103', name: 'Steel Shaft', quantity: 1, stock: 680, supplier: 'SUP-004', cost: 32.00 },
      { id: 'HOUS-104', name: 'Aluminum Housing', quantity: 1, stock: 420, supplier: 'SUP-002', cost: 68.00 },
    ],
    demand: {
      historical: [380, 420, 390, 410, 440, 460, 475],
      forecast: {
        optimistic: [550, 580, 600, 620],
        base: [500, 520, 540, 560],
        pessimistic: [450, 470, 490, 510],
      },
    },
  },
  'PROD-C': {
    id: 'PROD-C',
    name: 'Smart Thermostat',
    category: 'Electronics',
    status: 'active',
    inventory: {
      currentStock: 3200,
      safetyStock: 800,
      reorderPoint: 1200,
      avgDailyUsage: 180,
      leadTime: 10,
      stockoutRisk: 8,
    },
    bom: [
      { id: 'DISP-201', name: 'LCD Display', quantity: 1, stock: 3800, supplier: 'SUP-001', cost: 8.90 },
      { id: 'PCB-202', name: 'Control Board', quantity: 1, stock: 3500, supplier: 'SUP-001', cost: 15.20 },
      { id: 'WIFI-203', name: 'WiFi Module', quantity: 1, stock: 4200, supplier: 'SUP-003', cost: 6.50 },
      { id: 'CASE-204', name: 'Front Panel', quantity: 1, stock: 2900, supplier: 'SUP-002', cost: 4.20 },
    ],
    demand: {
      historical: [2800, 2950, 3100, 3200, 3350, 3500, 3600],
      forecast: {
        optimistic: [4200, 4400, 4500, 4600],
        base: [3800, 3900, 4000, 4100],
        pessimistic: [3400, 3500, 3600, 3700],
      },
    },
  },
  'PROD-D': {
    id: 'PROD-D',
    name: 'Hydraulic Pump',
    category: 'Mechanical',
    status: 'active',
    inventory: {
      currentStock: 280,
      safetyStock: 100,
      reorderPoint: 150,
      avgDailyUsage: 22,
      leadTime: 21,
      stockoutRisk: 25,
    },
    bom: [
      { id: 'PUMP-301', name: 'Pump Body (Cast Iron)', quantity: 1, stock: 320, supplier: 'SUP-004', cost: 185.00 },
      { id: 'SEAL-302', name: 'Hydraulic Seal Kit', quantity: 1, stock: 580, supplier: 'SUP-003', cost: 28.50 },
      { id: 'VAL-303', name: 'Pressure Valve', quantity: 2, stock: 840, supplier: 'SUP-001', cost: 42.00 },
      { id: 'HOSE-304', name: 'Hydraulic Hose Assembly', quantity: 2, stock: 650, supplier: 'SUP-002', cost: 15.80 },
    ],
    demand: {
      historical: [220, 240, 250, 260, 270, 285, 290],
      forecast: {
        optimistic: [340, 360, 370, 380],
        base: [310, 320, 330, 340],
        pessimistic: [280, 290, 300, 310],
      },
    },
  },
  'PROD-E': {
    id: 'PROD-E',
    name: 'LED Display Panel',
    category: 'Electronics',
    status: 'limited',
    inventory: {
      currentStock: 95,
      safetyStock: 50,
      reorderPoint: 80,
      avgDailyUsage: 12,
      leadTime: 45,
      stockoutRisk: 42,
    },
    bom: [
      { id: 'LED-401', name: 'LED Matrix Array', quantity: 1, stock: 120, supplier: 'SUP-003', cost: 95.00 },
      { id: 'DRV-402', name: 'LED Driver IC', quantity: 4, stock: 580, supplier: 'SUP-001', cost: 12.30 },
      { id: 'FRAME-403', name: 'Aluminum Frame', quantity: 1, stock: 88, supplier: 'SUP-002', cost: 42.00 },
      { id: 'PWR-404', name: 'Power Supply Unit', quantity: 1, stock: 150, supplier: 'SUP-001', cost: 38.50 },
    ],
    demand: {
      historical: [85, 92, 88, 95, 102, 110, 115],
      forecast: {
        optimistic: [140, 150, 155, 160],
        base: [125, 130, 135, 140],
        pessimistic: [110, 115, 120, 125],
      },
    },
  },
}

export const MACHINES_BY_PRODUCT = {
  'PROD-A': ['MCH-001', 'MCH-002', 'MCH-005'],
  'PROD-B': ['MCH-003'],
  'PROD-C': ['MCH-001', 'MCH-005'],
  'PROD-D': ['MCH-004'],
  'PROD-E': ['MCH-002', 'MCH-003'],
}

export const MACHINES = {
  'MCH-001': {
    id: 'MCH-001',
    name: 'Stamping Press A',
    type: 'Stamping',
    line: 'Line 1',
    status: 'healthy',
    oee: 87,
    availability: 92,
    performance: 95,
    quality: 100,
    failureRisk: 8,
    lastMaintenance: '2026-01-15',
    nextMaintenance: '2026-03-15',
    productionCapacity: 50,
    currentUtilization: 94,
    alarms: [
      { id: 1, time: '2026-02-27 14:22', severity: 'low', message: 'Oil pressure slightly below optimal' },
    ],
    maintenanceHistory: [
      { date: '2026-01-15', type: 'Preventive', technician: 'John Smith', duration: '2h', notes: 'Replaced hydraulic fluid' },
      { date: '2025-12-10', type: 'Corrective', technician: 'Maria Garcia', duration: '4h', notes: 'Fixed sensor calibration' },
    ],
    spareParts: [
      { part: 'Hydraulic Seal', stock: 5, minStock: 2, status: 'OK' },
      { part: 'Pressure Sensor', stock: 1, minStock: 2, status: 'LOW' },
    ],
  },
  'MCH-002': {
    id: 'MCH-002',
    name: 'Assembly Robot B',
    type: 'Robotic Assembly',
    line: 'Line 2',
    status: 'at_risk',
    oee: 64,
    availability: 78,
    performance: 85,
    quality: 96,
    failureRisk: 47,
    lastMaintenance: '2025-11-20',
    nextMaintenance: '2026-02-28',
    productionCapacity: 45,
    currentUtilization: 78,
    alarms: [
      { id: 2, time: '2026-02-28 09:15', severity: 'high', message: 'Gripper actuator showing increased cycle time' },
      { id: 3, time: '2026-02-27 16:40', severity: 'medium', message: 'Vision system alignment drift detected' },
    ],
    maintenanceHistory: [
      { date: '2025-11-20', type: 'Preventive', technician: 'David Lee', duration: '3h', notes: 'Lubrication and calibration' },
    ],
    spareParts: [
      { part: 'Gripper Assembly', stock: 0, minStock: 1, status: 'CRITICAL' },
      { part: 'Vision Camera', stock: 2, minStock: 1, status: 'OK' },
    ],
  },
  'MCH-003': {
    id: 'MCH-003',
    name: 'Quality Scanner C',
    type: 'Inspection',
    line: 'Line 3',
    status: 'healthy',
    oee: 91,
    availability: 96,
    performance: 95,
    quality: 100,
    failureRisk: 12,
    lastMaintenance: '2026-02-01',
    nextMaintenance: '2026-04-01',
    productionCapacity: 60,
    currentUtilization: 88,
    alarms: [],
    maintenanceHistory: [
      { date: '2026-02-01', type: 'Preventive', technician: 'Sarah Johnson', duration: '1h', notes: 'Lens cleaning and calibration check' },
    ],
    spareParts: [
      { part: 'Scanner Lens', stock: 3, minStock: 2, status: 'OK' },
      { part: 'Light Source', stock: 4, minStock: 2, status: 'OK' },
    ],
  },
  'MCH-004': {
    id: 'MCH-004',
    name: 'Welding Station D',
    type: 'Welding',
    line: 'Maintenance',
    status: 'critical',
    oee: 45,
    availability: 50,
    performance: 90,
    quality: 100,
    failureRisk: 78,
    lastMaintenance: '2026-02-20',
    nextMaintenance: '2026-02-23',
    productionCapacity: 40,
    currentUtilization: 0,
    alarms: [
      { id: 4, time: '2026-02-20 11:00', severity: 'critical', message: 'Welding transformer failure - machine down' },
    ],
    maintenanceHistory: [
      { date: '2026-02-20', type: 'Breakdown', technician: 'Robert Chen', duration: 'Ongoing', notes: 'Waiting for transformer replacement part' },
    ],
    spareParts: [
      { part: 'Welding Transformer', stock: 0, minStock: 1, status: 'CRITICAL' },
      { part: 'Welding Tips', stock: 15, minStock: 10, status: 'OK' },
    ],
  },
  'MCH-005': {
    id: 'MCH-005',
    name: 'Packaging Unit E',
    type: 'Packaging',
    line: 'Line 5',
    status: 'healthy',
    oee: 83,
    availability: 88,
    performance: 94,
    quality: 100,
    failureRisk: 6,
    lastMaintenance: '2026-02-10',
    nextMaintenance: '2026-03-10',
    productionCapacity: 55,
    currentUtilization: 0,
    alarms: [],
    maintenanceHistory: [
      { date: '2026-02-10', type: 'Preventive', technician: 'Emily Brown', duration: '2h', notes: 'Belt tension adjustment and sensor check' },
    ],
    spareParts: [
      { part: 'Conveyor Belt', stock: 2, minStock: 1, status: 'OK' },
      { part: 'Proximity Sensor', stock: 8, minStock: 5, status: 'OK' },
    ],
  },
}

export const SUPPLIERS = {
  'SUP-001': {
    id: 'SUP-001',
    name: 'Global Parts Co.',
    location: 'Detroit, USA',
    score: 92,
    rating: 'A',
    onTimeDelivery: 96,
    quality: 98,
    costIndex: 102,
    baseCost: 51.20,
    leadTime: 7,
    leadTimeVariability: 1,
    risk: 'Low',
    certifications: ['ISO-9001', 'IATF-16949', 'ISO-14001'],
    moq: 1000,
    paymentTerms: 'Net 30',
    currency: 'USD',
    contracts: [
      { id: 'CNT-2025-001', startDate: '2025-01-01', endDate: '2026-12-31', volume: 50000, status: 'active' },
    ],
    incidents: [
      { date: '2025-08-15', type: 'Quality', severity: 'low', resolution: 'Replaced defective batch' },
    ],
  },
  'SUP-002': {
    id: 'SUP-002',
    name: 'Precision Manufacturing Ltd.',
    location: 'Toronto, Canada',
    score: 78,
    rating: 'B',
    onTimeDelivery: 82,
    quality: 91,
    costIndex: 96,
    baseCost: 48.30,
    leadTime: 10,
    leadTimeVariability: 3,
    risk: 'Medium',
    certifications: ['ISO-9001'],
    moq: 500,
    paymentTerms: 'Net 45',
    currency: 'CAD',
    contracts: [
      { id: 'CNT-2024-008', startDate: '2024-06-01', endDate: '2026-05-31', volume: 25000, status: 'active' },
    ],
    incidents: [
      { date: '2026-02-25', type: 'Delivery', severity: 'medium', resolution: 'PO-2026-002 delayed 3 days' },
      { date: '2025-11-10', type: 'Quality', severity: 'medium', resolution: '5% batch rejected' },
    ],
  },
  'SUP-003': {
    id: 'SUP-003',
    name: 'Eastern Components Inc.',
    location: 'Shenzhen, China',
    score: 85,
    rating: 'B+',
    onTimeDelivery: 88,
    quality: 94,
    costIndex: 89,
    baseCost: 49.80,
    leadTime: 12,
    leadTimeVariability: 4,
    risk: 'Low',
    certifications: ['ISO-9001', 'ISO-14001', 'RoHS'],
    moq: 2000,
    paymentTerms: 'LC at Sight',
    currency: 'CNY',
    contracts: [
      { id: 'CNT-2025-015', startDate: '2025-03-01', endDate: '2027-02-28', volume: 75000, status: 'active' },
    ],
    incidents: [],
  },
  'SUP-004': {
    id: 'SUP-004',
    name: 'Quality Supplies LLC',
    location: 'Mexico City, Mexico',
    score: 68,
    rating: 'C+',
    onTimeDelivery: 74,
    quality: 85,
    costIndex: 84,
    baseCost: 45.00,
    leadTime: 14,
    leadTimeVariability: 6,
    risk: 'High',
    certifications: ['ISO-9001'],
    moq: 500,
    paymentTerms: 'Net 60',
    currency: 'MXN',
    contracts: [
      { id: 'CNT-2023-042', startDate: '2023-09-01', endDate: '2026-08-31', volume: 15000, status: 'review' },
    ],
    incidents: [
      { date: '2026-01-20', type: 'Delivery', severity: 'high', resolution: 'Shipment delayed 7 days' },
      { date: '2025-10-05', type: 'Quality', severity: 'high', resolution: '12% batch rejected' },
      { date: '2025-07-12', type: 'Delivery', severity: 'medium', resolution: 'Partial shipment only' },
    ],
  },
}

// Activity Log (for audit trail)
export const ACTIVITY_LOG = []

export function logActivity(user, action, details) {
  const entry = {
    id: Date.now(),
    timestamp: new Date().toISOString(),
    user: user || 'System User',
    action,
    details,
  }
  ACTIVITY_LOG.unshift(entry)
  // Keep only last 100 entries
  if (ACTIVITY_LOG.length > 100) {
    ACTIVITY_LOG.pop()
  }
  return entry
}
