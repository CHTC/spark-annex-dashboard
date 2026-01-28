import { DashboardHealth, UserInfo } from "@/types/types"

type APStatusProps = {
  data: UserInfo  
}

const HealthColors: Record<DashboardHealth, string> = {
  "Healthy": "text-emerald-500",
  "Poor": "text-red-500",
  "Unknown": "text-gray-500"
}

export default function APStatus({data}: APStatusProps) {
  const statusData = data.live_dashboard_status;
  if(!statusData) {
    return (
      <div>
        <p className="text-md text-gray-600">No status information available.</p>
      </div>
    )
  }
  const { pod_health, collector_health, dashboard_health } = statusData;

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
          :
          <span> One or more status checks on your Personal AP are 
          {" "}<span className={`${HealthColors["Poor"]} font-bold`}>Unhealthy.</span>{" "}
          If this problem persists, please reach out to the CHTC infrastructure services team
          via chtc-infrastructure@g-groups.wisc.edu for assistance.
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
        <div className="flex justify-end">
          {/* <button
            type="button"
            className="px-0 py-2 bg-none text-blue-600 font-medium rounded-md hover:text-blue-700 cursor-pointer"
          >
            Report a Problem
          </button> */}

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
      </div>

  )
}
