import React from "react";
import { Outlet, NavLink, useNavigate } from "react-router-dom";
import {
  LayoutDashboard,
  BarChart2,
  MessageSquare,
  LogOut,
} from "lucide-react";
import { useStockContext } from "../context/StockContext";

const Layout: React.FC = () => {
  const { userProfile } = useStockContext();
  const navigate = useNavigate();

  // Redirect to sign up if no user profile
  React.useEffect(() => {
    if (!userProfile) {
      navigate("/");
    }
  }, [userProfile, navigate]);

  return (
    <div className="flex h-screen">
      {/* Sidebar */}
      <div className="w-64 bg-gray-900 text-white flex flex-col">
        <div className="p-6 border-b border-gray-800">
          <h1 className="text-xl font-bold">EvoTradeX</h1>
          {userProfile && (
            <p className="text-sm text-gray-400 mt-2">
              Welcome, {userProfile.name}
            </p>
          )}
        </div>
        <nav className="flex-1 p-4">
          <ul className="space-y-2">
            <li>
              <NavLink
                to="/portfolio"
                className={({ isActive }) =>
                  `flex items-center p-3 rounded-md transition-colors ${
                    isActive ? "bg-blue-600" : "hover:bg-gray-800"
                  }`
                }
              >
                <LayoutDashboard className="mr-3 h-5 w-5" />
                Portfolio
              </NavLink>
            </li>
            <li>
              <NavLink
                to="/chatbot"
                className={({ isActive }) =>
                  `flex items-center p-3 rounded-md transition-colors ${
                    isActive ? "bg-blue-600" : "hover:bg-gray-800"
                  }`
                }
              >
                <MessageSquare className="mr-3 h-5 w-5" />
                Chatbot
              </NavLink>
            </li>
          </ul>
        </nav>
        <div className="p-4 border-t border-gray-800">
          <button
            onClick={() => navigate("/")}
            className="flex items-center p-3 w-full text-left rounded-md hover:bg-gray-800 transition-colors"
          >
            <LogOut className="mr-3 h-5 w-5" />
            Sign Out
          </button>
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1 overflow-auto">
        <Outlet />
      </div>
    </div>
  );
};

export default Layout;
