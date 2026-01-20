'use client'

import { DashboardRequestStatus, UserInfo } from "@/types/types";
import React from "react";

interface APNoticeProps {
  data?: UserInfo;
  isLoading: boolean;
}

export default function APNotice({data, isLoading}: APNoticeProps) {
  if(isLoading) {
    return <p className="text-md text-gray-600">Loading Personal AP configuration status...</p>
  } else if (data && !data.ldap_authorized) {
    return (
      <p className="text-md text-gray-600 mb-8">
        Spark access must be configured before requesting a Personal AP.
      </p>
    )
  }
  else if (data && data.dashboard_status === DashboardRequestStatus.NOT_REQUESTED) {
    return (
      <p className="text-md text-gray-600 mb-8">
        Please let us know about your expected workflows. This will help us right-size your AP. 
        Reach out to the facilitation team at chtc@cs.wisc.edu 
        for help determining your workflow parameters. You may also "Request Defaults" for a
        standard configuration.
      </p>
    )
  } else if (data && data.dashboard_status === DashboardRequestStatus.REQUEST_RECEIVED) {
    return (
      <p className="text-md text-gray-600 mb-8">
        We have received your request for a Personal AP with the below parameters. 
        The CHTC infrastructure services team is reviewing your request and 
        will contact you if we need any additional information.
      </p>
    )
  } else if (data && data.dashboard_status === DashboardRequestStatus.IN_PROGRESS) {
    return (
      <p className="text-md text-gray-600 mb-8">
        Your request for a Personal AP with the below paramters has been approved. 
        We are in the process of provisioning your AP.
      </p>
    )
  } else {
    return <React.Fragment></React.Fragment>;
  }
}
