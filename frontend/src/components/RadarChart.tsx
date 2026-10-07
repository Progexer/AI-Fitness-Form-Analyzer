import React from 'react';

interface RadarChartProps {
  metrics: {
    form_accuracy: number;
    range_of_motion: number;
    tempo_smoothness: number;
    bilateral_symmetry: number;
  };
  size?: number;
}

export const RadarChart: React.FC<RadarChartProps> = ({ metrics, size = 260 }) => {
  const center = size / 2;
  const radius = size * 0.38;

  const domains = [
    { key: 'form_accuracy', label: 'Form Accuracy', val: metrics.form_accuracy || 70, angle: -Math.PI / 2 },
    { key: 'range_of_motion', label: 'Range of Motion', val: metrics.range_of_motion || 75, angle: 0 },
    { key: 'tempo_smoothness', label: 'Smoothness', val: metrics.tempo_smoothness || 80, angle: Math.PI / 2 },
    { key: 'bilateral_symmetry', label: 'Symmetry', val: metrics.bilateral_symmetry || 85, angle: Math.PI },
  ];

  // Grid rings
  const rings = [0.25, 0.5, 0.75, 1.0];

  // Compute polygon points
  const points = domains.map((d) => {
    const r = (d.val / 100) * radius;
    const x = center + r * Math.cos(d.angle);
    const y = center + r * Math.sin(d.angle);
    return `${x},${y}`;
  }).join(' ');

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        {/* Background Grids */}
        {rings.map((factor, i) => {
          const r = radius * factor;
          return (
            <polygon
              key={i}
              points={domains.map((d) => {
                const x = center + r * Math.cos(d.angle);
                const y = center + r * Math.sin(d.angle);
                return `${x},${y}`;
              }).join(' ')}
              fill="transparent"
              stroke="rgba(255, 255, 255, 0.08)"
              strokeWidth="1"
              strokeDasharray={i === rings.length - 1 ? undefined : '2,2'}
            />
          );
        })}

        {/* Cross Axes */}
        {domains.map((d, i) => (
          <line
            key={i}
            x1={center}
            y1={center}
            x2={center + radius * Math.cos(d.angle)}
            y2={center + radius * Math.sin(d.angle)}
            stroke="rgba(255, 255, 255, 0.1)"
            strokeWidth="1"
          />
        ))}

        {/* Data Polygon */}
        <polygon
          points={points}
          fill="rgba(16, 185, 129, 0.25)"
          stroke="#10b981"
          strokeWidth="2.5"
          style={{ transition: 'all 0.5s ease-out' }}
        />

        {/* Data Vertices */}
        {domains.map((d, i) => {
          const r = (d.val / 100) * radius;
          const x = center + r * Math.cos(d.angle);
          const y = center + r * Math.sin(d.angle);
          return (
            <circle
              key={i}
              cx={x}
              cy={y}
              r="4.5"
              fill="#34d399"
              stroke="#0f172a"
              strokeWidth="2"
            />
          );
        })}

        {/* Axis Labels */}
        {domains.map((d, i) => {
          const r = radius + 22;
          const x = center + r * Math.cos(d.angle);
          const y = center + r * Math.sin(d.angle) + (d.angle === 0 || d.angle === Math.PI ? 4 : (d.angle > 0 ? 12 : -6));
          return (
            <text
              key={i}
              x={x}
              y={y}
              textAnchor="middle"
              fill="#94a3b8"
              fontSize="10"
              fontFamily="var(--font-body)"
              fontWeight="500"
            >
              {d.label} ({Math.round(d.val)}%)
            </text>
          );
        })}
      </svg>
    </div>
  );
};
