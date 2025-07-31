import React, { useState, useEffect, useRef } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { Search } from "lucide-react";
import CircleLoader from "./CircleLoader";
import axios from "axios";

const DashboardPage = () => {
  const [search, setSearch] = useState("");
  const [inbox, setInbox] = useState(0);
  const [spam, setSpam] = useState(0);
  const [section, setSection] = useState<any[]>([]);
  const containerRefs = useRef<Array<HTMLDivElement | null>>([]);
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);

  const percentage = 75;
  const radius = 50;
  const stroke = 10;
  const normalizedRadius = radius - stroke / 2;
  const circumference = normalizedRadius * 2 * Math.PI;

  const query = new URLSearchParams(useLocation().search);
  const emails = query.getAll("email");
  type Email = {
    account: string;
    diff_time: string;
    name: string;
    state: boolean;
    status: string;
    text: string;
  };
  const navigate = useNavigate();

  const logout = async () => {
    const token = localStorage.getItem("token");
    const device_id = localStorage.getItem("device_id");
    try {
      await axios.post(
        "https://email-check-backend.onrender.com/api/logout",
        {},
        {
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
            "X-Device-ID": device_id,
          },
          withCredentials: true,
        }
      );
    } catch (error) {
      console.warn("Logout error:", error);
    } finally {
      localStorage.clear();
      navigate("/");
    }
  };

  const onSearchClick = async (e: React.MouseEvent<HTMLButtonElement>) => {
    setLoading(true);
    setInbox(0);
    setSpam(0);
    const token = localStorage.getItem("token");
    const device_id = localStorage.getItem("device_id");
    try {
      const res = await axios.post("https://email-check-backend.onrender.com/api/check",

        { search },
        {
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
            "X-Device-ID": `${device_id}`,
          },
          withCredentials: true,
        }
      );

      if (res.data.results) {
        setSection(res.data.results);
        setInbox(res.data.inbox);
        setSpam(res.data.spam);
      } else {
        // Handle when no token is returned
        alert("Invalid credentials or search result not found.");
      }

    } catch (err: unknown) {
      if (axios.isAxiosError(err)) {
        console.error("Axios error:", err.response?.data || err.message);
        alert("A server error occurred. Please try again.");
      } else {
        console.error("Unexpected error:", err);
        alert("An unknown error occurred.");
      }
    }
    finally {
      setLoading(false); // ⬅️ Hide loader after completion
    }
  };

  const scroll = (index: number, direction: "left" | "right") => {
    const container = containerRefs.current[index];
    if (container) {
      const scrollAmount = 300;
      container.scrollBy({
        left: direction === "left" ? -scrollAmount : scrollAmount,
        behavior: "smooth",
      });
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      {/* Header */}
      <div className="flex justify-end w-full bg-[#174866] p-4">
        <div className="flex w-[400px] bg-white rounded shadow overflow-hidden mr-[30px]">
          <input
            type="text"
            placeholder="Enter keyword or email and press enter"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && onSearchClick(e as any)}
            className="flex-1 px-4 py-2 text-sm text-gray-700 focus:outline-none"
          />
          <button
            onClick={onSearchClick}
            className="bg-green-500 hover:bg-green-600 px-4 flex items-center justify-center"
          >
            <Search className="text-white w-4 h-4" />
          </button>
        </div>

        <button
          type="button"
          onClick={logout}
          data-twe-ripple-init
          data-twe-ripple-color="light"
          className="inline-block rounded-md bg-blue-400 bg-warning px-5 pb-2 pt-2.5 text-xs font-medium leading-normal text-white shadow-primary-3 transition duration-150 ease-in-out hover:bg-primary-accent-300 hover:shadow-primary-2 ">
          Logout
        </button>

      </div>
      {/* Stats */}
      <div className="flex gap-10 m-[30px]">
        <StatCircle label="Inbox" value={inbox} color="green" />
        <StatCircle label="Spam" value={spam} color="red" />
      </div>

      {/* Email Cards by Section */}
      {emails.map((emailAddress, groupIndex) => (
        <div
          key={groupIndex}
          className="message-item flex flex-col md:flex-row gap-4 items-stretch w-full"
        >
          {/* Static Card */}
          <div className="w-full md:w-[250px] h-auto p-2 px-[10px] pb-[10px] border rounded-lg shadow flex flex-col items-center">
            <img src="/gmail.png" alt="icon" className="w-[60px] mt-3" />
            <p className="text-base mt-2 text-center break-words">{emailAddress}</p>
            <p className="text-sm text-center text-green-700">
              <b>valid</b>
            </p>
          </div>

          {/* Scrollable Area */}
          <div className="relative w-full flex items-center min-h-[130px] border border-blue-300 overflow-hidden">
            {loading ? (
              <CircleLoader />
            ) : (
              <>
                {/* Left Button */}
                {section?.[groupIndex]?.emails?.length > 0 && (
                  <button
                    onClick={() => scroll(groupIndex, "left")}
                    className="absolute left-2 top-1/2 transform -translate-y-1/2 z-10 bg-slate-200 shadow p-2 rounded-full hover:bg-gray-100"
                  >
                    <ChevronLeft className="w-5 h-5" />
                  </button>
                )}

                {/* Horizontal Scroll */}
                <div
                  ref={(el) => {
                    containerRefs.current[groupIndex] = el;
                  }}
                  className="overflow-x-auto whitespace-nowrap scroll-smooth scrollbar-hide w-full px-4"
                >
                  <div className="flex gap-4 min-w-max snap-x">
                    {section?.[groupIndex]?.emails?.length > 0 ? (
                      section[groupIndex].emails.map((email: Email, emailIndex: number) => (
                        <div
                          key={`${groupIndex}-${emailIndex}`}
                          className={`min-w-[250px] max-w-[90vw] sm:max-w-[270px] h-auto border snap-start p-4 rounded-lg shadow ${email.status === "Inbox" ? "bg-green-100" : "bg-red-100"
                            }`}
                        >
                          <h3 className="font-bold text-gray-800 mb-1 truncate">{email.name}</h3>
                          <div className="text-sm text-teal-800 space-y-1 mb-2">
                            <p className="break-words">{email.account}</p>
                          </div>
                          <div className="text-sm text-gray-700 space-y-1 mb-2">
                            <p className="break-words">{email.text}</p>
                          </div>
                          <div className="flex justify-between items-center text-sm mt-[5px]">
                            <span
                              className={`px-3 py-1 rounded-lg text-xs font-semibold ${email.status === "Inbox"
                                ? "bg-green-600 text-white"
                                : "bg-red-600 text-white"
                                }`}
                            >
                              {email.status}
                            </span>
                            <span className="text-gray-500 text-xs">{email.diff_time}</span>
                          </div>
                        </div>
                      ))
                    ) : (
                      <p
                        key={`${groupIndex}-empty`}
                        className="text-gray-500 italic pl-[20px]"
                      >
                        No emails in this subgroup.
                      </p>
                    )}
                  </div>
                </div>

                {/* Right Button */}
                {section?.[groupIndex]?.emails?.length > 0 && (
                  <button
                    onClick={() => scroll(groupIndex, "right")}
                    className="absolute right-2 top-1/2 transform -translate-y-1/2 z-10 bg-slate-200 shadow p-2 rounded-full hover:bg-gray-100"
                  >
                    <ChevronRight className="w-5 h-5" />
                  </button>
                )}
              </>
            )}
          </div>
        </div>
      ))}
    </div>
  );

};

type Color = "red" | "green" | "blue";

interface StatCircleProps {
  label: string;
  value: number;
  color: Color;
}

const colorMap = {
  red: {
    border: "border-red-500",
    text: "text-red-700",
  },
  green: {
    border: "border-green-500",
    text: "text-green-700",
  },
  blue: {
    border: "border-blue-500",
    text: "text-blue-700",
  },
};

function StatCircle({ label, value, color }: StatCircleProps) {
  const radius = 45;
  const stroke = 10;
  const normalizedRadius = radius - stroke / 2;
  const circumference = normalizedRadius * 2 * Math.PI;
  const strokeDashoffset =
    circumference - (value / 100) * circumference;

  return (
    <div className="relative w-24 h-24 flex items-center justify-center">
      <svg
        height="100%"
        width="100%"
        className="rotate-[-90deg]"
      >
        {/* Background circle */}
        <circle
          stroke="#e5e7eb" // gray-200
          fill="transparent"
          strokeWidth={stroke}
          r={normalizedRadius}
          cx="48"
          cy="48"
        />
        {/* Progress circle */}
        <circle
          stroke={color} // Fallback if dynamic color fails
          className={`stroke-${color}-500`} // Tailwind dynamic stroke
          fill="transparent"
          strokeWidth={stroke}
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          strokeLinecap="round"
          r={normalizedRadius}
          cx="48"
          cy="48"
        />
      </svg>

      {/* Center Text */}
      <div className="absolute text-center text-sm font-semibold text-black">
        <p>{label}</p>
        <p>{value}%</p>
      </div>
    </div>
  );
}

export default DashboardPage;
