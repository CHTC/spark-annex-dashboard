export enum RequestStatus {
  NOT_REQUESTED =  "Not requested",
  REQUEST_RECEIVED = "Request received",
  IN_PROGRESS = "In progress",
  COMPLETE = "Active",
  DELETION_REQUESTED = "Deletion Requested",
  DELETED = "Deleted"
}


export interface DashboardRequest {
  job_input_size: number,
  job_output_size: number,
  job_count: number,
  concurrent_jobs: number,
  dagman: boolean,
  local_universe: boolean,
}

export type DashboardHealth = "Healthy" | "Poor" | "Unknown";

export interface LiveDashboardStatus {
    pod_health: DashboardHealth
    pod_health_reason: string

    collector_health: DashboardHealth
    collector_health_reason: string

    dashboard_health: DashboardHealth
    dashboard_health_reason: string
}

export interface CHTCAccountStatus {
  chtc_account: RequestStatus;
  spark_account: RequestStatus;
}
export interface UserInfo {
  user_id: string;

  chtc_account : CHTCAccountStatus;   

  dashboard_request_status: RequestStatus;
  dashboard_request_info?: DashboardRequest;
  live_dashboard_status?: LiveDashboardStatus;
}
