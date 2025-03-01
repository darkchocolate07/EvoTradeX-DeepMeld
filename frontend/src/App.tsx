import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import SignUp from './pages/SignUp';
import PortfolioOverview from './pages/PortfolioOverview';
import StockDetails from './pages/StockDetails';
import Chatbot from './pages/Chatbot';
import Layout from './components/Layout';
import { StockProvider } from './context/StockContext';

function App() {
  return (
    <StockProvider>
      <Router>
        <Routes>
          <Route path="/" element={<SignUp />} />
          <Route element={<Layout />}>
            <Route path="/portfolio" element={<PortfolioOverview />} />
            <Route path="/stock/:id" element={<StockDetails />} />
            <Route path="/chatbot" element={<Chatbot />} />
          </Route>
        </Routes>
      </Router>
    </StockProvider>
  );
}

export default App;