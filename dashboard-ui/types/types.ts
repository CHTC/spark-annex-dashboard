export enum DashboardRequestStatus {
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


export interface UserInfo {
  user_id: string;
  ldap_authorized: boolean;
  dashboard_status: DashboardRequestStatus;
  dashboard_info?: DashboardRequest;
}
