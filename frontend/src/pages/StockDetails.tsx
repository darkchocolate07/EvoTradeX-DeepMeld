import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import { TrendingUp } from "lucide-react";
import { useStockContext } from "../context/StockContext";

interface StockData {
  date: string;
  price: number;
}

// Generate prediction data with start date flexibility
const generatePredictionData = (
  startDate: Date,
  currentPrice: number,
  expectedReturn: number,
  volatility: number
) => {
  const data = [];
  let price = currentPrice;

  // Generate data for the next 14 days
  for (let i = 1; i <= 14; i++) {
    const day = new Date(startDate);
    day.setDate(startDate.getDate() + i);

    const dailyReturn = expectedReturn / 252; // Approximate trading days in a year
    const randomFactor = (Math.random() - 0.5) * volatility * 0.01; // Randomness for daily changes
    price = price * (1 + dailyReturn / 100 + randomFactor);

    data.push({
      date: day.toISOString().split("T")[0], // Format as YYYY-MM-DD
      price: price,
      isPrediction: true,
    });
  }

  return data;
};

const StockDetails: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { stocks } = useStockContext();

  const stock = stocks.find((s) => s.id === id);

  if (!stock) {
    return (
      <div className="p-6">
        <h1 className="text-2xl font-bold mb-6">Stock not found</h1>
        <button onClick={() => navigate("/portfolio")} className="btn-primary">
          Back to Portfolio
        </button>
      </div>
    );
  }

  // State for dropdown selection and data
  const [selectedDate, setSelectedDate] = useState<string>("today");
  const [historicalData, setHistoricalData] = useState<StockData[]>([]);
  const [predictionData, setPredictionData] = useState<StockData[]>([]);

  const handleDateChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedDate(event.target.value);
  };

  // Load historical data
  useEffect(() => {
    fetch(`/data/historical_price_daily/${stock.ticker}_historical_prices.csv`)
      .then((response) => response.text())
      .then((csvText) => {
        const rows = csvText.trim().split("\n");

        const january19th = new Date("2025-01-19");
        january19th.setHours(0, 0, 0, 0); // Set time to midnight for proper comparison

        let filteredRows = [];

        // If user selected "January 19th" or a date earlier

        // Filter for the 30 days leading up to January 19th
        const thirtyDaysBeforeJanuary19 = new Date(january19th);
        thirtyDaysBeforeJanuary19.setDate(january19th.getDate() - 30);

        filteredRows = rows.filter((row) => {
          const rowDate = new Date(row.split(",")[0]);
          return rowDate >= thirtyDaysBeforeJanuary19 && rowDate < january19th;
        });

        // Parse the filtered rows
        const last30Rows = filteredRows
          .map((row) => row.split(","))
          .map((columns) => ({
            date: columns[0],
            price: parseFloat(columns[1]) || 0,
          }));

        setHistoricalData(last30Rows);
      })
      .catch((error) => console.error("Error loading CSV:", error));
  }, [stock.ticker, selectedDate]);

  // Generate predictions when historical data is available
  useEffect(() => {
    if (historicalData.length > 0) {
      const lastPrice = historicalData[historicalData.length - 1].price;
      const startDate = new Date("2025-01-19");

      setPredictionData(
        generatePredictionData(
          startDate,
          lastPrice,
          stock.expectedReturn,
          stock.vol
        )
      );
    }
  }, [historicalData, selectedDate, stock.expectedReturn, stock.vol]);

  // Combine historical and prediction data for the chart
  const combinedData = [...historicalData, ...predictionData];

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold">
            {stock.name} ({stock.ticker})
          </h1>
          <div className="flex items-center mt-1">
            <span className="text-2xl font-bold mr-2">
              ${stock.currentPrice.toFixed(2)}
            </span>
          </div>
        </div>
        <button
          onClick={() => navigate("/portfolio")}
          className="btn-secondary"
        >
          Back to Portfolio
        </button>
      </div>

      {/* Price Chart */}
      <div className="card mb-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">Price History & Prediction</h2>
          <div className="flex items-center text-blue-400">
            <TrendingUp className="h-5 w-5 mr-1" />
            <span>Expected Return: {stock.expectedReturn.toFixed(1)}%</span>
          </div>
        </div>
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart
              data={combinedData}
              margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
            >
              <defs>
                <linearGradient
                  id="colorHistorical"
                  x1="0"
                  y1="0"
                  x2="0"
                  y2="1"
                >
                  <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8} />
                  <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                </linearGradient>
                <linearGradient
                  id="colorPrediction"
                  x1="0"
                  y1="0"
                  x2="0"
                  y2="1"
                >
                  <stop offset="5%" stopColor="#10b981" stopOpacity={0.8} />
                  <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                </linearGradient>
              </defs>
              <XAxis dataKey="date" />
              <YAxis domain={["auto", "auto"]} />
              <CartesianGrid strokeDasharray="3 3" />
              <Tooltip
                formatter={(value) => [`$${Number(value).toFixed(2)}`, "Price"]}
                labelFormatter={(label) => `Date: ${label}`}
              />
              <Legend />
              <Area
                type="monotone"
                dataKey="price"
                stroke="#3b82f6"
                fillOpacity={1}
                fill="url(#colorHistorical)"
                name="Historical Price"
                activeDot={{ r: 8 }}
                dot={{ r: 3 }}
                isAnimationActive={true}
                animationDuration={1000}
                connectNulls={true}
              />
              <Area
                type="monotone"
                dataKey={(data) => (data.isPrediction ? data.price : null)}
                stroke="#10b981"
                strokeDasharray="5 5"
                fillOpacity={1}
                fill="url(#colorPrediction)"
                name="Predicted Price"
                dot={{ r: 3 }}
                isAnimationActive={true}
                animationDuration={1000}
                connectNulls={true}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

export default StockDetails;

// import React, { useState, useEffect } from "react";
// import { useParams, useNavigate } from "react-router-dom";
// import {
//   LineChart,
//   Line,
//   XAxis,
//   YAxis,
//   CartesianGrid,
//   Tooltip,
//   ResponsiveContainer,
//   Area,
//   AreaChart,
//   Legend,
// } from "recharts";
// import { TrendingUp } from "lucide-react";
// import { useStockContext } from "../context/StockContext";

// interface StockData {
//   date: string;
//   price: number;
// }

// // Generate prediction data with start date flexibility
// const generatePredictionData = (
//   currentPrice: number,
//   expectedReturn: number,
//   volatility: number
// ) => {
//   const data = [];
//   let price = currentPrice;

//   // Generate data for the next 14 days
//   for (let i = 1; i <= 14; i++) {
//     const day = new Date();
//     day.setDate(day.getDate() + i);

//     // Expected daily return with some randomness based on volatility
//     const dailyReturn = expectedReturn / 252; // Approximate trading days in a year
//     const randomFactor = (Math.random() - 0.5) * volatility * 0.01; // Smaller randomness factor for daily changes
//     price = price * (1 + dailyReturn / 100 + randomFactor);

//     data.push({
//       date: day.toISOString().split("T")[0], // Format as YYYY-MM-DD
//       price: price,
//       isPrediction: true,
//     });
//   }

//   return data;
// };

// const StockDetails: React.FC = () => {
//   const { id } = useParams<{ id: string }>();
//   const navigate = useNavigate();
//   const { stocks } = useStockContext();

//   const stock = stocks.find((s) => s.id === id);

//   if (!stock) {
//     return (
//       <div className="p-6">
//         <h1 className="text-2xl font-bold mb-6">Stock not found</h1>
//         <button onClick={() => navigate("/portfolio")} className="btn-primary">
//           Back to Portfolio
//         </button>
//       </div>
//     );
//   }

//   // State for dropdown selection and data

//   const [historicalData, setHistoricalData] = useState<StockData[]>([]);
//   const [predictionData, setPredictionData] = useState<StockData[]>([]);

//   // Load historical data
//   useEffect(() => {
//     fetch(`/data/historical_price_daily/${stock.ticker}_historical_prices.csv`)
//       .then((response) => response.text())
//       .then((csvText) => {
//         const rows = csvText.trim().split("\n");
//         const last30Rows = rows
//           .slice(-30)
//           .map((row) => row.split(","))
//           .map((columns) => ({
//             date: columns[0],
//             price: parseFloat(columns[1]) || 0,
//           }));

//         setHistoricalData(last30Rows);
//       })
//       .catch((error) => console.error("Error loading CSV:", error));
//   }, [stock.ticker]);

//   // Generate predictions when historical data is available
//   useEffect(() => {
//     if (historicalData.length > 0) {
//       const lastPrice = historicalData[historicalData.length - 1].price;
//       setPredictionData(
//         generatePredictionData(lastPrice, stock.expectedReturn, stock.vol)
//       );
//     }
//   }, [historicalData, stock.expectedReturn, stock.vol]);

//   // Combine historical and prediction data for the chart
//   const combinedData = [...historicalData, ...predictionData];

//   return (
//     <div className="p-6">
//       <div className="flex justify-between items-center mb-6">
//         <div>
//           <h1 className="text-2xl font-bold">
//             {stock.name} ({stock.ticker})
//           </h1>
//           <div className="flex items-center mt-1">
//             <span className="text-2xl font-bold mr-2">
//               ${stock.currentPrice.toFixed(2)}
//             </span>
//           </div>
//         </div>
//         <button
//           onClick={() => navigate("/portfolio")}
//           className="btn-secondary"
//         >
//           Back to Portfolio
//         </button>
//       </div>

//       {/* Price Chart */}
//       <div className="card mb-6">
//         <div className="flex justify-between items-center mb-4">
//           <h2 className="text-xl font-semibold">Price History & Prediction</h2>
//           <div className="flex items-center text-blue-400">
//             <TrendingUp className="h-5 w-5 mr-1" />
//             <span>Expected Return: {stock.expectedReturn.toFixed(1)}%</span>
//           </div>
//         </div>
//         <div className="h-80">
//           <ResponsiveContainer width="100%" height="100%">
//             <AreaChart
//               data={combinedData}
//               margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
//             >
//               <defs>
//                 <linearGradient
//                   id="colorHistorical"
//                   x1="0"
//                   y1="0"
//                   x2="0"
//                   y2="1"
//                 >
//                   <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8} />
//                   <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
//                 </linearGradient>
//                 <linearGradient
//                   id="colorPrediction"
//                   x1="0"
//                   y1="0"
//                   x2="0"
//                   y2="1"
//                 >
//                   <stop offset="5%" stopColor="#10b981" stopOpacity={0.8} />
//                   <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
//                 </linearGradient>
//               </defs>
//               <XAxis dataKey="date" />
//               <YAxis domain={["auto", "auto"]} />
//               <CartesianGrid strokeDasharray="3 3" />
//               <Tooltip
//                 formatter={(value) => [`$${Number(value).toFixed(2)}`, "Price"]}
//                 labelFormatter={(label) => `Date: ${label}`}
//               />
//               <Legend />
//               <Area
//                 type="monotone"
//                 dataKey="price"
//                 stroke="#3b82f6"
//                 fillOpacity={1}
//                 fill="url(#colorHistorical)"
//                 name="Historical Price"
//                 activeDot={{ r: 8 }}
//                 dot={{ r: 3 }}
//                 isAnimationActive={true}
//                 animationDuration={1000}
//                 connectNulls={true}
//               />
//               <Area
//                 type="monotone"
//                 dataKey={(data) => (data.isPrediction ? data.price : null)}
//                 stroke="#10b981"
//                 strokeDasharray="5 5"
//                 fillOpacity={1}
//                 fill="url(#colorPrediction)"
//                 name="Predicted Price"
//                 dot={{ r: 3 }}
//                 isAnimationActive={true}
//                 animationDuration={1000}
//                 connectNulls={true}
//               />
//             </AreaChart>
//           </ResponsiveContainer>
//         </div>
//       </div>
//     </div>
//   );
// };

// export default StockDetails;
