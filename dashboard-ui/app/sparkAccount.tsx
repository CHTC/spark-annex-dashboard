'use client'

import { RequestStatus, UserInfo } from "@/types/types"

interface SparkAccountProps {
  error: any;
  isLoading: boolean;
  data: UserInfo | undefined;
}

const {NOT_REQUESTED, REQUEST_RECEIVED, COMPLETE} = RequestStatus;


/**
 * Widget to display a user's Spark account information
 * based on a query to the dashboard API.
 */
export default function SparkAccount({data, error, isLoading}: SparkAccountProps) {
  return  (
    <p className="text-md text-gray-600">
      {(()=>{
        if (isLoading) return <span>Loading Spark account information...</span>
        if (error) return <span>Error loading Spark account information.</span>
        if (!data) return <span>No Spark account information available.</span>
        const {chtc_account} = data;
        console.log(chtc_account)

        if (chtc_account.chtc_account == NOT_REQUESTED) {
          return (
            <span>
              A CHTC user account does not currently exist for your netID ({data.user_id}). A CHTC account is required for 
              accessing resources via the Spark cluster. Please
              {" "}
              <a className="text-blue-600 hover:text-blue-700" href="https://chtc.wisc.edu/uw-research-computing/form.html">request an account</a> 
              {" "}
              from CHTC to get started.
            </span>
          )
        }
        else if (chtc_account.chtc_account == REQUEST_RECEIVED) {
          return (
            <span>
              We have received your request for a CHTC account. You can expect follow up from the CHTC facilitation team within
              2-3 business days. Please reach out to
              {" "}
              <a className="text-blue-600 hover:text-blue-700" href="mailto:chtc@cs.wisc.edu">chtc@cs.wisc.edu</a>
              {" "}
              if you haven't heard from us after 3 business days.
            </span>
          )
        }

        else if (chtc_account.chtc_account == COMPLETE && chtc_account.spark_account == NOT_REQUESTED) {
          return (
            <div>
              <p className="pb-4">
                <span>
                  A CHTC account exists for netID {data.user_id}, but has not been configured for access to the Spark Slurm cluster. 
                  Please request Spark access using the button below. Once you've requested access, you can expect follow up from
                  CHTC's Infrastructure Services team within 2-3 days.
                </span>
              </p>
              <button
                type="submit"
                className="px-6 py-2 bg-blue-600 text-white font-medium rounded-md hover:bg-blue-700 cursor-pointer"
              >
                Request Spark Cluster Access
              </button>
            </div>
            )
        }

        else if (chtc_account.chtc_account == COMPLETE && chtc_account.spark_account == REQUEST_RECEIVED) {
          return (
            <span>
              Thank you for requesting access to the Spark cluster. We've received your request and will process it within 2-3 days.
              Please reach out to
              {" "}
              <a className="text-blue-600 hover:text-blue-700" href="mailto:chtc-infrastructure@g-groups.wisc.edu">chtc-infrastructure@g-groups.wisc.edu</a>
              {" "}
              if you haven't heard from us after 3 business days.
            </span>)
        }

        return (
          <span>
            Spark access is configured for user {data.user_id}.
          </span>)
      })()}
    </p>
  )

}
