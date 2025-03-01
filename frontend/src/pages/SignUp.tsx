import React from "react";
import { useNavigate } from "react-router-dom";
import { useForm, Controller } from "react-hook-form";
import { BarChart2 } from "lucide-react";
import { useStockContext } from "../context/StockContext";

type FormData = {
  name: string;
  interests: string[];
  initialCapital: number;
};

const SignUp: React.FC = () => {
  const navigate = useNavigate();
  const { setUserProfile } = useStockContext();
  const {
    register,
    handleSubmit,
    control,
    formState: { errors },
  } = useForm<FormData>();

  const onSubmit = (data: FormData) => {
    setUserProfile(data);
    navigate("/portfolio");
  };

  const sectors = ["Technology", "Healthcare", "Consumer Goods", "Finance"];

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="max-w-4xl w-full bg-gray-800 rounded-xl shadow-2xl overflow-hidden">
        <div className="flex flex-col md:flex-row">
          {/* Left side - Branding */}
          <div className="bg-gradient-to-br from-gray-900 to-blue-900 p-8 md:w-1/3 flex flex-col justify-center items-center">
            <div className="text-center">
              <BarChart2 className="h-16 w-16 text-blue-400 mx-auto mb-4" />
              <h1 className="text-3xl font-bold text-white mb-2">EvoTradeX</h1>
              <p className="text-blue-200">
                Your intelligent portfolio management solution
              </p>
            </div>
          </div>

          {/* Right side - Form */}
          <div className="p-8 md:w-2/3">
            <h2 className="text-2xl font-bold mb-6 text-white">
              Create Your Profile
            </h2>
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
              {/* Name */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">
                  Name
                </label>
                <input
                  {...register("name", { required: "Name is required" })}
                  className="input-field"
                  placeholder="Your full name"
                />
                {errors.name && (
                  <p className="mt-1 text-sm text-red-500">
                    {errors.name.message}
                  </p>
                )}
              </div>

              {/* Sector */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Sector to invest in
                </label>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  <Controller
                    name="interests"
                    control={control}
                    rules={{ required: "Please select at least one sector" }}
                    render={({ field }) => (
                      <>
                        {sectors.map((type) => (
                          <div
                            key={type}
                            className={`option-card ${
                              field.value?.includes(type) ? "selected" : ""
                            }`}
                            onClick={() => {
                              const currentValues = field.value || [];
                              if (currentValues.includes(type)) {
                                field.onChange(
                                  currentValues.filter((v) => v !== type)
                                );
                              } else {
                                field.onChange([...currentValues, type]);
                              }
                            }}
                          >
                            {type}
                          </div>
                        ))}
                      </>
                    )}
                  />
                </div>
                {errors.interests && (
                  <p className="mt-1 text-sm text-red-500">
                    {errors.interests.message}
                  </p>
                )}
              </div>

              {/* Initial Capital */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">
                  Initial Capital to Invest ($)
                </label>
                <input
                  type="number"
                  {...register("initialCapital", {
                    required: "Initial capital is required",
                    min: {
                      value: 1000,
                      message: "Minimum investment is $1000",
                    },
                  })}
                  className="input-field"
                  placeholder="Enter amount"
                />
                {errors.initialCapital && (
                  <p className="mt-1 text-sm text-red-500">
                    {errors.initialCapital.message}
                  </p>
                )}
              </div>

              <button type="submit" className="btn-primary w-full">
                Create Profile & Continue
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SignUp;
