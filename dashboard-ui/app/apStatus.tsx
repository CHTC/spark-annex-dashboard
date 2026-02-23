import { DashboardHealth, DashboardRequest, UserInfo } from "@/types/types"
import { ArrowPathIcon } from '@heroicons/react/24/solid';
import { getAPIUrl } from "./util"
import { useState } from "react"

type APStatusProps = {
  data: UserInfo  
  onSubmit: Function
}

const HealthColors: Record<DashboardHealth, string> = {
  "Healthy": "text-emerald-500",
  "Poor": "text-red-500",
  "Unknown": "text-gray-500"
}

const submitAPRepairRequest = async () => {
  var response = await fetch(`${getAPIUrl()}ap-repair-request`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    }
  })
  return response;
}

export default function APStatus({data, onSubmit}: APStatusProps) {
  const statusData = data.live_dashboard_status;
  if(!statusData) {
    return (
      <div>
        <p className="text-md text-gray-600">No status information available.</p>
      </div>
    )
  }

  const [sendingForm, setSendingForm] = useState({
    sending: false,
    error: "",
  });

  const handleHelpRequest = async (e: React.MouseEvent) => {
    e.preventDefault();
    console.log('Help form submitted.');

    setSendingForm({sending: true, error: ""});
    var response = await submitAPRepairRequest();
    if (!response.ok) {
      setSendingForm({sending: false, error: `Error submitting form: ${response.statusText}`});
    } else {
      setSendingForm({sending: false, error: ""});
      onSubmit();
    }
  };

  const { pod_health, collector_health, dashboard_health, assistance_requested } = statusData;

  var allHealthy = [pod_health, collector_health, dashboard_health]
    .every(status => status === "Healthy");

  return (
      <div>
        <p className="text-md text-gray-600 mb-4">
        {allHealthy ?
          <span> Your Personal AP is 
            {" "}<span className={`${HealthColors["Healthy"]} font-bold`}>Healthy.</span>{" "}
            You may access your AP via the "Go to AP Dashboard" button below. 
          </span>
          : assistance_requested ?
          <span> Your personal AP is 
            {" "}<span className={`${HealthColors["Poor"]} font-bold`}>Unhealthy,</span>{" "}
            and we have received your request for assistance in resolving the issue. If you
            have not received any information regarding the progress of your repair within 1 business day,
            please reach out to 
            {" "}
            <a className="text-blue-600 hover:text-blue-700" href="mailto:chtc-infrastructure@g-groups.wisc.edu">chtc-infrastructure@g-groups.wisc.edu</a>
            {" "}
            for assistance.
          </span>
          :
          <span> One or more status checks on your Personal AP are 
            {" "}<span className={`${HealthColors["Poor"]} font-bold`}>Unhealthy.</span>{" "}
            If this issue persists, please use the "Report a Problem" button below to notify the 
            Infrastructure Services team.
          </span>
        }
        </p>
        <p className="text-md text-gray-700">
          <span>AP Container Status:</span>{" "}
          <span className={`${HealthColors[pod_health]} font-bold`}>{pod_health}</span>
        </p>
        <p className="text-sm text-gray-600 mb-2">
          <span>{statusData.pod_health_reason || "Unable to complete health check"}</span>
        </p>
        <p className="text-md text-gray-700">
          <span>HTCondor Daemon Status:</span>{" "}
          <span className={`${HealthColors[collector_health]} font-bold`}>{collector_health}</span>
        </p>
        <p className="text-sm text-gray-600 mb-2">
          <span>{statusData.collector_health_reason || "Unable to complete health check"}</span>
        </p>
        <p className="text-md text-gray-700">
          <span>AP Web Dashboard Status:</span>{" "}
          <span className={`${HealthColors[dashboard_health]} font-bold`}>{dashboard_health}</span>
        </p>
        <p className="text-sm text-gray-600 mb-6">
          <span>{statusData.dashboard_health_reason || "Unable to complete health check"}</span>
        </p>
        {sendingForm.sending && 
          <div className="flex justify-end">
            <button
              type="button"
              className="px-6 py-2 bg-none text-blue-600 rounded-md"
            >
              <ArrowPathIcon className='size-6 animate-spin'/>
            </button>
          </div> 
        }
        {!sendingForm.sending &&
          <div className={ !allHealthy && !assistance_requested ? "flex justify-between": "flex justify-end" } >
            {!allHealthy && !assistance_requested &&
              <button
                type="button"
                className="px-0 py-2 bg-none text-blue-600 font-medium rounded-md hover:text-blue-700 cursor-pointer"
                onClick={handleHelpRequest}
              >
                Report a Problem
              </button>
            }
            <a href={`/dashboards/${data.user_id}/`} target="_blank">
              <button
                type="button"
                disabled={ !allHealthy }
                className="px-6 py-2 bg-blue-600 text-white font-medium rounded-md hover:bg-blue-700 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Go to AP Dashboard
              </button>
            </a>
          </div>
        }
      </div>

  )
}
