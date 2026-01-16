import React from 'react';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

const DepthChart = ({ bids, asks }) => {
  
  // 1. Process Bids (Buy Side - Green) - Cumulative Sum
  let bidSum = 0;
  const processedBids = [...bids]
    .sort((a, b) => b.price - a.price)
    .map(item => {
      bidSum += item.qty;
      return { price: item.price, bidVolume: bidSum, askVolume: null };
    })
    .reverse();

  // 2. Process Asks (Sell Side - Red) - Cumulative Sum
  let askSum = 0;
  const processedAsks = [...asks]
    .sort((a, b) => a.price - b.price)
    .map(item => {
      askSum += item.qty;
      return { price: item.price, bidVolume: null, askVolume: askSum };
    });

  const data = [...processedBids, ...processedAsks];

  return (
    <div style={{ height: 400, width: '100%', backgroundColor: '#1e1e1e', borderRadius: '8px', padding: '10px' }}>
      <h3 style={{ color: '#888', margin: '0 0 10px 0' }}>Real-Time Market Depth</h3>
      <ResponsiveContainer>
        <AreaChart data={data}>
          <XAxis 
            dataKey="price" 
            type="number" 
            domain={['dataMin', 'dataMax']} // Keep the view tight on the data
            tickFormatter={(tick) => `$${tick.toLocaleString()}`}
            tick={{ fill: '#666', fontSize: 12 }} 
          />
          <YAxis 
            tick={{ fill: '#666', fontSize: 12 }} 
            width={40}
          />
          <Tooltip 
            // Make the hover line bright white and thick
            cursor={{ stroke: '#FFFFFF', strokeWidth: 2 }}
            contentStyle={{ backgroundColor: '#333', border: '1px solid #fff' }}
            itemStyle={{ color: '#fff' }}
            formatter={(value) => value ? value.toFixed(4) : ''}
            labelFormatter={(label) => `Price: $${label}`}
          />
          {/* Green Mountain (Bids) */}
          <Area 
            type="stepAfter" 
            dataKey="bidVolume" 
            stroke="#00E676"   // Brighter Green
            strokeWidth={3}    // Thicker line
            fill="#00E676" 
            fillOpacity={0.8}  // Almost solid fill
            connectNulls 
            activeDot={{ r: 6, fill: 'white' }} // Big white dot on hover
          />
          {/* Red Mountain (Asks) */}
          <Area 
            type="stepBefore" 
            dataKey="askVolume" 
            stroke="#FF1744"   // Brighter Red
            strokeWidth={3}    // Thicker line
            fill="#FF1744" 
            fillOpacity={0.8}  // Almost solid fill
            connectNulls 
            activeDot={{ r: 6, fill: 'white' }} // Big white dot on hover
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
};

export default DepthChart;