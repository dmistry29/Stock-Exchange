import React, { useState } from 'react';
import useWebSocket from 'react-use-websocket';
import DepthChart from './components/DepthChart';

function App() {
  const [bids, setBids] = useState([]);
  const [asks, setAsks] = useState([]);
  const [status, setStatus] = useState("Disconnected");

  // Connect to your Python Backend
  const { lastJsonMessage } = useWebSocket('ws://localhost:8000/ws', {
    onOpen: () => setStatus("Connected to Exchange"),
    onClose: () => setStatus("Disconnected"),
    shouldReconnect: () => true,
  });

  // Update state whenever a new message arrives (50 times/sec)
  React.useEffect(() => {
    if (lastJsonMessage) {
      setBids(lastJsonMessage.bids);
      setAsks(lastJsonMessage.asks);
    }
  }, [lastJsonMessage]);

  // Calculate Mid-Price for Header
  const bestBid = bids.length > 0 ? bids[0].price : 0;
  const bestAsk = asks.length > 0 ? asks[0].price : 0;
  const midPrice = ((bestBid + bestAsk) / 2).toFixed(2);

  return (
    <div style={{ backgroundColor: '#121212', minHeight: '100vh', padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <div>
          <h1 style={{ color: 'white', margin: 0 }}>Deep Mistry <span style={{color: '#4CAF50'}}>Matching Engine</span></h1>
          <p style={{ color: '#666', margin: '5px 0 0 0' }}>Status: <span style={{ color: status.includes('Connected') ? '#00C853' : '#FF5252' }}>{status}</span></p>
        </div>
        <div style={{ textAlign: 'right' }}>
          <h2 style={{ color: 'white', fontSize: '2.5rem', margin: 0 }}>${midPrice}</h2>
          <p style={{ color: '#888', margin: 0 }}>BTC-USD Mid Market</p>
        </div>
      </div>

      {/* Main Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: '3fr 1fr', gap: '20px' }}>
        
        {/* Left Column: The Chart */}
        <DepthChart bids={bids} asks={asks} />

        {/* Right Column: Order Book Table */}
        <div style={{ backgroundColor: '#1e1e1e', padding: '15px', borderRadius: '8px', height: '400px', overflowY: 'hidden' }}>
          <h3 style={{ color: '#888', marginTop: 0 }}>Order Book</h3>
          <div style={{ display: 'flex', justifyContent: 'space-between', color: '#666', fontSize: '0.8rem', marginBottom: '10px' }}>
            <span>Size</span>
            <span>Price (USD)</span>
          </div>
          
          {/* Asks (Sells) - Red */}
          <div style={{ display: 'flex', flexDirection: 'column-reverse' }}>
            {asks.slice(0, 10).map((ask, i) => (
              <div key={i} style={{ display: 'flex', justifyContent: 'space-between', color: '#FF5252', fontFamily: 'monospace' }}>
                <span>{ask.qty.toFixed(4)}</span>
                <span>{ask.price.toFixed(2)}</span>
              </div>
            ))}
          </div>

          <div style={{ margin: '10px 0', borderTop: '1px dashed #444' }}></div>

          {/* Bids (Buys) - Green */}
          <div>
            {bids.slice(0, 10).map((bid, i) => (
              <div key={i} style={{ display: 'flex', justifyContent: 'space-between', color: '#00C853', fontFamily: 'monospace' }}>
                <span>{bid.qty.toFixed(4)}</span>
                <span>{bid.price.toFixed(2)}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;