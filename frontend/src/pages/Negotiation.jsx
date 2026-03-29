import React, { useState } from 'react';
import Card, { CardContent, CardHeader } from '../components/Card';
import { Play, AlertTriangle, CheckCircle, Clock, TrendingUp, Package, Wrench, DollarSign } from 'lucide-react';

export default function Negotiation() {
  const [selectedScenario, setSelectedScenario] = useState('demand_spike');
  const [negotiating, setNegotiating] = useState(false);
  const [result, setResult] = useState(null);
  const [currentRound, setCurrentRound] = useState(0);
  const [error, setError] = useState(null);

  const scenarios = {
    demand_spike: {
      title: 'Demand Spike Crisis',
      icon: TrendingUp,
      description: 'Customer emergency order exceeds normal production capacity',
      details: {
        customerOrder: 2000,
        timelineDays: 3,
        normalCapacity: 1500,
        gap: 500,
      },
      color: 'blue'
    },
    supplier_failure: {
      title: 'Supplier Failure',
      icon: Package,
      description: 'Primary supplier cannot deliver critical components',
      details: {
        missingComponents: 500,
        productionImpact: '5 days',
        alternativesAvailable: 2,
        costPremium: '25%',
      },
      color: 'orange'
    },
    machine_breakdown: {
      title: 'Machine Breakdown',
      icon: Wrench,
      description: 'Critical manufacturing equipment has failed',
      details: {
        machineId: 'MCH-004',
        repairTime: '5 days',
        repairCost: '$40,000',
        alternativeCapacity: '60%',
      },
      color: 'red'
    },
    cost_pressure: {
      title: 'Cost Reduction Pressure',
      icon: DollarSign,
      description: 'Need to reduce costs by 15% while maintaining quality',
      details: {
        targetReduction: '15%',
        currentCost: '$50/unit',
        qualityMustMaintain: true,
        volumeUnchanged: true,
      },
      color: 'green'
    }
  };

  const runNegotiation = async () => {
    setNegotiating(true);
    setResult(null);
    setError(null);
    setCurrentRound(0);

    // Simulate round-by-round progression
    setTimeout(() => setCurrentRound(1), 1000);
    setTimeout(() => setCurrentRound(2), 3000);
    setTimeout(() => setCurrentRound(3), 5000);

    try {
      const response = await fetch('http://localhost:8000/api/negotiation/run', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          scenario_type: selectedScenario,
          product_id: 'PROD-A',
          customer_order: 2000,
          timeline_days: 3
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setResult(data.result);
      setCurrentRound(4); // Completed
    } catch (err) {
      console.error('Negotiation error:', err);
      setError(err.message);
    } finally {
      setNegotiating(false);
    }
  };

  const ScenarioIcon = scenarios[selectedScenario].icon;
  const scenarioColor = scenarios[selectedScenario].color;

  const colorClasses = {
    blue: {
      border: 'border-blue-200',
      bg: 'bg-blue-50',
      text: 'text-blue-900',
      badge: 'bg-blue-100 text-blue-800'
    },
    orange: {
      border: 'border-orange-200',
      bg: 'bg-orange-50',
      text: 'text-orange-900',
      badge: 'bg-orange-100 text-orange-800'
    },
    red: {
      border: 'border-red-200',
      bg: 'bg-red-50',
      text: 'text-red-900',
      badge: 'bg-red-100 text-red-800'
    },
    green: {
      border: 'border-green-200',
      bg: 'bg-green-50',
      text: 'text-green-900',
      badge: 'bg-green-100 text-green-800'
    }
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">Agent Negotiation System</h1>
        <p className="text-gray-600">
          Watch specialized AI agents debate complex manufacturing decisions and reach consensus
        </p>
      </div>

      {/* Scenario Selection */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {Object.entries(scenarios).map(([key, scenario]) => {
          const Icon = scenario.icon;
          const isSelected = selectedScenario === key;
          const colors = colorClasses[scenario.color];

          return (
            <button
              key={key}
              onClick={() => setSelectedScenario(key)}
              disabled={negotiating}
              className={`p-4 rounded-lg border-2 transition-all text-left ${
                isSelected
                  ? `${colors.border} ${colors.bg} shadow-md`
                  : 'border-gray-200 bg-white hover:border-gray-300'
              } ${negotiating ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
            >
              <div className="flex items-center gap-2 mb-2">
                <Icon className={`h-5 w-5 ${isSelected ? colors.text : 'text-gray-600'}`} />
                <span className={`font-semibold ${isSelected ? colors.text : 'text-gray-900'}`}>
                  {scenario.title}
                </span>
              </div>
              <p className="text-sm text-gray-600">{scenario.description}</p>
            </button>
          );
        })}
      </div>

      {/* Selected Scenario Details */}
      <Card className={`mb-6 ${colorClasses[scenarioColor].border} ${colorClasses[scenarioColor].bg}`}>
        <CardHeader>
          <div className="flex items-center gap-3">
            <ScenarioIcon className={`h-6 w-6 ${colorClasses[scenarioColor].text}`} />
            <h2 className="text-xl font-bold">{scenarios[selectedScenario].title}</h2>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <p className="font-medium">{scenarios[selectedScenario].description}</p>
            <div className="grid grid-cols-2 gap-3">
              {Object.entries(scenarios[selectedScenario].details).map(([key, value]) => (
                <div key={key} className="bg-white/60 p-3 rounded">
                  <div className="text-xs text-gray-600 font-medium uppercase tracking-wide mb-1">
                    {key.replace(/([A-Z])/g, ' $1').trim()}
                  </div>
                  <div className="font-semibold">{typeof value === 'boolean' ? (value ? '✓ Yes' : '✗ No') : value}</div>
                </div>
              ))}
            </div>
          </div>

          <button
            onClick={runNegotiation}
            disabled={negotiating}
            className={`mt-4 px-6 py-3 rounded-lg font-semibold flex items-center gap-2 transition-colors text-white ${
              negotiating
                ? 'bg-gray-400 cursor-not-allowed'
                : ''
            }`}
            style={{
              backgroundColor: negotiating ? undefined : (
                scenarioColor === 'blue' ? '#2563eb' :
                scenarioColor === 'orange' ? '#ea580c' :
                scenarioColor === 'red' ? '#dc2626' :
                '#16a34a'
              )
            }}
          >
            {negotiating ? (
              <>
                <Clock className="h-5 w-5 animate-spin" />
                Agents Negotiating...
              </>
            ) : (
              <>
                <Play className="h-5 w-5" />
                Start Agent Negotiation
              </>
            )}
          </button>
        </CardContent>
      </Card>

      {/* Negotiation Progress */}
      {(negotiating || result) && (
        <Card className="mb-6">
          <CardHeader>
            <h2 className="text-xl font-bold">Negotiation Progress</h2>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              {/* Round 1 */}
              <div className={`transition-opacity duration-500 ${currentRound >= 1 ? 'opacity-100' : 'opacity-30'}`}>
                <div className="flex items-center gap-2 mb-3">
                  {currentRound > 1 ? (
                    <CheckCircle className="h-5 w-5 text-green-600" />
                  ) : currentRound === 1 ? (
                    <Clock className="h-5 w-5 text-blue-600 animate-spin" />
                  ) : (
                    <div className="h-5 w-5 rounded-full border-2 border-gray-300"></div>
                  )}
                  <h3 className="font-bold">Round 1: Initial Proposals</h3>
                </div>
                {currentRound >= 1 && (
                  <div className="ml-7 space-y-2 text-sm">
                    <div className="flex items-start gap-2">
                      <span className="text-blue-600 font-semibold">Demand Agent:</span>
                      <span className="text-gray-700">"Accept order - customer has high lifetime value"</span>
                    </div>
                    <div className="flex items-start gap-2">
                      <span className="text-purple-600 font-semibold">Production Agent:</span>
                      <span className="text-gray-700">"Capacity constraint - cannot meet timeline without overtime"</span>
                    </div>
                    <div className="flex items-start gap-2">
                      <span className="text-green-600 font-semibold">Inventory Agent:</span>
                      <span className="text-gray-700">"Use buffer stock + overtime - hybrid approach feasible"</span>
                    </div>
                  </div>
                )}
              </div>

              {/* Round 2 */}
              <div className={`transition-opacity duration-500 ${currentRound >= 2 ? 'opacity-100' : 'opacity-30'}`}>
                <div className="flex items-center gap-2 mb-3">
                  {currentRound > 2 ? (
                    <CheckCircle className="h-5 w-5 text-green-600" />
                  ) : currentRound === 2 ? (
                    <Clock className="h-5 w-5 text-blue-600 animate-spin" />
                  ) : (
                    <div className="h-5 w-5 rounded-full border-2 border-gray-300"></div>
                  )}
                  <h3 className="font-bold">Round 2: Agent Critiques</h3>
                </div>
                {currentRound >= 2 && (
                  <div className="ml-7 space-y-2 text-sm">
                    <div className="flex items-start gap-2">
                      <span className="text-blue-600 font-semibold">Demand →Production:</span>
                      <span className="text-gray-700">"Rejecting order risks losing $500K lifetime value customer"</span>
                    </div>
                    <div className="flex items-start gap-2">
                      <span className="text-purple-600 font-semibold">Production→Inventory:</span>
                      <span className="text-gray-700">"Overtime costs $6K but financially justified"</span>
                    </div>
                    <div className="flex items-start gap-2">
                      <span className="text-green-600 font-semibold">Inventory→Demand:</span>
                      <span className="text-gray-700">"Buffer usage safe - above minimum safety stock"</span>
                    </div>
                  </div>
                )}
              </div>

              {/* Round 3 */}
              <div className={`transition-opacity duration-500 ${currentRound >= 3 ? 'opacity-100' : 'opacity-30'}`}>
                <div className="flex items-center gap-2 mb-3">
                  {currentRound > 3 ? (
                    <CheckCircle className="h-5 w-5 text-green-600" />
                  ) : currentRound === 3 ? (
                    <Clock className="h-5 w-5 text-blue-600 animate-spin" />
                  ) : (
                    <div className="h-5 w-5 rounded-full border-2 border-gray-300"></div>
                  )}
                  <h3 className="font-bold">Round 3: Consensus Building</h3>
                </div>
                {currentRound >= 3 && (
                  <div className="ml-7 text-sm text-gray-700">
                    <p>Orchestrator synthesizing all proposals and critiques into final recommendation...</p>
                  </div>
                )}
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Error Display */}
      {error && (
        <Card className="mb-6 border-red-200 bg-red-50">
          <CardContent className="p-4">
            <div className="flex items-start gap-3">
              <AlertTriangle className="h-5 w-5 text-red-600 mt-0.5" />
              <div>
                <h3 className="font-semibold text-red-900">Negotiation Failed</h3>
                <p className="text-sm text-red-700 mt-1">{error}</p>
                <p className="text-xs text-red-600 mt-2">
                  Make sure the backend server is running on port 8000
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Final Result */}
      {result && currentRound === 4 && (
        <Card className="border-green-200 bg-green-50">
          <CardHeader>
            <div className="flex items-center gap-2">
              <CheckCircle className="h-6 w-6 text-green-600" />
              <h2 className="text-xl font-bold text-green-900">Consensus Reached</h2>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {/* Final Decision */}
              {result.round_3_consensus?.final_decision && (
                <div className="bg-white p-4 rounded-lg">
                  <h3 className="font-semibold mb-2">Final Decision:</h3>
                  <p className="text-gray-800 whitespace-pre-wrap">
                    {typeof result.round_3_consensus.final_decision === 'string'
                      ? result.round_3_consensus.final_decision
                      : JSON.stringify(result.round_3_consensus.final_decision, null, 2)}
                  </p>
                </div>
              )}

              {/* Agent Agreement */}
              <div className="bg-white p-4 rounded-lg">
                <h3 className="font-semibold mb-3">Agent Participation:</h3>
                <div className="flex items-center gap-6">
                  <div className="flex items-center gap-2">
                    <div className="h-3 w-3 rounded-full bg-blue-600"></div>
                    <span className="text-sm">Demand Agent</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="h-3 w-3 rounded-full bg-purple-600"></div>
                    <span className="text-sm">Production Agent</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="h-3 w-3 rounded-full bg-green-600"></div>
                    <span className="text-sm">Inventory Agent</span>
                  </div>
                </div>
                <p className="text-sm text-gray-600 mt-3">
                  All {result.round_3_consensus?.agents_involved || 3} agents contributed to this decision
                </p>
              </div>

              {/* Timestamp */}
              <div className="text-xs text-gray-500">
                Completed at: {new Date(result.timestamp).toLocaleString()}
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
