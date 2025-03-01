import React, { createContext, useState, useContext, ReactNode } from "react";

// Define types for suggested and invested stocks
export interface SuggestedStock {
  id: string;
  name: string;
  ticker: string;
  currentPrice: number;
  quantity: number;
  arr: number; // Annual Return Rate
  sr: number; // Sharpe Ratio
  cr: number; // Calmar Ratio
  sor: number; // Sortino Ratio
  mdd: number; // Maximum Drawdown
  vol: number; // Volatility
  expectedReturn: number; // AI prediction
}

export interface InvestedStock {
  id: string;
  name: string;
  ticker: string;
  quantity: number;
  purchasePrice: number;
  currentPrice: number;
  arr: number; // Annual Return Rate
  sr: number; // Sharpe Ratio
  cr: number; // Calmar Ratio
  sor: number; // Sortino Ratio
  mdd: number; // Maximum Drawdown
  vol: number; // Volatility

  expectedReturn: number;
}

export interface Stock {
  id: string;
  name: string;
  ticker: string;
  currentPrice: number;
  quantity: number;
  arr: number; // Annual Return Rate
  sr: number; // Sharpe Ratio
  cr: number; // Calmar Ratio
  sor: number; // Sortino Ratio
  mdd: number; // Maximum Drawdown
  vol: number; // Volatility
  expectedReturn: number; // AI prediction
}
export interface UserProfile {
  name: string;
  interests: string[];
  initialCapital: number;
}

interface StockContextType {
  stocks: Stock[];
  suggestedStocks: SuggestedStock[];
  investedStocks: InvestedStock[];
  userProfile: UserProfile | null;
  totalValue: number;
  totalInvested: number;
  totalProfitLoss: number;
  // profitLossPercentage:number;
  setUserProfile: (profile: UserProfile) => void;
  setInvestedStocks: React.Dispatch<React.SetStateAction<InvestedStock[]>>;
  setSuggestedStocks: React.Dispatch<React.SetStateAction<SuggestedStock[]>>;
}

const StockContext = createContext<StockContextType | undefined>(undefined);
// Sample suggested stocks (initially all stocks are suggested)
const sampleStocks: SuggestedStock[] = [
  {
    id: "1",
    name: "Mastercard Inc.",
    ticker: "MA",
    quantity: 7,
    currentPrice: 435.25,
    arr: 13.8,
    sr: 1.3,
    cr: 0.9,
    sor: 1.6,
    mdd: 14.5,
    vol: 17.2,
    expectedReturn: 14.9,
  },
  {
    id: "2",
    name: "Netflix, Inc.",
    ticker: "NFLX",
    quantity: 5,
    currentPrice: 615.5,
    arr: 10.4,
    sr: 1.1,
    cr: 0.75,
    sor: 1.3,
    mdd: 20.2,
    vol: 22.8,
    expectedReturn: 13.1,
  },
  {
    id: "3",
    name: "Visa Inc.",
    ticker: "V",
    quantity: 6,
    currentPrice: 252.75,
    arr: 12.9,
    sr: 1.25,
    cr: 0.88,
    sor: 1.5,
    mdd: 13.7,
    vol: 16.9,
    expectedReturn: 14.5,
  },
  {
    id: "4",
    name: "Tesla, Inc.",
    ticker: "TSLA",
    quantity: 3,
    currentPrice: 315.8, // Update this to Tesla’s latest price if needed
    arr: 18.5,
    sr: 1.6,
    cr: 1.1,
    sor: 1.9,
    mdd: 25.4,
    vol: 30.1,
    expectedReturn: 20.2,
  },
  {
    id: "5",
    name: "Palantir Technologies Inc.",
    ticker: "PLTR",
    quantity: 10,
    currentPrice: 22.4,
    arr: 16.2,
    sr: 1.45,
    cr: 1.0,
    sor: 1.8,
    mdd: 27.1,
    vol: 35.5,
    expectedReturn: 18.0,
  },
  {
    id: "6",
    name: "AbbVie Inc.",
    ticker: "ABBV",
    quantity: 5,
    currentPrice: 159.6,
    arr: 11.5,
    sr: 1.2,
    cr: 0.8,
    sor: 1.4,
    mdd: 15.9,
    vol: 18.2,
    expectedReturn: 12.8,
  },
];

export const StockProvider: React.FC<{ children: ReactNode }> = ({
  children,
}) => {
  const [stocks] = useState<Stock[]>(sampleStocks);
  const [suggestedStocks, setSuggestedStocks] = useState<SuggestedStock[]>(
    sampleStocks.filter((stock) => stock.id !== "4")
  );

  const [investedStocks, setInvestedStocks] = useState<InvestedStock[]>([]);
  const [userProfile, setUserProfile] = useState<UserProfile | null>(null);

  // Calculate total portfolio value based on invested stocks
  const totalValue = investedStocks.reduce(
    (total, stock) => total + stock.currentPrice * stock.quantity,
    0
  );

  const totalInvested = investedStocks.reduce(
    (total, stock) => total + stock.purchasePrice * stock.quantity,
    0
  );

  const totalProfitLoss = investedStocks.reduce(
    (total, stock) => total + stock.expectedReturn,
    0
  );

  return (
    <StockContext.Provider
      value={{
        stocks,
        suggestedStocks,
        investedStocks,
        userProfile,
        totalValue,
        totalInvested,
        setUserProfile,
        setInvestedStocks,
        setSuggestedStocks,
        totalProfitLoss,
      }}
    >
      {children}
    </StockContext.Provider>
  );
};

export const useStockContext = () => {
  const context = useContext(StockContext);
  if (context === undefined) {
    throw new Error("useStockContext must be used within a StockProvider");
  }
  return context;
};
