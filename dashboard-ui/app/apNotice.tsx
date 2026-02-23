'use client'

import { RequestStatus, UserInfo } from "@/types/types";
import React from "react";

interface APNoticeProps {
  data?: UserInfo;
  isLoading: boolean;
}

export default function APNotice({data, isLoading}: APNoticeProps) {
  if(isLoading || !data) {
    return <p className="text-md text-gray-600">Loading Personal AP configuration status...</p>
  } 
  
  const {chtc_account, dashboard_request_status} = data;
  if (chtc_account.spark_account !== RequestStatus.COMPLETE || chtc_account.spark_account !== RequestStatus.COMPLETE) {
    return (
      <p className="text-md text-gray-600 mb-8">
        Spark access must be configured before requesting a Personal AP.
      </p>
    )
  }
  else if (dashboard_request_status === RequestStatus.NOT_REQUESTED) {
    return (
      <p className="text-md text-gray-600 mb-8">
        Please let us know about your expected workflows. This will help us right-size your AP. 
        Reach out to the facilitation team at chtc@cs.wisc.edu 
        for help determining your workflow parameters. You may also "Request Defaults" for a
        standard configuration.
      </p>
    )
  } else if (dashboard_request_status === RequestStatus.REQUEST_RECEIVED) {
    return (
      <p className="text-md text-gray-600 mb-8">
        We have received your request for a Personal AP with the following parameters. 
        The CHTC Infrastructure Services team is reviewing your request and 
        will contact you if we need any additional information.
      </p>
    )
  } else if (dashboard_request_status === RequestStatus.IN_PROGRESS) {
    return (
      <p className="text-md text-gray-600 mb-8">
        Your request for a Personal AP with the following parameters has been approved. 
        The CHTC Infrastructure Services team is in the process of provisioning your AP.
      </p>
    )
  } else {
    return <React.Fragment></React.Fragment>;
  }
}
