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
        Reach out to the facilitation team at 
        {" "}
        <a className="text-blue-600 hover:text-blue-700" href="mailto:chtc@cs.wisc.edu">chtc@cs.wisc.edu</a>
        {" "}
        for help determining your workflow parameters. You may also "Request Defaults" for a
        standard configuration.
      </p>
    )
  } else if (dashboard_request_status === RequestStatus.REQUEST_RECEIVED) {
    return (
      <p className="text-md text-gray-600 mb-8">
        Thank for for letting us know about your expected HTCondor workflows. The infrastructure
        services team has received your request for a personal AP and will process it within
        1-2 business days. Please reach out to
        {" "}
        <a className="text-blue-600 hover:text-blue-700" href="mailto:chtc-infrastructure@g-groups.wisc.edu">chtc-infrastructure@g-groups.wisc.edu</a>
        {" "}
        if you haven't heard from us within 2 business days.
      </p>
    )
  } else if (dashboard_request_status === RequestStatus.IN_PROGRESS) {
    return (
      <p className="text-md text-gray-600 mb-8">
        The infrastructure service team is processing your Personal AP request. Your AP should be ready to
        go within 2-4 hours. Please reach out to
        {" "}
        <a className="text-blue-600 hover:text-blue-700" href="mailto:chtc-infrastructure@g-groups.wisc.edu">chtc-infrastructure@g-groups.wisc.edu</a>
        {" "}
        if you haven't heard from us within 1 business day.
      </p>
    )
  } else {
    return <React.Fragment></React.Fragment>;
  }
}
